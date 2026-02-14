#!/bin/bash
set -e

echo "=== LARAI.VN DEPLOYMENT ==="

APP_DIR="/var/www/coin87sourcev2"

# Check .env file exists
if [ ! -f "$APP_DIR/backend/.env.production.larai" ]; then
    echo "ERROR: File .env.production.larai not found!"
    exit 1
fi

# Load config from .env
source <(grep -E '^DATABASE_URL=' "$APP_DIR/backend/.env.production.larai")
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

# Install system dependencies
echo "[1/8] Installing system packages..."
apt update
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip postgresql postgresql-contrib nginx redis-server certbot python3-certbot-nginx curl jq

# Setup database
echo "[2/8] Setting up database..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Install Node.js
echo "[3/8] Installing Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi

# Install PM2
echo "[4/8] Installing PM2..."
npm install -g pm2

# Backend setup
echo "[5/8] Setting up backend..."
cd $APP_DIR/backend
cp .env.production.larai .env
rm -rf venv
python3.11 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install wheel setuptools
./venv/bin/pip install "sqlalchemy[asyncio]" asyncpg alembic greenlet
./venv/bin/pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-multipart
./venv/bin/pip install redis google-generativeai
./venv/bin/pip install beautifulsoup4 lxml feedparser requests aiohttp httpx
./venv/bin/pip install "python-jose[cryptography]" "passlib[bcrypt]" bcrypt python-dotenv pytz
./venv/bin/python init_db.py
./venv/bin/python create_trading_signals_tables.py 2>/dev/null || true
./venv/bin/python create_vote_table.py 2>/dev/null || true
# No need to deactivate as we used explicit paths

# Frontend setup
echo "[6/8] Setting up frontend..."
cd $APP_DIR/frontend
npm install
cp .env.production.larai .env.local
npm run build

# Start PM2
echo "[7/8] Starting services..."
cd $APP_DIR
pm2 delete all 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u root --hp /root

# Nginx setup
echo "[8/8] Setting up Nginx..."
cp deployment/nginx-larai.conf /etc/nginx/sites-available/larai.vn
ln -sf /etc/nginx/sites-available/larai.vn /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo ""
echo "=== DEPLOYMENT COMPLETED ==="
echo "Run: pm2 list"
echo "Logs: pm2 logs"
echo "SSL: certbot --nginx -d larai.vn -d www.larai.vn"
