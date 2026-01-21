// Affiliate Hub Extension - Service Worker
// Background Auto-Sync Service

const BACKEND_URL = 'http://localhost:8000';
const SYNC_INTERVAL = 5 * 60 * 1000; // 5 minutes

let syncTimer = null;
let accessCode = null;
let syncKey = null;

// ===== INITIALIZATION =====
chrome.runtime.onInstalled.addListener(() => {
    console.log('Affiliate Hub Extension installed');
    loadCredentials();
});

chrome.runtime.onStartup.addListener(() => {
    console.log('Affiliate Hub Extension started');
    loadCredentials();
    checkAutoSync();
});

// ===== LOAD CREDENTIALS =====
async function loadCredentials() {
    try {
        const data = await chrome.storage.local.get(['accessCode', 'syncKey']);
        accessCode = data.accessCode || null;
        syncKey = data.syncKey || null;

        console.log('Credentials loaded:', {
            hasAccessCode: !!accessCode,
            hasSyncKey: !!syncKey
        });
    } catch (error) {
        console.error('Failed to load credentials:', error);
    }
}

// ===== CHECK AUTO-SYNC ON STARTUP =====
async function checkAutoSync() {
    try {
        const data = await chrome.storage.local.get('autoSync');
        if (data.autoSync) {
            startAutoSync();
        }
    } catch (error) {
        console.error('Failed to check auto-sync:', error);
    }
}

// ===== LISTEN FOR MESSAGES FROM POPUP =====
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'ACCESS_CODE_UPDATED') {
        loadCredentials();
    } else if (message.type === 'AUTO_SYNC_TOGGLE') {
        if (message.enabled) {
            startAutoSync();
        } else {
            stopAutoSync();
        }
    }

    return true;
});

// ===== AUTO-SYNC FUNCTIONS =====
function startAutoSync() {
    if (syncTimer) {
        console.log('Auto-sync already running');
        return;
    }

    console.log('Starting auto-sync (5 min interval)');

    // Run immediately
    performAutoSync();

    // Then run every 5 minutes
    syncTimer = setInterval(performAutoSync, SYNC_INTERVAL);
}

function stopAutoSync() {
    if (syncTimer) {
        console.log('Stopping auto-sync');
        clearInterval(syncTimer);
        syncTimer = null;
    }
}

async function performAutoSync() {
    try {
        console.log('Auto-sync triggered');

        // Reload credentials in case they changed
        await loadCredentials();

        // Check if we have sync key (for background sync)
        if (!syncKey && !accessCode) {
            console.log('No credentials available, skipping auto-sync');
            return;
        }

        // Get all Shopee tabs
        const tabs = await chrome.tabs.query({
            url: [
                'https://*.shopee.co.id/*',
                'https://affiliate.shopee.co.id/*',
                'https://seller.shopee.co.id/*'
            ]
        });

        if (tabs.length === 0) {
            console.log('No Shopee tabs open, skipping auto-sync');
            return;
        }

        console.log(`Found ${tabs.length} Shopee tab(s), syncing...`);

        // Sync data from each tab
        for (const tab of tabs) {
            await syncTabData(tab);
        }

        // Update last sync time
        await chrome.storage.local.set({ lastSync: Date.now() });

        console.log('Auto-sync completed');
    } catch (error) {
        console.error('Auto-sync error:', error);
    }
}

async function syncTabData(tab) {
    try {
        // Inject script to scrape data
        const [result] = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: scrapePerformanceData
        });

        if (!result || !result.result) {
            console.log(`No data found on tab: ${tab.url}`);
            return;
        }

        // Send to backend (use sync key for background, or access code as fallback)
        const headers = {
            'Content-Type': 'application/json'
        };

        if (syncKey) {
            headers['x-sync-key'] = syncKey;
        } else if (accessCode) {
            headers['x-access-code'] = accessCode;
        }

        const response = await fetch(`${BACKEND_URL}/api/shopee-data/sync`, {
            method: 'POST',
            headers,
            body: JSON.stringify(result.result)
        });

        if (response.ok) {
            console.log(`Synced data from: ${tab.url}`);
        } else {
            const error = await response.json();
            console.error(`Sync failed for ${tab.url}:`, error);
        }
    } catch (error) {
        console.error(`Error syncing tab ${tab.id}:`, error);
    }
}

// ===== SCRAPING FUNCTION (injected into page) =====
function scrapePerformanceData() {
    const url = window.location.href;

    // Detect page type and scrape accordingly
    if (url.includes('affiliate.shopee.co.id')) {
        return scrapeAffiliateData();
    } else if (url.includes('seller.shopee.co.id/creator-center')) {
        return scrapeLiveData();
    } else if (url.includes('seller.shopee.co.id')) {
        return scrapeSellerData();
    }

    return null;
}

function scrapeAffiliateData() {
    try {
        const data = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            type: 'affiliate_dashboard',
            accountId: 'affiliate_account',
            sessionToken: null,
            payload: {
                totalCommission: 0,
                totalOrders: 0,
                date: new Date().toISOString().split('T')[0]
            }
        };

        return data;
    } catch (error) {
        console.error('Affiliate scrape error:', error);
        return null;
    }
}

function scrapeLiveData() {
    try {
        const data = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            type: 'live_streaming',
            accountId: 'live_account',
            sessionToken: null,
            payload: {
                revenue: 0,
                viewers: 0,
                duration: '0:00'
            }
        };

        return data;
    } catch (error) {
        console.error('Live scrape error:', error);
        return null;
    }
}

function scrapeSellerData() {
    try {
        const data = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            type: 'transactions',
            accountId: 'seller_account',
            sessionToken: null,
            payload: {
                transactions: []
            }
        };

        return data;
    } catch (error) {
        console.error('Seller scrape error:', error);
        return null;
    }
}
