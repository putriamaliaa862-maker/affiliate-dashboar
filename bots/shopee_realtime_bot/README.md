# Shopee Realtime Bot

24H Playwright bot untuk scraping data Shopee secara realtime.

## Features

- **Creator Live Dashboard**: Orders ready to ship, pending orders
- **Ads Center**: Spend today, budget available, coins
- **Multi-account**: Support 100+ accounts with batch processing
- **Persistent login**: Chrome profiles per account
- **Error recovery**: Auto-retry, screenshot on error
- **24H operation**: Continuous sync loop with 60s interval

## Setup

1. Install dependencies:
```bash
cd bots/shopee_realtime_bot
npm install
npx playwright install chromium
```

2. Configure accounts:
Edit `config/accounts.json`:
```json
[
  {
    "id": "account_1",
    "shopee_account_id": "affiliate_123456",
    "shop_name": "My Store",
    "enabled": true
  }
]
```

3. Set environment variables:
```bash
set ACCESS_CODE=your_access_code_here
set API_BASE=http://localhost:8000/api
set MAX_WORKERS=5
set SYNC_INTERVAL=60000
```

## Run

Start 24H bot:
```bash
npm start
# or
node supervisor.js
```

Test single account:
```bash
node worker.js
```

## Folder Structure

```
shopee_realtime_bot/
├── supervisor.js      # Main orchestrator
├── worker.js         # Single account scraper
├── config/
│   └── accounts.json # Account list
├── selectors/
│   ├── creator_live.js
│   └── ads_seller.js
├── lib/
│   ├── browser.js    # Playwright helpers
│   ├── logger.js     # File logging
│   └── uploader.js   # API client
├── logs/             # Daily log files
├── screenshots/      # Error screenshots
└── profiles/         # Chrome profiles
```

## Logs

Logs are written to `logs/bot_YYYY-MM-DD.log`

## Troubleshooting

1. **Login required**: Session expired. Login manually once via the browser profile.
2. **Selector not found**: Page structure changed. Update selectors/*.js
3. **API error**: Check ACCESS_CODE environment variable
