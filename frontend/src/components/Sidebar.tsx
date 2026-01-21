import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  BarChart3,
  Users,
  Calendar,
  ShoppingCart,
  FileText,
  DollarSign,
  Home,
  UserCog,
  ClipboardList,
  Coins,
  Settings as SettingsIcon,
  Database,
  TrendingUp,
  LineChart,
  Crown,
  Bot
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'




const Sidebar: React.FC = () => {
  const location = useLocation()
  const { user } = useAuth()

  // Define menu sections
  const menuSections = [
    {
      title: '🔥 MONITORING CUAN',
      items: [
        { label: 'Dashboard', icon: Home, path: '/' },
        { label: '👑 Owner Mode', icon: Crown, path: '/dashboard-owner', requiredRoles: ['owner', 'super_admin'] },
        { label: 'Ads Center', icon: BarChart3, path: '/ads-center', requiredRoles: ['super_admin', 'owner', 'supervisor', 'partner', 'leader', 'host'] },
        { label: 'Produk Live', icon: ShoppingCart, path: '/live-products', requiredRoles: ['leader', 'admin', 'super_admin', 'owner'] },
        { label: 'Commissions', icon: DollarSign, path: '/commissions' },
        { label: 'Reports', icon: FileText, path: '/reports' },
        { label: 'Shift Bonus', icon: Coins, path: '/shift-bonus', requiredRoles: ['leader', 'admin', 'super_admin'] },
        { label: 'Daily Insights', icon: TrendingUp, path: '/daily-insights', requiredRoles: ['leader', 'admin', 'super_admin', 'owner'] },
        { label: '🤖 Realtime Monitor', icon: Bot, path: '/realtime', requiredRoles: ['admin', 'super_admin', 'owner'] },
        // Keeping Daily Summary here as it fits the category, though not explicitly in the short list
        { label: 'Ringkasan Harian', icon: LineChart, path: '/daily-summary', requiredRoles: ['owner', 'admin', 'super_admin'] },
      ]
    },
    {
      title: '📥 DATA MASUK',
      items: [
        { label: 'Import Data', icon: Database, path: '/import-data', requiredRoles: ['admin', 'super_admin'] },
      ]
    },
    {
      title: '👥 TIM & OPERASIONAL',
      items: [
        { label: 'Employees', icon: Users, path: '/employees' },
        { label: 'Attendance', icon: Calendar, path: '/attendance' },
        { label: 'Bonus Settings', icon: SettingsIcon, path: '/bonus-settings', requiredRoles: ['admin', 'super_admin'] },
      ]
    },
    {
      title: '⚙️ ADMIN & SISTEM',
      items: [
        { label: 'Users', icon: UserCog, path: '/users', requiredRoles: ['admin', 'super_admin'] },
        { label: 'Accounts', icon: ShoppingCart, path: '/accounts' },
        { label: 'Activity Logs', icon: ClipboardList, path: '/activity-logs', requiredRoles: ['admin', 'super_admin'] },
      ]
    }
  ]

  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-full overflow-y-auto">
      {/* Logo Section */}
      <div className="p-6 border-b border-slate-700 shrink-0">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <BarChart3 size={28} />
          Affiliate Hub
        </h1>
        {user && (
          <p className="text-xs text-slate-400 mt-2">
            Logged in as {user.role.replace('_', ' ')}
          </p>
        )}
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-6">
        {menuSections.map((section, index) => {
          // Filter items within the section
          const visibleItems = section.items.filter(item => {
            if (!item.requiredRoles) return true
            if (!user) return false
            return item.requiredRoles.includes(user.role)
          })

          if (visibleItems.length === 0) return null

          return (
            <div key={index}>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 px-4">
                {section.title}
              </h3>
              <div className="space-y-1">
                {visibleItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors text-sm font-medium ${isActive ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                        }`}
                    >
                      <Icon size={18} />
                      <span>{item.label}</span>
                    </Link>
                  )
                })}
              </div>
            </div>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700">
        <div className="text-sm text-slate-400 space-y-1">
          <p className="font-semibold">v1.0.0</p>
          <p className="text-xs">Affiliate Dashboard</p>
          {user && (
            <p className="text-xs mt-2">
              {menuSections.reduce((acc, section) => acc + section.items.length, 0)} menu items
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Sidebar
