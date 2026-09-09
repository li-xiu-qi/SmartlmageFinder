// 统一 API 响应类型
export interface ApiResponse<T> {
  code: number | string
  message: string
  data: T
  metadata?: any
}

export interface Pagination {
  page: number
  page_size: number
  total_items: number
  total_pages: number
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  metadata: { pagination: Pagination }
}

// 统一请求封装
async function request<T>(url: string, options?: RequestInit): Promise<ApiResponse<T>> {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }))
    throw new Error(err.message || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  get: <T>(url: string, params?: Record<string, any>) => {
    const qs = params ? '?' + new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
        .map(([k, v]) => [k, String(v)])
    ).toString() : ''
    return request<T>(`/api/v1${url}${qs}`)
  },
  post: <T>(url: string, data?: any) =>
    request<T>(`/api/v1${url}`, { method: 'POST', body: data instanceof FormData ? data : JSON.stringify(data),
      headers: data instanceof FormData ? {} : { 'Content-Type': 'application/json' } }),
  put: <T>(url: string, data?: any) =>
    request<T>(`/api/v1${url}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: <T>(url: string, body?: any) =>
    request<T>(`/api/v1${url}`, { method: 'DELETE', body: body ? JSON.stringify(body) : undefined }),
}

// 图片类型
export interface ImageDetail {
  id: number
  filename: string
  filepath: string
  title: string
  description: string
  file_size: number
  file_type: string
  width: number
  height: number
  created_at: string
  updated_at: string
  metadata: string
  tags: string
}

export const imageService = {
  getList: (params?: { page?: number; page_size?: number; tags?: string; search?: string }) =>
    api.get<ImageDetail[]>('/images', params),
  getDetail: (id: number | string) =>
    api.get<ImageDetail>(`/images/${id}`),
  upload: (files: File[], options?: { auto_analyze?: boolean }) => {
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    if (options?.auto_analyze) formData.append('auto_analyze', 'true')
    return api.post<ImageDetail[]>('/images/upload', formData)
  },
  update: (id: number, data: { title?: string; description?: string; tags?: string[] }) =>
    api.put<ImageDetail>(`/images/${id}`, data),
  delete: (id: number) =>
    api.delete<{ id: number }>(`/images/${id}`),
  batchDelete: (ids: number[]) =>
    api.delete<any>('/images/batch', { image_ids: ids }),
  exportAllUrl: () => '/api/v1/images/export-all',
}

export const tagService = {
  getAll: (search?: string) =>
    api.get<Array<{ name: string; count: number }>>('/tags', { search }),
}

export const searchService = {
  similar: (id: number, params?: { vector_type?: string; limit?: number }) =>
    api.get<any[]>(`/search/similar/${id}`, params),
}

export const systemService = {
  getStatus: () =>
    api.get<any>('/system'),
}
