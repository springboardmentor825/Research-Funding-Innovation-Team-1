import api from './api'

const fundingService = {
  // Get personalized recommendations for a user
  getRecommendations: async (userId, topK = 10) => {
    try {
      const response = await api.get(`/funding/recommendations/${userId}?top_k=${topK}`)
      const data = response.data
      if (Array.isArray(data)) return data
      if (data && Array.isArray(data.recommendations)) return data.recommendations
      return []
    } catch (err) {
      try {
        const response = await api.get(`/v1/funding/recommendations/${userId}?top_k=${topK}`)
        const data = response.data
        if (Array.isArray(data)) return data
        if (data && Array.isArray(data.recommendations)) return data.recommendations
        return []
      } catch (innerErr) {
        console.error('getRecommendations service error:', innerErr)
        return []
      }
    }
  },

  // Search/Filter funding opportunities
  searchFunding: async (filters = {}) => {
    try {
      const response = await api.get('/funding/search', { params: filters })
      return Array.isArray(response.data) ? response.data : []
    } catch (err) {
      try {
        const response = await api.get('/v1/funding/search', { params: filters })
        return Array.isArray(response.data) ? response.data : []
      } catch (innerErr) {
        console.error('searchFunding service error:', innerErr)
        return []
      }
    }
  },

  // Submit feedback on a recommendation (relevant, not_relevant, saved, applied, dismissed)
  sendFeedback: async (userId, fundingId, feedback) => {
    try {
      const response = await api.post('/funding/recommendations/feedback', {
        user_id: userId,
        funding_id: fundingId,
        feedback: feedback
      })
      return response.data
    } catch (err) {
      const response = await api.post('/v1/funding/recommendations/feedback', {
        user_id: userId,
        funding_id: fundingId,
        feedback: feedback
      })
      return response.data
    }
  },

  // Get saved funding opportunities for a user
  getSavedFunding: async (userId) => {
    try {
      const response = await api.get(`/funding/saved/${userId}`)
      return Array.isArray(response.data) ? response.data : (response.data?.saved || [])
    } catch (err) {
      try {
        const response = await api.get(`/v1/funding/saved/${userId}`)
        return Array.isArray(response.data) ? response.data : (response.data?.saved || [])
      } catch (innerErr) {
        console.error('getSavedFunding service error:', innerErr)
        return []
      }
    }
  },

  // Part 6 Analytics APIs
  getGlobalAnalytics: async () => {
    try {
      const response = await api.get('/funding/analytics')
      return response.data
    } catch (err) {
      console.error('getGlobalAnalytics service error:', err)
      return null
    }
  },

  getResearcherAnalytics: async (userId) => {
    try {
      const response = await api.get(`/funding/analytics/${userId}`)
      return response.data
    } catch (err) {
      console.error('getResearcherAnalytics service error:', err)
      return null
    }
  },

  getPerformanceAnalytics: async (userId) => {
    try {
      const response = await api.get(`/funding/recommendations/performance/${userId}`)
      return response.data
    } catch (err) {
      console.error('getPerformanceAnalytics service error:', err)
      return null
    }
  },

  getDashboardSummary: async (userId) => {
    try {
      const response = await api.get(`/funding/dashboard/${userId}`)
      return response.data
    } catch (err) {
      console.error('getDashboardSummary service error:', err)
      return null
    }
  }
}

export default fundingService
