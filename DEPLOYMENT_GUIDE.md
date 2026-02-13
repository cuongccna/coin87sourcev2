# COIN87 PRODUCTION DEPLOYMENT GUIDE (Manual VPS)

## 📋 Pre-requisites

### VPS Requirements
- Ubuntu 22.04 LTS
- Minimum 2GB RAM (4GB recommended for AI features)
- 20GB SSD storage
- Domain name pointed to VPS IP (coin87.com)

### Local Requirements
- Git configured
- SSH access to VPS
- Database dump ready (if migrating)

---

## 🚀 DEPLOYMENT STEPS

### 1. Server Setup (First Time Only)

```bash
# SSH into VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Create coin87 user
adduser coin87
usermod -aG sudo coin87

# Switch to coin87 user
su - coin87
```

### 2. Install Dependencies

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 18 via NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 3. Setup Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE USER coin87v2_user WITH PASSWORD 'YOUR_STRONG_PASSWORD';
CREATE DATABASE coin87v2_db OWNER coin87v2_user;
GRANT ALL PRIVILEGES ON DATABASE coin87v2_db TO coin87v2_user;
\q

# Test connection
psql -U coin87v2_user -d coin87v2_db -h localhost
```

### 4. Clone Project

```bash
cd /home/coin87
git clone https://github.com/YOUR_USERNAME/coin87sourcev2.git
cd coin87sourcev2
```

### 5. Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
cp .env.production.template .env
nano .env  # Edit with real values

# Run database migrations
python init_db.py
python create_trading_signals_tables.py
python create_vote_table.py

# Seed initial data (optional)
python seed_rss.py

# Test backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# Press Ctrl+C after verifying it starts
```

### 6. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Copy and configure .env
cp .env.production.template .env.local
nano .env.local  # Set NEXT_PUBLIC_API_BASE_URL=https://api.coin87.com

# Build for production
npm run build

# Test frontend
npm start
# Press Ctrl+C after verifying it starts
```

### 7. Setup Systemd Services

```bash
# Create log directory
sudo mkdir -p /var/log/coin87
sudo chown coin87:coin87 /var/log/coin87

# Copy service files
sudo cp deployment/coin87-backend.service /etc/systemd/system/
sudo cp deployment/coin87-frontend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services (auto-start on boot)
sudo systemctl enable coin87-backend
sudo systemctl enable coin87-frontend

# Start services
sudo systemctl start coin87-backend
sudo systemctl start coin87-frontend

# Check status
sudo systemctl status coin87-backend
sudo systemctl status coin87-frontend
```

### 8. Configure Nginx

```bash
# Copy Nginx config
sudo cp deployment/nginx-coin87.conf /etc/nginx/sites-available/coin87

# Create symlink
sudo ln -s /etc/nginx/sites-available/coin87 /etc/nginx/sites-enabled/

# Remove default config
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 9. Setup SSL Certificate

```bash
# Ensure domain points to VPS IP first!
# Then run Certbot
sudo certbot --nginx -d coin87.com -d www.coin87.com

# Follow prompts, choose redirect HTTP to HTTPS

# Test auto-renewal
sudo certbot renew --dry-run
```

### 10. Setup Database Backup

```bash
# Create backup directory
mkdir -p /home/coin87/backups/database

# Copy backup script
cp deployment/backup_db.sh /home/coin87/scripts/
chmod +x /home/coin87/scripts/backup_db.sh

# Test backup
/home/coin87/scripts/backup_db.sh

# Setup cron job (daily at 3 AM)
crontab -e
# Add this line:
0 3 * * * /home/coin87/scripts/backup_db.sh >> /var/log/coin87/backup.log 2>&1
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Backend service running: `sudo systemctl status coin87-backend`
- [ ] Frontend service running: `sudo systemctl status coin87-frontend`
- [ ] Nginx running: `sudo systemctl status nginx`
- [ ] SSL certificate active: Visit https://coin87.com (🔒 should show)
- [ ] API accessible: `curl https://coin87.com/api/v1/config`
- [ ] Frontend loads: Visit https://coin87.com in browser
- [ ] Database backup working: Check `/home/coin87/backups/database`
- [ ] Logs accessible: `tail -f /var/log/coin87/backend.log`

---

## 🔄 UPDATE PROCEDURE (Deploy New Code)

```bash
# SSH into VPS
ssh coin87@YOUR_VPS_IP

# Pull latest code
cd /home/coin87/coin87sourcev2
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt  # If dependencies changed
# Run any new migrations if needed
sudo systemctl restart coin87-backend

# Update frontend
cd ../frontend
npm install  # If dependencies changed
npm run build
sudo systemctl restart coin87-frontend

# Check status
sudo systemctl status coin87-backend
sudo systemctl status coin87-frontend
```

---

## 🛡️ SECURITY BEST PRACTICES

1. **Firewall (UFW)**
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

2. **SSH Key Authentication**
```bash
# On local machine, generate key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to server
ssh-copy-id coin87@YOUR_VPS_IP

# Disable password auth on server
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

3. **Fail2Ban (Block brute force)**
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📊 MONITORING

### Check Logs
```bash
# Backend logs
sudo journalctl -u coin87-backend -f

# Frontend logs
sudo journalctl -u coin87-frontend -f

# Nginx logs
sudo tail -f /var/log/nginx/coin87-access.log
sudo tail -f /var/log/nginx/coin87-error.log
```

### System Resources
```bash
# CPU/Memory
htop

# Disk usage
df -h

# Database size
sudo -u postgres psql -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database;"
```

---

## 🆘 TROUBLESHOOTING

### Backend won't start
```bash
# Check logs
sudo journalctl -u coin87-backend -n 50

# Test manually
cd /home/coin87/coin87sourcev2/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend won't start
```bash
# Check logs
sudo journalctl -u coin87-frontend -n 50

# Test manually
cd /home/coin87/coin87sourcev2/frontend
npm run build
npm start
```

### Nginx 502 Bad Gateway
```bash
# Check if backend/frontend services are running
sudo systemctl status coin87-backend
sudo systemctl status coin87-frontend

# Check Nginx error log
sudo tail -f /var/log/nginx/coin87-error.log
```

### Database connection failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U coin87v2_user -d coin87v2_db -h localhost
```

---

## 📝 MAINTENANCE

### Update SSL Certificate (Auto-renews, but to manually trigger)
```bash
sudo certbot renew
sudo systemctl reload nginx
```

### Rotate Logs
```bash
# Nginx logs rotate automatically
# App logs - add logrotate config
sudo nano /etc/logrotate.d/coin87
```

### Backup Restore
```bash
# List backups
ls -lh /home/coin87/backups/database/

# Restore from backup
gunzip < /home/coin87/backups/database/coin87_backup_TIMESTAMP.sql.gz | psql -U coin87v2_user -d coin87v2_db -h localhost
```

---

## 🎯 PRODUCTION READY!

Your Coin87 app is now:
- ✅ Running on VPS with systemd
- ✅ Secured with HTTPS (Let's Encrypt)
- ✅ Reverse proxied through Nginx
- ✅ Auto-restart on crashes
- ✅ Daily database backups
- ✅ Production-optimized builds

**Access:** https://coin87.com
**API:** https://coin87.com/api/v1/
