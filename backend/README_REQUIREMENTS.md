# ⚠️ KHẮC PHỤC LỖI KIVY TRÊN LINUX

## Vấn Đề
File `requirements.txt` chứa các package Windows-only như:
- `kivy-deps.angle==0.3.3`
- `kivy-deps.glew==0.3.1`
- `kivy-deps.sdl2==0.6.0`

Những package này **KHÔNG CÓ** trên Linux và gây lỗi khi deploy.

---

## Giải Pháp

### ✅ Đã Tạo File Mới
**[backend/requirements-production.txt](../backend/requirements-production.txt)**

File này chỉ chứa packages cần thiết cho production:
- FastAPI, Uvicorn
- PostgreSQL (asyncpg, SQLAlchemy)
- Redis
- Google Gemini AI
- Web scraping (BeautifulSoup, feedparser)
- Authentication & Security
- **KHÔNG CÓ** Kivy hay Windows-only packages

---

## Cách Sử Dụng

### Trên VPS (Linux)
```bash
cd /var/www/coin87sourcev2/backend
source venv/bin/activate
pip install -r requirements-production.txt
```

### Trên Local (Windows - development)
```bash
cd backend
source venv/bin/activate  # hoặc venv\Scripts\activate trên Windows
pip install -r requirements.txt  # Full requirements
```

---

## Deploy Script Đã Cập Nhật

[scripts/quick_deploy_larai.sh](quick_deploy_larai.sh) tự động:
1. Kiểm tra file `requirements-production.txt`
2. Nếu có → dùng file này (production)
3. Nếu không → dùng `requirements.txt` và bỏ qua lỗi

```bash
if [ -f "requirements-production.txt" ]; then
    pip install -r requirements-production.txt
else
    pip install -r requirements.txt --ignore-installed || true
fi
```

---

## Hướng Dẫn Đã Cập Nhật

Các file sau đã được cập nhật để dùng `requirements-production.txt`:
- ✅ [QUICKSTART_ROOT.md](../QUICKSTART_ROOT.md)
- ✅ [START_HERE_ROOT.md](../START_HERE_ROOT.md)
- ✅ [scripts/quick_deploy_larai.sh](quick_deploy_larai.sh)

---

## Nếu Vẫn Gặp Lỗi

### Cách 1: Dùng requirements-production.txt
```bash
cd /var/www/coin87sourcev2/backend
source venv/bin/activate
pip install -r requirements-production.txt
deactivate
```

### Cách 2: Bỏ qua lỗi
```bash
pip install -r requirements.txt --ignore-installed || true
```

### Cách 3: Cài từng package quan trọng
```bash
pip install fastapi uvicorn[standard] asyncpg sqlalchemy alembic
pip install google-generativeai beautifulsoup4 feedparser
pip install redis python-jose passlib bcrypt
```

---

## Packages Quan Trọng Cho Production

| Category | Packages |
|----------|----------|
| **Web Framework** | fastapi, uvicorn, pydantic |
| **Database** | asyncpg, sqlalchemy, alembic |
| **AI/LLM** | google-generativeai |
| **Web Scraping** | beautifulsoup4, feedparser, newspaper3k |
| **Auth** | python-jose, passlib, bcrypt |
| **Cache** | redis, hiredis |
| **Web Push** | py-vapid, pywebpush |

---

## Test Sau Khi Cài

```bash
cd /var/www/coin87sourcev2/backend
source venv/bin/activate

# Test import
python -c "import fastapi; print('FastAPI OK')"
python -c "import asyncpg; print('AsyncPG OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK')"
python -c "import google.generativeai; print('Gemini OK')"

# Test start
uvicorn app.main:app --host 127.0.0.1 --port 9010
# Ctrl+C để stop
```

---

**✅ GIẢI PHÁP: Dùng `requirements-production.txt` khi deploy lên VPS Linux**
