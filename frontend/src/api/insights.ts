import api from './client'

export interface Dictionary<T> {
    [key: string]: T
}

export interface KPISummary {
    total_orders: number
    total_gmv: number
    total_commission: number
    total_bonus: number
}

export interface TopEntity {
    id?: any
    name: string
    orders: number
    gmv: number
    commission?: number
    bonus?: number
}

export interface DailySummaryResponse {
    date: string
    scope: string
    kpi: KPISummary
    best_account_today: TopEntity
    best_host_today: TopEntity | null
    best_shift_today: TopEntity
    weak_shift_today: TopEntity
    notes: string[]
}

export interface ProductWarning {
    product_id: string
    product_name: string
    orders_today: number
    orders_yesterday: number
    drop_percent: number
    account_name: string
}

export interface ProductProfit {
    product_id: string
    product_name: string
    total_commission: number
    total_orders: number
    commission_per_order: number
    account_name: string
}

export interface ShiftSummary {
    shift_name: string
    orders: number
    gmv: number
    commission: number
}

export interface HostRankingResponse {
    top: TopEntity[]
    needs_attention: TopEntity[]
}

export interface DailyInsightsResponse {
    date: string
    warnings: Dictionary<ProductWarning[]>
    top_profit_products: ProductProfit[]
    strongest_accounts: TopEntity[]
    host_ranking: HostRankingResponse
    shift_summary: ShiftSummary[]
    dependency_risk: Array<{ type: string, message: string }>
    action_items: string[]
}

export const insightsApi = {
    getDailySummary: async (date: string, shop_id?: number): Promise<DailySummaryResponse> => {
        const params: any = { date }
        if (shop_id) params.shop_id = shop_id

        const response = await api.get('/insights/daily-summary', { params })
        return response.data
    },

    getDailyInsights: async (date: string, shop_id?: number): Promise<DailyInsightsResponse> => {
        const params: any = { date }
        if (shop_id) params.shop_id = shop_id

        const response = await api.get('/insights/daily', { params })
        return response.data
    }
}
