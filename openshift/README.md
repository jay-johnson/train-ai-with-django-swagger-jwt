## AntiNex on OpenShift

This will deploy the following containers to OpenShift:

1. API Server - Django REST Framework with JWT and Swagger
1. API Worker - Celery Worker Pool
1. Core Worker - AntiNex AI Core Celery Worker
1. Posgres 9.6
1. Redis 3.2

### Login to OpenShift

```
oc login https://192.168.99.102:8443
```

### Deploy

Deploy the containers:

```
./deploy.sh
```

### Check the Stack

You can view the **antinex** project's pod on the OpenShift web console:

https://192.168.99.102:8443/console/project/antinex/browse/pods

You can also use the command line:

```
oc status
In project antinex on server https://192.168.99.102:8443

http://api-antinex.192.168.99.102.nip.io to pod port 8080 (svc/api)
  deployment/api deploys jayjohnson/ai-core:latest
    deployment #1 running for 4 minutes - 1 pod

http://postgres-antinex.192.168.99.102.nip.io to pod port 5432 (svc/postgres)
  dc/postgres deploys openshift/postgresql:9.6
    deployment #1 deployed 4 minutes ago - 1 pod

http://redis-antinex.192.168.99.102.nip.io to pod port 6379 (svc/redis)
  dc/redis deploys istag/redis:latest
    deployment #1 deployed 4 minutes ago - 1 pod

deployment/worker deploys jayjohnson/ai-core:latest
  deployment #1 running for 4 minutes - 1 pod

deployment/pipeline deploys jayjohnson/ai-core:latest
  deployment #1 running for 4 minutes - 1 pod

deployment/core deploys jayjohnson/ai-core:latest
  deployment #1 running for 4 minutes - 1 pod
```

### Migrations

Migrations have to run inside an ```api``` container. Use this to show how to run a migration:

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

or:

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
