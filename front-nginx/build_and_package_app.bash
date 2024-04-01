#!/bin/bash
set -euo pipefail

export app="front-nginx"
export tag="${TAG:-latest}"
tagged_image="${app}:${tag}"

echo "Creating package in dist directory for $tagged_image image..."
echo "Preparing dist dir..."

rm -r -f dist
mkdir dist
mkdir dist/conf

source "config_${ENV}.env"

export HTTP_PORT=${HTTP_PORT:-80}
export HTTPS_PORT=${HTTPS_PORT:-443}
export APP_URL="${APP_URL:-http://0.0.0.0:9999}"

echo "DOMAIN: $DOMAIN"

envsubst '${HTTP_PORT} ${HTTPS_PORT} ${DOMAIN} ${APP_URL}' < template_nginx.conf > dist/conf/default.conf
envsubst '${HTTP_PORT} ${HTTPS_PORT} ${DOMAIN}' < template_nginx.conf > dist/template_nginx_app.conf

export nginx_container="front-nginx"
# check if both proxying and proxied app are working properly
export app_health_check_url="http://0.0.0.0:${HTTP_PORT}/actuator/health"

envsubst '${nginx_container} ${app_health_check_url}' < template_update_app_url.bash > dist/update_app_url.bash

cp update_app_url_pre_start.bash dist/update_app_url_pre_start.bash

envsubst '${app_health_check_url}' < template_check_proxied_app.bash > dist/check_proxied_app.bash

envsubst '${nginx_container}' < template_reload_nginx_config.sh > dist/reload_nginx_config.sh

echo "Scripts prepared, building docker image..."

docker build . -t ${tagged_image}

gzipped_image_path="dist/$app.tar.gz"

echo "Image built, exporting it to $gzipped_image_path, this can take a while..."

docker save ${tagged_image} | gzip > ${gzipped_image_path}

if [ $ENV = 'local' ]; then
    CERTS_VOLUME="-v ${SSL_CERTIFICATE_VOLUME} -v ${SSL_CERTIFICATE_KEY_VOLUME}"
else
    CERTS_VOLUME="-v ${CERTS_VOLUME}"
fi

pre_run="bash update_app_url_pre_start.bash $APP_URL_FILE_PATH"
if [ $ENV = 'prod' ]; then
    pre_run_action="chmod -x reload_nginx_config.sh
sudo cp reload_nginx_config.sh /etc/letsencrypt/renewal-hooks/post/reload_nginx_config.sh"
else
    pre_run_action=""
fi

export run_cmd="$pre_run_action
bash update_app_url_pre_start.bash $APP_URL_FILE_PATH

docker run -d --network host \\
    -v ${CONFIG_VOLUME} \\
    ${CERTS_VOLUME} \\
    -v ${STATIC_RESOURCES_VOLUME} \\
    --restart ${DOCKER_RESTART} --name $app $tagged_image
    
bash check_proxied_app.bash"

cd ..
envsubst '${app} ${tag}' < scripts/template_load_and_run_app.bash > $app/dist/load_and_run_app.bash
envsubst '${app} ${run_cmd}' < scripts/template_run_app.bash > $app/dist/run_app.bash

echo "Package prepared."