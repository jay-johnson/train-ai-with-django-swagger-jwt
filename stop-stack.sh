#!/bin/bash

compose="full-stack-dev.yml"

echo "Stopping stack: ${compose}"
docker-compose -f $compose stop
docker stop postgres redis pgadmin >> /dev/null 2>&1
docker rm postgres redis pgadmin >> /dev/null 2>&1

exit 0
