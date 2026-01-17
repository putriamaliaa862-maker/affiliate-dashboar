import React, { useState, useEffect } from 'react'
import api from '@/api/client'

interface ActivityLog {
    id: number
    user_id: number
    action: string
    entity_type?: string
    entity_id?: number
    ip_address?: string
    created_at: string
}

const ActivityLogs: React.FC = () => {
    const [logs, setLogs] = useState<ActivityLog[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchLogs()
    }, [])

    const fetchLogs = async () => {
        try {
            setLoading(true)
            setError(null)
            const response = await api.get('/activity-logs')
            setLogs(response.data)
        } catch (err: any) {
            console.error('Failed to fetch activity logs:', err)
            setError(err.response?.data?.detail || 'Failed to load activity logs')
        } finally {
            setLoading(false)
        }
    }

    const getActionBadgeColor = (action: string) => {
        const colors: Record<string, string> = {
            login: 'bg-green-100 text-green-800',
            logout: 'bg-gray-100 text-gray-800',
            create: 'bg-blue-100 text-blue-800',
            update: 'bg-yellow-100 text-yellow-800',
            delete: 'bg-red-100 text-red-800',
        }
        return colors[action.toLowerCase()] || 'bg-gray-100 text-gray-800'
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('id-ID', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        })
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="text-gray-500">Loading activity logs...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600">{error}</p>
                <button
                    onClick={fetchLogs}
                    className="mt-2 text-red-700 hover:text-red-900 underline"
                >
                    Try again
                </button>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-3xl font-bold text-gray-800">Log Aktivitas</h1>
                        <div className="group relative">
                            <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
                            <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                                Rekaman jejak digital tim kamu.
                            </div>
                        </div>
                    </div>
                    <p className="text-gray-500">Pantau siapa ngapain aja di dashboard, biar nggak ada drama.</p>
                </div>
                <button
                    onClick={fetchLogs}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                    Refresh
                </button>
            </div>

            {logs.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                    No activity logs found.
                </div>
            ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Time
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    User ID
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Action
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    Entity
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                    IP Address
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {logs.map((log) => (
                                <tr key={log.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {formatDate(log.created_at)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        {log.user_id}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 rounded text-xs font-semibold ${getActionBadgeColor(log.action)}`}>
                                            {log.action}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {log.entity_type || '-'} {log.entity_id ? `#${log.entity_id}` : ''}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {log.ip_address || '-'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}

export default ActivityLogs
