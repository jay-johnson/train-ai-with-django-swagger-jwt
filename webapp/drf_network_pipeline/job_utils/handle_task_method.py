from django.conf import settings
from drf_network_pipeline.pipeline.consts import ERR
from drf_network_pipeline.pipeline.consts import NOTDONE
from spylunking.log.setup_logging import build_colorized_logger


name = 'handle_task_method'
log = build_colorized_logger(
    name=name)


def handle_task_method(
        req_node=None,
        task_method=None,
        get_result=False,
        delay_timeout=settings.CELERY_GET_RESULT_TIMEOUT):
    """handle_task_method

    Wraps task invocation for easier debugging with a
    standardized dictionary status, error, data response

    :param req_node: request tracking data
    :param task_method: task method to run
    :param get_result: get the result from task
    :param delay_timeout: timeout in seconds to wait
    """

    # copy the request into the response
    res_node = req_node
    if not req_node:
        res_node["err"] = ("Missing req_node "
                           "for task={}").format(
                                req_node)
        res_node["status"] = ERR
        res_node["data"] = None
        log.error(res_node["err"])
        return res_node
    if not task_method:
        res_node["err"] = ("Missing task_method "
                           "for task={}").format(
                                req_node)
        res_node["status"] = ERR
        res_node["data"] = None
        log.error(res_node["err"])
        return res_node
    else:
        log.info(("TK START - req_node={}")
                 .format(
                     str(req_node)[0:30]))

        if req_node["celery_enabled"]:
            task_job = task_method(req_node)
            if task_job:
                res_node["job_id"] = task_job.id
                if get_result:
                    log.debug(("waiting={}s for task={}")
                              .format(
                                delay_timeout,
                                res_node["task_name"]))
                    job_res = task_job.get(
                                timeout=delay_timeout)
                    if job_res:
                        res_node["status"] = job_res["status"]
                        res_node["err"] = job_res["err"]
                        res_node["data"] = job_res["data"]
                    else:
                        res_node["status"] = ERR
                        res_node["err"] = ("failed to get task={} "
                                           "result={}").format(
                                                res_node["task_name"],
                                                job_res)
                        log.error(res_node["err"])
                else:
                    res_node["status"] = NOTDONE
                    res_node["err"] = ""
                    res_node["data"] = None
            else:
                res_node["status"] = ERR
                res_node["err"] = ("Celery task failed to start: "
                                   "task={} job={}").format(
                                        res_node["task_name"],
                                        task_job)
                res_node["data"] = None
                log.error(res_node["err"])
            # end if if job started or not
        else:
            res_node = task_method(req_node)
    # end of if valid params or not

    log.info(("TK END - res_node={}")
             .format(
                 str(res_node)[0:32]))
    return res_node
# end of handle_task_method
