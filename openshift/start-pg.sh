#!/bin/bash

oc new-project dbs
user=postgres
pw=postgrees
db=webapp
adminpw=postgres

echo "Starting Redis"
oc new-app \
    redis \
    -n dbs \
    --name=redis \
    -l name=redis

oc expose svc/redis
echo ""

echo "Starting Postgres"
oc new-app \
    -e POSTGRESQL_USER=$user \
    -e POSTGRESQL_PASSWORD=$pw \
    -e POSTGRESQL_DATABASE=$db \
    -e POSTGRESQL_ADMIN_PASSWORD=$adminpq \
    openshift/postgresql-92-centos7 \
    -n dbs \
    --name=postgres \
    -l name=postgres

oc expose svc/postgres

echo "waiting for service to be up"
sleep 10
pg_pod=$(oc get pods | grep postgres | grep awk '{print $1}')
api_pod=$(oc get pods | grep api | grep awk '{print $1}')
echo ""
echo "Create the database with:"
echo "oc rsh ${pg_pod}"
echo "/opt/rh/postgresql92/root/usr/bin/createdb ${db}"
echo ""
echo ""
echo "Start the api with:"
echo "os project antinex"
echo "oc apply -f api-deployment.yaml"
echo "oc apply -f api-service.yaml"
echo ""
echo "Run the migration with:"
echo "oc project api"
echo "oc rsh ${api_pod}"
echo ". /opt/venv/bin/activate && cd /opt/antinex-api && source /opt/antinex-api/envs/all-dev.env && ./run-migrations.sh"
