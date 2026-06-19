#!/bin/bash
# Production Deployment Checklist for TransactIQ

set -e

echo "════════════════════════════════════════════════════════════"
echo "TransactIQ Production Deployment Checklist"
echo "════════════════════════════════════════════════════════════"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for checks
passed=0
failed=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((passed++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((failed++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo ""
echo "1. Checking Backend Requirements..."
echo "──────────────────────────────────────────────────────────────"

if [ -f "backend/requirements.txt" ]; then
    check_pass "requirements.txt exists"
else
    check_fail "requirements.txt not found"
fi

if [ -f "backend/main.py" ]; then
    check_pass "main.py exists"
else
    check_fail "main.py not found"
fi

if [ -d "backend/app" ]; then
    check_pass "app package exists"
else
    check_fail "app package not found"
fi

echo ""
echo "2. Checking Frontend Requirements..."
echo "──────────────────────────────────────────────────────────────"

if [ -f "frontend/package.json" ]; then
    check_pass "package.json exists"
else
    check_fail "package.json not found"
fi

if [ -f "frontend/next.config.js" ]; then
    check_pass "next.config.js exists"
else
    check_fail "next.config.js not found"
fi

echo ""
echo "3. Checking Infrastructure Files..."
echo "──────────────────────────────────────────────────────────────"

if [ -f "infrastructure/Dockerfile.backend" ]; then
    check_pass "Backend Dockerfile exists"
else
    check_fail "Backend Dockerfile not found"
fi

if [ -f "infrastructure/Dockerfile.frontend" ]; then
    check_pass "Frontend Dockerfile exists"
else
    check_fail "Frontend Dockerfile not found"
fi

if [ -f "infrastructure/docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
else
    check_fail "docker-compose.yml not found"
fi

if [ -f "infrastructure/nginx.conf" ]; then
    check_pass "nginx.conf exists"
else
    check_fail "nginx.conf not found"
fi

echo ""
echo "4. Checking Documentation..."
echo "──────────────────────────────────────────────────────────────"

for doc in README.md SETUP.md ARCHITECTURE.md DEPLOYMENT.md; do
    if [ -f "$doc" ]; then
        check_pass "$doc exists"
    else
        check_fail "$doc not found"
    fi
done

echo ""
echo "5. Checking Configuration Files..."
echo "──────────────────────────────────────────────────────────────"

if [ -f ".gitignore" ]; then
    check_pass ".gitignore exists"
else
    check_fail ".gitignore not found"
fi

if [ -f "backend/.env.example" ]; then
    check_pass "backend/.env.example exists"
else
    check_fail "backend/.env.example not found"
fi

if [ -f "frontend/.env.example" ]; then
    check_pass "frontend/.env.example exists"
else
    check_fail "frontend/.env.example not found"
fi

echo ""
echo "6. Checking Demo Datasets..."
echo "──────────────────────────────────────────────────────────────"

dataset_count=$(find demo_datasets -name "*.csv" 2>/dev/null | wc -l)
if [ "$dataset_count" -gt 0 ]; then
    check_pass "Found $dataset_count demo datasets"
else
    check_fail "No demo datasets found"
fi

echo ""
echo "7. Checking CI/CD Pipeline..."
echo "──────────────────────────────────────────────────────────────"

if [ -f ".github/workflows/ci-cd.yml" ]; then
    check_pass "GitHub Actions workflow exists"
else
    check_fail "GitHub Actions workflow not found"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Summary"
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}✓ All checks passed! Project is ready for deployment.${NC}\n"
    exit 0
else
    echo -e "\n${RED}✗ Some checks failed. Please review the output above.${NC}\n"
    exit 1
fi
