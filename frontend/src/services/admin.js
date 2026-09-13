import api from './api'

const adminService = {
  getDashboard: async () => {
    const response = await api.get('/admin/dashboard')
    return response.data
  },

  getUsers: async (params = {}) => {
    const response = await api.get('/admin/users', { params })
    return response.data
  },

  getUserDetails: async (userId) => {
    const response = await api.get(`/admin/users/${userId}`)
    return response.data
  },

  updateUserRole: async (userId, role) => {
    const response = await api.patch(`/admin/users/${userId}/role`, { role })
    return response.data
  },

  updateUserStatus: async (userId, status) => {
    const response = await api.patch(`/admin/users/${userId}/status`, { status })
    return response.data
  },

  getAnalytics: async () => {
    const response = await api.get('/admin/analytics')
    return response.data
  },

  getRecommendations: async () => {
    const response = await api.get('/admin/recommendations')
    return response.data
  },

  getReports: async () => {
    const response = await api.get('/admin/reports')
    return response.data
  },

  exportReportUrl: (reportType) => {
    const baseURL = api.defaults.baseURL || 'http://localhost:8000/api/v1'
    return `${baseURL}/admin/reports/${reportType}/export`
  }
}

export default adminService
