from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database import Base


class TrackedStock(Base):
    __tablename__ = "tracked_stocks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())