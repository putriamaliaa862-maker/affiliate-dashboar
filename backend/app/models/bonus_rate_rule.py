from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class BonusRateRule(Base):
    __tablename__ = "bonus_rate_rules"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shopee_accounts.id"), nullable=True)  # NULL = global rule
    day_type = Column(String(20), nullable=False)  # 'weekday', 'weekend', 'all'
    shift_id = Column(Integer, ForeignKey("shift_templates.id"), nullable=False)
    bonus_per_order = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shift = relationship("ShiftTemplate", back_populates="bonus_rules")
    shop = relationship("ShopeeAccount")

    # Unique constraint: one rule per (shop_id, day_type, shift_id)
    __table_args__ = (
        UniqueConstraint('shop_id', 'day_type', 'shift_id', name='uix_bonus_rule'),
    )
