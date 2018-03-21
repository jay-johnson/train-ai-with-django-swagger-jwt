#!/bin/bash

compose="compose.yml"

echo "Starting all containers with: ${compose}"
docker-compose -f $compose up -d

exit 0
