-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Supabase Security Configuration
-- ============================================

-- Enable RLS on all tables
ALTER TABLE shopee_data_sync ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopee_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- ============================================
-- SHOPEE_DATA_SYNC TABLE (Extension Staging)
-- ============================================

-- Policy: Allow extension to INSERT with valid access_code
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
CREATE POLICY "service_role_select_policy" ON shopee_data_sync
    FOR SELECT
    USING (auth.role() = 'service_role');

-- Policy: Allow service_role (backend) to UPDATE
CREATE POLICY "service_role_update_policy" ON shopee_data_sync
    FOR UPDATE
    USING (auth.role() = 'service_role');

-- Policy: Allow service_role (backend) to DELETE
CREATE POLICY "service_role_delete_policy" ON shopee_data_sync
    FOR DELETE
    USING (auth.role() = 'service_role');

-- ============================================
-- ORDERS TABLE
-- ============================================

-- Policy: Allow service_role full access
CREATE POLICY "service_role_orders_full_access" ON orders
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- ============================================
-- SHOPEE_ACCOUNTS TABLE
-- ============================================

-- Policy: Allow service_role full access
CREATE POLICY "service_role_accounts_full_access" ON shopee_accounts
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- ============================================
-- USERS TABLE
-- ============================================

-- Policy: Allow service_role full access
CREATE POLICY "service_role_users_full_access" ON users
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- ============================================
-- NOTES
-- ============================================
-- 
-- 1. Extension akan menggunakan ANON key dengan access_code validation
-- 2. Backend akan menggunakan SERVICE_ROLE key (full access)
-- 3. RLS memastikan extension hanya bisa insert dengan access_code yang valid
-- 4. Backend bisa access semua data untuk business logic processing
-- 
-- IMPORTANT: 
-- - Jangan expose SERVICE_ROLE key di extension/frontend
-- - Hanya pakai ANON key di extension dengan RLS policies
-- - Backend harus pakai SERVICE_ROLE key untuk full access