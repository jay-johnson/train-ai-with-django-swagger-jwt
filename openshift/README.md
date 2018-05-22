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

### Login to OpenShift

Here's an example of logging into a local Minishift instance:

[![asciicast](https://asciinema.org/a/p43SsSDRIuW53GtahbxHq7yD9.png)](https://asciinema.org/a/p43SsSDRIuW53GtahbxHq7yD9?autoplay=1)

```
oc login https://192.168.99.103:8443
```

### Deploy

Deploy the containers:

[![asciicast](https://asciinema.org/a/lBVLnxMvy4bHiOCvqtNYKmpxP.png)](https://asciinema.org/a/lBVLnxMvy4bHiOCvqtNYKmpxP?autoplay=1)

```
./deploy.sh
```

### Check the Stack

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

### Migrations

Migrations have to run inside an ``api`` container. Below is a recording of running the initial migration.

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

### Debugging

#### Tail API Logs

```
oc logs -f deployment/api
```

or

```
./logs-api.sh
```

#### Tail Worker Logs

```
oc logs -f deployment/worker
```

or

```
./logs-worker.sh
```

#### Tail AI Core Logs

```
oc logs -f deployment/core
```

or

```
./logs-core.sh
```

#### Tail Pipeline Logs

```
oc logs -f deployment/pipeline
```

or

```
./logs-pipeline.sh
```

#### Change the Entrypoint

To keep the containers running just add something like: ```tail -f <some file>``` to keep the container running for debugging issues.

I use:

```
&& tail -f /var/log/antinex/api/api.log
```

#### SSH into API Container

```
oc rsh deployment/api /bin/bash
```

#### SSH into API Worker Container

```
./ssh-worker.sh
```

or

```
oc rsh deployment/worker /bin/bash
```

#### SSH into AI Core Container

```
oc rsh deployment/core /bin/bash
```

### Stop All

Deploy the containers:

```
./deploy.sh
```
