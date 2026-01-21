import { useState, useEffect } from 'react';
import { getCreatorLiveOverview, CreatorLiveOverview } from '../../services/realtimeApi';

export default function CreatorLiveOverviewPage() {
    const [data, setData] = useState<CreatorLiveOverview | null>(null);
    const [loading, setLoading] = useState(true);
    const [sortField, setSortField] = useState<'orders_ready_to_ship' | 'pending_orders'>('orders_ready_to_ship');
    const [sortAsc, setSortAsc] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const result = await getCreatorLiveOverview();
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

    const sortedAccounts = data?.accounts.slice().sort((a, b) => {
        const diff = (b[sortField] || 0) - (a[sortField] || 0);
        return sortAsc ? -diff : diff;
    }) || [];

    const toggleSort = (field: 'orders_ready_to_ship' | 'pending_orders') => {
        if (sortField === field) {
            setSortAsc(!sortAsc);
        } else {
            setSortField(field);
            setSortAsc(false);
        }
    };

    if (loading) {
        return <div className="p-6">Loading Creator Live data...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">📦 Creator Live - Orders Overview</h1>
                <span className="text-sm text-gray-500">
                    Last update: {data?.last_updated ? new Date(data.last_updated).toLocaleString() : '-'}
                </span>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-6 rounded-xl shadow-md">
                    <p className="text-gray-500">Total Accounts</p>
                    <p className="text-4xl font-bold text-gray-900">{data?.total_accounts || 0}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-green-500">
                    <p className="text-gray-500">Total Ready to Ship</p>
                    <p className="text-4xl font-bold text-green-600">{data?.total_orders_ready || 0}</p>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-md border-l-4 border-yellow-500">
                    <p className="text-gray-500">Total Pending</p>
                    <p className="text-4xl font-bold text-yellow-600">{data?.total_pending || 0}</p>
                </div>
            </div>

            {/* Accounts Table */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-100">
                        <tr>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">#</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Shop Name</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Account ID</th>
                            <th
                                className="px-6 py-4 text-right text-sm font-semibold text-gray-700 cursor-pointer hover:bg-gray-200"
                                onClick={() => toggleSort('orders_ready_to_ship')}
                            >
                                Ready to Ship {sortField === 'orders_ready_to_ship' && (sortAsc ? '↑' : '↓')}
                            </th>
                            <th
                                className="px-6 py-4 text-right text-sm font-semibold text-gray-700 cursor-pointer hover:bg-gray-200"
                                onClick={() => toggleSort('pending_orders')}
                            >
                                Pending {sortField === 'pending_orders' && (sortAsc ? '↑' : '↓')}
                            </th>
                            <th className="px-6 py-4 text-right text-sm font-semibold text-gray-700">Last Scrape</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y">
                        {sortedAccounts.map((acc, i) => (
                            <tr key={i} className="hover:bg-gray-50">
                                <td className="px-6 py-4 text-sm text-gray-500">{i + 1}</td>
                                <td className="px-6 py-4 text-sm font-medium text-gray-900">{acc.shop_name || '-'}</td>
                                <td className="px-6 py-4 text-sm text-gray-500 font-mono">{acc.shopee_account_id}</td>
                                <td className="px-6 py-4 text-right">
                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${acc.orders_ready_to_ship > 10 ? 'bg-green-500 text-white' :
                                            acc.orders_ready_to_ship > 0 ? 'bg-green-100 text-green-800' :
                                                'bg-gray-100 text-gray-500'
                                        }`}>
                                        {acc.orders_ready_to_ship}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${acc.pending_orders > 5 ? 'bg-yellow-500 text-white' :
                                            acc.pending_orders > 0 ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-gray-100 text-gray-500'
                                        }`}>
                                        {acc.pending_orders}
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
