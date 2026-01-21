"""
Shopee Account Assignment Model
Many-to-many relationship between users and shopee accounts
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ShopeeAccountAssignment(Base):
    """
    Assignment of users to shopee accounts with role scoping.
    
    Allows flexible account access:
    - One user can have multiple accounts
    - One account can be assigned to multiple users (e.g., leader + host)
    """
    __tablename__ = "shopee_account_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    shopee_account_id = Column(Integer, ForeignKey("shopee_accounts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_scope = Column(String(20), nullable=False)  # owner/supervisor/partner/leader/host/viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    shopee_account = relationship("ShopeeAccount", back_populates="assignments")
    user = relationship("User", back_populates="account_assignments")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'shopee_account_id', name='uq_user_account'),
    )
    
    def __repr__(self):
        return f"<ShopeeAccountAssignment user_id={self.user_id} account_id={self.shopee_account_id} role={self.role_scope}>"
