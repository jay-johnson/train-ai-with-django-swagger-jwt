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

if [[ ! -e ${venv}/bin/activate ]]; then
    echo ""
    echo "Failed to create virtualenv: virtualenv -p python3 ${venv}"
    echo ""
    exit 1
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

echo "Migrating"
python manage.py makemigrations users
python manage.py makemigrations pipeline

echo "Syncing db"
python manage.py migrate --run-syncdb
echo ""

echo "Running makemigrations"
python manage.py makemigrations
echo ""

echo "Running initial migration"
python manage.py migrate --noinput
echo ""

echo "Creating super user - this should only run once"
./create-super-user.sh
echo ""

cd ..

exit 0
