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

echo "Activating pips: ${venv}/bin/activate"
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
log_level=INFO
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

if [[ "${SHARED_LOG_CFG}" != "" ]]; then
    echo ""
    echo "Logging config: ${SHARED_LOG_CFG}"
    echo ""
fi

if  [[ "${ANTINEX_API_NUM_WORKERS}" != "" ]]; then
    num_workers=${ANTINEX_API_NUM_WORKERS}
fi

# Use the WORKER_EXTRA_ARGS to pass in specific args:
# http://docs.celeryproject.org/en/latest/reference/celery.bin.worker.html
#
# example args from 4.2.0:
# --without-heartbeat
# --heartbeat-interval N
# --without-gossip
# --without-mingle

if [[ "${ANTINEX_API_WORKER_ARGS}" != "" ]]; then
    echo "Launching custom api worker=${ANTINEX_API_WORKER_ARGS}"
    celery worker ${ANTINEX_API_WORKER_ARGS}
elif [[ "${num_workers}" == "1" ]]; then
    echo "Starting worker=${worker_module}"
    echo "celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name} -Q ${custom_queues} ${WORKER_EXTRA_ARGS}"
    celery worker -A $worker_module -c ${num_workers} -l ${log_level} -n ${worker_name} -Q $custom_queues ${WORKER_EXTRA_ARGS}
else
    echo "Starting workers=${worker_module}"
    echo "celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name} --logfile=${log_file} -Q ${custom_queues} ${WORKER_EXTRA_ARGS}"
    celery worker -A $worker_module -c ${num_workers} -l ${log_level} -n ${worker_name} --logfile=${log_file} -Q ${custom_queues} ${WORKER_EXTRA_ARGS}
fi
echo ""
