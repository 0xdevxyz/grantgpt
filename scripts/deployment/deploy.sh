#!/bin/bash
# FörderScout AI - Production Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/foerderscout"
COMPOSE_FILE="docker-compose.prod.yml"
DOMAIN="foerderscout.de"

echo -e "${GREEN}=================================================="
echo "FörderScout AI - Production Deployment"
echo -e "==================================================${NC}"

# =============================================================================
# Pre-deployment checks
# =============================================================================
echo -e "\n${YELLOW}📋 Pre-deployment checks...${NC}"

# Check if .env exists
if [ ! -f "${PROJECT_DIR}/.env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file with required environment variables."
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed!${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not installed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Pre-deployment checks passed${NC}"

# =============================================================================
# Pull latest code
# =============================================================================
echo -e "\n${YELLOW}📥 Pulling latest code...${NC}"
cd "${PROJECT_DIR}"
git fetch origin
git pull origin main

# =============================================================================
# Build images
# =============================================================================
echo -e "\n${YELLOW}🔨 Building Docker images...${NC}"
docker compose -f "${COMPOSE_FILE}" build --no-cache

# =============================================================================
# Run database migrations
# =============================================================================
echo -e "\n${YELLOW}🗃️ Running database migrations...${NC}"
docker compose -f "${COMPOSE_FILE}" run --rm api alembic upgrade head

# =============================================================================
# Stop old containers
# =============================================================================
echo -e "\n${YELLOW}🛑 Stopping old containers...${NC}"
docker compose -f "${COMPOSE_FILE}" down

# =============================================================================
# Start new containers
# =============================================================================
echo -e "\n${YELLOW}🚀 Starting new containers...${NC}"
docker compose -f "${COMPOSE_FILE}" up -d

# =============================================================================
# Wait for services to be healthy
# =============================================================================
echo -e "\n${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check API health
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "http://localhost:8008/health" | grep -q "healthy"; then
        echo -e "${GREEN}✅ API is healthy${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for API... (${RETRY_COUNT}/${MAX_RETRIES})"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ API failed to become healthy${NC}"
    docker compose -f "${COMPOSE_FILE}" logs api
    exit 1
fi

# =============================================================================
# SSL Certificate (Let's Encrypt)
# =============================================================================
echo -e "\n${YELLOW}🔐 Checking SSL certificates...${NC}"

if [ ! -d "/etc/letsencrypt/live/${DOMAIN}" ]; then
    echo "Obtaining SSL certificate for ${DOMAIN}..."
    docker compose -f "${COMPOSE_FILE}" run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        -d "${DOMAIN}" \
        -d "www.${DOMAIN}" \
        -d "api.${DOMAIN}" \
        --email "admin@${DOMAIN}" \
        --agree-tos \
        --non-interactive
    
    # Reload nginx
    docker compose -f "${COMPOSE_FILE}" exec nginx nginx -s reload
fi

echo -e "${GREEN}✅ SSL certificates OK${NC}"

# =============================================================================
# Cleanup
# =============================================================================
echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
docker system prune -f

# =============================================================================
# Summary
# =============================================================================
echo -e "\n${GREEN}=================================================="
echo "🎉 Deployment Complete!"
echo "==================================================${NC}"
echo ""
echo "Services:"
docker compose -f "${COMPOSE_FILE}" ps
echo ""
echo "URLs:"
echo "  - Frontend: https://${DOMAIN}"
echo "  - API:      https://api.${DOMAIN}"
echo "  - API Docs: https://api.${DOMAIN}/docs"
echo ""
echo "Logs:"
echo "  docker compose -f ${COMPOSE_FILE} logs -f [service]"
