#!/bin/bash

target=ocp39.homelab.com

oc delete pv primary-pgdata
oc delete pvc primary-pgdata
oc delete pv redis-antinex-pv
oc delete pvc redis-antinex-pvc

ssh root@${target} "rm -rf /exports/postgres-antinex; rm -rf /exports/redis-antinex; exportfs -rf; mkdir /exports/postgres-antinex; mkdir /pgdata; mkdir /exports/redis-antinex; chown nfsnobody:nfsnobody /exports -R;chown nfsnobody:nfsnobody /pgdata -R; chmod 777 /exports -R; chmod 777 /pgdata -R; exportfs -rf;echo '';showmount -e;echo '';cat /etc/hosts"
