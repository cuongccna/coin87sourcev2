# Phase 6 - VPS Deployment Guide (No Docker)

## ✅ Hoàn thành tất cả 5 tasks

### 📦 Files đã tạo:

#### 1. Setup Scripts (`scripts/`)
- **setup_vps.sh**: Script tự động cài đặt VPS (Python, Node, PostgreSQL, Redis, UFW, Fail2Ban, Swap)
- **deploy.sh**: Script deploy code lên VPS (pull git, install deps, rebuild, restart services)
- **setup_ssl.sh**: Tự động cài SSL certificate với Certbot
- **backup_db.sh**: Backup PostgreSQL database hàng ngày
- **monitor.py**: Health check service với Telegram alerts

#### 2. Systemd Services (`scripts/systemd/`)
- **coin87-backend.service**: Quản lý FastAPI backend
- **coin87-frontend.service**: Quản lý Next.js frontend  
- **coin87-monitor.service**: Quản lý health monitoring

#### 3. Nginx Configuration (`scripts/nginx/`)
- **coin87.conf**: Reverse proxy config (/api/v1/ → :8000, / → :3000), SSL, GZIP, security headers

#### 4. CI/CD (`.github/workflows/`)
- **deploy.yml**: GitHub Actions workflow (push to main → auto deploy)

#### 5. Cron Jobs (`scripts/`)
- **crontab.txt**: Daily backup, log cleanup

---

## 🚀 Hướng dẫn Triển khai lên VPS

### Bước 1: Chuẩn bị VPS
```bash
# SSH vào VPS với quyền root
ssh root@your-vps-ip

# Tải repo về
apt install git -y
git clone https://github.com/yourusername/coin87sourcev2.git /opt/coin87
cd /opt/coin87

# Chạy setup script
chmod +x scripts/setup_vps.sh
bash scripts/setup_vps.sh
```

### Bước 2: Cấu hình Database
```bash
# Tạo database và user
sudo -u postgres psql
```
```sql
CREATE DATABASE coin87_db;
CREATE USER coin87_user WITH PASSWORD 'your-strong-password';
GRANT ALL PRIVILEGES ON DATABASE coin87_db TO coin87_user;
\q
```

### Bước 3: Setup Environment Variables
```bash
# Tạo file .env
nano /opt/coin87/.env
```
```env
# Database
DATABASE_URL=postgresql+asyncpg://coin87_user:your-password@localhost/coin87_db

# Redis
REDIS_URL=redis://localhost:6379

# API Keys
GEMINI_API_KEY=your-gemini-key
BINANCE_API_KEY=your-binance-key

# Security
SECRET_KEY=your-secret-key-here

# Frontend
NEXT_PUBLIC_API_URL=https://coin87.com/api/v1
```

### Bước 4: Setup Services
```bash
# Copy systemd services
sudo cp scripts/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable coin87-backend
sudo systemctl enable coin87-frontend
sudo systemctl enable coin87-monitor

# Start backend first (để chạy migrations nếu có)
cd /opt/coin87/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run initial migrations
python init_db.py

# Start all services
sudo systemctl start coin87-backend
sudo systemctl start coin87-frontend
sudo systemctl start coin87-monitor

# Check status
sudo systemctl status coin87-backend
sudo systemctl status coin87-frontend
```

### Bước 5: Setup Nginx & SSL
```bash
# Install Nginx
sudo apt install nginx -y

# Copy config
sudo cp scripts/nginx/coin87.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/coin87.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site

# Test config
sudo nginx -t

# Start Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx

# Setup SSL (Cập nhật domain trong script trước)
nano scripts/setup_ssl.sh  # Sửa DOMAIN và EMAIL
chmod +x scripts/setup_ssl.sh
sudo bash scripts/setup_ssl.sh
```

### Bước 6: Setup Backup & Monitoring
```bash
# Setup cron jobs
crontab -e
# Paste nội dung từ scripts/crontab.txt

# Tạo log directory
sudo mkdir -p /var/log/coin87
sudo chown coin87admin:coin87admin /var/log/coin87

# Test backup
bash scripts/backup_db.sh

# Configure Telegram alerts trong monitor.py
nano scripts/monitor.py  # Sửa TELEGRAM_BOT_TOKEN và CHAT_ID
```

### Bước 7: Setup GitHub Actions
```bash
# Tạo SSH key cho GitHub Actions
ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# Copy private key (paste vào GitHub Secrets)
cat ~/.ssh/github_actions
```

Vào GitHub repo → Settings → Secrets and variables → Actions → New secret:
- **VPS_HOST**: IP hoặc domain VPS
- **VPS_USERNAME**: `coin87admin`
- **VPS_SSH_KEY**: Nội dung private key vừa tạo

---

## 📊 Kiểm tra hệ thống

```bash
# Check all services
sudo systemctl status coin87-backend coin87-frontend coin87-monitor

# Check logs
sudo journalctl -u coin87-backend -f
sudo journalctl -u coin87-frontend -f

# Check Nginx
sudo nginx -t
curl http://localhost:8000/docs
curl http://localhost:3000

# Check SSL
curl https://coin87.com/api/v1/health
```

---

## 🔧 Lệnh thường dùng

```bash
# Restart services
sudo systemctl restart coin87-backend coin87-frontend

# View logs
sudo journalctl -u coin87-backend --since today
sudo tail -f /var/log/nginx/coin87_error.log

# Manual backup
bash /opt/coin87/scripts/backup_db.sh

# Check disk space
df -h

# Check memory
free -h

# Check running processes
ps aux | grep uvicorn
ps aux | grep node
```

---

## 🚨 Troubleshooting

### Service không start
```bash
sudo journalctl -u coin87-backend -n 50
# Kiểm tra port conflict: sudo netstat -tulpn | grep 8000
```

### Database connection error
```bash
# Check PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"  # List databases
```

### SSL certificate issues
```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

---

## 📝 Bảo trì

- **Backup tự động**: Chạy mỗi ngày lúc 3:00 AM
- **SSL renew**: Tự động renew 60 ngày 1 lần
- **Monitoring**: Alert qua Telegram khi API down, disk >90%, memory >90%
- **Log retention**: Tự động xóa logs cũ hơn 30 ngày

---

## ✅ Checklist Sau Deploy

- [ ] API docs accessible: https://coin87.com/docs
- [ ] Frontend loads: https://coin87.com
- [ ] SSL certificate valid (ổ khóa xanh)
- [ ] Telegram alerts working
- [ ] Daily backup running (check cron)
- [ ] GitHub Actions deploy success
- [ ] Health monitor service active
- [ ] All systemd services enabled

---

**NEXT**: Phase 7 - Testing & Optimization hoặc quay lại hoàn thiện Frontend (PWA features)
