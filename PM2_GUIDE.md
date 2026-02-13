# 🚀 PM2 DEPLOYMENT GUIDE - LARAI.VN

## 📌 Tại Sao Dùng PM2?

PM2 là process manager mạnh mẽ hơn systemd cho Node.js/Python apps:
- ✅ Auto-restart khi crash
- ✅ Zero-downtime reload
- ✅ Built-in monitoring (CPU, RAM)
- ✅ Log management tốt hơn
- ✅ Quản lý cron jobs dễ dàng
- ✅ Cluster mode cho scaling

---

## BƯỚC 1: SETUP PM2 (Lần Đầu)

### 1.1. Cài Đặt PM2
```bash
# SSH vào VPS
ssh coin87@YOUR_VPS_IP

# Chạy script setup
cd /home/coin87/coin87sourcev2
chmod +x scripts/setup_pm2.sh
./scripts/setup_pm2.sh
```

Script sẽ:
- Cài PM2 globally
- Start tất cả services (backend, frontend, crawler, ranking, clustering, verifier)
- Setup auto-start khi reboot
- Lưu process list

### 1.2. Verify Services
```bash
# Xem danh sách processes
pm2 list

# Monitor realtime (CPU, RAM)
pm2 monit

# Xem logs tất cả
pm2 logs

# Xem logs từng service
pm2 logs larai-backend
pm2 logs larai-frontend
pm2 logs larai-crawler
```

---

## BƯỚC 2: SETUP CRON JOBS

### 2.1. Cài Đặt Crontab
```bash
cd /home/coin87/coin87sourcev2
chmod +x scripts/crontab_larai.sh
./scripts/crontab_larai.sh
```

### 2.2. Các Cron Jobs Được Cài
| Job | Thời gian | Mô tả |
|-----|-----------|-------|
| **Database Backup** | 2:00 AM hàng ngày | Backup DB, giữ 7 ngày |
| **PM2 Save** | Mỗi 6h | Lưu trạng thái PM2 |
| **Log Rotation** | Chủ nhật 3:00 AM | Xóa logs cũ >7 ngày |
| **Cleanup Old News** | 4:00 AM hàng ngày | Xóa tin >30 ngày |
| **Health Check** | Mỗi 15 phút | Kiểm tra & restart nếu down |
| **PM2 Resurrect** | Mỗi giờ | Đảm bảo PM2 chạy |

### 2.3. Kiểm Tra Crontab
```bash
# Xem crontab hiện tại
crontab -l

# Test health check
./scripts/health_check.sh

# Xem log health check
tail -f /var/log/coin87/health.log
```

---

## BƯỚC 3: CÁC SERVICES ĐANG CHẠY

### 3.1. Main Services (2 processes)
```
larai-backend    - FastAPI (port 9010)
larai-frontend   - Next.js (port 9011)
```

### 3.2. Background Jobs (4 processes)
```
larai-crawler    - Crawl tin tức 24/7
larai-ranking    - Tính ranking tin
larai-clustering - Gom nhóm tin liên quan
larai-verifier   - Truth Engine verification
```

### 3.3. Xem Trạng Thái
```bash
# List tất cả
pm2 list

# Chi tiết 1 service
pm2 show larai-backend

# Monitor realtime
pm2 monit
```

---

## QUẢN LÝ PM2

### Start/Stop/Restart
```bash
# Start all
pm2 start ecosystem.config.js

# Restart all
pm2 restart all

# Reload (zero-downtime)
pm2 reload all

# Stop all
pm2 stop all

# Delete all
pm2 delete all
```

### Quản Lý Từng Service
```bash
# Restart backend only
pm2 restart larai-backend

# Stop crawler
pm2 stop larai-crawler

# View backend logs
pm2 logs larai-backend --lines 100

# Clear logs
pm2 flush
```

### Monitoring
```bash
# Realtime monitor
pm2 monit

# Xem status
pm2 status

# Xem memory usage
pm2 list | grep "MEM"
```

---

## DEPLOY CODE MỚI

### Cách 1: Quick Deploy Script
```bash
cd /home/coin87/coin87sourcev2
./scripts/quick_deploy_larai.sh
```

### Cách 2: Manual Deploy
```bash
cd /home/coin87/coin87sourcev2

# Pull code
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Frontend
cd ../frontend
npm install
npm run build

# Reload PM2 (zero-downtime)
pm2 reload ecosystem.config.js

# Hoặc restart all
pm2 restart all
```

---

## XEM LOGS

### PM2 Logs
```bash
# All logs realtime
pm2 logs

# Specific service
pm2 logs larai-backend
pm2 logs larai-crawler

# Last 100 lines
pm2 logs --lines 100

# Only errors
pm2 logs --err

# Clear all logs
pm2 flush
```

### System Logs
```bash
# Backend logs
tail -f /var/log/coin87/backend-out.log
tail -f /var/log/coin87/backend-error.log

# Crawler logs
tail -f /var/log/coin87/crawler-out.log

# Health check logs
tail -f /var/log/coin87/health.log

# Backup logs
tail -f /var/log/coin87/backup.log
```

---

## TROUBLESHOOTING

### Service Không Start
```bash
# Xem logs chi tiết
pm2 logs larai-backend --lines 100 --err

# Delete và start lại
pm2 delete larai-backend
pm2 start ecosystem.config.js --only larai-backend

# Kiểm tra port
sudo lsof -i :9010
sudo lsof -i :9011
```

### Memory Leak
```bash
# Xem memory usage
pm2 list

# Restart service tốn nhiều RAM
pm2 restart larai-backend

# Set max memory restart (auto restart nếu vượt 1GB)
pm2 start ecosystem.config.js --max-memory-restart 1G
```

### Database Connection Error
```bash
# Test database
psql -U coin87v2_user -d coin87v2_db -h localhost

# Kiểm tra .env backend
cat /home/coin87/coin87sourcev2/backend/.env | grep DATABASE_URL

# Restart backend
pm2 restart larai-backend
```

### PM2 Không Auto-Start Sau Reboot
```bash
# Setup lại startup
pm2 startup systemd -u coin87 --hp /home/coin87

# Chạy lệnh sudo được hiển thị
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u coin87 --hp /home/coin87

# Save process list
pm2 save
```

---

## BACKUP & RESTORE

### Manual Backup
```bash
# Backup database
./scripts/backup_db.sh

# Xem backups
ls -lh /home/coin87/backups/

# Restore từ backup
cd /home/coin87/backups
gunzip coin87v2_db_20260214_020000.sql.gz
psql -U coin87v2_user -d coin87v2_db -h localhost < coin87v2_db_20260214_020000.sql
```

### Auto Backup (Cron)
Auto chạy mỗi ngày lúc 2:00 AM

```bash
# Xem backup logs
tail -f /var/log/coin87/backup.log

# List backups (giữ 7 ngày gần nhất)
ls -lh /home/coin87/backups/
```

---

## PERFORMANCE TUNING

### Scaling Backend (Cluster Mode)
```javascript
// Trong ecosystem.config.js, sửa:
{
  name: 'larai-backend',
  instances: 4,  // Số CPU cores
  exec_mode: 'cluster'
}

// Reload
pm2 reload ecosystem.config.js
```

### Optimize Memory
```bash
# Set max memory restart
pm2 start ecosystem.config.js --max-memory-restart 1G

# Giảm số workers của uvicorn trong ecosystem.config.js
args: 'app.main:app --host 127.0.0.1 --port 9010 --workers 2'
```

---

## USEFUL PM2 COMMANDS

```bash
# Process Management
pm2 list                    # List all processes
pm2 start ecosystem.config.js  # Start all
pm2 restart all             # Restart all
pm2 reload all              # Zero-downtime reload
pm2 stop all                # Stop all
pm2 delete all              # Delete all
pm2 save                    # Save process list

# Logs
pm2 logs                    # All logs
pm2 logs larai-backend      # Specific service
pm2 logs --lines 200        # Last 200 lines
pm2 logs --err              # Only errors
pm2 flush                   # Clear logs

# Monitoring
pm2 monit                   # Realtime monitor
pm2 status                  # Status overview
pm2 show larai-backend      # Detailed info

# Startup
pm2 startup                 # Generate startup script
pm2 save                    # Save current processes
pm2 resurrect               # Restore saved processes
pm2 unstartup               # Remove startup

# Advanced
pm2 describe larai-backend  # Full process description
pm2 reset larai-backend     # Reset restart counter
pm2 sendSignal SIGUSR2 larai-backend  # Send signal
```

---

## 📊 MONITORING DASHBOARD

### PM2 Plus (Optional - Free tier)
```bash
# Link to PM2 Plus
pm2 link YOUR_SECRET_KEY YOUR_PUBLIC_KEY

# Dashboard: https://app.pm2.io
```

Có thể monitor từ web:
- CPU/Memory usage
- Error alerts
- Logs
- Custom metrics

---

## ✅ CHECKLIST

- [ ] PM2 installed (`pm2 --version`)
- [ ] All services started (`pm2 list`)
- [ ] Auto-startup configured (`pm2 save`)
- [ ] Crontab installed (`crontab -l`)
- [ ] Health check running (`tail -f /var/log/coin87/health.log`)
- [ ] Logs directory created (`ls /var/log/coin87`)
- [ ] Backup script tested (`./scripts/backup_db.sh`)
- [ ] Services accessible:
  - [ ] https://larai.vn (frontend)
  - [ ] https://larai.vn/api/health (backend)

---

**🎉 PM2 setup hoàn tất! Hệ thống tự động quản lý, restart, backup, và monitor.**
