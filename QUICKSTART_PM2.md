# 🎯 QUICK START - PM2 DEPLOYMENT

## Triển khai LARAI.VN lên VPS với PM2

### Bước 1: Clone & Setup môi trường
```bash
# SSH vào VPS
ssh coin87@YOUR_VPS_IP

# Clone repository
cd /home/coin87
git clone YOUR_REPO coin87sourcev2
cd coin87sourcev2

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.production.larai .env
python init_db.py
python create_trading_signals_tables.py
python create_vote_table.py
deactivate

# Frontend setup
cd ../frontend
npm install
cp .env.production.larai .env.local
npm run build
```

### Bước 2: Setup PM2
```bash
cd /home/coin87/coin87sourcev2
chmod +x scripts/setup_pm2.sh
./scripts/setup_pm2.sh
```

### Bước 3: Setup Cron Jobs
```bash
chmod +x scripts/crontab_larai.sh
chmod +x scripts/health_check.sh
chmod +x scripts/backup_db.sh
./scripts/crontab_larai.sh
```

### Bước 4: Setup Nginx & SSL
```bash
sudo cp deployment/nginx-larai.conf /etc/nginx/sites-available/larai.vn
sudo ln -s /etc/nginx/sites-available/larai.vn /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# SSL Certificate
sudo certbot --nginx -d larai.vn -d www.larai.vn
```

### Bước 5: Verify
```bash
# Kiểm tra PM2
pm2 list
pm2 logs

# Kiểm tra website
curl https://larai.vn
curl https://larai.vn/api/health
```

---

## 🚀 Deploy Code Mới

```bash
cd /home/coin87/coin87sourcev2
./scripts/quick_deploy_larai.sh
```

---

## 📊 Monitoring

```bash
# Realtime monitor
pm2 monit

# View logs
pm2 logs
pm2 logs larai-backend
pm2 logs larai-crawler

# Status
pm2 status
```

---

## 🔧 Quản Lý

```bash
# Restart
pm2 restart all
pm2 restart larai-backend

# Stop
pm2 stop all

# View status
pm2 list
```

---

## 📚 Tài Liệu Chi Tiết

- **[PM2_GUIDE.md](PM2_GUIDE.md)** - Hướng dẫn PM2 đầy đủ
- **[DEPLOY_VPS_LARAI.md](DEPLOY_VPS_LARAI.md)** - Hướng dẫn deploy VPS

---

## 🎯 Services Đang Chạy

| Service | Port | Mô tả |
|---------|------|-------|
| larai-backend | 9010 | FastAPI Backend |
| larai-frontend | 9011 | Next.js Frontend |
| larai-crawler | - | News Crawler |
| larai-ranking | - | Ranking Engine |
| larai-clustering | - | Clustering Engine |
| larai-verifier | - | Truth Verification |

---

## ⏰ Cron Jobs

| Job | Schedule | Mô tả |
|-----|----------|-------|
| Database Backup | Daily 2:00 AM | Backup DB |
| Health Check | Every 15 min | Auto-restart if down |
| Log Cleanup | Weekly | Delete old logs |
| Old News Cleanup | Daily 4:00 AM | Delete 30+ days news |

---

**Website: https://larai.vn**
