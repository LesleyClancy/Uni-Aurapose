export const API_BASE_URL = 'http://10.190.232.61:5000'
export const DEFAULT_OPENID = 'dev-openid'

export function getOpenid() {
  return uni.getStorageSync('profitai_openid') || DEFAULT_OPENID
}

export function setOpenid(openid) {
  if (openid) {
    uni.setStorageSync('profitai_openid', openid)
  }
}

export function apiRequest(path, options = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`
  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method: options.method || 'GET',
      data: options.data || {},
      timeout: options.timeout || 120000,
      header: {
        'content-type': 'application/json',
        ...(options.header || {})
      },
      success: (response) => {
        const data = response.data || {}
        if (response.statusCode >= 200 && response.statusCode < 300 && !data.error) {
          resolve(data)
          return
        }
        reject(data.error || data.message || `HTTP ${response.statusCode}`)
      },
      fail: (error) => {
        reject(error.errMsg || 'network error')
      }
    })
  })
}

export function fetchBootstrap(openid = getOpenid()) {
  return apiRequest(`/api/app/bootstrap?openid=${encodeURIComponent(openid)}`)
}

export function saveProfile(profile) {
  return apiRequest('/api/users/upsert', {
    method: 'POST',
    data: {
      openid: getOpenid(),
      ...profile
    }
  })
}

export function createTrainingSession(payload = {}) {
  return apiRequest('/api/training/sessions', {
    method: 'POST',
    data: {
      openid: getOpenid(),
      ...payload
    }
  })
}

export function finishTrainingSession(sessionId, payload = {}) {
  return apiRequest(`/api/training/sessions/${sessionId}/finish`, {
    method: 'POST',
    data: payload
  })
}
