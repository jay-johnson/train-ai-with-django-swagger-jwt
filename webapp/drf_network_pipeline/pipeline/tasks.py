from __future__ import absolute_import, unicode_literals
import json
import pandas as pd
from django.conf import settings
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
from drf_network_pipeline.pipeline.process_worker_results import \
    process_worker_results
from drf_network_pipeline.job_utils.build_task_response import \
    build_task_response
from kombu import Connection
from kombu import Producer
from kombu import Exchange
from kombu import Queue


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
def task_publish_to_core(
        req_node):
    """task_publish_to_core

    :param req_node: dictionary to send to the AntiNex Core Worker
    """

    if settings.ANTINEX_WORKER_ENABLED:

        conn = None
        dataset = req_node["body"].get("dataset", None)
        predict_rows = req_node["body"].get("predict_rows", None)

        if not dataset and not predict_rows:
            log.info(("skipping antinex core publish body={} - "
                      "is missing dataset and predict_rows")
                     .format(
                        req_node))
            return None
        # end of checking for supported requests to the core

        log.info(("task_publish_to_core - start req={}").format(
                    str(req_node)[0:32]))

        if not predict_rows:
            log.info(("building predict_rows from dataset={}")
                     .format(
                        dataset))
            predict_rows = []
            predict_rows_df = pd.read_csv(dataset)
            for idx, org_row in predict_rows_df.iterrows():
                new_row = json.loads(org_row.to_json())
                new_row["idx"] = len(predict_rows) + 1
                predict_rows.append(new_row)
            # end of building predict rows

            req_node["body"]["apply_scaler"] = True
            req_node["body"]["predict_rows"] = pd.DataFrame(
                predict_rows).to_json()
            # req_node["body"].pop("dataset", None)
        # end of validating

        req_node["body"]["ml_type"] = \
            req_node["body"]["manifest"]["ml_type"]

        log.debug(("NEXCORE - ssl={} exchange={} routing_key={}")
                  .format(
                    settings.ANTINEX_SSL_OPTIONS,
                    settings.ANTINEX_EXCHANGE_NAME,
                    settings.ANTINEX_ROUTING_KEY))

        try:
            if settings.ANTINEX_WORKER_SSL_ENABLED:
                log.debug("connecting with ssl")
                conn = Connection(
                    settings.ANTINEX_AUTH_URL,
                    login_method="EXTERNAL",
                    ssl=settings.ANTINEX_SSL_OPTIONS)
            else:
                log.debug("connecting without ssl")
                conn = Connection(
                    settings.ANTINEX_AUTH_URL)
            # end of connecting

            conn.connect()

            log.debug("getting channel")
            channel = conn.channel()

            core_exchange = Exchange(
                settings.ANTINEX_EXCHANGE_NAME,
                type=settings.ANTINEX_EXCHANGE_TYPE,
                durable=True)

            log.debug("creating producer")
            producer = Producer(
                channel=channel,
                auto_declare=True,
                serializer="json")

            try:
                log.debug("declaring exchange")
                producer.declare()
            except Exception as k:
                log.error(("declare exchange failed with ex={}")
                          .format(
                            k))
            # end of try to declare exchange which can fail if it exists

            core_queue = Queue(
                settings.ANTINEX_QUEUE_NAME,
                core_exchange,
                routing_key=settings.ANTINEX_ROUTING_KEY,
                durable=True)

            try:
                log.debug("declaring queue")
                core_queue.maybe_bind(conn)
                core_queue.declare()
            except Exception as k:
                log.error(("declare queue={} routing_key={} failed with ex={}")
                          .format(
                            settings.ANTINEX_QUEUE_NAME,
                            settings.ANTINEX_ROUTING_KEY,
                            k))
            # end of try to declare queue which can fail if it exists

            log.info(("publishing exchange={} routing_key={} persist={}")
                     .format(
                        core_exchange.name,
                        settings.ANTINEX_ROUTING_KEY,
                        settings.ANTINEX_DELIVERY_MODE))

            producer.publish(
                body=req_node["body"],
                exchange=core_exchange.name,
                routing_key=settings.ANTINEX_ROUTING_KEY,
                auto_declare=True,
                serializer="json",
                delivery_mode=settings.ANTINEX_DELIVERY_MODE)

        except Exception as e:
            log.info(("Failed to publish to core req={} with ex={}")
                     .format(
                        req_node,
                        e))
        # try/ex

        if conn:
            conn.close()

        log.info(("task_publish_to_core - done"))
    else:
        log.debug("core - disabled")
    # publish to the core if enabled

    return None
# end of task_publish_to_core


@shared_task
def task_ml_process_worker_results():
    if settings.ANTINEX_WORKER_ENABLED:
        log.info("processing worker results")
        process_worker_results()
    else:
        log.info("no worker to get results")
# end of task_ml_process_worker_results


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
    found_predictions = []
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

        # use pre-trained models in memory by label
        use_model_name = ml_job_obj.predict_manifest.get(
            "use_model_name",
            None)
        dataset = ml_job_obj.predict_manifest.get(
            "dataset",
            None)
        predict_rows = ml_job_obj.predict_manifest.get(
            "predict_rows",
            None)
        predict_feature = ml_job_obj.predict_manifest.get(
            "predict_feature",
            None)
        features_to_process = ml_job_obj.predict_manifest.get(
            "features_to_process",
            None)
        ignore_features = ml_job_obj.predict_manifest.get(
            "ignore_features",
            None)
        publish_to_core = ml_job_obj.predict_manifest.get(
            "publish_to_core",
            None)
        apply_scaler = ml_job_obj.predict_manifest.get(
            "apply_scaler",
            True)
        sort_values = ml_job_obj.predict_manifest.get(
            "sort_values",
            None)
        max_records = int(ml_job_obj.predict_manifest.get(
            "max_records",
            "100000"))
        loss = ml_job_obj.predict_manifest.get(
            "loss",
            "binary_crossentropy")
        metrics = ml_job_obj.predict_manifest.get(
            "metrics",
            [
                "accuracy"
            ])
        optimizer = ml_job_obj.predict_manifest.get(
            "optimizer",
            "adam")
        histories = ml_job_obj.predict_manifest.get(
            "histories",
            [
                "val_loss",
                "val_acc",
                "loss",
                "acc"
            ])

        needs_local_builder = True
        if ((dataset or predict_rows) and features_to_process):
            log.info(("using antinex builder dataset={} predict_rows={} "
                      "features_to_process={}")
                     .format(
                        dataset,
                        predict_rows,
                        features_to_process))

            needs_local_builder = False
        # flag for bypassing build inside django instead of antinex-utils

        image_file = ml_result_obj.acc_image_file
        version = ml_job_obj.version

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

        if needs_local_builder:

            log.info("starting local build_training_request")

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
                    log.info(("using Keras - regression - "
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
                    log.info(("using Keras - sequential model "
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

        # end of updating without antinex-utils
        # end of if needs_local_builder:

        ml_job_obj.status = "started"
        ml_job_obj.save()

        scores = None
        prediction_req = {
            "label": "job_{}_result_{}".format(
                ml_job_id,
                ml_result_id),
            "manifest": ml_job_obj.predict_manifest,
            "model_json": ml_result_obj.model_json,
            "model_desc": model_desc,
            "weights_json": ml_result_obj.model_weights,
        }

        if dataset:
            prediction_req["dataset"] = dataset
        if max_records:
            prediction_req["max_records"] = max_records
        if predict_rows:
            prediction_req["predict_rows"] = json.dumps(predict_rows)
        if features_to_process:
            prediction_req["features_to_process"] = features_to_process
        if ignore_features:
            prediction_req["ignore_features"] = ignore_features
        if apply_scaler:
            prediction_req["apply_scaler"] = apply_scaler
        if sort_values:
            prediction_req["sort_values"] = sort_values
        if loss:
            prediction_req["loss"] = loss
        if metrics:
            prediction_req["metrics"] = metrics
        if optimizer:
            prediction_req["optimizer"] = optimizer
        if histories:
            prediction_req["histories"] = histories
        if predict_feature:
            prediction_req["predict_feature"] = predict_feature
        if csv_file:
            prediction_req["csv_file"] = csv_file
        if meta_file:
            prediction_req["meta_file"] = meta_file

        # if you just want to use the core without django training:
        if publish_to_core or settings.ANTINEX_WORKER_ONLY:
            log.info(("model_name={} only publish={} worker={}")
                     .format(
                        use_model_name,
                        publish_to_core,
                        settings.ANTINEX_WORKER_ONLY))
            ml_job_obj.status = "launched"
            ml_job_obj.control_state = "launched"
            ml_job_obj.save()
            ml_result_obj.status = "launched"
            ml_result_obj.control_state = "launched"
            ml_result_obj.save()
        else:
            log.info(("start make_predictions req={}").format(
                ppj(prediction_req)))

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
                "predictions": json.loads(
                    pd.Series(
                        res_data["sample_predictions"]).to_json(
                            orient="records"))
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
            model_json = json.loads(model.to_json())
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
        # end of handing off to core worker without a database connection

        log.info(("saving job={} results")
                 .format(
                    ml_job_id))
        ml_result_obj.save()

        data["job"] = ml_job_obj.get_public()
        data["results"] = ml_result_obj.get_public()
        res["status"] = SUCCESS
        res["error"] = ""
        res["data"] = data

        if settings.ANTINEX_WORKER_ENABLED:

            if use_model_name:
                prediction_req["label"] = use_model_name

            log.info(("publishing to core use_model_name={}")
                     .format(
                        use_model_name))

            publish_req = {
                "body": prediction_req
            }
            if settings.CELERY_ENABLED:
                task_publish_to_core.delay(publish_req)
                task_ml_process_worker_results.delay()
            else:
                task_publish_to_core(publish_req)
        # send to core

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
