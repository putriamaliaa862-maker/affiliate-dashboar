import api from './client'

// Types
export interface BonusRateRule {
    id: number
    shop_id: number | null
    shop_name: string
    day_type: string
    shift_id: number
    shift_name: string
    bonus_per_order: number
    is_active: boolean
}

export interface BonusRateUpsert {
    shop_id?: number | null
    day_type: string
    shift_id: number
    bonus_per_order: number
    is_active?: boolean
}

export interface BonusRateUpdate {
    is_active: boolean
}

// Bonus API
export const bonusApi = {
    // Get all bonus rates
    getRates: async (): Promise<BonusRateRule[]> => {
        const response = await api.get('/bonus/rates')
        return response.data
    },

    // Upsert bonus rate
    upsertRate: async (data: BonusRateUpsert): Promise<any> => {
        const response = await api.post('/bonus/rates/upsert', data)
        return response.data
    },

    // Update rate status (enable/disable)
    updateRateStatus: async (ruleId: number, data: BonusRateUpdate): Promise<any> => {
        const response = await api.patch(`/bonus/rates/${ruleId}`, data)
        return response.data
    }
}
