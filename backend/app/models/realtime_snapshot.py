"""
RealtimeSnapshot Model - For 24H Playwright Bot data storage
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from datetime import datetime
from app.database import Base


class RealtimeSnapshot(Base):
    """Stores realtime scraped data from Playwright bot"""
    __tablename__ = "realtime_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    shopee_account_id = Column(String(100), nullable=False, index=True)
    shop_name = Column(String(255), nullable=True)
    snapshot_type = Column(String(50), nullable=False, index=True)  # creator_live, ads, coins, summary
    data = Column(JSON, nullable=False)
    scraped_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RealtimeSnapshot {self.id} {self.shopee_account_id} {self.snapshot_type}>"


class BotRun(Base):
    """Tracks bot run status for monitoring"""
    __tablename__ = "bot_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(36), unique=True, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="running")  # running, completed, error, stopped
    accounts_total = Column(Integer, default=0)
    accounts_processed = Column(Integer, default=0)
    accounts_success = Column(Integer, default=0)
    accounts_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<BotRun {self.run_id} {self.status}>"
