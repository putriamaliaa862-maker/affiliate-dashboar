/**
 * Creator Live Selectors - For scraping creator.shopee.co.id
 */

module.exports = {
    // Page URLs
    CREATOR_DASHBOARD: 'https://creator.shopee.co.id/live/dashboard',
    CREATOR_ORDERS: 'https://creator.shopee.co.id/portal/order/list',

    // Order counts
    ORDERS_READY_TO_SHIP: [
        '.order-tab-count[data-status="ready_to_ship"]',
        '[data-testid="order-count-ready"]',
        '.tab-item:contains("Siap Kirim") .count',
        'span:has-text("Siap Kirim") + span',
        '.order-status-count'
    ],

    PENDING_ORDERS: [
        '.order-tab-count[data-status="pending"]',
        '[data-testid="order-count-pending"]',
        '.tab-item:contains("Pending") .count'
    ],

    // Live session info
    LIVE_VIEWERS: [
        '.live-viewer-count',
        '[data-testid="viewer-count"]',
        '.viewer-number'
    ],

    LIVE_ORDERS: [
        '.live-order-count',
        '[data-testid="live-orders"]'
    ],

    // Login detection
    LOGIN_FORM: [
        'form[action*="login"]',
        'input[name="username"]',
        '.login-container'
    ]
};
