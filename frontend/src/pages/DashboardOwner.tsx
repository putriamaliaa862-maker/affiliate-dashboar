import React, { useState, useEffect } from 'react'
import {
    Crown, RefreshCw, Calendar, AlertTriangle,
    TrendingUp, TrendingDown, DollarSign, ShoppingCart,
    BarChart3, Target, Zap, Users, Clock, Award,
    AlertCircle, CheckCircle, XCircle
} from 'lucide-react'
import api from '@/api/client'
import { useAuth } from '@/hooks/useAuth'
import premiumApi, { PremiumDashboardData } from '@/api/premium'
import {
    RealtimePerformanceChart,
    TopPerformersWidget,
    AlertCenter,
    FinancialSummary,
    QuickActionsDashboard
} from '@/components/premium/PremiumFeatures'

// Types
interface SyncStatus {
    status: 'LIVE' | 'DELAY' | 'PUTUS'
    last_update: string
    delay_minutes: number
}

interface KPI {
    gmv_today: number
    orders_today: number
    commission_net: number
    ads_spend_total: number
    roas_today: number
    profit_estimate: number
    bonus_host_today: number
    audience_balance: number | null
}

interface AccountRank {
    account_id: number
    account_name: string
    gmv: number
    orders: number
    commission: number
    spend: number
    roas: number
    status: 'AMAN' | 'WASPADA' | 'BOROS'
}

interface OrderHour {
    hour: string
    orders: number
}

interface ShiftScore {
    shift_name: string
    total_gmv: number
    total_orders: number
    mvp_host: string
    mvp_gmv: number
}

interface ProductDrop {
    product_name: string
    yesterday_orders: number
    today_orders: number
    drop_percent: number
}

interface ProfitHunter {
    product_name: string
    total_commission: number
    orders: number
}

interface RiskDetector {
    top_account_dependency: number
    account_name: string
    is_risky: boolean
}

interface BorosDetector {
    threshold: number
    boros_accounts: string[]
}

interface WeakShift {
    shift_name: string
    gmv: number
    target: number
    gap_percent: number
    recommendation: string
}

interface Alert {
    level: 'critical' | 'warning' | 'info'
    message: string
    action: string
}

interface OwnerDashboardData {
    sync_status: SyncStatus
    kpi: KPI
    war_room: {
        account_ranking: AccountRank[]
        orders_per_hour: OrderHour[]
        shift_scoreboard: ShiftScore[]
    }
    insights: {
        product_drops: ProductDrop[]
        profit_hunters: ProfitHunter[]
        risk_detector: RiskDetector
        boros_detector: BorosDetector
        weak_shifts: WeakShift[]
    }
    alerts: Alert[]
}

const DashboardOwner: React.FC = () => {
    const { user } = useAuth()
    const [data, setData] = useState<OwnerDashboardData | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    // Filters
    const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0])
    const [selectedAccountId, setSelectedAccountId] = useState<string>('all')
    const [accounts, setAccounts] = useState<any[]>([])
    const [alertsEnabled, setAlertsEnabled] = useState(true)

    // Premium features data
    const [premiumData, setPremiumData] = useState<PremiumDashboardData | null>(null)
    const [_loadingPremium, setLoadingPremium] = useState(false)

    // Check if user can access premium features
    const isPremiumUser = user && ['owner', 'super_admin', 'supervisor'].includes(user.role.toLowerCase().replace(' ', '_'))

    // Fetch accounts for filter
    useEffect(() => {
        const fetchAccounts = async () => {
            try {
                const res = await api.get('/shopee-accounts')
                setAccounts(res.data)
            } catch (err) {
                console.error('Failed to load accounts', err)
            }
        }
        fetchAccounts()
    }, [])

    // Fetch owner dashboard data
    const fetchData = async () => {
        setLoading(true)
        setError(null)
        try {
            const params: any = { date }
            if (selectedAccountId !== 'all') {
                params.account_id = selectedAccountId
            }

            const res = await api.get('/dashboard/owner', { params })
            setData(res.data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Gagal load data owner dashboard')
            console.error('Owner dashboard error:', err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
        if (isPremiumUser) {
            fetchPremiumData()
        }
    }, [date, selectedAccountId])

    // Fetch premium dashboard data
    const fetchPremiumData = async () => {
        setLoadingPremium(true)
        try {
            const accId = selectedAccountId !== 'all' ? parseInt(selectedAccountId) : undefined
            const premium = await premiumApi.getPremiumDashboard(date, accId)
            setPremiumData(premium)
        } catch (err) {
            console.error('Failed to load premium data:', err)
        } finally {
            setLoadingPremium(false)
        }
    }

    if (loading && !data) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <RefreshCw className="animate-spin mx-auto mb-4 text-blue-600" size={48} />
                    <p className="text-slate-600 text-lg">Loading Owner Dashboard...</p>
                </div>
            </div>
        )
    }

    if (error && !data) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center max-w-md">
                    <AlertCircle className="mx-auto mb-4 text-red-600" size={48} />
                    <p className="text-red-600 text-lg font-semibold mb-2">Error Loading Dashboard</p>
                    <p className="text-slate-600 mb-4">{error}</p>
                    <button
                        onClick={fetchData}
                        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Retry
                    </button>
                </div>
            </div>
        )
    }

    if (!data) return null

    const { sync_status, kpi, war_room, insights, alerts } = data

    return (
        <div className="space-y-6 pb-20">
            {/* STICKY CONTROL BAR */}
            <div className="sticky top-0 z-10 bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 rounded-xl shadow-lg">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <Crown size={32} className="text-yellow-300" />
                        <div>
                            <h1 className="text-2xl font-bold">👑 Owner Mode</h1>
                            <p className="text-sm text-purple-100">Dashboard Premium - Pantau bisnis realtime</p>
                        </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-3">
                        {/* Sync Status */}
                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-bold text-sm ${sync_status.status === 'LIVE' ? 'bg-green-500' :
                            sync_status.status === 'DELAY' ? 'bg-yellow-500' : 'bg-red-500'
                            }`}>
                            {sync_status.status === 'LIVE' && <CheckCircle size={16} />}
                            {sync_status.status === 'DELAY' && <Clock size={16} />}
                            {sync_status.status === 'PUTUS' && <XCircle size={16} />}
                            {sync_status.status}
                        </div>

                        {/* Last Update */}
                        <div className="text-xs text-purple-100">
                            Update: {new Date(sync_status.last_update).toLocaleTimeString('id-ID')}
                        </div>

                        {/* Date Filter */}
                        <div className="relative">
                            <Calendar className="absolute left-2 top-2 text-slate-400" size={16} />
                            <input
                                type="date"
                                value={date}
                                onChange={(e) => setDate(e.target.value)}
                                className="pl-8 pr-3 py-1.5 border border-white/30 rounded-lg bg-white/10 text-white text-sm focus:ring-2 focus:ring-white/50 outline-none"
                            />
                        </div>

                        {/* Account Filter */}
                        <select
                            value={selectedAccountId}
                            onChange={(e) => setSelectedAccountId(e.target.value)}
                            className="px-3 py-1.5 border border-white/30 rounded-lg bg-white/10 text-white text-sm focus:ring-2 focus:ring-white/50 outline-none"
                        >
                            <option value="all">Semua Akun</option>
                            {accounts.map(acc => (
                                <option key={acc.id} value={acc.id}>{acc.account_name}</option>
                            ))}
                        </select>

                        {/* Alert Toggle */}
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={alertsEnabled}
                                onChange={(e) => setAlertsEnabled(e.target.checked)}
                                className="w-4 h-4"
                            />
                            <span className="text-sm">Alert Keras</span>
                        </label>

                        {/* Refresh Button */}
                        <button
                            onClick={fetchData}
                            className="flex items-center gap-2 px-4 py-1.5 bg-white/20 hover:bg-white/30 rounded-lg transition-colors font-medium text-sm"
                        >
                            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                            Refresh
                        </button>
                    </div>
                </div>
            </div>

            {/* KPI OWNER CARDS (8 cards) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <KPICard
                    title="GMV Hari Ini"
                    value={`Rp ${kpi.gmv_today.toLocaleString('id-ID')}`}
                    icon={<DollarSign />}
                    color="bg-green-500"
                    trend={kpi.gmv_today > 0 ? 'up' : 'neutral'}
                />
                <KPICard
                    title="Orders Hari Ini"
                    value={kpi.orders_today.toString()}
                    icon={<ShoppingCart />}
                    color="bg-blue-500"
                    trend={kpi.orders_today > 0 ? 'up' : 'neutral'}
                />
                <KPICard
                    title="Komisi Bersih"
                    value={`Rp ${kpi.commission_net.toLocaleString('id-ID')}`}
                    icon={<Target />}
                    color="bg-purple-500"
                    trend={kpi.commission_net > 0 ? 'up' : 'neutral'}
                />
                <KPICard
                    title="Ads Spend Total"
                    value={`Rp ${kpi.ads_spend_total.toLocaleString('id-ID')}`}
                    icon={<Zap />}
                    color="bg-red-500"
                    trend="neutral"
                />
                <KPICard
                    title="ROAS Hari Ini"
                    value={`${kpi.roas_today.toFixed(2)}x`}
                    icon={<BarChart3 />}
                    color={kpi.roas_today >= 8 ? 'bg-green-500' : kpi.roas_today >= 5 ? 'bg-yellow-500' : 'bg-red-500'}
                    trend={kpi.roas_today >= 5 ? 'up' : 'down'}
                />
                <KPICard
                    title="Profit Estimasi"
                    value={`Rp ${kpi.profit_estimate.toLocaleString('id-ID')}`}
                    icon={<TrendingUp />}
                    color={kpi.profit_estimate > 0 ? 'bg-green-500' : 'bg-red-500'}
                    trend={kpi.profit_estimate > 0 ? 'up' : 'down'}
                />
                <KPICard
                    title="Bonus Host Hari Ini"
                    value={kpi.bonus_host_today > 0 ? `Rp ${kpi.bonus_host_today.toLocaleString('id-ID')}` : 'Belum ada'}
                    icon={<Award />}
                    color="bg-amber-500"
                    trend="neutral"
                />
                <KPICard
                    title="Saldo Iklan Penonton"
                    value={kpi.audience_balance !== null ? `Rp ${kpi.audience_balance.toLocaleString('id-ID')}` : 'Manual input'}
                    icon={<Users />}
                    color="bg-indigo-500"
                    trend="neutral"
                />
            </div>

            {/* OWNER ALERT CENTER */}
            {alertsEnabled && alerts.length > 0 && (
                <div className="bg-gradient-to-r from-red-50 to-orange-50 border-l-4 border-red-500 p-4 rounded-lg">
                    <div className="flex items-start gap-3">
                        <AlertTriangle className="text-red-600 flex-shrink-0" size={24} />
                        <div className="flex-1">
                            <h3 className="font-bold text-red-900 mb-2">🚨 Owner Alert Center</h3>
                            <div className="space-y-2">
                                {alerts.map((alert, idx) => (
                                    <div key={idx} className={`p-3 rounded-lg ${alert.level === 'critical' ? 'bg-red-100 border border-red-300' :
                                        alert.level === 'warning' ? 'bg-yellow-100 border border-yellow-300' :
                                            'bg-blue-100 border border-blue-300'
                                        }`}>
                                        <p className="font-semibold text-sm">{alert.message}</p>
                                        <p className="text-xs text-slate-600 mt-1">💡 Aksi: {alert.action}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* PREMIUM FEATURES - Owner/Super Admin/Supervisor Only */}
            {isPremiumUser && premiumData && (
                <>
                    {/* Quick Actions */}
                    <QuickActionsDashboard userRole={user?.role || ''} />

                    {/* Realtime Performance Chart */}
                    <RealtimePerformanceChart data={premiumData.hourly_performance} />

                    {/* Top Performers */}
                    <TopPerformersWidget
                        accounts={premiumData.top_performers.accounts}
                        hosts={premiumData.top_performers.hosts}
                        products={premiumData.top_performers.products}
                    />

                    {/* Alert Center (Enhanced Premium Version) */}
                    <AlertCenter alerts={premiumData.alerts} />

                    {/* Financial Summary */}
                    <FinancialSummary data={premiumData.financial_summary} />
                </>
            )}

            {/* WAR ROOM GRID */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Account Ranking */}
                <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="p-4 border-b border-slate-100 bg-slate-50">
                        <h2 className="font-bold text-lg text-slate-800">🏆 Ranking Akun Terkuat</h2>
                    </div>
                    <div className="overflow-x-auto max-h-96">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-50 sticky top-0">
                                <tr>
                                    <th className="px-4 py-3 text-left">#</th>
                                    <th className="px-4 py-3 text-left">Akun</th>
                                    <th className="px-4 py-3 text-right">GMV</th>
                                    <th className="px-4 py-3 text-right">Orders</th>
                                    <th className="px-4 py-3 text-right">Komisi</th>
                                    <th className="px-4 py-3 text-right">Spend</th>
                                    <th className="px-4 py-3 text-right">ROAS</th>
                                    <th className="px-4 py-3 text-center">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {war_room.account_ranking.map((acc, idx) => (
                                    <tr key={acc.account_id} className="hover:bg-slate-50">
                                        <td className="px-4 py-3 font-bold text-slate-600">{idx + 1}</td>
                                        <td className="px-4 py-3 font-medium">{acc.account_name}</td>
                                        <td className="px-4 py-3 text-right">Rp {acc.gmv.toLocaleString()}</td>
                                        <td className="px-4 py-3 text-right">{acc.orders}</td>
                                        <td className="px-4 py-3 text-right">Rp {acc.commission.toLocaleString()}</td>
                                        <td className="px-4 py-3 text-right">Rp {acc.spend.toLocaleString()}</td>
                                        <td className={`px-4 py-3 text-right font-bold ${acc.roas >= 8 ? 'text-green-600' : acc.roas >= 5 ? 'text-blue-600' : 'text-red-600'
                                            }`}>{acc.roas.toFixed(2)}x</td>
                                        <td className="px-4 py-3 text-center">
                                            <span className={`px-2 py-1 rounded-full text-xs font-bold ${acc.status === 'AMAN' ? 'bg-green-100 text-green-700' :
                                                acc.status === 'WASPADA' ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-red-100 text-red-700'
                                                }`}>{acc.status}</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Shift Scoreboard */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="p-4 border-b border-slate-100 bg-slate-50">
                        <h2 className="font-bold text-lg text-slate-800">⏰ Shift Scoreboard</h2>
                    </div>
                    <div className="p-4 space-y-3">
                        {war_room.shift_scoreboard.map((shift, idx) => (
                            <div key={idx} className="p-3 bg-slate-50 rounded-lg">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="font-bold text-sm text-slate-700">{shift.shift_name}</h3>
                                    <span className="text-xs text-slate-500">{shift.total_orders} orders</span>
                                </div>
                                <div className="text-lg font-bold text-green-600 mb-1">
                                    Rp {shift.total_gmv.toLocaleString()}
                                </div>
                                <div className="text-xs text-slate-600">
                                    <span className="font-semibold">MVP:</span> {shift.mvp_host}
                                    {shift.mvp_gmv > 0 && ` (Rp ${shift.mvp_gmv.toLocaleString()})`}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Orders per Hour Chart */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                <h2 className="font-bold text-lg text-slate-800 mb-4">📊 Orders per Jam (05:00 - 00:00)</h2>
                <div className="flex items-end justify-between gap-1 h-48">
                    {war_room.orders_per_hour.map((hour, idx) => {
                        const maxOrders = Math.max(...war_room.orders_per_hour.map(h => h.orders), 1)
                        const height = (hour.orders / maxOrders) * 100
                        return (
                            <div key={idx} className="flex-1 flex flex-col items-center">
                                <div className="text-xs font-bold text-slate-700 mb-1">{hour.orders}</div>
                                <div
                                    className="w-full bg-blue-500 rounded-t hover:bg-blue-600 transition-colors"
                                    style={{ height: `${height}%` }}
                                    title={`${hour.hour}: ${hour.orders} orders`}
                                />
                                <div className="text-[10px] text-slate-500 mt-1 rotate-45 origin-left">{hour.hour}</div>
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* HARDCORE INSIGHTS PANEL */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Column */}
                <div className="space-y-6">
                    {/* Product Drops */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                        <h2 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                            <TrendingDown className="text-red-500" />
                            Produk Drop Tajam
                        </h2>
                        {insights.product_drops.length > 0 ? (
                            <div className="space-y-2">
                                {insights.product_drops.map((prod, idx) => (
                                    <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                                        <div className="flex justify-between items-start">
                                            <p className="font-semibold text-sm text-slate-800">{prod.product_name}</p>
                                            <span className="text-red-600 font-bold text-sm">{prod.drop_percent}%</span>
                                        </div>
                                        <p className="text-xs text-slate-600 mt-1">
                                            Kemarin: {prod.yesterday_orders} → Hari ini: {prod.today_orders}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-500 text-sm">Tidak ada produk drop signifikan</p>
                        )}
                    </div>

                    {/* Profit Hunters */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                        <h2 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                            <Target className="text-green-500" />
                            Profit Hunter (Top 5)
                        </h2>
                        {insights.profit_hunters.length > 0 ? (
                            <div className="space-y-2">
                                {insights.profit_hunters.map((prod, idx) => (
                                    <div key={idx} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                                        <div>
                                            <p className="font-semibold text-sm text-slate-800">{prod.product_name}</p>
                                            <p className="text-xs text-slate-600">{prod.orders} orders</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-green-600">Rp {prod.total_commission.toLocaleString()}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-500 text-sm">Belum ada data produk</p>
                        )}
                    </div>
                </div>

                {/* Right Column */}
                <div className="space-y-6">
                    {/* Risk Detector */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                        <h2 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                            <AlertTriangle className="text-amber-500" />
                            Risk Detector
                        </h2>
                        <div className={`p-4 rounded-lg ${insights.risk_detector.is_risky ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
                            <div className="text-center mb-3">
                                <div className={`text-4xl font-bold ${insights.risk_detector.is_risky ? 'text-red-600' : 'text-green-600'}`}>
                                    {insights.risk_detector.top_account_dependency}%
                                </div>
                                <p className="text-sm text-slate-600 mt-1">Ketergantungan pada {insights.risk_detector.account_name}</p>
                            </div>
                            {insights.risk_detector.is_risky && (
                                <div className="bg-red-100 p-2 rounded text-xs text-red-800 text-center font-semibold">
                                    ⚠️ RISKY! Diversifikasi akun ASAP!
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Boros Detector */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                        <h2 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                            <Zap className="text-red-500" />
                            Boros Detector
                        </h2>
                        <p className="text-sm text-slate-600 mb-3">Threshold: ROAS &lt; {insights.boros_detector.threshold}x</p>
                        {insights.boros_detector.boros_accounts.length > 0 ? (
                            <div className="space-y-2">
                                {insights.boros_detector.boros_accounts.map((acc, idx) => (
                                    <div key={idx} className="p-2 bg-red-50 border border-red-200 rounded text-sm font-semibold text-red-700">
                                        💸 {acc}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-green-600 font-semibold text-sm">✅ Semua akun aman!</p>
                        )}
                    </div>

                    {/* Weak Shifts */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
                        <h2 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                            <Clock className="text-amber-500" />
                            Shift Lemah Hari Ini
                        </h2>
                        {insights.weak_shifts.length > 0 ? (
                            <div className="space-y-3">
                                {insights.weak_shifts.map((shift, idx) => (
                                    <div key={idx} className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                                        <div className="flex justify-between items-start mb-2">
                                            <p className="font-semibold text-sm text-slate-800">{shift.shift_name}</p>
                                            <span className="text-red-600 font-bold text-sm">{shift.gap_percent}%</span>
                                        </div>
                                        <p className="text-xs text-slate-600 mb-2">
                                            GMV: Rp {shift.gmv.toLocaleString()} / Target: Rp {shift.target.toLocaleString()}
                                        </p>
                                        <div className="bg-amber-100 p-2 rounded text-xs text-amber-800 font-semibold">
                                            💡 {shift.recommendation}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-green-600 font-semibold text-sm">✅ Semua shift perform baik!</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

// KPI Card Component
const KPICard: React.FC<{
    title: string
    value: string
    icon: React.ReactNode
    color: string
    trend: 'up' | 'down' | 'neutral'
}> = ({ title, value, icon, color, trend }) => (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between mb-3">
            <div className={`p-3 rounded-lg ${color} text-white`}>
                {icon}
            </div>
            {trend !== 'neutral' && (
                <div className={`flex items-center gap-1 ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {trend === 'up' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                </div>
            )}
        </div>
        <p className="text-sm text-slate-500 mb-1">{title}</p>
        <h3 className="text-2xl font-bold text-slate-800">{value}</h3>
    </div>
)

export default DashboardOwner
