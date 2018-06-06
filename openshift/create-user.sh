#!/bin/bash

user_file="./users/user_1.sh"
if [[ "${1}" != "" ]]; then
    if [[ -e ${1} ]]; then
        user_file="${1}"
    else
        echo "Did not find user_file: ${1}"
        exit 1
    fi
fi

echo "Loading user env: ${user_file}" 
source ${user_file}

# View the AntiNex credentials for debugging:
# echo ""
# env | grep ANTINEX_ | sort
# echo ""

export ANTINEX_URL=$(./get-api-url.sh)
../tests/create-user.sh
if [[ "${?}" != "0" ]]; then
    echo "Failed creating OpenShift user: ${ANTINEX_USER}"
    exit 1
fi

exit 0
