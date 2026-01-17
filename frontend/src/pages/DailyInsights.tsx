import React, { useState, useEffect } from 'react'
import {
    TrendingDown,
    TrendingUp,
    AlertCircle,
    CheckCircle2,
    Zap
} from 'lucide-react'
import { insightsApi, DailyInsightsResponse } from '@/api/insights'
import { accountApi } from '@/api/accounts'

const DailyInsights: React.FC = () => {
    const [date, setDate] = useState(new Date().toISOString().split('T')[0])
    const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null)
    const [accounts, setAccounts] = useState<any[]>([])
    const [data, setData] = useState<DailyInsightsResponse | null>(null)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        fetchAccounts()
    }, [])

    useEffect(() => {
        fetchData()
    }, [date, selectedAccountId])

    const fetchAccounts = async () => {
        try {
            const res = await accountApi.getAll(1)
            setAccounts(res)
        } catch (err) { console.error(err) }
    }

    const fetchData = async () => {
        try {
            setLoading(true)
            const res = await insightsApi.getDailyInsights(date, selectedAccountId || undefined)
            setData(res)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (val: number) =>
        new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val)

    if (loading && !data) return <div className="p-8 text-center text-slate-500">Menganalisa data...</div>

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                            <Zap className="text-yellow-500" fill="currentColor" />
                            Insight Harian
                        </h1>
                        <div className="group relative">
                            <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
                            <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                                Biar besok live nggak asal gas.
                            </div>
                        </div>
                    </div>
                    <p className="text-slate-500">Rangkuman strategi hari ini: produk yang naik, drop, dan yang harus dipush.</p>
                </div>
                <div className="flex gap-3 bg-white p-2 rounded-lg shadow-sm border border-slate-200">
                    <input
                        type="date"
                        value={date}
                        onChange={e => setDate(e.target.value)}
                        className="rounded-md px-3 py-1 text-sm focus:outline-none"
                    />
                    <div className="w-px bg-slate-200"></div>
                    <select
                        value={selectedAccountId || ''}
                        onChange={e => setSelectedAccountId(e.target.value ? Number(e.target.value) : null)}
                        className="rounded-md px-3 py-1 text-sm focus:outline-none bg-transparent"
                    >
                        <option value="">Semua Akun</option>
                        {accounts.map(acc => (
                            <option key={acc.id} value={acc.id}>{acc.account_name}</option>
                        ))}
                    </select>
                    <button onClick={fetchData} className="px-3 py-1 bg-slate-100 hover:bg-slate-200 rounded text-sm font-medium">
                        Muat Ulang
                    </button>
                </div>
            </div>

            {data && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                    {/* LEFT COLUMN */}
                    <div className="space-y-8">

                        {/* 1. WARNINGS (Products Drop) */}
                        <div className="bg-white rounded-xl shadow-sm border border-red-100 overflow-hidden">
                            <div className="px-6 py-4 bg-red-50 border-b border-red-100 flex items-center justify-between">
                                <h3 className="font-bold text-red-800 flex items-center gap-2">
                                    <TrendingDown size={20} />
                                    Produk Drop Tajam
                                </h3>
                                <span className="bg-red-200 text-red-800 text-xs px-2 py-1 rounded-full font-bold">
                                    Total: {data.warnings.products_drop_sharp?.length || 0}
                                </span>
                            </div>
                            <div className="p-6">
                                {(!data.warnings.products_drop_sharp || data.warnings.products_drop_sharp.length === 0) ? (
                                    <p className="text-slate-500 text-center py-4">Aman! Tidak ada penurunan drastis hari ini 👍</p>
                                ) : (
                                    <div className="space-y-4">
                                        {data.warnings.products_drop_sharp.map((p, i) => (
                                            <div key={i} className="flex items-start justify-between pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                                                <div>
                                                    <p className="font-semibold text-slate-800 text-sm line-clamp-1" title={p.product_name}>{p.product_name}</p>
                                                    <p className="text-xs text-slate-500 mt-1">Akun: {p.account_name}</p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-red-600 font-bold text-sm">-{p.drop_percent}%</p>
                                                    <p className="text-xs text-slate-400">{p.orders_yesterday} ➔ {p.orders_today} orders</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* 3. SHIFT SUMMARY */}
                        <div className="bg-white rounded-xl shadow-sm border border-slate-200">
                            <div className="px-6 py-4 border-b border-slate-100">
                                <h3 className="font-bold text-slate-800">Performa Shift</h3>
                            </div>
                            <div className="p-6">
                                <div className="space-y-4">
                                    {data.shift_summary.map((shift, i) => (
                                        <div key={i} className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-2 h-8 rounded-full ${shift.orders > 0 ? (i % 2 === 0 ? 'bg-blue-500' : 'bg-indigo-500') : 'bg-slate-300'}`}></div>
                                                <div>
                                                    <p className="font-medium text-slate-700">{shift.shift_name}</p>
                                                    <p className="text-xs text-slate-500">{shift.orders} orders</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm font-semibold text-slate-700">{formatCurrency(shift.gmv)}</p>
                                                <p className="text-xs text-green-600">Comm: {formatCurrency(shift.commission)}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* RIGHT COLUMN */}
                    <div className="space-y-8">

                        {/* 2. TOP PROFIT PRODUCTS */}
                        <div className="bg-white rounded-xl shadow-sm border border-green-100 overflow-hidden">
                            <div className="px-6 py-4 bg-emerald-50 border-b border-emerald-100 flex items-center justify-between">
                                <h3 className="font-bold text-emerald-800 flex items-center gap-2">
                                    <TrendingUp size={20} />
                                    Produk Paling Cuan 💰
                                </h3>
                            </div>
                            <div className="p-6">
                                {data.top_profit_products.length === 0 ? (
                                    <p className="text-slate-500 text-center">Insight belum kebaca. Import data hari ini & kemarin biar bisa dibandingin.</p>
                                ) : (
                                    <div className="space-y-4">
                                        {data.top_profit_products.map((p, i) => (
                                            <div key={i} className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-xs">
                                                        {i + 1}
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <p className="font-medium text-slate-800 text-sm truncate w-48" title={p.product_name}>
                                                            {p.product_name}
                                                        </p>
                                                        <p className="text-xs text-slate-500">{p.total_orders} orders • {p.account_name}</p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-emerald-600 font-bold text-sm">{formatCurrency(p.total_commission)}</p>
                                                    <p className="text-xs text-slate-400">{formatCurrency(p.commission_per_order)} / order</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* 4. ACTION ITEMS */}
                        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl shadow-lg text-white p-6">
                            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                                <CheckCircle2 className="text-green-400" />
                                Rekomendasi Besok
                            </h3>
                            <div className="space-y-3">
                                {data.action_items.map((action, i) => (
                                    <div key={i} className="flex gap-3 items-start bg-white/10 p-3 rounded-lg backdrop-blur-sm">
                                        <div className="mt-1 w-2 h-2 rounded-full bg-yellow-400 shrink-0"></div>
                                        <p className="text-sm text-slate-200 leading-relaxed">{action}</p>
                                    </div>
                                ))}
                                {data.action_items.length === 0 && (
                                    <p className="text-slate-400 italic">Data belum cukup untuk memberikan rekomendasi.</p>
                                )}
                            </div>
                        </div>

                        {/* 5. RISK ALERT */}
                        {data.dependency_risk.length > 0 && (
                            <div className="bg-orange-50 border border-orange-200 p-4 rounded-xl">
                                <h4 className="text-orange-800 font-bold text-sm mb-2 flex items-center gap-2">
                                    <AlertCircle size={16} />
                                    Resiko Terdeteksi
                                </h4>
                                <ul className="list-disc list-inside text-xs text-orange-700 space-y-1">
                                    {data.dependency_risk.map((r, i) => (
                                        <li key={i}>{r.message}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                    </div>
                </div>
            )}
        </div>
    )
}

export default DailyInsights
