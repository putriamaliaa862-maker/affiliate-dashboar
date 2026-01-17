import api from '@/api/client'
import { Studio } from '@/types'

export const studioApi = {
    getAll: async () => {
        const response = await api.get('/studios')
        return response.data
    },

    getById: async (id: number) => {
        const response = await api.get(`/studios/${id}`)
        return response.data
    },

    create: async (data: Omit<Studio, 'id' | 'created_at' | 'updated_at'>) => {
        const response = await api.post('/studios', data)
        return response.data
    },

    update: async (id: number, data: Partial<Studio>) => {
        const response = await api.put(`/studios/${id}`, data)
        return response.data
    },

    delete: async (id: number) => {
        await api.delete(`/studios/${id}`)
    },
}
