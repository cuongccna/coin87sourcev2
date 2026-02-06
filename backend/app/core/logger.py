import sys
from loguru import logger

# Configure Loguru
# Remove default handler
logger.remove()

# Add console handler with color
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add file handler (Daily rotation, 10MB retention)
logger.add(
    "logs/coin87_{time:YYYY-MM-DD}.log",
    rotation="00:00", 
    retention="10 days",
    compression="zip",
    level="DEBUG",
    backtrace=True,
    diagnose=True
)

# Export logger for import in other files
log = logger
