#!/bin/bash

if [[ "${COLLECT_STATICS}" == "1" ]]; then
    echo ""
    echo "Collecting static files"
    python manage.py collectstatic --noinput >> /dev/null
    echo ""
else
    echo "Collect static disabled COLLECT_STATICS=${COLLECT_STATICS}"
fi

exit 0
