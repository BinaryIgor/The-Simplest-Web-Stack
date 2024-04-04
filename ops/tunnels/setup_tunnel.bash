#!/bin/bash
set -euo pipefail

local_port=${LOCAL_PORT:-5432}
remote_port=${REMOTE_PORT:-$local_port}
#TODO: generate it/add to readme
host=${HOST:-$DEPLOY_HOST}
remote_host="0.0.0.0"
remote_user=${REMOTE_USER:-$DEPLOY_USER}
background_tunnel="${BACKGROUND_TUNNEL:-false}"

echo "Tunneling through: $remote_user@$host..."

ssh_cmd="-o StrictHostKeyChecking=accept-new -N -L $local_port:$remote_host:$remote_port $remote_user@$host"
if [ $background_tunnel = "true" ]; then
    pid_file="/tmp/setup_tunnel.pid"
    ssh $ssh_cmd &
    t_pid=$!
    echo "Waiting to establish a tunnel in the background..."
    echo $t_pid > $pid_file
    sleep 1
    echo "Tunnel pid: $t_pid"
else
    echo "Establishing a tunnel..."
    ssh $ssh_cmd
fi