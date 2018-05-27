#!/bin/bash

project=antinex
test_exists=$(oc project | grep ${project} | wc -l)
first_time_deploy="0"
if [[ "${test_exists}" == "0" ]]; then
    oc new-project ${project}
    first_time_deploy="1"
fi
echo ""
echo "Creating ${project} project"
oc project ${project}

echo ""
echo "Getting Status"
oc status

echo "Deploying Redis"
oc new-app \
    --name=redis \
    ALLOW_EMPTY_PASSWORD=yes \
    --docker-image=bitnami/redis
echo ""

echo "Deploying Postgres"
oc new-app postgres/template.json \
    -p DATABASE_SERVICE_NAME=postgres \
    -p POSTGRESQL_USER=antinex \
    -p POSTGRESQL_PASSWORD=antinex \
    -p POSTGRESQL_DATABASE=webapp
echo ""

echo "Waiting for apps to register" 
sleep 5

echo "Creating Postgres - persistent volume"
oc apply -f postgres/persistent-volume.json
echo ""

echo "Creating Redis - persistent volume"
oc apply -f redis/persistent-volume.json
echo ""

echo "Waiting for volumes to register"
sleep 5

# map to template - objects[1].spec.volmes[0].persistentVolumeClaim.claimName
pg_pvc_claim_name="postgres-pvc"
# map to template - objects[1].spec.volmes[0].persistentVolumeClaim.claimName
pg_pvc_name="postgres-pvc"
# what path is this volume mounting into the container
pg_pvc_mount_path="/var/lib/pgsql/data"

# map to template - objects[1].spec.volmes[0].persistentVolumeClaim.claimName
redis_pvc_name="redis"
# what path is this volume mounting into the container
redis_pvc_mount_path="/bitnami"

echo "Creating Postgres persistent volume claim"
oc volume \
    dc/postgres \
    --add \
    --claim-size 10G \
    --claim-name ${pg_pvc_claim_name} \
    --name ${pg_pvc_name} \
    --mount-path ${pg_pvc_mount_path}
echo "Creating Postgres persistent volume claim"

echo "Creating Redis persistent volume claim"
oc volume \
    dc/redis \
    --add \
    --claim-size 10G \
    --name ${redis_pvc_name} \
    --mount-path ${redis_pvc_mount_path}
echo ""

echo "Exposing Postgres and Redis services"
oc expose svc/postgres
oc expose svc/redis

if [[ "${first_time_deploy}" == "1" ]]; then
    echo "Sleeping for 3 minutes for first time deployment to pull in images"
    sleep 60
    echo "2 more minutes..."
    sleep 60
    echo "1 more minute..."
    sleep 60
    echo "done..."
fi

echo "Deploying AntiNex - Django Rest Framework REST API workers"
oc apply -f worker/deployment.yaml
echo ""

if [[ "${first_time_deploy}" == "1" ]]; then
    echo "Sleeping for 4 minutes for first time deployment to pull in images"
    sleep 60
    echo "3 more minutes..."
    sleep 60
    echo "2 more minutes..."
    sleep 60
    echo "1 more minute..."
    sleep 60
    echo "done..."
fi

echo "Deploying AntiNex - Django Rest Framework REST API workers"
oc apply -f worker/deployment.yaml
echo ""

echo "Deploying AntiNex - AI Core"
oc apply -f core/deployment.yaml
echo ""

echo "Deploying AntiNex - Django Rest Framework REST API server"
oc apply -f api/service.yaml -f api/deployment.yaml 
echo ""

echo "Deploying AntiNex - Network Pipeline consumer"
oc apply -f pipeline/deployment.yaml
echo ""

echo "Deploying Jupyter integrated with AntiNex"
oc apply -f jupyter/service.yaml -f jupyter/deployment.yaml
echo ""

echo "Checking OpenShift cluster status"
oc status
echo ""

echo "Exposing API and Jupyter services"
oc expose svc/api
oc expose svc/jupyter

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
