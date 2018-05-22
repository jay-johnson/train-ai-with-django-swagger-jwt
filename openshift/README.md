## AntiNex on OpenShift

This will deploy the following containers to OpenShift:

1. API Server - Django REST Framework with JWT and Swagger
1. API Worker - Celery Worker Pool
1. Core Worker - AntiNex AI Core Celery Worker
1. Pipeline - AntiNex Network Pipeline Celery Worker
1. Posgres 9.6
1. Redis 3.2

As a note, please make sure to give the hosting vm(s) enough memory to run the stack. If you are using Minishift (https://github.com/minishift/minishift) make sure to start the vm with enough CPU and memory. Here is an example command:

```
minishift start --cpus 3 --memory 8GB --vm-driver=virtualbox
```

## Login to OpenShift

Here's an example of logging into a local Minishift instance:

[![asciicast](https://asciinema.org/a/182791.png)](https://asciinema.org/a/182791?autoplay=1)

```
oc login https://192.168.99.103:8443
```

## Deploy

Deploy the containers:

[![asciicast](https://asciinema.org/a/182796.png)](https://asciinema.org/a/182796?autoplay=1)

```
./deploy.sh
```

## Check the Stack

You can view the **antinex** project's pod on the OpenShift web console:

https://192.168.99.103:8443/console/project/antinex/browse/pods

You can also use the command line:

```
oc status
In project antinex on server https://192.168.99.103:8443

http://api-antinex.192.168.99.103.nip.io to pod port 8080 (svc/api)
  deployment/api deploys jayjohnson/ai-core:latest
    deployment #1 running for 12 minutes - 1 pod

http://postgres-antinex.192.168.99.103.nip.io to pod port postgresql (svc/postgres)
  dc/postgres deploys openshift/postgresql:9.6
    deployment #1 deployed 16 minutes ago - 1 pod

http://redis-antinex.192.168.99.103.nip.io to pod port 6379-tcp (svc/redis)
  dc/redis deploys istag/redis:latest
    deployment #1 deployed 16 minutes ago - 1 pod

deployment/pipeline deploys jayjohnson/ai-core:latest
  deployment #1 running for 12 minutes - 1 pod

deployment/worker deploys jayjohnson/ai-core:latest
  deployment #1 running for 16 minutes - 1 pod

deployment/core deploys jayjohnson/ai-core:latest
  deployment #1 running for 12 minutes - 1 pod
```

## Migrations

Migrations have to run inside an **api** container. Below is a recording of running the initial migration.

[![asciicast](https://asciinema.org/a/182811.png)](https://asciinema.org/a/182811?autoplay=1)

The command from the video is included in the openshift directory, and you can run the command to show how to run a migration. Once the command finishes, you can copy and paste the output into your shell to quickly run a migration:

```
./show-migrate-cmds.sh

Run a migration with:
oc rsh api-dd5b7bf6-hq758
/bin/bash
. /opt/venv/bin/activate && cd /opt/antinex-api && source /opt/antinex-api/envs/openshift-dev.env && export POSTGRES_DB=webapp && export POSTGRES_USER=antinex && export POSTGRES_PASSWORD=antinex && ./run-migrations.sh
exit
exit
```

## Creating a User

Here's how to create the default user **trex**

[![asciicast](https://asciinema.org/a/182829.png)](https://asciinema.org/a/182829?autoplay=1)

### Create Default User trex

The command to run is:

```
./create-user.sh
```

### Create User Using Swagger

You can create users using swagger the API's swagger url (here's the default one during creation of this guide):

http://api-antinex.192.168.99.100.nip.io/swagger/

### Create User From User File

You can define a user file with these environment keys in a file before running. You can also just exported them in the current shell session (but having a resource file will be required in the future):

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

```
./create-user.sh <optional path to user file>
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

### Stop All

Deploy the containers:

```
./deploy.sh
```
