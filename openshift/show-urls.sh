#!/bin/bash

api_url=$(oc status | grep api | grep http | awk '{print $1}')

echo "Testing API Response:"
echo ""
echo "curl -k -i -X GET ${api_url}/swagger/"
curl -k -i -X GET ${api_url}/swagger/
echo ""

exit 0
