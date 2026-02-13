#!/bin/bash
# Quick Deploy Script for LARAI.VN (VPS)
# Run this on VPS: /home/coin87/coin87sourcev2/scripts/quick_deploy_larai.sh

set -e

echo "================================"
echo "🚀 LARAI.VN QUICK DEPLOY"
echo "================================"

# Variables
APP_DIR="/home/coin87/coin87sourcev2"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

# Step 1: Pull latest code
echo ""
echo "[1/5] 📥 Pulling latest code..."
cd $APP_DIR
git pull origin main

# Step 2: Update Backend
echo ""
echo "[2/5] 🔧 Updating Backend..."
cd $BACKEND_DIR
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate

# Step 3: Update Frontend
echo ""
echo "[3/5] 🎨 Building Frontend..."
cd $FRONTEND_DIR
npm install --silent
npm run build

# Step 4: Restart Services (PM2)
echo ""
echo "[4/5] 🔄 Restarting services..."
pm2 reload ecosystem.config.js
sleep 3

# Step 5: Check Status
echo ""
echo "[5/5] ✅ Checking status..."
echo ""

# Show PM2 list
pm2 list

echo ""
echo "=== Service Health Check ==="
if curl -sf http://127.0.0.1:9010/api/health > /dev/null; then
    echo "✅ Backend is RUNNING on port 9010"
else
    echo "❌ Backend health check FAILED"
fi

if curl -sf http://127.0.0.1:9011 > /dev/null; then
    echo "✅ Frontend is RUNNING on port 9011"
else
    echo "❌ Frontend check FAILED"
fi

if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx is RUNNING"
else
    echo "❌ Nginx is NOT RUNNING"
fi

echo ""
echo "================================"
echo "🎉 DEPLOY COMPLETED!"
echo "================================"
echo "Website: https://larai.vn"
echo "API Health: https://larai.vn/api/health"
echo ""
echo "View logs:"
echo "  Backend:  sudo journalctl -u coin87-backend -f"
echo "  Frontend: sudo journalctl -u coin87-frontend -f"
echo "==All:      pm2 logs"
echo "  Backend:  pm2 logs larai-backend"
echo "  Frontend: pm2 logs larai-frontend"
echo "  Crawler:  pm2 logs larai-crawler"
echo "  Monitor:  pm2 monit