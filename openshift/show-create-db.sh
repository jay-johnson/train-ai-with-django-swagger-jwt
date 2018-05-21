#!/bin/bash

db=webapp

db_pod=$(oc get pods | grep postgres | awk '{print $1}' | tail -1)

echo ""
echo "Create the initial database with:"
echo "oc rsh ${db_pod}"
echo "createdb ${db}"
echo "exit"
echo ""

exit 0
