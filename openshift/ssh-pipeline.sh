#!/bin/bash

echo "Logging into deployment/pipeline"
oc rsh deployment/pipeline /bin/bash
