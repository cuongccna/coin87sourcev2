# LARAI.VN - Deploy VPS

## Setup (Run Once)

```bash
cd /var/www
git clone YOUR_REPO coin87sourcev2
cd coin87sourcev2
chmod +x deployNew.sh
./deployNew.sh
```

## SSL Certificate
```bash
certbot --nginx -d larai.vn -d www.larai.vn
```

## Management
```bash
pm2 list          # Status
pm2 logs          # Logs
pm2 restart all   # Restart
pm2 monit         # Monitor
```

## Update Code
```bash
cd /var/www/coin87sourcev2
git pull
cd backend && source venv/bin/activate && pip install -U fastapi uvicorn && deactivate
cd ../frontend && npm install && npm run build
pm2 restart all
```

**Domain:** larai.vn  
**Backend:** 9010  
**Frontend:** 9011
