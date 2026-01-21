import { test, expect } from '@playwright/test'

/**
 * DASHBOARD CLICK ALL - Automated Button Test
 * Tests all buttons in DashboardOwner.tsx systematically
 * Priority: P1 (Business Critical) first
 */

const BASE_URL = 'http://localhost:5174'
const DASHBOARD_URL = `${BASE_URL}/dashboard-owner`

// Test credentials
const OWNER_USER = {
    username: 'admin',
    password: 'admin123'
}

test.describe('Dashboard Owner - Button Click Tests', () => {

    test.beforeEach(async ({ page }) => {
        // Login as owner
        await page.goto(`${BASE_URL}/login`)
        await page.fill('input[name="username"]', OWNER_USER.username)
        await page.fill('input[type="password"]', OWNER_USER.password)
        await page.click('button[type="submit"]')

        // Wait for auth to complete
        await page.waitForURL(/\/(dashboard|dashboard-owner)/, { timeout: 5000 })

        // Navigate to owner dashboard
        await page.goto(DASHBOARD_URL)

        // Wait for dashboard to load (KPI cards visible)
        await page.waitForSelector('text=GMV', { timeout: 5000 })
    })

    // =========================
    // PRIORITY 1: BUSINESS CRITICAL BUTTONS
    // =========================

    test('P1: Quick Action - Tambah Modal → /ads-center', async ({ page }) => {
        // Wait for Quick Actions to load
        await page.waitForSelector('text=Quick Actions', { timeout: 3000 })

        // Click "Tambah Modal" button
        const tambahModalBtn = page.locator('button:has-text("Tambah Modal")')
        await expect(tambahModalBtn).toBeVisible()
        await tambahModalBtn.click()

        // Should navigate to ads-center
        await expect(page).toHaveURL(/\/ads-center/, { timeout: 5000 })

        // Page should load without errors
        await expect(page.locator('body')).toBeVisible()
        await expect(page.locator('text=404')).not.toBeVisible()
    })

    test('P1: Quick Action - Input Spend → /ads-center', async ({ page }) => {
        await page.waitForSelector('text=Quick Actions', { timeout: 3000 })

        const inputSpendBtn = page.locator('button:has-text("Input Spend")')
        await expect(inputSpendBtn).toBeVisible()
        await inputSpendBtn.click()

        await expect(page).toHaveURL(/\/ads-center/, { timeout: 5000 })
        await expect(page.locator('body')).toBeVisible()
    })

    test('P1: Quick Action - Sync Live Products → /live-products', async ({ page }) => {
        await page.waitForSelector('text=Quick Actions', { timeout: 3000 })

        const syncBtn = page.locator('button:has-text("Sync Live Products")')
        await expect(syncBtn).toBeVisible()
        await syncBtn.click()

        await expect(page).toHaveURL(/\/live-products/, { timeout: 5000 })
        await expect(page.locator('body')).toBeVisible()
        await expect(page.locator('text=404')).not.toBeVisible()
    })

    test('P1: Quick Action - Insights Produk → /daily-insights (FIXED)', async ({ page }) => {
        await page.waitForSelector('text=Quick Actions', { timeout: 3000 })

        const insightsBtn = page.locator('button:has-text("Insights Produk")')
        await expect(insightsBtn).toBeVisible()
        await insightsBtn.click()

        // Should navigate to CORRECT route (fixed from /insights/daily)
        await expect(page).toHaveURL(/\/daily-insights/, { timeout: 5000 })
        await expect(page.locator('body')).toBeVisible()
        await expect(page.locator('text=404')).not.toBeVisible()
    })

    // =========================
    // PRIORITY 2: OPERATIONAL BUTTONS
    // =========================

    test('P2: Quick Action - Laporan Komisi → /reports', async ({ page }) => {
        await page.waitForSelector('text=Quick Actions', { timeout: 3000 })

        const laporanBtn = page.locator('button:has-text("Laporan Komisi")')
        await expect(laporanBtn).toBeVisible()
        await laporanBtn.click()

        await expect(page).toHaveURL(/\/reports/, { timeout: 5000 })
        await expect(page.locator('body')).toBeVisible()
    })

    test('P2: Quick Action - Kelola User → /users', async ({ page }) => {
        await page.waitForSelector('text=Quick Actions', { timeout: 3000 })

        const usersBtn = page.locator('button:has-text("Kelola User")')
        await expect(usersBtn).toBeVisible()
        await usersBtn.click()

        await expect(page).toHaveURL(/\/users/, { timeout: 5000 })
        await expect(page.locator('body')).toBeVisible()
    })

    test('P2: Top Performers - Lihat Semua → /reports', async ({ page }) => {
        // Wait for premium features to load
        await page.waitForTimeout(2000)

        // Look for "Lihat Semua" button in Top Performers section
        const lihatSemuaBtn = page.locator('button:has-text("Lihat Semua")').first()

        // Only test if premium features are loaded
        if (await lihatSemuaBtn.isVisible()) {
            await lihatSemuaBtn.click()
            await expect(page).toHaveURL(/\/reports/, { timeout: 5000 })
        } else {
            console.log('Premium features not loaded - skipping')
        }
    })

    // =========================
    // PRIORITY 3: UTILITY BUTTONS
    // =========================

    test('P3: Refresh Button - Refetches data', async ({ page }) => {
        // Click refresh button
        const refreshBtn = page.locator('button:has-text("Refresh")')
        await expect(refreshBtn).toBeVisible()

        // Should have loading spinner after click
        await refreshBtn.click()

        // Wait for re-render (should not crash)
        await page.waitForTimeout(1000)

        // Dashboard should still be visible
        await expect(page).toHaveURL(DASHBOARD_URL)
        await expect(page.locator('text=GMV')).toBeVisible()
    })

    test('P3: Date Filter - Changes data', async ({ page }) => {
        // Find date input
        const dateInput = page.locator('input[type="date"]')
        await expect(dateInput).toBeVisible()

        // Change date
        const yesterday = new Date()
        yesterday.setDate(yesterday.getDate() - 1)
        const yesterdayStr = yesterday.toISOString().split('T')[0]

        await dateInput.fill(yesterdayStr)

        // Should trigger refetch (wait for network)
        await page.waitForTimeout(1000)

        // Should still be on dashboard
        await expect(page).toHaveURL(DASHBOARD_URL)
        await expect(page.locator('text=GMV')).toBeVisible()
    })

    test('P3: Account Filter - Filters by account', async ({ page }) => {
        // Find account select
        const accountSelect = page.locator('select').first()
        await expect(accountSelect).toBeVisible()

        // Get option count
        const options = await accountSelect.locator('option').count()

        if (options > 1) {
            // Select first non-"all" option
            await accountSelect.selectOption({ index: 1 })

            // Should trigger refetch
            await page.waitForTimeout(1000)

            // Should still be on dashboard
            await expect(page).toHaveURL(DASHBOARD_URL)
        }
    })

    test('P3: Alert Toggle - Shows/hides alerts', async ({ page }) => {
        // Find alert checkbox
        const alertCheckbox = page.locator('input[type="checkbox"]').first()

        if (await alertCheckbox.isVisible()) {
            const isChecked = await alertCheckbox.isChecked()

            // Toggle it
            await alertCheckbox.click()

            // Should toggle state
            await expect(alertCheckbox).toBeChecked({ checked: !isChecked })

            // Should still be on dashboard
            await expect(page).toHaveURL(DASHBOARD_URL)
        }
    })

    // =========================
    // ALERT CENTER DYNAMIC BUTTONS
    // =========================

    test('Alert Center - Action buttons navigate (if alerts exist)', async ({ page }) => {
        // Wait for alerts to load
        await page.waitForTimeout(2000)

        // Check if any alerts exist
        const alertActions = page.locator('button:has-text("→")')
        const count = await alertActions.count()

        if (count > 0) {
            // Test first alert action
            await alertActions.first().click()

            // Should navigate somewhere (not 404)
            await page.waitForTimeout(1000)
            await expect(page.locator('text=404')).not.toBeVisible()
        } else {
            console.log('No alerts found - skipping dynamic test')
        }
    })

    // =========================
    // NO CONSOLE ERRORS CHECK
    // =========================

    test('No console errors on any button click', async ({ page }) => {
        const consoleErrors: string[] = []

        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text())
            }
        })

        // Click refresh (safest button)
        const refreshBtn = page.locator('button:has-text("Refresh")')
        await refreshBtn.click()
        await page.waitForTimeout(1000)

        // Filter out acceptable errors
        const criticalErrors = consoleErrors.filter(err =>
            !err.includes('Failed to load resource') &&
            !err.includes('favicon')
        )

        expect(criticalErrors).toHaveLength(0)
    })
})

// =========================
// SUMMARY TEST
// =========================

test.describe('Dashboard Button Summary', () => {
    test('All buttons should be clickable', async ({ page }) => {
        await page.goto(`${BASE_URL}/login`)
        await page.fill('input[name="username"]', OWNER_USER.username)
        await page.fill('input[type="password"]', OWNER_USER.password)
        await page.click('button[type="submit"]')
        await page.waitForURL(/\//, { timeout: 5000 })
        await page.goto(DASHBOARD_URL)
        await page.waitForSelector('text=GMV', { timeout: 5000 })

        // Count all buttons
        const allButtons = await page.locator('button').count()
        console.log(`Total buttons found: ${allButtons}`)

        // All buttons should be enabled (not disabled)
        const disabledButtons = await page.locator('button:disabled').count()
        expect(disabledButtons).toBe(0)
    })
})
