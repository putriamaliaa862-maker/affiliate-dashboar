# ✅ User Acceptance Testing (UAT) Checklist
**Version**: 1.0.0
**Date**: 2026-01-16

---

## 👥 1. User Management (Admin Only)
- [ ] **Login**: Admin can login with valid credentials.
- [ ] **Create User**: Can create new 'Leader' and 'Affiliate' users.
- [ ] **Edit User**: Can update username/role.
- [ ] **Delete User**: Can delete user (soft delete/hard delete check).
- [ ] **RBAC**: A 'Leader' cannot access the Users page.

## 🏢 2. Employee & Attendance
- [ ] **Create Employee**: Add new employee with role 'Host'.
- [ ] **Check In**: Record attendance for today.
- [ ] **Duplicate Check**: Try checking in same employee twice (Expect Error).
- [ ] **View List**: Attendance list shows correct timestamps.

## 📊 3. Reports & Analytics
- [ ] **Generate Report**: Select Date Range + Shop -> Click Generate.
- [ ] **Data Accuracy**: Compare numbers with raw Shopee CSV if available.
- [ ] **Export CSV**: Download report as CSV.
- [ ] **Daily Summary**: Owner can see formatted KPI cards.

## 💰 4. Commissions & Bonus
- [ ] **Import Data**: Upload valid Shopee CSV -> Verify Success message.
- [ ] **View Commissions**: Data appears in Commissions table.
- [ ] **Mark Paid**: Select account -> Mark as paid -> Status updates.
- [ ] **Shift Bonus**: Check if bonus auto-calculates based on shift rules.

## ⚡ 5. Performance & Security
- [ ] **Speed**: Pages load under 2 seconds.
- [ ] **HTTPS**: Browser shows "Secure" padlock.
- [ ] **Session**: Logout works, back button doesn't reveal protected pages.

## 📝 Sign-off
**Tester Name**: _______________________
**Date**: ___________
**Result**: PASS / FAIL
