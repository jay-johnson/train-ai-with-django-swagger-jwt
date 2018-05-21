#!/bin/bash

echo "Deleting API"
oc delete -f api/service.yaml -f api/deployment.yaml
echo ""

echo "Deleting Workers:"
oc delete -f worker/deployment.yaml
echo ""

echo "Deleting Core:"
oc delete -f core/deployment.yaml
echo ""

echo "Deleting Pipeline:"
oc delete -f pipeline/deployment.yaml
echo ""

echo "Deleting Redis:"
oc delete svc/redis dc/redis
echo ""

echo "Deleting Postgres:"
oc delete svc/postgres dc/postgres
echo ""

echo "Checking Cluster Status:"
oc status
echo ""

exit 0
