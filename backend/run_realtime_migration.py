"""
Migration script for realtime_snapshots table
Run: python run_realtime_migration.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'app', 'affiliate_dashboard.db')

def run_migration():
    print("=" * 50)
    print("RUNNING MIGRATION: 008_realtime_snapshots")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create realtime_snapshots table
        print("[1/4] Creating realtime_snapshots table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS realtime_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shopee_account_id VARCHAR(100) NOT NULL,
                shop_name VARCHAR(255),
                snapshot_type VARCHAR(50) NOT NULL,
                data JSON NOT NULL,
                scraped_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ realtime_snapshots created")
        
        # Create indexes
        print("[2/4] Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_account ON realtime_snapshots(shopee_account_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_type ON realtime_snapshots(snapshot_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_scraped_at ON realtime_snapshots(scraped_at DESC)")
        print("✅ Indexes created")
        
        # Create bot_runs table
        print("[3/4] Creating bot_runs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id VARCHAR(36) NOT NULL UNIQUE,
                status VARCHAR(20) NOT NULL DEFAULT 'running',
                accounts_total INTEGER DEFAULT 0,
                accounts_processed INTEGER DEFAULT 0,
                accounts_success INTEGER DEFAULT 0,
                accounts_failed INTEGER DEFAULT 0,
                error_message TEXT,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME
            )
        """)
        print("✅ bot_runs created")
        
        # Create indexes for bot_runs
        print("[4/4] Creating bot_runs indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_runs_started_at ON bot_runs(started_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_runs_status ON bot_runs(status)")
        print("✅ bot_runs indexes created")
        
        conn.commit()
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('realtime_snapshots', 'bot_runs')")
        tables = cursor.fetchall()
        print("=" * 50)
        print(f"✅ MIGRATION COMPLETE - {len(tables)} tables created")
        print("Tables:", [t[0] for t in tables])
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
