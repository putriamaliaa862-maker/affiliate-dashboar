// Service Worker for Shopee Scraper Extension
// Updated: 1x/day auto sync for Live Products + Manual sync anytime
let apiEndpoint = 'http://localhost:8000/api';
let syncInterval = 5 * 60 * 1000; // 5 minutes (for scraping, not syncing)
let isAutoSyncEnabled = true;
let syncApiKey = ''; // API key for authentication

// Load settings from storage
chrome.storage.local.get(['apiEndpoint', 'syncInterval', 'syncApiKey', 'autoSync'], (result) => {
    if (result.apiEndpoint) apiEndpoint = result.apiEndpoint;
    if (result.syncInterval) syncInterval = result.syncInterval;
    if (result.syncApiKey) syncApiKey = result.syncApiKey;
    if (result.autoSync !== undefined) isAutoSyncEnabled = result.autoSync;
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SHOPEE_DATA') {
        syncDataToDashboard(message.data)
            .then(() => {
                sendResponse({ success: true });
                updateBadge('✓', '#4CAF50');
            })
            .catch((error) => {
                console.error('Sync failed:', error);
                sendResponse({ success: false, error: error.message });
                updateBadge('✗', '#F44336');
            });
        return true; // Keep channel open for async response
    }

    // NEW: Live Products sync (1x/day logic)
    if (message.type === 'LIVE_PRODUCTS_SYNC') {
        syncLiveProducts(message.data, message.isManual)
            .then((result) => {
                sendResponse({ success: true, result });
                updateBadge('✓', '#4CAF50');

                // Update last sync date for this account (if auto sync)
                if (!message.isManual) {
                    chrome.storage.local.get(['lastDailySyncDateByAccount'], (stored) => {
                        const lastDates = stored.lastDailySyncDateByAccount || {};
                        lastDates[message.data.account_id] = getTodayDate();
                        chrome.storage.local.set({ lastDailySyncDateByAccount: lastDates });
                    });
                }
            })
            .catch((error) => {
                console.error('Live Products sync failed:', error);
                sendResponse({ success: false, error: error.message });
                updateBadge('✗', '#F44336');

                // Update status
                chrome.storage.local.get(['lastSyncStatusByAccount'], (stored) => {
                    const statuses = stored.lastSyncStatusByAccount || {};
                    statuses[message.data.account_id] = 'FAIL';
                    chrome.storage.local.set({
                        lastSyncStatusByAccount: statuses,
                        lastSyncErrorByAccount: {
                            ...stored.lastSyncErrorByAccount,
                            [message.data.account_id]: error.message
                        }
                    });
                });
            });
        return true;
    }

    if (message.type === 'GET_STATUS') {
        chrome.storage.local.get(['lastSync', 'totalSynced', 'lastDailySyncDateByAccount', 'lastSyncStatusByAccount'], (result) => {
            sendResponse({
                connected: true,
                lastSync: result.lastSync || null,
                totalSynced: result.totalSynced || 0,
                apiEndpoint: apiEndpoint,
                lastDailySyncDateByAccount: result.lastDailySyncDateByAccount || {},
                lastSyncStatusByAccount: result.lastSyncStatusByAccount || {}
            });
        });
        return true;
    }

    if (message.type === 'MANUAL_SYNC') {
        // Trigger content script to scrape
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, { type: 'SCRAPE_NOW', isManual: true });
            }
        });
        sendResponse({ success: true });
    }

    // NEW: Check if we should sync today for specific account
    if (message.type === 'CHECK_SHOULD_SYNC_TODAY') {
        chrome.storage.local.get(['lastDailySyncDateByAccount'], (result) => {
            const lastDates = result.lastDailySyncDateByAccount || {};
            const lastSyncDate = lastDates[message.accountId];
            const today = getTodayDate();
            const shouldSync = lastSyncDate !== today;

            sendResponse({
                shouldSync,
                lastSyncDate,
                today
            });
        });
        return true;
    }
});

// Sync data to dashboard API (old endpoint)
async function syncDataToDashboard(data) {
    const headers = {
        'Content-Type': 'application/json',
    };

    // Add API key if configured
    if (syncApiKey) {
        headers['X-Sync-Key'] = syncApiKey;
    }

    const response = await fetch(`${apiEndpoint}/shopee-data/sync`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        if (response.status === 401) {
            throw new Error('API Key invalid atau belum diset. Silakan cek Settings.');
        }
        throw new Error(`API Error: ${response.status}`);
    }

    // Update stats
    chrome.storage.local.get(['totalSynced'], (result) => {
        const newTotal = (result.totalSynced || 0) + 1;
        chrome.storage.local.set({
            lastSync: new Date().toISOString(),
            totalSynced: newTotal
        });
    });

    return response.json();
}

// NEW: Sync Live Products with 10s timeout + 1 retry
async function syncLiveProducts(data, isManual = false) {
    const headers = {
        'Content-Type': 'application/json',
    };

    // Add API key or access code
    if (syncApiKey) {
        headers['X-Sync-Key'] = syncApiKey;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    try {
        const response = await fetch(`${apiEndpoint}/live-products/sync`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            if (response.status === 403) {
                throw new Error('Forbidden: Host role cannot sync. Contact leader.');
            }
            if (response.status === 401) {
                throw new Error('Unauthorized: Check your API key/access code.');
            }
            throw new Error(`API Error: ${response.status}`);
        }

        const result = await response.json();

        // Update last sync status
        chrome.storage.local.get(['lastSyncStatusByAccount', 'lastSyncAtByAccount'], (stored) => {
            const statuses = stored.lastSyncStatusByAccount || {};
            const syncTimes = stored.lastSyncAtByAccount || {};

            statuses[data.account_id] = 'SUCCESS';
            syncTimes[data.account_id] = new Date().toISOString();

            chrome.storage.local.set({
                lastSyncStatusByAccount: statuses,
                lastSyncAtByAccount: syncTimes
            });
        });

        return result;

    } catch (error) {
        clearTimeout(timeoutId);

        // If timeout or network error, retry once
        if (error.name === 'AbortError' || error.message.includes('fetch')) {
            console.log('Retrying sync after error:', error.message);

            // Retry once (without timeout this time, let it take as long as needed)
            try {
                const retryResponse = await fetch(`${apiEndpoint}/live-products/sync`, {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(data)
                });

                if (!retryResponse.ok) {
                    throw new Error(`Retry failed: ${retryResponse.status}`);
                }

                return await retryResponse.json();
            } catch (retryError) {
                throw new Error(`Sync failed after retry: ${retryError.message}`);
            }
        }

        throw error;
    }
}

// Helper: Get today's date as YYYY-MM-DD
function getTodayDate() {
    const now = new Date();
    return now.toISOString().split('T')[0];
}

// Update extension badge
function updateBadge(text, color) {
    chrome.action.setBadgeText({ text });
    chrome.action.setBadgeBackgroundColor({ color });

    // Clear badge after 3 seconds
    setTimeout(() => {
        chrome.action.setBadgeText({ text: '' });
    }, 3000);
}

// Auto-sync timer (scraping every 5 minutes, but syncing 1x/day)
setInterval(() => {
    if (isAutoSyncEnabled) {
        chrome.tabs.query({ url: '*://*.shopee.co.id/*' }, (tabs) => {
            tabs.forEach(tab => {
                chrome.tabs.sendMessage(tab.id, { type: 'SCRAPE_NOW', isManual: false });
            });
        });
    }
}, syncInterval);

console.log('Shopee Scraper Extension loaded (Live Products 1x/day sync enabled)');
