import React, { useState, useEffect } from 'react'
import { analyticsApi, BonusShiftResponse, HourlyData } from '@/api/analytics'
import { accountApi } from '@/api/accounts'

const ShiftBonus: React.FC = () => {
    const [date, setDate] = useState(new Date().toISOString().split('T')[0])
    const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null)
    const [accounts, setAccounts] = useState<any[]>([])
    const [loading, setLoading] = useState(false)
    const [activeTab, setActiveTab] = useState<'shift' | 'leaderboard'>('shift')

    // Data states
    const [hourlyData, setHourlyData] = useState<HourlyData[]>([])
    const [bonusData, setBonusData] = useState<BonusShiftResponse | null>(null)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchAccounts()
    }, [])

    const fetchAccounts = async () => {
        try {
            const data = await accountApi.getAll(1)
            setAccounts(data)
        } catch (err) {
            console.error('Failed to fetch accounts:', err)
        }
    }

    const handleFetchData = async () => {
        if (!date) {
            alert('Pilih tanggal dulu ya~')
            return
        }

        try {
            setLoading(true)
            setError(null)

            const params = {
                date,
                ...(selectedAccountId && { shop_id: selectedAccountId })
            }

            // Fetch hourly and bonus data
            const [hourly, bonus] = await Promise.all([
                analyticsApi.getHourlyOrders(params),
                analyticsApi.getBonusShift(params)
            ])

            setHourlyData(hourly)
            setBonusData(bonus)
        } catch (err: any) {
            console.error('Failed to fetch data:', err)
            setError(err.response?.data?.detail || 'Gagal memuat data. Coba lagi ya!')
        } finally {
            setLoading(false)
        }
    }

    const handleReset = () => {
        setDate(new Date().toISOString().split('T')[0])
        setSelectedAccountId(null)
        setHourlyData([])
        setBonusData(null)
        setError(null)
    }

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(value)
    }

    const totalOrders = hourlyData.reduce((sum, h) => sum + h.total_orders, 0)
    const totalGMV = hourlyData.reduce((sum, h) => sum + h.total_gmv, 0)
    const totalCommission = hourlyData.reduce((sum, h) => sum + h.total_commission, 0)

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <div className="flex items-center gap-3 mb-1">
                    <h1 className="text-3xl font-bold text-gray-800">Bonus per Shift</h1>
                    <div className="group relative">
                        <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
                        <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                            Bonus otomatis kebagi per shift biar fair.
                        </div>
                    </div>
                </div>
                <p className="text-gray-600 mt-1">Lihat shift paling gacor, bonus paling gede, dan siapa yang paling kontribusi.</p>
            </div>

            {/* Filter Bar */}
            <div className="bg-white rounded-lg shadow p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Tanggal
                        </label>
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Akun Shopee
                        </label>
                        <select
                            value={selectedAccountId || ''}
                            onChange={(e) => setSelectedAccountId(e.target.value ? parseInt(e.target.value) : null)}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                        >
                            <option value="">Semua Akun</option>
                            {accounts.map((account) => (
                                <option key={account.id} value={account.id}>
                                    {account.account_name || account.shopee_account_id}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="flex items-end gap-2">
                        <button
                            onClick={handleFetchData}
                            disabled={loading}
                            title="Update hasil terbaru biar nggak ketinggalan."
                            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
                        >
                            {loading ? 'Memuat...' : 'Tarik Data'}
                        </button>
                        <button
                            onClick={handleReset}
                            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                        >
                            Reset
                        </button>
                    </div>
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-600">{error}</p>
                </div>
            )}

            {/* Summary Cards */}
            {bonusData && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm text-gray-600">Total Order</div>
                        <div className="text-2xl font-bold text-gray-800 mt-2">{totalOrders}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm text-gray-600">Total GMV</div>
                        <div className="text-2xl font-bold text-gray-800 mt-2">{formatCurrency(totalGMV)}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm text-gray-600">Total Komisi</div>
                        <div className="text-2xl font-bold text-gray-800 mt-2">{formatCurrency(totalCommission)}</div>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6 border-2 border-green-500">
                        <div className="text-sm text-gray-600">Total Bonus</div>
                        <div className="text-2xl font-bold text-green-600 mt-2">{formatCurrency(bonusData.total_bonus)}</div>
                    </div>
                </div>
            )}

            {/* Tabs */}
            {bonusData && (
                <div className="bg-white rounded-lg shadow">
                    <div className="border-b border-gray-200">
                        <div className="flex">
                            <button
                                onClick={() => setActiveTab('shift')}
                                className={`px-6 py-3 font-medium border-b-2 ${activeTab === 'shift'
                                    ? 'border-blue-600 text-blue-600'
                                    : 'border-transparent text-gray-600 hover:text-gray-800'
                                    }`}
                            >
                                Ringkasan Shift
                            </button>
                            <button
                                onClick={() => setActiveTab('leaderboard')}
                                className={`px-6 py-3 font-medium border-b-2 ${activeTab === 'leaderboard'
                                    ? 'border-blue-600 text-blue-600'
                                    : 'border-transparent text-gray-600 hover:text-gray-800'
                                    }`}
                            >
                                Peringkat Host
                            </button>
                        </div>
                    </div>

                    <div className="p-6">
                        {activeTab === 'shift' && (
                            <div>
                                <table className="w-full">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Shift</th>
                                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Jam</th>
                                            <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Orders</th>
                                            <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Bonus/Order</th>
                                            <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Total Bonus</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200">
                                        {bonusData.shift_results.map((shift) => (
                                            <tr key={shift.shift_id} className="hover:bg-gray-50">
                                                <td className="px-4 py-3 text-sm text-gray-800">{shift.shift_name}</td>
                                                <td className="px-4 py-3 text-sm text-gray-600">-</td>
                                                <td className="px-4 py-3 text-sm text-right text-gray-800">{shift.total_orders}</td>
                                                <td className="px-4 py-3 text-sm text-right text-gray-600">
                                                    {formatCurrency(shift.bonus_per_order)}
                                                </td>
                                                <td className="px-4 py-3 text-sm text-right font-medium text-green-600">
                                                    {formatCurrency(shift.bonus_amount)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {activeTab === 'leaderboard' && (
                            <div className="text-center py-12 text-gray-500">
                                <p className="text-lg">Belum ada data leaderboard host nih 😄</p>
                                <p className="text-sm mt-2">Fitur ini akan aktif setelah data host tersedia</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!bonusData && !loading && !error && (
                <div className="bg-white rounded-lg shadow p-12 text-center">
                    <p className="text-gray-500 text-lg">Belum ada order yang masuk untuk tanggal ini.</p>
                    <p className="text-gray-400 mt-2">Pilih tanggal dan klik "Tarik Data" untuk melihat bonus shift</p>
                </div>
            )}
        </div>
    )
}

export default ShiftBonus
