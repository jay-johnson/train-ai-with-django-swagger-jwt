#!/bin/bash

venv=~/.venvs/venvdrfpipeline
env_name=drf-dev
webapp_host="localhost"
webapp_port="8080"

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

if [[ "${WEBAPP_HOST}" != "" ]]; then
    webapp_host="${WEBAPP_HOST}"
fi

if [[ "${WEBAPP_PORT}" != "" ]]; then
    webapp_port="${WEBAPP_PORT}"
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
env | grep DJANGO | sort
echo ""

# do not run these in the container in openshift
if [[ "${SKIP_BUILD_DOCS}" != "1" ]]; then
    echo ""
    echo "Deploying Sphinx docs"
    ./build-docs.sh
    echo ""
fi

# do not run these in the container in openshift
if [[ "${SKIP_COLLECT_STATICS}" != "1" ]]; then
    echo ""
    echo "Deploying Statics"
    ./collect-statics.sh
    echo ""
fi

if [[ "${SHARED_LOG_CFG}" != "" ]]; then
    echo ""
    echo "Logging config: ${SHARED_LOG_CFG}"
    echo ""
fi

echo ""
echo "Starting Django listening on TCP port ${webapp_port}"
echo "http://${webapp_host}:${webapp_port}/swagger"
echo ""
# runserver has issues with
# threads which break keras
# python ./manage.py runserver 0.0.0.0:8080

if [[ "${APP_SERVER}" == "uwsgi" ]]; then
    uwsgi ./django-uwsgi.ini --thunder-lock
else
    if [[ "${DJANGO_DEBUG}" == "yes" ]]; then
        gunicorn -c ./django-gunicorn.py drf_network_pipeline.wsgi
    else
        gunicorn -c ./django-gunicorn.py drf_network_pipeline.wsgi
    fi
fi
