#!/bin/bash
set -euo pipefail

cwd=$PWD
cd ../../config
source "global.env"
cd $cwd

app=$APP
app_dir="${APP_DIR:-$APP}"
deploy_user=$DEPLOY_USER
remote_host=$REMOTE_HOST
deploy_dir="$DEPLOY_DIR/$app"
previous_deploy_dir="$deploy_dir/previous"
latest_deploy_dir="$deploy_dir/latest"

echo "Deploying $app to a $remote_host host, preparing deploy directories.."

ssh ${remote_host} "rm -r -f $previous_deploy_dir;
mkdir -p $latest_deploy_dir;
cp -r $latest_deploy_dir $previous_deploy_dir;"

echo
echo "Dirs prepared, copying package, this can take a while..."

cd ../..
scp -r $app_dir/dist/* ${remote_host}:${latest_deploy_dir}

echo
echo "Package copied, loading and running app, this can take a while.."

ssh ${remote_host} "cd $latest_deploy_dir; bash load_and_run_app.bash"

echo
echo "App loaded, checking its logs and status after 5s.."
sleep 5
echo

ssh ${remote_host} "docker logs $app"
echo
echo "App status:"
ssh ${remote_host} "docker container inspect -f '{{ .State.Status }}' $app"

echo "App deployed!"
echo "In case of problems you can rollback to previous deployment: $previous_deploy_dir"