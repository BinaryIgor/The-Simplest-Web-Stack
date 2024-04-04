#!/bin/bash
cwd=$PWD
cd ../../config
. global.env
. prod.env
cd $cwd

export LOCAL_PORT=5432
export REMOTE_PORT=5432

echo "Tunneling postgres on a port: $LOCAL_PORT!"

exec bash setup_tunnel.bash