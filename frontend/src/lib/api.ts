const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface RequestOptions extends RequestInit {
  params?: Record<string, string>
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options
  
  let url = `${API_BASE_URL}${endpoint}`
  if (params) {
    const searchParams = new URLSearchParams(params)
    url += `?${searchParams.toString()}`
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Health
  health: () => request('/api/health'),
  
  // Transactions
  getTransactions: (params?: { source?: string; flagged_only?: boolean }) => {
    const searchParams: Record<string, string> = {}
    if (params?.source) searchParams.source = params.source
    if (params?.flagged_only) searchParams.flagged_only = 'true'
    return request('/api/transactions', { params: searchParams })
  },
  
  getTransaction: (id: number) => request(`/api/transactions/${id}`),
  
  uploadStatement: async (source: string, file: File) => {
    const formData = new FormData()
    formData.append('source', source)
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/api/transactions/upload/statement`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`)
    }
    
    return response.json()
  },
  
  getMonthlySummary: (year: number, month: number) => 
    request(`/api/transactions/summary/monthly`, { 
      params: { year: year.toString(), month: month.toString() } 
    }),
}
