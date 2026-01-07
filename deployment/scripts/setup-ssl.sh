#!/bin/bash

# SSL Setup Script for funding.wpma.io
# This script sets up Let's Encrypt SSL certificate

set -e

DOMAIN="funding.wpma.io"
EMAIL="admin@wpma.io"

echo "🔒 Setting up SSL certificate for $DOMAIN..."

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "❌ Certbot is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Request certificate
echo "📝 Requesting SSL certificate..."
sudo certbot certonly --nginx \
    -d "$DOMAIN" \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --preferred-challenges http

echo "✅ SSL certificate installed successfully!"
echo "📅 Certificate location: /etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "🔧 Next steps:"
echo "1. Copy nginx config: sudo cp deployment/nginx/funding.wpma.io.conf /etc/nginx/sites-available/"
echo "2. Enable site: sudo ln -sf /etc/nginx/sites-available/funding.wpma.io.conf /etc/nginx/sites-enabled/"
echo "3. Test nginx: sudo nginx -t"
echo "4. Reload nginx: sudo systemctl reload nginx"
