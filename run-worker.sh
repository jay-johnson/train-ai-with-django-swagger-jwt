#!/bin/bash

source ~/.venvs/venvdrfpipeline/bin/activate
env_name=drf-dev

if [[ "${USE_ENV}" != "" ]]; then
    env_name="${USE_ENV}"
fi

if [[ ! -e ./envs/${env_name}.env ]]; then
    echo ""
    echo "Failed to find env file: envs/${env_name}.env"
    echo ""
    exit 1
fi

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

num_workers=1
log_level=DEBUG
worker_module=drf_network_pipeline
worker_name="default@%h"

if [[ "${NUM_WORKERS}" != "" ]]; then
    num_workers=$NUM_WORKERS
fi
if [[ "${LOG_LEVEL}" != "" ]]; then
    log_level=$LOG_LEVEL
fi
if [[ "${WORKER_MODULE}" != "" ]]; then
    worker_module=$WORKER_MODULE
fi
if [[ "${WORKER_NAME}" != "" ]]; then
    worker_name=$WORKER_NAME
fi

echo ""
if [[ "${num_workers}" == "1" ]]; then
    echo "Starting Worker=${worker_module}"
    echo "celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name}"
    celery worker -A $worker_module -c ${num_workers} -l ${log_level} -n ${worker_name}
else
    echo "Starting Workers=${worker_module}"
    echo "celery worker multi -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name}"
    celery worker multi -A $worker_module -c ${num_workers} -l ${log_level} -n ${worker_name}
fi
echo ""
