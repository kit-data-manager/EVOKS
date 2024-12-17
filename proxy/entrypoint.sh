#!/bin/sh

# Substitute environment variables in the Nginx template
envsubst '\$EVOKS_URL' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Start Nginx
nginx -g 'daemon off;'
