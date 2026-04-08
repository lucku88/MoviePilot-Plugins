export function createRequest(baseURL = '') {
  const request = async (url, options = {}) => {
    const fullUrl = baseURL ? `${baseURL}${url}` : url
    const response = await fetch(fullUrl, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    })
    const data = await response.json().catch(() => null)
    if (!response.ok) {
      const message = data?.message || data?.detail || `HTTP ${response.status}`
      throw new Error(message)
    }
    return data
  }

  return {
    get: (url, config = {}) => request(url, { method: 'GET', ...config }),
    post: (url, data = {}, config = {}) => request(url, { method: 'POST', body: JSON.stringify(data), ...config }),
  }
}
