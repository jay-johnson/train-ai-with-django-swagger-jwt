#!/bin/bash

project="antinex"
project_exists=$(oc get projects | grep ${project} | wc -l)

if [[ "${project}" == "default" ]]; then
    echo ""
    echo "Unable to delete the 'default' project"
    echo ""
    exit 1
fi

echo ""

if [[ "${project_exists}" != "0" ]]; then
    echo "Deleting everything under the ${project} project"
    oc delete all --all -n ${project}

    echo "Deleting all Secrets"
    oc delete secrets $(oc get secrets | grep -i opaque | awk '{print $1}')

    echo "Deleting ${project} project"
    oc delete project ${project}

    echo "Checking Cluster Status"
    oc status
    echo ""

    echo "Changing to the default project"
    oc project default
else
    echo "There is no project named: ${project}"
    echo ""

    echo "Current project"
    oc project
    echo ""

    echo "Listing available projects"
    oc get projects

    echo ""
fi

not_done="1"
while [[ "${not_done}" == "1" ]]; do
    project_exists=$(oc get projects | grep ${project} | wc -l)

    if [[ "${project_exists}" == "0" ]]; then
        echo ""
        echo "Successfully deleted: ${project}"
        echo ""
        not_done="0"
    fi
    sleep 1
done

exit 0
