#!/usr/bin/env python

import os
import json
from celery import Celery
from spylunking.log.setup_logging import build_colorized_logger
from antinex_utils.utils import ppj


name = "send-worker-publish-to-core"
log = build_colorized_logger(name=name)

log.info("creating celery app")
app = Celery("test-decoupled-app")

broker_settings = {
    "broker_url": os.getenv(
        "ANTINEX_REST_API_BROKER_URL",
        "redis://localhost:6379/9")
}
app.conf.update(**broker_settings)

datafile = "../webapp/drf_network_pipeline/tests/pubsub/publish-to-core.json"
data = {}
with open(datafile, "r") as f:
    data = json.loads(f.read())

# Celery task routing and queue
parent_route = "drf_network_pipeline.pipeline.tasks"
task_name = ("{}.task_publish_to_core").format(
    parent_route)
queue_name = ("{}.task_publish_to_core").format(
    parent_route)

log.info(("sending args={} to broker={} task={}")
         .format(
            ppj(data),
            app.conf["BROKER_URL"],
            task_name))

app.send_task(
    task_name,
    args=[data],
    queue=queue_name)
