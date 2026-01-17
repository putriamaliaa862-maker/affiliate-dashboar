import React, { useState } from 'react'
import { X, Save } from 'lucide-react'
import { adsApi } from '@/api/ads'

interface RoasManualModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess: () => void
    date: string
    accountId: number
    accountName: string
    currentRoas?: number | null
}

const RoasManualModal: React.FC<RoasManualModalProps> = ({ isOpen, onClose, onSuccess, date, accountId, accountName, currentRoas }) => {
    const [roas, setRoas] = useState<string>(currentRoas ? currentRoas.toString() : '')
    const [revenue, setRevenue] = useState<string>('')
    const [note, setNote] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    if (!isOpen) return null

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            await adsApi.upsertMetrics({
                date,
                account_id: accountId,
                roas_manual: roas ? parseFloat(roas) : null,
                revenue_manual: revenue ? parseInt(revenue.replace(/\D/g, '')) : undefined,
                note
            })
            onSuccess()
            onClose()
        } catch (err: any) {
            console.error(err)
            setError(err.response?.data?.detail || "Gagal update ROAS 😭")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 transform transition-all scale-100">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-slate-800">Manual ROAS Override</h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
                        <X size={24} />
                    </button>
                </div>

                <div className="mb-4 p-3 bg-amber-50 rounded-lg border border-amber-100 text-amber-800 text-sm">
                    <div className="font-medium mb-1">Perhatian:</div>
                    Input ini akan menimpa perhitungan ROAS otomatis (GMV/Spend). Gunakan jika data otomatis tidak akurat atau tidak tersedia.
                </div>

                <div className="mb-4 p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="text-sm text-slate-800 font-medium">{accountName}</div>
                    <div className="text-xs text-slate-600">{date}</div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            ROAS Manual (x)
                        </label>
                        <input
                            type="number"
                            step="0.01"
                            required
                            value={roas}
                            onChange={(e) => setRoas(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none transition-all"
                            placeholder="Contoh: 12.5"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Revenue Manual (Opsional)
                        </label>
                        <input
                            type="number"
                            value={revenue}
                            onChange={(e) => setRevenue(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none placeholder:text-slate-400"
                            placeholder="Masukkan omzet manual jika ada"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Catatan
                        </label>
                        <textarea
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none transition-all"
                            placeholder="Alasan override..."
                            rows={2}
                        />
                    </div>

                    {error && (
                        <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100 flex items-center gap-2">
                            <span>⚠️ {error}</span>
                        </div>
                    )}

                    <div className="flex gap-3 pt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors font-medium"
                        >
                            Batal
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    <Save size={18} />
                                    Simpan
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default RoasManualModal
