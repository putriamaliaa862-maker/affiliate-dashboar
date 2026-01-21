-- ============================================
-- SUPABASE COMPLETE SETUP SCRIPT
-- ============================================
-- File ini berisi SEMUA yang perlu di-setup di Supabase:
-- 1. Schema (semua tables)
-- 2. Indexes
-- 3. Triggers
-- 4. RLS Policies
-- 
-- CARA PAKAI:
-- 1. Buka Supabase Dashboard
-- 2. SQL Editor → New Query
-- 3. Copy-paste SEMUA isi file ini
-- 4. Click "Run"
-- 5. Done! ✅
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- PART 1: CORE TABLES
-- ============================================

-- Studios
CREATE TABLE IF NOT EXISTS studios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description VARCHAR(1000),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),
    access_code VARCHAR(64) UNIQUE,
    role VARCHAR(20) NOT NULL,
    leader_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_access_code ON users(access_code);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Employees
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    studio_id INTEGER NOT NULL REFERENCES studios(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_employees_studio_id ON employees(studio_id);

-- Attendance
CREATE TABLE IF NOT EXISTS attendances (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    check_in TIMESTAMPTZ,
    check_out TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'present',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(employee_id, date)
);

CREATE INDEX IF NOT EXISTS idx_attendances_employee_id ON attendances(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendances_date ON attendances(date);

-- Shopee Accounts
CREATE TABLE IF NOT EXISTS shopee_accounts (
    id SERIAL PRIMARY KEY,
    studio_id INTEGER NOT NULL REFERENCES studios(id) ON DELETE CASCADE,
    account_name VARCHAR(255) NOT NULL,
    account_id VARCHAR(255),
    shopee_account_id VARCHAR(255) UNIQUE,
    access_token TEXT,
    refresh_token TEXT,
    token_expire_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shopee_accounts_studio_id ON shopee_accounts(studio_id);
CREATE INDEX IF NOT EXISTS idx_shopee_accounts_account_id ON shopee_accounts(account_id);
CREATE INDEX IF NOT EXISTS idx_shopee_accounts_shopee_account_id ON shopee_accounts(shopee_account_id);

-- Shopee Account Assignments
CREATE TABLE IF NOT EXISTS shopee_account_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    role_scope VARCHAR(20) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, shopee_account_id)
);

CREATE INDEX IF NOT EXISTS idx_assignments_user_id ON shopee_account_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_assignments_account_id ON shopee_account_assignments(shopee_account_id);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    order_id VARCHAR(255) UNIQUE NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    commission_amount NUMERIC(12, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'completed',
    date TIMESTAMPTZ NOT NULL,
    payout_status VARCHAR(50) DEFAULT 'pending',
    payment_method VARCHAR(50),
    validated_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    product_name VARCHAR(255),
    product_id VARCHAR(100),
    handler_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_account_id ON orders(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    campaign_name VARCHAR(255) NOT NULL,
    campaign_id VARCHAR(255),
    budget NUMERIC(12, 2) DEFAULT 0,
    spent NUMERIC(12, 2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_campaigns_account_id ON campaigns(shopee_account_id);

-- Commission Rules
CREATE TABLE IF NOT EXISTS commission_rules (
    id SERIAL PRIMARY KEY,
    studio_id INTEGER NOT NULL REFERENCES studios(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    value NUMERIC(10, 2) NOT NULL,
    min_order_amount NUMERIC(12, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_commission_rules_studio_id ON commission_rules(studio_id);

-- Commissions
CREATE TABLE IF NOT EXISTS commissions (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    period VARCHAR(50) NOT NULL,
    total_amount NUMERIC(12, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'calculated',
    paid_date TIMESTAMPTZ,
    notes VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_commissions_employee_id ON commissions(employee_id);
CREATE INDEX IF NOT EXISTS idx_commissions_period ON commissions(period);

-- Reports
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    studio_id INTEGER NOT NULL REFERENCES studios(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    period VARCHAR(50) NOT NULL,
    total_revenue NUMERIC(12, 2) DEFAULT 0,
    total_commission NUMERIC(12, 2) DEFAULT 0,
    total_ad_spent NUMERIC(12, 2) DEFAULT 0,
    attendance_summary JSONB,
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_studio_id ON reports(studio_id);

-- Activity Logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    new_value JSONB,
    old_value JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);

-- ============================================
-- PART 2: LIVE STREAMING TABLES
-- ============================================

-- Live Sessions
CREATE TABLE IF NOT EXISTS live_sessions (
    id SERIAL PRIMARY KEY,
    studio_id INTEGER NOT NULL,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    session_name VARCHAR(255) NOT NULL,
    streamer_id VARCHAR(255),
    streamer_name VARCHAR(255),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration_minutes INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'ongoing',
    is_live BOOLEAN DEFAULT TRUE,
    total_viewers INTEGER DEFAULT 0,
    peak_viewers INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    total_revenue FLOAT DEFAULT 0.0,
    total_comments INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    products_count INTEGER DEFAULT 0,
    items_promoted JSONB DEFAULT '{}',
    campaign_id VARCHAR(255),
    campaign_name VARCHAR(255),
    campaign_budget FLOAT DEFAULT 0.0,
    campaign_spent FLOAT DEFAULT 0.0,
    coins_distributed INTEGER DEFAULT 0,
    coin_total_value FLOAT DEFAULT 0.0,
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    synced_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_live_sessions_account_id ON live_sessions(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_live_sessions_session_id ON live_sessions(session_id);

-- Live Session Items
CREATE TABLE IF NOT EXISTS live_session_items (
    id SERIAL PRIMARY KEY,
    live_session_id INTEGER NOT NULL REFERENCES live_sessions(id) ON DELETE CASCADE,
    item_id VARCHAR(255) NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    product_image_url VARCHAR(500),
    regular_price FLOAT,
    live_price FLOAT,
    discount_percentage FLOAT DEFAULT 0.0,
    quantity_sold INTEGER DEFAULT 0,
    total_sales_amount FLOAT DEFAULT 0.0,
    commission_per_item FLOAT DEFAULT 0.0,
    total_commission FLOAT DEFAULT 0.0,
    promotion_type VARCHAR(100),
    is_featured VARCHAR(50) DEFAULT 'false',
    promoted_at TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_session_items_session_id ON live_session_items(live_session_id);

-- Live Product Daily Snapshots
CREATE TABLE IF NOT EXISTS live_product_daily_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    studio_id INTEGER REFERENCES studios(id),
    leader_id INTEGER,
    host_id INTEGER,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    sold_qty INTEGER DEFAULT 0,
    gmv FLOAT DEFAULT 0.0,
    clicks INTEGER,
    source VARCHAR(50) DEFAULT 'live',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, snapshot_date, product_id)
);

CREATE INDEX IF NOT EXISTS idx_live_product_snapshots_account_id ON live_product_daily_snapshots(account_id);
CREATE INDEX IF NOT EXISTS idx_live_product_snapshots_date ON live_product_daily_snapshots(snapshot_date);

-- Live Sync Logs
CREATE TABLE IF NOT EXISTS live_sync_logs (
    id SERIAL PRIMARY KEY,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    sync_type VARCHAR(50) NOT NULL,
    sync_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'success',
    records_synced INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_sync_logs_account_id ON live_sync_logs(shopee_account_id);

-- Live Analytics
CREATE TABLE IF NOT EXISTS live_analytics (
    id SERIAL PRIMARY KEY,
    studio_id INTEGER NOT NULL,
    live_session_id VARCHAR(255) NOT NULL,
    date VARCHAR(10) NOT NULL,
    total_sessions_count INTEGER DEFAULT 0,
    average_viewers FLOAT DEFAULT 0.0,
    peak_viewers INTEGER DEFAULT 0,
    total_watch_time_minutes INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    total_revenue FLOAT DEFAULT 0.0,
    average_order_value FLOAT DEFAULT 0.0,
    conversion_rate FLOAT DEFAULT 0.0,
    total_comments INTEGER DEFAULT 0,
    average_comments_per_session FLOAT DEFAULT 0.0,
    total_likes INTEGER DEFAULT 0,
    total_shares INTEGER DEFAULT 0,
    unique_products_promoted INTEGER DEFAULT 0,
    top_product VARCHAR(500),
    total_ad_spend FLOAT DEFAULT 0.0,
    total_commission FLOAT DEFAULT 0.0,
    roi_percentage FLOAT DEFAULT 0.0,
    top_streamer VARCHAR(255),
    streamer_count INTEGER DEFAULT 0,
    detailed_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_analytics_studio_id ON live_analytics(studio_id);
CREATE INDEX IF NOT EXISTS idx_live_analytics_date ON live_analytics(date);

-- ============================================
-- PART 3: ADS TABLES
-- ============================================

-- Ads Daily Spend
CREATE TABLE IF NOT EXISTS ads_daily_spend (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    spend_amount INTEGER NOT NULL DEFAULT 0,
    spend_type VARCHAR(50) DEFAULT 'general',
    note TEXT,
    created_by_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, shopee_account_id, spend_type)
);

CREATE INDEX IF NOT EXISTS idx_ads_daily_spend_account_id ON ads_daily_spend(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_ads_daily_spend_date ON ads_daily_spend(date);

-- Ads Daily Metrics
CREATE TABLE IF NOT EXISTS ads_daily_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    roas_manual FLOAT,
    revenue_manual INTEGER,
    note TEXT,
    created_by_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, shopee_account_id)
);

CREATE INDEX IF NOT EXISTS idx_ads_daily_metrics_account_id ON ads_daily_metrics(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_ads_daily_metrics_date ON ads_daily_metrics(date);

-- Audience Budget Settings
CREATE TABLE IF NOT EXISTS audience_budget_settings (
    id SERIAL PRIMARY KEY,
    shopee_account_id INTEGER NOT NULL UNIQUE REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    min_remaining_threshold INTEGER DEFAULT 3000,
    min_gap_minutes INTEGER DEFAULT 10,
    active_start_time VARCHAR(20) DEFAULT '05:00:00',
    active_end_time VARCHAR(20) DEFAULT '00:00:00',
    max_daily_add_budget INTEGER,
    is_enabled BOOLEAN DEFAULT TRUE,
    updated_by_user_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audience_budget_settings_account_id ON audience_budget_settings(shopee_account_id);

-- Audience Budget Actions
CREATE TABLE IF NOT EXISTS audience_budget_actions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time VARCHAR(20) NOT NULL,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    remaining_before INTEGER,
    added_amount INTEGER NOT NULL,
    remaining_after INTEGER,
    trigger_reason VARCHAR(50) DEFAULT 'threshold',
    created_by_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audience_budget_actions_account_id ON audience_budget_actions(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_audience_budget_actions_date ON audience_budget_actions(date);

-- ============================================
-- PART 4: BONUS & SHIFT TABLES
-- ============================================

-- Shift Templates
CREATE TABLE IF NOT EXISTS shift_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    timezone VARCHAR(50) DEFAULT 'Asia/Jakarta',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bonus Rate Rules
CREATE TABLE IF NOT EXISTS bonus_rate_rules (
    id SERIAL PRIMARY KEY,
    shop_id INTEGER REFERENCES shopee_accounts(id),
    day_type VARCHAR(20) NOT NULL,
    shift_id INTEGER NOT NULL REFERENCES shift_templates(id) ON DELETE CASCADE,
    bonus_per_order INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shop_id, day_type, shift_id)
);

CREATE INDEX IF NOT EXISTS idx_bonus_rate_rules_shop_id ON bonus_rate_rules(shop_id);
CREATE INDEX IF NOT EXISTS idx_bonus_rate_rules_shift_id ON bonus_rate_rules(shift_id);

-- ============================================
-- PART 5: REALTIME SNAPSHOTS (Bot)
-- ============================================

CREATE TABLE IF NOT EXISTS realtime_snapshots (
    id SERIAL PRIMARY KEY,
    shopee_account_id VARCHAR(100) NOT NULL,
    shop_name VARCHAR(255),
    snapshot_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_account_id ON realtime_snapshots(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_type ON realtime_snapshots(snapshot_type);
CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_captured_at ON realtime_snapshots(scraped_at);

-- Bot Runs
CREATE TABLE IF NOT EXISTS bot_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    accounts_total INTEGER DEFAULT 0,
    accounts_processed INTEGER DEFAULT 0,
    accounts_success INTEGER DEFAULT 0,
    accounts_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_bot_runs_run_id ON bot_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_bot_runs_status ON bot_runs(status);

-- ============================================
-- PART 6: STAGING TABLE FOR EXTENSION
-- ============================================

CREATE TABLE IF NOT EXISTS shopee_data_sync (
    id BIGSERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    account_info JSONB,
    payload JSONB NOT NULL,
    access_code VARCHAR(64),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shopee_data_sync_access_code ON shopee_data_sync(access_code);
CREATE INDEX IF NOT EXISTS idx_shopee_data_sync_processed ON shopee_data_sync(processed);
CREATE INDEX IF NOT EXISTS idx_shopee_data_sync_created_at ON shopee_data_sync(created_at);

-- ============================================
-- PART 7: TRIGGERS FOR UPDATED_AT
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_studios_updated_at BEFORE UPDATE ON studios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_attendances_updated_at BEFORE UPDATE ON attendances FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_shopee_accounts_updated_at BEFORE UPDATE ON shopee_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_commission_rules_updated_at BEFORE UPDATE ON commission_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_commissions_updated_at BEFORE UPDATE ON commissions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_live_sessions_updated_at BEFORE UPDATE ON live_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_live_analytics_updated_at BEFORE UPDATE ON live_analytics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bonus_rate_rules_updated_at BEFORE UPDATE ON bonus_rate_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_shift_templates_updated_at BEFORE UPDATE ON shift_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_audience_budget_settings_updated_at BEFORE UPDATE ON audience_budget_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PART 8: ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS on critical tables
ALTER TABLE shopee_data_sync ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopee_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- SHOPEE_DATA_SYNC TABLE (Extension Staging)
-- Policy: Allow extension to INSERT with valid access_code
DROP POLICY IF EXISTS "extension_insert_policy" ON shopee_data_sync;
CREATE POLICY "extension_insert_policy" ON shopee_data_sync
    FOR INSERT
    WITH CHECK (
        access_code IS NOT NULL AND
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.access_code = shopee_data_sync.access_code
            AND users.is_active = TRUE
        )
    );

-- Policy: Allow service_role (backend) to SELECT all
DROP POLICY IF EXISTS "service_role_select_policy" ON shopee_data_sync;
CREATE POLICY "service_role_select_policy" ON shopee_data_sync
    FOR SELECT
    USING (auth.role() = 'service_role');

-- Policy: Allow service_role (backend) to UPDATE
DROP POLICY IF EXISTS "service_role_update_policy" ON shopee_data_sync;
CREATE POLICY "service_role_update_policy" ON shopee_data_sync
    FOR UPDATE
    USING (auth.role() = 'service_role');

-- Policy: Allow service_role (backend) to DELETE
DROP POLICY IF EXISTS "service_role_delete_policy" ON shopee_data_sync;
CREATE POLICY "service_role_delete_policy" ON shopee_data_sync
    FOR DELETE
    USING (auth.role() = 'service_role');

-- ORDERS TABLE
DROP POLICY IF EXISTS "service_role_orders_full_access" ON orders;
CREATE POLICY "service_role_orders_full_access" ON orders
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- SHOPEE_ACCOUNTS TABLE
DROP POLICY IF EXISTS "service_role_accounts_full_access" ON shopee_accounts;
CREATE POLICY "service_role_accounts_full_access" ON shopee_accounts
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- USERS TABLE
DROP POLICY IF EXISTS "service_role_users_full_access" ON users;
CREATE POLICY "service_role_users_full_access" ON users
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- ============================================
-- COMPLETE! ✅
-- ============================================
-- 
-- Semua tables, indexes, triggers, dan RLS policies sudah di-setup!
-- 
-- NEXT STEPS:
-- 1. Cek di Table Editor apakah semua tables terbuat
-- 2. Test extension post ke shopee_data_sync table
-- 3. Test backend connect ke Supabase
-- 
-- ============================================