#!/bin/bash

venv=~/.venvs/venvdrfpipeline
env_name=dev

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
source ${venv}/bin/activate
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



if [[ "${MULTI_TENANT}" == "1" ]]; then
    echo ""
    echo "Starting Multi-Tenant Django listening on TCP port 8080"
    echo "http://localhost:8080/swagger"
    echo ""
    uwsgi ./django-uwsgi.ini --thunder-lock
else
    echo ""
    echo "Starting Django listening on TCP port 8080"
    echo "http://localhost:8080/swagger"
    echo ""
    python ./manage.py runserver 0.0.0.0:8080
fi
