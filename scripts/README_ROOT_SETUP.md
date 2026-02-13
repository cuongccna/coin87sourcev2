# ⚡ CẬP NHẬT: ROOT USER SETUP

## Thay Đổi Cấu Hình

Tất cả scripts và configs đã được cập nhật cho setup VPS với:
- **User:** root (thay vì coin87)
- **Thư mục:** /var/www/coin87sourcev2 (thay vì /home/coin87/coin87sourcev2)

---

## ✅ FILES ĐÃ CẬP NHẬT

### 1. PM2 Configuration
- ✅ [ecosystem.config.js](../ecosystem.config.js)
  - Paths: `/var/www/coin87sourcev2/*`
  - User: root

### 2. Setup Scripts
- ✅ [scripts/setup_pm2.sh](setup_pm2.sh)
  - User check: root
  - No sudo needed
  - Paths updated

- ✅ [scripts/quick_deploy_larai.sh](quick_deploy_larai.sh)
  - APP_DIR: `/var/www/coin87sourcev2`
  - PM2 reload instead of systemctl

- ✅ [scripts/crontab_larai.sh](crontab_larai.sh)
  - All paths: `/var/www/coin87sourcev2/*`

- ✅ [scripts/backup_db.sh](backup_db.sh)
  - BACKUP_DIR: `/var/www/backups`

- ✅ [scripts/health_check.sh](health_check.sh)
  - No changes needed (checks ports)

### 3. Systemd Services (Optional)
- ✅ [deployment/coin87-backend.service](../deployment/coin87-backend.service)
  - User: root
  - WorkingDirectory: `/var/www/coin87sourcev2/backend`

- ✅ [deployment/coin87-frontend.service](../deployment/coin87-frontend.service)
  - User: root
  - WorkingDirectory: `/var/www/coin87sourcev2/frontend`

### 4. Documentation
- ✅ [QUICKSTART_ROOT.md](../QUICKSTART_ROOT.md) - **MỚI**
  - Hướng dẫn setup cho root user
  - Từ đầu đến cuối

- ✅ [scripts/verify_deployment.sh](verify_deployment.sh) - **MỚI**
  - Script kiểm tra toàn bộ deployment
  - Check 30+ điều kiện

---

## 🚀 HƯỚNG DẪN DEPLOY

### Quick Start (Root User)

```bash
# 1. SSH vào VPS
ssh root@YOUR_VPS_IP

# 2. Clone project
mkdir -p /var/www
cd /var/www
git clone YOUR_REPO coin87sourcev2
cd coin87sourcev2

# 3. Setup backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.production.larai .env
python init_db.py
python create_trading_signals_tables.py
python create_vote_table.py
deactivate

# 4. Setup frontend
cd ../frontend
npm install
cp .env.production.larai .env.local
npm run build

# 5. Setup PM2
npm install -g pm2
cd /var/www/coin87sourcev2
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u root --hp /root

# 6. Setup cron jobs
chmod +x scripts/*.sh
./scripts/crontab_larai.sh

# 7. Setup Nginx & SSL
cp deployment/nginx-larai.conf /etc/nginx/sites-available/larai.vn
ln -s /etc/nginx/sites-available/larai.vn /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
certbot --nginx -d larai.vn -d www.larai.vn

# 8. Verify deployment
chmod +x scripts/verify_deployment.sh
./scripts/verify_deployment.sh
```

---

## 📊 KIỂM TRA DEPLOYMENT

```bash
# Run verification script
cd /var/www/coin87sourcev2
./scripts/verify_deployment.sh
```

Script sẽ kiểm tra:
- ✅ System (Python, Node, PM2, Nginx, PostgreSQL)
- ✅ Database connection
- ✅ Backend (venv, .env, port, health)
- ✅ Frontend (build, .env.local, port)
- ✅ PM2 processes
- ✅ Nginx config & SSL
- ✅ Cron jobs
- ✅ Logs & backups
- ✅ Public access (HTTPS)

---

## 🔧 QUẢN LÝ

### PM2 Commands
```bash
pm2 list          # Xem tất cả processes
pm2 logs          # Xem logs realtime
pm2 monit         # Monitor CPU/RAM
pm2 restart all   # Restart tất cả
```

### Deploy Code Mới
```bash
cd /var/www/coin87sourcev2
./scripts/quick_deploy_larai.sh
```

### Xem Logs
```bash
pm2 logs                              # All logs
pm2 logs larai-backend                # Backend only
tail -f /var/log/coin87/health.log    # Health check
tail -f /var/log/coin87/backup.log    # Backups
```

---

## 📁 CẤU TRÚC THƯ MỤC

```
/var/www/
├── coin87sourcev2/          # Main project
│   ├── backend/
│   │   ├── venv/
│   │   ├── .env             # Backend config
│   │   └── app/
│   ├── frontend/
│   │   ├── .next/           # Build output
│   │   ├── .env.local       # Frontend config
│   │   └── src/
│   ├── ecosystem.config.js  # PM2 config
│   ├── scripts/
│   │   ├── setup_pm2.sh
│   │   ├── quick_deploy_larai.sh
│   │   ├── crontab_larai.sh
│   │   ├── health_check.sh
│   │   ├── backup_db.sh
│   │   └── verify_deployment.sh
│   └── deployment/
│       ├── nginx-larai.conf
│       ├── coin87-backend.service
│       └── coin87-frontend.service
└── backups/                 # Database backups
    └── coin87v2_db_*.sql.gz

/var/log/coin87/             # All logs
├── backend-out.log
├── backend-error.log
├── frontend-out.log
├── crawler-out.log
├── health.log
└── backup.log
```

---

## ⚠️ LƯU Ý QUAN TRỌNG

1. **Backup trước khi deploy:**
   ```bash
   ./scripts/backup_db.sh
   ```

2. **Luôn test trên local trước:**
   ```bash
   cd backend
   source venv/bin/activate
   pytest
   ```

3. **Xem logs khi có lỗi:**
   ```bash
   pm2 logs larai-backend --lines 100 --err
   ```

4. **PM2 auto-restart:** Service tự động restart khi crash

5. **Cron jobs tự động:**
   - Database backup: 2 AM hàng ngày
   - Health check: Mỗi 15 phút
   - Log cleanup: Chủ nhật hàng tuần

---

## 📚 TÀI LIỆU

- [QUICKSTART_ROOT.md](../QUICKSTART_ROOT.md) - Setup từ đầu
- [PM2_GUIDE.md](../PM2_GUIDE.md) - PM2 chi tiết
- [DEPLOY_VPS_LARAI.md](../DEPLOY_VPS_LARAI.md) - Deploy VPS

---

## 🆘 HỖ TRỢ

Nếu gặp vấn đề:
1. Chạy: `./scripts/verify_deployment.sh`
2. Xem logs: `pm2 logs`
3. Check database: `psql -U coin87v2_user -d coin87v2_db -h localhost`
4. Restart: `pm2 restart all`

---

**✅ Tất cả scripts đã sẵn sàng cho root user và thư mục /var/www/**
