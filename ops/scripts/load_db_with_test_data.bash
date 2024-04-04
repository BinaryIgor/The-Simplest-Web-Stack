#!/bin/bash
set -euo pipefail

cwd=$PWD
cd ../../config
. global.env
. "$ENV.env"

cd $cwd

python3 _load_db_with_test_data.py
