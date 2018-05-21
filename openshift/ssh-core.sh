#!/bin/bash

echo "Logging into deployment/core"
oc rsh deployment/core /bin/bash
