import api from '@/api/client'
import { ShopeeAccount } from '@/types'

export const accountApi = {
    getAll: async (studioId?: number) => {
        const params = studioId ? `?studio_id=${studioId}` : ''
        const response = await api.get(`/shopee-accounts${params}`)
        return response.data
    },

    getById: async (id: number) => {
        const response = await api.get(`/shopee-accounts/${id}`)
        return response.data
    },

    create: async (data: Omit<ShopeeAccount, 'id' | 'created_at'>) => {
        const response = await api.post('/shopee-accounts', data)
        return response.data
    },

    update: async (id: number, data: Partial<ShopeeAccount>) => {
        const response = await api.put(`/shopee-accounts/${id}`, data)
        return response.data
    },

    delete: async (id: number) => {
        await api.delete(`/shopee-accounts/${id}`)
    },
}
