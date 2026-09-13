import React, { createContext, useContext, useState, useEffect } from 'react'
import authService from '../services/auth'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [pendingToken, setPendingToken] = useState(null)

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          const profile = await authService.getProfile()
          setUser(profile)
        } catch (err) {
          localStorage.removeItem('token')
        }
      }
      setLoading(false)
    }
    initAuth()
  }, [])

  const login = async (email, password, selectedRole) => {
    const data = await authService.login(email, password, selectedRole)
    if (data.access_token) {
      localStorage.setItem('token', data.access_token)
      const profile = await authService.getProfile()
      setUser(profile)
      return { status: 'success', user: profile }
    }
    return data
  }

  const googleAuth = async (email, fullName, credential = null) => {
    const data = await authService.googleAuth(email, fullName, credential)
    if (data.status === 'pending_role_selection') {
      setPendingToken(data.pending_token)
      return { status: 'pending_role_selection', pendingToken: data.pending_token, email: data.email }
    }
    if (data.access_token) {
      localStorage.setItem('token', data.access_token)
      const profile = await authService.getProfile()
      setUser(profile)
      return { status: 'success', user: profile }
    }
    return data
  }

  const completeGoogleRegistration = async (pToken, selectedRole) => {
    const tokenToUse = pToken || pendingToken
    const data = await authService.completeGoogleRegistration(tokenToUse, selectedRole)
    if (data.access_token) {
      localStorage.setItem('token', data.access_token)
      setPendingToken(null)
      const profile = await authService.getProfile()
      setUser(profile)
      return { status: 'success', user: profile }
    }
    return data
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (err) {
      console.warn('Backend token invalidation failed or expired:', err)
    } finally {
      localStorage.removeItem('token')
      setUser(null)
      setPendingToken(null)
    }
  }

  const value = {
    user,
    loading,
    pendingToken,
    login,
    googleAuth,
    completeGoogleRegistration,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
