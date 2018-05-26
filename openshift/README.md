## AntiNex on OpenShift Container Platform

This will deploy the following containers to OpenShift Container Platform:

1. API Server - Django REST Framework with JWT and Swagger
1. API Worker - Celery Worker Pool
1. Core Worker - AntiNex AI Core Celery Worker
1. Jupyter - Comes with Integrated AntiNex Notebooks
1. Pipeline - AntiNex Network Pipeline Celery Worker
1. Posgres 9.6
1. Redis 3.2

### Getting Started

The documents assumed the repository is cloned to the directory:

/opt/antinex/api

```
mkdir -p -m 777 /opt/antinex
git clone git@github.com:jay-johnson/train-ai-with-django-swagger-jwt.git /opt/antinex/api
```

#### Enable Admin Rights for Users

Add ``cluster-admin`` role to all users that need to deploy AntiNex on OCP

```
[root@ocp39 ~]# oc adm policy add-cluster-role-to-user cluster-admin trex
cluster role "cluster-admin" added: "trex"
[root@ocp39 ~]#
```

#### Persistence

For Postgres and Redis to use a persistent volume, the user must be a **cluster-admin**.

#### Resources

Please make sure to give the hosting vm(s) enough memory to run the stack. If you are using [OpenShift Container Platform](https://access.redhat.com/documentation/en-us/openshift_container_platform/3.9/html-single/installation_and_configuration/#install-config-install-rpm-vs-containerized) please use at least 2 CPU cores and 8 GB of RAM.

## Login to OpenShift Container Platform

Here's an example of logging into OpenShift Container Platform

[![asciicast](https://asciinema.org/a/183593.png)](https://asciinema.org/a/183593?autoplay=1)

```
oc login https://ocp39.homelab.com:8443
```

## Deploy

Deploy the containers to OpenShift Container Platform

[![asciicast](https://asciinema.org/a/183657.png)](https://asciinema.org/a/183657?autoplay=1)

### Run Deployment Command

```
./deploy.sh
```

## Check the Stack

You can view the **antinex** project's pod on the OpenShift web console:

OpenShift Container Platform:

https://ocp39.homelab.com:8443/console/project/antinex/browse/pods

You can also use the command line:

```
oc status -v
In project antinex on server https://ocp39.homelab.com:8443

http://api-antinex.apps.homelab.com to pod port 8080 (svc/api)
  deployment/api deploys jayjohnson/ai-core:latest
    deployment #1 running for 3 minutes - 1 pod

http://jupyter-antinex.apps.homelab.com to pod port 8888 (svc/jupyter)
  deployment/jupyter deploys jayjohnson/ai-core:latest
    deployment #1 running for 3 minutes - 1 pod

http://postgres-antinex.apps.homelab.com to pod port postgresql (svc/postgres)
  dc/postgres deploys openshift/postgresql:9.6 
    deployment #1 deployed 7 minutes ago - 1 pod

http://redis-antinex.apps.homelab.com to pod port 6379-tcp (svc/redis)
  dc/redis deploys istag/redis:latest 
    deployment #2 deployed 7 minutes ago - 1 pod
    deployment #1 deployed 7 minutes ago

deployment/worker deploys jayjohnson/ai-core:latest
  deployment #1 running for 7 minutes - 1 pod

deployment/core deploys jayjohnson/ai-core:latest
  deployment #1 running for 3 minutes - 1 pod

deployment/pipeline deploys jayjohnson/ai-core:latest
  deployment #1 running for 3 minutes - 1 pod

Warnings:
  * dc/redis references a volume which may only be used in a single pod at a time - this may lead to hung deployments

Info:
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
```

## Migrations

Migrations have to run inside an **api** container. Below is a recording of running the initial migration.

OpenShift Container Platform

[![asciicast](https://asciinema.org/a/183660.png)](https://asciinema.org/a/183660?autoplay=1)

The command from the video is included in the openshift directory, and you can run the command to show how to run a migration. Once the command finishes, you can copy and paste the output into your shell to quickly run a migration:

```
./show-migrate-cmds.sh

Run a migration with:
oc rsh api-57f45c99b-n9nxq
/bin/bash
. /opt/venv/bin/activate && cd /opt/antinex-api && source /opt/antinex-api/envs/openshift-dev.env && export POSTGRES_DB=webapp && export POSTGRES_USER=antinex && export POSTGRES_PASSWORD=antinex && ./run-migrations.sh
exit
exit

```

## Creating a User

Here's how to create the default user **trex**

OpenShift Container Platform

[![asciicast](https://asciinema.org/a/183661.png)](https://asciinema.org/a/183661?autoplay=1)

### Create Default User trex

The commands to create the default user **trex** are:

```
export ANTINEX_URL=$(./get-api-url.sh)
./create-user.sh
```

### Create User Using Swagger

You can create users using swagger the API's swagger url (here's the default one during creation of this guide):

http://http://api-antinex.apps.homelab.com/swagger/

### Create User From User File

You can define a user file with these environment keys in a file before running. You can also just exported them in the current shell session (but having a resource file will be required in the future):

1. Find the API Service

```
$ oc status | grep svc/api
http://api-antinex.apps.homelab.com to pod port 8080 (svc/api)
```

1. Confirm it is Discovered by the AntiNex Get API URL Tool

```
$ /opt/antinex/api/openshift/get-api-url.sh
http://api-antinex.apps.homelab.com
```

1. Set the Account Details

```
export API_USER="trex"
export API_PASSWORD="123321"
export API_URL="$(/opt/antinex/api/openshift/get-api-url.sh)"
export API_EMAIL="bugs@antinex.com"
export API_FIRSTNAME="Guest"
export API_LASTNAME="Guest"
export API_VERBOSE="true"
export API_DEBUG="false"
```

1. Create the user

```
./create-user.sh <optional path to user file>
```

1. Get a JWT Token for the New User

```
./get-token.sh
```

## Train a Deep Neural Network

Here's how to train a deep neural network using the AntiNex Client and the Django AntiNex dataset:

[![asciicast](https://asciinema.org/a/182848.png)](https://asciinema.org/a/182848?autoplay=1)

### Commands for Training a Deep Neural Network on OpenShift with AntiNex

1. Install the AntiNex Client

```
pip install antinex-client
```

2. Set the API URL for the AntiNex Client

```
export API_URL="$(/opt/antinex/api/openshift/get-api-url.sh)"
```

3. Train the Deep Nerual Network with the Django Dataset

```
ai_train_dnn.py -f ../tests/scaler-full-django-antinex-simple.json -s
```

4. Get the Job

The job from the video was MLJob.id: 6

```
ai_get_job.py -i 6
```

5. Get the Job Result

The job's result from the video was MLJobResult.id: 6

```
ai_get_results.py -i 6
```

## Drop and Restore Database with the Latest Migration

[![asciicast](https://asciinema.org/a/182822.png)](https://asciinema.org/a/182822?autoplay=1)

You can drop the database and restore it to the latest migration with this command. Copy and paste the output to run the commands quickly. Make sure to get the second batch or using the ``./show-migrate-cmds.sh`` if you need to migrate at some point in the future.

```
./tools/drop-database.sh
```

## Debugging

### Tail API Logs

```
oc logs -f deployment/api
```

or

```
./logs-api.sh
```

### Tail Worker Logs

```
oc logs -f deployment/worker
```

or

```
./logs-worker.sh
```

### Tail AI Core Logs

```
oc logs -f deployment/core
```

or

```
./logs-core.sh
```

### Tail Pipeline Logs

```
oc logs -f deployment/pipeline
```

or

```
./logs-pipeline.sh
```

### Change the Entrypoint

To keep the containers running just add something like: ```tail -f <some file>``` to keep the container running for debugging issues.

I use:

```
&& tail -f /var/log/antinex/api/api.log
```

### SSH into API Container

```
oc rsh deployment/api /bin/bash
```

### SSH into API Worker Container

```
./ssh-worker.sh
```

or

```
oc rsh deployment/worker /bin/bash
```

### SSH into AI Core Container

```
oc rsh deployment/core /bin/bash
```

### Stop All Containers

Stop all the containers without changing the persistent volumes with the command:

```
./stop-all.sh
```

### Delete Everything

Remove, delete and clean up everything in the AntiNex project with the command:

```
./remove-all.sh
```
