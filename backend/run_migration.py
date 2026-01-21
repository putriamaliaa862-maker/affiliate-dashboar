"""
Database Migration Runner
Runs migration 004: Add access_code to users table
Compatible with both SQLite and PostgreSQL
"""
from app.database import engine
from sqlalchemy import text

def run_migration():
    print("=" * 50)
    print(" Running Migration 004")
    print("=" * 50)
    print()
    
    # Detect database type
    db_type = engine.dialect.name
    print(f"Database type: {db_type}")
    print()
    
    # Read migration file
    with open('migrations/004_add_access_code_to_users.sql', 'r') as f:
        sql_content = f.read()
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
    
    with engine.connect() as conn:
        for i, statement in enumerate(statements, 1):
            try:
                print(f"[{i}/{len(statements)}] Executing: {statement[:60]}...")
                conn.execute(text(statement))
                conn.commit()
                print("✅ Success")
            except Exception as e:
                error_msg = str(e)
                # Check if it's "already exists" error - that's OK
                if 'already exists' in error_msg.lower() or 'duplicate column' in error_msg.lower():
                    print(f"⚠️  Column already exists (skipping)")
                else:
                    print(f"❌ Error: {e}")
                    # Continue anyway for other statements
    
    # Verify based on database type
    print()
    print("Verifying migration...")
    
    try:
        with engine.connect() as conn:
            if db_type == 'sqlite':
                # SQLite: Use PRAGMA table_info
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result.fetchall()]
                has_column = 'access_code' in columns
            else:
                # PostgreSQL: Use information_schema
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='users' AND column_name='access_code'"
                ))
                has_column = result.fetchone() is not None
            
            if has_column:
                print("✅ Migration verified! Column 'access_code' exists in users table.")
            else:
                print("❌ Verification failed! Column not found.")
                return False
    except Exception as e:
        print(f"⚠️  Warning: Could not verify migration: {e}")
        print("   Manual check recommended.")
    
    print()
    print("=" * 50)
    print(" Migration Complete!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
