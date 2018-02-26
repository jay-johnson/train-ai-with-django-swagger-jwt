#!/bin/bash

# this assumes docker is running and docker-compose is installed

echo "Starting redis"
docker-compose -f redis.yml up -d

exit 0
