#!/bin/bash

venv=~/.venvs/venvdrfpipeline
env_name=dev

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

if [[ "${SHARED_LOG_CFG}" != "" ]]; then
    echo ""
    echo "Logging config: ${SHARED_LOG_CFG}"
    echo ""
fi

cd webapp

echo ""
echo "Running unit tests"
python manage.py test
last_status=$?
if [[ "${last_status}" == "0" ]]; then
    echo ""
    echo "PASSED - unit tests"
    echo ""
    cd ..
    exit 0
else
    echo ""
    echo ""
    echo "FAILED - unit tests - run manually with:"
    echo ""
    echo "cd webapp; python manage.py test"
    echo ""
    cd ..
    exit 1
fi
