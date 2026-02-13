# 🚀 QUICK SETUP - LARAI.VN (ROOT USER)

## Setup VPS với Root User

### Thông Số Cấu Hình
- **User:** root
- **Thư mục:** /var/www/coin87sourcev2
- **Backend Port:** 9010
- **Frontend Port:** 9011
- **Domain:** larai.vn

---

## BƯỚC 1: CÀI ĐẶT CƠ BẢN

### 1.1. SSH vào VPS
```bash
ssh root@YOUR_VPS_IP
```

### 1.2. Cài Dependencies
```bash
# Update system
apt update && apt upgrade -y

# PostgreSQL
apt install postgresql postgresql-contrib -y

# Python 3.11
apt install python3.11 python3.11-venv python3-pip -y

# Node.js 18 (via NVM)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Nginx
apt install nginx -y

# Redis
apt install redis-server -y

# Certbot
apt install certbot python3-certbot-nginx -y

# jq (for health check script)
apt install jq -y
```

---

## BƯỚC 2: SETUP DATABASE

```bash
# Chuyển sang postgres user
sudo -u postgres psql

# Trong PostgreSQL shell
CREATE USER coin87v2_user WITH PASSWORD 'Cuongnv123456';
CREATE DATABASE coin87v2_db OWNER coin87v2_user;
GRANT ALL PRIVILEGES ON DATABASE coin87v2_db TO coin87v2_user;
\q

# Test connection
psql -U coin87v2_user -d coin87v2_db -h localhost -W
# Password: Cuongnv123456
# \q để thoát
```

---

## BƯỚC 3: CLONE PROJECT

```bash
# Tạo thư mục /var/www nếu chưa có
mkdir -p /var/www
cd /var/www

# Clone repository
git clone YOUR_REPO_URL coin87sourcev2
cd coin87sourcev2
```

---

## BƯỚC 4: SETUP BACKEND

```bash
cd /var/www/coin87sourcev2/backend

# Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy .env
cp .env.production.larai .env

# Chạy migrations
python init_db.py
python create_trading_signals_tables.py
python create_vote_table.py
python add_transactions_table.py

# Test backend
uvicorn app.main:app --host 127.0.0.1 --port 9010
# Ctrl+C để thoát sau khi test
```

---

## BƯỚC 5: SETUP FRONTEND

```bash
cd /var/www/coin87sourcev2/frontend

# Install dependencies
npm install

# Copy .env
cp .env.production.larai .env.local

# Build
npm run build

# Test
PORT=9011 npm start
# Ctrl+C để thoát sau khi test
```

---

## BƯỚC 6: SETUP PM2

```bash
# Install PM2 globally
npm install -g pm2

# Tạo log directory
mkdir -p /var/log/coin87

# Start tất cả services
cd /var/www/coin87sourcev2
pm2 start ecosystem.config.js

# Setup auto-start on boot
pm2 save
pm2 startup systemd -u root --hp /root

# Verify
pm2 list
pm2 logs
```

---

## BƯỚC 7: SETUP CRON JOBS

```bash
cd /var/www/coin87sourcev2

# Make scripts executable
chmod +x scripts/crontab_larai.sh
chmod +x scripts/health_check.sh
chmod +x scripts/backup_db.sh

# Install crontab
./scripts/crontab_larai.sh

# Verify
crontab -l
```

---

## BƯỚC 8: SETUP NGINX & SSL

```bash
# Copy nginx config
cp /var/www/coin87sourcev2/deployment/nginx-larai.conf /etc/nginx/sites-available/larai.vn

# Enable site
ln -s /etc/nginx/sites-available/larai.vn /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Test config
nginx -t

# Reload nginx
systemctl reload nginx

# Setup SSL
mkdir -p /var/www/certbot
certbot --nginx -d larai.vn -d www.larai.vn
```

---

## BƯỚC 9: VERIFY

```bash
# Kiểm tra PM2
pm2 list
pm2 monit

# Kiểm tra services
curl http://127.0.0.1:9010/api/health  # Backend
curl http://127.0.0.1:9011              # Frontend
curl https://larai.vn                   # Public site
curl https://larai.vn/api/health        # API

# Xem logs
pm2 logs
tail -f /var/log/coin87/health.log
```

---

## QUẢN LÝ HÀNG NGÀY

### Deploy Code Mới
```bash
cd /var/www/coin87sourcev2
./scripts/quick_deploy_larai.sh
```

### Xem Status
```bash
pm2 list
pm2 monit
```

### Xem Logs
```bash
pm2 logs
pm2 logs larai-backend
pm2 logs larai-crawler
```

### Restart Services
```bash
pm2 restart all
pm2 restart larai-backend
```

---

## TROUBLESHOOTING

### PM2 không start
```bash
# Xem logs chi tiết
pm2 logs larai-backend --lines 100 --err

# Delete & restart
pm2 delete all
pm2 start ecosystem.config.js
```

### Port bị chiếm
```bash
lsof -i :9010
lsof -i :9011

# Kill process
kill -9 <PID>
```

### Database connection error
```bash
# Test database
psql -U coin87v2_user -d coin87v2_db -h localhost

# Check .env
cat /var/www/coin87sourcev2/backend/.env | grep DATABASE
```

---

## 📋 CHECKLIST

- [ ] Dependencies installed
- [ ] Database created
- [ ] Backend .env configured
- [ ] Backend migrations done
- [ ] Frontend .env.local configured
- [ ] Frontend built
- [ ] PM2 started (6 services)
- [ ] PM2 auto-startup enabled
- [ ] Crontab installed
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] https://larai.vn accessible
- [ ] https://larai.vn/api/health returns OK

---

## 🎯 PM2 SERVICES

```
larai-backend      - FastAPI (port 9010)
larai-frontend     - Next.js (port 9011)
larai-crawler      - News crawler (24/7)
larai-ranking      - Ranking engine
larai-clustering   - Clustering engine
larai-verifier     - Truth verification
```

---

## ⏰ CRON JOBS

```
2:00 AM daily      - Database backup
Every 15 min       - Health check & auto-restart
Every 6 hours      - PM2 save state
Sunday 3:00 AM     - Log cleanup
4:00 AM daily      - Old news cleanup
```

---

**✅ Setup hoàn tất! Website chạy tại: https://larai.vn**
