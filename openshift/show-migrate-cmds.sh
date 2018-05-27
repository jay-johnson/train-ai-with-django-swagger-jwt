#!/bin/bash

user=antinex
pw=antinex
db=webapp

api_pod=$(oc get pods | grep api | awk '{print $1}')

if [[ "${ANTINEX_SILENT}" != "1" ]]; then
    echo ""
    echo "Run a migration with:"
fi

echo "oc rsh ${api_pod}"
echo "/bin/bash"
echo ". /opt/venv/bin/activate && cd /opt/antinex-api && source /opt/antinex-api/envs/openshift-dev.env && export POSTGRES_HOST=primary && export POSTGRES_DB=${db} && export POSTGRES_USER=${user} && export POSTGRES_PASSWORD=${pw} && ./run-migrations.sh"
echo "exit"
echo "exit"
echo ""

exit 0
