-- 1. Table: ads_daily_spend
CREATE TABLE IF NOT EXISTS ads_daily_spend (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id),
    spend_amount INTEGER NOT NULL DEFAULT 0,
    spend_type VARCHAR(50) DEFAULT 'general', -- 'audience', 'live', 'general'
    note TEXT,
    created_by_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(date, shopee_account_id, spend_type)
);

-- 2. Table: ads_daily_metrics
CREATE TABLE IF NOT EXISTS ads_daily_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id),
    roas_manual FLOAT,
    revenue_manual INTEGER,
    note TEXT,
    created_by_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(date, shopee_account_id)
);

-- 3. Table: audience_budget_settings
CREATE TABLE IF NOT EXISTS audience_budget_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id),
    min_remaining_threshold INTEGER DEFAULT 3000,
    min_gap_minutes INTEGER DEFAULT 10,
    active_start_time TIME DEFAULT '05:00:00',
    active_end_time TIME DEFAULT '00:00:00',
    max_daily_add_budget INTEGER,
    is_enabled BOOLEAN DEFAULT TRUE,
    updated_by_user_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(shopee_account_id)
);

-- 4. Table: audience_budget_actions
CREATE TABLE IF NOT EXISTS audience_budget_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id),
    remaining_before INTEGER,
    added_amount INTEGER NOT NULL,
    remaining_after INTEGER,
    trigger_reason VARCHAR(50) DEFAULT 'threshold', -- 'threshold', 'manual'
    created_by_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audience_actions_date_account ON audience_budget_actions(date, shopee_account_id);

-- Seed default settings for existing accounts
INSERT INTO audience_budget_settings (shopee_account_id)
SELECT id FROM shopee_accounts
WHERE id NOT IN (SELECT shopee_account_id FROM audience_budget_settings);
