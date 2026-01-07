#!/bin/bash

# Deployment Script for Funding.WPMA.io
# This script handles the complete deployment process

set -e

DOMAIN="funding.wpma.io"
PROJECT_DIR="/opt/projects/saas-project-8"

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║         🚀  DEPLOYMENT: FUNDING.WPMA.IO  🚀                          ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script requires sudo privileges. Please run with sudo."
    exit 1
fi

# Navigate to project directory
cd "$PROJECT_DIR" || {
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
}

echo "📂 Project directory: $PROJECT_DIR"
echo ""

# Step 1: Check prerequisites
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Checking prerequisites..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi
echo "✅ Docker installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
echo "✅ Docker Compose installed"

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please configure it before continuing."
        exit 1
    else
        echo "❌ .env.example not found. Cannot create .env file."
        exit 1
    fi
fi
echo "✅ .env file exists"

echo ""

# Step 2: Setup SSL (if not already done)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Setting up SSL certificate..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "📝 SSL certificate not found. Setting up..."
    bash deployment/scripts/setup-ssl.sh
else
    echo "✅ SSL certificate already exists"
fi

echo ""

# Step 3: Setup Nginx
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Setting up Nginx..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

bash deployment/scripts/setup-nginx.sh

echo ""

# Step 4: Update environment variables
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Updating environment variables..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update URLs in .env
sed -i "s|FRONTEND_URL=.*|FRONTEND_URL=https://$DOMAIN|g" .env
sed -i "s|BACKEND_URL=.*|BACKEND_URL=https://$DOMAIN|g" .env

# Update ALLOWED_ORIGINS
if grep -q "ALLOWED_ORIGINS=" .env; then
    sed -i "s|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=https://$DOMAIN,http://localhost:3008|g" .env
else
    echo "ALLOWED_ORIGINS=https://$DOMAIN,http://localhost:3008" >> .env
fi

echo "✅ Environment variables updated"
echo ""

# Step 5: Build and start Docker containers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Building and starting Docker containers..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "🛑 Stopping existing containers..."
docker-compose down

echo "🔨 Building containers..."
docker-compose build --no-cache

echo "🚀 Starting containers..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""

# Step 6: Verify deployment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: Verifying deployment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check container status
echo "📊 Container status:"
docker-compose ps

echo ""

# Test frontend
echo "🌐 Testing frontend..."
if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" | grep -q "200"; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️  Frontend might not be ready yet. Please check manually."
fi

# Test backend
echo "🔌 Testing backend API..."
if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/api/v1/grants/search" | grep -qE "(200|404|405)"; then
    echo "✅ Backend API is accessible"
else
    echo "⚠️  Backend API might not be ready yet. Please check manually."
fi

echo ""

# Final summary
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║         ✅  DEPLOYMENT COMPLETE!  ✅                                 ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Your application is now live at:"
echo "   → https://$DOMAIN"
echo ""
echo "📋 Useful commands:"
echo "   → View logs:        docker-compose logs -f"
echo "   → Stop services:    docker-compose down"
echo "   → Restart services: docker-compose restart"
echo "   → Update:           git pull && bash deployment/scripts/deploy.sh"
echo ""
echo "🎉 Happy deploying!"
