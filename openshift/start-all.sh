#!/bin/bash

oc new-project antinex
oc project antinex

user=postgres
pw=postgres
db=webapp
adminpw=postgres

echo "Starting Redis"
oc new-app \
    redis \
    -n antinex \
    --name=redis \
    -l name=redis
sleep 5
oc expose svc/redis
echo ""

echo "Starting Postgres"
oc new-app \
    -e POSTGRESQL_USER=$user \
    -e POSTGRESQL_PASSWORD=$pw \
    -e POSTGRESQL_DATABASE=$db \
    --docker-image=centos/postgresql-96-centos7 \
    -n antinex \
    --name=postgres
sleep 5
oc expose svc/postgres

echo "waiting for service to be up"
sleep 10
pg_pod=$(oc get pods | grep postgres | awk '{print $1}' | tail -1)
echo ""
echo "Create the database with:"
echo "oc rsh ${pg_pod}"
echo "createdb ${db}"
echo "exit"
echo ""
echo ""
echo "Starting api with:"
oc apply -f api-deployment.yaml
oc apply -f api-service.yaml
oc expose svc/api
echo ""
echo "Run the migration with:"
echo "api_pod=\$(oc get pods | grep api | awk '{print \$1}')"
echo 'oc rsh ${api_pod}'
echo "/bin/bash"
echo ". /opt/venv/bin/activate && cd /opt/antinex-api && source /opt/antinex-api/envs/openshift-dev.env && ./run-migrations.sh"
echo ""
