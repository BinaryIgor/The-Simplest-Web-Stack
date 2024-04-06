#!/bin/bash
set -euo pipefail

app=$JOB
app_dir="${JOB_DIR:-jobs/$JOB}"
export ENV="${ENV:-local}"

echo "Building $app with ${ENV} env profile..."

cwd=$PWD
cd "../../config"
. global.env
. ${ENV}.env
cd $cwd

cd ../..
cd $app_dir

rm -r -f dist
mkdir dist

echo "Running package cmd..."

. package_cmd.bash

tag="${TAG:-latest}"
tagged_image="${app}:${tag}"

echo "Building image..."

docker build . -t ${tagged_image}

gzipped_image_path="dist/$app.tar.gz"

echo "Image built, exporting it to $gzipped_image_path, this can take a while..."

docker save ${tagged_image} | gzip > ${gzipped_image_path}

echo "Image exported, preparing scripts..."

export app=$app
export tag=$tag
export create_cmd="
${PRE_DOCKER_CREATE_CMD:-}
docker create ${DOCKER_CREATE_PARAMS} --name $app $tagged_image
${POST_DOCKER_CREATE_CMD:-}"

cd $ROOT_REPO_DIR
envsubst '${app} ${tag}' < $LOAD_AND_CREATE_APP_TEMPLATE_PATH > $app_dir/dist/load_and_create_app.bash
envsubst '${app} ${create_cmd}' < $CREATE_APP_TEMPLATE_PATH > $app_dir/dist/create_app.bash

echo "Package prepared."