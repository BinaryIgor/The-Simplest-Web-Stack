FROM python:3.11-alpine3.18
RUN apk --no-cache add postgresql15-client
COPY backup.sh remove_old_backups.py requirements.txt /.
RUN chmod +x /backup.sh
RUN pip3 install -r /requirements.txt
ENTRYPOINT exec ./backup.sh