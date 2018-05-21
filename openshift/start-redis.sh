#!/bin/bash

oc new-app redis
oc expose svc/redis
