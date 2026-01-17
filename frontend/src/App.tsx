import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'

// Auth
import { AuthProvider } from '@/contexts/AuthContext'
import ProtectedRoute from '@/components/ProtectedRoute'
import PublicRoute from '@/components/PublicRoute'

// Pages
import Login from '@/pages/Login'
import Dashboard from '@/pages/Dashboard'
import DashboardOwner from '@/pages/DashboardOwner'
import Employees from '@/pages/Employees'
import Attendance from '@/pages/Attendance'
import Accounts from '@/pages/Accounts'
import Reports from '@/pages/Reports'
import Commissions from '@/pages/Commissions'
import Users from '@/pages/Users'
import ActivityLogs from '@/pages/ActivityLogs'
import Profile from '@/pages/Profile'
import Settings from '@/pages/Settings'
import ShiftBonus from '@/pages/ShiftBonus'
import BonusSettings from '@/pages/BonusSettings'
import ImportData from '@/pages/ImportData'
import DailySummary from '@/pages/DailySummary'
import DailyInsights from '@/pages/DailyInsights'
import AdsCenter from '@/pages/AdsCenter'
import LiveProducts from '@/pages/LiveProducts'

// Components
import Sidebar from '@/components/Sidebar'
import Header from '@/components/Header'

// Layout wrapper for authenticated pages
const AuthenticatedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />

          {/* Protected Routes - All require authentication */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Dashboard />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard-owner"
            element={
              <ProtectedRoute requiredRole="owner">
                <AuthenticatedLayout>
                  <DashboardOwner />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/employees"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Employees />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/attendance"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Attendance />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/accounts"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Accounts />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Reports />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/commissions"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Commissions />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/users"
            element={
              <ProtectedRoute requiredRole="admin">
                <AuthenticatedLayout>
                  <Users />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/activity-logs"
            element={
              <ProtectedRoute requiredRole="admin">
                <AuthenticatedLayout>
                  <ActivityLogs />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/daily-summary"
            element={
              <ProtectedRoute requiredRole="owner">
                <AuthenticatedLayout>
                  <DailySummary />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/daily-insights"
            element={
              <ProtectedRoute requiredRole="leader">
                <AuthenticatedLayout>
                  <DailyInsights />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/ads-center"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <AdsCenter />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/live-products"
            element={
              <ProtectedRoute requiredRole="leader">
                <AuthenticatedLayout>
                  <LiveProducts />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Profile />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Settings />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/shift-bonus"
            element={
              <ProtectedRoute requiredRole="leader">
                <AuthenticatedLayout>
                  <ShiftBonus />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/bonus-settings"
            element={
              <ProtectedRoute requiredRole="admin">
                <AuthenticatedLayout>
                  <BonusSettings />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/import-data"
            element={
              <ProtectedRoute requiredRole="admin">
                <AuthenticatedLayout>
                  <ImportData />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* Catch all - redirect to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
