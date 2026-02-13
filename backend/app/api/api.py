from fastapi import APIRouter
from app.api.endpoints import news, auth, users, votes, trends, admin, economy, signals

api_router = APIRouter()
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(votes.router, prefix="/news", tags=["votes"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])  # Task 5.8
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])  # Task 5.10
api_router.include_router(economy.router, prefix="/economy", tags=["economy"])  # Task 7.3
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])  # Trading Signals
