/**
 * Permission Utilities
 * Helper functions for role-based access control
 */

export type UserRole = 'super_admin' | 'admin' | 'leader' | 'affiliate'

// Role hierarchy (higher number = more permissions)
export const ROLE_HIERARCHY: Record<UserRole, number> = {
    super_admin: 4,
    admin: 3,
    leader: 2,
    affiliate: 1
}

/**
 * Check if user has permission based on role hierarchy
 * @param userRole - Current user's role
 * @param requiredRole - Minimum required role
 * @returns true if user has sufficient permissions
 */
export const hasPermission = (userRole: UserRole, requiredRole: UserRole): boolean => {
    const userLevel = ROLE_HIERARCHY[userRole] || 0
    const requiredLevel = ROLE_HIERARCHY[requiredRole] || 0
    return userLevel >= requiredLevel
}

/**
 * Check if user can manage other users
 * @param role - User's role
 * @returns true if user can create/edit users
 */
export const canManageUsers = (role: UserRole): boolean => {
    return ['admin', 'super_admin'].includes(role)
}

/**
 * Check if user can delete users
 * @param role - User's role
 * @returns true if user can delete users
 */
export const canDeleteUsers = (role: UserRole): boolean => {
    return role === 'super_admin'
}

/**
 * Check if user can view activity logs
 * @param role - User's role
 * @returns true if user can view logs
 */
export const canViewActivityLogs = (role: UserRole): boolean => {
    return ['admin', 'super_admin'].includes(role)
}

/**
 * Check if user can manage their team
 * @param role - User's role
 * @returns true if user is a leader or higher
 */
export const canManageTeam = (role: UserRole): boolean => {
    return hasPermission(role, 'leader')
}

/**
 * Get role display name
 * @param role - User's role
 * @returns Formatted role name
 */
export const getRoleDisplay = (role: UserRole): string => {
    const roleNames: Record<UserRole, string> = {
        super_admin: 'Super Admin',
        admin: 'Admin',
        leader: 'Leader',
        affiliate: 'Affiliate'
    }
    return roleNames[role] || role
}

/**
 * Get role badge color
 * @param role - User's role
 * @returns Tailwind CSS classes for role badge
 */
export const getRoleBadgeColor = (role: UserRole): string => {
    const colors: Record<UserRole, string> = {
        super_admin: 'bg-purple-100 text-purple-800',
        admin: 'bg-red-100 text-red-800',
        leader: 'bg-blue-100 text-blue-800',
        affiliate: 'bg-green-100 text-green-800'
    }
    return colors[role] || 'bg-gray-100 text-gray-800'
}
