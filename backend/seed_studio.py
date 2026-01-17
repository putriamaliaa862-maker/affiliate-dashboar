"""
Quick seed script to create a default studio for testing
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.studio import Studio

def seed_default_studio():
    db = SessionLocal()
    try:
        # Check if studio exists
        existing = db.query(Studio).first()
        if existing:
            print(f"Studio already exists: ID={existing.id}, Name={existing.name}")
            return existing.id
        
        # Create default studio
        studio = Studio(
            name="Default Studio",
            location="Main Office",
            is_active=True
        )
        db.add(studio)
        db.commit()
        db.refresh(studio)
        
        print(f"✅ Created default studio with ID: {studio.id}")
        return studio.id
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_studio()
