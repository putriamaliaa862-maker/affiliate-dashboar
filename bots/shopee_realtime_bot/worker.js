/**
 * Worker - Single account scraper for Playwright bot
 * Handles: Creator Live orders, Ads Center spend/budget
 */
const { launchBrowser, screenshotError, waitForSelector, isLoginPage } = require('./lib/browser');
const { postSnapshot } = require('./lib/uploader');
const logger = require('./lib/logger');
const creatorSelectors = require('./selectors/creator_live');
const adsSelectors = require('./selectors/ads_seller');

/**
 * Scrape a single account
 */
async function scrapeAccount(account) {
    const { shopee_account_id, shop_name } = account;
    logger.info(`Starting scrape for ${shop_name}`, shopee_account_id);

    let context = null;
    let results = { success: false, snapshots: [] };

    try {
        // Launch browser with persistent profile
        context = await launchBrowser(shopee_account_id);
        const page = await context.newPage();

        // 1. Scrape Creator Live Dashboard
        const creatorData = await scrapeCreatorLive(page, account);
        if (creatorData) {
            results.snapshots.push({
                shopee_account_id,
                shop_name,
                snapshot_type: 'creator_live',
                data: creatorData,
                scraped_at: new Date().toISOString()
            });
        }

        // 2. Scrape Ads Center
        const adsData = await scrapeAdsCenter(page, account);
        if (adsData) {
            results.snapshots.push({
                shopee_account_id,
                shop_name,
                snapshot_type: 'ads',
                data: adsData,
                scraped_at: new Date().toISOString()
            });
        }

        results.success = results.snapshots.length > 0;

        // Push snapshots to backend
        for (const snap of results.snapshots) {
            await postSnapshot(snap);
        }

        logger.info(`Completed: ${results.snapshots.length} snapshots`, shopee_account_id);

    } catch (error) {
        logger.error(`Scrape failed: ${error.message}`, shopee_account_id);
        results.error = error.message;
    } finally {
        if (context) {
            await context.close();
        }
    }

    return results;
}

/**
 * Scrape Creator Live dashboard
 */
async function scrapeCreatorLive(page, account) {
    const { shopee_account_id } = account;

    try {
        logger.info('Navigating to Creator Live...', shopee_account_id);
        await page.goto(creatorSelectors.CREATOR_ORDERS, { waitUntil: 'domcontentloaded', timeout: 30000 });

        // Check for login redirect
        if (isLoginPage(page.url())) {
            logger.warn('Login required - session expired', shopee_account_id);
            await screenshotError(page, shopee_account_id, 'login_required');
            return null;
        }

        // Wait for page content
        await page.waitForTimeout(3000);

        // Extract order counts
        const ordersReady = await extractNumber(page, creatorSelectors.ORDERS_READY_TO_SHIP);
        const pendingOrders = await extractNumber(page, creatorSelectors.PENDING_ORDERS);

        const data = {
            orders_ready_to_ship: ordersReady,
            pending_orders: pendingOrders,
            page_url: page.url()
        };

        logger.info(`Creator Live: ready=${ordersReady}, pending=${pendingOrders}`, shopee_account_id);
        return data;

    } catch (error) {
        logger.error(`Creator Live scrape failed: ${error.message}`, shopee_account_id);
        await screenshotError(page, shopee_account_id, 'creator_error');
        return null;
    }
}

/**
 * Scrape Ads Center
 */
async function scrapeAdsCenter(page, account) {
    const { shopee_account_id } = account;

    try {
        logger.info('Navigating to Ads Center...', shopee_account_id);
        await page.goto(adsSelectors.ADS_CENTER, { waitUntil: 'domcontentloaded', timeout: 30000 });

        if (isLoginPage(page.url())) {
            logger.warn('Login required for Ads Center', shopee_account_id);
            await screenshotError(page, shopee_account_id, 'ads_login_required');
            return null;
        }

        await page.waitForTimeout(3000);

        // Extract ads data
        const spendToday = await extractNumber(page, adsSelectors.SPEND_TODAY);
        const budgetAvailable = await extractNumber(page, adsSelectors.BUDGET_AVAILABLE);
        const coins = await extractNumber(page, adsSelectors.COINS_BALANCE);

        const data = {
            spend_today: spendToday,
            budget_available: budgetAvailable,
            coins: coins,
            page_url: page.url()
        };

        logger.info(`Ads: spend=${spendToday}, budget=${budgetAvailable}, coins=${coins}`, shopee_account_id);
        return data;

    } catch (error) {
        logger.error(`Ads Center scrape failed: ${error.message}`, shopee_account_id);
        await screenshotError(page, shopee_account_id, 'ads_error');
        return null;
    }
}

/**
 * Try multiple selectors to extract a number
 */
async function extractNumber(page, selectors) {
    for (const selector of selectors) {
        try {
            const el = await page.$(selector);
            if (el) {
                const text = await el.textContent();
                const num = parseFloat(text.replace(/[^0-9.]/g, ''));
                if (!isNaN(num)) return num;
            }
        } catch { }
    }
    return 0;
}

// Export for supervisor
module.exports = { scrapeAccount };

// Run standalone if called directly
if (require.main === module) {
    const accounts = require('./config/accounts.json');
    const testAccount = accounts[0];

    if (testAccount) {
        console.log('🧪 Running test scrape for:', testAccount.shop_name);
        scrapeAccount(testAccount).then(result => {
            console.log('Result:', JSON.stringify(result, null, 2));
            process.exit(result.success ? 0 : 1);
        });
    } else {
        console.log('❌ No accounts in config/accounts.json');
        process.exit(1);
    }
}
