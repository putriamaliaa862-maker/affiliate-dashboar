"""
Run Phase 2 Database Migrations - Fixed Version
Executes each statement individually with proper error handling
"""
from app.database import engine, SessionLocal
from sqlalchemy import text

def run_phase2_migrations():
    print("=" * 60)
    print(" PHASE 2 DATABASE MIGRATIONS")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # Migration 005: shopee_account_assignments
        print("[1/3] Creating shopee_account_assignments table...")
        
        # Create table
        try:
            db.execute(text("""
                CREATE TABLE shopee_account_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shopee_account_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role_scope TEXT NOT NULL CHECK(role_scope IN ('owner', 'supervisor', 'partner', 'leader', 'host', 'viewer')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (shopee_account_id) REFERENCES shopee_accounts(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, shopee_account_id)
                )
            """))
            db.commit()
            print("  ✅ Table created")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print("  ⚠️  Table already exists (OK)")
            else:
                raise
        
        # Create indexes
        print("[2/3] Creating indexes...")
        try:
            db.execute(text("CREATE INDEX idx_assignments_user ON shopee_account_assignments(user_id)"))
            db.commit()
            print("  ✅ user_id index created")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print("  ⚠️  Index already exists (OK)")
        
        try:
            db.execute(text("CREATE INDEX idx_assignments_account ON shopee_account_assignments(shopee_account_id)"))
            db.commit()
            print("  ✅ shopee_account_id index created")
        except Exception as e:
            if 'already exists' in str(e).lower():
                print("  ⚠️  Index already exists (OK)")
        
        # Migration 006: Update shopee_accounts
        print("[3/3] Adding last_synced_at to shopee_accounts...")
        try:
            db.execute(text("ALTER TABLE shopee_accounts ADD COLUMN last_synced_at TIMESTAMP"))
            db.commit()
            print("  ✅ Column added")
        except Exception as e:
            if 'duplicate column' in str(e).lower():
                print("  ⚠️  Column already exists (OK)")
            else:
                print(f"  ⚠️  Warning: {e}")
        
        # Verify
        print()
        print("Verifying migrations...")
        
        # Check assignments table
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='shopee_account_assignments'"))
        if result.fetchone():
            print("✅ shopee_account_assignments table exists")
        else:
            print("❌ shopee_account_assignments table NOT found")
            return False
        
        # Check last_synced_at column
        result = db.execute(text("PRAGMA table_info(shopee_accounts)"))
        columns = [row[1] for row in result.fetchall()]
        if 'last_synced_at' in columns:
            print("✅ last_synced_at column exists")
        else:
            print("❌ last_synced_at column NOT found")
            return False
        
        print()
        print("=" * 60)
        print(" MIGRATIONS COMPLETE!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = run_phase2_migrations()
    exit(0 if success else 1)
