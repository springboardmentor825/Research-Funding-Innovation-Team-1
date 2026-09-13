import api from './api'

const authService = {
  login: async (email, password, selectedRole) => {
    const response = await api.post('/auth/login', {
      email,
      password,
      selected_role: selectedRole
    })
    return response.data
  },

  register: async (email, password, fullName, role) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
      role
    })
    return response.data
  },

  googleAuth: async (email, fullName, credential = null) => {
    const response = await api.post('/auth/google', {
      email,
      full_name: fullName,
      credential
    })
    return response.data
  },

  completeGoogleRegistration: async (pendingToken, selectedRole) => {
    const response = await api.post('/auth/google/complete-registration', {
      pending_token: pendingToken,
      selected_role: selectedRole
    })
    return response.data
  },

  getProfile: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: async () => {
    const response = await api.post('/auth/logout')
    return response.data
  }
}

export default authService
