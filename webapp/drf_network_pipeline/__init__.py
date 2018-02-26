from __future__ import absolute_import, unicode_literals

# http://docs.celeryproject.org/en/master/django/first-steps-with-django.html#using-celery-with-django

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from drf_network_pipeline.celery_config import app as celery_app  # noqa
