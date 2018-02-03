#!/bin/bash

venv=~/.venvs/venvdrfpipeline
env_name=dev

if [[ ! -e ${venv} ]]; then
    mkdir -p -m 755 ~/.venvs >> /dev/null 2>&1
    virtualenv -p python3 ${venv}
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

echo "Activating and installing pips"
source ${venv}/bin/activate && pip install --upgrade -r ./requirements.txt
echo ""

echo "Sourcing: ./envs/${env_name}.env"
source ./envs/${env_name}.env
echo ""

cd webapp

echo ""
which python
pip list
echo ""

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

echo ""
echo "Run ./start.sh to run"
echo ""
