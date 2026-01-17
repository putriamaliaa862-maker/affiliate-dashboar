"""
Create tables for Bonus Engine V2
"""
import sys
sys.path.insert(0, '.')

from app.database import engine, Base
from app.models.shift_template import ShiftTemplate
from app.models.bonus_rate_rule import BonusRateRule

# Import all other models to ensure they're registered
from app.models.user import User
from app.models.employee import Employee
from app.models.shopee_account import ShopeeAccount
from app.models.order import Order
from app.models.attendance import Attendance
from app.models.commission import Commission

def create_bonus_tables():
    """Create shift_templates and bonus_rate_rules tables"""
    print("Creating Bonus Engine V2 tables...")
    
    try:
        # Create only the new tables
        ShiftTemplate.__table__.create(bind=engine, checkfirst=True)
        print("✅ shift_templates table created")
        
        BonusRateRule.__table__.create(bind=engine, checkfirst=True)
        print("✅ bonus_rate_rules table created")
        
        print("\n✅ All Bonus Engine V2 tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_bonus_tables()
