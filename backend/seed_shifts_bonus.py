"""
Seed shift templates and default bonus rates
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.shift_template import ShiftTemplate
from app.models.bonus_rate_rule import BonusRateRule
from datetime import time

def seed_shifts_and_bonus():
    db = SessionLocal()
    try:
        # Check if shifts already exist
        existing = db.query(ShiftTemplate).count()
        if existing > 0:
            print(f"Shifts already exist ({existing} shifts)")
            return
        
        print("Creating shift templates...")
        
        # Create 4 shifts
        shifts = [
            ShiftTemplate(
                name="Shift 1 (Pagi)",
                start_time=time(5, 0),
                end_time=time(10, 0),
                timezone="Asia/Jakarta"
            ),
            ShiftTemplate(
                name="Shift 2 (Siang)",
                start_time=time(10, 0),
                end_time=time(15, 0),
                timezone="Asia/Jakarta"
            ),
            ShiftTemplate(
                name="Shift 3 (Sore)",
                start_time=time(15, 0),
                end_time=time(20, 0),
                timezone="Asia/Jakarta"
            ),
            ShiftTemplate(
                name="Shift 4 (Malam)",
                start_time=time(20, 0),
                end_time=time(0, 0),
                timezone="Asia/Jakarta"
            ),
        ]
        
        for shift in shifts:
            db.add(shift)
        
        db.commit()
        db.refresh(shifts[0])  # Get IDs
        
        print("✅ Shift templates created")
        
        # Create default bonus rules
        print("Creating default bonus rates...")
        
        # Get shift IDs
        shift_ids = {s.name: s.id for s in db.query(ShiftTemplate).all()}
        
        # Default rates for all days (fallback)
        default_all = [
            (shift_ids["Shift 1 (Pagi)"], 500),
            (shift_ids["Shift 2 (Siang)"], 500),
            (shift_ids["Shift 3 (Sore)"], 600),
            (shift_ids["Shift 4 (Malam)"], 800),
        ]
        
        for shift_id, bonus in default_all:
            rule = BonusRateRule(
                shop_id=None,  # Global
                day_type="all",
                shift_id=shift_id,
                bonus_per_order=bonus,
                is_active=True
            )
            db.add(rule)
        
        # Weekend rates (higher)
        weekend_rates = [
            (shift_ids["Shift 1 (Pagi)"], 600),
            (shift_ids["Shift 2 (Siang)"], 600),
            (shift_ids["Shift 3 (Sore)"], 700),
            (shift_ids["Shift 4 (Malam)"], 900),
        ]
        
        for shift_id, bonus in weekend_rates:
            rule = BonusRateRule(
                shop_id=None,  # Global
                day_type="weekend",
                shift_id=shift_id,
                bonus_per_order=bonus,
                is_active=True
            )
            db.add(rule)
        
        db.commit()
        
        print("✅ Default bonus rates created")
        print(f"Total rules: {db.query(BonusRateRule).count()}")
        
        # Display summary
        print("\n📊 Bonus Rates Summary:")
        print("-" * 60)
        for rule in db.query(BonusRateRule).all():
            shift = db.query(ShiftTemplate).get(rule.shift_id)
            print(f"{shift.name} | {rule.day_type:8} | Rp {rule.bonus_per_order:,}/order")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_shifts_and_bonus()
