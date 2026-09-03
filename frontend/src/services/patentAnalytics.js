import api from './api'

const patentAnalyticsService = {
  domains: async () => {
    const response = await api.get('/patents/analysis/domains')
    return response.data
  },
  trends: async () => {
    const response = await api.get('/patents/analysis/trends')
    return response.data
  },
  growth: async () => {
    const response = await api.get('/patents/analysis/growth')
    return response.data
  },
  researchOverlap: async () => {
    const response = await api.get('/patents/analysis/research-overlap')
    return response.data
  },
  opportunities: async () => {
    const response = await api.get('/patents/analysis/opportunities')
    return response.data
  }
}

export default patentAnalyticsService
