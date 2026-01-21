-- Migration 005: Create shopee_account_assignments table
-- Purpose: Many-to-many relationship between users and shopee accounts
-- Date: 2026-01-18

CREATE TABLE IF NOT EXISTS shopee_account_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shopee_account_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role_scope TEXT NOT NULL CHECK(role_scope IN ('owner', 'supervisor', 'partner', 'leader', 'host', 'viewer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (shopee_account_id) REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, shopee_account_id)
);

CREATE INDEX IF NOT EXISTS idx_assignments_user ON shopee_account_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_account ON shopee_account_assignments(shopee_account_id);
