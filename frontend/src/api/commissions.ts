import api from './client'

// Types
export interface PayoutSummary {
    total_commission: number
    paid: number
    pending: number
    validating: number
}

export interface PayoutRow {
    order_id: string
    account_id: number
    account_name: string
    commission_amount: number
    payout_status: 'paid' | 'pending' | 'validating'
    payment_method: string | null
    validated_at: string | null
    completed_at: string | null
    paid_at: string | null
    date: string
}

export interface PayoutHistoryResponse {
    summary: PayoutSummary
    rows: PayoutRow[]
}

export interface PayoutParams {
    from: string
    to: string
    status?: string
    search?: string
    account_id?: number
}

// Commissions API
export const commissionsApi = {
    // Get payout history
    getPayoutHistory: async (params: PayoutParams): Promise<PayoutHistoryResponse> => {
        const response = await api.get('/commissions/payout-history', { params })
        return response.data
    },

    // Export CSV
    exportCsv: async (params: PayoutParams) => {
        const response = await api.get('/commissions/export-csv', {
            params,
            responseType: 'blob'
        })

        // Trigger download
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `payouts_${params.from}_${params.to}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
    },

    // Mark paid (bulk)
    markPaid: async (orderIds: string[]) => {
        const response = await api.post('/commissions/mark-paid', { order_ids: orderIds })
        return response.data
    }
}
