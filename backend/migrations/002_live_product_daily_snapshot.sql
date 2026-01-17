-- Migration 002: Live Product Daily Snapshot
-- Safe upgrade: Adds columns to existing tables if they exist, or creates new tables
-- Date: 2026-01-17

-- ============================================================
-- TABLE: live_product_daily_snapshots
-- ============================================================

-- Create table if not exists (safe for first run)
CREATE TABLE IF NOT EXISTS live_product_daily_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    account_id INTEGER NOT NULL,
    studio_id INTEGER,
    leader_id INTEGER,
    host_id INTEGER,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    sold_qty INTEGER DEFAULT 0,
    gmv NUMERIC(15,2) DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    source TEXT DEFAULT 'live',
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT unique_snapshot_product UNIQUE (snapshot_date, account_id, product_id)
);

-- Add indexes if not exist
CREATE INDEX IF NOT EXISTS idx_live_snapshots_date ON live_product_daily_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_live_snapshots_account ON live_product_daily_snapshots(account_id);
CREATE INDEX IF NOT EXISTS idx_live_snapshots_studio ON live_product_daily_snapshots(studio_id);
CREATE INDEX IF NOT EXISTS idx_live_snapshots_leader ON live_product_daily_snapshots(leader_id);
CREATE INDEX IF NOT EXISTS idx_live_snapshots_host ON live_product_daily_snapshots(host_id);
CREATE INDEX IF NOT EXISTS idx_live_snapshots_product ON live_product_daily_snapshots(product_id);

-- Safe ALTER TABLE: Add columns if table already exists from previous implementation
-- These will only execute if columns don't exist
DO $$ 
BEGIN
    -- Add sold_qty if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_product_daily_snapshots' AND column_name='sold_qty') THEN
        ALTER TABLE live_product_daily_snapshots ADD COLUMN sold_qty INTEGER DEFAULT 0;
    END IF;
    
    -- Add gmv if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_product_daily_snapshots' AND column_name='gmv') THEN
        ALTER TABLE live_product_daily_snapshots ADD COLUMN gmv NUMERIC(15,2) DEFAULT 0;
    END IF;
    
    -- Add clicks if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_product_daily_snapshots' AND column_name='clicks') THEN
        ALTER TABLE live_product_daily_snapshots ADD COLUMN clicks INTEGER DEFAULT 0;
    END IF;
    
    -- Add source if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_product_daily_snapshots' AND column_name='source') THEN
        ALTER TABLE live_product_daily_snapshots ADD COLUMN source TEXT DEFAULT 'live';
    END IF;
    
    -- Add raw_data if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_product_daily_snapshots' AND column_name='raw_data') THEN
        ALTER TABLE live_product_daily_snapshots ADD COLUMN raw_data JSONB;
    END IF;
    
    -- Add studio_id if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_product_daily_snapshots' AND column_name='studio_id') THEN
        ALTER TABLE live_product_daily_snapshots ADD COLUMN studio_id INTEGER;
    END IF;
    
    -- Add leader_id if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_product_daily_snapshots' AND column_name='leader_id') THEN
        ALTER TABLE live_product_daily_snapshots ADD COLUMN leader_id INTEGER;
    END IF;
    
    -- Add host_id if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_product_daily_snapshots' AND column_name='host_id') THEN
        ALTER TABLE live_product_daily_snapshots ADD COLUMN host_id INTEGER;
    END IF;
END $$;

-- ============================================================
-- TABLE: live_sync_logs
-- ============================================================

CREATE TABLE IF NOT EXISTS live_sync_logs (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    synced_at TIMESTAMP DEFAULT NOW(),
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'FAIL')),
    total_rows INTEGER DEFAULT 0,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_live_sync_logs_account ON live_sync_logs(account_id);
CREATE INDEX IF NOT EXISTS idx_live_sync_logs_date ON live_sync_logs(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_live_sync_logs_synced_at ON live_sync_logs(synced_at DESC);

-- Safe ALTER TABLE for live_sync_logs (in case old structure exists)
DO $$ 
BEGIN
    -- Ensure snapshot_date column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_sync_logs' AND column_name='snapshot_date') THEN
        ALTER TABLE live_sync_logs ADD COLUMN snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE;
    END IF;
    
    -- Ensure total_rows exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_sync_logs' AND column_name='total_rows') THEN
        ALTER TABLE live_sync_logs ADD COLUMN total_rows INTEGER DEFAULT 0;
    END IF;
    
    -- Ensure message column exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='live_sync_logs' AND column_name='message') THEN
        ALTER TABLE live_sync_logs ADD COLUMN message TEXT;
    END IF;
END $$;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Check tables exist
SELECT 
    table_name, 
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_name IN ('live_product_daily_snapshots', 'live_sync_logs')
ORDER BY table_name;

-- Show columns for verification
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'live_product_daily_snapshots'
ORDER BY ordinal_position;
