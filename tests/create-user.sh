#!/bin/bash

user="nex"
pw="123321"
email=""
firstname=""
lastname=""

if [[ "${1}" != "" ]]; then
    user=${1}
fi
if [[ "${ANTINEX_USER}" != "" ]]; then
    user=${ANTINEX_USER}
fi
if [[ "${API_USER}" != "" ]]; then
    user=${API_USER}
fi

if [[ "${2}" != "" ]]; then
    pw=${2}
fi
if [[ "${ANTINEX_PASSWORD}" != "" ]]; then
    pw=${ANTINEX_PASSWORD}
fi
if [[ "${API_PASSWORD}" != "" ]]; then
    pw=${API_PASSWORD}
fi

if [[ "${3}" != "" ]]; then
    email=${3}
fi
if [[ "${ANTINEX_EMAIL}" != "" ]]; then
    email=${ANTINEX_EMAIL}
fi
if [[ "${API_EMAIL}" != "" ]]; then
    email=${API_EMAIL}
fi

if [[ "${4}" != "" ]]; then
    firstname=${4}
fi
if [[ "${ANTINEX_FIRSTNAME}" != "" ]]; then
    firstname=${ANTINEX_FIRSTNAME}
fi
if [[ "${API_FIRSTNAME}" != "" ]]; then
    firstname=${API_FIRSTNAME}
fi

if [[ "${5}" != "" ]]; then
    lastname=${5}
fi
if [[ "${ANTINEX_LASTNAME}" != "" ]]; then
    lastname=${ANTINEX_LASTNAME}
fi
if [[ "${API_LASTNAME}" != "" ]]; then
    lastname=${API_LASTNAME}
fi

auth_url="http://0.0.0.0:8080/users/"
if [[ "${ANTINEX_URL}" != "" ]]; then
    auth_url="${ANTINEX_URL}/users/"
fi

user_login_dict="{\"username\":\"${user}\",\"password\":\"${pw}\",\"email\":\"${email}\",\"first\":\"${firstname}\",\"last\":\"${lastname}\"}"

curl -s -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "${user_login_dict}" ${auth_url}
last_status=$?
if [[ "${last_status}" != 0 ]]; then
    echo "Failed adding new user: ${user}"
    exit 1
else
    exit 0
fi

exit 0
