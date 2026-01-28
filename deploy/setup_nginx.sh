#!/bin/bash

# Copy nginx config
sudo cp deploy/fastapi_nginx.conf /etc/nginx/conf.d/fastapi.conf

# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

echo "Nginx reverse proxy setup complete!"
