// Content Script - Runs on Shopee pages
// Updated: Smart 1x/day sync for Live Products
console.log('Shopee Scraper: Content script loaded');

// Listen for scrape requests from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SCRAPE_NOW') {
        scrapeShopeeData(message.isManual || false);
        sendResponse({ success: true });
    }
});

// Auto-scrape when page loads (if on relevant pages)
if (window.location.href.includes('live.shopee.co.id') ||
    window.location.href.includes('affiliate') ||
    window.location.href.includes('seller.shopee.co.id')) {
    setTimeout(() => scrapeShopeeData(false), 3000); // Wait for page to load
}

function scrapeShopeeData(isManual = false) {
    console.log('Shopee Scraper: Starting scrape...', { isManual });

    const data = {
        timestamp: new Date().toISOString(),
        url: window.location.href,
        type: detectPageType(),
        payload: {}
    };

    // Extract cookies/session
    data.sessionToken = extractSessionToken();
    data.accountId = extractAccountId();

    // Scrape based on page type
    switch (data.type) {
        case 'live_streaming':
            data.payload = scrapeLiveStreamingData();
            break;
        case 'live_products':
            // NEW: Scrape live products page
            scrapeLiveProductsPage(data.accountId, isManual);
            return; // Handled separately
        case 'affiliate_dashboard':
            data.payload = scrapeAffiliateDashboard();
            break;
        case 'transactions':
            data.payload = scrapeTransactions();
            break;
        default:
            console.log('Shopee Scraper: Unknown page type');
            return;
    }

    // Send to background script (old flow)
    chrome.runtime.sendMessage({
        type: 'SHOPEE_DATA',
        data: data
    }, (response) => {
        if (response && response.success) {
            console.log('Shopee Scraper: Data synced successfully');
            showNotification('✓ Data synced to dashboard');
        } else {
            console.error('Shopee Scraper: Sync failed');
            showNotification('✗ Sync failed');
        }
    });
}

function detectPageType() {
    const url = window.location.href;
    if (url.includes('live.shopee.co.id')) return 'live_streaming';
    if (url.includes('seller.shopee.co.id/portal/product/list')) return 'live_products';
    if (url.includes('affiliate')) return 'affiliate_dashboard';
    if (url.includes('/user/purchase')) return 'transactions';
    return 'unknown';
}

// NEW: Scrape Live Products page and sync (with 1x/day logic)
function scrapeLiveProductsPage(accountId, isManual) {
    console.log('Scraping Live Products page...', { accountId, isManual });

    // Extract account ID from page if not provided
    if (!accountId || accountId === 'unknown') {
        accountId = extractAccountIdFromPage();
    }

    // Check if we should sync today (only for auto sync)
    if (!isManual) {
        chrome.runtime.sendMessage({
            type: 'CHECK_SHOULD_SYNC_TODAY',
            accountId: accountId
        }, (response) => {
            if (!response.shouldSync) {
                console.log(`Already synced today for account ${accountId}. Last sync: ${response.lastSyncDate}`);
                showNotification('⏭️ Sudah sync hari ini');
                return;
            }

            // Should sync, proceed
            performLiveProductsSync(accountId, isManual);
        });
    } else {
        // Manual sync: always proceed
        performLiveProductsSync(accountId, isManual);
    }
}

function performLiveProductsSync(accountId, isManual) {
    const products = scrapeProductsFromPage();

    if (products.length === 0) {
        console.warn('No products found on page');
        showNotification('⚠️ Tidak ada produk ditemukan');
        return;
    }

    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD

    const syncData = {
        account_id: parseInt(accountId) || 1, // Fallback to 1 if parsing fails
        snapshot_date: today,
        source: 'extension',
        products: products,
        raw_data: {
            url: window.location.href,
            scrapedAt: new Date().toISOString(),
            userAgent: navigator.userAgent
        }
    };

    console.log('Sending Live Products sync:', syncData);

    // Send to background for API sync
    chrome.runtime.sendMessage({
        type: 'LIVE_PRODUCTS_SYNC',
        data: syncData,
        isManual: isManual
    }, (response) => {
        if (response && response.success) {
            console.log('Live Products sync successful:', response.result);
            showNotification(`✓ Sync ${products.length} produk berhasil!`);
        } else {
            console.error('Live Products sync failed:', response?.error);
            showNotification(`✗ Sync gagal: ${response?.error || 'Unknown error'}`);
        }
    });
}

// Extract products from Shopee Seller page
function scrapeProductsFromPage() {
    const products = [];

    // Try multiple selectors (Shopee seller page structure varies)
    const productRows = document.querySelectorAll('.product-list-item, .product-row, tr[data-product-id]');

    productRows.forEach((row, index) => {
        try {
            const productId = extractProductId(row);
            const productName = extractProductName(row);
            const soldQty = extractSoldQty(row);
            const gmv = extractGMV(row);
            const clicks = extractClicks(row);

            if (productId && productName) {
                products.push({
                    product_id: productId,
                    product_name: productName,
                    sold_qty: soldQty,
                    gmv: gmv,
                    clicks: clicks
                });
            }
        } catch (error) {
            console.error(`Error scraping product at index ${index}:`, error);
        }
    });

    console.log(`Scraped ${products.length} products`);
    return products;
}

function extractProductId(row) {
    // Try multiple methods to get product ID
    const dataAttr = row.getAttribute('data-product-id') || row.getAttribute('data-id');
    if (dataAttr) return dataAttr;

    const idElement = row.querySelector('[data-product-id], .product-id');
    if (idElement) {
        return idElement.getAttribute('data-product-id') || idElement.textContent.trim();
    }

    return `product_${Date.now()}_${Math.random().toString(36).substring(7)}`;
}

function extractProductName(row) {
    const nameElement = row.querySelector('.product-name, .product-title, .item-name, td:nth-child(2)');
    return nameElement ? nameElement.textContent.trim() : 'Unknown Product';
}

function extractSoldQty(row) {
    const soldElement = row.querySelector('.sold-qty, .product-sold, [data-sold]');
    if (soldElement) {
        const text = soldElement.textContent.trim().replace(/[^0-9]/g, '');
        return parseInt(text) || 0;
    }
    return 0;
}

function extractGMV(row) {
    const gmvElement = row.querySelector('.gmv, .revenue, .product-revenue, [data-gmv]');
    if (gmvElement) {
        const text = gmvElement.textContent.trim().replace(/[^0-9.]/g, '');
        return parseFloat(text) || 0;
    }
    // Fallback: calculate from price * sold
    const priceElement = row.querySelector('.price, .product-price');
    const soldElement = row.querySelector('.sold-qty, .product-sold');
    if (priceElement && soldElement) {
        const price = parseFloat(priceElement.textContent.trim().replace(/[^0-9.]/g, '')) || 0;
        const sold = parseInt(soldElement.textContent.trim().replace(/[^0-9]/g, '')) || 0;
        return price * sold;
    }
    return 0;
}

function extractClicks(row) {
    const clicksElement = row.querySelector('.clicks, .views, .product-views');
    if (clicksElement) {
        const text = clicksElement.textContent.trim().replace(/[^0-9]/g, '');
        return parseInt(text) || 0;
    }
    return 0;
}

function extractAccountIdFromPage() {
    // Try to extract from URL, page data, or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const urlAccountId = urlParams.get('shop_id') || urlParams.get('account_id');
    if (urlAccountId) return urlAccountId;

    // Try localStorage
    const storedAccountId = localStorage.getItem('shopee_account_id');
    if (storedAccountId) return storedAccountId;

    return '1'; // Fallback
}

function extractSessionToken() {
    // Extract from cookies or localStorage
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'SPC_EC' || name === 'SPC_F') {
            return value;
        }
    }
    return localStorage.getItem('token') || null;
}

function extractAccountId() {
    // Try to get account ID from page
    const accountElement = document.querySelector('[data-account-id]');
    if (accountElement) {
        return accountElement.getAttribute('data-account-id');
    }

    // Fallback: extract from URL or username
    const usernameElement = document.querySelector('.navbar__username');
    return usernameElement ? usernameElement.textContent.trim() : 'unknown';
}

function scrapeLiveStreamingData() {
    return {
        viewers: extractNumber('.live-viewer-count'),
        likes: extractNumber('.like-count'),
        totalSales: extractNumber('.total-sales'),
        revenue: extractNumber('.revenue-amount'),
        products: scrapeProductsList(),
        duration: extractDuration()
    };
}

function scrapeAffiliateDashboard() {
    return {
        totalCommission: extractNumber('.total-commission'),
        pendingCommission: extractNumber('.pending-commission'),
        paidCommission: extractNumber('.paid-commission'),
        clicks: extractNumber('.total-clicks'),
        conversions: extractNumber('.total-conversions')
    };
}

function scrapeTransactions() {
    const transactions = [];
    document.querySelectorAll('.order-item').forEach(item => {
        transactions.push({
            orderId: item.querySelector('.order-id')?.textContent.trim(),
            amount: extractNumber('.order-amount', item),
            commission: extractNumber('.commission-amount', item),
            status: item.querySelector('.order-status')?.textContent.trim(),
            date: item.querySelector('.order-date')?.textContent.trim()
        });
    });
    return { transactions };
}

function scrapeProductsList() {
    const products = [];
    document.querySelectorAll('.product-item').forEach(item => {
        products.push({
            name: item.querySelector('.product-name')?.textContent.trim(),
            price: extractNumber('.product-price', item),
            sold: extractNumber('.product-sold', item)
        });
    });
    return products;
}

// Utility functions
function extractNumber(selector, parent = document) {
    const element = parent.querySelector(selector);
    if (!element) return 0;
    const text = element.textContent.trim().replace(/[^0-9.]/g, '');
    return parseFloat(text) || 0;
}

function extractDuration() {
    const durationElement = document.querySelector('.live-duration');
    return durationElement ? durationElement.textContent.trim() : '0:00';
}

function showNotification(message) {
    // Create a small notification div
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${message.includes('✓') ? '#4CAF50' : message.includes('✗') ? '#F44336' : '#2196F3'};
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    z-index: 999999;
    font-size: 14px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    animation: slideIn 0.3s ease;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
