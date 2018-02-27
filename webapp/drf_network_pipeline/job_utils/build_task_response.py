from django.conf import settings
from drf_network_pipeline.pipeline.consts import NOTRUN


def build_task_response(
        status=NOTRUN,
        err="not-set",
        task_name="",
        data=None,
        celery_enabled=settings.CELERY_ENABLED,
        use_cache=settings.CACHEOPS_ENABLED,
        cache_key=None):
    """build_task_response

    :param status: task return status code
    :param err: task error message for debugging
    :param task_name: task label for debugging
    :param data: task return data
    :param celery_enabled: control flag for testing celery tasks
    :param use_cache: use the cached record if available
    :param cache_key: cache the result in this redis key
    """

    task_response_node = {
        "status": status,
        "err": err,
        "task_name": task_name,
        "data": data,
        "celery_enabled": celery_enabled,
        "use_cache": use_cache,
        "cache_key": cache_key
    }

    return task_response_node
# end of build_task_response
