export const BACKEND_RELOAD_ENDPOINT = '/plugin/reload/VuePanel'

export function normalizeVersion(value) {
  const match = String(value || '').trim().match(/^v?(\d+)\.(\d+)\.(\d+)$/i)
  return match ? match.slice(1).map(Number) : null
}

export function compareVersions(left, right) {
  const leftParts = normalizeVersion(left)
  const rightParts = normalizeVersion(right)
  if (!leftParts || !rightParts) return null

  for (let index = 0; index < leftParts.length; index += 1) {
    if (leftParts[index] === rightParts[index]) continue
    return leftParts[index] > rightParts[index] ? 1 : -1
  }
  return 0
}

export function extractBackendVersion(payload = {}) {
  return String(
    payload?.status?.dashboard?.schema_version
      || payload?.dashboard?.schema_version
      || '',
  ).trim()
}

export function decideBackendVersionAction(frontendVersion, backendVersion, alreadyAttempted) {
  const comparison = compareVersions(frontendVersion, backendVersion)
  if (comparison === 0) return 'ready'
  if (comparison === -1) return 'refresh-frontend'
  return alreadyAttempted ? 'manual-reload' : 'auto-reload'
}

export function backendReloadSessionKey(version) {
  return `vuepanel:backend-reload:${String(version || 'unknown')}`
}

function readStorage(storage, key) {
  try {
    return storage?.getItem?.(key) || null
  } catch (_) {
    return null
  }
}

function writeStorage(storage, key, value) {
  try {
    storage?.setItem?.(key, value)
  } catch (_) {
    // Browser privacy settings may disable sessionStorage; reloading can still proceed safely.
  }
}

const defaultWait = (delayMs) => new Promise((resolve) => setTimeout(resolve, delayMs))

export async function reloadVuePanelBackend({
  api,
  expectedVersion,
  readStatus,
  storage,
  wait = defaultWait,
  pollAttempts = 5,
  pollDelayMs = 500,
  force = false,
}) {
  const sessionKey = backendReloadSessionKey(expectedVersion)
  if (!force && readStorage(storage, sessionKey)) {
    return { success: false, reason: 'already-attempted', backendVersion: '', payload: null }
  }

  writeStorage(storage, sessionKey, 'attempted')

  try {
    const reloadResponse = await api.get(BACKEND_RELOAD_ENDPOINT)
    if (reloadResponse?.success === false) {
      throw new Error(reloadResponse.message || 'MoviePilot 重新加载插件失败')
    }
  } catch (error) {
    return {
      success: false,
      reason: 'reload-request-failed',
      backendVersion: '',
      payload: null,
      error,
    }
  }

  let backendVersion = ''
  let payload = null
  let lastError = null
  const attempts = Math.max(1, Number(pollAttempts) || 1)

  for (let attempt = 0; attempt < attempts; attempt += 1) {
    if (attempt > 0) await wait(pollDelayMs)
    try {
      payload = await readStatus()
      backendVersion = extractBackendVersion(payload)
      if (compareVersions(backendVersion, expectedVersion) === 0) {
        return { success: true, reason: 'ready', backendVersion, payload }
      }
    } catch (error) {
      lastError = error
    }
  }

  return {
    success: false,
    reason: payload ? 'version-mismatch' : 'status-unavailable',
    backendVersion,
    payload,
    error: lastError,
  }
}

export async function reconcileVuePanelBackend({
  api,
  expectedVersion,
  initialPayload,
  readStatus,
  storage,
  wait = defaultWait,
  pollAttempts = 5,
  pollDelayMs = 500,
}) {
  const backendVersion = extractBackendVersion(initialPayload)
  const attempted = !!readStorage(storage, backendReloadSessionKey(expectedVersion))
  const action = decideBackendVersionAction(expectedVersion, backendVersion, attempted)

  if (action !== 'auto-reload') {
    return {
      action,
      reloaded: false,
      backendVersion,
      payload: initialPayload,
      reason: action,
    }
  }

  const reloadResult = await reloadVuePanelBackend({
    api,
    expectedVersion,
    readStatus,
    storage,
    wait,
    pollAttempts,
    pollDelayMs,
  })

  if (reloadResult.success) {
    return {
      ...reloadResult,
      action: 'ready',
      reloaded: true,
    }
  }

  return {
    ...reloadResult,
    action: 'manual-reload',
    reloaded: false,
    backendVersion: reloadResult.backendVersion || backendVersion,
    payload: reloadResult.payload || initialPayload,
  }
}
