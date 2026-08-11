# Vue-面板后端自动切换实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** Vue-面板更新后自动把仍绑定旧实例的后端接口切换到当前版本，同时保留卡片、Cookie、Cron、日志和运行时间。

**架构：** 前端构建时嵌入 `package.json` 版本，首次加载状态后与后端 `dashboard.schema_version` 比较。仅当前端较新时调用 MoviePilot 内置 `/plugin/reload/VuePanel`，并通过会话标记限制自动尝试次数；失败后由页面按钮手动重试。

**技术栈：** Vue 3、Vuetify、Vite、Node.js 内置测试断言、MoviePilot 插件 API、Python。

---

## 文件结构

- 创建 `plugins.v2/vuepanel/src/utils/backendVersion.js`：版本比较、重载决策和安全重载流程。
- 创建 `plugins.v2/vuepanel/tests/test_backend_version.mjs`：覆盖版本方向、循环保护和重载轮询。
- 修改 `plugins.v2/vuepanel/src/components/Page.vue`：首次加载时执行版本协调，并显示异常提示与手动按钮。
- 修改 `plugins.v2/vuepanel/vite.config.js`：从 `package.json` 注入前端版本常量。
- 修改 `plugins.v2/vuepanel/package.json`：升级版本并增加前端测试命令。
- 修改 `plugins.v2/vuepanel/__init__.py`：升级后端插件版本。
- 修改 `package.v2.json`：升级市场版本并记录更新说明，保留文件中的其他未提交修改。
- 更新 `plugins.v2/vuepanel/dist/`：重新构建 Vue 联邦模块产物。

### 任务 1：版本判断与安全重载工具

**文件：**
- 创建：`plugins.v2/vuepanel/tests/test_backend_version.mjs`
- 创建：`plugins.v2/vuepanel/src/utils/backendVersion.js`
- 修改：`plugins.v2/vuepanel/package.json`

- [ ] **步骤 1：编写版本方向的失败测试**

测试导入以下接口：

```javascript
import {
  BACKEND_RELOAD_ENDPOINT,
  compareVersions,
  decideBackendVersionAction,
  extractBackendVersion,
} from '../src/utils/backendVersion.js'
```

断言：

```javascript
assert.equal(compareVersions('0.1.38', '0.1.37'), 1)
assert.equal(compareVersions('v0.1.38', '0.1.38'), 0)
assert.equal(decideBackendVersionAction('0.1.38', '0.1.37', false), 'auto-reload')
assert.equal(decideBackendVersionAction('0.1.38', '0.1.37', true), 'manual-reload')
assert.equal(decideBackendVersionAction('0.1.37', '0.1.38', false), 'refresh-frontend')
assert.equal(decideBackendVersionAction('0.1.38', '0.1.38', false), 'ready')
assert.equal(extractBackendVersion({ status: { dashboard: { schema_version: '0.1.37' } } }), '0.1.37')
assert.equal(BACKEND_RELOAD_ENDPOINT, '/plugin/reload/VuePanel')
```

- [ ] **步骤 2：运行测试并确认因工具文件缺失而失败**

运行：

```powershell
node plugins.v2/vuepanel/tests/test_backend_version.mjs
```

预期：FAIL，提示无法找到 `src/utils/backendVersion.js`。

- [ ] **步骤 3：实现最少版本判断代码**

`backendVersion.js` 提供：

```javascript
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
    if (leftParts[index] !== rightParts[index]) return leftParts[index] > rightParts[index] ? 1 : -1
  }
  return 0
}
```

`decideBackendVersionAction()` 返回 `ready`、`auto-reload`、`manual-reload` 或 `refresh-frontend`。后端版本缺失或异常时按旧后端处理。

- [ ] **步骤 4：运行测试并确认版本判断通过**

运行：

```powershell
node plugins.v2/vuepanel/tests/test_backend_version.mjs
```

预期：PASS，进程退出码为 0。

- [ ] **步骤 5：追加安全重载流程的失败测试**

测试 `reloadVuePanelBackend()`：

```javascript
const calls = []
const storage = new Map()
const result = await reloadVuePanelBackend({
  api: { get: async (path) => calls.push(path) },
  expectedVersion: '0.1.38',
  readStatus: async () => ({ dashboard: { schema_version: '0.1.38' } }),
  storage: {
    getItem: (key) => storage.get(key) || null,
    setItem: (key, value) => storage.set(key, value),
  },
  wait: async () => {},
})

assert.equal(result.success, true)
assert.deepEqual(calls, ['/plugin/reload/VuePanel'])
```

再断言同一版本已经有会话标记时，非强制调用返回 `already-attempted` 且不会请求接口；`force: true` 可以手动重试。

- [ ] **步骤 6：运行测试并确认因重载函数缺失而失败**

运行：

```powershell
node plugins.v2/vuepanel/tests/test_backend_version.mjs
```

预期：FAIL，提示 `reloadVuePanelBackend` 未导出。

- [ ] **步骤 7：实现安全重载流程**

实现要求：

```javascript
export function backendReloadSessionKey(version) {
  return `vuepanel:backend-reload:${String(version || 'unknown')}`
}
```

- 请求前写入会话标记。
- 只调用 `BACKEND_RELOAD_ENDPOINT`，绝不调用 reset。
- 重载后最多读取状态 5 次，每次间隔 500 ms。
- 后端版本与 `expectedVersion` 相同才返回成功。
- 返回值包含 `success`、`reason`、`backendVersion` 和最后一次 `payload`。

- [ ] **步骤 8：运行测试并确认全部通过**

运行：

```powershell
npm run test:frontend
```

预期：版本工具测试与现有日志匹配测试均退出码为 0。

- [ ] **步骤 9：提交任务 1**

```powershell
git add plugins.v2/vuepanel/src/utils/backendVersion.js plugins.v2/vuepanel/tests/test_backend_version.mjs plugins.v2/vuepanel/package.json
git commit -m "test(Vue-面板): 覆盖后端版本自动切换"
```

### 任务 2：状态页自动协调和手动兜底

**文件：**
- 修改：`plugins.v2/vuepanel/src/components/Page.vue`
- 修改：`plugins.v2/vuepanel/vite.config.js`

- [ ] **步骤 1：扩充失败测试，固定页面接入所需状态**

为工具测试增加以下行为：

```javascript
assert.equal(decideBackendVersionAction('0.1.38', '', false), 'auto-reload')
assert.equal(decideBackendVersionAction('0.1.38', '', true), 'manual-reload')
```

增加轮询测试：第 1 次状态仍为 `0.1.37`，第 2 次变为 `0.1.38`，最终必须成功并返回新版状态。

- [ ] **步骤 2：运行测试并确认新轮询断言失败**

运行：

```powershell
npm run test:frontend
```

预期：FAIL，失败原因是当前重载流程没有按新断言返回最后状态或轮询次数不正确。

- [ ] **步骤 3：补齐工具返回值并让测试通过**

确保 `reloadVuePanelBackend()` 返回成功时携带新版状态 `payload`，失败时保留最后识别到的后端版本。

- [ ] **步骤 4：在 Vite 中注入前端版本**

`vite.config.js` 从同目录 `package.json` 读取版本，并加入：

```javascript
define: {
  __VUEPANEL_VERSION__: JSON.stringify(packageJson.version),
},
```

- [ ] **步骤 5：在状态页接入自动重载**

`Page.vue` 导入工具，并定义：

```javascript
const FRONTEND_VERSION = __VUEPANEL_VERSION__
const backendUpdate = reactive({
  action: 'ready',
  frontendVersion: FRONTEND_VERSION,
  backendVersion: '',
  loading: false,
  error: '',
})
```

首次 `loadStatus()` 后调用 `reconcileBackendVersion(payload)`：

- `ready`：隐藏提示。
- `auto-reload`：调用安全重载函数，成功后 `applyStatusPayload(result.payload)`。
- `manual-reload`：显示按钮，不再自动请求。
- `refresh-frontend`：提示关闭并重新打开 Vue-面板。

手动按钮调用同一函数并传入 `force: true`。

- [ ] **步骤 6：增加紧凑版本提示**

在普通消息提示上方增加 `v-alert`。只有 `backendUpdate.action !== 'ready'` 时显示，内容包含前端版本、后端版本和恢复说明；`manual-reload` 状态显示「重新加载后端」按钮。

- [ ] **步骤 7：运行前端测试和构建**

运行：

```powershell
npm run test:frontend
npm run build
```

预期：测试全部通过；Vite 构建退出码为 0，产物中包含 `/plugin/reload/VuePanel` 和当前前端版本。

- [ ] **步骤 8：提交任务 2**

```powershell
git add plugins.v2/vuepanel/src/components/Page.vue plugins.v2/vuepanel/vite.config.js plugins.v2/vuepanel/src/utils/backendVersion.js plugins.v2/vuepanel/tests/test_backend_version.mjs plugins.v2/vuepanel/dist
git commit -m "fix(Vue-面板): 自动切换更新后的后端实例"
```

### 任务 3：版本发布和完整验证

**文件：**
- 修改：`plugins.v2/vuepanel/__init__.py`
- 修改：`plugins.v2/vuepanel/package.json`
- 修改：`package.v2.json`
- 更新：`plugins.v2/vuepanel/dist/`

- [ ] **步骤 1：统一升级到 v0.1.38**

修改：

```text
plugins.v2/vuepanel/__init__.py        plugin_version = "0.1.38"
plugins.v2/vuepanel/package.json       "version": "0.1.38"
package.v2.json                        "version": "0.1.38"
```

市场历史新增：更新后状态页会检测前后端版本；发现旧后端时调用 MoviePilot 内置重载保留配置并切换接口，失败时提供手动按钮。

- [ ] **步骤 2：重新构建最终版本产物**

运行：

```powershell
npm run build
```

工作目录：`plugins.v2/vuepanel`

预期：构建退出码为 0，产物嵌入 `0.1.38`。

- [ ] **步骤 3：运行完整自动化验证**

运行：

```powershell
python -m py_compile plugins.v2/vuepanel/__init__.py
npm run test:frontend
node plugins.v2/vuepanel/tests/test_log_matching.mjs
python -m unittest discover -s plugins.v2/vuepanel/tests -p "test_*.py"
git diff --check
```

预期：全部命令退出码为 0，且没有空白错误。

- [ ] **步骤 4：检查变更范围**

运行：

```powershell
git status --short
git diff --stat HEAD
git diff -- package.v2.json
```

确认只提交 Vue-面板相关版本行与历史条目，不提交 `FnMediaCoverGenerator` 的用户修改，也不提交 `.playwright-cli/`、`.superpowers/` 和 `output/`。

- [ ] **步骤 5：提交任务 3**

```powershell
git add plugins.v2/vuepanel/__init__.py plugins.v2/vuepanel/package.json package.v2.json plugins.v2/vuepanel/dist
git commit -m "chore(Vue-面板): 发布后端自动切换版本"
```

提交 `package.v2.json` 时使用交互补丁或临时索引，仅暂存 VuePanel 区块，排除其他插件的未提交修改。

### 任务 4：实机验证并推送 main

**文件：**
- 不新增源码文件。

- [ ] **步骤 1：记录更新前配置快照**

从已登录 MoviePilot 的 `/plugin/VuePanel/status` 记录：后端版本、卡片数量、启用数量、各卡片 Cron、历史数量和 `last_run`。不要执行任何功能任务。

- [ ] **步骤 2：让 MoviePilot 获取 v0.1.38 更新**

通过插件市场更新或 PluginManagerVue 重装 Vue-面板，不点击「重置插件」。

- [ ] **步骤 3：打开新版状态页触发自动协调**

确认首次状态可能返回旧后端版本，随后页面调用 `/plugin/reload/VuePanel`，最终状态返回 `schema_version: 0.1.38`。

- [ ] **步骤 4：核对配置未丢失且没有误执行**

重新读取状态，核对卡片数量、Cookie 是否已配置、Cron、历史数量和 `last_run` 与更新前一致。检查插件日志中没有因版本切换触发签到、领取、下馆子、展柜或舞台任务。

- [ ] **步骤 5：合并到 main 并推送**

在验证分支通过后，将提交快进合并到 `main`，保留主工作区中的用户修改，然后执行：

```powershell
git push origin main
```

预期：远端 `origin/main` 指向本次发布提交。
