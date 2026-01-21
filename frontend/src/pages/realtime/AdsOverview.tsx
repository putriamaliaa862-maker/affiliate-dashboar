import { useState, useEffect } from 'react';
import { getAdsOverview, AdsOverview } from '../../services/realtimeApi';

export default function AdsOverviewPage() {
    const [data, setData] = useState<AdsOverview | null>(null);
    const [loading, setLoading] = useState(true);
    const [sortField, setSortField] = useState<'spend_today' | 'budget_available' | 'coins'>('spend_today');
    const [sortAsc, setSortAsc] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const result = await getAdsOverview();
                setData(result);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        load();
        const interval = setInterval(load, 30000);
        return () => clearInterval(interval);
    }, []);

    const formatCurrency = (num: number) => {
        return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(num);
    };

    const sortedAccounts = data?.accounts.slice().sort((a, b) => {
        const diff = (b[sortField] || 0) - (a[sortField] || 0);
        return sortAsc ? -diff : diff;
    }) || [];

    const toggleSort = (field: 'spend_today' | 'budget_available' | 'coins') => {
        if (sortField === field) {
            setSortAsc(!sortAsc);
        } else {
            setSortField(field);
            setSortAsc(false);
        }
    };

    if (loading) {
        return <div className="p-6">Loading Ads data...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">📊 Ads Center Overview</h1>
                <span className="text-sm text-gray-500">
                    Last update: {data?.last_updated ? new Date(data.last_updated).toLocaleString() : '-'}
                </span>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white p-6 rounded-xl shadow-md">
                    <p className="text-gray-500">Total Accounts</p>
                    <p className="text-4xl font-bold text-gray-900">{data?.total_accounts || 0}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-red-500">
                    <p className="text-gray-500">Total Spend Today</p>
                    <p className="text-2xl font-bold text-red-600">{formatCurrency(data?.total_spend_today || 0)}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-blue-500">
                    <p className="text-gray-500">Total Budget</p>
                    <p className="text-2xl font-bold text-blue-600">{formatCurrency(data?.total_budget_available || 0)}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-yellow-500">
                    <p className="text-gray-500">Total Coins</p>
                    <p className="text-3xl font-bold text-yellow-600">🪙 {(data?.total_coins || 0).toLocaleString()}</p>
                </div>
            </div>

            {/* Accounts Table */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-100">
                        <tr>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">#</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Shop Name</th>
                            <th
                                className="px-6 py-4 text-right text-sm font-semibold text-gray-700 cursor-pointer hover:bg-gray-200"
                                onClick={() => toggleSort('spend_today')}
                            >
                                Spend Today {sortField === 'spend_today' && (sortAsc ? '↑' : '↓')}
                            </th>
                            <th
                                className="px-6 py-4 text-right text-sm font-semibold text-gray-700 cursor-pointer hover:bg-gray-200"
                                onClick={() => toggleSort('budget_available')}
                            >
                                Budget {sortField === 'budget_available' && (sortAsc ? '↑' : '↓')}
                            </th>
                            <th
                                className="px-6 py-4 text-right text-sm font-semibold text-gray-700 cursor-pointer hover:bg-gray-200"
                                onClick={() => toggleSort('coins')}
                            >
                                Coins {sortField === 'coins' && (sortAsc ? '↑' : '↓')}
                            </th>
                            <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">Last Scrape</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {sortedAccounts.map((acc, i) => (
                            <tr key={i} className="hover:bg-gray-50">
                                <td className="px-6 py-4 text-sm text-gray-500">{i + 1}</td>
                                <td className="px-6 py-4 text-sm font-medium text-gray-900">{acc.shop_name || acc.shopee_account_id}</td>
                                <td className="px-6 py-4 text-right">
                                    <span className={`text-sm font-bold ${acc.spend_today > 100000 ? 'text-red-600' :
                                            acc.spend_today > 0 ? 'text-red-400' :
                                                'text-gray-400'
                                        }`}>
                                        {formatCurrency(acc.spend_today)}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-right text-sm font-bold text-blue-600">
                                    {formatCurrency(acc.budget_available)}
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-bold bg-yellow-100 text-yellow-800">
                                        🪙 {acc.coins.toLocaleString()}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-right text-sm text-gray-500">
                                    {acc.scraped_at ? new Date(acc.scraped_at).toLocaleTimeString() : '-'}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {sortedAccounts.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        No data yet. Start the Playwright bot to begin scraping.
                    </div>
                )}
            </div>
        </div>
    );
}
