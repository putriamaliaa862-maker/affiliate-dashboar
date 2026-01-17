from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    studio_id = Column(Integer, ForeignKey("studios.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    period = Column(String(50), nullable=False)
    total_revenue = Column(Numeric(12, 2), default=0)
    total_commission = Column(Numeric(12, 2), default=0)
    total_ad_spent = Column(Numeric(12, 2), default=0)
    attendance_summary = Column(JSON)  # {present: 0, absent: 0, late: 0}
    data = Column(JSON)  # Additional summary data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    studio = relationship("Studio", back_populates="reports")
