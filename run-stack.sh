#!/bin/bash

compose="full-stack-dev.yml"

echo "Starting stack: ${compose}"
docker-compose -f $compose up -d

exit 0
