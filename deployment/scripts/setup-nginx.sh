#!/bin/bash

# Nginx Setup Script
# This script configures Nginx reverse proxy for funding.wpma.io

set -e

DOMAIN="funding.wpma.io"
CONFIG_FILE="deployment/nginx/funding.wpma.io.conf"
NGINX_AVAILABLE="/etc/nginx/sites-available/$DOMAIN.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/$DOMAIN.conf"

echo "⚙️  Setting up Nginx for $DOMAIN..."

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Copy configuration
echo "📋 Copying Nginx configuration..."
sudo cp "$CONFIG_FILE" "$NGINX_AVAILABLE"

# Enable site
echo "🔗 Enabling site..."
sudo ln -sf "$NGINX_AVAILABLE" "$NGINX_ENABLED"

# Test configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Reload nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo "✅ Nginx configured successfully!"
echo ""
echo "🌐 Your site should now be accessible at:"
echo "   - HTTP:  http://$DOMAIN (redirects to HTTPS)"
echo "   - HTTPS: https://$DOMAIN"
