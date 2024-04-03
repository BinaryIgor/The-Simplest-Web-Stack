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
bash build_and_package_app.bash