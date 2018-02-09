#!/bin/bash

venv=~/.venvs/venvdrfpipeline
env_name=dev

if [[ "${USE_ENV}" != "" ]]; then
    env_name="${USE_ENV}"
fi

if [[ ! -e ../envs/${env_name}.env ]]; then
    echo ""
    echo "Failed to find env file: envs/${env_name}.env"
    echo ""
    exit 1
fi

echo "Activating and installing pips"
source ${venv}/bin/activate
echo ""

echo "Sourcing: ../envs/${env_name}.env"
source ../envs/${env_name}.env
echo ""

export TEST_DATA="./stocks/spy.json"
./build-new-dataset.py
export TEST_DATA="./stocks/dnn-spy.json"
./create-keras-dnn.py
