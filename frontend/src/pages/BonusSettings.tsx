import React, { useState, useEffect } from 'react'
import { bonusApi, BonusRateRule } from '@/api/bonus'
import { accountApi } from '@/api/accounts'

const BonusSettings: React.FC = () => {
    const [rules, setRules] = useState<BonusRateRule[]>([])
    const [accounts, setAccounts] = useState<any[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [success, setSuccess] = useState<string | null>(null)

    // Form state
    const [formShopId, setFormShopId] = useState<number | null>(null)
    const [formDayType, setFormDayType] = useState<string>('all')
    const [formShiftId, setFormShiftId] = useState<number>(1)
    const [formBonusAmount, setFormBonusAmount] = useState<number>(500)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            setLoading(true)
            const [rulesData, accountsData] = await Promise.all([
                bonusApi.getRates(),
                accountApi.getAll(1)
            ])
            setRules(rulesData)
            setAccounts(accountsData)
        } catch (err: any) {
            setError('Gagal memuat data. Silakan refresh halaman.')
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        try {
            setError(null)
            setSuccess(null)

            const response = await bonusApi.upsertRate({
                shop_id: formShopId,
                day_type: formDayType,
                shift_id: formShiftId,
                bonus_per_order: formBonusAmount,
                is_active: true
            })

            setSuccess(response.message)
            fetchData() // Reload

            // Reset form
            setFormShopId(null)
            setFormDayType('all')
            setFormShiftId(1)
            setFormBonusAmount(500)

            setTimeout(() => setSuccess(null), 3000)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Gagal menyimpan aturan')
        }
    }

    const handleToggleRule = async (ruleId: number, currentStatus: boolean) => {
        try {
            setError(null)

            const response = await bonusApi.updateRateStatus(ruleId, { is_active: !currentStatus })
            setSuccess(response.message)
            fetchData()

            setTimeout(() => setSuccess(null), 3000)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Gagal mengubah status')
        }
    }

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(value)
    }

    const getDayTypeLabel = (dayType: string) => {
        switch (dayType) {
            case 'weekday': return 'Hari Kerja'
            case 'weekend': return 'Weekend'
            case 'all': return 'Semua Hari'
            default: return dayType
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-gray-600">Memuat...</div>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <div className="flex items-center gap-3 mb-1">
                    <h1 className="text-3xl font-bold text-gray-800">Atur Bonus</h1>
                    <div className="group relative">
                        <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
                        <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                            Setting bonus biar hitungan makin rapi.
                        </div>
                    </div>
                </div>
                <p className="text-gray-600 mt-1">Atur rate bonus sesuai akun & hari (weekday/weekend) biar makin fleksibel.</p>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-600">{error}</p>
                </div>
            )}

            {success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-600">{success}</p>
                </div>
            )}

            {/* Form Builder */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Buat Aturan Baru</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Akun Shopee
                            </label>
                            <select
                                value={formShopId || ''}
                                onChange={(e) => setFormShopId(e.target.value ? parseInt(e.target.value) : null)}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            >
                                <option value="">Semua Akun (Global)</option>
                                {accounts.map((account) => (
                                    <option key={account.id} value={account.id}>
                                        {account.account_name || account.shopee_account_id}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Tipe Hari
                            </label>
                            <select
                                value={formDayType}
                                onChange={(e) => setFormDayType(e.target.value)}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            >
                                <option value="all">Semua Hari</option>
                                <option value="weekday">Hari Kerja (Senin-Jumat)</option>
                                <option value="weekend">Weekend (Sabtu-Minggu)</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Shift
                            </label>
                            <select
                                value={formShiftId}
                                onChange={(e) => setFormShiftId(parseInt(e.target.value))}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            >
                                <option value={1}>Shift 1 (Pagi 05:00-10:00)</option>
                                <option value={2}>Shift 2 (Siang 10:00-15:00)</option>
                                <option value={3}>Shift 3 (Sore 15:00-20:00)</option>
                                <option value={4}>Shift 4 (Malam 20:00-00:00)</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Bonus per Order (Rp)
                            </label>
                            <input
                                type="number"
                                value={formBonusAmount}
                                onChange={(e) => setFormBonusAmount(parseInt(e.target.value) || 0)}
                                min="0"
                                step="100"
                                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                required
                            />
                        </div>
                    </div>

                    <div className="flex justify-end">
                        <button
                            type="submit"
                            title="Simpan setting bonus yang kamu atur."
                            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                        >
                            Simpan Aturan
                        </button>
                    </div>
                </form>
            </div>

            {/* Rules Table */}
            <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b border-gray-200">
                    <h2 className="text-lg font-semibold text-gray-800">Aturan yang Sudah Ada</h2>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Akun</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Tipe Hari</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Shift</th>
                                <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Bonus/Order</th>
                                <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Status</th>
                                <th className="px-4 py-3 text-center text-sm font-medium text-gray-700">Aksi</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {rules.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-4 py-12 text-center text-gray-500">
                                        Belum ada aturan bonus nih 😄
                                    </td>
                                </tr>
                            ) : (
                                rules.map((rule) => (
                                    <tr key={rule.id} className="hover:bg-gray-50">
                                        <td className="px-4 py-3 text-sm text-gray-800">{rule.shop_name}</td>
                                        <td className="px-4 py-3 text-sm text-gray-600">{getDayTypeLabel(rule.day_type)}</td>
                                        <td className="px-4 py-3 text-sm text-gray-600">{rule.shift_name}</td>
                                        <td className="px-4 py-3 text-sm text-right font-medium text-gray-800">
                                            {formatCurrency(rule.bonus_per_order)}
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${rule.is_active
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-gray-100 text-gray-800'
                                                }`}>
                                                {rule.is_active ? 'Aktif' : 'Nonaktif'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-center">
                                            <button
                                                onClick={() => handleToggleRule(rule.id, rule.is_active)}
                                                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                            >
                                                {rule.is_active ? 'Nonaktifkan' : 'Aktifkan'}
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

export default BonusSettings
