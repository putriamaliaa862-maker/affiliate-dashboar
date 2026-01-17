# Shopee Affiliate Scraper - Chrome Extension

Auto-sync your Shopee Live and Affiliate data to your custom dashboard!

## 🎯 Features

- ✅ **Auto-detect Shopee sessions** - No OAuth needed
- ✅ **Scrape live streaming data** - Viewers, sales, revenue in real-time
- ✅ **Extract transaction history** - Orders, commissions automatically
- ✅ **Background sync** - Set it and forget it
- ✅ **Multi-account support** - Install on multiple Chrome profiles
- ✅ **Customizable settings** - Configure API endpoint and sync intervals

## 📦 Installation

### Method 1: Load Unpacked (Development)

1. **Download** this repository as ZIP and extract
2. Open Chrome and go to `chrome://extensions/`
3. Enable **Developer mode** (top right toggle)
4. Click **Load unpacked**
5. Select the `shopee-scraper-extension` folder
6. Extension installed! ✓

### Method 2: From Release (Coming Soon)

1. Download `shopee-scraper-extension.zip` from Releases
2. Drag and drop the ZIP file to `chrome://extensions/`
3. Done!

## ⚙️ Configuration

1. Click the extension icon in your browser toolbar
2. Click **Settings** button
3. Configure:
   - **API Endpoint**: Your dashboard API URL (e.g., `http://localhost:8000/api`)
   - **Sync Interval**: How often to auto-sync (1-60 minutes)
   - **Auto-Sync**: Enable/disable automatic syncing
4. Click **Save Settings**

## 🚀 Usage

### Automatic Mode
1. Login to your Shopee account
2. Navigate to Shopee Live or Affiliate dashboard
3. Extension will automatically detect and scrape data
4. Data syncs to your dashboard in the background

### Manual Mode
1. Click extension icon
2. Click **Sync Now** button
3. Data immediately syncs to dashboard

## 📊 What Data is Scraped?

### Shopee Live
- Viewer count
- Total sales
- Revenue
- Product performance
- Stream duration

### Affiliate Dashboard
- Total commission
- Pending commission
- Paid commission
- Click count
- Conversion rate

### Transactions
- Order ID
- Amount
- Commission
- Status
- Date

## 🔒 Privacy & Security

- All data is sent directly to YOUR dashboard API
- No third-party servers involved
- Session tokens are stored locally in Chrome storage (encrypted)
- You control your own data

## 🛠️ Development

### File Structure
```
shopee-scraper-extension/
├── manifest.json           # Extension configuration
├── background/
│   └── service-worker.js  # Background process
├── content/
│   └── shopee-scraper.js  # Page scraper
├── popup/
│   ├── popup.html         # Extension popup UI
│   ├── popup.css
│   └── popup.js
├── options/
│   ├── options.html       # Settings page
│   └── options.js
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

### Build for Distribution
```bash
# Navigate to extension directory
cd shopee-scraper-extension

# Create ZIP file
# Windows:
powershell Compress-Archive -Path * -DestinationPath ../shopee-scraper-extension.zip

# Linux/Mac:
zip -r ../shopee-scraper-extension.zip *
```

## 🔧 Backend API Requirements

Your dashboard needs this endpoint:

**POST /api/shopee-data/sync**
```json
{
  "timestamp": "2024-01-15T06:30:00Z",
  "url": "https://live.shopee.co.id/...",
  "type": "live_streaming",
  "sessionToken": "user_token",
  "accountId": "account_id",
  "payload": {
    "viewers": 1234,
    "totalSales": 5000000,
    "revenue": 2500000
  }
}
```

## 📝 Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Auto-scrape Shopee Live data
- Auto-scrape transaction history
- Configurable sync intervals
- Manual sync button

## 🤝 Support

For issues or questions:
1. Check the logs in Chrome DevTools Console
2. Verify your API endpoint is correct
3. Ensure your dashboard is running
4. Check if you're logged into Shopee

## 📄 License

MIT License - Feel free to modify and distribute

---

Made with ❤️ for Shopee Affiliates
