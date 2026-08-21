/**
 * Wealify API Client
 * Provides typed methods for Authentication & Authorization API endpoints
 * with automatic Bearer token management in localStorage.
 */

export interface AuthUser {
  id: number
  email: string
  full_name?: string | null
  phone?: string | null
  role: string
  is_active: boolean
  created_at: string
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export interface RegisterPayload {
  email: string
  password: string
  full_name?: string
  phone?: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface GoogleAuthPayload {
  email: string
  full_name?: string
  google_id?: string
}

export interface MessageResponse {
  message: string
  success: boolean
}

interface ApiErrorResponse {
  detail?: string | Array<{ msg?: string }>
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const TOKEN_KEY = 'wealify_access_token'
const USER_KEY = 'wealify_user_profile'

export const tokenStorage = {
  getToken: (): string | null => {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(TOKEN_KEY)
  },
  setToken: (token: string): void => {
    if (typeof window === 'undefined') return
    localStorage.setItem(TOKEN_KEY, token)
  },
  removeToken: (): void => {
    if (typeof window === 'undefined') return
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
  getUser: (): AuthUser | null => {
    if (typeof window === 'undefined') return null
    const userStr = localStorage.getItem(USER_KEY)
    if (!userStr) return null
    try {
      const parsed: unknown = JSON.parse(userStr)
      if (parsed && typeof parsed === 'object' && 'email' in parsed) {
        return parsed as AuthUser
      }
      return null
    } catch {
      return null
    }
  },
  setUser: (user: AuthUser): void => {
    if (typeof window === 'undefined') return
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = tokenStorage.getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const url = `${API_BASE_URL}${endpoint}`
  let response: Response
  try {
    response = await fetch(url, {
      ...options,
      headers,
    })
  } catch {
    throw new Error(
      'Không thể kết nối đến máy chủ backend (http://localhost:8000). Vui lòng kiểm tra lại dịch vụ.'
    )
  }

  const rawData: unknown = await response.json().catch(() => null)

  if (!response.ok) {
    let errorDetail = 'Có lỗi xảy ra. Vui lòng thử lại.'
    if (rawData && typeof rawData === 'object' && 'detail' in rawData) {
      const errorObj = rawData as ApiErrorResponse
      if (typeof errorObj.detail === 'string') {
        errorDetail = errorObj.detail
      } else if (Array.isArray(errorObj.detail)) {
        errorDetail = errorObj.detail
          .map((item) => (item && typeof item === 'object' && item.msg ? item.msg : ''))
          .filter(Boolean)
          .join(', ')
      }
    }
    throw new Error(errorDetail)
  }

  return rawData as T
}

export const authApi = {
  register: async (payload: RegisterPayload): Promise<AuthTokenResponse> => {
    const data = await request<AuthTokenResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    tokenStorage.setToken(data.access_token)
    tokenStorage.setUser(data.user)
    return data
  },

  login: async (payload: LoginPayload): Promise<AuthTokenResponse> => {
    const data = await request<AuthTokenResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    tokenStorage.setToken(data.access_token)
    tokenStorage.setUser(data.user)
    return data
  },

  googleAuth: async (payload: GoogleAuthPayload): Promise<AuthTokenResponse> => {
    const data = await request<AuthTokenResponse>('/api/auth/google', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    tokenStorage.setToken(data.access_token)
    tokenStorage.setUser(data.user)
    return data
  },

  getMe: async (): Promise<AuthUser> => {
    const user = await request<AuthUser>('/api/auth/me', {
      method: 'GET',
    })
    tokenStorage.setUser(user)
    return user
  },

  forgotPassword: async (email: string): Promise<MessageResponse> => {
    return request<MessageResponse>('/api/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    })
  },

  logout: async (): Promise<void> => {
    try {
      await request<MessageResponse>('/api/auth/logout', {
        method: 'POST',
      })
    } catch {
      // Ignore network errors on logout
    } finally {
      tokenStorage.removeToken()
    }
  },
}
