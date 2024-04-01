#!/bin/bash
stop_timeout=${stop_timeout:-30}
found_container=$(docker ps -q -f name="${app}")

if [ "$found_container" ]; then
  echo "Stopping previous ${app} version..."
  docker stop ${app} --time ${stop_timeout}
fi

echo "Removing previous container...."
docker rm ${app}

echo
echo "Creating new ${app} version..."
echo

${create_cmd}