// Service Worker v2.0 - FINAL
// Fixed: Robust identity handling with explicit Promise-based storage
console.log('[BG] Service worker starting...');

let apiEndpoint = 'http://localhost:8000/api';
let isAutoSyncEnabled = true;
let supabaseUrl = null;
let supabaseAnonKey = null;
let useSupabase = false;

// ==================== STORAGE HELPERS ====================

function getStorage(keys) {
    return new Promise((resolve) => {
        chrome.storage.local.get(keys, (result) => {
            resolve(result);
        });
    });
}

function setStorage(data) {
    return new Promise((resolve) => {
        chrome.storage.local.set(data, () => {
            resolve();
        });
    });
}

async function getConnectedIdentity() {
    const result = await getStorage(['connected_identity']);
    const identity = result.connected_identity || null;
    console.log('[BG] getConnectedIdentity:', identity);
    return identity;
}

async function saveConnectedIdentity(identity) {
    const data = {
        shopee_account_id: identity.shopee_account_id,
        shop_name: identity.shop_name || identity.shopee_account_id,
        username: identity.username || null,
        connected_at: new Date().toISOString()
    };
    await setStorage({ connected_identity: data });
    console.log('[BG] ✅ Identity saved:', data);
    return data;
}

async function requireConnectedIdentity() {
    const identity = await getConnectedIdentity();
    if (!identity || !identity.shopee_account_id) {
        throw new Error('NOT_CONNECTED: Click Connect Account first');
    }
    return identity;
}

// ==================== LOAD SETTINGS ====================

getStorage(['apiEndpoint', 'autoSync', 'supabaseUrl', 'supabaseAnonKey', 'useSupabase']).then((result) => {
    if (result.apiEndpoint) apiEndpoint = result.apiEndpoint;
    if (result.autoSync !== undefined) isAutoSyncEnabled = result.autoSync;
    if (result.supabaseUrl) supabaseUrl = result.supabaseUrl;
    if (result.supabaseAnonKey) supabaseAnonKey = result.supabaseAnonKey;
    if (result.useSupabase !== undefined) useSupabase = result.useSupabase;
    console.log('[BG] Settings loaded:', { apiEndpoint, isAutoSyncEnabled, useSupabase, hasSupabase: !!supabaseUrl });
});

// ==================== TAB HELPERS ====================

const ALLOWED_DOMAINS = [
    'affiliate.shopee.co.id',
    'creator.shopee.co.id',
    'seller.shopee.co.id',
    'live.shopee.co.id'
];

async function getBestShopeeTab() {
    const tabs = await chrome.tabs.query({ currentWindow: true });

    // Priority 1: Active Shopee tab
    const activeTab = tabs.find(t => t.active);
    if (activeTab && activeTab.url && ALLOWED_DOMAINS.some(d => activeTab.url.includes(d))) {
        console.log('[BG] Using active Shopee tab:', activeTab.url);
        return activeTab;
    }

    // Priority 2: Any Shopee tab (not chrome-extension://)
    const shopeeTab = tabs.find(t =>
        t.url &&
        !t.url.startsWith('chrome') &&
        ALLOWED_DOMAINS.some(d => t.url.includes(d))
    );

    if (shopeeTab) {
        console.log('[BG] Using Shopee tab:', shopeeTab.url);
        return shopeeTab;
    }

    console.warn('[BG] No Shopee tab found');
    return null;
}

async function injectContentScript(tabId, tabUrl) {
    if (!ALLOWED_DOMAINS.some(d => tabUrl.includes(d))) {
        throw new Error('Page not supported');
    }

    try {
        await chrome.tabs.sendMessage(tabId, { type: 'PING' });
        return true;
    } catch {
        console.log('[BG] Injecting content script...');
        await chrome.scripting.executeScript({
            target: { tabId },
            files: ['content/shopee-scraper.js']
        });
        await new Promise(r => setTimeout(r, 500));
        return true;
    }
}

async function sendTabMessage(tabId, tabUrl, message) {
    try {
        await injectContentScript(tabId, tabUrl);
        return new Promise((resolve) => {
            chrome.tabs.sendMessage(tabId, message, (response) => {
                if (chrome.runtime.lastError) {
                    console.error('[BG] Tab message error:', chrome.runtime.lastError.message);
                    resolve({ success: false, error: chrome.runtime.lastError.message });
                } else {
                    resolve(response || { success: true });
                }
            });
        });
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ==================== MESSAGE HANDLERS ====================

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('[BG] Message:', message.type);

    // GET_STATUS
    if (message.type === 'GET_STATUS') {
        (async () => {
            const identity = await getConnectedIdentity();
            const storage = await getStorage(['lastSync', 'totalSynced']);
            sendResponse({
                connected: !!(identity && identity.shopee_account_id),
                identity: identity,
                lastSync: storage.lastSync || null,
                totalSynced: storage.totalSynced || 0,
                apiEndpoint: apiEndpoint
            });
        })();
        return true;
    }

    // SHOPEE_DATA - Main sync
    if (message.type === 'SHOPEE_DATA') {
        console.log('[BG] SHOPEE_DATA:', message.data?.type);
        syncData(message.data)
            .then((result) => {
                console.log('[BG] ✅ Sync success');
                sendResponse({ success: true, result });
                updateBadge('✓', '#28a745');
            })
            .catch((error) => {
                console.error('[BG] ✗ Sync failed:', error.message);
                sendResponse({ success: false, error: error.message });
                updateBadge('✗', '#dc3545');
            });
        return true;
    }

    // LIVE_PRODUCTS_SYNC
    if (message.type === 'LIVE_PRODUCTS_SYNC') {
        syncLiveProducts(message.data)
            .then((result) => {
                sendResponse({ success: true, result });
                updateBadge('✓', '#28a745');
            })
            .catch((error) => {
                sendResponse({ success: false, error: error.message });
                updateBadge('✗', '#dc3545');
            });
        return true;
    }

    // MANUAL_SYNC
    if (message.type === 'MANUAL_SYNC') {
        console.log('[BG] MANUAL_SYNC');
        (async () => {
            try {
                // Check connected
                const identity = await getConnectedIdentity();
                if (!identity || !identity.shopee_account_id) {
                    updateBadge('!', '#ffc107');
                    sendResponse({ success: false, error: 'NOT_CONNECTED: Click Connect Account first' });
                    return;
                }

                // Get Shopee tab
                const tab = await getBestShopeeTab();
                if (!tab) {
                    updateBadge('!', '#ffc107');
                    sendResponse({ success: false, error: 'Open a Shopee page first' });
                    return;
                }

                // Block extension pages
                if (tab.url.startsWith('chrome-extension://') || tab.url.startsWith('chrome://')) {
                    updateBadge('!', '#ffc107');
                    sendResponse({ success: false, error: 'Switch to Shopee page, not extension' });
                    return;
                }

                console.log('[BG] Sending SCRAPE_NOW to:', tab.url);
                const result = await sendTabMessage(tab.id, tab.url, { type: 'SCRAPE_NOW', isManual: true });

                if (result.success) {
                    updateBadge('✓', '#28a745');
                } else {
                    updateBadge('!', '#ffc107');
                }

                sendResponse(result);
            } catch (error) {
                console.error('[BG] MANUAL_SYNC error:', error);
                sendResponse({ success: false, error: error.message });
            }
        })();
        return true;
    }

    // SYNC_IDENTITY
    if (message.type === 'SYNC_IDENTITY') {
        console.log('[BG] SYNC_IDENTITY:', message.data);
        (async () => {
            try {
                const { shopee_account_id, account_id, shop_name, username } = message.data || {};
                const finalId = shopee_account_id || account_id;

                if (!finalId) {
                    sendResponse({ success: false, error: 'Missing account_id' });
                    return;
                }

                // Save identity
                await saveConnectedIdentity({
                    shopee_account_id: finalId,
                    shop_name: shop_name || finalId,
                    username: username
                });

                // Sync to backend
                const payload = {
                    account: {
                        shopee_account_id: finalId,
                        shop_name: shop_name || finalId,
                        username: username
                    },
                    type: 'identity',
                    data: { shopee_account_id: finalId, shop_name: shop_name || finalId },
                    url: 'https://affiliate.shopee.co.id/account_setting'
                };

                await syncData(payload);

                console.log('[BG] ✅ Identity synced');
                sendResponse({ success: true });
                updateBadge('✓', '#28a745');

            } catch (error) {
                console.error('[BG] SYNC_IDENTITY error:', error);
                sendResponse({ success: false, error: error.message });
                updateBadge('✗', '#dc3545');
            }
        })();
        return true;
    }

    // SYNC_ALL
    if (message.type === 'SYNC_ALL') {
        console.log('[BG] SYNC_ALL');
        (async () => {
            try {
                const identity = await requireConnectedIdentity();
                console.log('[BG] SYNC_ALL for:', identity.shop_name);

                const tab = await getBestShopeeTab();
                if (tab) {
                    await sendTabMessage(tab.id, tab.url, { type: 'SCRAPE_NOW', isManual: true });
                }

                sendResponse({ success: true });
                updateBadge('✓', '#28a745');
            } catch (error) {
                console.error('[BG] SYNC_ALL error:', error);
                sendResponse({ success: false, error: error.message });
            }
        })();
        return true;
    }
});

// ==================== BACKEND SYNC ====================

async function syncToSupabase(data) {
    if (!supabaseUrl || !supabaseAnonKey) {
        throw new Error('Supabase not configured. Using backend fallback.');
    }

    const storage = await getStorage(['accessCode']);
    if (!storage.accessCode) {
        throw new Error('Access Code not set. Open extension popup.');
    }

    console.log('[BG] POST to Supabase:', supabaseUrl);
    console.log('[BG] Payload type:', data.type);

    const payload = {
        type: data.type,
        account_info: data.account || {},
        payload: data.data || {},
        access_code: storage.accessCode
    };

    const response = await fetch(`${supabaseUrl}/rest/v1/shopee_data_sync`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'apikey': supabaseAnonKey,
            'Authorization': `Bearer ${supabaseAnonKey}`,
            'Prefer': 'return=representation'
        },
        body: JSON.stringify(payload)
    });

    console.log('[BG] Supabase Response:', response.status, response.statusText);

    if (!response.ok) {
        const errorBody = await response.text();
        console.error('[BG] Supabase Error:', errorBody);
        throw new Error(`Supabase ${response.status}: ${errorBody.substring(0, 100)}`);
    }

    const result = await response.json();
    
    // Update stats
    const stats = await getStorage(['totalSynced']);
    await setStorage({
        lastSync: new Date().toISOString(),
        totalSynced: (stats.totalSynced || 0) + 1
    });

    return result;
}

async function syncToBackend(data) {
    const endpoint = `${apiEndpoint}/shopee-data/sync`;
    console.log('[BG] POST', endpoint);
    console.log('[BG] Payload type:', data.type);
    console.log('[BG] Account:', data.account);

    const storage = await getStorage(['accessCode']);
    if (!storage.accessCode) {
        throw new Error('Access Code not set. Open extension popup.');
    }

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Access-Code': storage.accessCode
        },
        body: JSON.stringify(data)
    });

    console.log('[BG] Response:', response.status, response.statusText);

    if (!response.ok) {
        const errorBody = await response.text();
        console.error('[BG] Error body:', errorBody);
        throw new Error(`API ${response.status}: ${errorBody.substring(0, 100)}`);
    }

    // Update stats
    const stats = await getStorage(['totalSynced']);
    await setStorage({
        lastSync: new Date().toISOString(),
        totalSynced: (stats.totalSynced || 0) + 1
    });

    return await response.json();
}

// Main sync function - chooses Supabase or Backend
async function syncData(data) {
    if (useSupabase && supabaseUrl && supabaseAnonKey) {
        try {
            return await syncToSupabase(data);
        } catch (error) {
            console.warn('[BG] Supabase sync failed, falling back to backend:', error.message);
            // Fallback to backend
            return await syncToBackend(data);
        }
    } else {
        // Default to backend
        return await syncToBackend(data);
    }
}

async function syncLiveProducts(data) {
    const storage = await getStorage(['accessCode']);
    if (!storage.accessCode) throw new Error('Access Code not set');

    const response = await fetch(`${apiEndpoint}/live-products/sync`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Access-Code': storage.accessCode
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) throw new Error(`API ${response.status}`);
    return await response.json();
}

// ==================== BADGE ====================

function updateBadge(text, color) {
    chrome.action.setBadgeText({ text });
    chrome.action.setBadgeBackgroundColor({ color });
    setTimeout(() => chrome.action.setBadgeText({ text: '' }), 3000);
}

// ==================== AUTO SYNC ====================

setInterval(async () => {
    if (!isAutoSyncEnabled) return;

    const identity = await getConnectedIdentity();
    if (!identity?.shopee_account_id) return;

    const tabs = await chrome.tabs.query({ url: '*://*.shopee.co.id/*' });
    for (const tab of tabs) {
        try {
            await chrome.tabs.sendMessage(tab.id, { type: 'SCRAPE_NOW', isManual: false });
        } catch { }
    }
}, 5 * 60 * 1000);

console.log('[BG] ✅ Service worker ready');
