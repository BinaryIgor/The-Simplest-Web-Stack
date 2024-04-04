FROM alpine:3.18
RUN apk --no-cache add postgresql15-client
COPY restore_locally.sh /.
RUN chmod +x /restore_locally.sh
ENTRYPOINT exec ./restore_locally.sh