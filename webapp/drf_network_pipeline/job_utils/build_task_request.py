from django.conf import settings
from drf_network_pipeline.pipeline.consts import NOTRUN


def build_task_request(
        status=NOTRUN,
        err="not-set",
        task_name="",
        data=None,
        job_id=None,
        celery_enabled=settings.CELERY_ENABLED,
        use_cache=settings.CACHEOPS_ENABLED,
        cache_record=False,
        cache_key=None):
    """build_task_node

    :param status: task return status code
    :param err: task error message for debugging
    :param task_name: task label for debugging
    :param data: task return data
    :param job_id: task job id
    :param celery_enabled: control flag for testing celery tasks
    :param use_cache: use the cached record if available
    :param cache_record: cache the result in redis after done
    :param cache_key: cache the result in this redis key
    """

    task_node = {
        "status": status,
        "err": err,
        "task_name": task_name,
        "data": data,
        "job_id": job_id,
        "celery_enabled": celery_enabled,
        "use_cache": use_cache,
        "cache_record": cache_record,
        "cache_key": cache_key
    }

    return task_node
# end of build_task_request
