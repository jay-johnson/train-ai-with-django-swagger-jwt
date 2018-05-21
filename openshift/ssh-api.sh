#!/bin/bash

echo "Logging into deployment/api"
oc rsh deployment/api /bin/bash
