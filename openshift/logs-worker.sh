#!/bin/bash

echo "Tailing Worker Logs:"
oc logs -f deployment/worker

exit 0
