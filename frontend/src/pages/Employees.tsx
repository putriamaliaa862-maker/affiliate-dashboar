import React, { useState, useEffect } from 'react'
import Modal from '@/components/Modal'
import EmployeeForm from '@/components/forms/EmployeeForm'
import { employeeApi } from '@/api/employees'
import { Employee } from '@/types'

const Employees: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | undefined>()
  const studioId = 1 // Default studio, you can make this dynamic later

  const fetchEmployees = async () => {
    try {
      setLoading(true)
      const data = await employeeApi.getAll(studioId)
      setEmployees(data)
    } catch (error) {
      console.error('Failed to fetch employees:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEmployees()
  }, [])

  const handleAddEmployee = () => {
    setSelectedEmployee(undefined)
    setIsModalOpen(true)
  }

  const handleEditEmployee = (employee: Employee) => {
    setSelectedEmployee(employee)
    setIsModalOpen(true)
  }

  const handleSubmit = async (data: Partial<Employee>) => {
    try {
      if (selectedEmployee) {
        await employeeApi.update(selectedEmployee.id, data)
      } else {
        await employeeApi.create(data as Omit<Employee, 'id' | 'created_at' | 'updated_at'>)
      }
      setIsModalOpen(false)
      fetchEmployees()
    } catch (error) {
      console.error('Failed to save employee:', error)
      alert('Failed to save employee. Please try again.')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this employee?')) return

    try {
      await employeeApi.delete(id)
      fetchEmployees()
    } catch (error) {
      console.error('Failed to delete employee:', error)
      alert('Failed to delete employee. Please try again.')
    }
  }

  const getRoleBadgeColor = (role: string) => {
    const colors = {
      host: 'bg-blue-100 text-blue-800',
      leader: 'bg-green-100 text-green-800',
      supervisor: 'bg-purple-100 text-purple-800',
      director: 'bg-red-100 text-red-800',
    }
    return colors[role as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return <div className="text-center py-8">Loading employees...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-3xl font-bold text-gray-800">Data Tim</h1>
            <div className="group relative">
              <div className="bg-slate-200 hover:bg-slate-300 text-slate-600 rounded-full w-5 h-5 flex items-center justify-center text-xs cursor-help">?</div>
              <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                Semua anggota tim ke-list rapi.
              </div>
            </div>
          </div>
          <p className="text-gray-500">Lihat siapa aja yang aktif, role-nya apa, dan info penting tim kamu.</p>
        </div>
        <button
          onClick={handleAddEmployee}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Add Employee
        </button>
      </div>

      {employees.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No employees found. Click "Add Employee" to create one.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {employees.map((employee) => (
            <div key={employee.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">{employee.name}</h3>
                  <p className="text-sm text-gray-500">{employee.email}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${getRoleBadgeColor(employee.role)}`}>
                  {employee.role}
                </span>
              </div>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                {employee.phone && (
                  <div className="flex justify-between">
                    <span>Phone:</span>
                    <span className="font-medium text-gray-800">{employee.phone}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>Salary:</span>
                  <span className="font-medium text-gray-800">
                    Rp {employee.salary_base.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className={`font-medium ${employee.is_active ? 'text-green-600' : 'text-red-600'}`}>
                    {employee.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleEditEmployee(employee)}
                  className="flex-1 bg-blue-100 text-blue-600 px-3 py-2 rounded hover:bg-blue-200 text-sm font-semibold"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(employee.id)}
                  className="flex-1 bg-red-100 text-red-600 px-3 py-2 rounded hover:bg-red-200 text-sm font-semibold"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedEmployee ? 'Edit Employee' : 'Add Employee'}
      >
        <EmployeeForm
          employee={selectedEmployee}
          studioId={studioId}
          onSubmit={handleSubmit}
          onCancel={() => setIsModalOpen(false)}
        />
      </Modal>
    </div>
  )
}

export default Employees
