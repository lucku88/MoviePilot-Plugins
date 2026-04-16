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

    const contentType = response.headers.get('content-type') || ''
    const isJson = contentType.includes('application/json')
    const payload = isJson ? await response.json() : await response.text()

    if (!response.ok) {
      const message = typeof payload === 'object' && payload
        ? (payload.message || `HTTP ${response.status}`)
        : `HTTP ${response.status}`
      throw new Error(message)
    }

    return payload
  }

  return {
    get: (url, config = {}) => request(url, { method: 'GET', ...config }),
    post: (url, data = {}, config = {}) => request(url, {
      method: 'POST',
      body: JSON.stringify(data),
      ...config,
    }),
    put: (url, data = {}, config = {}) => request(url, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...config,
    }),
  }
}
