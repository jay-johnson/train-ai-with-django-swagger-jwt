#!/bin/bash

echo "Logging into deployment/worker"
oc rsh deployment/worker /bin/bash
