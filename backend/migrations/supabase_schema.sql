-- ============================================
-- SUPABASE SCHEMA MIGRATION
-- Export schema untuk import ke Supabase
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- CORE TABLES
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
    shopee_account_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shopee_accounts_studio_id ON shopee_accounts(studio_id);
CREATE INDEX IF NOT EXISTS idx_shopee_accounts_account_id ON shopee_accounts(account_id);

-- Shopee Account Assignments (Phase 2)
CREATE TABLE IF NOT EXISTS shopee_account_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
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
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
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
    ip_address VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);

-- ============================================
-- LIVE STREAMING TABLES
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

-- Live Product Snapshots
CREATE TABLE IF NOT EXISTS live_product_snapshots (
    id SERIAL PRIMARY KEY,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    item_id VARCHAR(255) NOT NULL,
    item_name VARCHAR(255),
    price NUMERIC(10, 2),
    quantity_sold INTEGER DEFAULT 0,
    commission_rate FLOAT,
    total_commission NUMERIC(10, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(shopee_account_id, snapshot_date, item_id)
);

CREATE INDEX IF NOT EXISTS idx_live_product_snapshots_account_id ON live_product_snapshots(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_live_product_snapshots_date ON live_product_snapshots(snapshot_date);

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

-- ============================================
-- REALTIME SNAPSHOTS (Bot)
-- ============================================

CREATE TABLE IF NOT EXISTS realtime_snapshots (
    id SERIAL PRIMARY KEY,
    shopee_account_id INTEGER NOT NULL REFERENCES shopee_accounts(id) ON DELETE CASCADE,
    snapshot_type VARCHAR(50) NOT NULL,
    snapshot_data JSONB NOT NULL,
    captured_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_account_id ON realtime_snapshots(shopee_account_id);
CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_type ON realtime_snapshots(snapshot_type);
CREATE INDEX IF NOT EXISTS idx_realtime_snapshots_captured_at ON realtime_snapshots(captured_at);

-- ============================================
-- STAGING TABLE FOR EXTENSION
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
-- TRIGGERS FOR UPDATED_AT
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
CREATE TRIGGER update_live_sessions_updated_at BEFORE UPDATE ON live_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();