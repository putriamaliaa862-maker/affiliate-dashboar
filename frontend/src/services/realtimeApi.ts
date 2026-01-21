/**
 * Realtime API service for frontend
 */
import api from './client';

export interface RealtimeSnapshot {
    id: number;
    shopee_account_id: string;
    shop_name: string | null;
    snapshot_type: string;
    data: Record<string, unknown>;
    scraped_at: string;
    created_at: string;
}

export interface CreatorLiveOverview {
    total_accounts: number;
    total_orders_ready: number;
    total_pending: number;
    last_updated: string | null;
    accounts: Array<{
        shopee_account_id: string;
        shop_name: string | null;
        orders_ready_to_ship: number;
        pending_orders: number;
        scraped_at: string | null;
    }>;
}

export interface AdsOverview {
    total_accounts: number;
    total_spend_today: number;
    total_budget_available: number;
    total_coins: number;
    last_updated: string | null;
    accounts: Array<{
        shopee_account_id: string;
        shop_name: string | null;
        spend_today: number;
        budget_available: number;
        coins: number;
        scraped_at: string | null;
    }>;
}

export interface BotStatus {
    success: boolean;
    is_active: boolean;
    status: string;
    recent_snapshots_count: number;
    last_snapshot_at: string | null;
    message: string;
}

// Get bot status
export async function getBotStatus(): Promise<BotStatus> {
    const response = await api.get('/bot/status');
    return response.data;
}

// Get Creator Live overview
export async function getCreatorLiveOverview(): Promise<CreatorLiveOverview> {
    const response = await api.get('/bot/dashboard/creator-live');
    return response.data;
}

// Get Ads overview
export async function getAdsOverview(): Promise<AdsOverview> {
    const response = await api.get('/bot/dashboard/ads');
    return response.data;
}

// Get latest snapshots
export async function getLatestSnapshots(type?: string): Promise<{ snapshots: RealtimeSnapshot[] }> {
    const params = type ? { snapshot_type: type } : {};
    const response = await api.get('/bot/realtime-snapshots/latest', { params });
    return response.data;
}

// Get all snapshots with pagination
export async function getSnapshots(params?: {
    snapshot_type?: string;
    account_id?: string;
    limit?: number;
    offset?: number;
}): Promise<{ total: number; snapshots: RealtimeSnapshot[] }> {
    const response = await api.get('/bot/realtime-snapshots', { params });
    return response.data;
}
