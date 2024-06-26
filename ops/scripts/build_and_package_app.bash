#!/bin/bash
set -euo pipefail

app=$APP
app_dir="${APP_DIR:-$APP}"
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

zero_downtime_deploy=${ZERO_DOWNTIME_DEPLOY:-false}

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
export run_cmd="${PRE_DOCKER_RUN_CMD:-}
docker run -d ${DOCKER_RUN_PARAMS} --name $app $tagged_image
${POST_DOCKER_RUN_CMD:-}"

cd $ROOT_REPO_DIR
envsubst '${app} ${tag}' < $LOAD_AND_RUN_APP_TEMPLATE_PATH > $app/dist/load_and_run_app.bash

if [ $zero_downtime_deploy == "true" ]; then
  export upstream_nginx_dir=$UPSTREAM_NGINX_DIR
  export app_url=$APP_URL
  export app_health_check_url=$APP_HEALTH_CHECK_URL
  envsubst '${app} ${run_cmd} ${app_health_check_url} ${upstream_nginx_dir} ${app_url}' < $RUN_ZERO_DOWNTIME_APP_TEMPLATE_PATH > $app/dist/run_app.bash
else 
  envsubst '${app} ${run_cmd}' < $RUN_APP_TEMPLATE_PATH > $app/dist/run_app.bash
fi

echo "Package prepared."