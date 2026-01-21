import React, { useState, useEffect } from 'react'
import {
    BarChart3, RefreshCw, Calendar,
    DollarSign, TrendingUp, AlertTriangle,
    PlusCircle, Edit2
} from 'lucide-react'
import api from '@/api/client'
import { adsApi, AdsCenterAccountRow } from '@/api/ads'
import { useAuth } from '@/hooks/useAuth'
import SpendInputModal from '@/components/ads/SpendInputModal'
import RoasManualModal from '@/components/ads/RoasManualModal'
import AudienceBudgetModal from '@/components/ads/AudienceBudgetModal'

const AdsCenter: React.FC = () => {
    const { user } = useAuth()
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<AdsCenterAccountRow[]>([])

    // Filters
    const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0])
    const [selectedAccountId, setSelectedAccountId] = useState<string>('all')
    const [accounts, setAccounts] = useState<any[]>([])

    // Load States
    const [_loadingAccounts, setLoadingAccounts] = useState(false)

    // Modals
    const [spendModal, setSpendModal] = useState<{ isOpen: boolean, accountId: number, accountName: string } | null>(null)
    const [roasModal, setRoasModal] = useState<{ isOpen: boolean, accountId: number, accountName: string, currentRoas?: number | null } | null>(null)
    const [budgetModal, setBudgetModal] = useState<{ isOpen: boolean, accountId: number, accountName: string, threshold: number, gapMinutes: number } | null>(null)

    // Active Tab
    const [activeTab, setActiveTab] = useState<'spend' | 'audience' | 'roas'>('spend')

    // Logs Data
    const [logs, setLogs] = useState<any[]>([])
    const [loadingLogs, setLoadingLogs] = useState(false)

    // Fetch Accounts for dropdown
    useEffect(() => {
        const fetchAccounts = async () => {
            setLoadingAccounts(true)
            try {
                const res = await api.get('/shopee-accounts')
                setAccounts(res.data)
            } catch (err) {
                console.error("Failed to load accounts", err)
            } finally {
                setLoadingAccounts(false)
            }
        }
        fetchAccounts()
    }, [])

    // Fetch Main Data
    const fetchData = async () => {
        setLoading(true)
        try {
            const accId = selectedAccountId === 'all' ? null : parseInt(selectedAccountId)
            const res = await adsApi.getAdsCenter(date, accId)

            // Sort: Boros Score Descending by default
            const sorted = res.sort((a, b) => b.boros_score - a.boros_score)
            setData(sorted)
        } catch (err) {
            console.error("Failed to load ads data", err)
        } finally {
            setLoading(false)
        }
    }

    // Fetch Logs when tab/date/account changes
    const fetchLogs = async () => {
        setLoadingLogs(true)
        const accId = selectedAccountId === 'all' ? null : parseInt(selectedAccountId)
        try {
            let resLogs: any[] = []
            if (activeTab === 'spend') {
                resLogs = await adsApi.getSpendLogs(date, date, accId)
            } else if (activeTab === 'audience') {
                resLogs = await adsApi.getAudienceLogs(date, date, accId)
            } else if (activeTab === 'roas') {
                resLogs = await adsApi.getRoasLogs(date, date, accId)
            }
            setLogs(resLogs)
        } catch (err) {
            console.error(err)
        } finally {
            setLoadingLogs(false)
        }
    }

    useEffect(() => {
        fetchData()
    }, [date, selectedAccountId])

    useEffect(() => {
        fetchLogs()
    }, [date, selectedAccountId, activeTab])


    // Helper: RBAC check
    const canEdit = user && ['owner', 'supervisor', 'partner', 'super_admin'].includes(user.role)
    const canAddBudget = user && ['owner', 'supervisor', 'partner', 'super_admin', 'leader'].includes(user.role)
    // Host cannot do anything (view only)

    // Calcs for KPI Cards
    const totalSpend = data.reduce((acc, curr) => acc + curr.spend_today, 0)
    const totalGmv = data.reduce((acc, curr) => acc + curr.gmv_today, 0)
    const avgRoas = totalSpend > 0 ? totalGmv / totalSpend : 0
    const mostBoros = data.length > 0 ? data[0] : null // sorted desc

    return (
        <div className="p-6 space-y-6 max-w-[1600px] mx-auto pb-20">

            {/* HEADER */}
            <div>
                <h1 className="text-2xl font-bold text-slate-900">Ads Center</h1>
                <p className="text-slate-500">Pantau iklan per akun biar nggak boncos & makin gacor.</p>
            </div>

            {/* FILTER BAR */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
                <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto">
                    <div className="relative">
                        <Calendar className="absolute left-3 top-2.5 text-slate-400" size={18} />
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none w-full md:w-auto"
                        />
                    </div>

                    <div className="relative min-w-[200px]">
                        <select
                            value={selectedAccountId}
                            onChange={(e) => setSelectedAccountId(e.target.value)}
                            className="w-full pl-3 pr-8 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none appearance-none bg-white"
                        >
                            <option value="all">Semua Akun</option>
                            {accounts.map(acc => (
                                <option key={acc.id} value={acc.id}>{acc.account_name}</option>
                            ))}
                        </select>
                    </div>
                </div>

                <button
                    onClick={fetchData}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors font-medium"
                >
                    <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
                    Refresh
                </button>
            </div>

            {/* KPI CARDS */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <KPICard
                    title="Total Spend Hari Ini"
                    value={`Rp ${totalSpend.toLocaleString('id-ID')}`}
                    icon={<DollarSign className="text-red-500" />}
                    color="bg-red-50 text-red-700"
                />
                <KPICard
                    title="Total GMV Hari Ini"
                    value={`Rp ${totalGmv.toLocaleString('id-ID')}`}
                    icon={<TrendingUp className="text-green-500" />}
                    color="bg-green-50 text-green-700"
                />
                <KPICard
                    title="Avg ROAS"
                    value={`${avgRoas.toFixed(2)}x`}
                    icon={<BarChart3 className="text-blue-500" />}
                    color="bg-blue-50 text-blue-700"
                />
                <KPICard
                    title="Akun Paling Boros"
                    value={mostBoros ? mostBoros.account_name : "-"}
                    subValue={mostBoros ? `Score: ${mostBoros.boros_score}` : ""}
                    icon={<AlertTriangle className="text-amber-500" />}
                    color="bg-amber-50 text-amber-700"
                />
            </div>

            {/* MAIN TABLE */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                    <h2 className="font-bold text-lg text-slate-800">Performa Iklan per Akun</h2>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-slate-50 text-slate-500 font-medium">
                            <tr>
                                <th className="px-6 py-4">Akun</th>
                                <th className="px-6 py-4">Spend</th>
                                <th className="px-6 py-4">GMV</th>
                                <th className="px-6 py-4">ROAS</th>
                                <th className="px-6 py-4">Status Boros</th>
                                <th className="px-6 py-4">Status Budget</th>
                                <th className="px-6 py-4 text-center">Aksi</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loading ? (
                                <tr><td colSpan={7} className="px-6 py-12 text-center text-slate-400">Loading data...</td></tr>
                            ) : data.length === 0 ? (
                                <tr><td colSpan={7} className="px-6 py-12 text-center text-slate-400">Belum ada data iklan untuk tanggal ini. <br /> Santai, tinggal input spend aja dulu ✨</td></tr>
                            ) : (
                                data.map(row => (
                                    <tr key={row.account_id} className="hover:bg-slate-50">
                                        <td className="px-6 py-4 font-medium text-slate-800">{row.account_name}</td>
                                        <td className="px-6 py-4 text-slate-600">Rp {row.spend_today.toLocaleString('id-ID')}</td>
                                        <td className="px-6 py-4 text-slate-600">Rp {row.gmv_today.toLocaleString('id-ID')}</td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <span className={`font-bold ${(row.roas_final || 0) >= 8 ? 'text-green-600' : (row.roas_final || 0) >= 5 ? 'text-blue-600' : 'text-red-500'}`}>
                                                    {(row.roas_final || 0).toFixed(2)}x
                                                </span>
                                                {row.roas_manual !== undefined && row.roas_manual !== null && (
                                                    <span className="px-1.5 py-0.5 bg-amber-100 text-amber-700 text-[10px] rounded uppercase font-bold tracking-wide">
                                                        MANUAL
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-bold ${row.boros_status === 'BOROS' ? 'bg-red-100 text-red-700' :
                                                row.boros_status === 'WASPADA' ? 'bg-amber-100 text-amber-700' :
                                                    'bg-green-100 text-green-700'
                                                }`}>
                                                {row.boros_status}
                                            </span>
                                            {row.boros_status !== 'AMAN' && (
                                                <div className="text-[10px] text-slate-400 mt-1 max-w-[150px] leading-tight">
                                                    {row.boros_reason}
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`px-2 py-1 rounded-full text-xs font-bold ${row.audience_status === 'HAMPIR_HABIS' ? 'bg-red-100 text-red-700' :
                                                'bg-blue-100 text-blue-700'
                                                }`}>
                                                {row.audience_status === 'HAMPIR_HABIS' ? 'HAMPIR HABIS' : 'AMAN'}
                                            </span>
                                            {row.last_add_budget_at && (
                                                <div className="text-[10px] text-slate-400 mt-1">
                                                    Last add: {row.last_add_budget_at}
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex justify-center gap-2">
                                                {canEdit && (
                                                    <>
                                                        <button
                                                            onClick={() => setSpendModal({ isOpen: true, accountId: row.account_id, accountName: row.account_name })}
                                                            className="p-2 text-blue-600 bg-blue-50 rounded hover:bg-blue-100 hover:scale-105 transition-all tooltip"
                                                            title="Input Spend"
                                                        >
                                                            <DollarSign size={16} />
                                                        </button>
                                                        <button
                                                            onClick={() => setRoasModal({ isOpen: true, accountId: row.account_id, accountName: row.account_name, currentRoas: row.roas_manual })}
                                                            className="p-2 text-amber-600 bg-amber-50 rounded hover:bg-amber-100 hover:scale-105 transition-all tooltip"
                                                            title="Override ROAS"
                                                        >
                                                            <Edit2 size={16} />
                                                        </button>
                                                    </>
                                                )}
                                                {canAddBudget && (
                                                    <button
                                                        onClick={() => setBudgetModal({
                                                            isOpen: true,
                                                            accountId: row.account_id,
                                                            accountName: row.account_name,
                                                            threshold: row.audience_threshold,
                                                            gapMinutes: row.audience_gap_minutes
                                                        })}
                                                        className="p-2 text-purple-600 bg-purple-50 rounded hover:bg-purple-100 hover:scale-105 transition-all tooltip"
                                                        title="Tambah Modal"
                                                    >
                                                        <PlusCircle size={16} />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* LOGS TABS */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="flex border-b border-slate-200">
                    <TabButton label="Riwayat Spend" active={activeTab === 'spend'} onClick={() => setActiveTab('spend')} />
                    <TabButton label="Riwayat Modal Penonton" active={activeTab === 'audience'} onClick={() => setActiveTab('audience')} />
                    <TabButton label="Riwayat ROAS Manual" active={activeTab === 'roas'} onClick={() => setActiveTab('roas')} />
                </div>

                <div className="p-0 overflow-x-auto max-h-[400px]">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-slate-50 text-slate-500 font-medium sticky top-0">
                            <tr>
                                <th className="px-6 py-3">Waktu</th>
                                <th className="px-6 py-3">Akun</th>
                                <th className="px-6 py-3">
                                    {activeTab === 'spend' ? 'Mata Uang / Tipe' : activeTab === 'audience' ? 'Nominal / Trigger' : 'Nilai Log'}
                                </th>
                                <th className="px-6 py-3">User</th>
                                <th className="px-6 py-3">Catatan</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loadingLogs ? (
                                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-400">Loading logs...</td></tr>
                            ) : logs.length === 0 ? (
                                <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-400">Belum ada riwayat.</td></tr>
                            ) : (
                                logs.map((log: any) => (
                                    <tr key={log.id} className="hover:bg-slate-50">
                                        <td className="px-6 py-3 text-slate-500 text-xs">
                                            {new Date(log.created_at).toLocaleString('id-ID')}
                                        </td>
                                        <td className="px-6 py-3 font-medium text-slate-700">{log.account_name}</td>
                                        <td className="px-6 py-3">
                                            {activeTab === 'spend' && (
                                                <div>
                                                    <div className="font-bold text-slate-700">Rp {log.spend_amount.toLocaleString()}</div>
                                                    <div className="text-xs text-slate-400 capitalize">{log.spend_type}</div>
                                                </div>
                                            )}
                                            {activeTab === 'audience' && (
                                                <div>
                                                    <div className="font-bold text-green-600">+ Rp {log.added_amount.toLocaleString()}</div>
                                                    <div className="text-xs text-slate-400 capitalize">Trigger: {log.trigger_reason}</div>
                                                </div>
                                            )}
                                            {activeTab === 'roas' && (
                                                <div>
                                                    <div className="font-bold text-amber-600">{log.roas_manual}x</div>
                                                    {log.revenue_manual && <div className="text-xs text-slate-400">Rev: {log.revenue_manual}</div>}
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-3 text-slate-600">{log.created_by || "-"}</td>
                                        <td className="px-6 py-3 text-slate-500 italic max-w-[200px] truncate">{log.note || (activeTab === 'audience' ? `Sisa: ${log.remaining_after || '?'}` : "-")}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* MODALS RENDER */}
            {spendModal && (
                <SpendInputModal
                    isOpen={spendModal.isOpen}
                    onClose={() => setSpendModal(null)}
                    date={date}
                    accountId={spendModal.accountId}
                    accountName={spendModal.accountName}
                    onSuccess={() => {
                        fetchData()
                        fetchLogs() // Refresh logs too
                    }}
                />
            )}

            {roasModal && (
                <RoasManualModal
                    isOpen={roasModal.isOpen}
                    onClose={() => setRoasModal(null)}
                    date={date}
                    accountId={roasModal.accountId}
                    accountName={roasModal.accountName}
                    currentRoas={roasModal.currentRoas}
                    onSuccess={() => {
                        fetchData()
                        fetchLogs()
                    }}
                />
            )}

            {budgetModal && (
                <AudienceBudgetModal
                    isOpen={budgetModal.isOpen}
                    onClose={() => setBudgetModal(null)}
                    date={date}
                    accountId={budgetModal.accountId}
                    accountName={budgetModal.accountName}
                    threshold={budgetModal.threshold}
                    gapMinutes={budgetModal.gapMinutes}
                    onSuccess={() => {
                        fetchData()
                        fetchLogs()
                    }}
                />
            )}
        </div>
    )
}

// Helpers Components
const KPICard: React.FC<{ title: string, value: string, icon: React.ReactNode, color: string, subValue?: string }> = ({ title, value, icon, color, subValue }) => (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-start justify-between">
        <div>
            <p className="text-sm text-slate-500 mb-1">{title}</p>
            <h3 className="text-2xl font-bold text-slate-800">{value}</h3>
            {subValue && <p className="text-xs text-slate-400 mt-1">{subValue}</p>}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
            {icon}
        </div>
    </div>
)

const TabButton: React.FC<{ label: string, active: boolean, onClick: () => void }> = ({ label, active, onClick }) => (
    <button
        onClick={onClick}
        className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${active
            ? 'border-blue-600 text-blue-600'
            : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
    >
        {label}
    </button>
)

export default AdsCenter
