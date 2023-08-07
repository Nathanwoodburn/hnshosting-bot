#!/bin/bash

domain=$1
user=$2

# Set all to lowercase
domain=${domain,,}
user=${user,,}

file_path="/etc/nginx/sites-available/$domain"

# Check if domain already exists
if [ -f $file_path ]; then
    # Verify owner
    if grep -q "$user" "$file_path"; then
        rm $file_path
        rm /etc/nginx/sites-enabled/$domain
        systemctl restart nginx
        echo "Domain deleted!"
    else
        echo "ERROR: You do not own this domain"
        exit 0;
    fi
else
    echo "ERROR: Domain doesn't exists"
    exit 0;
fi

# Check if website files exist
if [ -d "/var/www/$domain" ]; then
    rm -rf /var/www/$domain
    echo "Website files deleted!"
fi