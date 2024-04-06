#!/bin/bash
set -eu

if [ $ENV = 'prod' ]; then
    export PRE_DOCKER_CREATE_CMD="
export DO_SPACES_KEY=\$(cat "${SECRETS_PATH}"/do-spaces-key.txt)
export DO_SPACES_SECRET=\$(cat "${SECRETS_PATH}"/do-spaces-secret.txt)"
    spaces_params="-e UPLOAD_TO_DO_SPACES=true -e REGION=fra1 -e DO_SPACES_KEY -e DO_SPACES_SECRET -e DO_SPACES_BUCKET=binaryigor -e DO_SPACES_BUCKET_FOLDER=db-backups"
else
    spaces_params=""
fi

export DOCKER_CREATE_PARAMS="-e "DB_NAME=$DB_NAME" -e "DB_USER=$DB_USER" $spaces_params --network host -v ${DB_BACKUPS_PATH}:/backups"