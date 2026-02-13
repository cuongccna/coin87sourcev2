"""Deployment Script for VPS (No Docker)
Run this on VPS after initial setup
"""

#!/bin/bash
set -e

APP_DIR="/opt/coin87"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

echo "================================"
echo "LARAI.VN DEPLOYMENT SCRIPT"
echo "================================"

# Step 1: Pull latest code (SKIPPED as per request)
# echo "[1/6] Pulling latest code from Git..."
# cd $APP_DIR
# git pull origin main

# Step 2: Backend - Install dependencies
echo "[2/6] Setting up Backend..."
cd $BACKEND_DIR
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: Run database migrations
echo "[3/6] Running database migrations..."
# Add your migration commands here
# alembic upgrade head

# Step 4: Frontend - Install and build
echo "[4/6] Setting up Frontend..."
cd $FRONTEND_DIR
npm install
npm run build

# Step 5: Restart systemd services
echo "[5/6] Restarting services..."
sudo systemctl restart coin87-backend
sudo systemctl restart coin87-frontend

# Step 6: Check service status
echo "[6/6] Checking service status..."
sudo systemctl status coin87-backend --no-pager
sudo systemctl status coin87-frontend --no-pager

echo "================================"
echo "✓ Deployment Complete!"
echo "================================"
echo "Backend: https://larai.vn/api/docs"
echo "Frontend: https://larai.vn"
echo "================================"
