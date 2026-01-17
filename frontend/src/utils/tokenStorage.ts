/**
 * Token Storage Utility
 * Handles storing and retrieving JWT tokens from localStorage
 */

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user'

export const tokenStorage = {
    /**
     * Get access token from localStorage
     */
    getAccessToken: (): string | null => {
        return localStorage.getItem(ACCESS_TOKEN_KEY)
    },

    /**
     * Set access token in localStorage
     */
    setAccessToken: (token: string): void => {
        localStorage.setItem(ACCESS_TOKEN_KEY, token)
    },

    /**
     * Get refresh token from localStorage
     */
    getRefreshToken: (): string | null => {
        return localStorage.getItem(REFRESH_TOKEN_KEY)
    },

    /**
     * Set refresh token in localStorage
     */
    setRefreshToken: (token: string): void => {
        localStorage.setItem(REFRESH_TOKEN_KEY, token)
    },

    /**
     * Get stored user data
     */
    getUser: (): any | null => {
        const userStr = localStorage.getItem(USER_KEY)
        if (!userStr) return null
        try {
            return JSON.parse(userStr)
        } catch {
            return null
        }
    },

    /**
     * Set user data in localStorage
     */
    setUser: (user: any): void => {
        localStorage.setItem(USER_KEY, JSON.stringify(user))
    },

    /**
     * Clear all tokens and user data from localStorage
     */
    clearAll: (): void => {
        localStorage.removeItem(ACCESS_TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
    },

    /**
     * Check if user is authenticated (has access token)
     */
    isAuthenticated: (): boolean => {
        return !!localStorage.getItem(ACCESS_TOKEN_KEY)
    }
}

export default tokenStorage
