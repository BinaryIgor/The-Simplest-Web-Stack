#!/bin/bash
set -euo pipefail

cwd=$PWD
cd ../../config
source "${ENV}.env"
cd $cwd

app="set-https-nginx"
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
export run_cmd="docker run -d -v ${STATIC_PATH}:/usr/share/nginx/site --name $app $tagged_image"

cd ../..
envsubst '${app} ${tag}' < $LOAD_AND_RUN_APP_TEMPLATE_PATH > tools/$app/dist/load_and_run_app.bash
envsubst '${app} ${run_cmd}' < $RUN_APP_TEMPLATE_PATH > tools/$app/dist/run_app.bash

echo "Package prepared."