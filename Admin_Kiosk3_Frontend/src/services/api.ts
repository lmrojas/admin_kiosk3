/**
 * @fileoverview Servicios API centralizados para Admin Kiosk 3
 */
import axios, { AxiosInstance } from 'axios'
import { 
  LoginCredentials, 
  AuthResponse,
  Kiosk,
  KioskResponse
} from '../types'

const API_BASE = '/api'

const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para tokens
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// Interceptor para errores
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: async (credentials: LoginCredentials) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, credentials, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
      }
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Error en la autenticación');
      }
      throw error;
    }
  },
  logout: () => 
    api.post('/auth/logout')
}

export const kioskApi = {
  getAll: () => 
    api.get<KioskResponse>('/kiosk/list'),
    
  getById: (id: number) => 
    api.get<KioskResponse>(`/kiosk/${id}`),
    
  create: (data: Partial<Kiosk>) => 
    api.post<KioskResponse>('/kiosk/create', data),
    
  update: (id: number, data: Partial<Kiosk>) => 
    api.put<KioskResponse>(`/kiosk/${id}`, data),
    
  updateStatus: (id: number, status: string) => 
    api.put<KioskResponse>(`/kiosk/${id}/status`, { status }),
    
  delete: (id: number) => 
    api.delete<KioskResponse>(`/kiosk/${id}`),
    
  assign: (id: number, userId: number) => 
    api.post<KioskResponse>(`/kiosk/${id}/assign`, { user_id: userId }),

  list: () => 
    fetch(`${API_BASE}/kiosk`, {
      headers: { 
        'Authorization': `Bearer ${localStorage.getItem('token')}` 
      }
    })
}

// Verificar que las URLs apunten a los puertos correctos
const AUTH_URL = 'http://localhost:5001/api/auth';
const KIOSK_URL = 'http://localhost:5002/api/kiosk'; 