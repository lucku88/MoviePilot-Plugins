import assert from 'node:assert/strict'
import {
  BACKEND_RELOAD_ENDPOINT,
  backendReloadSessionKey,
  compareVersions,
  decideBackendVersionAction,
  extractBackendVersion,
  reconcileVuePanelBackend,
  reloadVuePanelBackend,
} from '../src/utils/backendVersion.js'

assert.equal(compareVersions('0.1.38', '0.1.37'), 1, '新版前端应识别为更高版本')
assert.equal(compareVersions('v0.1.38', '0.1.38'), 0, '版本比较应兼容 v 前缀')
assert.equal(compareVersions('0.1.37', '0.1.38'), -1, '旧版前端应识别为更低版本')

assert.equal(
  decideBackendVersionAction('0.1.38', '0.1.37', false),
  'auto-reload',
  '前端较新且未尝试时应自动重载后端',
)
assert.equal(
  decideBackendVersionAction('0.1.38', '0.1.37', true),
  'manual-reload',
  '同一会话已经尝试后只能手动重载',
)
assert.equal(
  decideBackendVersionAction('0.1.37', '0.1.38', false),
  'refresh-frontend',
  '后端较新时应提示刷新旧前端',
)
assert.equal(
  decideBackendVersionAction('0.1.38', '0.1.38', false),
  'ready',
  '前后端版本一致时无需处理',
)

assert.equal(
  extractBackendVersion({ status: { dashboard: { schema_version: '0.1.37' } } }),
  '0.1.37',
  '应从嵌套状态响应中读取后端版本',
)
assert.equal(
  extractBackendVersion({ dashboard: { schema_version: '0.1.38' } }),
  '0.1.38',
  '应从直接状态响应中读取后端版本',
)
assert.equal(BACKEND_RELOAD_ENDPOINT, '/plugin/reload/VuePanel', '必须调用 MoviePilot 内置重载接口')

function createMemoryStorage() {
  const values = new Map()
  return {
    getItem: (key) => values.get(key) || null,
    setItem: (key, value) => values.set(key, String(value)),
  }
}

const calls = []
const storage = createMemoryStorage()
const readyPayload = { dashboard: { schema_version: '0.1.38' } }
const reloadResult = await reloadVuePanelBackend({
  api: {
    get: async (path) => {
      calls.push(path)
      return { success: true }
    },
  },
  expectedVersion: '0.1.38',
  readStatus: async () => readyPayload,
  storage,
  wait: async () => {},
})

assert.equal(reloadResult.success, true, '重载后读到当前版本才算成功')
assert.equal(reloadResult.backendVersion, '0.1.38')
assert.equal(reloadResult.payload, readyPayload)
assert.deepEqual(calls, ['/plugin/reload/VuePanel'], '自动恢复只能调用 MoviePilot 内置重载接口')
assert.equal(
  storage.getItem(backendReloadSessionKey('0.1.38')),
  'attempted',
  '请求前应写入当前版本的会话标记',
)

const duplicateResult = await reloadVuePanelBackend({
  api: { get: async (path) => calls.push(path) },
  expectedVersion: '0.1.38',
  readStatus: async () => readyPayload,
  storage,
  wait: async () => {},
})

assert.equal(duplicateResult.success, false)
assert.equal(duplicateResult.reason, 'already-attempted')
assert.equal(calls.length, 1, '同一会话不应自动重复重载')

const forcedResult = await reloadVuePanelBackend({
  api: {
    get: async (path) => {
      calls.push(path)
      return { success: true }
    },
  },
  expectedVersion: '0.1.38',
  readStatus: async () => readyPayload,
  storage,
  wait: async () => {},
  force: true,
})

assert.equal(forcedResult.success, true, '手动操作应能绕过自动尝试限制')
assert.equal(calls.length, 2)

const pollingStorage = createMemoryStorage()
const pollingPayloads = [
  { dashboard: { schema_version: '0.1.37' } },
  { status: { dashboard: { schema_version: '0.1.38' } } },
]
let statusReads = 0
let waits = 0
const pollingResult = await reloadVuePanelBackend({
  api: { get: async () => ({ success: true }) },
  expectedVersion: '0.1.38',
  readStatus: async () => pollingPayloads[Math.min(statusReads++, pollingPayloads.length - 1)],
  storage: pollingStorage,
  wait: async () => { waits += 1 },
  pollAttempts: 3,
  pollDelayMs: 1,
})

assert.equal(pollingResult.success, true, '后端接口切换有短暂延迟时应继续轮询')
assert.equal(statusReads, 2)
assert.equal(waits, 1)

const reconcileCalls = []
const reconcileResult = await reconcileVuePanelBackend({
  api: {
    get: async (path) => {
      reconcileCalls.push(path)
      return { success: true }
    },
  },
  expectedVersion: '0.1.38',
  initialPayload: { dashboard: { schema_version: '0.1.37' } },
  readStatus: async () => ({ dashboard: { schema_version: '0.1.38' } }),
  storage: createMemoryStorage(),
  wait: async () => {},
})

assert.equal(reconcileResult.action, 'ready')
assert.equal(reconcileResult.reloaded, true)
assert.equal(reconcileResult.backendVersion, '0.1.38')
assert.deepEqual(reconcileCalls, ['/plugin/reload/VuePanel'])

const readyCalls = []
const readyResult = await reconcileVuePanelBackend({
  api: { get: async (path) => readyCalls.push(path) },
  expectedVersion: '0.1.38',
  initialPayload: { dashboard: { schema_version: '0.1.38' } },
  readStatus: async () => ({ dashboard: { schema_version: '0.1.38' } }),
  storage: createMemoryStorage(),
  wait: async () => {},
})

assert.equal(readyResult.action, 'ready')
assert.equal(readyResult.reloaded, false)
assert.deepEqual(readyCalls, [], '同版本不能触发重载')

const newerBackendCalls = []
const newerBackendResult = await reconcileVuePanelBackend({
  api: { get: async (path) => newerBackendCalls.push(path) },
  expectedVersion: '0.1.37',
  initialPayload: { dashboard: { schema_version: '0.1.38' } },
  readStatus: async () => ({ dashboard: { schema_version: '0.1.38' } }),
  storage: createMemoryStorage(),
  wait: async () => {},
})

assert.equal(newerBackendResult.action, 'refresh-frontend')
assert.deepEqual(newerBackendCalls, [], '浏览器前端较旧时不能反复重载新版后端')

const upgradedDuringReloadResult = await reconcileVuePanelBackend({
  api: { get: async () => ({ success: true }) },
  expectedVersion: '0.1.38',
  initialPayload: { dashboard: { schema_version: '0.1.37' } },
  readStatus: async () => ({ dashboard: { schema_version: '0.1.39' } }),
  storage: createMemoryStorage(),
  wait: async () => {},
})

assert.equal(upgradedDuringReloadResult.success, true, '重载得到更高版本后端也应视为切换成功')
assert.equal(upgradedDuringReloadResult.action, 'refresh-frontend', '后端更高时应提示重新打开前端')
assert.equal(upgradedDuringReloadResult.backendVersion, '0.1.39')
