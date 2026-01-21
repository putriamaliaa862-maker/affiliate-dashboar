import React, { useState, useEffect } from 'react'
import { AttendanceCreate } from '@/api/attendance'
import { employeeApi } from '@/api/employees'
import { Employee } from '@/types'

interface AttendanceFormProps {
    onSubmit: (data: AttendanceCreate) => Promise<void>
    onCancel: () => void
}

const AttendanceForm: React.FC<AttendanceFormProps> = ({ onSubmit, onCancel }) => {
    const [employees, setEmployees] = useState<Employee[]>([])
    const [loading, setLoading] = useState(false)
    const [loadingEmployees, setLoadingEmployees] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const [formData, setFormData] = useState<AttendanceCreate>({
        employee_id: 0,
        date: new Date().toISOString().split('T')[0],
        check_in_time: '09:00:00',
        check_out_time: undefined,
        status: 'present',
        notes: '',
    })

    useEffect(() => {
        fetchEmployees()
    }, [])

    const fetchEmployees = async () => {
        try {
            setLoadingEmployees(true)
            const data = await employeeApi.getAll(1) // TODO: dynamic studio_id
            setEmployees(data)
            if (data.length > 0) {
                setFormData((prev) => ({ ...prev, employee_id: data[0].id }))
            }
        } catch (err: any) {
            console.error('Failed to fetch employees:', err)
            setError('Failed to load employees')
        } finally {
            setLoadingEmployees(false)
        }
    }

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
    ) => {
        const { name, value } = e.target
        setFormData((prev) => ({
            ...prev,
            [name]: name === 'employee_id' ? parseInt(value) : value,
        }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            // Validation
            if (!formData.employee_id) {
                throw new Error('Please select an employee')
            }

            if (!formData.date) {
                throw new Error('Date is required')
            }

            if (!formData.check_in_time) {
                throw new Error('Check-in time is required')
            }

            await onSubmit(formData)
        } catch (err: any) {
            setError(err.message || 'Failed to record attendance')
        } finally {
            setLoading(false)
        }
    }

    if (loadingEmployees) {
        return (
            <div className="p-8 text-center text-gray-500">
                Loading employees...
            </div>
        )
    }

    if (employees.length === 0) {
        return (
            <div className="p-8 text-center">
                <p className="text-gray-500 mb-4">No employees found. Please create employees first.</p>
                <button
                    onClick={onCancel}
                    className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
                >
                    Close
                </button>
            </div>
        )
    }

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
                <div className="bg-red-50 border border-red-200 rounded p-3">
                    <p className="text-red-600 text-sm">{error}</p>
                </div>
            )}

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Employee *
                </label>
                <select
                    name="employee_id"
                    value={formData.employee_id}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                >
                    <option value="">Select Employee</option>
                    {employees.map((emp) => (
                        <option key={emp.id} value={emp.id}>
                            {emp.name} - {emp.role}
                        </option>
                    ))}
                </select>
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date *
                </label>
                <input
                    type="date"
                    name="date"
                    value={formData.date}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Check-in Time *
                </label>
                <input
                    type="time"
                    name="check_in_time"
                    value={formData.check_in_time}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                />
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Check-out Time
                </label>
                <input
                    type="time"
                    name="check_out_time"
                    value={formData.check_out_time || ''}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Optional - leave empty if still working</p>
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status *
                </label>
                <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                >
                    <option value="present">Present</option>
                    <option value="late">Late</option>
                    <option value="absent">Absent</option>
                    <option value="sick">Sick</option>
                </select>
            </div>

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes
                </label>
                <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Optional notes..."
                />
            </div>

            <div className="flex gap-3 pt-4">
                <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-semibold"
                >
                    {loading ? 'Recording...' : 'Record Attendance'}
                </button>
                <button
                    type="button"
                    onClick={onCancel}
                    disabled={loading}
                    className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 font-semibold"
                >
                    Cancel
                </button>
            </div>
        </form>
    )
}

export default AttendanceForm
