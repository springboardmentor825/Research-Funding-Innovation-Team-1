import api from './api'

const analyticsService = {
  overview: async () => {
    const response = await api.get('/analytics/overview')
    return response.data
  },
  publicationTrends: async (params = {}) => {
    const response = await api.get('/analytics/publication-trends', { params })
    return response.data
  },
  publicationTypes: async () => {
    const response = await api.get('/analytics/publication-types')
    return response.data
  },
  topics: async (limit = 10) => {
    const response = await api.get('/analytics/topics', { params: { limit } })
    return response.data
  },
  institutions: async (limit = 10) => {
    const response = await api.get('/analytics/institutions', { params: { limit } })
    return response.data
  },
  authors: async (limit = 10) => {
    const response = await api.get('/analytics/authors', { params: { limit } })
    return response.data
  },
  primaryTopics: async (limit = 10) => {
    const response = await api.get('/analytics/primary-topics', { params: { limit } })
    return response.data
  },
  concepts: async (limit = 10) => {
    const response = await api.get('/analytics/concepts', { params: { limit } })
    return response.data
  },
  topCited: async (limit = 10) => {
    const response = await api.get('/analytics/top-cited', { params: { limit } })
    return response.data
  },
  openAccessStatus: async () => {
    const response = await api.get('/analytics/open-access-status')
    return response.data
  },
  retractionStatus: async () => {
    const response = await api.get('/analytics/retraction-status')
    return response.data
  },
  sources: async (limit = 10) => {
    const response = await api.get('/analytics/sources', { params: { limit } })
    return response.data
  }
}

export default analyticsService