=======================================
AntiNex on OpenShift Container Platform
=======================================

This will deploy the following containers to OpenShift Container Platform:

#. API Server - Django REST Framework with JWT and Swagger

#. API Worker - Celery Worker Pool

#. Core Worker - AntiNex AI Core Celery Worker

#. Jupyter - Includes ready-to-use AntiNex IPython Notebooks

#. Pipeline - AntiNex Network Pipeline Celery Worker

#. Posgres 10.4 - Crunchy Data Single Primary

#. Redis 3.2

Getting Started
---------------

#.  Clone

    This guide assumes the repository is cloned to the directory:

    **/opt/antinex/api**

    ::

        mkdir -p -m 777 /opt/antinex
        git clone git@github.com:jay-johnson/train-ai-with-django-swagger-jwt.git /opt/antinex/api

#.  Setting up Database Tools

    For preparing Ubuntu 18 to manage the Crunchy containers:

    ::

        sudo apt install golang-go
        mkdir -p -m 777 /opt/antinex
        # on ubuntu 18.04:
        export GOPATH=$HOME/go
        export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
        go get github.com/blang/expenv

#.  Enable Admin Rights for Users

    On the OpenShift Container Platform, add ``cluster-admin`` role to all users that need to deploy AntiNex on OCP

    ::

        [root@ocp39 ~]# oc adm policy add-cluster-role-to-user cluster-admin trex
        cluster role "cluster-admin" added: "trex"
        [root@ocp39 ~]#

#.  Persistent Volumes

    For Postgres and Redis to use a persistent volume, the user must be a **cluster-admin**.

#.  Resources

    Please make sure to give the hosting vm(s) enough memory to run the stack. If you are using [OpenShift Container Platform](https://access.redhat.com/documentation/en-us/openshift_container_platform/3.9/html-single/installation_and_configuration/#install-config-install-rpm-vs-containerized) please use at least 2 CPU cores and 8 GB of RAM.

Login to OpenShift Container Platform
-------------------------------------

Here's an example of logging into OpenShift Container Platform

.. raw:: html

    <a href="https://asciinema.org/a/183593?autoplay=1" target="_blank"><img src="https://asciinema.org/a/183593.png"/></a>

::

    oc login https://ocp39.homelab.com:8443

Deploy
------

Deploy the containers to OpenShift Container Platform

.. raw:: html

    <a href="https://asciinema.org/a/183873?autoplay=1" target="_blank"><img src="https://asciinema.org/a/183873.png"/></a>

**Run Deployment Command**

::

    ./deploy.sh

Check the AntiNex Stack
-----------------------

You can view the **antinex** project's pod on the OpenShift web console:

OpenShift Container Platform:

https://ocp39.homelab.com:8443/console/project/antinex/browse/pods

You can also use the command line:

::

    oc status -v
    In project antinex on server https://ocp39.homelab.com:8443

    http://api-antinex.apps.homelab.com to pod port 8080 (svc/api)
    deployment/api deploys jayjohnson/ai-core:latest
        deployment #1 running for 12 minutes - 1 pod

    http://jupyter-antinex.apps.homelab.com to pod port 8888 (svc/jupyter)
    deployment/jupyter deploys jayjohnson/ai-core:latest
        deployment #1 running for 12 minutes - 1 pod

    http://primary-antinex.apps.homelab.com to pod port 5432 (svc/primary)
    pod/primary runs crunchydata/crunchy-postgres:centos7-10.4-1.8.3

    http://redis-antinex.apps.homelab.com to pod port 6379-tcp (svc/redis)
    dc/redis deploys istag/redis:latest
        deployment #1 deployed 13 minutes ago - 1 pod

    deployment/core deploys jayjohnson/ai-core:latest
    deployment #1 running for 13 minutes - 1 pod

    deployment/pipeline deploys jayjohnson/ai-core:latest
    deployment #1 running for 12 minutes - 1 pod

    deployment/worker deploys jayjohnson/ai-core:latest
    deployment #1 running for 12 minutes - 1 pod

    Info:
    * pod/primary has no liveness probe to verify pods are still running.
        try: oc set probe pod/primary --liveness ...
    * deployment/api has no liveness probe to verify pods are still running.
        try: oc set probe deployment/api --liveness ...
    * deployment/core has no liveness probe to verify pods are still running.
        try: oc set probe deployment/core --liveness ...
    * deployment/jupyter has no liveness probe to verify pods are still running.
        try: oc set probe deployment/jupyter --liveness ...
    * deployment/pipeline has no liveness probe to verify pods are still running.
        try: oc set probe deployment/pipeline --liveness ...
    * deployment/worker has no liveness probe to verify pods are still running.
        try: oc set probe deployment/worker --liveness ...
    * dc/redis has no readiness probe to verify pods are ready to accept traffic or ensure deployment is successful.
        try: oc set probe dc/redis --readiness ...
    * dc/redis has no liveness probe to verify pods are still running.
        try: oc set probe dc/redis --liveness ...

    View details with 'oc describe <resource>/<name>' or list everything with 'oc get all'.

Migrations
----------

Migrations have to run inside an **api** container. Below is a recording of running the initial migration.

OpenShift Container Platform

.. raw:: html

    <a href="https://asciinema.org/a/183874?autoplay=1" target="_blank"><img src="https://asciinema.org/a/183874.png"/></a>

The command from the video is included in the openshift directory, and you can run the command to show how to run a migration. Once the command finishes, you can copy and paste the output into your shell to quickly run a migration:

::

    ./show-migrate-cmds.sh

    Run a migration with:
    oc rsh api-5958c5d995-jjxkt
    /bin/bash
    . /opt/venv/bin/activate && cd /opt/antinex-api && source /opt/antinex-api/envs/openshift-no-hostnames.env && export POSTGRES_HOST=primary && export POSTGRES_DB=webapp && export POSTGRES_USER=antinex && export POSTGRES_PASSWORD=antinex && ./run-migrations.sh
    exit
    exit

Creating a User
---------------

Here's how to create the default user **trex**

OpenShift Container Platform

.. raw:: html

    <a href="https://asciinema.org/a/183661?autoplay=1" target="_blank"><img src="https://asciinema.org/a/183661.png"/></a>

#.  Create a User from the command line

    The commands to create the default user **trex** are:

    ::

        source users/user_1.sh
        ./create-user.sh

#.  Create a User using Swagger

    You can create users using swagger the API's swagger url (here's the default one during creation of this guide):

    http://api-antinex.apps.homelab.com/swagger/

#.  Create a User from a User file

    You can create your own user file's like: **users/user_1.sh** that have the supported environment keys in a file before running. You can also just exported them in the current shell session (but having a resource file will be required in the future):

    Here's the steps to build your own:

    #.  Find the API Service

        ::

            $ oc status | grep svc/api
            http://api-antinex.apps.homelab.com to pod port 8080 (svc/api)

    #.  Confirm it is Discovered by the AntiNex Get API URL Tool

        ::
    
            $ /opt/antinex/api/openshift/get-api-url.sh
            http://api-antinex.apps.homelab.com

    #.  Set the Account Details

        ::

            export API_USER="trex"
            export API_PASSWORD="123321"
            export API_EMAIL="bugs@antinex.com"
            export API_FIRSTNAME="Guest"
            export API_LASTNAME="Guest"
            export API_URL=https://ocp39.homelab.com:8443
            export API_VERBOSE="true"
            export API_DEBUG="false"

    #.  Create the user

        ::

            ./create-user.sh <optional path to user file>

    #.  Get a JWT Token for the New User

        ::

            ./get-token.sh

Train a Deep Neural Network
===========================

Here's how to train a deep neural network using the AntiNex Client and the Django AntiNex dataset:

.. raw:: html

    <a href="https://asciinema.org/a/183875?autoplay=1" target="_blank"><img src="https://asciinema.org/a/183875.png"/></a>

Commands for Training a Deep Neural Network on OpenShift with AntiNex
---------------------------------------------------------------------

#.  Install the AntiNex Client

    ::

        pip install antinex-client

#.  Source User File

    ::

        source ./users/user_1.sh

#.  Train the Deep Neural Network with the Django Dataset

    ::

        ai_train_dnn.py -f ../tests/scaler-full-django-antinex-simple.json -s

#.  Get the Job

    The job from the video was MLJob.id: 3

    ::

        ai_get_job.py -i 3

#.  Get the Job Result

    The job's result from the video was MLJobResult.id: 3

    ::

        ai_get_results.py -i 3

Drop and Restore Database with the Latest Migration
---------------------------------------------------

.. raw:: html

    <a href="https://asciinema.org/a/184069?autoplay=1" target="_blank"><img src="https://asciinema.org/a/184069.png"/></a>

You can drop the database and restore it to the latest migration with this command. Copy and paste the output to run the commands quickly. Make sure to get the second batch or using the ``./show-migrate-cmds.sh`` if you need to migrate at some point in the future.

::

    ./tools/drop-database.sh

Debugging
=========

Tail API Logs
-------------

::

    oc logs -f deployment/api

or

::

    ./logs-api.sh

Tail Worker Logs
----------------

::

    oc logs -f deployment/worker

or

::

    ./logs-worker.sh

Tail AI Core Logs
-----------------

::

    oc logs -f deployment/core

or

::

    ./logs-core.sh

Tail Pipeline Logs
------------------

::

    oc logs -f deployment/pipeline

or

::

    ./logs-pipeline.sh

Change the Entrypoint
---------------------

To keep the containers running just add something like: ``tail -f <some file>`` to keep the container running for debugging issues.

I use:

::

    && tail -f /var/log/antinex/api/api.log

SSH into API Container
----------------------

::

    oc rsh deployment/api /bin/bash

SSH into API Worker Container
-----------------------------

::

    ./ssh-worker.sh

or

::

    oc rsh deployment/worker /bin/bash

SSH into AI Core Container
--------------------------

::

    oc rsh deployment/core /bin/bash

Stop All Containers
-------------------

Stop all the containers without changing the persistent volumes with the command:

::

    ./stop-all.sh

Delete Everything
-----------------

Remove, delete and clean up everything in the AntiNex project with the command:

::

    ./remove-all.sh

Troubleshooting
===============

Permission Errors for Postgres or Redis
---------------------------------------

If you see an error about permission denied in the logs for the primary postgres server or redis that mentions one of these directories:

::

    /pgdata
    /exports/redis-antinex

Then run this command to ssh over to the OCP vm and fix the volume mount directories. Please note, this tool assumes you have copied over the ssh keys and are using NFS mounts for OCP volumes.

::

    ./tools/delete-and-fix-volumes.sh
