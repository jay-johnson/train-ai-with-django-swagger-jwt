#!/bin/bash

curl -s -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ "username": "root", "password": "123321" }' 'http://0.0.0.0:8080/api-token-auth/'
echo ""
