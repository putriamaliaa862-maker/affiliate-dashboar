import React, { useState, useEffect } from 'react'
import {
  Search,
  Download,
  Filter,
  CheckCircle2,
  Clock,
  AlertCircle,
  Calendar as CalendarIcon
} from 'lucide-react'
import { commissionsApi, PayoutRow, PayoutSummary } from '@/api/commissions'
import { accountApi } from '@/api/accounts'

const Commissions: React.FC = () => {
  // State
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<PayoutRow[]>([])
  const [summary, setSummary] = useState<PayoutSummary | null>(null)
  const [accounts, setAccounts] = useState<any[]>([])

  // Filters
  const [fromDate, setFromDate] = useState('2025-12-17') // Default to match seed data
  const [toDate, setToDate] = useState('2026-01-16')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [accountId, setAccountId] = useState<number | null>(null)

  useEffect(() => {
    fetchAccounts()
    fetchData()
  }, [])

  // Refetch when filters change
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchData()
    }, 500) // Debounce search
    return () => clearTimeout(timer)
  }, [fromDate, toDate, statusFilter, searchQuery, accountId])

  const fetchAccounts = async () => {
    try {
      const res = await accountApi.getAll(1)
      setAccounts(res)
    } catch (err) {
      console.error(err)
    }
  }

  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await commissionsApi.getPayoutHistory({
        from: fromDate,
        to: toDate,
        status: statusFilter === 'all' ? undefined : statusFilter,
        search: searchQuery || undefined,
        account_id: accountId || undefined
      })
      setData(res.rows)
      setSummary(res.summary)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      await commissionsApi.exportCsv({
        from: fromDate,
        to: toDate,
        status: statusFilter === 'all' ? undefined : statusFilter,
        search: searchQuery || undefined,
        account_id: accountId || undefined
      })
    } catch (err) {
      alert('Gagal mengunduh CSV')
    }
  }

  // Formatters
  const formatCurrency = (val: number) =>
    new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val)

  const formatDate = (dateStr: string) =>
    new Date(dateStr).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-green-100 text-green-700 border-green-200'
      case 'pending': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'validating': return 'bg-blue-100 text-blue-700 border-blue-200'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid': return <CheckCircle2 size={16} />
      case 'pending': return <Clock size={16} />
      case 'validating': return <AlertCircle size={16} />
      default: return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold text-slate-800">Riwayat Komisi</h1>
            <div className="group relative">
              <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
              <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                Semua status komisi, biar kamu nggak nebak-nebak.
              </div>
            </div>
          </div>
          <p className="text-slate-500">Cek komisi yang masih diproses sampai yang sudah cair.</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchData}
            title="Update hasil terbaru biar nggak ketinggalan."
            className="px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-700 font-medium transition-colors"
          >
            Refresh
          </button>
          <button
            onClick={handleExport}
            title="Ambil data komisi sesuai filter kamu."
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
          >
            <Download size={18} />
            Unduh CSV
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card
            title="Total Komisi"
            value={summary.total_commission}
            icon={<DollarSignIcon />}
            color="text-slate-700"
          />
          <Card
            title="Sudah Dibayar (Paid)"
            value={summary.paid}
            icon={<CheckCircle2 />}
            color="text-green-600"
            bg="bg-green-50"
          />
          <Card
            title="Menunggu (Pending)"
            value={summary.pending}
            icon={<Clock />}
            color="text-yellow-600"
            bg="bg-yellow-50"
          />
          <Card
            title="Validasi"
            value={summary.validating}
            icon={<AlertCircle />}
            color="text-blue-600"
            bg="bg-blue-50"
          />
        </div>
      )}

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-wrap gap-4 items-center">
        {/* Date Range */}
        <div className="flex items-center gap-2 bg-slate-50 px-3 py-2 rounded-lg border border-slate-200">
          <CalendarIcon size={16} className="text-slate-500" />
          <input
            type="date"
            value={fromDate}
            onChange={e => setFromDate(e.target.value)}
            className="bg-transparent text-sm focus:outline-none w-32"
          />
          <span className="text-slate-400">-</span>
          <input
            type="date"
            value={toDate}
            onChange={e => setToDate(e.target.value)}
            className="bg-transparent text-sm focus:outline-none w-32"
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">Semua Status</option>
          <option value="pending">Pending</option>
          <option value="paid">Paid</option>
          <option value="validating">Validating</option>
        </select>

        {/* Account Filter */}
        <select
          value={accountId || ''}
          onChange={e => setAccountId(e.target.value ? Number(e.target.value) : null)}
          className="px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Semua Akun</option>
          {accounts.map(acc => (
            <option key={acc.id} value={acc.id}>{acc.account_name}</option>
          ))}
        </select>

        {/* Search */}
        <div className="flex-1 min-w-[200px] relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Cari Order ID..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-medium">
              <tr>
                <th className="px-6 py-4">Order ID</th>
                <th className="px-6 py-4">Tanggal Order</th>
                <th className="px-6 py-4">Akun</th>
                <th className="px-6 py-4 text-right">Komisi</th>
                <th className="px-6 py-4 text-center">Status</th>
                <th className="px-6 py-4">Metode Bayar</th>
                <th className="px-6 py-4">Tanggal Bayar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    Memuat data...
                  </td>
                </tr>
              ) : data.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    <p className="text-lg mb-1">Komisi belum muncul. Pastikan datanya sudah diimport.</p>
                    <p className="text-sm">Atau coba ubah filter tanggal/status ya~</p>
                  </td>
                </tr>
              ) : (
                data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-700">{row.order_id}</td>
                    <td className="px-6 py-4 text-slate-600">{formatDate(row.date)}</td>
                    <td className="px-6 py-4 text-slate-600">{row.account_name}</td>
                    <td className="px-6 py-4 text-right font-semibold text-slate-700">
                      {formatCurrency(row.commission_amount)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(row.payout_status)}`}>
                        {getStatusIcon(row.payout_status)}
                        {row.payout_status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">{row.payment_method || '-'}</td>
                    <td className="px-6 py-4 text-slate-600">
                      {row.paid_at ? formatDate(row.paid_at) : '-'}
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

// Simple Components
const Card = ({ title, value, icon, color, bg = 'bg-white' }: any) => (
  <div className={`${bg} p-6 rounded-xl shadow-sm border border-slate-200`}>
    <div className={`flex items-start justify-between ${color}`}>
      <div>
        <p className="text-sm font-medium mb-1 opacity-80">{title}</p>
        <h3 className="text-2xl font-bold">{new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value)}</h3>
      </div>
      <div className="p-2 rounded-lg bg-white/50">{icon}</div>
    </div>
  </div>
)

const DollarSignIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
)

export default Commissions
