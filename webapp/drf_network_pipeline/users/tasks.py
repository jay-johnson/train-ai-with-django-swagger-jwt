from __future__ import absolute_import, unicode_literals
from celery import shared_task
from antinex_utils.log.setup_logging import build_colorized_logger
from django.conf import settings
from drf_network_pipeline.pipeline.consts import SUCCESS
from drf_network_pipeline.pipeline.consts import FAILED
from drf_network_pipeline.pipeline.consts import ERR
from drf_network_pipeline.job_utils.build_task_response import \
    build_task_response
from drf_network_pipeline.users.db_lookup_user import \
    db_lookup_user


name = "user_tasks"
log = build_colorized_logger(name=name)


@shared_task
def task_get_user(
        req_node):
    """task_get_user

    :param req_node: dictionary for lookup values
    """

    label = "task_get_user"

    log.info(("task - {} - start "
              "req_node={}")
             .format(
                label,
                req_node))

    req_data = req_node.get("data", {})
    use_cache = req_node.get("use_cache", settings.CACHEOPS_ENABLED)

    # create the response node from request
    res = build_task_response(
            use_cache=use_cache,
            celery_enabled=req_node["celery_enabled"],
            cache_key=req_node["cache_key"])

    user_id = req_data.get("user_id", None)
    if user_id:
        full_user_res = db_lookup_user(
            user_id=user_id,
            use_cache=use_cache)
        if full_user_res["status"] == SUCCESS:
            res["status"] = SUCCESS
            res["err"] = ""
            res["data"] = full_user_res.get("data", None)
        else:
            res["err"] = ("did not find user_id={}").format(
                            user_id)
            log.info(res["err"])
            res["status"] = FAILED
            res["data"] = None
        # end of looking up user from db
    else:
        res["err"] = ("no user_id in data={}").format(
                        req_data)
        log.info(res["err"])
        res["status"] = ERR
        res["data"] = None
    # end of if user_id found

    log.info(("task - {} result={} - done")
             .format(
                label,
                res))

    return res
# end of task_get_user
