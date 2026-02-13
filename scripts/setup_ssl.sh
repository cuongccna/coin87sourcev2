#!/bin/bash
# SSL Certificate Setup Script using Certbot

echo "================================"
echo "SETTING UP SSL WITH CERTBOT"
echo "================================"

DOMAIN="coin87.com"
EMAIL="admin@coin87.com"  # Replace with your email

# Install Certbot
echo "[1/3] Installing Certbot..."
apt update
apt install -y certbot python3-certbot-nginx

# Obtain certificate
echo "[2/3] Obtaining SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive

# Setup auto-renewal
echo "[3/3] Setting up auto-renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

# Test renewal
certbot renew --dry-run

echo "================================"
echo "✓ SSL Setup Complete!"
echo "================================"
echo "Certificate will auto-renew every 60 days"
echo "Check status: systemctl status certbot.timer"
echo "================================"
