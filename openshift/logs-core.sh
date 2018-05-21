#!/bin/bash

echo "Tailing Core Logs:"
oc logs -f deployment/core

exit 0
