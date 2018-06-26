#!/bin/bash

project="antinex"
redis_pv="redis-antinex-pv"
redis_pvc="redis-antinex-pvc"
pg_service_name="primary"
pg_deployment_dir="./.pgdeployment"
pg_repo="https://github.com/jay-johnson/crunchy-containers.git"
include_pgadmin="1"
test_exists=$(oc project | grep ${project} | wc -l)
test_svc_pg_exists=$(oc status | grep "svc/${pg_service_name}" | wc -l)
test_pv_redis_exists=$(oc get pv | grep ${redis_pv} | wc -l)
test_pvc_redis_exists=$(oc get pvc | grep ${redis_pvc} | wc -l)

splunk_enabled="0"
if [[ "${1}" == "splunk" ]] || [[ "${1}" == "splunkenterprise" ]]; then
    splunk_enabled="1"
    echo "splunk enabled"
fi

first_time_deploy="0"
if [[ "${test_exists}" == "0" ]]; then
    oc new-project ${project}
    first_time_deploy="1"
fi

if [[ ! -d ${pg_deployment_dir} ]]; then
    mkdir -p -m 777 ${pg_deployment_dir}
fi

if [[ "${DISABLE_PGADMIN}" == "1" ]]; then
    include_pgadmin="0"
fi

echo ""
echo "Creating ${project} project"
oc project ${project}

echo ""
echo "Getting Status"
oc status

# start the AntiNex docker image download as it can take a few minutes
echo "Deploying AntiNex - AI Core"
if [[ "${splunk_enabled}" == "1" ]]; then
    echo " - core/log_to_splunk_deployment.yaml"
    oc apply -f core/log_to_splunk_deployment.yaml
else
    echo " - core/deployment.yaml"
    oc apply -f core/deployment.yaml
fi
echo ""

echo "Deploying Redis"
oc new-app \
    --name=redis \
    ALLOW_EMPTY_PASSWORD=yes \
    --docker-image=bitnami/redis
echo ""

echo "Deploying Crunchy Postgres Single Primary Database"
source ./primary-db.sh
if [[ "${test_svc_pg_exists}" == "0" ]]; then
    if [[ ! -e ${pg_deployment_dir}/examples/kube/primary/primary.json ]]; then
        echo "Installing Crunchy Containers Repository with command:"
        echo "git clone ${pg_repo} ${pg_deployment_dir}"
        git clone ${pg_repo} ${pg_deployment_dir}
        if [[ ! -e ${pg_deployment_dir}/examples/kube/primary/primary.json ]]; then
            echo "Failed to clone Crunchy Postgres Deployment repository to: ${pg_deployment_dir} - please confirm it exists"
            ls -lrt ${pg_deployment_dir}
            echo ""
            echo "Tried cloning repository to deployment directory with command:"
            echo "git clone ${pg_repo} ${pg_deployment_dir}"
            echo ""
            exit 1
        else
            echo "Installed Crunchy Containers"
        fi
    else
        pushd ${pg_deployment_dir}
        git checkout ./examples/kube/primary/primary.json
        git pull
        popd
    fi
    cp postgres/crunchy-template.json ${pg_deployment_dir}/examples/kube/primary/primary.json
    pushd ${pg_deployment_dir}/examples/kube/primary
    ./run.sh
    popd
else
    echo "Detected running Crunchy Postgres Database: svc/${pg_service_name}"
fi

echo ""

if [[ "${test_pv_redis_exists}" == "0" ]]; then
    echo "Creating Redis - persistent volume"
    oc apply -f redis/pv.yml
    echo ""
    echo "Waiting for volumes to register"
    sleep 5
else
    echo "Redis persistent volume: ${redis_pv} already exists"
    oc get pv
    echo ""
fi

if [[ "${test_pvc_redis_exists}" == "0" ]]; then
    echo "Creating Redis persistent volume claim: ${redis_pvc}"
    oc apply -f redis/pvc.yml
    echo ""
else
    echo "Updating Redis persistent volume claim: ${redis_pvc}"
    oc apply -f redis/pvc.yml
    echo ""
fi

echo "Checking if Postgres Database is ready"
echo ""

not_done=1
while [[ "${not_done}" == "1" ]]; do
    test_pg_svc=$(oc status -v | grep 'svc/primary' | wc -l)
    if [[ "${test_pg_svc}" != "0" ]]; then
        echo "Exposing Postgres Database service"
        oc expose svc/primary
        echo ""
        not_done="0"
    fi
    sleep 1
done

echo "Checking if Redis is ready"
echo ""

not_done=1
while [[ "${not_done}" == "1" ]]; do
    test_rd_svc=$(oc status -v | grep 'svc/redis' | wc -l)
    if [[ "${test_rd_svc}" != "0" ]]; then
        echo "Exposing Redis service"
        oc expose svc/redis
        echo ""
        not_done="0"
    fi
    sleep 1
done

echo "Checking if AntiNex Core is ready"
echo ""

not_done=1
while [[ "${not_done}" == "1" ]]; do
    test_core_deployment=$(oc status -v | grep 'deployment/core' | wc -l)
    if [[ "${test_core_deployment}" != "0" ]]; then
        echo "AntiNex Core is running"
        oc status -v | grep deployment/core
        echo ""
        not_done="0"
    fi
    sleep 1
done

echo "Deploying AntiNex - Django Rest Framework REST API workers"
if [[ "${splunk_enabled}" == "1" ]]; then
    echo " - worker/log_to_splunk_deployment.yaml"
    oc apply -f worker/log_to_splunk_deployment.yaml
else
    echo " - worker/deployment.yaml"
    oc apply -f worker/deployment.yaml
fi
echo ""

echo "Deploying AntiNex - Django Rest Framework REST API server"
if [[ "${splunk_enabled}" == "1" ]]; then
    echo " - api/log_to_splunk_deployment.yaml"
    oc apply -f api/service.yaml -f api/log_to_splunk_deployment.yaml
else
    echo " - pipeline/deployment.yaml"
    oc apply -f api/service.yaml -f api/deployment.yaml
fi
echo ""

echo "Deploying AntiNex - Network Pipeline consumer"
if [[ "${splunk_enabled}" == "1" ]]; then
    echo " - pipeline/log_to_splunk_deployment.yaml"
    oc apply -f pipeline/log_to_splunk_deployment.yaml
else
    echo " - pipeline/deployment.yaml"
    oc apply -f pipeline/deployment.yaml
fi
echo ""

echo "Deploying Jupyter integrated with AntiNex"
if [[ "${splunk_enabled}" == "1" ]]; then
    echo " - jupyter/log_to_splunk_deployment.yaml"
    oc apply -f jupyter/service.yaml -f jupyter/log_to_splunk_deployment.yaml
else
    echo " - jupyter/deployment.yaml"
    oc apply -f jupyter/service.yaml -f jupyter/deployment.yaml
fi
echo ""

echo "Checking OpenShift cluster status"
oc status
echo ""

echo "Exposing API and Jupyter services"
oc expose svc/api
oc expose svc/jupyter
echo ""

if [[ "${include_pgadmin}" == "1" ]]; then
    echo "Starting pgAdmin4"
    ./run-pgadmin4.sh
    echo ""
else
    echo "Skipping pgadmin4"
fi

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
