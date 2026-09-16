import api from './api'

const ragService = {
  chat: async (queryText) => {
    try {
      const response = await api.post('/rag/chat', { query: queryText })
      return response.data
    } catch (err) {
      const response = await api.post('/v1/rag/chat', { query: queryText })
      return response.data
    }
  },

  search: async (queryText, topK = 5) => {
    try {
      const response = await api.post('/rag/search', { query: queryText, top_k: topK })
      return response.data
    } catch (err) {
      const response = await api.post('/v1/rag/search', { query: queryText, top_k: topK })
      return response.data
    }
  }
}

export default ragService
