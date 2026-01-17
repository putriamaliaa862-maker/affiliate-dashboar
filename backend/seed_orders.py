"""
Seed sample order data for testing reports
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.order import Order
from app.models.shopee_account import ShopeeAccount
from datetime import datetime, timedelta
from decimal import Decimal
import random

def seed_orders():
    db = SessionLocal()
    try:
        # Check if we have shopee accounts
        accounts = db.query(ShopeeAccount).all()
        if not accounts:
            print("No Shopee accounts found. Creating a sample account...")
            account = ShopeeAccount(
                shop_name="Sample Shopee Store",
                shop_url="https://shopee.co.id/sample",
                is_active=True
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            accounts = [account]
        
        # Check existing orders
        existing_count = db.query(Order).count()
        print(f"Existing orders: {existing_count}")
        
        if existing_count >= 10:
            print("Already have sample orders")
            return
        
        # Create sample orders for last 30 days
        print("Creating sample orders...")
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(50):
            days_offset = random.randint(0, 30)
            order_date = base_date + timedelta(days=days_offset)
            
            gmv = Decimal(random.randint(50000, 500000))
            commission_rate = Decimal('0.05')  # 5%
            commission = gmv * commission_rate
            
            order = Order(
                shopee_account_id=random.choice(accounts).id,
                order_id=f"SHP{order_date.strftime('%Y%m%d')}{i:04d}",
                total_amount=gmv,
                commission_amount=commission,
                status='completed',
                date=order_date
            )
            db.add(order)
        
        db.commit()
        
        # Count
        total = db.query(Order).count()
        print(f"✅ Seed complete! Total orders in DB: {total}")
        
        # Show date range
        first = db.query(Order).order_by(Order.date).first()
        last = db.query(Order).order_by(Order.date.desc()).first()
        print(f"Date range: {first.date.date()} to {last.date.date()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_orders()
