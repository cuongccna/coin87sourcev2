#!/bin/bash
# Verification Script for LARAI.VN Deployment
# Run this to check if everything is configured correctly

echo "================================"
echo "🔍 LARAI.VN DEPLOYMENT CHECK"
echo "================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo ""
echo "=== System Checks ==="

# Check if running as root
if [ "$USER" = "root" ]; then
    check_pass "Running as root user"
else
    check_warn "Not running as root (current: $USER)"
fi

# Check directory
if [ -d "/var/www/coin87sourcev2" ]; then
    check_pass "Project directory exists: /var/www/coin87sourcev2"
else
    check_fail "Project directory NOT found: /var/www/coin87sourcev2"
fi

# Check Python
if command -v python3.11 &> /dev/null; then
    check_pass "Python 3.11 installed"
else
    check_fail "Python 3.11 NOT installed"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_pass "Node.js installed: $NODE_VERSION"
else
    check_fail "Node.js NOT installed"
fi

# Check PM2
if command -v pm2 &> /dev/null; then
    PM2_VERSION=$(pm2 --version)
    check_pass "PM2 installed: v$PM2_VERSION"
else
    check_fail "PM2 NOT installed"
fi

# Check Nginx
if systemctl is-active --quiet nginx; then
    check_pass "Nginx is running"
else
    check_fail "Nginx is NOT running"
fi

# Check PostgreSQL
if systemctl is-active --quiet postgresql; then
    check_pass "PostgreSQL is running"
else
    check_fail "PostgreSQL is NOT running"
fi

# Check Redis
if systemctl is-active --quiet redis-server 2>/dev/null || systemctl is-active --quiet redis 2>/dev/null; then
    check_pass "Redis is running"
else
    check_warn "Redis is NOT running (optional)"
fi

echo ""
echo "=== Database Checks ==="

# Check database connection
if PGPASSWORD='Cuongnv123456' psql -U coin87v2_user -d coin87v2_db -h localhost -c "SELECT 1" &> /dev/null; then
    check_pass "Database connection successful"
else
    check_fail "Database connection FAILED"
fi

echo ""
echo "=== Backend Checks ==="

# Check backend venv
if [ -d "/var/www/coin87sourcev2/backend/venv" ]; then
    check_pass "Backend virtual environment exists"
else
    check_fail "Backend virtual environment NOT found"
fi

# Check backend .env
if [ -f "/var/www/coin87sourcev2/backend/.env" ]; then
    check_pass "Backend .env file exists"
else
    check_fail "Backend .env file NOT found"
fi

# Check backend port
if lsof -i :9010 &> /dev/null; then
    check_pass "Backend running on port 9010"
else
    check_fail "Backend NOT running on port 9010"
fi

# Check backend health
if curl -sf http://127.0.0.1:9010/api/health &> /dev/null; then
    check_pass "Backend health check PASSED"
else
    check_fail "Backend health check FAILED"
fi

echo ""
echo "=== Frontend Checks ==="

# Check frontend node_modules
if [ -d "/var/www/coin87sourcev2/frontend/node_modules" ]; then
    check_pass "Frontend node_modules exists"
else
    check_fail "Frontend node_modules NOT found"
fi

# Check frontend .env.local
if [ -f "/var/www/coin87sourcev2/frontend/.env.local" ]; then
    check_pass "Frontend .env.local file exists"
else
    check_fail "Frontend .env.local file NOT found"
fi

# Check frontend build
if [ -d "/var/www/coin87sourcev2/frontend/.next" ]; then
    check_pass "Frontend build exists"
else
    check_fail "Frontend build NOT found"
fi

# Check frontend port
if lsof -i :9011 &> /dev/null; then
    check_pass "Frontend running on port 9011"
else
    check_fail "Frontend NOT running on port 9011"
fi

# Check frontend response
if curl -sf http://127.0.0.1:9011 &> /dev/null; then
    check_pass "Frontend responding"
else
    check_fail "Frontend NOT responding"
fi

echo ""
echo "=== PM2 Checks ==="

# Check PM2 processes
if pm2 list &> /dev/null; then
    PM2_ONLINE=$(pm2 jlist 2>/dev/null | jq -r '.[] | select(.pm2_env.status == "online") | .name' | wc -l)
    if [ "$PM2_ONLINE" -ge 2 ]; then
        check_pass "PM2 processes running: $PM2_ONLINE online"
    else
        check_fail "PM2 processes: only $PM2_ONLINE online (expected 6)"
    fi
else
    check_fail "PM2 NOT working"
fi

# Check PM2 startup
if pm2 list &> /dev/null && pm2 startup &> /dev/null; then
    check_pass "PM2 startup configured"
else
    check_warn "PM2 startup NOT configured"
fi

echo ""
echo "=== Nginx & SSL Checks ==="

# Check nginx config
if [ -f "/etc/nginx/sites-available/larai.vn" ]; then
    check_pass "Nginx config exists"
else
    check_fail "Nginx config NOT found"
fi

# Check nginx enabled
if [ -L "/etc/nginx/sites-enabled/larai.vn" ]; then
    check_pass "Nginx site enabled"
else
    check_fail "Nginx site NOT enabled"
fi

# Check SSL certificate
if [ -f "/etc/letsencrypt/live/larai.vn/fullchain.pem" ]; then
    check_pass "SSL certificate exists"
    
    # Check SSL expiry
    EXPIRY_DATE=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/larai.vn/fullchain.pem | cut -d= -f2)
    echo "   Expires: $EXPIRY_DATE"
else
    check_warn "SSL certificate NOT found (run certbot)"
fi

echo ""
echo "=== Cron Jobs Checks ==="

# Check crontab
CRON_COUNT=$(crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l)
if [ "$CRON_COUNT" -gt 0 ]; then
    check_pass "Crontab configured ($CRON_COUNT jobs)"
else
    check_warn "No crontab entries found"
fi

echo ""
echo "=== Log Checks ==="

# Check log directory
if [ -d "/var/log/coin87" ]; then
    check_pass "Log directory exists"
    
    # Check log files
    LOG_COUNT=$(ls -1 /var/log/coin87/*.log 2>/dev/null | wc -l)
    echo "   Log files: $LOG_COUNT"
else
    check_fail "Log directory NOT found"
fi

# Check backup directory
if [ -d "/var/www/backups" ]; then
    check_pass "Backup directory exists"
    
    BACKUP_COUNT=$(ls -1 /var/www/backups/*.sql.gz 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 0 ]; then
        echo "   Backups: $BACKUP_COUNT files"
    else
        check_warn "No backup files found"
    fi
else
    check_warn "Backup directory NOT found"
fi

echo ""
echo "=== Public Access Checks ==="

# Check HTTPS
if curl -sf https://larai.vn &> /dev/null; then
    check_pass "Website accessible: https://larai.vn"
else
    check_warn "Website NOT accessible via HTTPS (DNS or SSL issue)"
fi

# Check API
if curl -sf https://larai.vn/api/health &> /dev/null; then
    check_pass "API accessible: https://larai.vn/api/health"
else
    check_warn "API NOT accessible via HTTPS"
fi

echo ""
echo "================================"
echo "📊 SUMMARY"
echo "================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL CHECKS PASSED!${NC}"
    echo "Your deployment is ready!"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  SOME CHECKS FAILED${NC}"
    echo "Please fix the issues above"
    exit 1
fi
