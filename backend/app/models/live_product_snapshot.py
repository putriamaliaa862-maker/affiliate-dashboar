from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class LiveProductSnapshot(Base):
    """Live Product Daily Snapshot"""
    __tablename__ = "live_product_daily_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Date and Account identifiers
    snapshot_date = Column(Date, nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('shopee_accounts.id'), nullable=False, index=True)
    
    # Scope identifiers (for RBAC)
    studio_id = Column(Integer, ForeignKey("studios.id"), nullable=True, index=True)
    leader_id = Column(Integer, nullable=True, index=True)  # For leader scope
    host_id = Column(Integer, nullable=True, index=True)  # For host scope
    
    # Product identifiers
    product_id = Column(Text, nullable=False, index=True)  # Shopee product ID
    product_name = Column(Text, nullable=False)
    
    # Performance metrics (updated names)
    sold_qty = Column(Integer, default=0)
    gmv = Column(Float, default=0.0)  # Gross Merchandise Value
    clicks = Column(Integer, nullable=True)  # Optional: clicks/views
    
    # Metadata
    source = Column(String(50), default='live')  # 'live', 'manual', 'extension'
    raw_data = Column(JSON, nullable=True)  # Changed from JSONB to JSON for SQLite compatibility
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    studio = relationship("Studio")
    account = relationship("ShopeeAccount", back_populates="live_snapshots")
