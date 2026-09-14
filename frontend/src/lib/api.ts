const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const msg = await res.text()
    throw new Error(`${res.status}: ${msg}`)
  }
  return res.json()
}

// ── Opportunities ─────────────────────────────────────────────────────────────
export const api = {
  opportunities: {
    list: (params?: { category?: string; keyword?: string }) => {
      const qs = new URLSearchParams()
      if (params?.category) qs.set('category', params.category)
      if (params?.keyword) qs.set('keyword', params.keyword)
      return req<{ count: number; opportunities: any[] }>(`/api/opportunities?${qs}`)
    },
    get: (id: string) => req<any>(`/api/opportunities/${id}`),
  },

  missions: {
    list: () => req<{ count: number; missions: any[] }>('/api/missions'),
    get: (id: string) => req<any>(`/api/missions/${id}`),
    create: (body: { opportunity_id: string; goal?: string }) =>
      req<any>('/api/missions', { method: 'POST', body: JSON.stringify(body) }),
    approve: (id: string, action: 'approve' | 'deny', reason?: string) =>
      req<any>(`/api/missions/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ action, reason }),
      }),
    cancel: (id: string) =>
      req<any>(`/api/missions/${id}/cancel`, { method: 'POST' }),
    events: (id: string) =>
      req<{ mission_id: string; count: number; events: any[] }>(`/api/missions/${id}/events`),
  },

  documents: {
    list: () => req<{ count: number; documents: any[] }>('/api/documents'),
    add: (body: { name: string; file_path: string; status?: string }) =>
      req<any>('/api/documents', { method: 'POST', body: JSON.stringify(body) }),
  },

  applications: {
    list: () => req<{ count: number; applications: any[] }>('/api/applications'),
    get: (id: string) => req<any>(`/api/applications/${id}`),
  },

  notifications: {
    list: () => req<{ count: number; unread_count: number; notifications: any[] }>('/api/notifications'),
    markRead: (id: string) => req<any>(`/api/notifications/${id}/read`, { method: 'POST' }),
  },

  agent: {
    status: () => req<any>('/api/agent/status'),
    run: (message: string) =>
      fetch(`${BASE}/api/agent/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      }),
  },
}
