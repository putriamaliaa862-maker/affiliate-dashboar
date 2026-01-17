from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    shopee_account_id = Column(Integer, ForeignKey("shopee_accounts.id"), nullable=False)
    order_id = Column(String(255), unique=True, index=True)
    total_amount = Column(Numeric(12, 2), nullable=False)
    commission_amount = Column(Numeric(12, 2), default=0)
    status = Column(String(50), default="completed")  # completed, cancelled
    date = Column(DateTime, nullable=False)
    
    # NEW Phase 3: Payout / Commission Tracking
    payout_status = Column(String(50), default="pending")  # pending, validating, paid
    payment_method = Column(String(50), nullable=True)     # transfer, etc
    validated_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # NEW Phase 5: Product & Host Insights
    product_name = Column(String(255), nullable=True)
    product_id = Column(String(100), nullable=True)
    handler_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shopee_account = relationship("ShopeeAccount", back_populates="orders")
    handler = relationship("User", foreign_keys=[handler_user_id])
