import api from './api'

const adminService = {
  getOverview: async () => {
    try {
      const response = await api.get('/v1/admin/overview')
      return response.data
    } catch (err) {
      try {
        const response = await api.get('/admin/overview')
        return response.data
      } catch (innerErr) {
        console.error('getOverview service error:', innerErr)
        throw innerErr
      }
    }
  }
}

export default adminService