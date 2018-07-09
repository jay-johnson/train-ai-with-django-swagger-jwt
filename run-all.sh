#!/bin/bash

compose="compose.yml"
if [[ "$1" != "" ]]; then
    if [[ ! -e "$1" ]]; then
        echo "Missing compose file: ${1}"
        exit 1
    else
        compose="$1"
    fi
fi

echo "Starting all containers with: ${compose}"
docker-compose -f $compose up -d

exit 0
