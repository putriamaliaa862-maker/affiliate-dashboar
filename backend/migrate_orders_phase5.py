"""
Migration script to add product and handler columns to orders table (Phase 5)
"""
import sys
import sqlite3
import os

DB_PATH = "c:/workspace/affiliate-dashboard/backend/affiliate.db"

def migrate_orders_phase5():
    print(f"Migrating database (Phase 5) at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(orders)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Add new columns if missing
        new_columns = [
            ("product_name", "TEXT"),
            ("product_id", "TEXT"),
            ("handler_user_id", "INTEGER REFERENCES users(id)")
        ]
        
        for col_name, col_def in new_columns:
            if col_name not in columns:
                print(f"Adding column '{col_name}'...")
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def}")
            else:
                print(f"Column '{col_name}' already exists.")
        
        conn.commit()
        print("✅ Phase 5 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_orders_phase5()
