import React, { useState } from 'react'
import { X, PlusCircle, AlertTriangle } from 'lucide-react'
import { adsApi } from '@/api/ads'

interface AudienceBudgetModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess: () => void
    date: string
    accountId: number
    accountName: string
    threshold: number
    gapMinutes: number
}

const AudienceBudgetModal: React.FC<AudienceBudgetModalProps> = ({
    isOpen, onClose, onSuccess, date, accountId, accountName, threshold, gapMinutes
}) => {
    const [amount, setAmount] = useState<string>('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [gapError, setGapError] = useState<boolean>(false)

    if (!isOpen) return null

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setGapError(false)

        try {
            await adsApi.addAudienceBudget({
                date,
                account_id: accountId,
                added_amount: parseInt(amount.replace(/\D/g, '')),
                remaining_before: undefined // Optional, backend will rely on logs if not provided or just log 'manual'
            })
            onSuccess()
            onClose()
            setAmount('')
        } catch (err: any) {
            console.error(err)
            if (err.response?.status === 409) {
                setGapError(true)
                setError(err.response?.data?.detail || "Sedang cooldown, tunggu bentar ya! ⏳")
            } else {
                setError(err.response?.data?.detail || "Gagal tambah modal 😭")
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 transform transition-all scale-100">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-xl font-bold text-slate-800">Tambah Modal Penonton</h3>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
                        <X size={24} />
                    </button>
                </div>

                <div className="mb-4 p-3 bg-purple-50 rounded-lg border border-purple-100">
                    <div className="text-sm text-purple-900 font-medium mb-1">{accountName}</div>
                    <div className="flex gap-4 text-xs text-purple-700">
                        <div className='flex flex-col'>
                            <span className='opacity-75'>Threshold</span>
                            <span className='font-bold'>Rp {threshold.toLocaleString()}</span>
                        </div>
                        <div className='flex flex-col'>
                            <span className='opacity-75'>Min Gap</span>
                            <span className='font-bold'>{gapMinutes} menit</span>
                        </div>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Tambah Saldo (Rp)
                        </label>
                        <input
                            type="number"
                            required
                            min="1000"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all font-bold text-lg"
                            placeholder="0"
                            autoFocus
                        />
                    </div>

                    {error && (
                        <div className={`p-3 rounded-lg border flex items-start gap-2 text-sm ${gapError ? 'bg-orange-50 border-orange-200 text-orange-800' : 'bg-red-50 border-red-100 text-red-600'}`}>
                            {gapError ? <AlertTriangle size={18} className="shrink-0 mt-0.5" /> : <span>⚠️</span>}
                            <span>{error}</span>
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
                            className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    <PlusCircle size={18} />
                                    Tambah
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default AudienceBudgetModal
