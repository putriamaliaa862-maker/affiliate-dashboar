// Content Script v2.0
console.log('[CS] Loaded:', window.location.href);

function getStorage(keys) {
    return new Promise(r => chrome.storage.local.get(keys, r));
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    console.log('[CS] Msg:', msg.type);

    if (msg.type === 'PING') {
        sendResponse({ success: true });
        return true;
    }

    if (msg.type === 'CONNECT_ACCOUNT_SCRAPE') {
        if (!window.location.href.includes('affiliate.shopee.co.id/account_setting')) {
            sendResponse({ success: false, error: 'Wrong page' });
            return true;
        }

        const accountId = extractAccountId();
        const shopName = extractShopName();
        console.log('[CS] Extracted:', { accountId, shopName });

        if (accountId) {
            sendResponse({ success: true, shopee_account_id: accountId, account_id: accountId, shop_name: shopName || accountId, username: accountId });
        } else {
            sendResponse({ success: false, error: 'Could not find account ID' });
        }
        return true;
    }

    if (msg.type === 'SCRAPE_NOW') {
        doScrape(msg.isManual || false);
        sendResponse({ success: true });
        return true;
    }
});

const url = window.location.href;
if (!url.includes('account_setting') && (url.includes('live.shopee') || url.includes('creator.shopee') || url.includes('affiliate.shopee/dashboard'))) {
    setTimeout(() => doScrape(false), 3000);
}

async function doScrape(isManual) {
    console.log('[CS] Scraping...');
    const storage = await getStorage(['connected_identity']);
    const identity = storage.connected_identity;

    if (!identity || !identity.shopee_account_id) {
        console.error('[CS] NOT CONNECTED');
        showToast('⚠️ Connect Account dulu!');
        return;
    }

    const accountId = identity.shopee_account_id;
    const shopName = identity.shop_name || accountId;
    console.log('[CS] Using:', shopName, accountId);

    const pageType = detectPageType();
    let data = {};

    if (pageType === 'live_streaming') data = { viewers: extractNum('.viewer-count'), likes: extractNum('.like-count') };
    else if (pageType === 'affiliate_dashboard') data = { clicks: extractNum('[class*="click"]'), orders: extractNum('[class*="order"]') };
    else return;

    const payload = { account: { shopee_account_id: accountId, shop_name: shopName, username: accountId }, type: pageType, data, url: window.location.href };
    console.log('[CS] Payload:', payload);

    chrome.runtime.sendMessage({ type: 'SHOPEE_DATA', data: payload }, resp => {
        if (resp?.success) showToast('✓ Synced');
        else showToast('✗ Failed');
    });
}

function detectPageType() {
    const u = window.location.href;
    if (u.includes('live.shopee') || u.includes('creator.shopee.co.id/dashboard/live')) return 'live_streaming';
    if (u.includes('affiliate.shopee')) return 'affiliate_dashboard';
    return 'unknown';
}

function extractAccountId() {
    const text = document.body.innerText;
    let m = text.match(/ID\s*Affiliate[:\s]*(\d+)/i);
    if (m) return `affiliate_${m[1]}`;
    m = text.match(/User\s*ID[:\s]*(\d+)/i);
    if (m) return m[1];
    m = text.match(/Username[:\s]*([a-zA-Z0-9_]+)/i);
    if (m) return m[1];
    return null;
}

function extractShopName() {
    const text = document.body.innerText;
    let m = text.match(/Nama[:\s]*([^\n]+)/i);
    if (m && m[1].trim().length > 1) return m[1].trim();
    const title = document.title.match(/(.+?)\s*[-–|]/);
    if (title) return title[1].trim();
    return null;
}

function extractNum(sel) {
    const el = document.querySelector(sel);
    return el ? parseFloat(el.textContent.replace(/[^0-9.]/g, '')) || 0 : 0;
}

function showToast(msg) {
    const el = document.createElement('div');
    el.textContent = msg;
    el.style.cssText = 'position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:8px;color:white;z-index:999999;background:' + (msg.includes('✓') ? '#28a745' : '#ffc107');
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

console.log('[CS] Ready');
