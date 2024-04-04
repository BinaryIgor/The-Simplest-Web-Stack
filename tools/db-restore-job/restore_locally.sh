#!/bin/sh
set -eu

db_user=$DB_USER
db_name=$DB_NAME
backup_path="/backups/backup_restore.back"

echo "$(date): restoring ${db_name} db of ${db_user} user from ${backup_path} file..."
echo

# Compressed, custom dump format. For details, check out the docs: https://www.postgresql.org/docs/current/app-pgdump.html
pg_restore -Fc -h "0.0.0.0" -U $db_user -d $db_name -v "$backup_path"

echo
echo "$(date): db restored!"