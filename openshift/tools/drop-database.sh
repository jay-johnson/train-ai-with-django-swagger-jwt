#!/bin/bash

db=webapp

db_pod=$(oc get pods | grep postgres | awk '{print $1}' | tail -1)

echo ""
echo "Drop the database with:"
echo "oc rsh ${db_pod}"
echo "psql"
echo "drop database ${db};"
echo "\q"
echo "createdb ${db}"
echo "exit"
echo ""

export ANTINEX_SILENT="1"
if [[ -e ./show-migrate-cmds.sh ]]; then
    ./show-migrate-cmds.sh
else
    ../show-migrate-cmds.sh
fi

exit 0
