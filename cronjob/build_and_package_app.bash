#!/bin/bash
set -euo pipefail

app="cronjob"
tag="${TAG:-latest}"
tagged_image="${app}:${tag}"

echo "Creating package in dist directory for $tagged_image image..."
echo "Preparing dist dir..."

rm -r -f dist
mkdir dist

echo "Building image..."

docker build . -t ${tagged_image}

gzipped_image_path="dist/$app.tar.gz"

echo "Image built, exporting it to $gzipped_image_path, this can take a while..."

docker save ${tagged_image} | gzip > ${gzipped_image_path}

echo "Image exported, preparing scripts..."

export app=$app
export tag=$tag
export create_cmd="docker create --network host --restart no --name $app $tagged_image"

cd ..
envsubst '${app} ${tag}' < $LOAD_AND_CREATE_APP_TEMPLATE_PATH > $app/dist/load_and_create_app.bash
envsubst '${app} ${create_cmd}' < $CREATE_APP_TEMPLATE_PATH > $app/dist/create_app.bash

echo "Package prepared."