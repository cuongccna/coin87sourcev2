# GitHub Secrets Configuration

Để GitHub Actions hoạt động, bạn cần thêm các secrets sau vào repository:

## Cách thêm secrets:
1. Vào repository trên GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"

## Required Secrets:

### VPS_HOST
- **Giá trị**: IP address hoặc domain của VPS
- **Ví dụ**: `123.45.67.89` hoặc `coin87.com`

### VPS_USERNAME
- **Giá trị**: Username SSH (thường là `coin87admin`)
- **Ví dụ**: `coin87admin`

### VPS_SSH_KEY
- **Giá trị**: Private SSH key (KHÔNG phải public key)
- **Cách lấy**: 
  ```bash
  # Trên VPS, tạo SSH key cho GitHub Actions
  ssh-keygen -t ed25519 -f ~/.ssh/github_actions -N ""
  
  # Copy public key vào authorized_keys
  cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys
  
  # Copy private key (paste vào GitHub Secret)
  cat ~/.ssh/github_actions
  ```

## Hướng dẫn setup lần đầu trên VPS:

```bash
# 1. SSH vào VPS
ssh root@your-vps-ip

# 2. Chạy setup script
chmod +x /opt/coin87/scripts/setup_vps.sh
bash /opt/coin87/scripts/setup_vps.sh

# 3. Clone repository
su - coin87admin
cd /opt/coin87
git clone https://github.com/yourusername/coin87sourcev2.git .

# 4. Setup systemd services
sudo cp /opt/coin87/scripts/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable coin87-backend coin87-frontend
sudo systemctl start coin87-backend coin87-frontend

# 5. Setup Nginx
sudo apt install nginx
sudo cp /opt/coin87/scripts/nginx/coin87.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/coin87.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 6. Setup SSL
bash /opt/coin87/scripts/setup_ssl.sh
```

## Kiểm tra sau khi deploy:

```bash
# Check service status
sudo systemctl status coin87-backend
sudo systemctl status coin87-frontend

# Check logs
sudo journalctl -u coin87-backend -f
sudo journalctl -u coin87-frontend -f

# Test endpoints
curl http://localhost:8000/docs
curl http://localhost:3000
```
