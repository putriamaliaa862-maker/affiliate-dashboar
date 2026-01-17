from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ActivityLog(Base):
    """
    Activity log for audit trail.
    Tracks all important user actions for security and compliance.
    
    Partitioned by month for scalability.
    """
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    
    # Action details
    action = Column(String(100), nullable=False)  # 'login', 'create_employee', 'edit_commission'
    entity_type = Column(String(50))  # 'employee', 'order', 'report'
    entity_id = Column(Integer)
    
    # Change tracking (use JSON for SQLite compatibility)
    old_value = Column(JSON)
    new_value = Column(JSON)
    
    # Request metadata (use String for IP address for SQLite compatibility)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog {self.action} by user {self.user_id}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
