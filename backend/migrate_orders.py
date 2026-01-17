"""
Migration script to add payout columns to orders table
"""
import sys
import sqlite3
import os

DB_PATH = "c:/workspace/affiliate-dashboard/backend/affiliate.db"

def migrate_orders_table():
    print(f"Migrating database at {DB_PATH}...")
    
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
            ("payout_status", "TEXT DEFAULT 'pending'"),
            ("payment_method", "TEXT"),
            ("validated_at", "DATETIME"),
            ("paid_at", "DATETIME")
        ]
        
        for col_name, col_def in new_columns:
            if col_name not in columns:
                print(f"Adding column '{col_name}'...")
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def}")
            else:
                print(f"Column '{col_name}' already exists.")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_orders_table()
