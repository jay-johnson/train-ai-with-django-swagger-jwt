from __future__ import absolute_import, unicode_literals
import os
import uuid
from django.db.models import Q
from django.conf import settings
from celery import shared_task
from celery_loaders.log.setup_logging import build_colorized_logger
from celery_connectors.utils import ev
from network_pipeline.utils import ppj
from network_pipeline.consts import VALID
from network_pipeline.build_training_request import build_training_request
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLJobResult
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
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense
import matplotlib
matplotlib.use("Agg")  # noqa
import matplotlib.pyplot as plt  # noqa

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
                req_node))

    user_data = req_node["data"].get("user_data", None)
    ml_job = req_node["data"].get("ml_job_data", None)
    ml_result = req_node["data"].get("ml_result_data", None)

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

        job_manifest = ml_job_obj.job_manifest
        csv_file = job_manifest["csv_file"]
        meta_file = job_manifest["meta_file"]
        epochs = job_manifest["epochs"]
        test_size = job_manifest["test_size"]
        batch_size = job_manifest["batch_size"]
        verbose = job_manifest["verbose"]
        image_file = job_manifest["image_file"]
        version = ml_job_obj.version

        ml_job_id = ml_job_obj.id
        ml_result_id = ml_result_obj.id

        last_step = ("starting user={} "
                     "job.id={} result.id={} "
                     "csv={} meta={}").format(
                        ml_job_obj.user.id,
                        ml_job_id,
                        ml_result_id,
                        csv_file,
                        meta_file)
        log.info(last_step)

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
            last_step = ("built_training_request={} "
                         "features={} ignore={}").format(
                            ml_req["status"],
                            ml_req["features_to_process"],
                            ml_req["ignore_features"])

            log.info(last_step)

            log.info("resetting Keras backend")

            scores = None
            model = Sequential()
            histories = []

            if ml_job_obj.ml_type == "regression":
                log.info(("creating Keras - regression - "
                          "sequential model ml_type={}")
                         .format(
                             ml_job_obj.ml_type))

                # create the model
                model.add(
                    Dense(
                        8,
                        input_dim=len(ml_req["features_to_process"]),
                        kernel_initializer="normal",
                        activation="relu"))
                model.add(
                    Dense(
                        6,
                        kernel_initializer="normal",
                        activation="relu"))
                model.add(
                    Dense(
                        1,
                        kernel_initializer="normal",
                        activation="sigmoid"))

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

                last_step = ("compiling model "
                             "loss={} metrics={}").format(
                                loss,
                                metrics)
                log.info(last_step)

                # compile the model
                model.compile(
                        loss=loss,
                        optimizer="adam",
                        metrics=metrics)

            else:
                log.info(("creating Keras - sequential model"
                          "ml_type={}")
                         .format(ml_job_obj.ml_type))

                # create the model
                model.add(
                    Dense(
                        8,
                        input_dim=len(ml_req["features_to_process"]),
                        kernel_initializer="uniform",
                        activation="relu"))
                model.add(
                    Dense(
                        6,
                        kernel_initializer="uniform",
                        activation="relu"))
                model.add(
                    Dense(
                        1,
                        kernel_initializer="uniform",
                        activation="sigmoid"))

                histories = [
                    "val_loss",
                    "val_acc",
                    "loss",
                    "acc"
                ]

                last_step = "compiling model"
                log.info(last_step)

                # compile the model
                model.compile(
                        loss="binary_crossentropy",
                        optimizer="adam",
                        metrics=["accuracy"])

            # end of classification vs regression

            last_step = ("fitting model - "
                         "epochs={} batch={} "
                         "verbose={} - please wait").format(
                            epochs,
                            batch_size,
                            verbose)
            log.info(last_step)

            # fit the model
            history = model.fit(
                        ml_req["X_train"],
                        ml_req["Y_train"],
                        validation_data=(
                            ml_req["X_test"],
                            ml_req["Y_test"]),
                        epochs=epochs,
                        batch_size=batch_size,
                        verbose=verbose)

            # evaluate the model
            scores = model.evaluate(
                        ml_req["X_test"],
                        ml_req["Y_test"])

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
            log.info(("converting job={} model weights")
                     .format(
                        ml_job_id))
            model_weights = {
                "weights": pd.Series(
                    model.get_weights()).to_json(
                        orient="values")
            }
            log.info(("building job={} results")
                     .format(
                        ml_job_id))

            ml_result_obj.status = "finished"
            ml_result_obj.acc_data = acc_data
            ml_result_obj.error_data = error_data
            ml_result_obj.model_json = model_json
            ml_result_obj.model_weights = model_weights
            ml_result_obj.version = version

            log.info(("saving job={} results")
                     .format(
                        ml_job_id))
            ml_result_obj.save()

            try:
                if history and len(histories) > 0:
                    log.info(("plotting history={} "
                              "histories={}")
                             .format(
                                history,
                                histories))
                    should_save = False
                    for h in histories:
                        if h in history.history:
                            log.info(("plotting={}")
                                     .format(
                                        h))
                            plt.plot(
                                history.history[h],
                                label=h)
                            should_save = True
                        else:
                            log.error(("missing history={}")
                                      .format(
                                            h))
                    # for all histories

                    if should_save:
                        if not image_file:
                            image_file = ("{}/accuracy_job_"
                                          "{}_result_{}.png").format(
                                            settings.IMAGE_SAVE_DIR,
                                            ml_job_id,
                                            ml_result_id,
                                            str(uuid.uuid4()).replace(
                                                "-", ""))
                        log.info(("saving plots as image={}")
                                 .format(
                                    image_file))
                        plt.legend(loc='best')
                        plt.savefig(image_file)
                        if not os.path.exists(image_file):
                            log.error(("Failed saving image={}")
                                      .format(
                                            image_file))
                        else:
                            ml_result_obj.acc_image_file = \
                                    image_file
                    # end of saving file

                # end of if there are hsitories to plot
            except Exception as e:
                if ml_job_obj and ml_result_obj:
                    log.error(("Failed saving job={} "
                               "image_file={} ex={}")
                              .format(
                                ml_job_id,
                                image_file,
                                e))
                else:
                    log.error(("Failed saving "
                               "image_file={} ex={}")
                              .format(
                                image_file,
                                e))
            # end of try/ex

            log.info(("updating job={} results={}")
                     .format(
                        ml_job_id,
                        ml_result_id))
            ml_result_obj.save()

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
              "ml_job.id={} ml_result.id={} data={}")
             .format(
                req_node["task_name"],
                ml_job_id,
                ml_result_id,
                res["data"]))

    return res
# end of task_ml_job
