/**
 * Ads Seller Selectors - For scraping seller.shopee.co.id ads center
 */

module.exports = {
    // Page URLs
    ADS_CENTER: 'https://seller.shopee.co.id/portal/marketing/pas',
    ADS_BALANCE: 'https://seller.shopee.co.id/portal/marketing/pas/balance',

    // Spend today
    SPEND_TODAY: [
        '.spend-today-value',
        '[data-testid="spend-today"]',
        '.ads-spend .amount',
        '.today-spend-amount',
        'span:has-text("Pengeluaran Hari Ini") + span'
    ],

    // Budget / Balance
    BUDGET_AVAILABLE: [
        '.budget-value',
        '[data-testid="budget-available"]',
        '.ads-balance .amount',
        '.balance-amount',
        'span:has-text("Saldo Iklan") + span'
    ],

    // Coins
    COINS_BALANCE: [
        '.coins-balance',
        '[data-testid="coins"]',
        '.shopee-coins .amount',
        'span:has-text("Koin") + span'
    ],

    // Campaign stats
    ACTIVE_CAMPAIGNS: [
        '.campaign-count-active',
        '[data-testid="active-campaigns"]'
    ],

    // ROAS
    ROAS_VALUE: [
        '.roas-value',
        '[data-testid="roas"]',
        '.roas-percentage'
    ],

    // Login detection
    LOGIN_REQUIRED: [
        '.login-modal',
        '[data-testid="login-prompt"]',
        'button:has-text("Login")'
    ]
};
