# SHOPEE LIVE STREAMING API REFERENCE - QUICK START

## 22 API Endpoints Summary

| # | Category | Endpoint | Method | Purpose |
|---|----------|----------|--------|---------|
| 1 | Auth | `/api/v2/authentication/gen_qrcode` | POST | Generate QR code |
| 2 | Auth | `/api/v2/authentication/qrcode_status` | GET | Check QR status |
| 3 | Auth | `/api/v2/authentication/qrcode_login` | POST | Login via QR |
| 4 | Creator | `/supply/api/lm/sellercenter/userInfo` | GET | Get creator user info |
| 5 | Creator | `/supply/api/lm/sellercenter/realtime/sessionList` | GET | List sessions (paginated) |
| 6 | Creator | `/supply/api/lm/sellercenter/realtime/dashboard/sessionInfo` | GET | Get session details |
| 7 | Creator | `/supply/api/lm/sellercenter/realtime/dashboard/overview` | GET | Get dashboard overview |
| 8 | Promotion | `/api/v4/streaming_promotion/streamer_selector/` | GET | Get streamer selectors |
| 9 | Promotion | `/app/pas/v1/live_stream/get_promotions_today/` | GET | Get today's promotions |
| 10 | Promotion | `/app/pas/v1/live_stream/edit/` | POST | Edit promotions |
| 11 | Items | `/api/v1/item/promotion` | GET | List promoted items |
| 12 | Items | `/api/v1/item/promotion/{promoId}` | GET | Get item details |
| 13 | Campaign | `/app/pas/v1/live_stream/get_campaign_expense_today/` | GET | Campaign expense today |
| 14 | Campaign | `/app/pas/v1/meta/get_ads_data/` | GET | Get ads data |
| 15 | Live | `/api/v1/shop_page/live/ongoing` | GET | Check shop live status |
| 16 | Share | Share link builder | GET | Generate share link |
| 17 | Product | Product URL builder | GET | Generate product URL |
| 18 | Coin | `/api/v1/session/{sessionId}/coin/start` | POST | Start coin distribution |
| 19 | Coin | `/api/v1/session/{sessionId}/coin/giveout` | POST | Give out coins |
| 20 | Coin | `/api/v1/session/{sessionId}/coin/rewardinfo` | GET | Get coin reward info |
| 21 | External | `https://undrctrl.id/api/v2/` | - | External API |
| 22 | Shop | Shop page URL builder | GET | Generate shop URL |

## Our Dashboard API Wrappers

All 22 endpoints are wrapped & integrated into FastAPI. Access via:

```
Base URL: http://localhost:8000/api/live-streaming
```

## Quick Integration Examples

### 1. Get Session List
```bash
curl -X POST http://localhost:8000/api/live-streaming/creator/session-list \
  -H "Content-Type: application/json" \
  -d '{"access_token":"your_token","page":1,"page_size":10}'
```

### 2. Sync Live Session Data
```bash
curl -X POST http://localhost:8000/api/live-streaming/sessions/sync \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"sess_123",
    "studio_id":1,
    "shopee_account_id":1,
    "access_token":"your_token"
  }'
```

### 3. Get Today Promotions
```bash
curl -X POST http://localhost:8000/api/live-streaming/promotions/today \
  -H "Content-Type: application/json" \
  -d '{"access_token":"your_token"}'
```

### 4. Get Campaign Expense
```bash
curl -X POST http://localhost:8000/api/live-streaming/campaign/expense-today \
  -H "Content-Type: application/json" \
  -d '{"access_token":"your_token"}'
```

### 5. Get Items/Products
```bash
curl -X POST http://localhost:8000/api/live-streaming/items/promotion \
  -H "Content-Type: application/json" \
  -d '{"access_token":"your_token","offset":0,"limit":50}'
```

### 6. Analytics Summary
```bash
curl -X GET "http://localhost:8000/api/live-streaming/analytics/summary?studio_id=1&days=30"
```

### 7. List Stored Sessions
```bash
curl -X GET "http://localhost:8000/api/live-streaming/sessions?studio_id=1&status=ongoing"
```

### 8. Get Share Link
```bash
curl -X GET "http://localhost:8000/api/live-streaming/share-link/sess_123"
```

## Core Workflows

### Workflow 1: Daily Sync
```
1. Get session list (API #5)
2. For each session:
   - Get session info (API #6)
   - Get dashboard overview (API #7)
   - Get items (API #11)
   - Store in database
3. Generate daily analytics
4. Create report
```

### Workflow 2: Real-Time Monitoring
```
1. Get ongoing sessions (API #15)
2. Stream metrics every 30s:
   - Viewer count
   - Order count
   - Revenue
   - Top products
3. Alert if metrics drop
```

### Workflow 3: Campaign Optimization
```
1. Get today promotions (API #9)
2. Get campaign expense (API #13)
3. Get ads data (API #14)
4. Calculate ROI
5. Suggest optimizations
6. Auto-pause underperforming campaigns
```

### Workflow 4: Engagement Boost
```
1. Get current viewers (API #6)
2. Start coin distribution (API #18)
3. Distribute coins periodically (API #19)
4. Track redemptions (API #20)
```

## Authentication Flow

### Step 1: Generate QR Code
```python
import httpx

async def get_qr_code():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://shopee.co.id/api/v2/authentication/gen_qrcode"
        )
        return resp.json()
```

### Step 2: Check QR Status
```python
async def check_qr(qrcode_id):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://shopee.co.id/api/v2/authentication/qrcode_status",
            params={"qrcode_id": qrcode_id}
        )
        return resp.json()
```

### Step 3: Login via QR
```python
async def login_qr(qrcode_id):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://shopee.co.id/api/v2/authentication/qrcode_login",
            json={"qrcode_id": qrcode_id}
        )
        data = resp.json()
        return {
            "access_token": data.get("access_token"),
            "shop_id": data.get("shop_id"),
            "user_id": data.get("user_id")
        }
```

## Data Models

### LiveSession
```python
{
  "id": 1,
  "studio_id": 1,
  "shopee_account_id": 1,
  "session_id": "sess_123",
  "session_name": "Flash Sale",
  "status": "ongoing",
  "total_viewers": 5000,
  "total_orders": 150,
  "total_revenue": 5000000,
  "total_comments": 1200,
  "total_likes": 800,
  "total_shares": 100,
  "campaign_id": "camp_1",
  "campaign_budget": 10000000,
  "campaign_spent": 3000000,
  "coins_distributed": 1000,
  "coin_total_value": 500000,
  "created_at": "2025-11-01T10:00:00Z"
}
```

### LiveAnalytics
```python
{
  "id": 1,
  "studio_id": 1,
  "date": "2025-11-01",
  "total_sessions": 5,
  "total_revenue": 50000000,
  "total_viewers": 50000,
  "average_order_value": 10000000,
  "conversion_rate": 0.15,
  "roi_percentage": 1.8,
  "total_ad_spend": 25000000,
  "total_commission": 5000000
}
```

## Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {
    "session_id": "sess_123",
    "total_viewers": 5000,
    ...
  },
  "timestamp": "2025-11-01T15:30:00Z"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Invalid access token",
  "code": "AUTH_ERROR",
  "timestamp": "2025-11-01T15:30:00Z"
}
```

## Best Practices

### 1. Token Management
- Store access token securely (database, not hardcoded)
- Refresh token before expiry
- Implement token rotation

### 2. Rate Limiting
- Shopee API may have rate limits
- Implement exponential backoff retry
- Add delay between consecutive requests (0.5-1 second)

### 3. Error Handling
```python
try:
    data = await get_session_info(session_id, token)
except TokenExpiredError:
    token = await refresh_token(old_token)
except RateLimitError:
    await asyncio.sleep(60)  # Wait 1 minute
except Exception as e:
    logger.error(f"API error: {e}")
    # Use cached data
```

### 4. Sync Strategy
- **Active sessions**: Sync every 5 minutes
- **Ended sessions**: Sync once, then archive
- **Analytics**: Daily aggregation
- **Reports**: Weekly/Monthly summary

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid access token` | Token expired | Refresh token |
| `Session not found` | Wrong session_id | Verify session still active |
| `Rate limit exceeded` | Too many requests | Add delay, use backoff |
| `Network timeout` | Connection issue | Increase timeout, retry |
| `400 Bad Request` | Invalid parameters | Check parameter format |
| `401 Unauthorized` | Auth failed | Re-login with QR code |
| `403 Forbidden` | Permission denied | Check partner credentials |
| `500 Server Error` | Shopee API issue | Wait & retry, check status |

## Performance Tips

### Optimization 1: Batch Requests
```python
# Instead of sequential
for session in sessions:
    data = await get_session_info(session_id, token)

# Use concurrent requests
import asyncio
tasks = [get_session_info(s, token) for s in sessions]
results = await asyncio.gather(*tasks)
```

### Optimization 2: Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedShopeeService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_cached_session(self, session_id, token):
        cache_key = f"{session_id}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return cached_data
        
        data = await self.get_session_info(session_id, token)
        self.cache[cache_key] = (data, datetime.now())
        return data
```

### Optimization 3: Database Indexing
```sql
-- Create indexes for faster queries
CREATE INDEX idx_live_sessions_studio ON live_sessions(studio_id);
CREATE INDEX idx_live_sessions_status ON live_sessions(status);
CREATE INDEX idx_live_sessions_created ON live_sessions(created_at);
CREATE INDEX idx_live_analytics_date ON live_analytics(date);
```

## Security Considerations

1. **Token Storage**: Use environment variables or secure vault
2. **API Keys**: Never commit to git
3. **HTTPS Only**: Always use HTTPS for API calls
4. **Input Validation**: Validate all user inputs
5. **Rate Limiting**: Implement rate limiting on your endpoints
6. **CORS**: Configure CORS properly for frontend

## Documentation Links

- Full Integration Guide: [SHOPEE_LIVE_INTEGRATION.md](./SHOPEE_LIVE_INTEGRATION.md)
- API Documentation: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- Deployment Guide: [DEPLOYMENT.md](./DEPLOYMENT.md)
- Troubleshooting: [INSTALLATION.md](./INSTALLATION.md)

---

**Status**: ✅ All 22 Shopee Live APIs Integrated & Production Ready 🚀
