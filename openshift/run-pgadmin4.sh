#!/bin/bash

project="antinex"
db_file="./primary-db.sh"
svc_name="pgadmin4-http"
deployment_dir="./.pgdeployment"
repo="https://github.com/jay-johnson/crunchy-containers.git"
first_time_deploy="0"

if [[ "${1}" != "" ]]; then
    db_file="${1}"
fi

if [[ -e ${db_file} ]]; then
    echo "Loading db: ${db_file}"
    . ${db_file}
else
    echo "Missing db file: ${db_file}"
    exit 1
fi

project="${PROJECT}"
repo="${PGADMIN_REPO}"
svc_name="${PGADMIN_SVC_NAME}"
deployment_dir="${PGADMIN_DEPLOYMENT_DIR}"
test_exists=$(oc project | grep ${project} | wc -l)

if [[ "${test_exists}" == "0" ]]; then
    oc new-project ${project}
    first_time_deploy="1"
fi

env | sort | grep PGADMIN

if [[ ! -e ${deployment_dir} ]]; then
    echo "Cloning Crunchy repo:"
    echo "git clone ${repo} ${deployment_dir}"
    git clone ${repo} ${deployment_dir}
    if [[ ! -e ${deployment_dir} ]]; then
        echo "Failed cloning Crunchy repo:"
        echo "git clone ${repo} ${deployment_dir}"
        exit 1
    fi
fi

echo "Creating project"
oc project ${project}

test_svc_exists=$(oc status | grep "svc/${svc_name}" | wc -l)

echo ""
echo "Getting status"
oc status
echo ""

echo "Deploying Crunchy pgAdmin4 web application"
if [[ "${test_svc_exists}" == "0" ]]; then
    echo " - checking file: ${deployment_dir}/examples/kube/${svc_name}/pgadmin4-http.json"
    if [[ ! -e ${deployment_dir}/examples/kube/${svc_name}/pgadmin4-http.json ]]; then
        echo "Installing Crunchy Containers Repository with command:"
        echo "git clone ${repo} ${deployment_dir}"
        git clone ${repo} ${deployment_dir}
        if [[ ! -e ${deployment_dir}/examples/kube/${svc_name}/pgadmin4-http.json ]]; then
            echo "Failed to clone Crunchy pgAdmin4 Deployment repository to: ${deployment_dir} - please confirm it exists"
            ls -lrt ${deployment_dir}
            echo ""
            echo "Tried cloning repository to deployment directory with command:"
            echo "git clone ${repo} ${deployment_dir}"
            echo ""
            exit 1
        else
            echo "Installed Crunchy Containers"
        fi
    else
        pushd ${deployment_dir}
        git checkout ./examples/kube/${svc_name}/pgadmin4-http.json
        git pull
        popd
    fi

    echo "${svc_name} - installing deployment"
    cp pgadmin4/crunchy-template-http.json ${deployment_dir}/examples/kube/${svc_name}/pgadmin4-http.json
    pushd ${deployment_dir}/examples/kube/${svc_name}
    echo ""
    echo "--------------------------------------------------"
    echo "${svc_name} - starting deployment directory: $(pwd)"
    ./run.sh
    echo ""
    echo "${svc_name} - end deployment"
    echo "--------------------------------------------------"
    popd

    test_route=$(oc status | grep "route/${svc_name}" | wc -l)
    if [[ "${test_route}" == "0" ]]; then
        echo "Exposing Service: svc/${svc_name}"
        oc expose svc/${svc_name}
        echo ""
    fi
else
    echo "Detected running Crunchy ${svc_name}: svc/${svc_name}"
fi
