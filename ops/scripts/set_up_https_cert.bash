#!/bin/bash

# Webroot mode: certbot will create challenge file in the specified webroot to verify domain.
# Make sure that given webroot-path is exposed via your http server!
#
# https://eff-certbot.readthedocs.io/en/stable/using.html#webroot
# The webroot plugin works by creating a temporary file for each of your requested domains in: 
# ${webroot-path}/.well-known/acme-challenge.
# Then the Let’s Encrypt validation server makes HTTP requests to validate that the DNS for each requested domain
# resolves to the server running certbot. An example request made to your web server would look like:
# 66.133.109.36 - - [05/Jan/2016:20:11:24 -0500] "GET /.well-known/acme-challenge/HGr8U1IeTW4kY_Z6UIyaakzOkyQgPr_7ArlLgtZE8SX HTTP/1.1" 200 87 "-" "Mozilla/5.0 (compatible; Let's Encrypt validation server; +https://www.letsencrypt.org)"

# You can check renewal by running: sudo certbot renew --dry-run.
# For some reasons, it hangs in below script.

set -euo pipefail

cwd=$PWD
cd ../../config
. global.env
. "$ENV.env"

cd $cwd

skip_https_server_setup="${SKIP_HTTPS_SERVER_SETUP:-false}"
set_https_server_app="set-https-nginx"

if [ $skip_https_server_setup = "false" ]; then
    export APP="$set_https_server_app"
    export APP_DIR="tools/$APP"
    echo "Building and deploying $set_https_server_app server..."
    bash build_and_package_app.bash
    echo
    echo "https server build, deploying it..."
    echo
    bash deploy_app.bash
else
    echo "Skipping $set_https_server_app server setup and assuming that it is prepared and available!"
fi

echo
echo "Setting up certbot and http cert on ${DEPLOY_HOST} and ${DOMAIN} domain..."
echo

webroot_path=$STATIC_PATH

ssh $REMOTE_HOST "
echo "Setting up certbot..."
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
echo
echo "Certbot configured, generating certs..."
sudo certbot certonly --webroot --webroot-path "${webroot_path}" --domains "${DOMAIN}" \
    --non-interactive --email ${DOMAINS_EMAIL} --agree-tos -v"

echo
echo "Certbot set, stopping ${set_https_server_app}..."

ssh $REMOTE_HOST "docker stop $set_https_server_app --time 30"

echo "$set_https_server_app stopped, http cert with autorenewal prepared!"