import React, { useState, useEffect } from 'react'
import { reportsApi, ReportRow } from '@/api/reports'
import { accountApi } from '@/api/accounts'

const Reports: React.FC = () => {
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null)
  const [accounts, setAccounts] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [reportData, setReportData] = useState<ReportRow[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      const data = await accountApi.getAll(1) // TODO: dynamic studio_id
      setAccounts(data)
    } catch (err) {
      console.error('Failed to fetch accounts:', err)
    }
  }

  const handleGenerateReport = async () => {
    if (!fromDate || !toDate) {
      alert('Please select both From Date and To Date')
      return
    }

    try {
      setLoading(true)
      setError(null)

      const response = await reportsApi.generate({
        from_date: fromDate,
        to_date: toDate,
        account_id: selectedAccountId || undefined,
      })

      setReportData(response.data)
      setSummary(response.summary)
    } catch (err: any) {
      console.error('Failed to generate report:', err)
      setError(err.response?.data?.detail || 'Failed to generate report. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleExportCsv = async () => {
    if (!fromDate || !toDate) {
      alert('Please select both From Date and To Date')
      return
    }

    try {
      setExporting(true)
      setError(null)

      await reportsApi.exportCsv({
        from_date: fromDate,
        to_date: toDate,
        account_id: selectedAccountId || undefined,
      })

      // Success - file downloaded
    } catch (err: any) {
      console.error('Failed to export CSV:', err)
      setError(err.response?.data?.detail || 'Failed to export CSV. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold text-slate-800">Laporan Penjualan</h1>
            <div className="group relative">
              <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
              <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                Rekap harian biar gampang evaluasi.
              </div>
            </div>
          </div>
          <p className="text-slate-500">Lihat total order, GMV, dan komisi dari semua akun dalam satu tempat.</p>
        </div>
        <div className="space-x-2">
          <button
            onClick={handleExportCsv}
            disabled={exporting || !reportData.length}
            title="Download datanya biar gampang dicek di Excel."
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {exporting ? 'Exporting...' : 'Export CSV'}
          </button>
          <button
            onClick={handleGenerateReport}
            disabled={loading}
            title="Gas! Tampilkan laporan sesuai tanggal yang kamu pilih."
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating...' : 'Generate Report'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Report Type
            </label>
            <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
              <option>Sales Report</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Shopee Account
            </label>
            <select
              value={selectedAccountId || ''}
              onChange={(e) => setSelectedAccountId(e.target.value ? parseInt(e.target.value) : null)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            >
              <option value="">All Accounts</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.account_name || account.shopee_account_id}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              From Date *
            </label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              To Date *
            </label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
              required
            />
          </div>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600 font-medium">Total Orders</p>
              <p className="text-2xl font-bold text-blue-800">{summary.total_orders.toLocaleString()}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-green-600 font-medium">Total GMV</p>
              <p className="text-2xl font-bold text-green-800">
                Rp {summary.total_gmv.toLocaleString('id-ID')}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-purple-600 font-medium">Total Commission</p>
              <p className="text-2xl font-bold text-purple-800">
                Rp {summary.total_commission.toLocaleString('id-ID')}
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <p className="text-sm text-orange-600 font-medium">Avg Order Value</p>
              <p className="text-2xl font-bold text-orange-800">
                Rp {summary.avg_order_value.toLocaleString('id-ID')}
              </p>
            </div>
          </div>
        )}

        {/* Report Table */}
        {loading && (
          <div className="text-center py-8 text-gray-500">
            Generating report...
          </div>
        )}

        {!loading && reportData.length === 0 && !error && (
          <div className="text-center py-8 text-gray-500">
            Belum ada data nih. Coba Import Data dulu ya ✨
          </div>
        )}

        {!loading && reportData.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Shopee Account
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Affiliate
                  </th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-gray-800">
                    Orders
                  </th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-gray-800">
                    GMV (Rp)
                  </th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-gray-800">
                    Commission (Rp)
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {reportData.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-800">{row.date}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{row.shopee_account}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{row.affiliate_name}</td>
                    <td className="px-6 py-4 text-sm text-gray-800 text-right">
                      {row.total_orders.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-800 text-right font-semibold">
                      {row.total_gmv.toLocaleString('id-ID')}
                    </td>
                    <td className="px-6 py-4 text-sm text-green-600 text-right font-semibold">
                      {row.total_commission.toLocaleString('id-ID')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default Reports
