import React, { useState, useEffect } from 'react'
import liveProductsApi, { LiveProductSnapshot, LiveSyncLog } from '@/api/liveProducts'
import api from '@/api/client'
import { useAuth } from '@/hooks/useAuth'

const LiveProducts: React.FC = () => {
    const { user } = useAuth()
    const [activeTab, setActiveTab] = useState<'snapshots' | 'ranking' | 'logs'>('snapshots')
    const [products, setProducts] = useState<LiveProductSnapshot[]>([])
    const [logs, setLogs] = useState<LiveSyncLog[]>([])
    const [ranking, setRanking] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [syncing, setSyncing] = useState(false)

    // Filters
    const [selectedDate, setSelectedDate] = useState<string>(getTodayDate())
    const [selectedAccount, setSelectedAccount] = useState<string>('')
    const [accounts, setAccounts] = useState<any[]>([])

    // RBAC: Check if user can sync
    const canSync = user && !['host', 'affiliate'].includes(user.role.toLowerCase().replace(' ', '_'))

    // Fetch accounts on mount
    useEffect(() => {
        const loadAccounts = async () => {
            try {
                const res = await api.get('/shopee-accounts')
                setAccounts(res.data)
            } catch (err) {
                console.error('Failed to load accounts:', err)
            }
        }
        loadAccounts()
    }, [])

    useEffect(() => {
        fetchData()
    }, [selectedDate, selectedAccount, activeTab])

    const fetchData = async () => {
        try {
            setLoading(true)

            const accountId = selectedAccount ? parseInt(selectedAccount) : undefined

            if (activeTab === 'snapshots') {
                const data = await liveProductsApi.getDailySnapshots(selectedDate, accountId)
                setProducts(data)
            } else if (activeTab === 'ranking') {
                const data = await liveProductsApi.getRanking(selectedDate, accountId)
                setRanking(data)
            } else if (activeTab === 'logs') {
                const data = await liveProductsApi.getSyncLogs(accountId)
                setLogs(data)
            }
        } catch (error: any) {
            console.error('Failed to fetch live products:', error)
            if (error.response?.status === 403) {
                alert('Akses ditolak. Cek role kamu ya!')
            }
        } finally {
            setLoading(false)
        }
    }

    const handleRefresh = () => {
        fetchData()
    }

    const handleManualSync = async () => {
        if (!canSync) {
            alert('Host gak bisa sync. Minta tolong Leader ya buat sync 🙏')
            return
        }

        setSyncing(true)
        try {
            alert('Buka halaman Shopee Seller product list, lalu klik extension icon untuk sync manual.')
        } catch (error) {
            alert('Sync manual harus lewat extension. Buka Shopee Seller ya!')
        } finally {
            setSyncing(false)
        }
    }

    const getStatusBadge = (product: LiveProductSnapshot, prevProduct?: LiveProductSnapshot) => {
        // Calculate DROP status (if sold/GMV down >40% from yesterday)
        if (prevProduct) {
            const soldChange = prevProduct.sold_qty > 0
                ? ((product.sold_qty - prevProduct.sold_qty) / prevProduct.sold_qty) * 100
                : 0
            const gmvChange = prevProduct.gmv > 0
                ? ((product.gmv - prevProduct.gmv) / prevProduct.gmv) * 100
                : 0

            if (soldChange < -40 || gmvChange < -40) {
                return <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 border border-red-300">DROP 📉</span>
            }
            if (soldChange > 50 || gmvChange > 50) {
                return <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 border border-green-300">GACOR 🔥</span>
            }
        }

        // Fallback: GACOR if sold > 20 or GMV > 1M
        if (product.sold_qty > 20 || product.gmv > 1000000) {
            return <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 border border-green-300">GACOR 🔥</span>
        }

        return <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700 border border-gray-300">STABIL</span>
    }

    const formatRupiah = (amount: number) => {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount)
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow-lg p-6 text-white">
                <h1 className="text-3xl font-bold mb-2">Produk Live Hari Ini</h1>
                <p className="text-purple-100">Lihat mana yang gacor, mana yang drop. Biar besok live makin cuan 😈</p>
            </div>

            {/* Filters & Actions */}
            <div className="bg-white rounded-lg shadow p-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Tanggal</label>
                        <input
                            type="date"
                            value={selectedDate}
                            onChange={(e) => setSelectedDate(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Akun Shopee</label>
                        <select
                            value={selectedAccount}
                            onChange={(e) => setSelectedAccount(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="">Semua Akun</option>
                            {accounts.map(acc => (
                                <option key={acc.id} value={acc.id}>{acc.account_name}</option>
                            ))}
                        </select>
                    </div>
                    <div className="flex items-end">
                        <button
                            onClick={handleRefresh}
                            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            🔄 Refresh Data
                        </button>
                    </div>
                    <div className="flex items-end">
                        <button
                            onClick={handleManualSync}
                            disabled={syncing || !canSync}
                            title={!canSync ? 'Host gak bisa sync, minta Leader ya' : 'Sync via Extension'}
                            className={`w-full px-4 py-2 rounded-lg transition-colors ${canSync
                                ? 'bg-green-600 text-white hover:bg-green-700'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                }`}
                        >
                            {syncing ? 'Syncing...' : '⚡ Sync Sekarang'}
                        </button>
                    </div>
                </div>
            </div>

            {/* KPI Cards - Daily Summary */}
            {activeTab === 'snapshots' && products.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-white rounded-lg shadow p-6">
                    <div className="text-center">
                        <p className="text-sm text-gray-500 mb-1">Total Produk</p>
                        <h3 className="text-3xl font-bold text-gray-900">{products.length}</h3>
                    </div>
                    <div className="text-center">
                        <p className="text-sm text-gray-500 mb-1">Total Terjual</p>
                        <h3 className="text-3xl font-bold text-green-600">{products.reduce((sum, p) => sum + p.sold_qty, 0).toLocaleString('id-ID')}</h3>
                    </div>
                    <div className="text-center">
                        <p className="text-sm text-gray-500 mb-1">Total GMV</p>
                        <h3 className="text-3xl font-bold text-blue-600">{formatRupiah(products.reduce((sum, p) => sum + p.gmv, 0))}</h3>
                    </div>
                    <div className="text-center">
                        <p className="text-sm text-gray-500 mb-1">Produk Gacor 🔥</p>
                        <h3 className="text-3xl font-bold text-purple-600">{products.filter(p => p.sold_qty > 20 || p.gmv > 1000000).length}</h3>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="bg-white rounded-lg shadow">
                <div className="border-b border-gray-200">
                    <nav className="flex -mb-px">
                        <button
                            onClick={() => setActiveTab('snapshots')}
                            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${activeTab === 'snapshots'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            📊 Snapshot Produk
                        </button>
                        <button
                            onClick={() => setActiveTab('ranking')}
                            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${activeTab === 'ranking'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            🏆 Ranking Hari Ini
                        </button>
                        <button
                            onClick={() => setActiveTab('logs')}
                            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${activeTab === 'logs'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                }`}
                        >
                            📝 Log Sync
                        </button>
                    </nav>
                </div>

                <div className="p-6">
                    {loading ? (
                        <div className="text-center py-12">
                            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            <p className="mt-2 text-gray-500">Loading...</p>
                        </div>
                    ) : (
                        <>
                            {/* Tab: Snapshots */}
                            {activeTab === 'snapshots' && (
                                <div className="overflow-x-auto">
                                    {products.length === 0 ? (
                                        <div className="text-center py-12 bg-gray-50 rounded-lg">
                                            <p className="text-gray-600 text-lg mb-2">Belum ada data produk nih 🤔</p>
                                            <p className="text-gray-500 text-sm">Buka Shopee Live Seller, terus tekan <strong>Sync Sekarang</strong> atau tunggu autosync dari extension ya!</p>
                                        </div>
                                    ) : (
                                        <table className="min-w-full divide-y divide-gray-200">
                                            <thead className="bg-gray-50">
                                                <tr>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Produk</th>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Terjual</th>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">GMV</th>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Klik</th>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                                </tr>
                                            </thead>
                                            <tbody className="bg-white divide-y divide-gray-200">
                                                {products.map((product) => (
                                                    <tr key={product.id} className="hover:bg-gray-50">
                                                        <td className="px-6 py-4">
                                                            <div className="text-sm font-medium text-gray-900">{product.product_name}</div>
                                                            <div className="text-sm text-gray-500">ID: {product.product_id}</div>
                                                        </td>
                                                        <td className="px-6 py-4 text-sm text-gray-900">{product.sold_qty.toLocaleString('id-ID')}</td>
                                                        <td className="px-6 py-4 text-sm text-gray-900">{formatRupiah(product.gmv)}</td>
                                                        <td className="px-6 py-4 text-sm text-gray-500">{product.clicks || '-'}</td>
                                                        <td className="px-6 py-4">{getStatusBadge(product)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    )}
                                </div>
                            )}

                            {/* Tab: Ranking */}
                            {activeTab === 'ranking' && (
                                <>
                                    {!ranking || (ranking.top_by_gmv?.length === 0 && ranking.top_by_sold?.length === 0) ? (
                                        <div className="text-center py-12 bg-gray-50 rounded-lg">
                                            <p className="text-gray-600 text-lg mb-2">Belum ada data ranking 📊</p>
                                            <p className="text-gray-500 text-sm">Sync dulu ya biar ada data!</p>
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div>
                                                <h3 className="text-lg font-bold mb-4">🏆 Top 10 by GMV</h3>
                                                <div className="space-y-2">
                                                    {ranking.top_by_gmv?.map((item: any, idx: number) => (
                                                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                                                            <div className="flex items-center gap-3">
                                                                <span className="text-2xl font-bold text-gray-400">#{idx + 1}</span>
                                                                <div>
                                                                    <div className="font-medium text-gray-900">{item.product_name}</div>
                                                                    <div className="text-sm text-gray-500">{formatRupiah(item.gmv)}</div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-bold mb-4">🔥 Top 10 by Terjual</h3>
                                                <div className="space-y-2">
                                                    {ranking.top_by_sold?.map((item: any, idx: number) => (
                                                        <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                                                            <div className="flex items-center gap-3">
                                                                <span className="text-2xl font-bold text-gray-400">#{idx + 1}</span>
                                                                <div>
                                                                    <div className="font-medium text-gray-900">{item.product_name}</div>
                                                                    <div className="text-sm text-gray-500">{item.sold_qty} terjual</div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}

                            {/* Tab: Logs */}
                            {activeTab === 'logs' && (
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tanggal</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Jam Sync</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Rows</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Message</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {logs.map((log) => (
                                                <tr key={log.id} className="hover:bg-gray-50">
                                                    <td className="px-6 py-4 text-sm">{log.snapshot_date}</td>
                                                    <td className="px-6 py-4 text-sm">{new Date(log.synced_at).toLocaleTimeString('id-ID')}</td>
                                                    <td className="px-6 py-4">
                                                        <span className={`px-2 py-1 text-xs rounded-full ${log.status === 'SUCCESS' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                            }`}>
                                                            {log.status}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 text-sm">{log.total_rows}</td>
                                                    <td className="px-6 py-4 text-sm text-gray-500">{log.message || '-'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}

function getTodayDate(): string {
    return new Date().toISOString().split('T')[0]
}

export default LiveProducts
