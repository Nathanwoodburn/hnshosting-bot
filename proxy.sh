#!/bin/bash

domain=$1
url=$2
user=$3

# Set all to lowercase
domain=${domain,,}
url=${url,,}
user=${user,,}

# Check if domain already exists
if [ -f /etc/nginx/sites-available/$domain ]; then
    echo "ERROR: Domain already exists"
    exit 0;
fi


# Verify url is valid timeout 5 seconds

valid=$(timeout 5 curl -s -o /dev/null -w "%{http_code}" $url | grep 200)
if [ -n "$valid" ]; then
    echo "URL is valid: $url"
else
    echo "ERROR: URL is not valid or unreachable: $url"
    exit 0;
fi


printf "# $user
server {
  listen 80;
  listen [::]:80;
  server_name $domain;
  proxy_ssl_server_name on;
  location / {
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_pass $url;
    }

    listen 443 ssl;
    ssl_certificate /etc/ssl/$domain.crt;
    ssl_certificate_key /etc/ssl/$domain.key;
}" > /etc/nginx/sites-available/$domain
sudo ln -s /etc/nginx/sites-available/$domain /etc/nginx/sites-enabled/$domain

#generate ssl certificate
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
  -keyout cert.key -out cert.crt -extensions ext  -config \
  <(echo "[req]";
    echo distinguished_name=req;
    echo "[ext]";
    echo "keyUsage=critical,digitalSignature,keyEncipherment";
    echo "extendedKeyUsage=serverAuth";
    echo "basicConstraints=critical,CA:FALSE";
    echo "subjectAltName=DNS:$domain,DNS:*.$domain";
    ) -subj "/CN=*.$domain"

# Respond with TLSA

TLSA=$(echo -n "3 1 1 " && openssl x509 -in cert.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | xxd  -p -u -c 32)

echo "TLSA: $TLSA"

sudo mv cert.key /etc/ssl/$domain.key
sudo mv cert.crt /etc/ssl/$domain.crt

# Restart to apply config file
sudo systemctl restart nginx