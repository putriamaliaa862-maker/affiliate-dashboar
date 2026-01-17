#!/usr/bin/env python
"""
Seed script to create initial super admin user.
Run this once during initial setup.

Usage:
    python seed_admin.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.auth.jwt import get_password_hash
from sqlalchemy.exc import IntegrityError


def create_super_admin():
    """Create default super admin user if it doesn't exist"""
    
    # Create tables first
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if super admin already exists
        existing_admin = db.query(User).filter(User.role == "super_admin").first()
        
        if existing_admin:
            print(f"✓ Super admin already exists: {existing_admin.username}")
            print(f"  Email: {existing_admin.email}")
            print(f"  Created: {existing_admin.created_at}")
            return
        
        # Default credentials
        username = "admin"
        email = "admin@affiliatedashboard.com"
        password = "Admin123!"
        
        # Create super admin user
        super_admin = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            full_name="Super Administrator",
            role="super_admin",
            is_active=True
        )
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print("="*60)
        print("✓ Super Admin Created Successfully!")
        print("="*60)
        print(f"Username: {username}")
        print(f"Email:    {email}")
        print(f"Password: {password}")
        print("="*60)
        print("\n⚠️  IMPORTANT: Change the default password after first login!")
        print("   Use the change password endpoint: POST /api/users/{id}/change-password")
        print("\n🔐 You can now login at: POST /api/auth/login")
        print("="*60)
        
    except IntegrityError as e:
        db.rollback()
        print(f"✗ Error: {e}")
        print("  Username or email may already exist.")
    except Exception as e:
        db.rollback()
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  AFFILIATE DASHBOARD - SEED SUPER ADMIN")
    print("="*60 + "\n")
    
    create_super_admin()
    
    print("\n✓ Seed script completed.\n")
