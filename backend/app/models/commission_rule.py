from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class CommissionRule(Base):
    __tablename__ = "commission_rules"

    id = Column(Integer, primary_key=True, index=True)
    studio_id = Column(Integer, ForeignKey("studios.id"), nullable=False)
    role = Column(String(50), nullable=False)  # host, leader, supervisor, director
    commission_type = Column(String(50), nullable=False)  # percentage, fixed
    value = Column(Numeric(10, 2), nullable=False)  # percentage (%) or fixed amount
    min_order_amount = Column(Numeric(12, 2), default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    studio = relationship("Studio", back_populates="commission_rules")
