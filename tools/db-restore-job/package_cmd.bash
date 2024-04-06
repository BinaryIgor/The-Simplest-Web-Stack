#!/bin/bash
export DOCKER_CREATE_PARAMS="-e "DB_NAME=$DB_NAME" -e "DB_USER=$DB_USER" --network host -v ${DB_BACKUPS_PATH}:/backups"
