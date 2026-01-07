#!/bin/bash

# Environment Variables Update Script
# Updates .env file with production URLs

set -e

DOMAIN="${1:-funding.wpma.io}"
ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

echo "🔧 Updating environment variables for domain: $DOMAIN"

# Update FRONTEND_URL
if grep -q "^FRONTEND_URL=" "$ENV_FILE"; then
    sed -i "s|^FRONTEND_URL=.*|FRONTEND_URL=https://$DOMAIN|g" "$ENV_FILE"
    echo "✅ Updated FRONTEND_URL"
else
    echo "FRONTEND_URL=https://$DOMAIN" >> "$ENV_FILE"
    echo "✅ Added FRONTEND_URL"
fi

# Update BACKEND_URL
if grep -q "^BACKEND_URL=" "$ENV_FILE"; then
    sed -i "s|^BACKEND_URL=.*|BACKEND_URL=https://$DOMAIN|g" "$ENV_FILE"
    echo "✅ Updated BACKEND_URL"
else
    echo "BACKEND_URL=https://$DOMAIN" >> "$ENV_FILE"
    echo "✅ Added BACKEND_URL"
fi

# Update ALLOWED_ORIGINS
if grep -q "^ALLOWED_ORIGINS=" "$ENV_FILE"; then
    sed -i "s|^ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=https://$DOMAIN,http://localhost:3008|g" "$ENV_FILE"
    echo "✅ Updated ALLOWED_ORIGINS"
else
    echo "ALLOWED_ORIGINS=https://$DOMAIN,http://localhost:3008" >> "$ENV_FILE"
    echo "✅ Added ALLOWED_ORIGINS"
fi

echo ""
echo "✅ Environment variables updated successfully!"
echo ""
echo "📋 Updated values:"
echo "   FRONTEND_URL=https://$DOMAIN"
echo "   BACKEND_URL=https://$DOMAIN"
echo "   ALLOWED_ORIGINS=https://$DOMAIN,http://localhost:3008"
