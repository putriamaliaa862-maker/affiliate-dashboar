"""
Verify data in database after sync
"""
from app.database import SessionLocal
from app.models.shopee_account import ShopeeAccount
from app.models.order import Order
from app.models.ads import AdsDailyMetrics, AdsDailySpend

db = SessionLocal()

print("🔍 Verifying Database After Sync\n")
print("="*60)

# Check account
print("\n1️⃣ Checking ShopeeAccount...")
account = db.query(ShopeeAccount).filter(
    ShopeeAccount.account_name == "YEYEP STORE"
).first()

if account:
    print(f"   ✅ Account found: {account.account_name}")
    print(f"      ID: {account.id}")
    print(f"      Shopee Account ID: {account.shopee_account_id}")
    print(f"      Active: {account.is_active}")
else:
    print("   ❌ Account not found!")

# Check orders
print("\n2️⃣ Checking Orders...")
if account:
    orders = db.query(Order).filter(
        Order.shopee_account_id == account.id
    ).all()
    
    print(f"   ✅ Found {len(orders)} orders")
    for order in orders:
        print(f"      - {order.order_id}: GMV={order.total_amount}, Commission={order.commission_amount}")
else:
    print("   ⚠️ Skipped (no account)")

# Check metrics
print("\n3️⃣ Checking AdsDailyMetrics...")
if account:
    metrics = db.query(AdsDailyMetrics).filter(
        AdsDailyMetrics.shopee_account_id == account.id
    ).all()
    
    print(f"   ✅ Found {len(metrics)} metrics records")
    for m in metrics:
        print(f"      - {m.date}: Revenue={m.revenue_manual}, ROAS={m.roas_manual}")
else:
    print("   ⚠️ Skipped (no account)")

# Check spend
print("\n4️⃣ Checking AdsDailySpend...")
if account:
    spends = db.query(AdsDailySpend).filter(
        AdsDailySpend.shopee_account_id == account.id
    ).all()
    
    print(f"   ✅ Found {len(spends)} spend records")
    for s in spends:
        print(f"      - {s.date} ({s.spend_type}): {s.spend_amount}")
else:
    print("   ⚠️ Skipped (no account)")

print("\n" + "="*60)
print("✅ Database verification complete!")

db.close()
