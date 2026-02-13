"""VPS Server Setup & Hardening Script for Coin87
WARNING: Run this on a FRESH Ubuntu 22.04/24.04 VPS only!
"""

#!/bin/bash
set -e  # Exit on error

echo "================================"
echo "COIN87 VPS SETUP SCRIPT"
echo "================================"

# Configuration
ADMIN_USER="coin87admin"
APP_DIR="/opt/coin87"
PYTHON_VERSION="3.11"

# Step 1: System Updates
echo "[1/8] Updating system packages..."
apt update && apt upgrade -y

# Step 2: Create admin user (non-root)
echo "[2/8] Creating admin user: $ADMIN_USER"
if id "$ADMIN_USER" &>/dev/null; then
    echo "User $ADMIN_USER already exists"
else
    adduser --disabled-password --gecos "" $ADMIN_USER
    usermod -aG sudo $ADMIN_USER
    echo "$ADMIN_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$ADMIN_USER
fi

# Step 3: Install Python 3.11
echo "[3/8] Installing Python $PYTHON_VERSION..."
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev
apt install -y python3-pip

# Step 4: Install Node.js 20 (for Next.js)
echo "[4/8] Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g pm2  # Process manager for Node.js

# Step 5: Install PostgreSQL & Redis
echo "[5/8] Installing PostgreSQL 16 & Redis..."
apt install -y postgresql postgresql-contrib redis-server
systemctl enable postgresql
systemctl enable redis-server
systemctl start postgresql
systemctl start redis-server

# Step 6: Firewall Setup (UFW)
echo "[6/8] Configuring firewall..."
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# Step 7: SSH Hardening
echo "[7/8] Hardening SSH..."
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# Step 8: Install Fail2Ban
echo "[8/8] Installing Fail2Ban..."
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Step 9: Create Swap (4GB)
echo "[9/9] Creating 4GB swap file..."
if [ -f /swapfile ]; then
    echo "Swap file already exists"
else
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Create app directory
mkdir -p $APP_DIR
chown -R $ADMIN_USER:$ADMIN_USER $APP_DIR

echo "================================"
echo "✓ VPS Setup Complete!"
echo "================================"
echo "Next steps:"
echo "1. Create SSH key: ssh-keygen -t ed25519"
echo "2. Add public key to ~/.ssh/authorized_keys"
echo "3. Clone repo: cd $APP_DIR && git clone <repo_url> ."
echo "4. Run database setup script"
echo "================================"
