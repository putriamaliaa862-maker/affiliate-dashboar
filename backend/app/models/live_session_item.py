"""
Live Session Item Model - Produk yang dipromosikan dalam live
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class LiveSessionItem(Base):
    """Model untuk produk yang dipromosikan dalam live session"""
    
    __tablename__ = "live_session_items"
    
    id = Column(Integer, primary_key=True)
    live_session_id = Column(Integer, ForeignKey("live_sessions.id"), nullable=False)
    
    # Product Info
    item_id = Column(String(255), nullable=False)
    product_name = Column(String(500), nullable=False)
    product_image_url = Column(String(500))
    
    # Pricing
    regular_price = Column(Float)
    live_price = Column(Float)
    discount_percentage = Column(Float, default=0.0)
    
    # Sales
    quantity_sold = Column(Integer, default=0)
    total_sales_amount = Column(Float, default=0.0)
    
    # Commission
    commission_per_item = Column(Float, default=0.0)
    total_commission = Column(Float, default=0.0)
    
    # Promotion
    promotion_type = Column(String(100))  # flash_sale, bundle, etc
    is_featured = Column(String(50), default=False)
    
    # Tracking
    promoted_at = Column(DateTime)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LiveSessionItem {self.product_name}>"
