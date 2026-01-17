from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Text, Boolean, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AdsDailySpend(Base):
    __tablename__ = "ads_daily_spend"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    shopee_account_id = Column(Integer, ForeignKey("shopee_accounts.id"), nullable=False)
    spend_amount = Column(Integer, nullable=False, default=0)
    spend_type = Column(String(50), default="general") # 'audience', 'live', 'general'
    note = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now)

    # Relationships
    account = relationship("ShopeeAccount")
    creator = relationship("User")

    __table_args__ = (
        UniqueConstraint('date', 'shopee_account_id', 'spend_type', name='uix_date_account_type'),
    )

class AdsDailyMetrics(Base):
    __tablename__ = "ads_daily_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    shopee_account_id = Column(Integer, ForeignKey("shopee_accounts.id"), nullable=False)
    roas_manual = Column(Float, nullable=True)
    revenue_manual = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now)

    account = relationship("ShopeeAccount")
    creator = relationship("User")

    __table_args__ = (
        UniqueConstraint('date', 'shopee_account_id', name='uix_date_account_metrics'),
    )

class AudienceBudgetSetting(Base):
    __tablename__ = "audience_budget_settings"

    id = Column(Integer, primary_key=True, index=True)
    shopee_account_id = Column(Integer, ForeignKey("shopee_accounts.id"), nullable=False, unique=True)
    min_remaining_threshold = Column(Integer, default=3000)
    min_gap_minutes = Column(Integer, default=10)
    active_start_time = Column(String(20), default="05:00:00") # SQLite stores time as text usually
    active_end_time = Column(String(20), default="00:00:00")
    max_daily_add_budget = Column(Integer, nullable=True)
    is_enabled = Column(Boolean, default=True)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    account = relationship("ShopeeAccount")
    updater = relationship("User")

class AudienceBudgetAction(Base):
    __tablename__ = "audience_budget_actions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    time = Column(String(20), nullable=False) # Time as string
    shopee_account_id = Column(Integer, ForeignKey("shopee_accounts.id"), nullable=False)
    remaining_before = Column(Integer, nullable=True)
    added_amount = Column(Integer, nullable=False)
    remaining_after = Column(Integer, nullable=True)
    trigger_reason = Column(String(50), default="threshold") # 'threshold', 'manual'
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.now)

    account = relationship("ShopeeAccount")
    creator = relationship("User")
