#!/bin/bash

venv=~/.venvs/venvdrfpipeline/bin/activate
env_name=drf-dev

# support for using venv in other locations
if [[ "${USE_VENV}" != "" ]]; then
    if [[ -e ${USE_VENV}/bin/activate ]]; then
        echo "Using custom virtualenv: ${USE_VENV}"
        venv=${USE_VENV}
    else
        echo "Did not find custom virtualenv: ${USE_VENV}"
        exit 1
    fi
fi

if [[ "${USE_ENV}" != "" ]]; then
    env_name="${USE_ENV}"
fi

if [[ ! -e ./envs/${env_name}.env ]]; then
    echo ""
    echo "Failed to find env file: envs/${env_name}.env"
    echo ""
    exit 1
fi

echo "Activating and installing pips"
. ${venv}/bin/activate
echo ""

echo "Sourcing: ./envs/${env_name}.env"
source ./envs/${env_name}.env
echo ""

cd webapp

echo ""
which python
pip list
echo ""
echo ""
env | grep -E "DJANGO|CELERY" | sort
echo ""

echo ""
echo "Loading Celery environment variables"
echo ""

num_workers=4
log_level=DEBUG
log_file=/tmp/worker.log
worker_module=drf_network_pipeline
worker_name="default@%h"

if [[ "${NUM_WORKERS}" != "" ]]; then
    num_workers=$NUM_WORKERS
fi
if [[ "${LOG_LEVEL}" != "" ]]; then
    log_level=$LOG_LEVEL
fi
if [[ "${LOG_FILE}" != "" ]]; then
    log_file=$LOG_FILE
fi
if [[ "${WORKER_MODULE}" != "" ]]; then
    worker_module=$WORKER_MODULE
fi
if [[ "${WORKER_NAME}" != "" ]]; then
    worker_name=$WORKER_NAME
fi

custom_queues="celery,drf_network_pipeline.users.tasks.task_get_user,drf_network_pipeline.pipeline.tasks.task_ml_process_results,drf_network_pipeline.pipeline.tasks.task_publish_to_core,drf_network_pipeline.pipeline.tasks.task_ml_prepare,drf_network_pipeline.pipeline.tasks.task_ml_job"

echo ""
if [[ "${num_workers}" == "1" ]]; then
    echo "Starting Worker=${worker_module}"
    echo "celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name} -Q ${custom_queues}"
    celery worker -A $worker_module -c ${num_workers} -l ${log_level} -n ${worker_name} -Q $custom_queues
else
    echo "Starting Workers=${worker_module}"
    echo "celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name} --logfile=${log_file} -Q ${custom_queues}"
    celery worker -A $worker_module -c ${num_workers} -l ${log_level} -n ${worker_name} --logfile=${log_file} -Q ${custom_queues}
fi
echo ""
