// 默认后端地址：调试用局域网 IP（手机/小程序需与运行后端的电脑同网段）
// App 发行前可在「设置 → 服务器地址」填入生产服务器（建议 HTTPS 域名）
export const DEFAULT_API_BASE_URL = 'http://10.190.232.61:5000'
export const API_BASE_URL_STORAGE_KEY = 'profitai_api_base_url'
export const DEFAULT_OPENID = 'dev-openid'
export const DETECT_MODE_STORAGE_KEY = 'profitai_detect_mode'

export function getApiBaseUrl() {
  const saved = uni.getStorageSync(API_BASE_URL_STORAGE_KEY)
  if (typeof saved === 'string' && saved.trim()) {
    return saved.trim().replace(/\/+$/, '')
  }
  return DEFAULT_API_BASE_URL
}

export function setApiBaseUrl(url) {
  const normalized = String(url || '').trim().replace(/\/+$/, '')
  if (normalized) {
    uni.setStorageSync(API_BASE_URL_STORAGE_KEY, normalized)
  } else {
    uni.removeStorageSync(API_BASE_URL_STORAGE_KEY)
  }
  return getApiBaseUrl()
}

export function getOpenid() {
  return uni.getStorageSync('profitai_openid') || DEFAULT_OPENID
}

// 识别模式：App 端默认 local（端侧 AI，离线可用），其余平台默认 server
export function getDetectMode() {
  const saved = uni.getStorageSync(DETECT_MODE_STORAGE_KEY)
  if (saved === 'local' || saved === 'server') {
    return saved
  }
  // #ifdef APP-PLUS
  return 'local'
  // #endif
  // #ifndef APP-PLUS
  return 'server'
  // #endif
}

export function setDetectMode(mode) {
  if (mode === 'local' || mode === 'server') {
    uni.setStorageSync(DETECT_MODE_STORAGE_KEY, mode)
  } else {
    uni.removeStorageSync(DETECT_MODE_STORAGE_KEY)
  }
  return getDetectMode()
}

export function setOpenid(openid) {
  if (openid) {
    uni.setStorageSync('profitai_openid', openid)
  }
}

export function apiRequest(path, options = {}) {
  const url = path.startsWith('http') ? path : `${getApiBaseUrl()}${path}`
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

export function fetchRecoveryStatus(openid = getOpenid()) {
  return apiRequest(`/api/users/${encodeURIComponent(openid)}/recovery`)
}

export function saveRecoveryCheckin(prsScore, openid = getOpenid()) {
  return apiRequest(`/api/users/${encodeURIComponent(openid)}/recovery`, {
    method: 'POST',
    data: { prs_score: prsScore }
  })
}

export function fetchProgress(days = 7, openid = getOpenid()) {
  return apiRequest(`/api/users/${encodeURIComponent(openid)}/progress?days=${encodeURIComponent(days)}`)
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

// 离线训练本地存档：会话创建/结束失败时留存训练摘要，避免数据丢失
export const PENDING_SESSIONS_STORAGE_KEY = 'profitai_pending_sessions'

export function savePendingSession(summary) {
  const list = uni.getStorageSync(PENDING_SESSIONS_STORAGE_KEY) || []
  list.push(summary)
  uni.setStorageSync(PENDING_SESSIONS_STORAGE_KEY, list)
  return list.length
}

export function getPendingSessions() {
  return uni.getStorageSync(PENDING_SESSIONS_STORAGE_KEY) || []
}
