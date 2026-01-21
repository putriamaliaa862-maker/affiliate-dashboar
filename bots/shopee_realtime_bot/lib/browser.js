/**
 * Browser helper - Playwright context management
 */
const { chromium } = require('playwright');
const path = require('path');
const logger = require('./logger');

const PROFILES_DIR = path.join(__dirname, '..', 'profiles');
const SCREENSHOTS_DIR = path.join(__dirname, '..', 'screenshots');

/**
 * Launch browser with persistent profile for session cookies
 */
async function launchBrowser(accountId, options = {}) {
    const profileDir = path.join(PROFILES_DIR, `profile_${accountId}`);

    logger.info(`Launching browser with profile: ${profileDir}`, accountId);

    const context = await chromium.launchPersistentContext(profileDir, {
        headless: false, // VISIBLE mode as required
        viewport: { width: 1280, height: 800 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        args: [
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox'
        ],
        ...options
    });

    return context;
}

/**
 * Take screenshot on error
 */
async function screenshotError(page, accountId, errorType) {
    try {
        const filename = `${accountId}_${errorType}_${Date.now()}.png`;
        const filepath = path.join(SCREENSHOTS_DIR, filename);
        await page.screenshot({ path: filepath, fullPage: true });
        logger.warn(`Screenshot saved: ${filename}`, accountId);
        return filepath;
    } catch (e) {
        logger.error(`Failed to take screenshot: ${e.message}`, accountId);
        return null;
    }
}

/**
 * Wait for selector with timeout and retry
 */
async function waitForSelector(page, selector, timeout = 10000) {
    try {
        await page.waitForSelector(selector, { timeout });
        return true;
    } catch {
        return false;
    }
}

/**
 * Check if page redirected to login
 */
function isLoginPage(url) {
    return url.includes('login') ||
        url.includes('buyer/login') ||
        url.includes('signin');
}

module.exports = {
    launchBrowser,
    screenshotError,
    waitForSelector,
    isLoginPage
};
