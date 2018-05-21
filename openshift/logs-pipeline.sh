#!/bin/bash

echo "Tailing Pipeline Logs:"
oc logs -f deployment/pipeline

exit 0
