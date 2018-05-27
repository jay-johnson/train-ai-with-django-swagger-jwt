#!/bin/bash

project="antinex"
# map to template - objects[1].spec.volmes[0].persistentVolumeClaim.claimName
redis_pvc_name="redis-antinex-pvc"
# volume name
redis_pv_name="redis-antinex-pv"
# what path is this volume mounting into the container
redis_pvc_mount_path="/bitnami"

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

echo "Creating Redis - persistent volume"
oc apply -f redis/persistent-volume.json
echo ""

echo "Waiting for volumes to register"
sleep 5

echo "Creating Redis persistent volume claim"
oc apply -f redis/pvc.yml
# oc volume \
#     dc/redis \
#     --add \
#     --claim-size 10G \
#     --claim-name ${redis_pvc_name} \
#     --mount-path ${redis_pvc_mount_path} \
#     --name ${redis_pv_name}
echo ""

echo "Exposing Redis service"
oc expose svc/redis

exit 0
