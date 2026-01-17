/**
 * useAuth Hook
 * Custom hook to access authentication context
 */
import { useContext } from 'react'
import { AuthContext } from '@/contexts/AuthContext'

/**
 * Hook to access authentication state and methods
 * Must be used within AuthProvider
 * 
 * @example
 * const { user, login, logout, isAuthenticated } = useAuth()
 */
export const useAuth = () => {
    const context = useContext(AuthContext)

    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }

    return context
}

export default useAuth
