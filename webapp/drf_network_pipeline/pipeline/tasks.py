from __future__ import absolute_import, unicode_literals
from django.db.models import Q
from celery import shared_task
from antinex_utils.log.setup_logging import build_colorized_logger
from antinex_utils.utils import ev
from antinex_utils.utils import ppj
from antinex_utils.consts import VALID
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLJobResult
from antinex_utils.consts import SUCCESS
from antinex_utils.consts import ERR
from antinex_utils.prepare_dataset_tools import build_csv
from antinex_utils.prepare_dataset_tools import find_all_pipeline_csvs
from antinex_utils.build_training_request import build_training_request
from antinex_utils.make_predictions import make_predictions
from drf_network_pipeline.users.db_lookup_user import \
    db_lookup_user
from drf_network_pipeline.pipeline.create_ml_prepare_record import \
    create_ml_prepare_record
from drf_network_pipeline.job_utils.build_task_response import \
    build_task_response


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
                ppj(req_node)))

    ml_prepare_data = req_node["data"].get("ml_prepare_data", None)

    user_obj = None
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

            log.info("successfully processed datasets:")

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


@shared_task
def task_ml_job(
        req_node):
    """task_ml_job

    :param req_node: job utils dictionary for passing a dictionary
    """

    log.info(("task - {} - start "
              "req_node={}")
             .format(
                req_node["task_name"],
                ppj(req_node)))

    user_data = req_node["data"].get("user_data", None)
    ml_job = req_node["data"].get("ml_job_data", None)
    ml_result = req_node["data"].get("ml_result_data", None)
    model_desc = req_node["data"].get("model_desc", None)
    label_rules = req_node["data"].get("label_rules", None)
    predict_rows = req_node["data"].get("predict_rows", None)

    user_res = db_lookup_user(
                    user_id=user_data["id"])
    user_obj = user_res.get(
        "user_obj",
        None)
    ml_job_id = None
    ml_result_id = None
    ml_job_obj = None
    found_predictions = None
    found_accuracy = None

    if req_node["use_cache"]:
        ml_job_obj = MLJob.objects.select_related().filter(
            Q(id=int(ml_job["id"])) & Q(user=user_obj)).cache().first()
    else:
        ml_job_obj = MLJob.objects.select_related().filter(
            Q(id=int(ml_job["id"])) & Q(user=user_obj)).first()
    # end of finding the MLJob record

    ml_result_obj = None
    if req_node["use_cache"]:
        ml_result_obj = MLJobResult.objects.select_related().filter(
            Q(id=int(ml_result["id"])) & Q(user=user_obj)).cache().first()
    else:
        ml_result_obj = MLJobResult.objects.select_related().filter(
            Q(id=int(ml_result["id"])) & Q(user=user_obj)).first()
    # end of finding the MLJobResult record

    res = build_task_response(
            use_cache=req_node["use_cache"],
            celery_enabled=req_node["celery_enabled"],
            cache_key=req_node["cache_key"])

    last_step = "not started"
    data = {}
    data["job"] = {}
    data["results"] = {}
    try:

        res["status"] = ERR
        res["error"] = ""

        predict_manifest = ml_job_obj.predict_manifest
        csv_file = predict_manifest.get("csv_file", None)
        meta_file = predict_manifest.get("meta_file", None)
        epochs = int(predict_manifest.get("epochs", "5"))
        test_size = float(predict_manifest.get("test_size", "0.2"))
        batch_size = int(predict_manifest.get("batch_size", "32"))
        verbose = int(predict_manifest.get("verbose", "1"))
        image_file = ml_result_obj.acc_image_file
        version = ml_job_obj.version
        loss = predict_manifest.get(
            "loss",
            "binary_crossentropy")
        optimizer = predict_manifest.get(
            "optimizer",
            "adam")
        metrics = predict_manifest.get(
            "metrics",
            [
                "accuracy"
            ])
        histories = predict_manifest.get(
            "histories",
            [
                "val_loss",
                "val_acc",
                "loss",
                "acc"
            ])

        ml_job_id = ml_job_obj.id
        ml_result_id = ml_result_obj.id

        last_step = ("starting user={} "
                     "job.id={} result.id={} predict={} "
                     "model_desc={} "
                     "csv={} meta={}").format(
                        ml_job_obj.user.id,
                        ml_job_id,
                        ml_result_id,
                        ml_job_obj.predict_feature,
                        model_desc,
                        csv_file,
                        meta_file)
        log.info(last_step)

        ml_job_obj.status = "analyzing"
        ml_job_obj.save()

        ml_req = build_training_request(
                csv_file=csv_file,
                meta_file=meta_file,
                predict_feature=ml_job_obj.predict_feature,
                test_size=test_size)

        if ml_req["status"] != VALID:
            last_step = ("Stopping for status={} "
                         "errors: {}").format(
                            ml_req["status"],
                            ml_req["err"])
            log.error(last_step)
            ml_job_obj.status = "error"
            ml_job_obj.control_state = "error"
            log.info(("saving job={}")
                     .format(
                            ml_job_id))
            ml_job_obj.save()
            data["job"] = ml_job_obj.get_public()
            error_data = {
                "status": ml_req["status"],
                "err": ml_req["err"]
            }
            data["results"] = error_data
            res["status"] = ERR
            res["error"] = last_step
            res["data"] = data
            return res
        else:

            predict_manifest["ignore_features"] = \
                ml_req.get("ignore_features", [])
            predict_manifest["features_to_process"] = \
                ml_req.get("features_to_process", [])
            if label_rules:
                predict_manifest["label_rules"] = \
                    label_rules
            else:
                predict_manifest["label_rules"] = \
                    ml_req["meta_data"]["label_rules"]
            predict_manifest["post_proc_rules"] = \
                ml_req["meta_data"]["post_proc_rules"]
            predict_manifest["version"] = version

            last_step = ("job.id={} built_training_request={} "
                         "predict={} features={} ignore={} "
                         "label_rules={} post_proc={}").format(
                            ml_job_obj.id,
                            ml_req["status"],
                            predict_manifest["predict_feature"],
                            predict_manifest["features_to_process"],
                            predict_manifest["ignore_features"],
                            predict_manifest["label_rules"],
                            predict_manifest["post_proc_rules"])

            log.info(last_step)

            if ml_job_obj.ml_type == "regression":
                log.info(("creating Keras - regression - "
                          "sequential model ml_type={}")
                         .format(
                             ml_job_obj.ml_type))

                loss = "mse"
                metrics = [
                    "mse",
                    "mae",
                    "mape",
                    "cosine"
                ]

                histories = [
                    "mean_squared_error",
                    "mean_absolute_error",
                    "mean_absolute_percentage_error",
                    "cosine_proximity"
                ]
            else:
                log.info(("creating Keras - sequential model"
                          "ml_type={}")
                         .format(ml_job_obj.ml_type))
            # end of classification vs regression

            ml_job_obj.predict_manifest["epochs"] = epochs
            ml_job_obj.predict_manifest["batch_size"] = batch_size
            ml_job_obj.predict_manifest["verbose"] = verbose
            ml_job_obj.predict_manifest["loss"] = loss
            ml_job_obj.predict_manifest["metrics"] = metrics
            ml_job_obj.predict_manifest["optimizer"] = optimizer
            ml_job_obj.predict_manifest["histories"] = histories

            ml_job_obj.predict_manifest = predict_manifest
            ml_job_obj.status = "started"
            ml_job_obj.save()

            scores = None
            prediction_req = {
                "label": "job_{}_result_{}".format(
                    ml_job_id,
                    ml_result_id),
                "predict_rows": predict_rows,
                "manifest": ml_job_obj.predict_manifest,
                "model_json": ml_result_obj.model_json,
                "model_desc": model_desc,
                "weights_json": ml_result_obj.model_weights,
                "meta": req_node
            }

            prediction_res = make_predictions(
                req=prediction_req)

            if prediction_res["status"] != SUCCESS:
                last_step = ("Stopping for prediction_status={} "
                             "errors: {}").format(
                                prediction_res["status"],
                                prediction_res["err"])
                log.error(last_step)
                ml_job_obj.status = "error"
                ml_job_obj.control_state = "error"
                log.info(("saving job={}")
                         .format(
                                ml_job_id))
                ml_job_obj.save()
                data["job"] = ml_job_obj.get_public()
                error_data = {
                    "status": prediction_res["status"],
                    "err": prediction_res["err"]
                }
                data["results"] = error_data
                res["status"] = ERR
                res["error"] = last_step
                res["data"] = data
                return res

            res_data = prediction_res["data"]
            model = res_data["model"]
            model_weights = res_data["weights"]
            scores = res_data["scores"]
            acc_data = res_data["acc"]
            error_data = res_data["err"]
            predictions_json = {
                "predictions": res_data["sample_predictions"]
            }
            found_predictions = res_data["sample_predictions"]
            found_accuracy = acc_data.get(
                "accuracy",
                None)

            last_step = ("job={} accuracy={}").format(
                            ml_job_id,
                            scores[1] * 100)
            log.info(last_step)

            ml_job_obj.status = "finished"
            ml_job_obj.control_state = "finished"
            ml_job_obj.save()
            log.info(("saved job={}")
                     .format(
                        ml_job_id))

            data["job"] = ml_job_obj.get_public()
            acc_data = {
                "accuracy": scores[1] * 100
            }
            error_data = None
            log.info(("converting job={} model to json")
                     .format(
                        ml_job_id))
            model_json = model.to_json()
            log.info(("saving job={} weights_file={}")
                     .format(
                        ml_job_id,
                        ml_result_obj.model_weights_file))

            log.info(("building job={} results")
                     .format(
                        ml_job_id))

            ml_result_obj.status = "finished"
            ml_result_obj.acc_data = acc_data
            ml_result_obj.error_data = error_data
            ml_result_obj.model_json = model_json
            ml_result_obj.model_weights = model_weights
            ml_result_obj.acc_image_file = image_file
            ml_result_obj.predictions_json = predictions_json
            ml_result_obj.version = version

            log.info(("saving job={} results")
                     .format(
                        ml_job_id))
            ml_result_obj.save()

            log.info(("updating job={} results={}")
                     .format(
                        ml_job_id,
                        ml_result_id))
            ml_result_obj.save()

            data["job"] = ml_job_obj.get_public()
            data["results"] = ml_result_obj.get_public()
            res["status"] = SUCCESS
            res["error"] = ""
            res["data"] = data
            # end of checking it started

        # end of checking it started

        res["data"] = data
    except Exception as e:
        res["status"] = ERR
        res["err"] = ("Failed task={} with "
                      "ex={}").format(
                          req_node["task_name"],
                          e)
        if ml_job_obj:
            data["job"] = ml_job_obj.get_public()
        else:
            data["job"] = None

        if ml_result_obj:
            data["results"] = ml_result_obj.get_public()
        else:
            data["results"] = None
        log.error(res["err"])
    # end of try/ex

    log.info(("task - {} - done - "
              "ml_job.id={} ml_result.id={} "
              "accuracy={} predictions={}")
             .format(
                req_node["task_name"],
                ml_job_id,
                ml_result_id,
                found_accuracy,
                len(found_predictions)))

    return res
# end of task_ml_job


@shared_task
def task_ml_predict(
        req_node):
    """task_ml_predict

    :param req_node: job utils dictionary for passing a dictionary
    """

    log.info(("task - {} - start "
              "req_node={}")
             .format(
                req_node["task_name"],
                ppj(req_node)))

    user_data = req_node["data"].get("user_data", None)
    ml_job = req_node["data"].get("ml_job_data", None)
    ml_result = req_node["data"].get("ml_result_data", None)
    predict_rows = req_node["data"].get("predict_rows", [])
    model_desc = req_node["data"].get("model_desc", None)

    user_res = db_lookup_user(
                    user_id=user_data["id"])
    user_obj = user_res.get(
        "user_obj",
        None)
    ml_job_id = None
    ml_result_id = None
    ml_job_obj = None
    if req_node["use_cache"]:
        ml_job_obj = MLJob.objects.select_related().filter(
            Q(id=int(ml_job["id"])) & Q(user=user_obj)).cache().first()
    else:
        ml_job_obj = MLJob.objects.select_related().filter(
            Q(id=int(ml_job["id"])) & Q(user=user_obj)).first()
    # end of finding the MLJob record

    ml_result_obj = None
    if req_node["use_cache"]:
        ml_result_obj = MLJobResult.objects.select_related().filter(
            Q(id=int(ml_result["id"]))
            & Q(user=user_obj)).cache().first()
    else:
        ml_result_obj = MLJobResult.objects.select_related().filter(
            Q(id=int(ml_result["id"])) & Q(user=user_obj)).first()
    # end of finding the MLJobResult record

    res = build_task_response(
            use_cache=req_node["use_cache"],
            celery_enabled=req_node["celery_enabled"],
            cache_key=req_node["cache_key"])

    last_step = "not started"
    data = {}
    data["job"] = {}
    data["results"] = {}
    try:

        res["status"] = ERR
        res["error"] = ""

        predict_manifest = ml_job_obj.predict_manifest
        csv_file = predict_manifest["csv_file"]
        meta_file = predict_manifest["meta_file"]

        ml_job_id = ml_job_obj.id
        ml_result_id = ml_result_obj.id

        last_step = ("starting predictions={} for user={} "
                     "job.id={} result.id={} row={} "
                     "csv={} meta={} "
                     "manifest={}").format(
                        len(predict_rows),
                        ml_job_obj.user.id,
                        ml_job_id,
                        ml_result_id,
                        predict_rows,
                        csv_file,
                        meta_file,
                        predict_manifest)

        log.info(last_step)

        prediction_req = {
            "label": "job_{}_result_{}".format(
                ml_job_id,
                ml_result_id),
            "predict_rows": predict_rows,
            "manifest": predict_manifest,
            "model_json": ml_result_obj.model_json,
            "model_desc": model_desc,
            "weights_json": ml_result_obj.model_weights,
            "meta": req_node
        }

        prediction_res = make_predictions(
            req=prediction_req)

        res["status"] = prediction_res["status"]
        res["err"] = prediction_res["err"]
        res["data"] = prediction_res["data"]
    except Exception as e:
        res["status"] = ERR
        res["err"] = ("Failed task={} with "
                      "ex={}").format(
                          req_node["task_name"],
                          e)
        if ml_job_obj:
            data["job"] = ml_job_obj.get_public()
        else:
            data["job"] = None

        if ml_result_obj:
            data["results"] = ml_result_obj.get_public()
        else:
            data["results"] = None
        log.error(res["err"])
    # end of try/ex

    log.info(("task - {} - done - "
              "ml_job.id={} ml_result.id={} data={}")
             .format(
                req_node["task_name"],
                ml_job_id,
                ml_result_id,
                res["data"]))

    return res
# end of task_ml_predict
