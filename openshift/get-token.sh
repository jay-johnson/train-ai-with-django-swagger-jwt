#!/bin/bash

user="root"
pw="123321"

if [[ "${1}" != "" ]]; then
    user="${1}"
fi

if [[ "${2}" != "" ]]; then
    pw="${2}"
fi

user_login_dict="{ \"username\": \"${user}\", \"password\": \"${pw}\" }"

api_url=$(oc status | grep api | grep http | awk '{print $1}')

curl -s -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "${user_login_dict}" "${api_url}/api-token-auth/"
echo ""
