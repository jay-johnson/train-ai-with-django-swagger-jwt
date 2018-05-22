#!/bin/bash

api_url=$(oc status | grep api | grep http | awk '{print $1}')
echo "${api_url}"

exit 0
