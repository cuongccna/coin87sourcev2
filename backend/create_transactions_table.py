from sqlalchemy import create_engine
from app.models.base import Base
# Import all models to register them
from app.models import *
from app.core.config import settings

# Create sync engine for creating table
engine = create_engine(settings.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql'))

# Create transactions table
Base.metadata.create_all(bind=engine, tables=[Transaction.__table__])

print("✅ Created transactions table successfully!")
