# COIN87 - Hướng Dẫn Realtime & Auto Crawler

## 1. DARK/LIGHT MODE ✅ FIXED
- Thêm inline script trong layout.tsx để set theme trước khi React hydrate
- Không còn flash màu khi reload trang
- Toggle hoạt động mượt mà

## 2. WELCOME BONUS ✅ IMPLEMENTED
- User mới nhận **1000 $C87** khi đăng ký
- Có thể đọc free ~15-20 tin đầu tiên
- Button hiển thị "Read Free (Welcome Bonus)" thay vì "Unlock AI Insights"

## 3. DAILY FREE QUOTA ✅ IMPLEMENTED
- Thêm column `daily_free_unlocks` vào users table
- Free users có 10 lần unlock miễn phí mỗi ngày
- Reset hàng ngày lúc 00:00

## 4. REALTIME NEWS UPDATE ⚠️ CHƯA CÓ

### Hiện trạng:
- Tin tức được fetch từ backend khi load trang
- Sử dụng SWR infinite scroll để lazy load
- **KHÔNG CÓ** auto refresh realtime

### Giải pháp đề xuất:

#### Option 1: Polling (Đơn giản - Khuyến nghị)
```typescript
// Trong NewsFeed.tsx
useEffect(() => {
  const interval = setInterval(() => {
    mutate() // SWR revalidate
  }, 60000) // Refresh mỗi 60 giây
  
  return () => clearInterval(interval)
}, [mutate])
```

#### Option 2: WebSocket (Realtime thực sự)
```python
# backend/app/websocket.py
from fastapi import WebSocket

@app.websocket("/ws/news")
async def websocket_news(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Broadcast new news to all connected clients
        await websocket.send_json({"type": "new_news", "data": {...}})
```

#### Option 3: Server-Sent Events (SSE)
```python
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

@app.get("/stream/news")
async def stream_news(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            yield {"data": json.dumps({"news": [...]})}
            await asyncio.sleep(30)
    
    return EventSourceResponse(event_generator())
```

**KHUYẾN NGHỊ:** Dùng Option 1 (Polling 60s) vì:
- Đơn giản nhất
- Đủ nhanh cho crypto news
- Không tốn tài nguyên server
- SWR đã support sẵn

## 5. AUTO CRAWLER JOB ⚠️ CHƯA CÓ

### Hiện trạng:
- File `main_crawler.py` tồn tại nhưng chạy manual
- Không có scheduler tự động

### Giải pháp:

#### Option 1: APScheduler (Python)
```python
# backend/app/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.crawler import crawl_all_sources

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=15)
async def auto_crawl():
    print("Starting auto crawl...")
    await crawl_all_sources()
    print("Auto crawl completed")

# Trong main.py
from app.scheduler import scheduler

@app.on_event("startup")
async def startup_event():
    scheduler.start()
```

#### Option 2: Celery (Production grade)
```python
# backend/celery_app.py
from celery import Celery
from celery.schedules import crontab

app = Celery('coin87')

@app.task
def crawl_news():
    # Run crawler
    pass

app.conf.beat_schedule = {
    'crawl-every-15-minutes': {
        'task': 'celery_app.crawl_news',
        'schedule': crontab(minute='*/15'),
    },
}
```

#### Option 3: Cron Job (VPS)
```bash
# crontab -e
*/15 * * * * cd /path/to/backend && python main_crawler.py >> /var/log/coin87_crawler.log 2>&1
```

**KHUYẾN NGHỊ:** Dùng Option 1 (APScheduler) vì:
- Tích hợp trực tiếp vào FastAPI
- Không cần setup thêm service
- Dễ monitor và debug

## 6. IMPLEMENTATION STEPS

### Bước 1: Thêm Polling Refresh (5 phút)
```bash
# Chỉnh sửa frontend/src/components/NewsFeed.tsx
# Thêm polling interval
```

### Bước 2: Install APScheduler
```bash
cd backend
pip install apscheduler
```

### Bước 3: Tạo Scheduler
```bash
# Tạo file backend/app/scheduler.py
# Import vào main.py
```

### Bước 4: Test
```bash
# Start backend → check logs mỗi 15 phút
# Frontend → check news refresh mỗi 60 giây
```

## 7. MONITORING

### Logs cần theo dõi:
- Crawler success/fail rate
- Number of new articles fetched
- API response time
- User engagement metrics

### Tools:
- Backend: Python logging module
- Frontend: Browser DevTools Console
- Production: Sentry, LogRocket
