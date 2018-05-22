#!/bin/bash

echo "Tailing Jupyter Logs:"
oc logs -f deployment/jupyter

exit 0
