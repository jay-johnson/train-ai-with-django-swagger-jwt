from django.conf import settings
from antinex_utils.utils import ppj
from drf_network_pipeline.pipeline.consts import SUCCESS
from drf_network_pipeline.pipeline.consts import ERR
from drf_network_pipeline.pipeline.consts import NOTRUN
from drf_network_pipeline.pipeline.consts import NOTDONE
from drf_network_pipeline.job_utils.build_task_request import \
    build_task_request
from drf_network_pipeline.job_utils.build_task_response import \
    build_task_response
from drf_network_pipeline.job_utils.handle_task_method import \
    handle_task_method
from antinex_utils.log.setup_logging import build_colorized_logger


name = "run-task"
log = build_colorized_logger(name=name)


def run_task(
        task_method=None,
        task_name="please-set-name",
        req_data=None,
        get_result=False,
        delay_timeout=settings.CELERY_GET_RESULT_TIMEOUT,
        use_cache=settings.CACHEOPS_ENABLED,
        cache_record=False,
        cache_key=None):

    """run_task

    Handles Celery sync/async task processing

    :param task_method: requested method
    :param task_name: name of the task for logging
    :param req_data: requested data
    :param get_result: get the result from task
    :param delay_timeout: seconds to wait for the task to finish
    :param use_cache: use the cached record if available
    :param cache_record: cache the result in redis after done
    :param cache_key: cache the result in this redis key
    """

    req_node = build_task_request(
        task_name=task_name,
        use_cache=use_cache,
        cache_record=cache_record,
        cache_key=cache_key,
        data=req_data)
    res_node = build_task_response(
        status=NOTRUN,
        data=None,
        err="not-run")

    try:

        res_node = handle_task_method(
            req_node=req_node,
            get_result=get_result,
            delay_timeout=delay_timeout,
            task_method=task_method)

        if "celery_enabled" not in res_node:
            log.error(("Invalid return node from task={} "
                       "task_method={} with req_node={} "
                       "returned data={}")
                      .format(
                          task_name,
                          task_method,
                          ppj(req_node),
                          ppj(res_node)))

        if res_node["status"] == SUCCESS:
            log.info(("celery={} - running task with data={}")
                     .format(
                        res_node["celery_enabled"],
                        str(res_node["data"])[0:32]))
        elif not get_result and res_node["status"] == NOTDONE:
            log.info(("celery={} - running task with data={}")
                     .format(
                        res_node["celery_enabled"],
                        str(res_node["data"])[0:32]))
        else:
            res_node["data"] = None
            res_node["status"] = res_node["status"]
            res_node["err"] = ("task={} method={} "
                               "status={} err={}").format(
                                    task_name,
                                    task_method,
                                    res_node["status"],
                                    res_node["err"])
            log.error(("Failed {}")
                      .format(
                          res_node["err"]))
        # end of handling success/failure

    except Exception as e:
        res_node = build_task_response(
            status=ERR,
            data=None,
            err=("Failed to run {} celery={} "
                 "with ex={}").format(
                    task_name,
                    res_node.get(
                        "celery_enabled",
                        None),
                    e))
        log.error(res_node["err"])
    # try/ex handling Celery task

    return res_node
# end of run_task
