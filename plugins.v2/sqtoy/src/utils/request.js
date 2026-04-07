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
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return response.json()
  }

  return {
    get: (url, config = {}) => request(url, { method: 'GET', ...config }),
    post: (url, data = {}, config = {}) => request(url, { method: 'POST', body: JSON.stringify(data), ...config }),
  }
}
