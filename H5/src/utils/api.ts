import axios from 'axios'
import type { ApiResponse } from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response): ApiResponse => {
    return response.data as ApiResponse
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message
    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data
    })
  }
)

export default api
