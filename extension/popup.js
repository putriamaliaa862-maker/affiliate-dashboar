// Affiliate Hub Extension - Popup Logic
// Streamo-Style Edition v2.0.0

const BACKEND_URL = 'http://localhost:8000';

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadSettings();
    setupEventListeners();
});

// ===== LOAD SAVED SETTINGS =====
async function loadSettings() {
    try {
        const data = await chrome.storage.local.get(['accessCode', 'autoSync', 'lastSync']);

        // Load Access Code (don't show in input for security)
        if (data.accessCode) {
            document.getElementById('accessCode').placeholder = '••••••••';
            updateConnectionStatus(true);
        }

        // Load Auto-sync toggle
        document.getElementById('autoSyncToggle').checked = data.autoSync || false;

        // Load Last Sync time
        if (data.lastSync) {
            const lastSyncDate = new Date(data.lastSync);
            document.getElementById('lastSyncText').textContent = formatTime(lastSyncDate);
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Save Access Code
    document.getElementById('saveBtn').addEventListener('click', handleSaveAccessCode);

    // Add Account to Server
    document.getElementById('addAccountBtn').addEventListener('click', handleAddAccount);

    // Send Daily Performance
    document.getElementById('sendPerformanceBtn').addEventListener('click', handleSendPerformance);

    // Auto-sync Toggle
    document.getElementById('autoSyncToggle').addEventListener('change', handleAutoSyncToggle);
}

// ===== SAVE ACCESS CODE =====
async function handleSaveAccessCode() {
    const accessCode = document.getElementById('accessCode').value.trim();

    if (!accessCode) {
        showStatus('Please enter access code', 'error');
        return;
    }

    try {
        // Save to storage
        await chrome.storage.local.set({ accessCode });

        // Clear input for security
        document.getElementById('accessCode').value = '';
        document.getElementById('accessCode').placeholder = '••••••••';

        showStatus('Access code saved!', 'success');
        updateConnectionStatus(true);

        // Notify service worker
        chrome.runtime.sendMessage({ type: 'ACCESS_CODE_UPDATED' });
    } catch (error) {
        showStatus('Failed to save access code', 'error');
        console.error(error);
    }
}

// ===== ADD ACCOUNT TO SERVER =====
async function handleAddAccount() {
    try {
        const { accessCode } = await chrome.storage.local.get('accessCode');

        if (!accessCode) {
            showStatus('Please save access code first', 'error');
            return;
        }

        showStatus('Extracting account info...', 'info');

        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab.url.includes('shopee')) {
            showStatus('Please open a Shopee page first', 'error');
            return;
        }

        // Extract cookies
        const cookies = await extractShopeeC ookies();

        if (!cookies.SPC_EC || !cookies.SPC_F) {
            showStatus('Cookies not found. Please login to Shopee first', 'error');
            return;
        }

        // Send to backend
        const response = await fetch(`${BACKEND_URL}/api/shopee-accounts/import-cookies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-access-code': accessCode
            },
            body: JSON.stringify({
                platform: 'shopee',
                account_name: 'Auto-detected',
                cookie_spc_ec: cookies.SPC_EC,
                cookie_spc_f: cookies.SPC_F,
                source_url: tab.url
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add account');
        }

        const result = await response.json();
        showStatus(`✓ Account "${result.account_name}" added!`, 'success');

    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
        console.error('Add account error:', error);
    }
}

// ===== SEND DAILY PERFORMANCE =====
async function handleSendPerformance() {
    try {
        const { accessCode } = await chrome.storage.local.get('accessCode');

        if (!accessCode) {
            showStatus('Please save access code first', 'error');
            return;
        }

        showStatus('Scraping performance data...', 'info');

        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab.url.includes('shopee')) {
            showStatus('Please open a Shopee page first', 'error');
            return;
        }

        // Inject content script to scrape data
        const [result] = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: scrapePerformanceData
        });

        if (!result || !result.result) {
            showStatus('No data found on this page', 'error');
            return;
        }

        // Send to backend
        const response = await fetch(`${BACKEND_URL}/api/shopee-data/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-access-code': accessCode
            },
            body: JSON.stringify(result.result)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Sync failed');
        }

        // Update last sync time
        const now = Date.now();
        await chrome.storage.local.set({ lastSync: now });
        document.getElementById('lastSyncText').textContent = formatTime(new Date(now));

        showStatus('✓ Performance data synced!', 'success');

    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
        console.error('Send performance error:', error);
    }
}

// ===== AUTO-SYNC TOGGLE =====
async function handleAutoSyncToggle(event) {
    const enabled = event.target.checked;

    try {
        await chrome.storage.local.set({ autoSync: enabled });
        showStatus(`Auto-sync ${enabled ? 'enabled' : 'disabled'}`, 'success');

        // Notify service worker
        chrome.runtime.sendMessage({
            type: 'AUTO_SYNC_TOGGLE',
            enabled
        });
    } catch (error) {
        showStatus('Failed to update auto-sync', 'error');
        console.error(error);
    }
}

// ===== HELPER FUNCTIONS =====

async function extractShopeeCookies() {
    try {
        const spc_ec = await chrome.cookies.get({
            url: 'https://shopee.co.id',
            name: 'SPC_EC'
        });

        const spc_f = await chrome.cookies.get({
            url: 'https://shopee.co.id',
            name: 'SPC_F'
        });

        return {
            SPC_EC: spc_ec?.value || '',
            SPC_F: spc_f?.value || ''
        };
    } catch (error) {
        console.error('Cookie extraction error:', error);
        return { SPC_EC: '', SPC_F: '' };
    }
}

// This function will be injected into the page
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

// Scrape Affiliate Dashboard
function scrapeAffiliateData() {
    try {
        // Basic scraping - adjust selectors based on actual page
        const data = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            type: 'affiliate_dashboard',
            accountId: 'affiliate_account',
            payload: {
                totalCommission: 0,
                totalOrders: 0,
                // Add more fields as needed
            }
        };

        return data;
    } catch (error) {
        console.error('Affiliate scrape error:', error);
        return null;
    }
}

// Scrape Live Streaming Data
function scrapeLiveData() {
    try {
        const data = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            type: 'live_streaming',
            accountId: 'live_account',
            payload: {
                revenue: 0,
                viewers: 0,
                duration: '0:00',
                // Add more fields as needed
            }
        };

        return data;
    } catch (error) {
        console.error('Live scrape error:', error);
        return null;
    }
}

// Scrape Seller Data
function scrapeSellerData() {
    try {
        const data = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            type: 'transactions',
            accountId: 'seller_account',
            payload: {
                transactions: [],
                // Add more fields as needed
            }
        };

        return data;
    } catch (error) {
        console.error('Seller scrape error:', error);
        return null;
    }
}

function showStatus(message, type) {
    const statusText = document.getElementById('statusText');
    statusText.textContent = message;

    // Update status text color based on type
    if (type === 'success') {
        statusText.style.color = '#10b981';
    } else if (type === 'error') {
        statusText.style.color = '#ef4444';
    } else {
        statusText.style.color = 'white';
    }

    // Auto-clear success messages
    if (type === 'success') {
        setTimeout(() => {
            statusText.textContent = 'Ready';
            statusText.style.color = 'white';
        }, 3000);
    }
}

function updateConnectionStatus(connected) {
    const badge = document.getElementById('connectionBadge');

    if (connected) {
        badge.textContent = '✓ Connected';
        badge.className = 'badge badge-success';
    } else {
        badge.textContent = '✗ Not Connected';
        badge.className = 'badge badge-error';
    }
}

function formatTime(date) {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;

    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}
