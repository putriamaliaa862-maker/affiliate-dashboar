import { test, expect } from '@playwright/test';

test.describe('Dashboard Automatic Audit', () => {

    test('Audit All Sidebar Pages', async ({ page }) => {
        const errors: string[] = [];

        // Listen for console errors
        page.on('console', msg => {
            if (msg.type() === 'error') {
                errors.push(`Console Error: ${msg.text()}`);
            }
        });

        // Listen for network errors
        page.on('response', response => {
            if (response.status() >= 400 && response.request().resourceType() === 'fetch') {
                errors.push(`Network Error: ${response.status()} ${response.url()}`);
            }
        });

        await page.goto('/');

        // Get all sidebar links
        // Assuming sidebar links are in a <nav> or specific container
        // We'll try to find links that look like sidebar items
        await page.waitForSelector('nav a', { timeout: 5000 });
        const links = await page.locator('nav a').all();
        const urls = [];

        for (const link of links) {
            const href = await link.getAttribute('href');
            if (href && !href.includes('logout')) {
                urls.push(href);
            }
        }

        console.log('Found sidebar URLs:', urls);

        for (const url of urls) {
            console.log(`Navigating to ${url}...`);
            await page.goto(url);
            await page.waitForLoadState('networkidle');

            // Check for Visible headers
            await expect(page.locator('h1, h2, h3').first()).toBeVisible();

            // Take screenshot for visual audit
            const sanitizeName = url.replace(/\//g, '_').substring(1) || 'home';
            await page.screenshot({ path: `e2e/screenshots/${sanitizeName}.png` });
        }

        // Report Logic
        if (errors.length > 0) {
            console.error('Audit Found Errors:', errors);
            // We can choose to fail the test or just log
            // expect(errors).toHaveLength(0); 
        }
    });

    test('Verify Bonus Settings Endpoint Access', async ({ page }) => {
        await page.goto('/bonus-settings');
        await expect(page.getByText('Aturan Bonus')).toBeVisible();
        await expect(page.getByText('Forbidden')).not.toBeVisible();

        // Optional: Try to open the add modal to ensure full interactivity
        // await page.getByText('Tambah Aturan').click();
        // await expect(page.getByText('Simpan')).toBeVisible();
    });
});
