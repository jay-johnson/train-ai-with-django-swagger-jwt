import os
import json
import uuid
from celery_loaders.log.setup_logging import build_colorized_logger
from drf_network_pipeline.pipeline.consts import SUCCESS
from drf_network_pipeline.pipeline.consts import ERR
from drf_network_pipeline.pipeline.consts import FAILED
from drf_network_pipeline.pipeline.models import MLJob
from drf_network_pipeline.pipeline.models import MLJobResult
from drf_network_pipeline.job_utils.build_task_response import \
    build_task_response
from drf_network_pipeline.users.db_lookup_user import \
    db_lookup_user


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
        title = req_data["title"]
        desc = req_data["desc"]
        ds_name = req_data["ds_name"]
        algo_name = req_data["algo_name"]
        ml_type = str(req_data["ml_type"]).strip().lower()
        version = req_data["version"]
        status = "initial"
        control_state = "active"
        predict_feature = req_data["predict_feature"]
        training_data = json.loads(req_data["training_data"])
        pre_proc = json.loads(req_data["pre_proc"])
        post_proc = json.loads(req_data["post_proc"])
        meta_data = json.loads(req_data["meta_data"])
        tracking_id = "ml_{}".format(str(uuid.uuid4()))
        test_size = 0.20
        epochs = 5
        batch_size = 2
        verbose = 1
        csv_file = req_data["csv_file"]
        meta_file = req_data["meta_file"]

        if "test_size" in training_data:
            last_step = "parsing test_size"
            test_size = float(training_data["test_size"])
        if "epochs" in training_data:
            last_step = "parsing test_size"
            epochs = int(training_data["epochs"])
        if "batch_size" in training_data:
            last_step = "parsing batch_size"
            batch_size = int(training_data["batch_size"])
        if "verbose" in training_data:
            last_step = "parsing verbose"
            verbose = int(training_data["verbose"])

        image_file = None
        if "image_file" in req_data:
            image_file = req_data["image_file"]
        # end of saving file naming

        job_manifest = {
            "test_size": test_size,
            "epochs": epochs,
            "batch_size": batch_size,
            "csv_file": csv_file,
            "meta_file": meta_file,
            "image_file": image_file,
            "verbose": verbose
        }

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
        # end of check for csv file
        if not os.path.exists(meta_file):
            last_step = ("Missing meta_file={}").format(
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
                job_manifest=job_manifest,
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
        ml_result_obj = None
        ml_result_obj = MLJobResult(
                user=ml_job_obj.user,
                job=ml_job_obj,
                status="initial",
                csv_file=csv_file,
                meta_file=meta_file,
                test_size=test_size,
                acc_data=acc_data,
                error_data=None)
        ml_result_obj.save()

        log.info(("create_ml_job_record - end "
                  "user.id={} ml_job.id={} ml_result.id={} "
                  "csv_file={} meta_file={}")
                 .format(
                    user_id,
                    ml_job_obj.id,
                    ml_result_obj.id,
                    ml_result_obj.csv_file,
                    ml_result_obj.meta_file))

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
