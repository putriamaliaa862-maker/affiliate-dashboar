import api from './client'

export interface ImportPreviewResponse {
    detected_type: 'commission' | 'sales' | 'unknown'
    headers: string[]
    sample_rows: any[]
    suggested_mapping: Record<string, string>
    total_rows: number
    warnings: string[]
}

export interface ImportResult {
    inserted: number
    updated: number
    skipped: number
    failed: number
    failed_rows: Array<{
        row_index: number
        reason: string
        raw: any
    }>
}

export const importApi = {
    // Preview CSV
    previewCsv: async (file: File): Promise<ImportPreviewResponse> => {
        const formData = new FormData()
        formData.append('file', file)

        // Axios (and browser) will automatically set correct Content-Type with boundary for FormData
        // Token is handled by interceptor in ./client
        const response = await api.post('/import/csv/preview', formData)
        return response.data
    },

    // Execute Import
    executeImport: async (data: {
        shop_id: number
        import_type: string
        mapping: Record<string, string>
        rows: any[] // Passing rows back for now (MVP)
    }): Promise<ImportResult> => {
        const response = await api.post('/import/csv/execute', data)
        return response.data
    }
}
