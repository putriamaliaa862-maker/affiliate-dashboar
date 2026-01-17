import api from '@/api/client'

export interface ReportFilters {
    from_date: string  // YYYY-MM-DD
    to_date: string    // YYYY-MM-DD
    account_id?: number
    employee_id?: number
}

export interface ReportRow {
    date: string
    shopee_account: string
    affiliate_name: string
    total_orders: number
    total_gmv: number
    total_commission: number
    conversion_rate?: number
}

export interface ReportResponse {
    data: ReportRow[]
    summary: {
        total_orders: number
        total_gmv: number
        total_commission: number
        avg_order_value: number
    }
}

export const reportsApi = {
    generate: async (filters: ReportFilters): Promise<ReportResponse> => {
        const response = await api.post('/reports/generate', filters)
        return response.data
    },

    exportCsv: async (filters: ReportFilters): Promise<void> => {
        const queryParams = new URLSearchParams()
        queryParams.append('from', filters.from_date)
        queryParams.append('to', filters.to_date)
        if (filters.account_id) queryParams.append('account_id', filters.account_id.toString())
        if (filters.employee_id) queryParams.append('employee_id', filters.employee_id.toString())

        const response = await api.get(`/reports/export-csv?${queryParams.toString()}`, {
            responseType: 'blob',
        })

        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url

        // Extract filename from Content-Disposition header or use default
        const contentDisposition = response.headers['content-disposition']
        let filename = 'report.csv'
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+)"?/)
            if (match) filename = match[1]
        }

        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
    },
}
