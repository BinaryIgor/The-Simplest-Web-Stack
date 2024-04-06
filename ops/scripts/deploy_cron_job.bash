#!/bin/bash
set -euo pipefail

cwd=$PWD
cd ../../config
. "global.env"
cd $cwd

app=$JOB
app_dir="${JOB_DIR:-jobs/$JOB}"
deploy_user=$DEPLOY_USER
remote_host=$REMOTE_HOST
deploy_dir="/home/$deploy_user/deploy/$app"
previous_deploy_dir="$deploy_dir/previous"
latest_deploy_dir="$deploy_dir/latest"

echo "Deploying $app to a $remote_host host, preparing deploy directories.."

ssh ${remote_host} "rm -r -f $previous_deploy_dir;
mkdir -p $latest_deploy_dir;
cp -r $latest_deploy_dir $previous_deploy_dir;"

echo
echo "Dirs prepared, copying package, this can take a while..."


cwd=$PWD
cd ../..
scp -r $app_dir/dist/* ${remote_host}:${latest_deploy_dir}
cd $cwd

echo
echo "Package copied, loading and creating app, this can take a while.."

ssh ${remote_host} "cd $latest_deploy_dir; bash load_and_create_app.bash"

echo
echo "App loaded and created, updating crontab.."

bash deploy_crontab.bash

echo "App created and new crontab state updated"