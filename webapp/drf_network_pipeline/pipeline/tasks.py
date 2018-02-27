from __future__ import absolute_import, unicode_literals
from django.db.models import Q
from celery import shared_task
from celery_loaders.log.setup_logging import build_colorized_logger
from celery_connectors.utils import ev
from network_pipeline.utils import ppj
from network_pipeline.consts import VALID
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.pipeline.consts import SUCCESS
from drf_network_pipeline.pipeline.consts import ERR
from drf_network_pipeline.job_utils.build_task_response import \
    build_task_response
from drf_network_pipeline.pipeline.prepare_dataset_tools import \
    build_csv
from drf_network_pipeline.pipeline.prepare_dataset_tools import \
    find_all_pipeline_csvs
from drf_network_pipeline.users.db_lookup_user import \
    db_lookup_user
from drf_network_pipeline.pipeline.create_ml_prepare_record import \
    create_ml_prepare_record

name = "ml_tasks"
log = build_colorized_logger(name=name)


@shared_task
def task_ml_prepare(
        req_node):
    """task_ml_prepare

    :param req_node: job utils dictionary for passing a dictionary
    """

    log.info(("task - {} - start "
              "req_node={}")
             .format(
                req_node["task_name"],
                req_node))

    user_data = req_node["data"].get("user_data", None)
    ml_prepare_data = req_node["data"].get("ml_prepare_data", None)

    user_obj = db_lookup_user(
                    user_id=user_data["id"])

    ml_prepare_obj = None
    if req_node["use_cache"]:
        ml_prepare_obj = MLPrepare.objects.select_related().filter(
            Q(id=int(ml_prepare_data["id"]))).cache().first()
    else:
        ml_prepare_obj = MLPrepare.objects.select_related().filter(
            Q(id=int(ml_prepare_data["id"]))).first()
    # end of finding the MLPrepare record

    create_new_record = False

    # create the response node from request
    res = build_task_response(
            use_cache=req_node["use_cache"],
            celery_enabled=req_node["celery_enabled"],
            cache_key=req_node["cache_key"])

    try:

        if create_new_record:
            create_res = create_ml_prepare_record(
                            req_node=req_node)
            user_obj = create_res.get(
                "user_obj",
                None)
            ml_prepare_obj = create_res.get(
                "ml_prepare_obj",
                None)
            if not user_obj:
                res["error"] = ("{} - Failed to find User").format(
                                    req_node["task_name"])
                res["status"] = ERR
                res["error"] = create_res.get("err", "error not set")
                res["data"] = None
                log.error(res["error"])
                return res
            if not ml_prepare_obj:
                res["error"] = ("{} - Failed to create MLPrepare").format(
                                    req_node["task_name"])
                res["status"] = ERR
                res["error"] = create_res.get("err", "error not set")
                res["data"] = None
                log.error(res["error"])
            return res
        # end of create_new_record

        last_step = ("starting user={} prepare={} "
                     "pipeline={} clean={} full={} "
                     "post={} label={} tracking={}").format(
                            ml_prepare_obj.user_id,
                            ml_prepare_obj.id,
                            ml_prepare_obj.pipeline_files,
                            ml_prepare_obj.clean_file,
                            ml_prepare_obj.full_file,
                            ml_prepare_obj.post_proc,
                            ml_prepare_obj.label_rules,
                            ml_prepare_obj.tracking_id)
        log.info(last_step)

        log_id = "job={}".format(
            ml_prepare_obj.id)

        log.info(("prepare={} csvs={}")
                 .format(
                    ml_prepare_obj.id,
                    ml_prepare_obj.ds_glob_path))

        ml_prepare_obj.pipeline_files = find_all_pipeline_csvs(
            use_log_id=log_id,
            csv_glob_path=ml_prepare_obj.ds_glob_path)

        log.info(("preparing={} clean={} full={} "
                  "meta_suffix={} files={}")
                 .format(
                    ml_prepare_obj.id,
                    ml_prepare_obj.clean_file,
                    ml_prepare_obj.full_file,
                    ml_prepare_obj.meta_suffix,
                    ml_prepare_obj.pipeline_files))

        save_node = build_csv(
            use_log_id=log_id,
            pipeline_files=ml_prepare_obj.pipeline_files,
            fulldata_file=ml_prepare_obj.full_file,
            clean_file=ml_prepare_obj.clean_file,
            post_proc_rules=ml_prepare_obj.post_proc,
            label_rules=ml_prepare_obj.label_rules,
            meta_suffix=ml_prepare_obj.meta_suffix)

        if save_node["status"] == VALID:

            log.info("successfully process datasets:")

            ml_prepare_obj.post_proc = save_node["post_proc_rules"]
            ml_prepare_obj.post_proc["features_to_process"] = \
                save_node["features_to_process"]
            ml_prepare_obj.post_proc["ignore_features"] = \
                save_node["ignore_features"]
            ml_prepare_obj.post_proc["feature_to_predict"] = \
                save_node["feature_to_predict"]
            ml_prepare_obj.label_rules = save_node["label_rules"]
            ml_prepare_obj.pipeline_files = save_node["pipeline_files"]
            ml_prepare_obj.full_file = save_node["fulldata_file"]
            ml_prepare_obj.clean_file = save_node["clean_file"]
            ml_prepare_obj.status = "finished"
            ml_prepare_obj.control_state = "finished"
            ml_prepare_obj.save()
            log.info(("saved prepare={}")
                     .format(
                         ml_prepare_obj.id))

            if ev("SHOW_SUMMARY",
                    "0") == "1":
                log.info(("Full csv: {}")
                         .format(
                             save_node["fulldata_file"]))
                log.info(("Full meta: {}")
                         .format(
                             save_node["fulldata_metadata_file"]))
                log.info(("Clean csv: {}")
                         .format(
                             save_node["clean_file"]))
                log.info(("Clean meta: {}")
                         .format(
                             save_node["clean_metadata_file"]))
                log.info("------------------------------------------")
                log.info(("Predicting Feature: {}")
                         .format(
                             save_node["feature_to_predict"]))
                log.info(("Features to Process: {}")
                         .format(
                             ppj(save_node["features_to_process"])))
                log.info(("Ignored Features: {}")
                         .format(ppj(
                             save_node["ignore_features"])))
                log.info("------------------------------------------")
            # end of show summary

            log.info("Full: {}".format(
                save_node["fulldata_file"]))
            log.info("Cleaned (no-NaNs in columns): {}".format(
                save_node["clean_file"]))
            data = ml_prepare_obj.get_public()
            res["status"] = SUCCESS
            res["err"] = ""
            res["data"] = data
        else:
            last_step = ("failed to prepare csv status={} "
                         "errors: {}").format(
                            save_node["status"],
                            save_node["err"])
            log.error(last_step)
            ml_prepare_obj.status = "error"
            ml_prepare_obj.control_state = "error"
            ml_prepare_obj.save()
            data["prepare"] = ml_prepare_obj.get_public()
            data["ready"] = {}
            res["status"] = ERR
            res["error"] = last_step
            res["data"] = data
            return res
        # end of checking it started

    except Exception as e:
        res["status"] = ERR
        res["err"] = ("Failed task={} with "
                      "ex={}").format(
                          req_node["task_name"],
                          e)
        res["data"] = None
        log.error(res["err"])
    # end of try/ex

    log.info(("task - {} - done")
             .format(
                 req_node["task_name"]))

    return res
# end of task_ml_prepare
