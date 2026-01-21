import React from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { TrendingUp, AlertTriangle, DollarSign, Zap, ExternalLink } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

// ==================== PREMIUM FEATURE 1: Realtime Hourly Chart ====================

interface HourlyDataPoint {
    hour: string
    gmv: number
    orders: number
    gmv_yesterday?: number
}

interface RealtimeChartProps {
    data: HourlyDataPoint[]
}

export const RealtimePerformanceChart: React.FC<RealtimeChartProps> = ({ data }) => {
    const formatRupiah = (value: number) => {
        return `${(value / 1000000).toFixed(1)}jt`
    }

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="font-bold text-lg text-slate-800 flex items-center gap-2">
                    <TrendingUp className="text-blue-500" />
                    📈 Performa Realtime (Jam per Jam)
                </h2>
                <span className="text-xs text-green-600 font-bold px-3 py-1 bg-green-50 rounded-full">
                    LIVE
                </span>
            </div>

            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <XAxis
                            dataKey="hour"
                            tick={{ fontSize: 11 }}
                            stroke="#94a3b8"
                        />
                        <YAxis
                            yAxisId="left"
                            tick={{ fontSize: 11 }}
                            stroke="#3b82f6"
                            tickFormatter={formatRupiah}
                        />
                        <YAxis
                            yAxisId="right"
                            orientation="right"
                            tick={{ fontSize: 11 }}
                            stroke="#10b981"
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1e293b',
                                border: 'none',
                                borderRadius: '8px',
                                color: 'white',
                                fontSize: '12px'
                            }}
                            formatter={(value: any) => {
                                if (typeof value === 'number') {
                                    return value >= 1000 ? `Rp ${(value / 1000000).toFixed(2)}jt` : value
                                }
                                return value
                            }}
                        />

                        {/* Yesterday GMV (dotted line for comparison) */}
                        {data.some(d => d.gmv_yesterday) && (
                            <Line
                                yAxisId="left"
                                type="monotone"
                                dataKey="gmv_yesterday"
                                stroke="#94a3b8"
                                strokeDasharray="5 5"
                                strokeWidth={1.5}
                                dot={false}
                                name="GMV Kemarin"
                            />
                        )}

                        {/* Today GMV */}
                        <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="gmv"
                            stroke="#3b82f6"
                            strokeWidth={3}
                            dot={{ fill: '#3b82f6', r: 4 }}
                            activeDot={{ r: 6 }}
                            name="GMV Hari Ini"
                        />

                        {/* Orders */}
                        <Line
                            yAxisId="right"
                            type="monotone"
                            dataKey="orders"
                            stroke="#10b981"
                            strokeWidth={2}
                            dot={{ fill: '#10b981', r: 3 }}
                            name="Orders"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-100">
                <div className="text-center">
                    <p className="text-xs text-slate-500">Jam Puncak</p>
                    <p className="font-bold text-blue-600">
                        {data.reduce((max, d) => d.gmv > max.gmv ? d : max, data[0])?.hour || '-'}
                    </p>
                </div>
                <div className="text-center">
                    <p className="text-xs text-slate-500">Total GMV</p>
                    <p className="font-bold text-green-600">
                        Rp {(data.reduce((sum, d) => sum + d.gmv, 0) / 1000000).toFixed(1)}jt
                    </p>
                </div>
                <div className="text-center">
                    <p className="text-xs text-slate-500">Total Orders</p>
                    <p className="font-bold text-purple-600">
                        {data.reduce((sum, d) => sum + d.orders, 0)}
                    </p>
                </div>
            </div>
        </div>
    )
}

// ==================== PREMIUM FEATURE 2: Top Performers Widget ====================

interface TopPerformer {
    name: string
    value: number
    subtitle?: string
    rank: number
}

interface TopPerformersProps {
    accounts: TopPerformer[]
    hosts: TopPerformer[]
    products: TopPerformer[]
}

export const TopPerformersWidget: React.FC<TopPerformersProps> = ({ accounts, hosts, products }) => {
    const navigate = useNavigate()

    const rankColors = ['bg-yellow-500 text-white', 'bg-gray-400 text-white', 'bg-amber-700 text-white']

    const PerformerCard = ({ title, items, type }: { title: string, items: TopPerformer[], type: string }) => (
        <div className="bg-gradient-to-br from-white to-slate-50 rounded-xl border border-slate-200 shadow-sm p-4">
            <h3 className="font-bold text-sm text-slate-700 mb-3">{title}</h3>
            <div className="space-y-2">
                {items.slice(0, 5).map((item, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-2 bg-white rounded-lg border border-slate-100 hover:shadow-md transition-shadow">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${idx < 3 ? rankColors[idx] : 'bg-slate-200 text-slate-600'}`}>
                            {idx + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="font-semibold text-sm text-slate-800 truncate">{item.name}</p>
                            {item.subtitle && <p className="text-xs text-slate-500">{item.subtitle}</p>}
                        </div>
                        <div className="text-right">
                            <p className="font-bold text-sm text-green-600">
                                {item.value >= 1000000
                                    ? `Rp ${(item.value / 1000000).toFixed(1)}jt`
                                    : item.value >= 1000
                                        ? `Rp ${(item.value / 1000).toFixed(0)}rb`
                                        : type === 'conversion'
                                            ? `${item.value}%`
                                            : item.value
                                }
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="font-bold text-lg text-slate-800">🏆 Top Performers Hari Ini</h2>
                <button
                    onClick={() => navigate('/reports')}
                    className="text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
                >
                    Lihat Semua <ExternalLink size={12} />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <PerformerCard title="🥇 Akun Terkuat (GMV)" items={accounts} type="currency" />
                <PerformerCard title="💎 Host Terbaik (Konversi)" items={hosts} type="conversion" />
                <PerformerCard title="🔥 Produk Gacor (Terjual)" items={products} type="number" />
            </div>
        </div>
    )
}

// ==================== PREMIUM FEATURE 3: Alert Center ====================

interface AlertItem {
    type: 'boros' | 'budget' | 'drop' | 'risk'
    title: string
    description: string
    severity: 'critical' | 'warning' | 'info'
    actionLabel: string
    actionPath: string
}

interface AlertCenterProps {
    alerts: AlertItem[]
}

export const AlertCenter: React.FC<AlertCenterProps> = ({ alerts }) => {
    const navigate = useNavigate()

    const severityConfig = {
        critical: { bg: 'bg-red-50', border: 'border-red-300', text: 'text-red-800', icon: '🚨' },
        warning: { bg: 'bg-amber-50', border: 'border-amber-300', text: 'text-amber-800', icon: '⚠️' },
        info: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-800', icon: 'ℹ️' }
    }

    if (alerts.length === 0) {
        return (
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200 p-6">
                <div className="text-center">
                    <div className="text-4xl mb-2">✅</div>
                    <h3 className="font-bold text-green-800 text-lg mb-1">Semua Aman!</h3>
                    <p className="text-green-600 text-sm">Tidak ada alert kritis hari ini. Semua performa stabil 🎉</p>
                </div>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="text-red-500" size={24} />
                <h2 className="font-bold text-lg text-slate-800">⚡ Alert Center Realtime</h2>
                <span className="ml-auto px-2 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full">
                    {alerts.filter(a => a.severity === 'critical').length} Critical
                </span>
            </div>

            <div className="space-y-3">
                {alerts.map((alert, idx) => {
                    const config = severityConfig[alert.severity]
                    return (
                        <div
                            key={idx}
                            className={`${config.bg} border ${config.border} rounded-lg p-4 hover:shadow-md transition-shadow`}
                        >
                            <div className="flex items-start gap-3">
                                <span className="text-2xl">{config.icon}</span>
                                <div className="flex-1">
                                    <h4 className={`font-bold text-sm ${config.text} mb-1`}>{alert.title}</h4>
                                    <p className="text-xs text-slate-600 mb-3">{alert.description}</p>
                                    <button
                                        onClick={() => navigate(alert.actionPath)}
                                        className={`text-xs font-semibold ${config.text} hover:underline flex items-center gap-1`}
                                    >
                                        {alert.actionLabel} →
                                    </button>
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

// ==================== PREMIUM FEATURE 4: Financial Summary ====================

interface FinancialData {
    revenue_today: number
    revenue_yesterday: number
    commission_pending: number
    commission_paid: number
    budget_used: number
    budget_total: number
    accounts_roas: { account_name: string, roas: number }[]
}

interface FinancialSummaryProps {
    data: FinancialData
}

export const FinancialSummary: React.FC<FinancialSummaryProps> = ({ data }) => {
    const revenueChange = data.revenue_yesterday > 0
        ? ((data.revenue_today - data.revenue_yesterday) / data.revenue_yesterday * 100).toFixed(1)
        : '0'

    const budgetUtilization = data.budget_total > 0
        ? (data.budget_used / data.budget_total * 100).toFixed(0)
        : 0

    const getRoasColor = (roas: number) => {
        if (roas >= 8) return '#10b981'
        if (roas >= 5) return '#3b82f6'
        if (roas >= 3) return '#f59e0b'
        return '#ef4444'
    }

    return (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h2 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
                <DollarSign className="text-green-500" />
                💰 Financial Summary
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Revenue Comparison */}
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
                    <p className="text-xs text-green-700 font-medium mb-2">Revenue Today vs Yesterday</p>
                    <div className="flex items-end justify-between">
                        <div>
                            <p className="text-2xl font-bold text-green-800">
                                Rp {(data.revenue_today / 1000000).toFixed(1)}jt
                            </p>
                            <p className="text-xs text-green-600 mt-1">
                                Kemarin: Rp {(data.revenue_yesterday / 1000000).toFixed(1)}jt
                            </p>
                        </div>
                        <div className={`px-2 py-1 rounded font-bold text-sm ${parseFloat(revenueChange) >= 0 ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>
                            {parseFloat(revenueChange) >= 0 ? '+' : ''}{revenueChange}%
                        </div>
                    </div>
                </div>

                {/* Commission Status */}
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
                    <p className="text-xs text-purple-700 font-medium mb-2">Commission Status</p>
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <span className="text-xs text-slate-600">Pending</span>
                            <span className="font-bold text-amber-600">Rp {(data.commission_pending / 1000000).toFixed(1)}jt</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-xs text-slate-600">Paid</span>
                            <span className="font-bold text-green-600">Rp {(data.commission_paid / 1000000).toFixed(1)}jt</span>
                        </div>
                    </div>
                </div>

                {/* Budget Utilization */}
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
                    <p className="text-xs text-blue-700 font-medium mb-2">Budget Utilization</p>
                    <div className="relative pt-1">
                        <div className="flex justify-between mb-2">
                            <span className="text-xs text-slate-600">Used: Rp {(data.budget_used / 1000000).toFixed(1)}jt</span>
                            <span className="text-xs font-bold text-blue-800">{budgetUtilization}%</span>
                        </div>
                        <div className="overflow-hidden h-4 text-xs flex rounded-full bg-blue-100">
                            <div
                                style={{ width: `${Math.min(parseFloat(budgetUtilization.toString()), 100)}%` }}
                                className={`flex flex-col text-center whitespace-nowrap text-white justify-center ${parseFloat(budgetUtilization.toString()) > 90 ? 'bg-red-500' : parseFloat(budgetUtilization.toString()) > 70 ? 'bg-amber-500' : 'bg-blue-500'}`}
                            />
                        </div>
                        <p className="text-xs text-slate-500 mt-1">Total: Rp {(data.budget_total / 1000000).toFixed(1)}jt</p>
                    </div>
                </div>

                {/* ROAS Heatmap */}
                <div className="bg-gradient-to-br from-slate-50 to-gray-50 rounded-lg p-4 border border-slate-200">
                    <p className="text-xs text-slate-700 font-medium mb-3">ROAS Heatmap (Per Akun)</p>
                    <div className="h-24">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data.accounts_roas.slice(0, 6)}>
                                <XAxis
                                    dataKey="account_name"
                                    tick={{ fontSize: 9 }}
                                    angle={-45}
                                    textAnchor="end"
                                    height={40}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '4px', fontSize: '11px' }}
                                    formatter={(value: any) => [`${value}x ROAS`, '']}
                                />
                                <Bar dataKey="roas" radius={[4, 4, 0, 0]}>
                                    {data.accounts_roas.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={getRoasColor(entry.roas)} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    )
}

// ==================== PREMIUM FEATURE 5: Quick Actions Dashboard ====================

interface QuickActionsProps {
    userRole: string
}

export const QuickActionsDashboard: React.FC<QuickActionsProps> = ({ userRole }) => {
    const navigate = useNavigate()

    const actions = [
        {
            id: 'add-budget',
            label: 'Tambah Modal',
            icon: '💸',
            color: 'bg-purple-500 hover:bg-purple-600',
            path: '/ads-center',
            roles: ['owner', 'super_admin', 'supervisor', 'partner', 'leader']
        },
        {
            id: 'input-spend',
            label: 'Input Spend',
            icon: '💰',
            color: 'bg-blue-500 hover:bg-blue-600',
            path: '/ads-center',
            roles: ['owner', 'super_admin', 'supervisor', 'partner', 'leader']
        },
        {
            id: 'sync-live',
            label: 'Sync Live Products',
            icon: '⚡',
            color: 'bg-green-500 hover:bg-green-600',
            path: '/live-products',
            roles: ['owner', 'super_admin', 'admin', 'supervisor', 'partner', 'leader']
        },
        {
            id: 'view-insights',
            label: 'Insights Produk',
            icon: '📊',
            color: 'bg-amber-500 hover:bg-amber-600',
            path: '/daily-insights',  // Fixed: was /insights/daily, route doesn't exist
            roles: ['owner', 'super_admin', 'admin', 'supervisor', 'partner', 'leader', 'host']
        },
        {
            id: 'commission-report',
            label: 'Laporan Komisi',
            icon: '💵',
            color: 'bg-indigo-500 hover:bg-indigo-600',
            path: '/reports',
            roles: ['owner', 'super_admin', 'admin', 'supervisor']
        },
        {
            id: 'manage-users',
            label: 'Kelola User',
            icon: '👥',
            color: 'bg-red-500 hover:bg-red-600',
            path: '/users',
            roles: ['owner', 'super_admin', 'admin']
        }
    ]

    const normalizedRole = userRole.toLowerCase().replace(' ', '_')
    const availableActions = actions.filter(action => action.roles.includes(normalizedRole))

    return (
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl border border-slate-700 shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
                <Zap className="text-yellow-400" size={24} />
                <h2 className="font-bold text-lg text-white">⚡ Quick Actions</h2>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {availableActions.map(action => (
                    <button
                        key={action.id}
                        onClick={() => navigate(action.path)}
                        className={`${action.color} text-white rounded-lg p-4 transition-all hover:scale-105 hover:shadow-xl flex flex-col items-center justify-center gap-2`}
                    >
                        <span className="text-3xl">{action.icon}</span>
                        <span className="text-xs font-semibold text-center">{action.label}</span>
                    </button>
                ))}
            </div>

            {availableActions.length < 3 && (
                <p className="text-xs text-slate-400 mt-3 text-center">
                    Beberapa aksi dibatasi sesuai role kamu 🔒
                </p>
            )}
        </div>
    )
}
