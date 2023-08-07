#!/bin/bash
domain=$1
# Check if args passed
if [ -z "$1" ]
then
#  Ask for domain name
  echo "Domain name:"
    read domain
fi

echo "TLSA record:"
echo -n "3 1 1 " && openssl x509 -in /etc/ssl/$domain.crt -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | xxd  -p -u -c 32