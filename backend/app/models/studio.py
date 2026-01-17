from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Studio(Base):
    __tablename__ = "studios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    description = Column(String(1000))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employees = relationship("Employee", back_populates="studio", cascade="all, delete-orphan")
    shopee_accounts = relationship("ShopeeAccount", back_populates="studio", cascade="all, delete-orphan")
    commission_rules = relationship("CommissionRule", back_populates="studio", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="studio", cascade="all, delete-orphan")
