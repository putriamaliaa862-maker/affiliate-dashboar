import api from '@/api/client'

export interface Attendance {
  id: number
  employee_id: number
  employee_name?: string
  date: string  // YYYY-MM-DD
  check_in_time?: string  // HH:MM:SS
  check_out_time?: string  // HH:MM:SS
  status: 'present' | 'late' | 'absent' | 'sick'
  notes?: string
  created_at: string
  updated_at: string
}

export interface AttendanceCreate {
  employee_id: number
  date: string  // YYYY-MM-DD
  check_in_time?: string  // HH:MM:SS
  check_out_time?: string  // HH:MM:SS
  status: 'present' | 'late' | 'absent' | 'sick'
  notes?: string
}

export const attendanceApi = {
  getAll: async (params?: {
    employee_id?: number
    from?: string  // YYYY-MM-DD
    to?: string    // YYYY-MM-DD
    status?: string
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.employee_id) queryParams.append('employee_id', params.employee_id.toString())
    if (params?.from) queryParams.append('from', params.from)
    if (params?.to) queryParams.append('to', params.to)
    if (params?.status) queryParams.append('status', params.status)

    const response = await api.get(`/attendances?${queryParams.toString()}`)
    return response.data as Attendance[]
  },

  getById: async (id: number) => {
    const response = await api.get(`/attendances/${id}`)
    return response.data as Attendance
  },

  create: async (data: AttendanceCreate) => {
    const response = await api.post('/attendances', data)
    return response.data as Attendance
  },

  update: async (id: number, data: Partial<AttendanceCreate>) => {
    const response = await api.put(`/attendances/${id}`, data)
    return response.data as Attendance
  },

  delete: async (id: number) => {
    await api.delete(`/attendances/${id}`)
  },
}
