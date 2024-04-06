FROM alpine:3.18
RUN apk --no-cache add postgresql15-client
COPY restore.sh /.
RUN chmod +x /restore.sh
ENTRYPOINT exec ./restore.sh