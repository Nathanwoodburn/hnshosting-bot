#!/bin/bash

# Variables
domain=$1
user=$2
# Verify owner
file_path="/etc/nginx/sites-available/$domain"
if grep -q "$user" "$file_path"; then
    git -C /var/www/$domain pull
    echo "Git pull complete!"
else 
    echo "ERROR: You do not own this domain"
fi

