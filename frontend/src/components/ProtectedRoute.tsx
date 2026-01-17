/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 * Optionally checks for required role
 */
import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

// Role hierarchy for permission checking
const ROLE_HIERARCHY = {
    super_admin: 4,
    admin: 3,
    leader: 2,
    affiliate: 1
}

interface ProtectedRouteProps {
    children: React.ReactNode
    requiredRole?: 'super_admin' | 'admin' | 'leader' | 'affiliate'
}

/**
 * ProtectedRoute component
 * Wraps routes that require authentication
 * 
 * @example
 * <Route path="/users" element={<ProtectedRoute requiredRole="admin"><Users /></ProtectedRoute>} />
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    requiredRole
}) => {
    const { isAuthenticated, user, loading } = useAuth()
    const location = useLocation()

    // Show loading while checking auth status
    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated || !user) {
        return <Navigate to="/login" state={{ from: location }} replace />
    }

    // Check role if required
    if (requiredRole) {
        const userLevel = ROLE_HIERARCHY[user.role] || 0
        const requiredLevel = ROLE_HIERARCHY[requiredRole] || 0

        if (userLevel < requiredLevel) {
            // User doesn't have sufficient permissions
            return (
                <div className="flex items-center justify-center h-screen bg-gray-100">
                    <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
                        <div className="text-center">
                            <div className="text-6xl text-red-500 mb-4">🚫</div>
                            <h1 className="text-2xl font-bold text-gray-800 mb-2">
                                Access Denied
                            </h1>
                            <p className="text-gray-600 mb-4">
                                You don't have permission to access this page.
                            </p>
                            <p className="text-sm text-gray-500">
                                Required role: <span className="font-semibold">{requiredRole}</span>
                                <br />
                                Your role: <span className="font-semibold">{user.role}</span>
                            </p>
                            <button
                                onClick={() => window.history.back()}
                                className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                                Go Back
                            </button>
                        </div>
                    </div>
                </div>
            )
        }
    }

    // User is authenticated and has required role
    return <>{children}</>
}

export default ProtectedRoute
