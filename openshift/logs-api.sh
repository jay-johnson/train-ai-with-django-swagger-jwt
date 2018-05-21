#!/bin/bash

echo "Tailing API Logs:"
oc logs -f deployment/api

exit 0
