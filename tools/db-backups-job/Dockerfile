FROM alpine:3.18
RUN apk --no-cache add postgresql15-client python3
COPY backup_locally.sh remove_old_backups.py /.
RUN chmod +x /backup_locally.sh
ENTRYPOINT exec ./backup_locally.sh