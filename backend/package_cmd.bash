#!/bin/bash
set -e

. "config_${ENV}.env"

skip_tests=${SKIP_TESTS:-false}

if [ $skip_tests == "true" ]; then
  mvn clean install -Dmaven.test.skip=true -Pexecutable
else
  mvn clean install -Pexecutable
fi

HTTP_PORT=$(shuf -i 10000-20000 -n 1)

app_url="http://0.0.0.0:$HTTP_PORT"
echo $app_url > "dist/current_url.txt"
echo $HTTP_PORT > "dist/current_port.txt"

export DOCKER_RUN_PARAMS="--network host -e SERVER_PORT=$HTTP_PORT --restart ${DOCKER_RESTART}"

export ZERO_DOWNTIME_DEPLOY=true
export APP_HEALTH_CHECK_URL="$app_url/actuator/health"
export UPSTREAM_NGINX_DIR=$UPSTREAM_NGINX_DIR
export APP_URL=$app_url