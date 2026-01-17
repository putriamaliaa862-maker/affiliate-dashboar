/**
 * Public Route Component
 * Redirects to dashboard if user is already authenticated
 * Used for login page and other auth pages
 */
import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

interface PublicRouteProps {
    children: React.ReactNode
}

/**
 * PublicRoute component
 * Wraps routes that should only be accessible when NOT authenticated
 * (e.g., login page)
 * 
 * @example
 * <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
 */
export const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
    const { isAuthenticated, loading } = useAuth()

    // Show loading while checking auth status
    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    // Redirect to dashboard if already authenticated
    if (isAuthenticated) {
        return <Navigate to="/" replace />
    }

    // User is not authenticated, show the public route
    return <>{children}</>
}

export default PublicRoute
