const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

async function parseResponse(res) {
  const contentType = res.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return res.json()
  }
  const text = await res.text()
  return text ? { detail: text } : {}
}

export async function apiRequest(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  const data = await parseResponse(res)
  if (!res.ok) {
    const detail = typeof data?.detail === 'string' ? data.detail : `Request failed (${res.status})`
    throw new Error(detail)
  }

  return data
}
