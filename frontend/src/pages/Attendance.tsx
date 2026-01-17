import React, { useState, useEffect } from 'react'
import { attendanceApi, Attendance } from '@/api/attendance'
import Modal from '@/components/Modal'
import AttendanceForm from '@/components/forms/AttendanceForm'

const AttendancePage: React.FC = () => {
  const [attendances, setAttendances] = useState<Attendance[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAttendances()
  }, [selectedDate])

  const fetchAttendances = async () => {
    try {
      setLoading(true)
      setError(null)

      const data = await attendanceApi.getAll({
        from: selectedDate,
        to: selectedDate,
      })

      setAttendances(data)
    } catch (err: any) {
      console.error('Failed to fetch attendances:', err)
      setError(err.response?.data?.detail || 'Failed to load attendance records')
    } finally {
      setLoading(false)
    }
  }

  const handleRecordAttendance = () => {
    setIsModalOpen(true)
  }

  const handleSubmit = async (formData: any) => {
    try {
      await attendanceApi.create(formData)
      setIsModalOpen(false)
      fetchAttendances() // Refresh list
      alert('Attendance recorded successfully!')
    } catch (error: any) {
      console.error('Failed to record attendance:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to record attendance'

      // Handle duplicate error (409)
      if (error.response?.status === 409) {
        throw new Error(errorMessage) // Show in form
      } else {
        alert(errorMessage)
      }
      throw error // Re-throw to keep modal open
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present':
        return 'bg-green-100 text-green-800'
      case 'late':
        return 'bg-yellow-100 text-yellow-800'
      case 'absent':
        return 'bg-red-100 text-red-800'
      case 'sick':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-3xl font-bold text-gray-800">Absensi Tim</h1>
            <div className="group relative">
              <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
              <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                Absensi simpel tapi ngaruh banget ke performa.
              </div>
            </div>
          </div>
          <p className="text-gray-500">Catat hadir, izin, atau off biar bonus & evaluasi makin jelas.</p>
        </div>
        <button
          onClick={handleRecordAttendance}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Record Attendance
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Date
          </label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2"
          />
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">
            Loading attendance records...
          </div>
        ) : attendances.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No attendance records for {new Date(selectedDate).toLocaleDateString('id-ID')}.
            <br />
            Click "Record Attendance" to add one.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Employee
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Check In
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Check Out
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-800">
                    Notes
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {attendances.map((att) => (
                  <tr key={att.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-800">
                      {att.employee_name || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(att.date).toLocaleDateString('id-ID')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {att.check_in_time || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {att.check_out_time || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(
                          att.status
                        )}`}
                      >
                        {att.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {att.notes || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Record Attendance"
      >
        <AttendanceForm
          onSubmit={handleSubmit}
          onCancel={() => setIsModalOpen(false)}
        />
      </Modal>
    </div>
  )
}

export default AttendancePage
