-- Migration 006: Update shopee_accounts table
-- Purpose: Add last_synced_at for extension sync tracking
-- Date: 2026-01-18

-- Add last_synced_at column (safe - nullable)
ALTER TABLE shopee_accounts ADD COLUMN last_synced_at TIMESTAMP;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_shopee_accounts_last_synced ON shopee_accounts(last_synced_at);
