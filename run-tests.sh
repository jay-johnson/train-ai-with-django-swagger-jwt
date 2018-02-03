#!/bin/bash

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
