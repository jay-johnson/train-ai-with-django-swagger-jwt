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
# export DJANGO_SECRET_KEY=supersecret
# export DJANGO_SECRET_KEY=supersecret
# export DJANGO_DEBUG=yes
# export DJANGO_TEMPLATE_DEBUG=yes
env | grep DJANGO | sort
echo ""

echo ""
echo "Starting Django listening on TCP port 8080"
echo "http://localhost:8080/swagger"
echo ""


python ./manage.py runserver 0.0.0.0:8080
