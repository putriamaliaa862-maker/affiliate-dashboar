/**
 * Authentication API Client
 * Handles all authentication-related API calls
 */
import client from './client'

// ==================== Types ====================

export interface LoginRequest {
    username: string
    password: string
}

export interface TokenResponse {
    access_token: string
    refresh_token: string
    token_type: string
    user: User
}

export interface User {
    id: number
    username: string
    email: string
    full_name: string | null
    phone: string | null
    role: 'super_admin' | 'admin' | 'leader' | 'affiliate' | 'owner'
    leader_id: number | null
    is_active: boolean
    last_login: string | null
    created_at: string
    updated_at: string
}

export interface RefreshTokenRequest {
    refresh_token: string
}

// ==================== API Functions ====================

/**
 * Login with username/email and password
 */
export const login = async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await client.post<TokenResponse>('/auth/login', credentials)
    return response.data
}

/**
 * Logout (logs activity on backend)
 */
export const logout = async (): Promise<void> => {
    await client.post('/auth/logout')
}

/**
 * Refresh access token using refresh token
 */
export const refreshToken = async (refreshToken: string): Promise<TokenResponse> => {
    const response = await client.post<TokenResponse>('/auth/refresh', {
        refresh_token: refreshToken
    })
    return response.data
}

/**
 * Get current authenticated user information
 */
export const getCurrentUser = async (): Promise<User> => {
    const response = await client.get<User>('/auth/me')
    return response.data
}

// ==================== ACCESS CODE MANAGEMENT ====================

export interface AccessCodeResponse {
    access_code: string | null
    has_code: boolean
}

export interface RegenerateAccessCodeResponse {
    access_code: string
    message: string
}

/**
 * Get current user's access code
 */
export const getMyAccessCode = async (): Promise<AccessCodeResponse> => {
    const response = await client.get<AccessCodeResponse>('/auth/access-code/me')
    return response.data
}

/**
 * Generate or regenerate access code for current user
 */
export const regenerateAccessCode = async (): Promise<RegenerateAccessCodeResponse> => {
    const response = await client.post<RegenerateAccessCodeResponse>('/auth/access-code/regenerate')
    return response.data
}

// ==================== Export ====================

const authApi = {
    login,
    logout,
    refreshToken,
    getCurrentUser,
    getMyAccessCode,
    regenerateAccessCode
}

export default authApi
