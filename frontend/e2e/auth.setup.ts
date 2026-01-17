import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
    console.log('Navigating to login...');
    await page.goto('/login');

    // Wait for form to be ready
    console.log('Waiting for login form...');
    await page.waitForSelector('form', { state: 'visible', timeout: 30000 });
    await page.waitForLoadState('networkidle');

    // Fill login form
    console.log('Filling credentials...');
    await page.fill('input[name="username"]', 'test_super');
    await page.fill('input[name="password"]', 'password123');

    // Submit
    console.log('Clicking submit...');
    await page.click('button[type="submit"]');

    // Wait for navigation
    console.log('Waiting for dashboard...');
    // We wait for the URL to likely verify we moved away from /login or got a token
    // And check for a dashboard-specific element
    await expect(page.locator('h1')).toBeVisible({ timeout: 60000 });

    console.log('Login successful, saving state...');
    await page.context().storageState({ path: authFile });
});
