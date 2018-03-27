from django.conf import settings


def build_worker_result_node(
        req=None):
    """build_worker_result_node

    :param req: incoming request dictionary - not used right now
    """

    api_node = None
    if settings.ANTINEX_WORKER_ENABLED:
        api_node = {
            "source": settings.ANTINEX_API_NAME,
            "auth_url": settings.ANTINEX_RESULT_AUTH_URL,
            "ssl_options": settings.ANTINEX_RESULT_SSL_OPTIONS,
            "exchange": settings.ANTINEX_RESULT_EXCHANGE_NAME,
            "exchange_type": settings.ANTINEX_RESULT_EXCHANGE_TYPE,
            "routing_key": settings.ANTINEX_RESULT_ROUTING_KEY,
            "queue": settings.ANTINEX_RESULT_QUEUE_NAME,
            "delivery_mode": settings.ANTINEX_RESULT_DELIVERY_MODE,
            "task_name": settings.ANTINEX_RESULT_TASK_NAME,
            "manifest": req
        }
    # end of setting up the general api for responses back from the core

    return api_node
# end of build_worker_result_node
