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
  }
}

export default fundingService
