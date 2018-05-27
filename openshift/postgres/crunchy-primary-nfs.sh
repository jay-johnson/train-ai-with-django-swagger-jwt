# https://crunchydata.github.io/crunchy-containers/getting-started/kubernetes-and-openshift/#_single_primary
# sudo apt install golang-go
# go get github.com/blang/expenv
# mkdir -p -m 777 /opt/antinex
# git clone https://github.com/CrunchyData/crunchy-containers.git /opt/antinex/crunchy
# on ubuntu 18.04:
# export GOPATH=$HOME/go
# export PATH=$PATH:$GOROOT/bin:$GOPATH/bin

export CCP_IMAGE_PREFIX=crunchydata
export CCP_IMAGE_TAG=centos7-10.4-1.8.3
export CCP_CLI=oc
export CCP_NAMESPACE=antinex
export CCPROOT=/opt/antinex/crunchy
export CCP_SECURITY_CONTEXT='"supplementalGroups": [65534]'
export CCP_STORAGE_PATH=/exports/postgres-antinex
export CCP_NFS_IP=192.168.0.35
export CCP_STORAGE_MODE=ReadWriteMany
export CCP_STORAGE_CAPACITY=400M
