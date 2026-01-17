import api from '@/api/client'
import { Employee } from '@/types'

export const employeeApi = {
  getAll: async (studioId: number) => {
    const response = await api.get(`/employees?studio_id=${studioId}`)
    return response.data
  },

  getById: async (id: number) => {
    const response = await api.get(`/employees/${id}`)
    return response.data
  },

  create: async (data: Omit<Employee, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await api.post('/employees', data)
    return response.data
  },

  update: async (id: number, data: Partial<Employee>) => {
    const response = await api.put(`/employees/${id}`, data)
    return response.data
  },

  delete: async (id: number) => {
    await api.delete(`/employees/${id}`)
  },
}
