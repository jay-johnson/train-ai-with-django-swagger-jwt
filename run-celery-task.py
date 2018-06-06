#!/usr/bin/env python

import os
import sys
import json
import argparse
from celery import signals
from antinex_utils.log.setup_logging import build_colorized_logger
from celery_loaders.work_tasks.get_celery_app import get_celery_app


name = "run-celery-task"
log = build_colorized_logger(name=name)

parser = argparse.ArgumentParser(description="sending Celery task data")
parser.add_argument(
    "-f",
    help="task data file: path to data file",
    required=True,
    dest="data_file")
parser.add_argument(
    "-t",
    help="task name: drf_network_pipeline.users.tasks.task_get_user",
    required=True,
    dest="task_name")
args = parser.parse_args()


task_name = args.task_name
task_data = None
file_contents = None
if args.data_file:
    if os.path.exists(args.data_file):
        file_contents = json.loads(open(args.data_file).read())
        task_data = {
            "celery_enabled": True,
            "cache_key": None,
            "use_cache": False,
            "data": file_contents
        }
# end of loading the data to send

if not task_data:
    log.error(("Please provide a "
               "path to task_data file with -f <path to file>"))
    sys.exit(1)
# end of checking if there is data to send


# Disable celery log hijacking
# https://github.com/celery/celery/issues/2509
@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass


log.info(("start - {}")
         .format(name))

broker_url = os.getenv(
    "BROKER_URL",
    "redis://localhost:6379/9").strip().lstrip()
backend_url = os.getenv(
    "BACKEND_URL",
    "redis://localhost:6379/10").strip().lstrip()

# comma delimited
tasks_str = os.getenv(
    "INCLUDE_TASKS",
    "drf_network_pipeline.users.tasks")
include_tasks = tasks_str.split(",")

log.info(("connecting Celery={} "
          "broker={} backend={} tasks={}")
         .format(
            name,
            broker_url,
            backend_url,
            include_tasks))

# Get the Celery app using the celery-loaders api
app = get_celery_app(
        name,
        auth_url=broker_url,
        backend_url=backend_url,
        include_tasks=include_tasks)

log.info(("app.broker_url={} calling task={} data={}")
         .format(
            app.conf.broker_url,
            task_name,
            task_data))
task_job = app.send_task(
    task_name,
    (task_data,))
log.info(("calling task={} - started job_id={}")
         .format(
            task_name,
            task_job.id))
task_result = task_job.get()
log.info(("calling task={} - success "
          "job_id={} task_result={}")
         .format(
            task_name,
            task_job.id,
            task_result))

log.info(("end - {}")
         .format(name))

sys.exit(0)
