#!/bin/bash
# Simple Health Monitor for Coin87
# Run as systemd service or via cron every 5 minutes

API_URL="https://coin87.com/health"
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
LOG_FILE="/var/log/coin87/health-monitor.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_telegram_alert() {
    local message="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${message}" \
        -d "parse_mode=HTML" > /dev/null
}

# Check API health
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL" --max-time 10)

if [ "$HTTP_STATUS" != "200" ]; then
    log "🚨 ALERT: API is DOWN! Status: $HTTP_STATUS"
    send_telegram_alert "🚨 <b>Coin87 ALERT</b>%0A%0AAPI is DOWN!%0AStatus: $HTTP_STATUS%0ATime: $(date '+%Y-%m-%d %H:%M:%S')"
else
    log "✅ API is healthy (Status: $HTTP_STATUS)"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    log "⚠️ WARNING: Disk usage is ${DISK_USAGE}%"
    send_telegram_alert "⚠️ <b>Coin87 WARNING</b>%0A%0ADisk usage: ${DISK_USAGE}%%"
fi

# Check memory usage (optional)
MEM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEM_USAGE" -gt 90 ]; then
    log "⚠️ WARNING: Memory usage is ${MEM_USAGE}%"
    send_telegram_alert "⚠️ <b>Coin87 WARNING</b>%0A%0AMemory usage: ${MEM_USAGE}%%"
fi
