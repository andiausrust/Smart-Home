#!/bin/bash

MOUNT="/outside"
IMAGE="cogitator:latest"

# for travel and demonstrations, if there is no running 'postgres' docker image (=we are not on deimos)
# redirect 'postgres' to local docker host, hopefully there is a local 'postgres' container running
ip=$( docker ps | grep '  postgres' )
if [ -z "$ip" ]; then
  RUNOPT="--add-host postgres:172.17.0.1"
else
  RUNOPT="--link postgres"
fi

ip=$( docker ps | grep '  server' )
if [ -z "$ip" ]; then
  RUNOPT+=" --add-host server:172.17.0.1"
else
  RUNOPT+=" --link server"
fi


docker run -e X_UID="$(id -u)" -e X_GID="$(id -g)" -e X_NAME="$(whoami)" \
   $RUNOPT \
   -v $PWD:$MOUNT \
   -w $MOUNT \
   --name cogitator_${USER}_$$ --rm -it \
   $IMAGE \
   "/usr/bin/python3 /outside-module/run_as_rmq_service.py $*"
