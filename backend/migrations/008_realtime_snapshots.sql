-- Migration 008: Realtime Snapshots for 24H Playwright Bot
-- Created: 2026-01-18

-- Table for storing realtime scraped data from bot
CREATE TABLE IF NOT EXISTS realtime_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shopee_account_id VARCHAR(100) NOT NULL,
    shop_name VARCHAR(255),
    snapshot_type VARCHAR(50) NOT NULL,  -- creator_live, ads, coins, summary
    data JSON NOT NULL,
    scraped_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Index for fast queries
    CONSTRAINT check_snapshot_type CHECK (snapshot_type IN ('creator_live', 'ads', 'coins', 'summary'))
);

-- Index for querying by account and type
CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_account ON realtime_snapshots(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_type ON realtime_snapshots(snapshot_type);
CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_scraped_at ON realtime_snapshots(scraped_at DESC);

-- Table for tracking bot run status
CREATE TABLE IF NOT EXISTS bot_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id VARCHAR(36) NOT NULL UNIQUE,  -- UUID
    status VARCHAR(20) NOT NULL DEFAULT 'running',  -- running, completed, error
    accounts_total INTEGER DEFAULT 0,
    accounts_processed INTEGER DEFAULT 0,
    accounts_success INTEGER DEFAULT 0,
    accounts_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    
    CONSTRAINT check_bot_status CHECK (status IN ('running', 'completed', 'error', 'stopped'))
);

-- Index for querying latest runs
CREATE INDEX IF NOT EXISTS idx_bot_runs_started_at ON bot_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_bot_runs_status ON bot_runs(status);
