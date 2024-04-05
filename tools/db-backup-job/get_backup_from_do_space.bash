#!/bin/bash
set -eu

# To use it, go to DigitalOcean Spaces UI.
# Find desired backup and click "Quick Share".
# It allows to generate tmp urls to download files from private spaces ;)

# Sourcing global variables
. ../../config/global.env
. ../../config/prod.env

curl -o "${DB_BACKUPS_PATH}/backup_restore.back" ${DO_SPACE_BACKUP_URL}