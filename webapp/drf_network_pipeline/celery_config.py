import os
import django
from celery import Celery
from celery import signals
from spylunking.log.setup_logging import build_colorized_logger


# Disable celery log hijacking
# https://github.com/celery/celery/issues/2509
@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass


name = 'worker'
log = build_colorized_logger(
    name=name)


# Required load order for backend workers
import configurations  # noqa
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "drf_network_pipeline.settings")
os.environ.setdefault(
    "DJANGO_CONFIGURATION",
    "Development")
configurations.setup()  # noqa
import django  # noqa

app = Celery(
    "drf_network_pipeline")

CELERY_TIMEZONE = "UTC"

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY")
app.autodiscover_tasks()
