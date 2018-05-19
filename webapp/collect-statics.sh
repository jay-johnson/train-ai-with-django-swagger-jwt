#!/bin/bash

venv=~/.venvs/venvdrfpipeline

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

if [[ -e ${venv}/bin/activate ]]; then
    echo "Activating and pips: ${venv}/bin/activate"
    . ${venv}/bin/activate
    echo ""
else
    if [[ -e /opt/venv/bin/activate ]]; then
        echo "Activating /opt/venv and pips"
        . /opt/venv/bin/activate
        echo ""
    fi
fi

if [[ "${COLLECT_STATICS}" == "1" ]]; then
    echo "Collecting static files"
    python manage.py collectstatic --noinput >> /dev/null
    echo ""
else
    echo "Collect static disabled COLLECT_STATICS=${COLLECT_STATICS}"
fi

exit 0
