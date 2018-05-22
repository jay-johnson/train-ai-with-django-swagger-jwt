#!/bin/bash

user="root"
pw="123321"

if [[ "${1}" != "" ]]; then
    user="${1}"
fi

if [[ "${ANTINEX_USER}" != "" ]]; then
    user="${ANTINEX_USER}"
fi

if [[ "${2}" != "" ]]; then
    pw="${2}"
fi

if [[ "${ANTINEX_PASSWORD}" != "" ]]; then
    pw="${ANTINEX_PASSWORD}"
fi

user_login_dict="{ \"username\": \"${user}\", \"password\": \"${pw}\" }"

api_url=$(oc status | grep api | grep http | awk '{print $1}')
if [[ "${api_url}" == "" ]]; then
    api_url="${ANTINEX_URL}"
fi

# echo "curl -s -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '${user_login_dict}' ${api_url}/api-token-auth/"
curl -s -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "${user_login_dict}" "${api_url}/api-token-auth/"
echo ""
