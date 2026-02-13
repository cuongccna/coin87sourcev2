#!/bin/bash
# Health Check Script for LARAI.VN
# Checks if services are running and restarts if needed

LOG_FILE="/var/log/coin87/health.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Function to log messages
log() {
    echo "[$TIMESTAMP] $1"
}

# Function to check if service is responding
check_service() {
    local name=$1
    local url=$2
    local timeout=5
    
    if curl -sf --max-time $timeout "$url" > /dev/null 2>&1; then
        return 0  # Service OK
    else
        return 1  # Service DOWN
    fi
}

# Function to restart PM2 app
restart_app() {
    local app_name=$1
    log "⚠️  Restarting $app_name..."
    pm2 restart $app_name
    sleep 5
}

# Check Backend
if ! check_service "Backend" "http://127.0.0.1:9010/api/health"; then
    log "❌ Backend is DOWN"
    restart_app "larai-backend"
else
    log "✅ Backend is UP"
fi

# Check Frontend
if ! check_service "Frontend" "http://127.0.0.1:9011"; then
    log "❌ Frontend is DOWN"
    restart_app "larai-frontend"
else
    log "✅ Frontend is UP"
fi

# Check PM2 processes status
STOPPED_APPS=$(pm2 jlist | jq -r '.[] | select(.pm2_env.status != "online") | .name' 2>/dev/null)

if [ -n "$STOPPED_APPS" ]; then
    log "⚠️  Found stopped apps: $STOPPED_APPS"
    log "🔄 Restarting all PM2 processes..."
    pm2 restart all
else
    log "✅ All PM2 processes are online"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    log "⚠️  WARNING: Disk usage is ${DISK_USAGE}%"
fi

# Check memory
MEM_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    log "⚠️  WARNING: Memory usage is ${MEM_USAGE}%"
fi

log "📊 Health check completed"
