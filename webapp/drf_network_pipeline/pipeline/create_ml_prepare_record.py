from __future__ import absolute_import, unicode_literals
import json
import uuid
from spylunking.log.setup_logging import build_colorized_logger
from antinex_utils.consts import SUCCESS
from antinex_utils.consts import ERR
from antinex_utils.consts import FAILED
from drf_network_pipeline.pipeline.models import MLPrepare
from drf_network_pipeline.job_utils.build_task_response import \
    build_task_response
from drf_network_pipeline.users.db_lookup_user import \
    db_lookup_user


name = "create_ml_prepare"
log = build_colorized_logger(name=name)


def create_ml_prepare_record(
        req_data=None):
    """create_ml_prepare_record

    :param req_data: dictionary to build the MLPrepare object
    """

    user_obj = None
    ml_prepare_obj = None

    status = FAILED
    last_step = "starting"

    try:

        last_step = "getting user node"
        user_id = req_data.get("user_id", None)

        log.info(("create_ml_prepare - start "
                  "user.id={}")
                 .format(
                    user_id))

        user_res = db_lookup_user(
            user_id=user_id)

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
        ml_prepare_id = None

        status = "initial"
        control_state = "active"
        title = "no title"
        desc = "no desc"
        full_file = None
        clean_file = None
        meta_suffix = "metadata.json"
        output_dir = None
        ds_dir = None
        ds_glob_path = None
        pipeline_files = {}
        post_proc = {}
        label_rules = {}
        meta_data = {}
        version = 1

        if req_data["title"]:
            title = req_data["title"]
        if req_data["desc"]:
            desc = req_data["desc"]
        if req_data["full_file"]:
            last_step = "parsing full_file"
            full_file = req_data["full_file"]
        if req_data["clean_file"]:
            last_step = "parsing clean_file"
            clean_file = req_data["clean_file"]
        if req_data["meta_suffix"]:
            last_step = "parsing meta_suffix"
            meta_suffix = req_data["meta_suffix"]
        if req_data["output_dir"]:
            last_step = "parsing output_dir"
            output_dir = req_data["output_dir"]
        if req_data["ds_dir"]:
            last_step = "parsing ds_dir"
            ds_dir = req_data["ds_dir"]
        if req_data["ds_glob_path"]:
            last_step = "parsing ds_glob_path"
            ds_glob_path = req_data["ds_glob_path"]
        if req_data["pipeline_files"]:
            last_step = "parsing pipeline_files"
            try:
                pipeline_files = json.loads(req_data["pipeline_files"])
            except Exception:
                pipeline_files = req_data["pipeline_files"]
        if "post_proc" in req_data:
            if req_data["post_proc"]:
                last_step = "parsing post_proc"
                try:
                    post_proc = json.loads(req_data["post_proc"])
                except Exception:
                    post_proc = req_data["post_proc"]
        if req_data["meta_data"]:
            last_step = "parsing meta_data"
            try:
                meta_data = json.loads(req_data["meta_data"])
            except Exception:
                meta_data = req_data["meta_data"]
        if "label_rules" in req_data:
            if req_data["label_rules"]:
                last_step = "parsing label_rules"
                try:
                    label_rules = json.loads(req_data["label_rules"])
                except Exception:
                    label_rules = req_data["label_rules"]
        if req_data["version"]:
            version = int(req_data["version"])

        tracking_id = "prep_{}".format(
                        str(uuid.uuid4()))

        ml_prepare_obj = MLPrepare(
                user=user_obj,
                status=status,
                control_state=control_state,
                title=title,
                desc=desc,
                full_file=full_file,
                clean_file=clean_file,
                meta_suffix=meta_suffix,
                output_dir=output_dir,
                ds_dir=ds_dir,
                ds_glob_path=ds_glob_path,
                pipeline_files=pipeline_files,
                post_proc=post_proc,
                label_rules=label_rules,
                meta_data=meta_data,
                tracking_id=tracking_id,
                version=version)

        last_step = "saving"
        log.info("saving prepare")
        ml_prepare_obj.save()
        log.info(("create_ml_prepare - end "
                  "user.id={} ml_prepare.id={}")
                 .format(
                    user_id,
                    ml_prepare_id))

        last_step = ""
        status = SUCCESS

    except Exception as e:
        status = ERR
        last_step = ("create ml_prepare failed last_step='{}' "
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
        "ml_prepare_obj": ml_prepare_obj
    }
    return res
# end of create_ml_prepare_record
