#!/bin/bash

compose="compose.yml"

echo "Stopping stack: ${compose}"
docker-compose -f $compose stop
docker stop postgres pgadmin jupyter redis core api worker pipeline >> /dev/null 2>&1
docker rm postgres pgadmin jupyter redis core api worker pipeline >> /dev/null 2>&1

exit 0
