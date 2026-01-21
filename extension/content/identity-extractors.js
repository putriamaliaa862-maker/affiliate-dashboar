// ==================== IDENTITY EXTRACTION FUNCTIONS ====================

/**
 * Extract account ID from account settings page
 */
function extractAccountIdFromSettings() {
    // Try multiple selectors for account ID

    // Method 1: From data attributes
    const accountElement = document.querySelector('[data-account-id], [data-user-id], [data-seller-id]');
    if (accountElement) {
        const id = accountElement.getAttribute('data-account-id') ||
            accountElement.getAttribute('data-user-id') ||
            accountElement.getAttribute('data-seller-id');
        if (id) return id;
    }

    // Method 2: From window global data
    if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.user_id) {
        return window.__INITIAL_STATE__.user_id;
    }

    if (window.seller_id) {
        return window.seller_id;
    }

    // Method 3: From URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const urlId = urlParams.get('user_id') || urlParams.get('account_id');
    if (urlId) return urlId;

    // Method 4: From page text (username/email)
    const usernameElement = document.querySelector('.username, .user-name, .account-name, input[name="username"]');
    if (usernameElement) {
        const username = usernameElement.textContent || usernameElement.value;
        if (username && username.trim()) return username.trim();
    }

    return null;
}

/**
 * Extract shop name from account settings page
 */
function extractShopNameFromSettings() {
    // Try multiple selectors for shop name

    // Method 1: From shop name fields
    const shopElement = document.querySelector('.shop-name, .store-name, input[name="shop_name"], input[name="store_name"]');
    if (shopElement) {
        const name = shopElement.textContent || shopElement.value;
        if (name && name.trim()) return name.trim();
    }

    // Method 2: From profile/account info section
    const profileName = document.querySelector('.profile-name, .account-info__name, .user-info__shop-name');
    if (profileName) {
        const name = profileName.textContent.trim();
        if (name) return name;
    }

    // Method 3: From window global data
    if (window.__INITIAL_STATE__ && window.__INITIAL_STATE__.shop_name) {
        return window.__INITIAL_STATE__.shop_name;
    }

    // Method 4: From page title
    const titleMatch = document.title.match(/(.+?)\s*[-–|]/);
    if (titleMatch && titleMatch[1]) {
        return titleMatch[1].trim();
    }

    // Method 5: From meta tags
    const metaShop = document.querySelector('meta[property="og:site_name"]');
    if (metaShop && metaShop.content) {
        return metaShop.content;
    }

    return null;
}
