#!/usr/bin/env sh
set -e

# Display an error message if the DOMAIN_NAME environment variable is not set
if [ -z "$DOMAIN_NAME" ]; then
  echo "DOMAIN_NAME environment variable is not set"
  exit 1
fi


LOCAL_CERT_DIR="/etc/letsencrypt/live/$DOMAIN_NAME"

# Fetch or renew the certificates (or do nothing if they are already up to date)
# These get synced back to S3 by the cert-deploy-hook.sh script
certbot certonly \
        --dns-route53 \
        --keep-until-expiring \
        --non-interactive \
        --agree-tos \
        -d $DOMAIN_NAME

# Sort out permissions on the files
chown -R opensearch:opensearch $LOCAL_CERT_DIR
chmod 644 $LOCAL_CERT_DIR/cert.pem
chmod 644 $LOCAL_CERT_DIR/chain.pem
chmod 644 $LOCAL_CERT_DIR/fullchain.pem
chmod 600 $LOCAL_CERT_DIR/privkey.pem