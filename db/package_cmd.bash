#!/bin/bash
set -eu

if [ $ENV = 'prod' ]; then
    docker_restart="unless-stopped"
    volume="-v /mnt/db_volume/data:/var/lib/postgresql/data"
else
    docker_restart="no"
    volume="-v /tmp/${APP_NAME}_volume:/var/lib/postgresql/data"
fi

export DOCKER_RUN_PARAMS="--network host ${volume} --restart ${docker_restart}"