#!/bin/bash
set -euo pipefail

cwd=$PWD
cd ../../config
. "global.env"
cd $cwd

crontab_path="/home/$DEPLOY_USER/crontab.txt"

cd $ROOT_REPO_DIR

scp config/crontab.txt ${REMOTE_HOST}:${crontab_path}
ssh ${REMOTE_HOST} "echo 'current crontab:'
crontab -l
echo
echo \"Updating it from ${crontab_path}...\"
crontab ${crontab_path}
echo
echo 'Crontab updated, new state:'
crontab -l"