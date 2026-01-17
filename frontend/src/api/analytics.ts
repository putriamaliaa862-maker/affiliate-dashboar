import api from './client'

// Types
export interface HourlyData {
    hour: string
    total_orders: number
    total_gmv: number
    total_commission: number
}

export interface ShiftData {
    shift_id: number
    shift_name: string
    start_time: string
    end_time: string
    total_orders: number
    total_gmv: number
    total_commission: number
}

export interface ShiftBonus {
    shift_id: number
    shift_name: string
    total_orders: number
    bonus_per_order: number
    bonus_amount: number
}

export interface BonusShiftResponse {
    date: string
    day_type: string
    shop_id: number | null
    host_id: number | null
    shift_results: ShiftBonus[]
    total_bonus: number
}

export interface HostShiftBreakdown {
    shift_name: string
    orders: number
    bonus: number
}

export interface HostLeaderboardItem {
    rank: number
    host_id: number
    host_name: string
    total_orders: number
    total_gmv: number
    total_commission: number
    total_bonus: number
    shift_breakdown: HostShiftBreakdown[]
}

export interface LeaderboardResponse {
    date: string
    shop_id: number | null
    leaderboard: HostLeaderboardItem[]
}

// Analytics API
export const analyticsApi = {
    // Get hourly orders
    getHourlyOrders: async (params: {
        date: string
        shop_id?: number
        host_id?: number
    }): Promise<HourlyData[]> => {
        const response = await api.get('/analytics/orders-hourly', { params })
        return response.data
    },

    // Get shift orders
    getShiftOrders: async (params: {
        date: string
        shop_id?: number
        host_id?: number
    }): Promise<ShiftData[]> => {
        const response = await api.get('/analytics/orders-shift', { params })
        return response.data
    },

    // Get bonus per shift
    getBonusShift: async (params: {
        date: string
        shop_id?: number
        host_id?: number
    }): Promise<BonusShiftResponse> => {
        const response = await api.get('/analytics/bonus-shift', { params })
        return response.data
    },

    // Get host leaderboard
    getHostLeaderboard: async (params: {
        date: string
        shop_id?: number
    }): Promise<LeaderboardResponse> => {
        const response = await api.get('/analytics/bonus-host-leaderboard', { params })
        return response.data
    }
}
