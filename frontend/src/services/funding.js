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
    const params = {
      keyword: filters.query || filters.keyword,
      domain: filters.domain,
      status: filters.status,
      technology_area: filters.technology_area,
      funder: filters.funder,
      minimum_score: filters.minimum_score
    }
    Object.keys(params).forEach(k => params[k] === undefined && delete params[k])
    try {
      const response = await api.get('/funding/search', { params })
      return Array.isArray(response.data) ? response.data : []
    } catch (err) {
      try {
        const response = await api.get('/v1/funding/search', { params })
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

  // Submit a grant application (requires auth token)
  submitApplication: async (fundingId, researchStatement, budgetAsk) => {
    try {
      const response = await api.post('/applications', {
        funding_id: fundingId,
        research_statement: researchStatement,
        budget_ask: budgetAsk || null
      })
      return response.data
    } catch (err) {
      console.error('submitApplication service error:', err)
      throw err
    }
  },

  // List the current user's applications
  getApplications: async () => {
    try {
      const response = await api.get('/applications')
      return Array.isArray(response.data) ? response.data : []
    } catch (err) {
      console.error('getApplications service error:', err)
      return []
    }
  },

  // Withdraw an application
  withdrawApplication: async (applicationId) => {
    try {
      const response = await api.post(`/applications/${applicationId}/withdraw`)
      return response.data
    } catch (err) {
      console.error('withdrawApplication service error:', err)
      throw err
    }
  }
}

export default fundingService
