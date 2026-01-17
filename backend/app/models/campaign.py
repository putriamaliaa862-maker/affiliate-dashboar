from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    shopee_account_id = Column(Integer, ForeignKey("shopee_accounts.id"), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    campaign_id = Column(String(255), unique=True, index=True)
    budget = Column(Numeric(12, 2), default=0)
    spent = Column(Numeric(12, 2), default=0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default="active")  # active, paused, ended
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shopee_account = relationship("ShopeeAccount", back_populates="campaigns")
