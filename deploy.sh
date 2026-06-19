#!/bin/bash

# TransactIQ Quick Deployment Script
# Usage: ./deploy.sh [environment] [domain]
# Example: ./deploy.sh production api.transactiq.com

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get parameters
ENVIRONMENT=${1:-production}
DOMAIN=${2:-localhost}
API_DOMAIN="api.${DOMAIN}"

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}TransactIQ Deployment Script${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Environment: $ENVIRONMENT"
echo "Domain: $DOMAIN"
echo "API Domain: $API_DOMAIN"
echo ""

# Step 1: Validate project
echo -e "${YELLOW}[1/7]${NC} Validating project structure..."
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo -e "${RED}Error: Project structure invalid${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Project structure valid"
echo ""

# Step 2: Create environment files
echo -e "${YELLOW}[2/7]${NC} Creating environment configuration..."

# Generate secure secret key
SECRET_KEY=$(openssl rand -base64 32)

# Create backend .env
cat > backend/.env << EOF
DATABASE_URL=postgresql://transactiq:transactiq@postgres:5432/transactiq
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=$ENVIRONMENT
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=$SECRET_KEY
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,https://$API_DOMAIN
LOG_SQL=false
CHUNK_SIZE=10000
EOF

# Create frontend .env.production
cat > frontend/.env.production << EOF
NEXT_PUBLIC_API_URL=https://$API_DOMAIN/api/v1
NEXT_PUBLIC_ENVIRONMENT=$ENVIRONMENT
NEXT_PUBLIC_APP_NAME=TransactIQ
EOF

echo -e "${GREEN}✓${NC} Environment files created"
echo ""

# Step 3: Build Docker images
echo -e "${YELLOW}[3/7]${NC} Building Docker images..."
docker-compose -f infrastructure/docker-compose.yml build --no-cache > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Docker images built"
echo ""

# Step 4: Start services
echo -e "${YELLOW}[4/7]${NC} Starting services..."
docker-compose -f infrastructure/docker-compose.yml up -d > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Services started"
echo ""

# Step 5: Wait for services to be healthy
echo -e "${YELLOW}[5/7]${NC} Waiting for services to be healthy..."
sleep 10

# Check if backend is responding
max_retries=30
retry=0
while [ $retry -lt $max_retries ]; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is responding"
        break
    fi
    retry=$((retry + 1))
    if [ $retry -eq $max_retries ]; then
        echo -e "${RED}✗${NC} Backend failed to start"
        docker-compose logs backend
        exit 1
    fi
    sleep 1
done
echo ""

# Step 6: Initialize database
echo -e "${YELLOW}[6/7]${NC} Initializing database..."
docker-compose exec -T backend python -c "from app.database import init_db; init_db()" > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Database initialized"
echo ""

# Step 7: Verify deployment
echo -e "${YELLOW}[7/7]${NC} Verifying deployment..."

# Check backend API
if curl -s http://localhost:8000/ | grep -q "TransactIQ"; then
    echo -e "${GREEN}✓${NC} Backend API is operational"
else
    echo -e "${RED}✗${NC} Backend API verification failed"
    exit 1
fi

# Check frontend
if curl -s http://localhost:3000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend is operational"
else
    echo -e "${RED}✗${NC} Frontend verification failed"
    exit 1
fi

# Check database
if docker-compose exec -T postgres psql -U transactiq -d transactiq -c "SELECT COUNT(*) FROM datasets;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Database is operational"
else
    echo -e "${RED}✗${NC} Database verification failed"
    exit 1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Access your application:"
echo -e "  Frontend: ${BLUE}http://localhost:3000${NC}"
echo -e "  API: ${BLUE}http://localhost:8000${NC}"
echo -e "  API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "Configuration:"
echo "  Environment: $ENVIRONMENT"
echo "  Domain: $DOMAIN"
echo "  Database: postgresql://transactiq:***@postgres:5432/transactiq"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo ""
echo "For production deployment, see SERVER_DEPLOYMENT.md"
echo ""
