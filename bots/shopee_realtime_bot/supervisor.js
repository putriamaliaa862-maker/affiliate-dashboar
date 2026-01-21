/**
 * Supervisor - Main orchestrator for 24H Playwright bot
 * Manages worker pool, scheduling, and crash recovery
 */
const { scrapeAccount } = require('./worker');
const logger = require('./lib/logger');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    ACCOUNTS_FILE: path.join(__dirname, 'config', 'accounts.json'),
    MAX_PARALLEL_WORKERS: parseInt(process.env.MAX_WORKERS) || 5,
    SYNC_INTERVAL_MS: parseInt(process.env.SYNC_INTERVAL) || 60000, // 60 seconds
    RETRY_DELAY_MS: 5000
};

// State
let accounts = [];
let isRunning = false;
let currentCycle = 0;
let stats = {
    totalCycles: 0,
    successCount: 0,
    failCount: 0,
    lastCycleAt: null
};

/**
 * Load accounts from config file
 */
function loadAccounts() {
    try {
        const data = fs.readFileSync(CONFIG.ACCOUNTS_FILE, 'utf8');
        accounts = JSON.parse(data).filter(a => a.enabled !== false);
        logger.info(`Loaded ${accounts.length} enabled accounts`);
        return accounts;
    } catch (error) {
        logger.error(`Failed to load accounts: ${error.message}`);
        return [];
    }
}

/**
 * Process accounts in batches
 */
async function processBatch(batch) {
    const promises = batch.map(async (account) => {
        try {
            const result = await scrapeAccount(account);
            if (result.success) {
                stats.successCount++;
            } else {
                stats.failCount++;
            }
            return result;
        } catch (error) {
            logger.error(`Worker crashed for ${account.shopee_account_id}: ${error.message}`);
            stats.failCount++;
            return { success: false, error: error.message };
        }
    });

    return Promise.all(promises);
}

/**
 * Run a complete sync cycle for all accounts
 */
async function runCycle() {
    currentCycle++;
    const cycleStart = Date.now();
    logger.info(`=== CYCLE ${currentCycle} STARTING (${accounts.length} accounts) ===`);

    // Process in batches
    for (let i = 0; i < accounts.length; i += CONFIG.MAX_PARALLEL_WORKERS) {
        const batch = accounts.slice(i, i + CONFIG.MAX_PARALLEL_WORKERS);
        logger.info(`Processing batch ${Math.floor(i / CONFIG.MAX_PARALLEL_WORKERS) + 1}: ${batch.map(a => a.shop_name).join(', ')}`);

        await processBatch(batch);

        // Small delay between batches to prevent overwhelming
        if (i + CONFIG.MAX_PARALLEL_WORKERS < accounts.length) {
            await new Promise(r => setTimeout(r, 1000));
        }
    }

    const duration = ((Date.now() - cycleStart) / 1000).toFixed(1);
    stats.totalCycles++;
    stats.lastCycleAt = new Date().toISOString();

    logger.info(`=== CYCLE ${currentCycle} COMPLETED in ${duration}s (success: ${stats.successCount}, fail: ${stats.failCount}) ===`);
}

/**
 * Main loop - runs continuously
 */
async function startSupervisor() {
    logger.info('🚀 SUPERVISOR STARTING');
    logger.info(`Max parallel workers: ${CONFIG.MAX_PARALLEL_WORKERS}`);
    logger.info(`Sync interval: ${CONFIG.SYNC_INTERVAL_MS / 1000}s`);

    loadAccounts();

    if (accounts.length === 0) {
        logger.error('No accounts to process. Add accounts to config/accounts.json');
        process.exit(1);
    }

    isRunning = true;

    // Run immediately on start
    await runCycle();

    // Then schedule periodic runs
    const intervalId = setInterval(async () => {
        if (!isRunning) {
            clearInterval(intervalId);
            return;
        }

        try {
            await runCycle();
        } catch (error) {
            logger.error(`Cycle failed with error: ${error.message}`);
            // Don't crash supervisor on cycle error, will retry next interval
        }
    }, CONFIG.SYNC_INTERVAL_MS);

    // Graceful shutdown handlers
    process.on('SIGINT', () => shutdown('SIGINT'));
    process.on('SIGTERM', () => shutdown('SIGTERM'));

    logger.info('✅ SUPERVISOR RUNNING - Press Ctrl+C to stop');
}

/**
 * Graceful shutdown
 */
function shutdown(signal) {
    logger.info(`${signal} received. Shutting down gracefully...`);
    isRunning = false;

    logger.info('=== FINAL STATS ===');
    logger.info(`Total cycles: ${stats.totalCycles}`);
    logger.info(`Success: ${stats.successCount}`);
    logger.info(`Failures: ${stats.failCount}`);

    setTimeout(() => {
        logger.info('Supervisor stopped.');
        process.exit(0);
    }, 2000);
}

/**
 * Get current stats (for API)
 */
function getStats() {
    return {
        isRunning,
        currentCycle,
        accountsCount: accounts.length,
        ...stats
    };
}

// Export for external use
module.exports = { startSupervisor, getStats };

// Run if called directly
if (require.main === module) {
    startSupervisor().catch(error => {
        logger.error(`Supervisor failed to start: ${error.message}`);
        process.exit(1);
    });
}
