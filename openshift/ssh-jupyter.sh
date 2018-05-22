#!/bin/bash

echo "Logging into deployment/jupyter"
oc rsh deployment/jupyter /bin/bash
