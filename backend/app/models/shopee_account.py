from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ShopeeAccount(Base):
    __tablename__ = "shopee_accounts"

    id = Column(Integer, primary_key=True, index=True)
    studio_id = Column(Integer, ForeignKey("studios.id"), nullable=False)
    account_name = Column(String(255), nullable=False)
    shopee_account_id = Column(String(255), unique=True, index=True)
    refresh_token = Column(String(500))
    access_token = Column(String(500))
    token_expire_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    last_synced_at = Column(DateTime, nullable=True)  # NEW: Track extension sync
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    studio = relationship("Studio", back_populates="shopee_accounts")
    campaigns = relationship("Campaign", back_populates="shopee_account", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="shopee_account", cascade="all, delete-orphan")
    live_snapshots = relationship("LiveProductSnapshot", back_populates="account", cascade="all, delete-orphan")
    assignments = relationship("ShopeeAccountAssignment", back_populates="shopee_account", cascade="all, delete-orphan")  # NEW
