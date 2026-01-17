import React, { useState, useRef, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { LogOut, Settings, Bell, User, ChevronDown } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { getRoleDisplay, getRoleBadgeColor } from '@/utils/permissions'

const Header: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
      // Navigate to login anyway
      navigate('/login')
    }
  }

  if (!user) {
    return null
  }

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Affiliate Dashboard</h2>
        <p className="text-sm text-gray-500">Welcome back, {user.full_name || user.username}!</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Notifications */}
        <button
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative"
          title="Notifications"
        >
          <Bell size={20} className="text-gray-600" />
        </button>

        {/* Settings Icon in Header */}
        <Link
          to="/settings"
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Settings"
        >
          <Settings size={20} className="text-gray-600" />
        </Link>

        {/* User Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="flex items-center gap-3 px-4 py-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {/* User Avatar */}
            <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <User size={18} className="text-white" />
            </div>

            {/* User Info */}
            <div className="text-left hidden md:block">
              <p className="text-sm font-medium text-gray-700">
                {user.full_name || user.username}
              </p>
              <p className="text-xs text-gray-500">{user.email}</p>
            </div>

            <ChevronDown
              size={16}
              className={`text-gray-500 transition-transform ${showDropdown ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Dropdown Menu */}
          {showDropdown && (
            <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
              {/* User Info Section */}
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="font-medium text-gray-900">{user.full_name || user.username}</p>
                <p className="text-sm text-gray-500 mb-2">{user.email}</p>
                <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                  {getRoleDisplay(user.role)}
                </span>
              </div>

              {/* Menu Items */}
              <div className="py-1">
                <Link
                  to="/profile"
                  onClick={() => setShowDropdown(false)}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2 text-gray-700 transition-colors"
                >
                  <User size={16} />
                  <span className="text-sm">My Profile</span>
                </Link>

                <Link
                  to="/settings"
                  onClick={() => setShowDropdown(false)}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2 text-gray-700 transition-colors"
                >
                  <Settings size={16} />
                  <span className="text-sm">Settings</span>
                </Link>
              </div>

              {/* Logout */}
              <div className="border-t border-gray-100 pt-1">
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 hover:bg-red-50 flex items-center gap-2 text-red-600 transition-colors"
                >
                  <LogOut size={16} />
                  <span className="text-sm font-medium">Logout</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Header
