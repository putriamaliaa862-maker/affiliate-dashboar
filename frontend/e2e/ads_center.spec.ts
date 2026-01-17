import { test, expect } from '@playwright/test';

test.describe('Ads Center', () => {
    test('should navigate to Ads Center and display elements', async ({ page }) => {
        // 1. Login (Reuse auth state if configured, or manual login)
        // Assuming auth.setup.ts handles login state storage.

        // Go to Ads Center
        await page.goto('/ads-center');

        // Check Header
        await expect(page.getByText('Ads Center')).toBeVisible();
        await expect(page.getByText('Pantau iklan per akun biar nggak boncos & makin gacor.')).toBeVisible();

        // Check Filter Bar
        await expect(page.getByRole('combobox')).toBeVisible(); // Account dropdown
        await expect(page.getByRole('button', { name: 'Refresh' })).toBeVisible();

        // Check KPI Cards
        await expect(page.getByText('Total Spend Hari Ini')).toBeVisible();
        await expect(page.getByText('Avg ROAS')).toBeVisible();

        // Check Table
        await expect(page.getByRole('table')).toBeVisible();
        await expect(page.getByText('Performa Iklan per Akun')).toBeVisible();
    });
});
