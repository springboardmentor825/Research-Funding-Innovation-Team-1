import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Login from '../pages/Login'
import Register from '../pages/Register'
import Dashboard from '../pages/Dashboard'
import Recommendations from '../pages/Recommendations'
import Funding from '../pages/Funding'
import Innovation from '../pages/Innovation'
import Profile from '../pages/Profile'
import Publications from '../pages/Publications'
import Patents from '../pages/Patents'
import InnovationScore from '../pages/InnovationScore'
import Reports from '../pages/Reports'
import Collaborations from '../pages/Collaborations'
import LabResources from '../pages/LabResources'
import Alerts from '../pages/Alerts'
import Settings from '../pages/Settings'

const ProtectedRoute = ({ children }) => {
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
  return children
}

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
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

      <Route path="/innovation-score" element={
        <ProtectedRoute>
          <InnovationScore />
        </ProtectedRoute>
      } />

      <Route path="/reports" element={
        <ProtectedRoute>
          <Reports />
        </ProtectedRoute>
      } />

      <Route path="/collaborations" element={
        <ProtectedRoute>
          <Collaborations />
        </ProtectedRoute>
      } />

      <Route path="/lab-resources" element={
        <ProtectedRoute>
          <LabResources />
        </ProtectedRoute>
      } />

      <Route path="/alerts" element={
        <ProtectedRoute>
          <Alerts />
        </ProtectedRoute>
      } />

      <Route path="/settings" element={
        <ProtectedRoute>
          <Settings />
        </ProtectedRoute>
      } />

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default AppRoutes
