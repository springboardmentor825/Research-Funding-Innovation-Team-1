// frontend/src/services/researchIntelligence.js

import api from './api'

/**
 * Part 7: Fetch Research Collaboration Recommendations for a researcher.
 */
export const getCollaboratorRecommendations = async (userId, limit = 10, domain = '') => {
  const params = { limit }
  if (domain) params.domain = domain
  const response = await api.get(`/researchers/${userId}/collaborators`, { params })
  return response.data
}

/**
 * Part 8: Fetch Patent & Innovation Intelligence summary.
 */
export const getPatentIntelligence = async () => {
  const response = await api.get('/patents/intelligence')
  return response.data
}

/**
 * Part 8: Fetch Patent trends & emerging technology indicators.
 */
export const getPatentTrends = async () => {
  const response = await api.get('/patents/trends')
  return response.data
}

/**
 * Part 8: Fetch Patent detail intelligence by ID.
 */
export const getPatentDetailIntelligence = async (patentId) => {
  const response = await api.get(`/patents/${patentId}/intelligence`)
  return response.data
}

/**
 * Part 9: Fetch 360° Researcher Profile Intelligence.
 */
export const getResearcherIntelligence = async (userId) => {
  const response = await api.get(`/researchers/${userId}/intelligence`)
  return response.data
}

/**
 * Part 9: Compare two researchers side-by-side.
 */
export const compareResearchers = async (userId1, userId2) => {
  const response = await api.get('/researchers/compare', {
    params: { user1: userId1, user2: userId2 }
  })
  return response.data
}

/**
 * Part 12: Fetch Integrated Research Intelligence Dashboard aggregation.
 */
export const getIntegratedDashboard = async (userId) => {
  const response = await api.get(`/research-intelligence/dashboard/${userId}`)
  return response.data
}

/**
 * Part 12: Fetch user alerts.
 */
export const getUserAlerts = async (userId, unreadOnly = false, priority = null) => {
  const params = {}
  if (unreadOnly) params.unread_only = true
  if (priority) params.priority = priority
  const response = await api.get(`/research-intelligence/alerts/${userId}`, { params })
  return response.data
}

/**
 * Part 12: Mark alert as read.
 */
export const markAlertRead = async (alertId, userId) => {
  const response = await api.patch(`/research-intelligence/alerts/${alertId}/read`, null, {
    params: { user_id: userId }
  })
  return response.data
}

/**
 * Part 12: Dismiss alert.
 */
export const dismissAlert = async (alertId, userId) => {
  const response = await api.patch(`/research-intelligence/alerts/${alertId}/dismiss`, null, {
    params: { user_id: userId }
  })
  return response.data
}

/**
 * Part 12: Trigger alert generation evaluation.
 */
export const triggerAlertGeneration = async (userId) => {
  const response = await api.post(`/research-intelligence/alerts/generate/${userId}`)
  return response.data
}
