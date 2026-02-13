"""Health Check & Monitoring Service for Coin87
Run as systemd service: systemctl enable coin87-monitor
"""
import asyncio
import aiohttp
import psutil
from datetime import datetime
from typing import Optional

# Configuration
API_URL = "https://coin87.com/api/v1/health"  
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"  # Get from @BotFather
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # Your Telegram user ID
CHECK_INTERVAL = 60  # seconds
DISK_THRESHOLD = 90  # percent

class HealthMonitor:
    def __init__(self):
        self.last_alert_time = None
        self.alert_cooldown = 300  # 5 minutes between alerts
    
    async def send_telegram_alert(self, message: str):
        """Send alert via Telegram"""
        if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN":
            print(f"[ALERT] {message}")
            return
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"🚨 COIN87 ALERT\n\n{message}",
            "parse_mode": "HTML"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        print(f"Alert sent: {message}")
        except Exception as e:
            print(f"Failed to send alert: {e}")
    
    async def check_api_health(self) -> bool:
        """Check if API is responding"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=10) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"API health check failed: {e}")
            return False
    
    def check_disk_space(self) -> tuple[bool, int]:
        """Check disk usage"""
        disk = psutil.disk_usage('/')
        usage = disk.percent
        return usage < DISK_THRESHOLD, int(usage)
    
    def check_memory(self) -> tuple[bool, int]:
        """Check memory usage"""
        mem = psutil.virtual_memory()
        return mem.percent < 90, int(mem.percent)
    
    async def run_checks(self):
        """Run all health checks"""
        now = datetime.now()
        
        # API Health
        api_healthy = await self.check_api_health()
        if not api_healthy:
            await self.send_telegram_alert(
                "API is DOWN!\n"
                f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                "Please check the service immediately."
            )
        
        # Disk Space
        disk_ok, disk_usage = self.check_disk_space()
        if not disk_ok:
            await self.send_telegram_alert(
                f"DISK SPACE WARNING!\n"
                f"Usage: {disk_usage}%\n"
                f"Threshold: {DISK_THRESHOLD}%"
            )
        
        # Memory
        mem_ok, mem_usage = self.check_memory()
        if not mem_ok:
            await self.send_telegram_alert(
                f"MEMORY WARNING!\n"
                f"Usage: {mem_usage}%"
            )
        
        # Status log
        status = "✓" if api_healthy else "✗"
        print(f"[{now.strftime('%H:%M:%S')}] {status} API | Disk: {disk_usage}% | Mem: {mem_usage}%")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        print("Starting Coin87 Health Monitor...")
        print(f"API URL: {API_URL}")
        print(f"Check interval: {CHECK_INTERVAL}s")
        
        while True:
            try:
                await self.run_checks()
            except Exception as e:
                print(f"Monitor error: {e}")
            
            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor = HealthMonitor()
    asyncio.run(monitor.monitor_loop())
