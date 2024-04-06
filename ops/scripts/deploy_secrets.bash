#!/bin/bash
set -eu

cwd=$PWD
cd ../../config
. global.env
. "$ENV.env"

cd $cwd

python3 _deploy_secrets.py
