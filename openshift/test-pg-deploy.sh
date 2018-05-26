#!/bin/bash

project=antinex
test_exists=$(oc project | grep ${project} | wc -l)
first_time_deploy="0"
if [[ "${test_exists}" == "0" ]]; then
    oc new-project ${project}
    first_time_deploy="1"
fi
echo ""
echo "Creating project"
oc project ${project}

echo ""
echo "Getting status"
oc status

echo "Deploying Postgres"
oc new-app postgres/template.json \
    -p DATABASE_SERVICE_NAME=postgres \
    -p POSTGRESQL_USER=antinex \
    -p POSTGRESQL_PASSWORD=antinex \
    -p POSTGRESQL_DATABASE=webapp
echo ""

echo "Waiting for app to register" 
sleep 5

echo "Creating Postgres - persistent volume"
oc apply -f postgres/persistent-volume.json

echo "Waiting for volume to register"
sleep 5

echo "Creating Postgres persistent volume claim"
# map to template - objects[1].spec.volmes[0].persistentVolumeClaim.claimName
pvc_claim_name=postgres-pvc
# map to template - objects[1].spec.volmes[0].persistentVolumeClaim.claimName
pvc_name=postgres-pvc
# what path is this volume mounting into the container
pvc_mount_path=/var/lib/pgsql/data

oc volume \
    dc/postgres \
    --add \
    --claim-size 10G \
    --claim-name ${pvc_claim_name} \
    --name ${pvc_name} \
    --mount-path ${pvc_mount_path}
