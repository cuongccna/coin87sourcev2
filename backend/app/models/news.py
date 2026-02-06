from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(String, nullable=False)
    url = Column(String, unique=True, index=True, nullable=False)
    raw_content = Column(Text)
    tags = Column(JSON, default=[])
    topic_category = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source = relationship("app.models.source.Source")
