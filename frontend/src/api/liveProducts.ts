/**
 * Live Products API Client
 * STRICT: Uses api from './client' (no direct axios)
 */
import api from './client'

// ==================== Types ====================

export interface ProductSyncItem {
    product_id: string
    product_name: string
    sold_qty: number
    gmv: number
    clicks?: number
}

export interface LiveProductSyncRequest {
    account_id: number
    snapshot_date: string
    source: string
    products: ProductSyncItem[]
    raw_data?: any
}

export interface LiveProductSnapshot {
    id: number
    snapshot_date: string
    account_id: number
    studio_id: number | null
    leader_id: number | null
    host_id: number | null
    product_id: string
    product_name: string
    sold_qty: number
    gmv: number
    clicks: number | null
    source: string
    created_at: string
}

export interface LiveProductRankingItem {
    product_id: string
    product_name: string
    sold_qty: number
    gmv: number
    rank: number
}

export interface LiveSyncLog {
    id: number
    account_id: number
    snapshot_date: string
    synced_at: string
    status: string
    total_rows: number
    message: string | null
}

// ==================== API Functions ====================

/**
 * Sync live products (manual)
 */
export const syncLiveProducts = async (data: LiveProductSyncRequest) => {
    const response = await api.post('/live-products/sync', data)
    return response.data
}

/**
 * Get daily snapshots
 */
export const getDailySnapshots = async (date?: string, accountId?: number): Promise<LiveProductSnapshot[]> => {
    const params: any = {}
    if (date) params.date = date
    if (accountId) params.account_id = accountId

    const response = await api.get<LiveProductSnapshot[]>('/live-products/daily', { params })
    return response.data
}

/**
 * Get product rankings (top by GMV and sold)
 */
export const getRanking = async (date?: string, accountId?: number) => {
    const params: any = {}
    if (date) params.date = date
    if (accountId) params.account_id = accountId

    const response = await api.get('/live-products/ranking', { params })
    return response.data
}

/**
 * Get sync logs
 */
export const getSyncLogs = async (accountId?: number): Promise<LiveSyncLog[]> => {
    const params: any = {}
    if (accountId) params.account_id = accountId

    const response = await api.get<LiveSyncLog[]>('/live-products/sync-logs', { params })
    return response.data
}

const liveProductsApi = {
    syncLiveProducts,
    getDailySnapshots,
    getRanking,
    getSyncLogs
}

export default liveProductsApi
