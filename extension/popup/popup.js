// Popup Script v2.0 - FINAL
// Fixed: Direct storage save with verification
console.log('[Popup] Loaded');

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('[Popup] DOMContentLoaded');
    initUI();
    loadStatus();
    loadAccessCode();
    loadConnectionStatus();
});

function initUI() {
    document.getElementById('btnConnectSyncAll').addEventListener('click', handleConnectSyncAll);
    document.getElementById('btnManualSync').addEventListener('click', handleManualSync);
    document.getElementById('btnSaveCode').addEventListener('click', handleSaveAccessCode);
    document.getElementById('btnOpenSettings').addEventListener('click', () => {
        chrome.runtime.openOptionsPage();
    });
}

// ==================== LOAD FUNCTIONS ====================

function loadStatus() {
    chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
        console.log('[Popup] GET_STATUS response:', response);
        if (chrome.runtime.lastError) {
            console.error('[Popup] GET_STATUS error:', chrome.runtime.lastError);
            return;
        }
        if (response) {
            const statusDot = document.querySelector('.status-dot');
            const statusText = document.querySelector('.status-text');

            if (response.connected) {
                statusDot.classList.add('connected');
                statusText.textContent = 'Connected';
            } else {
                statusDot.classList.remove('connected');
                statusText.textContent = 'Not Connected';
            }

            document.getElementById('lastSync').textContent =
                response.lastSync ? formatDate(response.lastSync) : 'Never';
            document.getElementById('totalSynced').textContent = response.totalSynced || 0;
            document.getElementById('apiEndpoint').textContent = response.apiEndpoint || 'localhost:8000';
        }
    });
}

function loadAccessCode() {
    chrome.storage.local.get(['accessCode'], (result) => {
        console.log('[Popup] Access code loaded:', result.accessCode ? 'YES' : 'NO');
        const codeStatus = document.getElementById('codeStatus');
        const input = document.getElementById('accessCodeInput');

        if (result.accessCode) {
            codeStatus.textContent = '✓';
            codeStatus.className = 'code-status code-ok';
            input.value = result.accessCode;
        } else {
            codeStatus.textContent = '✗';
            codeStatus.className = 'code-status code-missing';
        }
    });
}

function loadConnectionStatus() {
    chrome.storage.local.get(['connected_identity'], (result) => {
        console.log('[Popup] Connection status:', result.connected_identity);
        const identity = result.connected_identity;
        const statusEl = document.getElementById('connStatus');
        const infoEl = document.getElementById('connectedInfo');

        if (identity && identity.shopee_account_id) {
            statusEl.className = 'status-badge status-connected';
            statusEl.textContent = `✅ Connected: ${identity.shop_name}`;
            infoEl.style.display = 'block';
            document.getElementById('connectedShopName').textContent = identity.shop_name || '-';
            document.getElementById('connectedAccountId').textContent = identity.shopee_account_id || '-';
        } else {
            statusEl.className = 'status-badge status-disconnected';
            statusEl.textContent = '⚠️ Not Connected';
            infoEl.style.display = 'none';
        }
    });
}

// ==================== CONNECT + SYNC ALL ====================

async function handleConnectSyncAll() {
    const btn = document.getElementById('btnConnectSyncAll');

    // Check access code first
    const storage = await getStorage(['accessCode']);
    if (!storage.accessCode) {
        showToast('❌ Set Access Code dulu!');
        return;
    }

    btn.disabled = true;
    btn.textContent = '⏳ Opening page...';

    try {
        // STEP 1: Open account_setting page
        console.log('[Popup] Step 1: Opening account_setting...');
        const tab = await new Promise((resolve, reject) => {
            chrome.tabs.create({
                url: 'https://affiliate.shopee.co.id/account_setting',
                active: true
            }, (tab) => {
                if (chrome.runtime.lastError) {
                    reject(new Error(chrome.runtime.lastError.message));
                } else {
                    resolve(tab);
                }
            });
        });

        console.log('[Popup] Tab created:', tab.id);

        // STEP 2: Wait for page to fully load
        btn.textContent = '⏳ Loading page...';
        await waitForTabLoad(tab.id);
        console.log('[Popup] Tab loaded');

        // Extra delay for dynamic content
        await sleep(2500);

        // STEP 3: Send CONNECT_ACCOUNT_SCRAPE message
        btn.textContent = '⏳ Extracting identity...';
        console.log('[Popup] Step 2: Sending CONNECT_ACCOUNT_SCRAPE...');

        const response = await new Promise((resolve) => {
            chrome.tabs.sendMessage(tab.id, { type: 'CONNECT_ACCOUNT_SCRAPE' }, (resp) => {
                if (chrome.runtime.lastError) {
                    console.error('[Popup] Message error:', chrome.runtime.lastError);
                    resolve({ success: false, error: chrome.runtime.lastError.message });
                } else {
                    resolve(resp || { success: false, error: 'No response' });
                }
            });
        });

        console.log('[Popup] CONNECT_ACCOUNT_SCRAPE response:', response);

        if (!response.success) {
            throw new Error(response.error || 'Failed to extract identity');
        }

        // Extract values (handle both field names)
        const accountId = response.shopee_account_id || response.account_id;
        const shopName = response.shop_name || accountId;
        const username = response.username || accountId;

        if (!accountId) {
            throw new Error('No account ID found on page');
        }

        console.log('[Popup] Extracted:', { accountId, shopName, username });

        // STEP 4: SAVE TO STORAGE DIRECTLY (CRITICAL!)
        btn.textContent = '⏳ Saving identity...';
        console.log('[Popup] Step 3: Saving to storage...');

        const identityData = {
            shopee_account_id: accountId,
            shop_name: shopName,
            username: username,
            connected_at: new Date().toISOString()
        };

        await setStorage({ connected_identity: identityData });
        console.log('[Popup] ✅ Saved to storage:', identityData);

        // STEP 5: VERIFY STORAGE (CRITICAL!)
        const verifyResult = await getStorage(['connected_identity']);
        console.log('[Popup] Storage verification:', verifyResult);

        if (!verifyResult.connected_identity || !verifyResult.connected_identity.shopee_account_id) {
            throw new Error('Storage verification failed - identity not saved');
        }

        // STEP 6: Sync identity to backend
        btn.textContent = '⏳ Syncing to backend...';
        console.log('[Popup] Step 4: Syncing to backend...');

        const syncResult = await new Promise((resolve) => {
            chrome.runtime.sendMessage({
                type: 'SYNC_IDENTITY',
                data: {
                    shopee_account_id: accountId,
                    shop_name: shopName,
                    username: username
                }
            }, (resp) => {
                if (chrome.runtime.lastError) {
                    resolve({ success: false, error: chrome.runtime.lastError.message });
                } else {
                    resolve(resp || { success: false });
                }
            });
        });

        console.log('[Popup] SYNC_IDENTITY result:', syncResult);

        if (!syncResult.success) {
            console.warn('[Popup] Backend sync failed, but identity is saved locally');
        }

        // STEP 7: Trigger SYNC_ALL
        btn.textContent = '⏳ Syncing all data...';
        console.log('[Popup] Step 5: Triggering SYNC_ALL...');

        chrome.runtime.sendMessage({ type: 'SYNC_ALL' });

        // SUCCESS!
        btn.disabled = false;
        btn.textContent = '🚀 Connect + Sync Semua';

        loadStatus();
        loadConnectionStatus();
        showToast(`✅ Connected: ${shopName}`);

    } catch (error) {
        console.error('[Popup] Connect + Sync failed:', error);
        btn.disabled = false;
        btn.textContent = '🚀 Connect + Sync Semua';
        showToast(`❌ ${error.message}`);
    }
}

// ==================== MANUAL SYNC ====================

async function handleManualSync() {
    const btn = document.getElementById('btnManualSync');

    // Check if connected
    const storage = await getStorage(['connected_identity', 'accessCode']);

    if (!storage.accessCode) {
        showToast('❌ Set Access Code dulu!');
        return;
    }

    if (!storage.connected_identity || !storage.connected_identity.shopee_account_id) {
        showToast('⚠️ Connect Account dulu!');
        return;
    }

    btn.disabled = true;
    btn.textContent = '⏳ Syncing...';

    chrome.runtime.sendMessage({ type: 'MANUAL_SYNC' }, (response) => {
        console.log('[Popup] MANUAL_SYNC response:', response);
        btn.disabled = false;
        btn.textContent = '🔄 Manual Sync';

        if (response && response.success) {
            showToast('✅ Sync berhasil!');
            loadStatus();
        } else {
            showToast(`❌ ${response?.error || 'Sync failed'}`);
        }
    });
}

// ==================== ACCESS CODE ====================

function handleSaveAccessCode() {
    const input = document.getElementById('accessCodeInput');
    const code = input.value.trim();

    if (!code) {
        showToast('❌ Access Code kosong!');
        return;
    }

    chrome.storage.local.set({ accessCode: code }, () => {
        console.log('[Popup] Access code saved');
        loadAccessCode();
        showToast('✅ Access Code saved!');
    });
}

// ==================== HELPERS ====================

function getStorage(keys) {
    return new Promise((resolve) => {
        chrome.storage.local.get(keys, resolve);
    });
}

function setStorage(data) {
    return new Promise((resolve) => {
        chrome.storage.local.set(data, resolve);
    });
}

function waitForTabLoad(tabId) {
    return new Promise((resolve) => {
        const listener = (id, info) => {
            if (id === tabId && info.status === 'complete') {
                chrome.tabs.onUpdated.removeListener(listener);
                resolve();
            }
        };
        chrome.tabs.onUpdated.addListener(listener);

        // Timeout after 30s
        setTimeout(() => {
            chrome.tabs.onUpdated.removeListener(listener);
            resolve();
        }, 30000);
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function formatDate(isoString) {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    return date.toLocaleString('id-ID', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showToast(message) {
    const toast = document.getElementById('toastMessage');
    toast.textContent = message;
    toast.style.display = 'block';

    toast.className = 'toast ' + (
        message.includes('✅') ? 'toast-success' :
            message.includes('❌') ? 'toast-error' : 'toast-warning'
    );

    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}

console.log('[Popup] ✅ Ready');
