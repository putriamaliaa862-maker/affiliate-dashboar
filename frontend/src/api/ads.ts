import api from "./client"

// Types
export interface AdsDailySpend {
    id: number
    date: string
    shopee_account_id: number
    spend_amount: number
    spend_type: string
    note?: string
    created_by_user_id?: number
    created_at?: string
}

export interface AdsCenterAccountRow {
    account_id: number
    account_name: string
    spend_today: number
    gmv_today: number
    roas_auto?: number | null
    roas_manual?: number | null
    roas_final?: number | null

    boros_score: number
    boros_status: string // AMAN, WASPADA, BOROS
    boros_reason?: string

    audience_threshold: number
    audience_gap_minutes: number
    audience_status: string // AMAN, HAMPIR_HABIS

    last_add_budget_at?: string
    total_added_budget_today: number
}

// Params
export interface UpsertSpendParams {
    date: string
    account_id: number
    spend_amount: number
    spend_type?: string
    note?: string
}

export interface UpsertMetricsParams {
    date: string
    account_id: number
    roas_manual?: number | null
    revenue_manual?: number | null
    note?: string
}

export interface AddBudgetParams {
    date: string
    account_id: number
    added_amount: number
    remaining_before?: number
}

export interface AudienceSettings {
    shopee_account_id: number
    min_remaining_threshold: number
    min_gap_minutes: number
    active_start_time: string
    active_end_time: string
    max_daily_add_budget?: number | null
    is_enabled: boolean
}

// Logs Interfaces
export interface LogSpend {
    id: number
    date: string
    account_name: string
    spend_amount: number
    spend_type: string
    note?: string
    created_by?: string
    created_at: string
}

export interface LogAudience {
    id: number
    date: string
    time: string
    account_name: string
    remaining_before?: number
    added_amount: number
    remaining_after?: number
    trigger_reason: string
    created_by?: string
    created_at: string
}

export interface LogRoas {
    id: number
    date: string
    account_name: string
    roas_manual: number
    revenue_manual?: number
    note?: string
    created_by?: string
    created_at: string
}


export const adsApi = {
    getAdsCenter: async (date: string, accountId?: number | null) => {
        const params: any = { date }
        if (accountId) params.account_id = accountId
        const response = await api.get<AdsCenterAccountRow[]>('/ads/center', { params })
        return response.data
    },

    upsertSpend: async (data: UpsertSpendParams) => {
        const response = await api.post('/ads/spend/upsert', data)
        return response.data
    },

    upsertMetrics: async (data: UpsertMetricsParams) => {
        const response = await api.post('/ads/metrics/upsert', data)
        return response.data
    },

    getAudienceSettings: async (accountId: number) => {
        const response = await api.get<AudienceSettings>('/ads/audience/settings', {
            params: { account_id: accountId }
        })
        return response.data
    },

    upsertAudienceSettings: async (data: AudienceSettings) => {
        // Backend endpoint expects: account_id in body, mapping front 'shopee_account_id' to 'account_id' if needed?
        // Let's check backend schema: AudienceSettingsUpsertRequest has account_id.
        // So we need to ensure the payload matches.
        const payload = {
            account_id: data.shopee_account_id,
            min_remaining_threshold: data.min_remaining_threshold,
            min_gap_minutes: data.min_gap_minutes,
            active_start_time: data.active_start_time,
            active_end_time: data.active_end_time,
            max_daily_add_budget: data.max_daily_add_budget,
            is_enabled: data.is_enabled
        }
        const response = await api.post('/ads/audience/settings/upsert', payload)
        return response.data
    },

    addAudienceBudget: async (data: AddBudgetParams) => {
        const response = await api.post('/ads/audience/add-budget', data)
        return response.data
    },

    getSpendLogs: async (from: string, to: string, accountId?: number | null) => {
        const params: any = { from_date: from, to_date: to }
        if (accountId) params.account_id = accountId
        const response = await api.get<LogSpend[]>('/ads/logs/spend', { params })
        return response.data
    },

    getAudienceLogs: async (from: string, to: string, accountId?: number | null) => {
        const params: any = { from_date: from, to_date: to }
        if (accountId) params.account_id = accountId
        const response = await api.get<LogAudience[]>('/ads/logs/audience', { params })
        return response.data
    },

    getRoasLogs: async (from: string, to: string, accountId?: number | null) => {
        const params: any = { from_date: from, to_date: to }
        if (accountId) params.account_id = accountId
        const response = await api.get<LogRoas[]>('/ads/logs/roas', { params })
        return response.data
    }
}
