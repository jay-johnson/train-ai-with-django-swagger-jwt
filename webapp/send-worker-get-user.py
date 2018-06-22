#!/usr/bin/env python

import os
import json
from celery import Celery
from django.conf import settings
from spylunking.log.setup_logging import build_colorized_logger
from antinex_utils.utils import ppj


name = "send-worker-get-user"
log = build_colorized_logger(name=name)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "drf_network_pipeline.settings")

log.info("creating celery app")
app = Celery("test-app")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY")

app.autodiscover_tasks(
    lambda: settings.INSTALLED_APPS)

datafile = "./drf_network_pipeline/tests/pubsub/get-user.json"
data = {}
with open(datafile, "r") as f:
    data = json.loads(f.read())

# Celery task routing and queue
parent_route = "drf_network_pipeline.users.tasks"
task_name = ("{}.task_get_user").format(
    parent_route)
queue_name = ("{}.task_get_user").format(
    parent_route)

log.info(("sending args={} to broker={} task={}")
         .format(
            ppj(data),
            app.conf["BROKER_URL"],
            task_name))

task_res = app.send_task(
    task_name,
    args=[data],
    queue=queue_name)

log.info(("task={} task.id={} result={}")
         .format(
            task_name,
            task_res.id,
            ppj(task_res.get())))
