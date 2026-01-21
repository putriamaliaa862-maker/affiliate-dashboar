import React, { useState, useEffect } from 'react'
import {
    Trophy,
    TrendingUp,
    DollarSign,
    ShoppingBag,
    Users
} from 'lucide-react'
import { insightsApi, DailySummaryResponse } from '@/api/insights'
import { accountApi } from '@/api/accounts'

const DailySummary: React.FC = () => {
    const [date, setDate] = useState(new Date().toISOString().split('T')[0])
    const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null)
    const [accounts, setAccounts] = useState<any[]>([])
    const [data, setData] = useState<DailySummaryResponse | null>(null)
    const [loading, setLoading] = useState(false)
    const [_error, setError] = useState<string | null>(null)

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
            const res = await insightsApi.getDailySummary(date, selectedAccountId || undefined)
            setData(res)
            setError(null)
        } catch (err) {
            setError('Gagal memuat ringkasan hari ini')
        } finally {
            setLoading(false)
        }
    }

    if (loading && !data) return <div className="p-8 text-center text-slate-500">Memuat data...</div>

    return (
        <div className="space-y-8">
            {/* Header & Filter */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                    <div>
                        <h1 className="text-2xl font-bold text-slate-800">Ringkasan Hari Ini</h1>
                        <p className="text-slate-500">Pantau performa bisnis secara real-time 🚀</p>
                    </div>
                    <div className="flex gap-3">
                        <input
                            type="date"
                            value={date}
                            onChange={e => setDate(e.target.value)}
                            className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
                        />
                        <select
                            value={selectedAccountId || ''}
                            onChange={e => setSelectedAccountId(e.target.value ? Number(e.target.value) : null)}
                            className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
                        >
                            <option value="">Semua Akun</option>
                            {accounts.map(acc => (
                                <option key={acc.id} value={acc.id}>{acc.account_name}</option>
                            ))}
                        </select>
                        <button
                            onClick={fetchData}
                            className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700"
                        >
                            Tarik Data
                        </button>
                    </div>
                </div>

                {/* Notes */}
                {data && data.notes.length > 0 && (
                    <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-6">
                        <h3 className="text-sm font-semibold text-blue-800 mb-2">Catatan Harian:</h3>
                        <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
                            {data.notes.map((note, idx) => <li key={idx}>{note}</li>)}
                        </ul>
                    </div>
                )}

                {/* KPI Cards */}
                {data && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <KPICard
                            title="Total Order"
                            value={data.kpi.total_orders}
                            icon={<ShoppingBag className="text-white" />}
                            bg="bg-gradient-to-br from-blue-500 to-blue-600"
                            isCurrency={false}
                        />
                        <KPICard
                            title="Total GMV"
                            value={data.kpi.total_gmv}
                            icon={<DollarSign className="text-white" />}
                            bg="bg-gradient-to-br from-emerald-500 to-emerald-600"
                        />
                        <KPICard
                            title="Total Komisi"
                            value={data.kpi.total_commission}
                            icon={<TrendingUp className="text-white" />}
                            bg="bg-gradient-to-br from-purple-500 to-purple-600"
                        />
                        <KPICard
                            title="Total Bonus"
                            value={data.kpi.total_bonus}
                            icon={<Trophy className="text-white" />}
                            bg="bg-gradient-to-br from-amber-500 to-amber-600"
                        />
                    </div>
                )}
            </div>

            {/* Highlights */}
            {data && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <HighlightCard
                        title="Akun Paling Ngebut 🏆"
                        entity={data.best_account_today}
                        color="text-emerald-600"
                        bgColor="bg-emerald-50"
                    />
                    <HighlightCard
                        title="Shift Terkuat ✅"
                        entity={data.best_shift_today}
                        color="text-blue-600"
                        bgColor="bg-blue-50"
                        isShift
                    />
                    <HighlightCard
                        title="Perlu Perhatian ⚠️"
                        entity={data.weak_shift_today}
                        color="text-red-600"
                        bgColor="bg-red-50"
                        isShift
                    />
                </div>
            )}
        </div>
    )
}

const KPICard = ({ title, value, icon, bg, isCurrency = true }: any) => (
    <div className={`${bg} rounded-xl p-6 text-white shadow-lg`}>
        <div className="flex justify-between items-start">
            <div>
                <p className="text-blue-100 text-sm font-medium mb-1">{title}</p>
                <h3 className="text-2xl font-bold">
                    {isCurrency
                        ? new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value)
                        : value}
                </h3>
            </div>
            <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                {icon}
            </div>
        </div>
    </div>
)

const HighlightCard = ({ title, entity, color, bgColor, isShift }: any) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <div className="flex items-center gap-2 mb-4">
            <div className={`p-2 rounded-lg ${bgColor}`}>
                <Users className={`w-5 h-5 ${color}`} />
            </div>
            <h3 className="font-semibold text-slate-800">{title}</h3>
        </div>

        <div className="space-y-2">
            <div className="text-lg font-bold text-slate-800">{entity.name}</div>
            <div className="flex justify-between text-sm text-slate-600 border-t border-slate-100 pt-3">
                <span>Total Orders:</span>
                <span className="font-medium">{entity.orders}</span>
            </div>
            {!isShift && (
                <div className="flex justify-between text-sm text-slate-600">
                    <span>Total GMV:</span>
                    <span className="font-medium">
                        {new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(entity.gmv)}
                    </span>
                </div>
            )}
        </div>
    </div>
)

export default DailySummary
