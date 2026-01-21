import { useState, useEffect } from 'react';
import {
    getBotStatus,
    getCreatorLiveOverview,
    getAdsOverview,
    BotStatus,
    CreatorLiveOverview,
    AdsOverview
} from '../../services/realtimeApi';

export default function RealtimeMonitor() {
    const [botStatus, setBotStatus] = useState<BotStatus | null>(null);
    const [creatorLive, setCreatorLive] = useState<CreatorLiveOverview | null>(null);
    const [adsData, setAdsData] = useState<AdsOverview | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

    const loadData = async () => {
        try {
            setLoading(true);
            const [status, creator, ads] = await Promise.all([
                getBotStatus(),
                getCreatorLiveOverview(),
                getAdsOverview()
            ]);
            setBotStatus(status);
            setCreatorLive(creator);
            setAdsData(ads);
            setError(null);
            setLastRefresh(new Date());
        } catch (err) {
            setError('Failed to load data. Make sure backend is running.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 30000);
        return () => clearInterval(interval);
    }, []);

    const formatCurrency = (num: number) => {
        return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(num);
    };

    const formatTime = (isoString: string | null) => {
        if (!isoString) return '-';
        return new Date(isoString).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    const getTimeDiff = (isoString: string | null) => {
        if (!isoString) return null;
        const diff = Date.now() - new Date(isoString).getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'Just now';
        if (mins < 60) return `${mins}m ago`;
        return `${Math.floor(mins / 60)}h ago`;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">🤖 Realtime Monitor</h1>
                    <p className="text-sm text-gray-500">
                        Last refresh: {lastRefresh.toLocaleTimeString()}
                    </p>
                </div>
                <button
                    onClick={loadData}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                    {loading ? '⏳' : '🔄'} Refresh
                </button>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    ❌ {error}
                </div>
            )}

            {/* Bot Status Banner */}
            <div className={`p-6 rounded-xl shadow-lg ${botStatus?.is_active
                    ? 'bg-gradient-to-r from-green-500 to-emerald-600'
                    : 'bg-gradient-to-r from-red-500 to-rose-600'
                } text-white`}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className={`w-16 h-16 rounded-full flex items-center justify-center text-3xl ${botStatus?.is_active ? 'bg-green-400' : 'bg-red-400'
                            }`}>
                            {botStatus?.is_active ? '🟢' : '🔴'}
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold">
                                BOT {botStatus?.is_active ? 'ACTIVE' : 'INACTIVE'}
                            </h2>
                            <p className="text-white/80">{botStatus?.message}</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-white/70">Recent Snapshots</p>
                        <p className="text-3xl font-bold">{botStatus?.recent_snapshots_count || 0}</p>
                        <p className="text-sm text-white/70">
                            Last: {getTimeDiff(botStatus?.last_snapshot_at || null)}
                        </p>
                    </div>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Total Accounts */}
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-indigo-500">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Total Accounts</p>
                            <p className="text-3xl font-bold text-indigo-600">
                                {(creatorLive?.total_accounts || 0) + (adsData?.total_accounts || 0)}
                            </p>
                        </div>
                        <div className="text-4xl">👥</div>
                    </div>
                </div>

                {/* Orders Ready */}
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-green-500">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Orders Ready to Ship</p>
                            <p className="text-3xl font-bold text-green-600">
                                {creatorLive?.total_orders_ready || 0}
                            </p>
                        </div>
                        <div className="text-4xl">📦</div>
                    </div>
                </div>

                {/* Total Spend */}
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-red-500">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Ads Spend Today</p>
                            <p className="text-2xl font-bold text-red-600">
                                {formatCurrency(adsData?.total_spend_today || 0)}
                            </p>
                        </div>
                        <div className="text-4xl">💸</div>
                    </div>
                </div>

                {/* Budget */}
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-blue-500">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-500">Budget Available</p>
                            <p className="text-2xl font-bold text-blue-600">
                                {formatCurrency(adsData?.total_budget_available || 0)}
                            </p>
                        </div>
                        <div className="text-4xl">💰</div>
                    </div>
                </div>
            </div>

            {/* Two Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Creator Live Table */}
                <div className="bg-white rounded-xl shadow-md overflow-hidden">
                    <div className="px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            📦 Creator Live - Orders
                        </h3>
                        <p className="text-sm text-white/80">{creatorLive?.total_accounts || 0} accounts</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Shop</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ready</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pending</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Updated</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {creatorLive?.accounts.map((acc, i) => (
                                    <tr key={i} className="hover:bg-gray-50">
                                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                                            {acc.shop_name || acc.shopee_account_id}
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                {acc.orders_ready_to_ship}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                                {acc.pending_orders}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right text-xs text-gray-500">
                                            {formatTime(acc.scraped_at)}
                                        </td>
                                    </tr>
                                ))}
                                {(!creatorLive?.accounts || creatorLive.accounts.length === 0) && (
                                    <tr>
                                        <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                                            No data yet. Start the bot to begin scraping.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Ads Center Table */}
                <div className="bg-white rounded-xl shadow-md overflow-hidden">
                    <div className="px-6 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            📊 Ads Center
                        </h3>
                        <p className="text-sm text-white/80">{adsData?.total_accounts || 0} accounts</p>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Shop</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Spend</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Budget</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Coins</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {adsData?.accounts.map((acc, i) => (
                                    <tr key={i} className="hover:bg-gray-50">
                                        <td className="px-4 py-3 text-sm font-medium text-gray-900">
                                            {acc.shop_name || acc.shopee_account_id}
                                        </td>
                                        <td className="px-4 py-3 text-right text-sm text-red-600 font-medium">
                                            {formatCurrency(acc.spend_today)}
                                        </td>
                                        <td className="px-4 py-3 text-right text-sm text-blue-600 font-medium">
                                            {formatCurrency(acc.budget_available)}
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                                🪙 {acc.coins}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                                {(!adsData?.accounts || adsData.accounts.length === 0) && (
                                    <tr>
                                        <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                                            No data yet. Start the bot to begin scraping.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Quick Start Guide */}
            <div className="bg-gradient-to-r from-gray-700 to-gray-800 rounded-xl p-6 text-white">
                <h3 className="text-lg font-bold mb-4">🚀 Quick Start Guide</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="bg-white/10 rounded-lg p-4">
                        <p className="font-bold mb-2">1️⃣ Setup Bot</p>
                        <code className="text-xs bg-black/30 px-2 py-1 rounded">SETUP_REALTIME_BOT.bat</code>
                    </div>
                    <div className="bg-white/10 rounded-lg p-4">
                        <p className="font-bold mb-2">2️⃣ Configure Accounts</p>
                        <code className="text-xs bg-black/30 px-2 py-1 rounded">bots/.../config/accounts.json</code>
                    </div>
                    <div className="bg-white/10 rounded-lg p-4">
                        <p className="font-bold mb-2">3️⃣ Run 24H</p>
                        <code className="text-xs bg-black/30 px-2 py-1 rounded">RUN_REALTIME_BOT_24H.bat</code>
                    </div>
                </div>
            </div>
        </div>
    );
}
