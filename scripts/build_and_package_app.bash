#!/bin/bash
set -euo pipefail

app=$APP
export ENV="${ENV:-local}"

echo "Building $app with ${ENV} env profile..."

cd ..
cd $app
bash build_and_package_app.bash