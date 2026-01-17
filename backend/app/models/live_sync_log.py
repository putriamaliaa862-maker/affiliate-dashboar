from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class LiveSyncLog(Base):
    """
    Tracks synchronization operations from Chrome Extension
    Logs both auto and manual sync attempts
    """
    __tablename__ = "live_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("shopee_accounts.id"), nullable=False, index=True)
    
    # Sync metadata
    snapshot_date = Column(Date, nullable=False, index=True)
    synced_at = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(Text, nullable=False)  # 'SUCCESS' or 'FAIL'
    total_rows = Column(Integer, default=0)
    message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    shopee_account = relationship("ShopeeAccount")
