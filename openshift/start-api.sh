#!/bin/bash

oc new-project antinex
oc project antinex

user=postgres
pw=postgres
db=webapp
adminpw=postgres

pg_pod=$(oc get pods | grep postgres | awk '{print $1}' | tail -1)
api_pod=$(oc get pods | grep api | awk '{print $1}')
echo ""
echo "Create the database with:"
echo "oc rsh ${pg_pod}"
echo "/opt/rh/postgresql92/root/usr/bin/createdb ${db}"
echo ""
echo ""
echo "Starting api with:"
oc apply -f api-deployment.yaml
oc apply -f api-service.yaml
oc expose svc/api
echo ""
echo "Run the migration with:"
echo "oc rsh ${api_pod}"
echo "/bin/bash"
echo ". /opt/venv/bin/activate && cd /opt/antinex-api && source /opt/antinex-api/envs/all-dev.env && ./run-migrations.sh"
echo ""
