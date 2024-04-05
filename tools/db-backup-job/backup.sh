#!/bin/sh
set -eu

db_user=$DB_USER
db_name=$DB_NAME
backup_date=$(date '+%Y%m%d_%H%M%S')
backup_name="backup_${backup_date}.back"
backup_path="/backups/$backup_name"

echo "$(date): backing up ${db_name} db of ${db_user} user to ${backup_path} file..."

# Compressed, custom dump format. For details, check out the docs: https://www.postgresql.org/docs/current/app-pgdump.html
pg_dump -Fc -h "0.0.0.0" -U $db_user -d $db_name > "$backup_path"

echo "$(date): backup done! Checking if we need to remove old backups..."

export MAX_BACKUPS=10
export BACKUPS_PATH="/backups"

python3 remove_old_backups.py

if [ "${UPLOAD_TO_DO_SPACES:-false}" = "true" ]; then
  echo "Uploading backup to DO spaces..."
  export BACKUP_LOCAL_PATH=$backup_path
  export BACKUP_NAME=$backup_name
  python3 upload_backups_to_do_spaces.py
else
  echo "Skipping backup to DO spaces upload"
fi