import api from './client'

// ==================== Premium Dashboard Types ====================

export interface HourlyDataPoint {
    hour: string
    gmv: number
    orders: number
    gmv_yesterday?: number
}

export interface TopPerformer {
    name: string
    value: number
    subtitle?: string
    rank: number
}

export interface AlertItem {
    type: 'boros' | 'budget' | 'drop' | 'risk'
    title: string
    description: string
    severity: 'critical' | 'warning' | 'info'
    actionLabel: string
    actionPath: string
}

export interface FinancialData {
    revenue_today: number
    revenue_yesterday: number
    commission_pending: number
    commission_paid: number
    budget_used: number
    budget_total: number
    accounts_roas: { account_name: string, roas: number }[]
}

export interface PremiumDashboardData {
    hourly_performance: HourlyDataPoint[]
    top_performers: {
        accounts: TopPerformer[]
        hosts: TopPerformer[]
        products: TopPerformer[]
    }
    alerts: AlertItem[]
    financial_summary: FinancialData
}

// ==================== API Functions ====================

/**
 * Get premium dashboard data (hourly, top performers, alerts, financial)
 */
export const getPremiumDashboard = async (date: string, accountId?: number): Promise<PremiumDashboardData> => {
    const params: any = { date }
    if (accountId) params.account_id = accountId

    const response = await api.get<PremiumDashboardData>('/dashboard/premium', { params })
    return response.data
}

const premiumApi = {
    getPremiumDashboard
}

export default premiumApi
