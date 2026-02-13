from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        *([logging.FileHandler(settings.LOG_FILE)] if settings.LOG_FILE else [])
    ]
)

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Coin87 API",
    description="Crypto News Aggregator API with AI Intelligence",
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/api/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# CORS - Use settings from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting Coin87 API in {settings.ENVIRONMENT} mode")
    logger.info(f"CORS origins: {settings.cors_origins}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Coin87 API")

@app.get("/")
async def root():
    return {"message": "Coin87 API is Service is Up"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

@app.get("/api/v1/config")
async def get_config():
    """Public endpoint to get feature flags"""
    return {
        "enable_paywall": settings.ENABLE_PAYWALL
    }
