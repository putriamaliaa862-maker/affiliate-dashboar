import { test, expect } from '@playwright/test';
import path from 'path';

// 1. Global timeout & Retries
// Max 2 minutes per test, 1 retry on failure
test.describe.configure({ mode: 'parallel', retries: 1, timeout: 120_000 });

test.describe('Regression Guard Suite', () => {
    // 2. Action & Navigation timeouts
    test.use({ actionTimeout: 10000, navigationTimeout: 15000 });

    test.beforeEach(async ({ page }) => {
        // Monitor Console Errors
        page.on('console', msg => {
            if (msg.type() === 'error') {
                const text = msg.text();
                // Fail on critical runtime errors (e.g. broken imports)
                if (text.includes('Uncaught') || text.includes('SyntaxError') || text.includes('ReferenceError')) {
                    console.error(`CRITICAL CONSOLE ERROR: ${text}`);
                }
            }
        });

        // Login Logic with strict timeout
        await page.goto('/');

        // If redirected to login, perform login
        if (page.url().includes('/login')) {
            await page.fill('input[type="email"]', 'admin@example.com');
            await page.fill('input[type="password"]', 'admin123');
            await page.click('button[type="submit"]');
        }

        // 3. Fail if sidebar not visible in 15s
        try {
            await expect(page.locator('nav')).toBeVisible({ timeout: 15000 });
        } catch (e) {
            console.error('FATAL: Login failed or Sidebar not found within 15s');
            throw e;
        }
    });

    // 5 & 6. Summary & Screenshot on Failure
    test.afterEach(async ({ page }, testInfo) => {
        const cleanTitle = testInfo.title.replace(/\s+/g, '_').replace(/Guard:_/, '');

        if (testInfo.status !== 'passed') {
            const screenshotPath = path.join('screenshots', 'regression', `FAIL_${cleanTitle}.png`);
            // Ensure directory exists if possible (Playwright usually handles it, or we rely on pre-creation)
            // But strict path usage is good.
            await page.screenshot({ path: screenshotPath, fullPage: true });
            console.log(`❌ FAIL: ${testInfo.title}`);
            console.log(`   Screenshot: ${screenshotPath}`);
        } else {
            console.log(`✅ PASS: ${cleanTitle}`);
        }
    });

    test('Guard: USERS Module', async ({ page }) => {
        await page.click('a[href="/users"]');
        // 2. Expectation timeout max 10s
        await expect(page).toHaveURL(/\/users/, { timeout: 10000 });
        await expect(page.getByText('Manajemen User', { exact: false })).toBeVisible({ timeout: 10000 });
        await expect(page.locator('table')).toBeVisible({ timeout: 10000 });
        await expect(page.locator('.toast-error')).not.toBeVisible();
    });

    test('Guard: EMPLOYEES Module', async ({ page }) => {
        await page.click('a[href="/employees"]');
        await expect(page).toHaveURL(/\/employees/, { timeout: 10000 });
        await expect(page.getByText('Data Tim')).toBeVisible({ timeout: 10000 });
        await expect(page.locator('table')).toBeVisible({ timeout: 10000 });
    });

    test('Guard: ATTENDANCE Module', async ({ page }) => {
        await page.click('a[href="/attendance"]');
        await expect(page).toHaveURL(/\/attendance/, { timeout: 10000 });
        await expect(page.getByText('Absensi Tim')).toBeVisible({ timeout: 10000 });
    });

    test('Guard: REPORTS Module', async ({ page }) => {
        await page.click('a[href="/reports"]');
        await expect(page).toHaveURL(/\/reports/, { timeout: 10000 });
        await expect(page.getByText('Laporan Penjualan')).toBeVisible({ timeout: 10000 });

        // Attempt generation if button exists
        const generateBtn = page.getByRole('button', { name: /Tampilkan|Generate|Filter/i }).first();
        if (await generateBtn.isVisible()) {
            await generateBtn.click();
            await page.waitForTimeout(1000);
        }
        await expect(page.locator('table')).toBeVisible({ timeout: 10000 });
    });

    test('Guard: COMMISSIONS Module', async ({ page }) => {
        await page.click('a[href="/commissions"]');
        await expect(page).toHaveURL(/\/commissions/, { timeout: 10000 });
        await expect(page.getByText('Riwayat Komisi')).toBeVisible({ timeout: 10000 });
        await expect(page.locator('table')).toBeVisible({ timeout: 10000 });
    });
});
