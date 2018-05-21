#!/bin/bash

project=antinex
test_exists=$(oc project | grep ${project} | wc -l)
first_time_deploy="0"
if [[ "${test_exists}" == "0" ]]; then
    oc new-project ${project}
    first_time_deploy="1"
fi
oc project ${project}

echo "Deploying Postgres"
oc new-app postgres/template.json \
    -p DATABASE_SERVICE_NAME=postgres \
    -p POSTGRESQL_USER=antinex \
    -p POSTGRESQL_PASSWORD=antinex \
    -p POSTGRESQL_DATABASE=webapp
echo ""

echo "Deploying Redis"
oc new-app \
    --name=redis \
    ALLOW_EMPTY_PASSWORD=yes \
    --docker-image=bitnami/redis
echo ""

echo "Deploying AntiNex - API Workers"
oc apply -f worker/deployment.yaml
echo ""

if [[ "${first_time_deploy}" == "1" ]]; then
    echo "Sleeping for 3 minutes for first time deployment to pull in images"
    sleep 60
    echo "2 more minutes..."
    sleep 60
    echo "1 more minute..."
    sleep 60
    echo "done..."
fi

echo "Deploying AntiNex - AI Core"
oc apply -f core/deployment.yaml
echo ""

echo "Deploying AntiNex - API"
oc apply -f api/service.yaml -f api/deployment.yaml 
echo ""

echo "Deploying AntiNex - Pipeline Consumer"
oc apply -f pipeline/deployment.yaml
echo ""

echo "Checking Cluster Status:"
oc status
echo ""

echo "Exposing API, Postgres and Redis services"
oc expose svc/api
oc expose svc/postgres
oc expose svc/redis

echo "Waiting for services to start"
sleep 5

echo ""
oc status
echo ""

# If you're using Postgres before 9.6 then you might need to create the database:
#
# echo "------------------------"
# echo "For first time deployment make sure to create the database:"
# ./show-create-db.sh
# echo "------------------------"
# echo ""

echo "------------------------"
echo "If you need to run a database migration you can use:"
echo "./show-migrate-cmds.sh"
echo ""
echo "which should show the commands to perform the migration:"
./show-migrate-cmds.sh
echo "------------------------"
echo ""

exit 0
