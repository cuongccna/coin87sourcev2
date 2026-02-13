# 🚀 HƯỚNG DẪN DEPLOY VPS - LARAI.VN

## 📋 Thông Số Cấu Hình
- **Domain:** larai.vn
- **Backend Port:** 9010
- **Frontend Port:** 9011
- **VPS:** Ubuntu 22.04 LTS (min 2GB RAM)

---

## BƯỚC 1: CÀI ĐẶT MÔI TRƯỜNG VPS

### 1.1. SSH vào VPS
```bash
ssh root@YOUR_VPS_IP
```

### 1.2. Tạo User và Cài Đặt Cơ Bản
```bash
# Update hệ thống
apt update && apt upgrade -y

# Tạo user coin87
adduser coin87
usermod -aG sudo coin87
su - coin87
```

### 1.3. Cài Đặt Dependencies
```bash
# PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Node.js 18 (via NVM)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Nginx
sudo apt install nginx -y

# Redis (optional cho caching)
sudo apt install redis-server -y

# Certbot cho SSL
sudo apt install certbot python3-certbot-nginx -y
```

---

## BƯỚC 2: SETUP DATABASE

```bash
# Chuyển sang postgres user
sudo -u postgres psql

# Tạo database (trong PostgreSQL shell)
CREATE USER coin87v2_user WITH PASSWORD 'Cuongnv123456';
CREATE DATABASE coin87v2_db OWNER coin87v2_user;
GRANT ALL PRIVILEGES ON DATABASE coin87v2_db TO coin87v2_user;
\q

# Test kết nối
psql -U coin87v2_user -d coin87v2_db -h localhost -W
# Nhập password: Cuongnv123456
# Gõ \q để thoát
```

---

## BƯỚC 3: CLONE PROJECT

```bash
cd /home/coin87
git clone YOUR_GIT_REPOSITORY coin87sourcev2
cd coin87sourcev2
```

---

## BƯỚC 4: SETUP BACKEND

### 4.1. Cài Đặt Backend
```bash
cd /home/coin87/coin87sourcev2/backend

# Tạo virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.2. Cấu Hình Environment
```bash
# Copy file .env
cp .env.production.larai .env

# Kiểm tra nội dung (đảm bảo đúng thông số)
cat .env
```

**File .env phải có:**
- `DATABASE_URL=postgresql+asyncpg://coin87v2_user:Cuongnv123456@localhost:5432/coin87v2_db`
- `PORT=9010`
- `ALLOWED_ORIGINS=https://larai.vn,https://www.larai.vn`
- `GEMINI_API_KEY=...`
- `VAPID_PUBLIC_KEY=...`
- `VAPID_PRIVATE_KEY=...`

### 4.3. Chạy Migrations
```bash
# Kích hoạt venv nếu chưa
source venv/bin/activate

# Chạy init database
python init_db.py

# Tạo các bảng cần thiết
python create_trading_signals_tables.py
python create_vote_table.py
python add_transactions_table.py

# Seed dữ liệu mẫu (nếu cần)
python seed_rss.py
```

### 4.4. Test Backend
```bash
# Test chạy thử
uvicorn app.main:app --host 127.0.0.1 --port 9010

# Mở tab terminal khác, test API
curl http://127.0.0.1:9010/api/health

# Ctrl+C để stop test server
```

---

## BƯỚC 5: SETUP FRONTEND

### 5.1. Cài Đặt Frontend
```bash
cd /home/coin87/coin87sourcev2/frontend

# Cài dependencies
npm install
```

### 5.2. Cấu Hình Environment
```bash
# Copy file .env
cp .env.production.larai .env.local

# Kiểm tra nội dung
cat .env.local
```

**File .env.local phải có:**
- `NEXT_PUBLIC_API_BASE_URL=https://larai.vn`
- `NEXT_PUBLIC_SOCKET_URL=wss://larai.vn`
- `NEXT_PUBLIC_ENABLE_PAYWALL=true`
- `NEXT_PUBLIC_VAPID_KEY=...`

### 5.3. Build Production
```bash
npm run build
```

### 5.4. Test Frontend
```bash
# Test chạy thử
PORT=9011 npm start

# Mở tab terminal khác
curl http://127.0.0.1:9011

# Ctrl+C để stop test server
```

---

## BƯỚC 6: SETUP SYSTEMD SERVICES

### 6.1. Tạo Thư Mục Logs
```bash
sudo mkdir -p /var/log/coin87
sudo chown coin87:coin87 /var/log/coin87
```

### 6.2. Cài Đặt Service Files
```bash
cd /home/coin87/coin87sourcev2

# Copy service files
sudo cp deployment/coin87-backend.service /etc/systemd/system/
sudo cp deployment/coin87-frontend.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload
```

### 6.3. Start Services
```bash
# Enable auto-start khi boot
sudo systemctl enable coin87-backend
sudo systemctl enable coin87-frontend

# Start services
sudo systemctl start coin87-backend
sudo systemctl start coin87-frontend

# Kiểm tra status
sudo systemctl status coin87-backend
sudo systemctl status coin87-frontend
```

### 6.4. Xem Logs (Troubleshooting)
```bash
# Logs realtime
sudo journalctl -u coin87-backend -f
sudo journalctl -u coin87-frontend -f

# Hoặc xem file log
tail -f /var/log/coin87/backend.log
tail -f /var/log/coin87/frontend.log
```

---

## BƯỚC 7: SETUP NGINX

### 7.1. Cài Đặt Nginx Config
```bash
# Copy nginx config
sudo cp /home/coin87/coin87sourcev2/deployment/nginx-larai.conf /etc/nginx/sites-available/larai.vn

# Enable site
sudo ln -s /etc/nginx/sites-available/larai.vn /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 7.2. Setup SSL Certificate (Let's Encrypt)
```bash
# Tạo folder cho certbot
sudo mkdir -p /var/www/certbot

# Chạy certbot
sudo certbot --nginx -d larai.vn -d www.larai.vn

# Các câu hỏi:
# - Email: nhập email của bạn
# - Terms: A (Agree)
# - Share email: N (No)
# - Redirect HTTP to HTTPS: 2 (Yes)

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## BƯỚC 8: KIỂM TRA DEPLOYMENT

### 8.1. Kiểm Tra Services
```bash
# Kiểm tra backend port
curl http://127.0.0.1:9010/api/health

# Kiểm tra frontend port
curl http://127.0.0.1:9011

# Kiểm tra Nginx
curl http://larai.vn   # Sẽ redirect sang HTTPS
curl https://larai.vn  # Frontend
curl https://larai.vn/api/health  # Backend API
```

### 8.2. Kiểm Tra Logs
```bash
# Backend logs
tail -f /var/log/coin87/backend.log

# Frontend logs
tail -f /var/log/coin87/frontend.log

# Nginx logs
tail -f /var/log/nginx/larai-access.log
tail -f /var/log/nginx/larai-error.log
```

---

## BƯỚC 9: QUẢN LÝ THƯỜNG XUYÊN

### 9.1. Restart Services
```bash
# Restart backend
sudo systemctl restart coin87-backend

# Restart frontend
sudo systemctl restart coin87-frontend

# Restart nginx
sudo systemctl reload nginx
```

### 9.2. Update Code (Deploy mới)
```bash
cd /home/coin87/coin87sourcev2

# Pull code mới
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
# Chạy migrations nếu có
sudo systemctl restart coin87-backend

# Update frontend
cd /home/coin87/coin87sourcev2/frontend
npm install
npm run build
sudo systemctl restart coin87-frontend
```

### 9.3. Backup Database
```bash
# Backup manual
sudo -u postgres pg_dump coin87v2_db > backup_$(date +%Y%m%d).sql

# Restore từ backup
sudo -u postgres psql coin87v2_db < backup_20240214.sql
```

### 9.4. Monitor Resources
```bash
# CPU/Memory usage
htop

# Disk usage
df -h

# Service status
sudo systemctl status coin87-backend coin87-frontend nginx postgresql
```

---

## 🔧 TROUBLESHOOTING

### Backend không start
```bash
# Xem logs chi tiết
sudo journalctl -u coin87-backend -n 100 --no-pager

# Kiểm tra port 9010 có bị chiếm
sudo lsof -i :9010

# Kiểm tra database connection
psql -U coin87v2_user -d coin87v2_db -h localhost
```

### Frontend không start
```bash
# Xem logs chi tiết
sudo journalctl -u coin87-frontend -n 100 --no-pager

# Kiểm tra port 9011 có bị chiếm
sudo lsof -i :9011

# Rebuild frontend
cd /home/coin87/coin87sourcev2/frontend
rm -rf .next
npm run build
```

### SSL Certificate Issues
```bash
# Renew SSL
sudo certbot renew

# Force renew
sudo certbot renew --force-renewal
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R coin87:coin87 /home/coin87/coin87sourcev2
sudo chown -R coin87:coin87 /var/log/coin87
```

---

## 📝 CHECKLIST DEPLOY

- [ ] VPS setup (user, dependencies)
- [ ] PostgreSQL database created
- [ ] Backend .env configured
- [ ] Backend migrations run
- [ ] Frontend .env.local configured
- [ ] Frontend build successful
- [ ] Systemd services installed & running
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] Domain pointing to VPS IP
- [ ] Backend health check: `https://larai.vn/api/health`
- [ ] Frontend accessible: `https://larai.vn`
- [ ] Logs checked for errors

---

## 🎯 QUICK DEPLOY SCRIPT

Sau khi setup lần đầu xong, dùng script này để deploy nhanh:

```bash
#!/bin/bash
# File: /home/coin87/deploy.sh

cd /home/coin87/coin87sourcev2

# Pull code
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart coin87-backend

# Frontend
cd /home/coin87/coin87sourcev2/frontend
npm install
npm run build
sudo systemctl restart coin87-frontend

# Status
echo "=== Backend Status ==="
sudo systemctl status coin87-backend --no-pager | head -n 5

echo "=== Frontend Status ==="
sudo systemctl status coin87-frontend --no-pager | head -n 5

echo "✅ Deploy completed!"
```

Tạo script:
```bash
nano /home/coin87/deploy.sh
# Paste nội dung script ở trên
chmod +x /home/coin87/deploy.sh
```

Chạy deploy:
```bash
/home/coin87/deploy.sh
```

---

**✅ HOÀN TẤT! Website của bạn đã chạy tại https://larai.vn**
