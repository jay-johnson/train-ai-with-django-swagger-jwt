import os
import json
import uuid
from spylunking.log.setup_logging import build_colorized_logger
from antinex_utils.consts import SUCCESS
from antinex_utils.consts import ERR
from antinex_utils.consts import FAILED
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLJobResult
from drf_network_pipeline.job_utils.build_task_response import \
    build_task_response
from drf_network_pipeline.users.db_lookup_user import \
    db_lookup_user
from drf_network_pipeline.pipeline.build_worker_result_node import \
    build_worker_result_node


name = "create_ml_job"
log = build_colorized_logger(name=name)


def create_ml_job_record(
        req_data=None):
    """create_ml_job_record

    :param req_data: dictionary to build the MLJob and MLJobResult objects
    """

    user_obj = None
    ml_prepare_obj = None
    ml_job_obj = None
    ml_result_obj = None

    status = FAILED
    last_step = "starting"

    try:

        last_step = "getting user node"
        user_id = req_data.get("user_id", None)

        # create the response node from request
        res = build_task_response()

        user_res = db_lookup_user(
            user_id=user_id)

        if user_res["status"] != SUCCESS:
            res["status"] = ERR
            res["err"] = ("Failed to find user_id={} "
                          "user_obj={}").format(
                            user_id,
                            user_res["user_obj"])
            res["data"] = None
            log.error(res["err"])
            return res
        # end of lookup for user

        user_obj = user_res.get("user_obj", None)

        last_step = "parsing data"
        label = req_data.get(
            "label",
            "")
        title = req_data.get(
            "title",
            label)
        desc = req_data.get(
            "desc",
            None)
        ds_name = req_data.get(
            "ds_name",
            label)
        algo_name = req_data.get(
            "algo_name",
            label)
        ml_type = str(req_data.get(
            "ml_type",
            "classification")).strip().lower()
        apply_scaler = req_data.get(
            "apply_scaler",
            True)
        version = int(req_data.get(
            "version",
            1))
        status = "initial"
        control_state = "active"
        predict_feature = req_data.get(
            "predict_feature",
            "label_value")
        training_data = json.loads(req_data.get(
            "training_data",
            "{}"))
        pre_proc = json.loads(req_data.get(
            "pre_proc",
            "{}"))
        post_proc = json.loads(req_data.get(
            "post_proc",
            "{}"))
        meta_data = json.loads(req_data.get(
            "meta_data",
            "{}"))
        model_weights_file = req_data.get(
            "model_weights_file",
            None)
        model_weights_dir = req_data.get(
            "model_weights_dir",
            os.getenv("MODEL_WEIGHTS_DIR", "/tmp"))
        seed = int(req_data.get(
            "seed",
            training_data.get("seed", "9")))
        test_size = float(req_data.get(
            "test_size",
            training_data.get("test_size", "0.2")))
        epochs = int(req_data.get(
            "epochs",
            training_data.get("epochs", "5")))
        batch_size = int(req_data.get(
            "batch_size",
            training_data.get("batch_size", "32")))
        num_splits = int(req_data.get(
            "num_splits",
            training_data.get("num_splits", "5")))
        verbose = int(req_data.get(
            "verbose",
            training_data.get("verbose", "1")))
        loss = req_data.get(
            "loss",
            "binary_crossentropy")
        optimizer = req_data.get(
            "optimizer",
            "adam")
        metrics = req_data.get(
            "metrics",
            [
                "accuracy"
            ])
        histories = req_data.get(
            "histories",
            [
                "val_loss",
                "val_acc",
                "loss",
                "acc"
            ])
        csv_file = req_data.get(
            "csv_file",
            None)
        meta_file = req_data.get(
            "meta_file",
            None)
        dataset = req_data.get(
            "dataset",
            None)
        predict_rows = req_data.get(
            "predict_rows",
            None)
        features_to_process = req_data.get(
            "features_to_process",
            None)
        ignore_features = req_data.get(
            "ignore_features",
            None)
        sort_values = req_data.get(
            "sort_values",
            None)
        model_desc = req_data.get(
            "model_desc",
            None)
        label_rules = req_data.get(
            "label_rules",
            None)
        image_file = req_data.get(
            "image_file",
            None)
        publish_to_core = req_data.get(
            "publish_to_core",
            None)
        tracking_id = "ml_{}".format(str(uuid.uuid4()))
        # end of saving file naming

        predict_manifest = {
            "job_id": None,
            "result_id": None,
            "ml_type": ml_type,
            "test_size": test_size,
            "epochs": epochs,
            "batch_size": batch_size,
            "num_splits": num_splits,
            "loss": loss,
            "metrics": metrics,
            "optimizer": optimizer,
            "histories": histories,
            "seed": seed,
            "training_data": training_data,
            "csv_file": csv_file,
            "meta_file": meta_file,
            "use_model_name": label,
            "dataset": dataset,
            "predict_rows": predict_rows,
            "apply_scaler": apply_scaler,
            "predict_feature": predict_feature,
            "features_to_process": features_to_process,
            "ignore_features": ignore_features,
            "sort_values": sort_values,
            "model_desc": model_desc,
            "label_rules": label_rules,
            "post_proc_rules": None,
            "model_weights_file": None,
            "verbose": verbose,
            "version": 1
        }

        # if this is only being published to the core workers
        if publish_to_core:
            predict_manifest["publish_to_core"] = True
        # end of building core response node

        if csv_file:
            if not os.path.exists(csv_file):
                last_step = ("Missing csv_file={}").format(
                                csv_file)
                log.error(last_step)
                res = {
                    "status": ERR,
                    "error": last_step,
                    "user_obj": user_obj,
                    "ml_prepare_obj": None,
                    "ml_job_obj": None,
                    "ml_result_obj": None
                }
                return res
            # check if set
        # end of check for csv file
        if meta_file:
            if not os.path.exists(meta_file):
                last_step = ("Missing meta_file={}").format(
                                meta_file)
                log.error(last_step)
                res = {
                    "status": ERR,
                    "error": last_step,
                    "user_obj": user_obj,
                    "ml_prepare_obj": None,
                    "ml_job_obj": None,
                    "ml_result_obj": None
                }
                return res
            # check if set
        # end of check for meta file

        ml_job_obj = MLJob(
                user=user_obj,
                title=title,
                desc=desc,
                ds_name=ds_name,
                algo_name=algo_name,
                ml_type=ml_type,
                status=status,
                control_state=control_state,
                predict_feature=predict_feature,
                predict_manifest=predict_manifest,
                training_data=training_data,
                pre_proc=pre_proc,
                post_proc=post_proc,
                meta_data=meta_data,
                tracking_id=tracking_id,
                version=version)

        last_step = "saving"
        log.info("saving job")
        ml_job_obj.save()

        last_step = ("creating user={} job={} "
                     "initial result "
                     "csv={} meta={}").format(
                        user_id,
                        ml_job_obj.id,
                        csv_file,
                        meta_file)
        log.info(last_step)

        acc_data = {
            "accuracy": -1.0
        }
        ml_result_obj = MLJobResult(
                user=ml_job_obj.user,
                job=ml_job_obj,
                status="initial",
                csv_file=csv_file,
                meta_file=meta_file,
                test_size=test_size,
                acc_data=acc_data,
                acc_image_file=image_file,
                model_json=None,
                model_weights=None,
                predictions_json=None,
                error_data=None)
        ml_result_obj.save()

        if not model_weights_file:
            model_weights_file = "{}/{}".format(
                model_weights_dir,
                "ml_weights_job_{}_result_{}.h5".format(
                    ml_job_obj.id,
                    ml_result_obj.id))
        # end of building model weights file

        # make sure to save this to the manifest too
        predict_manifest["job_id"] = ml_job_obj.id
        predict_manifest["result_id"] = ml_result_obj.id
        predict_manifest["model_weights_file"] = \
            model_weights_file

        job_manifest = {
            "job_id": ml_job_obj.id,
            "result_id": ml_result_obj.id,
            "job_type": "train-and-predict"
        }
        predict_manifest["worker_result_node"] = build_worker_result_node(
            req=job_manifest)

        ml_job_obj.predict_manifest = predict_manifest
        ml_job_obj.save()

        ml_result_obj.model_weights_file = \
            model_weights_file
        ml_result_obj.save()

        log.info(("create_ml_job_record - end "
                  "user.id={} ml_job.id={} ml_result.id={} "
                  "csv_file={} meta_file={} weights_file={}")
                 .format(
                    user_id,
                    ml_job_obj.id,
                    ml_result_obj.id,
                    ml_result_obj.csv_file,
                    ml_result_obj.meta_file,
                    ml_result_obj.model_weights_file))

        last_step = ""
        status = SUCCESS

    except Exception as e:
        status = ERR
        last_step = ("create create_ml_job_record failed last_step='{}' "
                     "with ex={} data={}").format(
                        last_step,
                        e,
                        req_data)
        log.error(last_step)
    # end of try/ex

    res = {
        "status": status,
        "error": last_step,
        "user_obj": user_obj,
        "ml_prepare_obj": ml_prepare_obj,
        "ml_job_obj": ml_job_obj,
        "ml_result_obj": ml_result_obj
    }
    return res
# end of create_ml_job_record
