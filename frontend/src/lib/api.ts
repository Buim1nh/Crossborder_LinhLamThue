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
  credential?: string
  access_token?: string
  email?: string
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

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_BASE_URL = rawApiUrl.replace(/\/+$/, '')

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
  } catch (err: unknown) {
    const nativeMsg = err instanceof Error ? err.message : ''
    throw new Error(
      `Không thể kết nối đến máy chủ backend (${API_BASE_URL}). Vui lòng kiểm tra lại dịch vụ và CORS.${nativeMsg ? ` Chi tiết: ${nativeMsg}` : ''}`
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

// ─── Subscription / ML Model ───────────────────────────────────────────────

export interface ScoredTransaction {
  subscription_proba: number
  is_subscription: number
  model_version: string
}

export interface SubscriptionScoreRequest {
  transactions: TransactionRow[]
  threshold?: number
}

export interface SubscriptionScoreResponse {
  model_version: string
  threshold: number
  n_scored: number
  n_subscription: number
  results: ScoredTransaction[]
}

export interface SubscriptionModelInfo {
  version: string
  threshold: number
  train_rows: number
  positive_rate: number
  cv_mcc: number
  cv_precision: number
  cv_recall: number
  feature_mode: string
  created_at: string
  git_sha?: string
}

/** Raw statement row — must match the CSV column names the ML model expects. */
export interface TransactionRow {
  [key: string]: string | number | boolean | null | undefined
}

export const subscriptionsApi = {
  getModelInfo: async (): Promise<SubscriptionModelInfo> => {
    return request<SubscriptionModelInfo>('/api/subscriptions/model')
  },

  scoreTransactions: async (
    payload: SubscriptionScoreRequest
  ): Promise<SubscriptionScoreResponse> => {
    return request<SubscriptionScoreResponse>('/api/subscriptions/score', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },
}

// ─── Transactions ──────────────────────────────────────────────────────────

export interface TransactionFilters {
  source?: string
  is_flagged?: boolean
  is_subscription?: boolean
  limit?: number
  offset?: number
}

export interface TransactionListResponse {
  total: number
  limit: number
  offset: number
  transactions: TransactionSummary[]
}

export interface TransactionSummary {
  id: number
  source: string
  source_id?: string
  type: string
  amount: number
  currency: string
  description: string
  merchant_name?: string
  category?: string
  transaction_date: string
  is_flagged: boolean
  alert_level?: string
  alert_reason?: string
  is_subscription: boolean
  subscription_name?: string
  next_charge_date?: string
  masked_card?: string
}

export const transactionsApi = {
  list: async (filters: TransactionFilters = {}): Promise<TransactionListResponse> => {
    const params = new URLSearchParams()
    if (filters.source) params.set('source', filters.source)
    if (filters.is_flagged !== undefined) params.set('is_flagged', String(filters.is_flagged))
    if (filters.is_subscription !== undefined) params.set('is_subscription', String(filters.is_subscription))
    if (filters.limit !== undefined) params.set('limit', String(filters.limit))
    if (filters.offset !== undefined) params.set('offset', String(filters.offset))
    const qs = params.toString()
    return request<TransactionListResponse>(`/api/transactions${qs ? `?${qs}` : ''}`)
  },
}

// ─── Chat ────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatResponse {
  reply: string
  model: string
}

export const chatApi = {
  sendMessage: async (message: string, history: ChatMessage[] = []): Promise<ChatResponse> => {
    return request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    })
  },
}

// ─── Upload ─────────────────────────────────────────────────────────────────

export interface UploadResponse {
  source: string
  file_name: string
  total_parsed: number
  total_saved: number
  n_subscriptions: number
  scored: ScoredTransaction[]
}

export const uploadApi = {
  uploadStatement: async (
    source: 'bank' | 'wallet' | 'card',
    file: File
  ): Promise<UploadResponse> => {
    const token = tokenStorage.getToken()
    const formData = new FormData()
    formData.append('source', source)
    formData.append('file', file)

    const url = `${API_BASE_URL}/api/upload/upload`
    const response = await fetch(url, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    })

    const rawData: unknown = await response.json().catch(() => null)

    if (!response.ok) {
      let errorDetail = 'Có lỗi xảy ra. Vui lòng thử lại.'
      if (rawData && typeof rawData === 'object' && 'detail' in rawData) {
        const d = (rawData as { detail?: string }).detail
        if (typeof d === 'string') errorDetail = d
      }
      throw new Error(errorDetail)
    }

    return rawData as UploadResponse
  },
}
