"""
Simple Direct Migration for Access Code
Works with SQLite - executes SQL directly
"""
from app.database import engine
from sqlalchemy import text

print("=" * 60)
print(" ADDING ACCESS_CODE COLUMN TO USERS TABLE")
print("=" * 60)
print()

# Get database info
from app.models.user import User
from app.database import SessionLocal

db = SessionLocal()

try:
    # Check if column already exists  
    result = db.execute(text("PRAGMA table_info(users)"))
    columns = [row[1] for row in result.fetchall()]
    
    if 'access_code' in columns:
        print("✅ Column 'access_code' already exists!")
        print("   No migration needed.")
    else:
        print("Adding 'access_code' column...")
        
        # Step 1: Add column
        db.execute(text("ALTER TABLE users ADD COLUMN access_code VARCHAR(64)"))
        db.commit()
        print("✅ Column added successfully!")
        
        # Step 2: Create unique index
        try:
            print("Creating unique index...")
            db.execute(text("CREATE UNIQUE INDEX ix_users_access_code ON users(access_code)"))
            db.commit()
            print("✅ Index created successfully!")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print("⚠️  Index already exists (OK)")
            else:
                print(f"⚠️  Warning creating index: {e}")
        
        # Verify
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'access_code' in columns:
            print()
            print("=" * 60)
            print(" ✅ MIGRATION SUCCESSFUL!")
            print("=" * 60)
            print()
            print("Next step: Restart backend server")
        else:
            print("❌ Verification failed!")
            
except Exception as e:
    if 'duplicate column' in str(e).lower():
        print("✅ Column already exists!")
    else:
        print(f"❌ Error: {e}")
        db.rollback()
finally:
    db.close()
