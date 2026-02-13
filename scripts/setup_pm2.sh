#!/bin/bash
# PM2 Setup Script for LARAI.VN
# Run this ONCE on VPS after initial deployment

set -e

echo "================================"
echo "🚀 PM2 SETUP FOR LARAI.VN"
echo "================================"

# Check if running as root
if [ "$USER" != "root" ]; then
    echo "❌ This script must be run as 'root' user"
    echo "   Run: sudo su"
    exit 1
fi

# Step 1: Install PM2 globally
echo ""
echo "[1/6] 📦 Installing PM2..."
if ! command -v pm2 &> /dev/null; then
    npm install -g pm2
    echo "✅ PM2 installed successfully"
else
    echo "✅ PM2 already installed"
    pm2 --version
fi

# Step 2: Create log directory
echo ""
echo "[2/6] 📁 Creating log directories..."
mkdir -p /var/log/coin87
echo "✅ Log directory created"

# Step 3: Stop any existing PM2 processes
echo ""
echo "[3/6] 🛑 Stopping existing PM2 processes..."
pm2 delete all 2>/dev/null || echo "No existing processes"

# Step 4: Start all services with PM2
echo ""
echo "[4/6] 🚀 Starting services with PM2..."
cd /var/www/coin87sourcev2
pm2 start ecosystem.config.js

# Step 5: Setup PM2 startup (auto-start on boot)
echo ""
echo "[5/6] ⚙️  Setting up PM2 startup..."
pm2 save
pm2 startup systemd -u root --hp /root
echo ""
echo "⚠️  IMPORTANT: PM2 startup configured for root user"
echo ""

# Verify startup is configured
pm2 save

# Step 6: Verify services
echo ""
echo "[6/6] ✅ Verifying services..."
sleep 3
pm2 list

echo ""
echo "================================"
echo "🎉 PM2 SETUP COMPLETED!"
echo "================================"
echo ""
echo "📊 Useful PM2 Commands:"
echo "  pm2 list              - List all processes"
echo "  pm2 monit             - Monitor processes (CPU, Memory)"
echo "  pm2 logs              - View all logs"
echo "  pm2 logs larai-backend      - View backend logs"
echo "  pm2 logs larai-frontend     - View frontend logs"
echo "  pm2 logs larai-crawler      - View crawler logs"
echo "  pm2 restart all       - Restart all processes"
echo "  pm2 restart larai-backend   - Restart backend only"
echo "  pm2 stop all          - Stop all processes"
echo "  pm2 delete all        - Delete all processes"
echo "  pm2 save              - Save current process list"
echo ""
echo "🔄 Auto-restart on boot: ENABLED"
echo "📝 Logs location: /var/log/coin87/"
echo ""
echo "================================"
