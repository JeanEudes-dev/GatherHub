import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api/v1/`
  : 'http://localhost:8000/api/v1/'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor to add JWT token to requests
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Interceptor to handle token refresh (simplified version)
// A real implementation would involve checking for token expiry and using the refresh token
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          })
          const { tokens } = response.data
          localStorage.setItem('access', tokens.access)
          if (tokens.refresh) {
            // Some refresh endpoints might not return a new refresh token
            localStorage.setItem('refresh', tokens.refresh)
          }
          apiClient.defaults.headers.common['Authorization'] =
            'Bearer ' + tokens.access
          originalRequest.headers['Authorization'] = 'Bearer ' + tokens.access
          return apiClient(originalRequest)
        } else {
          // No refresh token, redirect to login or handle error
          console.error('No refresh token available.')
          window.location.href = '/login' // Example redirect
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError)
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        window.location.href = '/login' // Example redirect
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export const login = async (credentials: LoginCredentials) => {
  const response = await apiClient.post('auth/login/', credentials)
  console.error('Login response:', response.data)
  const { tokens, user } = response.data
  localStorage.setItem('access', tokens.access)
  localStorage.setItem('refresh', tokens.refresh)
  // You might want to store user data in a global state (e.g., Zustand)
  return user
}

export const register = async (userData: RegisterData) => {
  try {
    const response = await apiClient.post('auth/register/', userData)
    const { tokens, user } = response.data
    localStorage.setItem('access', tokens.access)
    localStorage.setItem('refresh', tokens.refresh)
    return user
  } catch (error) {
    console.error('Register error:', error)
    throw error
  }
}

export const logout = async () => {
  const refreshToken = localStorage.getItem('refresh')
  if (refreshToken) {
    try {
      await apiClient.post('auth/logout/', { refresh: refreshToken })
    } catch (error) {
      console.error('Logout failed on server:', error)
      // Still remove tokens locally even if server call fails
    }
  }
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  // Clear user from global state
}

export const getUserProfile = async () => {
  const response = await apiClient.get('auth/profile/')
  return response.data
}

export const updateUserProfile = async (profileData: UpdateProfileData) => {
  // For file uploads, content-type needs to be multipart/form-data
  // This example assumes profileData is already a FormData object if an avatar is included
  let headers = {}
  if (profileData.avatar && profileData.avatar instanceof File) {
    headers = { 'Content-Type': 'multipart/form-data' }
  }
  const response = await apiClient.put('auth/profile/', profileData, {
    headers,
  })
  return response.data
}

// Define types for credentials and user data based on your backend API
// These should be in a types/index.ts file ideally

interface LoginCredentials {
  username?: string
  email?: string // Backend might support login with email
  password?: string
}

interface RegisterData {
  username?: string
  email?: string
  password?: string
  first_name?: string
  last_name?: string
  password_confirm?: string
}

interface UpdateProfileData {
  first_name?: string
  last_name?: string
  bio?: string
  avatar?: File | null | string // File for new upload, string for existing URL, null to remove
}
