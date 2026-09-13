import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Login from '../pages/Login'
import Register from '../pages/Register'
import GoogleRoleSelection from '../pages/GoogleRoleSelection'
import Dashboard from '../pages/Dashboard'
import StartupDashboard from '../pages/StartupDashboard'
import Recommendations from '../pages/Recommendations'
import Funding from '../pages/Funding'
import Innovation from '../pages/Innovation'
import Profile from '../pages/Profile'
import Publications from '../pages/Publications'
import Patents from '../pages/Patents'
import PatentIntelligence from '../pages/PatentIntelligence'
import ResearcherProfile from '../pages/ResearcherProfile'

import AdminDashboard from '../pages/admin/AdminDashboard'
import UserManagement from '../pages/admin/UserManagement'
import PlatformAnalytics from '../pages/admin/PlatformAnalytics'
import RecommendationMonitoring from '../pages/admin/RecommendationMonitoring'
import SystemReports from '../pages/admin/SystemReports'

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: 'var(--bg-dark)', color: 'var(--accent-cyan-light)', fontWeight: 600 }}>
        Authenticating AI Session...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const userRole = user.role || 'researcher'
    if (!allowedRoles.includes(userRole) && userRole !== 'administrator') {
      if (userRole === 'startup_founder') {
        return <Navigate to="/startup/dashboard" replace />
      } else {
        return <Navigate to="/dashboard" replace />
      }
    }
  }

  return children
}

const DefaultDashboardRedirect = () => {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  const role = user.role || 'researcher'
  if (role === 'administrator') return <Navigate to="/admin/dashboard" replace />
  if (role === 'startup_founder') return <Navigate to="/startup/dashboard" replace />
  return <Navigate to="/dashboard" replace />
}

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/select-role" element={<GoogleRoleSelection />} />

      {/* Admin Module Routes */}
      <Route path="/admin/dashboard" element={
        <ProtectedRoute allowedRoles={['administrator']}>
          <AdminDashboard />
        </ProtectedRoute>
      } />

      <Route path="/admin/users" element={
        <ProtectedRoute allowedRoles={['administrator']}>
          <UserManagement />
        </ProtectedRoute>
      } />

      <Route path="/admin/analytics" element={
        <ProtectedRoute allowedRoles={['administrator']}>
          <PlatformAnalytics />
        </ProtectedRoute>
      } />

      <Route path="/admin/recommendations" element={
        <ProtectedRoute allowedRoles={['administrator']}>
          <RecommendationMonitoring />
        </ProtectedRoute>
      } />

      <Route path="/admin/reports" element={
        <ProtectedRoute allowedRoles={['administrator']}>
          <SystemReports />
        </ProtectedRoute>
      } />

      {/* Researcher & General Dashboard */}
      <Route path="/dashboard" element={
        <ProtectedRoute allowedRoles={['researcher', 'administrator']}>
          <Dashboard />
        </ProtectedRoute>
      } />

      {/* Startup Founder Dashboard */}
      <Route path="/startup/dashboard" element={
        <ProtectedRoute allowedRoles={['startup_founder', 'administrator']}>
          <StartupDashboard />
        </ProtectedRoute>
      } />

      <Route path="/recommendations" element={
        <ProtectedRoute>
          <Recommendations />
        </ProtectedRoute>
      } />
      
      <Route path="/profile" element={
        <ProtectedRoute>
          <Profile />
        </ProtectedRoute>
      } />

      <Route path="/researcher-intelligence" element={
        <ProtectedRoute>
          <ResearcherProfile />
        </ProtectedRoute>
      } />
      
      <Route path="/publications" element={
        <ProtectedRoute>
          <Publications />
        </ProtectedRoute>
      } />
      
      <Route path="/patents" element={
        <ProtectedRoute>
          <Patents />
        </ProtectedRoute>
      } />

      <Route path="/patent-intelligence" element={
        <ProtectedRoute>
          <PatentIntelligence />
        </ProtectedRoute>
      } />
      
      <Route path="/funding" element={
        <ProtectedRoute>
          <Funding />
        </ProtectedRoute>
      } />
      
      <Route path="/innovation" element={
        <ProtectedRoute>
          <Innovation />
        </ProtectedRoute>
      } />

      <Route path="/technology" element={
        <ProtectedRoute>
          <Innovation />
        </ProtectedRoute>
      } />

      <Route path="/commercialization" element={
        <ProtectedRoute>
          <Innovation />
        </ProtectedRoute>
      } />

      <Route path="*" element={<DefaultDashboardRedirect />} />
    </Routes>
  )
}

export default AppRoutes
