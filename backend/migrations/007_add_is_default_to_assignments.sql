-- Migration: Add is_default to shopee_account_assignments
-- Date: 2026-01-18

-- Add is_default column
ALTER TABLE shopee_account_assignments ADD COLUMN is_default BOOLEAN NOT NULL DEFAULT 0;

-- Create index for faster default account lookups
CREATE INDEX IF NOT EXISTS idx_account_assignments_default 
ON shopee_account_assignments(user_id, is_default) 
WHERE is_default = 1;

-- Set first assignment as default for users who already have assignments
UPDATE shopee_account_assignments
SET is_default = 1
WHERE id IN (
    SELECT MIN(id)
    FROM shopee_account_assignments
    GROUP BY user_id
);
