# PRODUCTION CHECKLIST FOR COIN87

## 🔒 Security Pre-Deploy

- [ ] Generate strong SECRET_KEY (min 32 chars random)
- [ ] Generate strong DATABASE_PASSWORD
- [ ] Create separate API keys for each external service
- [ ] Setup SSH key authentication (disable password)
- [ ] Configure UFW firewall (only ports 22, 80, 443)
- [ ] Install fail2ban for SSH protection
- [ ] Review CORS allowed_origins (only production domains)
- [ ] Disable DEBUG mode in production .env
- [ ] Remove or disable API docs (/api/docs) in production

## 📦 Build & Dependencies

- [ ] Run `npm run build` locally to verify frontend builds
- [ ] Check for TypeScript errors (if ignoreBuildErrors is off)
- [ ] Update all dependencies to latest stable versions
- [ ] Run backend tests (if any)
- [ ] Freeze Python dependencies: `pip freeze > requirements.txt`

## 🗄️ Database

- [ ] Create production database and user
- [ ] Run all migrations (init_db.py, create_vote_table.py, create_trading_signals_tables.py)
- [ ] Seed initial RSS sources (seed_rss.py)
- [ ] Test database connection from backend
- [ ] Setup daily backup cron job
- [ ] Test backup restore procedure

## 🚀 Deployment

- [ ] Copy .env.production.template to .env (both backend/frontend)
- [ ] Fill in all environment variables with production values
- [ ] Upload code to VPS via git clone
- [ ] Install backend dependencies in venv
- [ ] Install frontend dependencies via npm
- [ ] Build frontend for production
- [ ] Copy systemd service files to /etc/systemd/system/
- [ ] Enable and start services
- [ ] Verify services are running (systemctl status)

## 🌐 Nginx & SSL

- [ ] Copy Nginx config to /etc/nginx/sites-available/
- [ ] Create symlink in /etc/nginx/sites-enabled/
- [ ] Test Nginx config: `nginx -t`
- [ ] Ensure domain DNS points to VPS IP
- [ ] Run Certbot for SSL certificate
- [ ] Verify HTTPS works
- [ ] Test HTTP to HTTPS redirect

## 📊 Monitoring

- [ ] Test /health endpoint: `curl https://coin87.com/health`
- [ ] Setup health monitor script (cron or systemd timer)
- [ ] Configure Telegram alerts (optional)
- [ ] Setup log rotation for app logs
- [ ] Monitor initial traffic and errors
- [ ] Check disk space availability

## ✅ Functional Testing

- [ ] Visit https://coin87.com (frontend loads)
- [ ] Test API: `curl https://coin87.com/api/v1/config`
- [ ] Login/Register flow works
- [ ] News articles display correctly
- [ ] Voting system works
- [ ] Trading signals dashboard loads
- [ ] Charts render properly
- [ ] Mobile responsive (test on phone)
- [ ] PWA install prompt appears
- [ ] Dark mode toggle works

## 🔄 Post-Deploy

- [ ] Monitor logs for 24 hours
- [ ] Check for any 500 errors
- [ ] Verify database connections stable
- [ ] Test auto-restart (kill a service, check if it restarts)
- [ ] Verify SSL auto-renewal is scheduled
- [ ] Document any production-specific issues
- [ ] Create incident response plan
- [ ] Setup regular maintenance schedule

## 📝 Documentation

- [ ] Update README with production URLs
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Share credentials securely with team (if any)
- [ ] Document backup/restore procedure

## 🎯 Performance

- [ ] Enable gzip compression (Nginx)
- [ ] Check page load times
- [ ] Verify API response times < 500ms
- [ ] Monitor database query performance
- [ ] Setup CDN for static assets (optional)
- [ ] Enable browser caching headers

## 🐛 Rollback Plan

- [ ] Keep previous deployment backed up
- [ ] Know how to revert to previous commit
- [ ] Have database rollback script ready
- [ ] Document emergency contact procedures

---

**Deployment Date:** _____________

**Deployed By:** _____________

**Sign-off:** _____________
