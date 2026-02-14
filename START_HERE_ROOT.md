# 🎯 DEPLOY LARAI.VN - ROOT USER

## Setup Nhanh (5 Phút)

```bash
# Trên VPS (đã login root)
cd /var/www
git clone YOUR_REPO coin87sourcev2
cd coin87sourcev2

# Backend
cd backend && python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-production.txt
cp .env.production.larai .env
python init_db.py && python create_trading_signals_tables.py && python create_vote_table.py
deactivate

# Frontend
cd ../frontend && npm install && cp .env.production.larai .env.local && npm run build

# PM2
npm install -g pm2
cd /var/www/coin87sourcev2
pm2 start ecosystem.config.js && pm2 save && pm2 startup

# Cron
chmod +x scripts/*.sh && ./scripts/crontab_larai.sh

# Nginx
cp deployment/nginx-larai.conf /etc/nginx/sites-available/larai.vn
ln -s /etc/nginx/sites-available/larai.vn /etc/nginx/sites-enabled/
systemctl reload nginx
certbot --nginx -d larai.vn -d www.larai.vn

# Verify
./scripts/verify_deployment.sh
```

---

## Deploy Update

```bash
cd /var/www/coin87sourcev2
./scripts/quick_deploy_larai.sh
```

---

## Monitor

```bash
pm2 monit              # Realtime monitor
pm2 logs               # All logs
pm2 list               # Process list
```

---

## Services

| Service | Port | Status |
|---------|------|--------|
| Backend | 9010 | `pm2 logs larai-backend` |
| Frontend | 9011 | `pm2 logs larai-frontend` |
| Crawler | - | `pm2 logs larai-crawler` |
| Ranking | - | `pm2 logs larai-ranking` |
| Clustering | - | `pm2 logs larai-clustering` |
| Verifier | - | `pm2 logs larai-verifier` |

---

## Tài Liệu

- **[QUICKSTART_ROOT.md](QUICKSTART_ROOT.md)** ← BẮT ĐẦU TẠI ĐÂY
- [PM2_GUIDE.md](PM2_GUIDE.md) - PM2 chi tiết
- [scripts/README_ROOT_SETUP.md](scripts/README_ROOT_SETUP.md) - File updates

---

## Cấu Hình

- User: **root**
- Thư mục: **/var/www/coin87sourcev2**
- Backend: **port 9010**
- Frontend: **port 9011**
- Domain: **larai.vn**

---

**🚀 https://larai.vn**
