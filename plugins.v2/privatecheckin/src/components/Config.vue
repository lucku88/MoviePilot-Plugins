<template>
  <div ref="rootEl" class="pc-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="pc-shell">
      <section class="pc-hero">
        <div class="pc-hero-copy">
          <div class="pc-badge">自用签到</div>
          <h1 class="pc-title">配置页</h1>
          <p class="pc-subtitle">
            这里统一管理签到页、接口请求、Cookie 和过 CF 策略。浏览器型任务默认优先用 MoviePilot 自带的 Playwright，
            接口型任务默认按 requests 执行。
          </p>
        </div>
        <div class="pc-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回数据页</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存配置</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="pc-grid">
        <article class="pc-panel">
          <div class="pc-panel-head">
            <div>
              <div class="pc-kicker">运行控制</div>
              <h2>全局调度</h2>
            </div>
          </div>
          <div class="pc-switch-grid">
            <v-switch v-model="config.enabled" label="启用插件" color="success" hide-details />
            <v-switch v-model="config.notify" label="发送通知" color="primary" hide-details />
            <v-switch v-model="config.onlyonce" label="保存后立即运行一次" color="warning" hide-details />
            <v-switch v-model="config.use_proxy" label="默认使用系统代理" color="info" hide-details />
            <v-switch v-model="config.force_ipv4" label="默认优先 IPv4" color="secondary" hide-details />
          </div>
          <div class="pc-form-grid">
            <v-text-field
              v-model="config.cron"
              label="执行周期"
              hint="5 位 Cron，例如 0 9 * * *"
              persistent-hint
              variant="outlined"
              density="comfortable"
            />
            <v-text-field v-model="config.max_workers" type="number" label="并发任务数" variant="outlined" density="comfortable" />
            <v-text-field
              v-model="config.random_delay_max_seconds"
              type="number"
              label="随机延迟上限(秒)"
              variant="outlined"
              density="comfortable"
            />
          </div>
        </article>

        <article class="pc-panel">
          <div class="pc-panel-head">
            <div>
              <div class="pc-kicker">CF 与网络</div>
              <h2>请求环境</h2>
            </div>
          </div>
          <div class="pc-form-grid">
            <v-text-field v-model="config.http_timeout" type="number" label="HTTP 超时(秒)" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.http_retry_times" type="number" label="重试次数" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.http_retry_delay" type="number" label="重试间隔(ms)" variant="outlined" density="comfortable" />
            <v-text-field
              v-model="config.flaresolverr_url"
              label="FlareSolverr 地址"
              placeholder="http://flaresolverr:8191/v1"
              hint="MoviePilot V2 已自带 Playwright。只有强 CF 仍过不去时，再额外部署 FlareSolverr。"
              persistent-hint
              variant="outlined"
              density="comfortable"
            />
          </div>
          <div class="pc-note-stack">
            <div class="pc-note">
              `智能兜底` 会按 `Playwright -> requests -> FlareSolverr` 顺序尝试。浏览器自动签到页通常优先用 `仅 Playwright`，
              接口签到通常优先用 `仅请求`。
            </div>
            <div class="pc-note">
              如果站点已经配置在 MoviePilot 站点管理里，可以打开“优先使用 MoviePilot Cookie”；否则直接填写浏览器 Cookie 或请求头。
            </div>
          </div>
        </article>
      </section>

      <section class="pc-panel">
        <div class="pc-panel-head">
          <div>
            <div class="pc-kicker">常见方式</div>
            <h2>任务类型说明</h2>
          </div>
        </div>
        <div class="pc-note-grid">
          <article v-for="item in modeGuides" :key="item.title" class="pc-note-card">
            <strong>{{ item.title }}</strong>
            <p>{{ item.text }}</p>
          </article>
        </div>
      </section>

      <section class="pc-panel">
        <div class="pc-panel-head pc-panel-head-wrap">
          <div>
            <div class="pc-kicker">任务编排</div>
            <h2>签到 / 领取任务列表</h2>
          </div>
          <div class="pc-actions">
            <v-btn color="success" variant="flat" @click="addTask">新增任务</v-btn>
          </div>
        </div>

        <v-alert type="info" variant="tonal" class="mb-4">
          新任务默认是空白配置，请自己填写站点地址、任务地址、Cookie 或请求参数后再启用。
        </v-alert>

        <div v-if="!config.tasks.length" class="pc-empty">
          还没有任务，点击右上角“新增任务”开始。
        </div>

        <v-expansion-panels v-else multiple class="pc-panels">
          <v-expansion-panel v-for="(task, index) in config.tasks" :key="task.id">
            <v-expansion-panel-title>
              <div class="pc-task-title">
                <div>
                  <strong>{{ task.name || `任务 ${index + 1}` }}</strong>
                  <div class="pc-mini">{{ resolveTaskTypeLabel(task.task_type) }}</div>
                </div>
                <div class="pc-title-meta">
                  <v-chip size="small" :color="task.enabled ? 'success' : 'default'" variant="tonal">
                    {{ task.enabled ? '启用' : '未启用' }}
                  </v-chip>
                  <v-chip size="small" color="primary" variant="tonal">
                    {{ resolveCfModeLabel(task.cf_mode) }}
                  </v-chip>
                </div>
              </div>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <div class="pc-task-layout">
                <section class="pc-task-group">
                  <div class="pc-group-head">
                    <div class="pc-kicker">基础信息</div>
                    <div class="pc-mini">{{ taskTypeDescription(task.task_type) }}</div>
                  </div>
                  <div class="pc-form-grid">
                    <v-text-field v-model="task.name" label="任务名称" variant="outlined" density="comfortable" />
                    <v-select
                      v-model="task.task_type"
                      :items="taskTypeOptions"
                      label="任务类型"
                      variant="outlined"
                      density="comfortable"
                      @update:modelValue="handleTaskTypeChange(task)"
                    />
                    <v-text-field
                      v-model="task.site_url"
                      label="站点地址"
                      placeholder="https://example.com"
                      variant="outlined"
                      density="comfortable"
                    />
                    <v-text-field
                      v-model="task.target_url"
                      label="签到 / 任务地址"
                      :placeholder="taskTargetPlaceholder(task.task_type)"
                      variant="outlined"
                      density="comfortable"
                    />
                  </div>
                </section>

                <section class="pc-task-group">
                  <div class="pc-group-head">
                    <div class="pc-kicker">Cookie 与过盾</div>
                    <div class="pc-mini">浏览器自动签到页默认建议 Playwright，接口型任务默认建议 requests。</div>
                  </div>
                  <div class="pc-switch-grid pc-switch-grid-tight">
                    <v-switch v-model="task.enabled" label="启用任务" color="success" hide-details />
                    <v-switch v-model="task.use_moviepilot_cookie" label="优先使用 MoviePilot Cookie" color="info" hide-details />
                    <v-switch v-model="task.use_proxy" label="该任务使用代理" color="secondary" hide-details />
                    <v-switch v-model="task.force_ipv4" label="该任务优先 IPv4" color="secondary" hide-details />
                    <v-switch
                      v-if="task.task_type === 'generic_attendance'"
                      v-model="task.allow_logged_in_as_success"
                      label="页面可正常打开即视为通过"
                      color="warning"
                      hide-details
                    />
                  </div>
                  <div class="pc-form-grid">
                    <v-text-field
                      v-model="task.moviepilot_domain"
                      label="MoviePilot 站点域名"
                      placeholder="example.com"
                      hint="用于同步站点 Cookie；不填会自动从地址里提取。"
                      persistent-hint
                      variant="outlined"
                      density="comfortable"
                    />
                    <v-select
                      v-model="task.cf_mode"
                      :items="cfModeOptions"
                      label="CF 策略"
                      variant="outlined"
                      density="comfortable"
                    />
                    <v-text-field
                      v-model="task.user_agent"
                      label="自定义 User-Agent"
                      placeholder="留空则使用内置默认 UA"
                      variant="outlined"
                      density="comfortable"
                    />
                    <v-text-field
                      v-if="task.task_type === 'new_api_checkin'"
                      v-model="task.new_api_uid"
                      label="Legacy UID"
                      placeholder="仅旧专用任务需要"
                      variant="outlined"
                      density="comfortable"
                    />
                  </div>
                  <v-textarea
                    v-model="task.cookie"
                    label="手动 Cookie"
                    rows="4"
                    auto-grow
                    variant="outlined"
                    density="comfortable"
                    placeholder="例如 cf_clearance=...; passkey=..."
                  />
                </section>

                <section v-if="usesRequestPayload(task.task_type)" class="pc-task-group">
                  <div class="pc-group-head">
                    <div class="pc-kicker">接口参数</div>
                    <div class="pc-mini">支持自定义请求头和请求体，适配 GET / 表单 / JSON 这几类常见方式。</div>
                  </div>
                  <div class="pc-form-grid pc-form-grid-wide">
                    <v-textarea
                      v-model="task.request_headers"
                      label="请求头"
                      rows="5"
                      auto-grow
                      variant="outlined"
                      density="comfortable"
                      placeholder='JSON 或每行一个 Header: Value，例如 {"X-Requested-With":"XMLHttpRequest"}'
                    />
                    <v-textarea
                      v-model="task.request_body"
                      :label="requestBodyLabel(task.task_type)"
                      rows="5"
                      auto-grow
                      variant="outlined"
                      density="comfortable"
                      :placeholder="requestBodyPlaceholder(task.task_type)"
                    />
                  </div>
                </section>

                <section v-if="usesKeywordMatcher(task.task_type)" class="pc-task-group">
                  <div class="pc-group-head">
                    <div class="pc-kicker">响应匹配</div>
                    <div class="pc-mini">可用关键字或正则匹配响应内容，支持用 `|` 分隔多个条件。</div>
                  </div>
                  <div class="pc-form-grid pc-form-grid-wide">
                    <v-textarea
                      v-model="task.success_keywords"
                      label="成功关键字 / 正则"
                      rows="4"
                      auto-grow
                      variant="outlined"
                      density="comfortable"
                      placeholder='例如 签到成功|今日已签到|"success":true'
                    />
                    <v-textarea
                      v-model="task.failure_keywords"
                      label="失败关键字 / 正则"
                      rows="4"
                      auto-grow
                      variant="outlined"
                      density="comfortable"
                      placeholder='例如 未登录|Cookie已失效|"success":false'
                    />
                  </div>
                </section>

                <div class="pc-task-footer">
                  <div class="pc-mini">{{ taskTypeDescription(task.task_type) }}</div>
                  <v-btn color="error" variant="tonal" @click="removeTask(index)">删除任务</v-btn>
                </div>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
})

const emit = defineEmits(['switch', 'close'])

const DEFAULT_SUCCESS_KEYWORDS = '签到成功|今日已签到|已经签到|已签到|签到已得|"success":true|"status":"success"|already signed|already attended|check-in completed'
const DEFAULT_FAILURE_KEYWORDS = 'Cookie已失效|未登录|请先登录|重新登录|login required'
const REQUEST_TASK_TYPES = ['request_get', 'request_post_form', 'request_post_json']
const KEYWORD_TASK_TYPES = ['generic_attendance', ...REQUEST_TASK_TYPES]
const LEGACY_TASK_LABELS = {
  siqi_attendance: '思齐签到（旧专用模式）',
  siqi_hnr_claim: '思齐 HNR 领取（旧专用模式）',
  new_api_checkin: 'New API 签到（旧专用模式）',
}
const BASE_TASK_TYPE_OPTIONS = [
  { title: '浏览器自动签到页', value: 'generic_attendance' },
  { title: 'GET 接口签到', value: 'request_get' },
  { title: 'POST 表单签到', value: 'request_post_form' },
  { title: 'POST JSON 签到', value: 'request_post_json' },
]

const rootEl = ref(null)
const isDarkTheme = ref(false)
const saving = ref(false)
const taskSeed = ref(1)
const message = reactive({ text: '', type: 'success' })
const modeGuides = [
  {
    title: '浏览器自动签到页',
    text: '适合 attendance.php、bonus.php 或打开页面就自动签到的站点。默认建议 Playwright，站点地址填域名，任务地址填签到页。',
  },
  {
    title: 'GET 接口签到',
    text: '适合点击按钮后实际发起 GET 请求的接口。请求参数填 query string，成功/失败关键字可以写接口返回里的标识。',
  },
  {
    title: 'POST 表单签到',
    text: '适合 application/x-www-form-urlencoded 类型接口。请求体写成 key=value，每行一个或用 & 连接都可以。',
  },
  {
    title: 'POST JSON 签到',
    text: '适合 JSON API。请求体直接填写 JSON，对方接口要求的 Header 也可以在请求头里补上。',
  },
]
const taskTypeOptions = ref([...BASE_TASK_TYPE_OPTIONS])
const cfModeOptions = ref([
  { title: '智能兜底', value: 'auto' },
  { title: '仅请求', value: 'request' },
  { title: '仅 Playwright', value: 'playwright' },
  { title: '仅 FlareSolverr', value: 'flaresolverr' },
])

const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  cron: '0 9 * * *',
  max_workers: 2,
  random_delay_max_seconds: 5,
  http_timeout: 18,
  http_retry_times: 3,
  http_retry_delay: 1500,
  flaresolverr_url: '',
  tasks: [],
})

let themeObserver = null
let observedThemeNode = null

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function createTask(overrides = {}) {
  const taskType = overrides.task_type || 'generic_attendance'
  return {
    id: overrides.id || '',
    name: overrides.name || '',
    enabled: overrides.enabled ?? true,
    task_type: taskType,
    site_url: overrides.site_url || '',
    target_url: overrides.target_url || '',
    use_moviepilot_cookie: overrides.use_moviepilot_cookie ?? false,
    moviepilot_domain: overrides.moviepilot_domain || '',
    cookie: overrides.cookie || '',
    user_agent: overrides.user_agent || '',
    cf_mode: overrides.cf_mode || (REQUEST_TASK_TYPES.includes(taskType) ? 'request' : 'playwright'),
    success_keywords: overrides.success_keywords ?? DEFAULT_SUCCESS_KEYWORDS,
    failure_keywords: overrides.failure_keywords ?? DEFAULT_FAILURE_KEYWORDS,
    request_body: overrides.request_body || '',
    request_headers: overrides.request_headers || '',
    allow_logged_in_as_success: overrides.allow_logged_in_as_success ?? true,
    use_proxy: overrides.use_proxy ?? false,
    force_ipv4: overrides.force_ipv4 ?? true,
    new_api_uid: overrides.new_api_uid || '',
  }
}

function createBlankTask() {
  const nextIndex = taskSeed.value++
  return createTask({
    id: `task-${Date.now()}-${nextIndex}`,
    name: `新任务 ${nextIndex}`,
    task_type: 'generic_attendance',
    cf_mode: 'playwright',
  })
}

function mergeTaskTypeOptions(tasks, options) {
  const merged = [...options]
  for (const task of tasks || []) {
    if (merged.some((item) => item.value === task.task_type)) continue
    const legacyTitle = LEGACY_TASK_LABELS[task.task_type]
    if (legacyTitle) {
      merged.push({ title: legacyTitle, value: task.task_type })
    }
  }
  return merged
}

function resolveTaskTypeLabel(value) {
  return taskTypeOptions.value.find((item) => item.value === value)?.title || LEGACY_TASK_LABELS[value] || value
}

function resolveCfModeLabel(value) {
  return cfModeOptions.value.find((item) => item.value === value)?.title || value
}

function usesKeywordMatcher(type) {
  return KEYWORD_TASK_TYPES.includes(type)
}

function usesRequestPayload(type) {
  return REQUEST_TASK_TYPES.includes(type)
}

function handleTaskTypeChange(task) {
  if (REQUEST_TASK_TYPES.includes(task.task_type) && task.cf_mode === 'playwright') {
    task.cf_mode = 'request'
  } else if (!REQUEST_TASK_TYPES.includes(task.task_type) && task.cf_mode === 'request') {
    task.cf_mode = 'playwright'
  }
}

function taskTargetPlaceholder(type) {
  if (type === 'request_get') return 'https://example.com/api/checkin'
  if (type === 'request_post_form') return 'https://example.com/signin'
  if (type === 'request_post_json') return 'https://example.com/api/user/checkin'
  if (type === 'siqi_hnr_claim') return 'https://example.com/hnrview.php'
  if (type === 'new_api_checkin') return 'https://example.com/console/personal'
  return 'https://example.com/attendance.php'
}

function requestBodyLabel(type) {
  if (type === 'request_get') return 'GET 参数'
  if (type === 'request_post_json') return 'JSON 请求体'
  return '表单参数'
}

function requestBodyPlaceholder(type) {
  if (type === 'request_get') return '例如 action=checkin&page=1'
  if (type === 'request_post_json') return '{\n  "action": "checkin"\n}'
  return '例如 action=checkin&token=xxx'
}

function taskTypeDescription(type) {
  if (type === 'request_get') return '适合 AJAX / API 类型的 GET 签到接口，可填写请求参数和请求头。'
  if (type === 'request_post_form') return '适合 form-urlencoded 类型接口，常见于表单提交签到。'
  if (type === 'request_post_json') return '适合 JSON API，可直接填写 JSON 请求体和鉴权请求头。'
  if (type === 'siqi_attendance') return '旧专用模式。已不再提供新建入口，建议改成通用接口模式或浏览器模式。'
  if (type === 'siqi_hnr_claim') return '旧专用模式。已不再提供新建入口，建议改成通用接口模式或浏览器模式。'
  if (type === 'new_api_checkin') return '旧专用模式。已不再提供新建入口，建议改成 POST JSON 或其他通用接口模式。'
  return '适合浏览器打开页面即可自动完成签到或领取的站点，默认建议只用 Playwright。'
}

function findThemeNode() {
  let current = rootEl.value
  while (current) {
    if (current.getAttribute?.('data-theme')) {
      return current
    }
    current = current.parentElement
  }
  if (document.body?.getAttribute('data-theme')) return document.body
  if (document.documentElement?.getAttribute('data-theme')) return document.documentElement
  return null
}

function detectTheme() {
  const node = findThemeNode()
  const themeValue = node?.getAttribute?.('data-theme') || ''
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  isDarkTheme.value = ['dark', 'purple', 'transparent'].includes(themeValue) || (!themeValue && !!prefersDark)
}

function bindThemeObserver() {
  themeObserver?.disconnect()
  themeObserver = new MutationObserver(() => {
    const nextNode = findThemeNode()
    if (nextNode && nextNode !== observedThemeNode) {
      bindThemeObserver()
      return
    }
    detectTheme()
  })

  observedThemeNode = findThemeNode()
  if (observedThemeNode) {
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme'] })
  }
  themeObserver.observe(document.documentElement, { attributes: true, subtree: true, attributeFilter: ['data-theme'] })
  if (document.body) {
    themeObserver.observe(document.body, { attributes: true, subtree: true, attributeFilter: ['data-theme'] })
  }
}

function applyConfig(payload) {
  config.enabled = !!payload.enabled
  config.notify = !!payload.notify
  config.onlyonce = !!payload.onlyonce
  config.use_proxy = !!payload.use_proxy
  config.force_ipv4 = payload.force_ipv4 !== false
  config.cron = payload.cron || '0 9 * * *'
  config.max_workers = payload.max_workers ?? 2
  config.random_delay_max_seconds = payload.random_delay_max_seconds ?? 5
  config.http_timeout = payload.http_timeout ?? 18
  config.http_retry_times = payload.http_retry_times ?? 3
  config.http_retry_delay = payload.http_retry_delay ?? 1500
  config.flaresolverr_url = payload.flaresolverr_url || ''
  config.tasks = Array.isArray(payload.tasks) ? clone(payload.tasks) : []
  const baseOptions = Array.isArray(payload.task_type_options) && payload.task_type_options.length ? payload.task_type_options : BASE_TASK_TYPE_OPTIONS
  taskTypeOptions.value = mergeTaskTypeOptions(config.tasks, baseOptions)
  cfModeOptions.value = payload.cf_mode_options || cfModeOptions.value
}

async function loadConfig() {
  try {
    const payload = await props.api.get('/plugin/PrivateCheckin/config')
    applyConfig(payload || {})
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const payload = await props.api.post('/plugin/PrivateCheckin/config', clone(config))
    applyConfig(payload?.config || config)
    flash(payload?.message || '配置已保存')
  } catch (error) {
    flash(error?.message || '保存配置失败', 'error')
  } finally {
    saving.value = false
  }
}

function addTask() {
  config.tasks.push(createBlankTask())
}

function removeTask(index) {
  config.tasks.splice(index, 1)
}

onMounted(() => {
  loadConfig()
  detectTheme()
  bindThemeObserver()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect()
})
</script>

<style scoped>
.pc-config {
  color: #13251a;
  padding: clamp(16px, 2vw, 24px) clamp(18px, 4vw, 56px) 48px;
}

.pc-shell {
  width: min(1360px, 100%);
  margin: 0 auto;
  display: grid;
  gap: 28px;
}

.pc-hero,
.pc-panel {
  border: 1px solid rgba(21, 70, 52, 0.14);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(12px);
  box-shadow: 0 18px 50px rgba(18, 48, 39, 0.08);
}

.pc-hero {
  display: flex;
  justify-content: space-between;
  gap: 28px;
  padding: 32px;
}

.pc-hero-copy {
  max-width: 840px;
}

.pc-badge,
.pc-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(19, 89, 59, 0.1);
  color: #12573a;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.pc-title {
  margin: 14px 0 10px;
  font-size: clamp(30px, 4vw, 42px);
  line-height: 1.08;
}

.pc-subtitle {
  margin: 0;
  color: #506355;
  line-height: 1.8;
}

.pc-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-start;
}

.pc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 20px;
}

.pc-panel {
  padding: 28px;
}

.pc-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.pc-panel-head-wrap {
  flex-wrap: wrap;
}

.pc-panel-head h2 {
  margin: 10px 0 0;
  font-size: 24px;
}

.pc-switch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px 18px;
  margin-bottom: 20px;
}

.pc-switch-grid-tight {
  margin: 0 0 20px;
}

.pc-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.pc-form-grid-wide {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.pc-note-stack,
.pc-note-grid,
.pc-panels,
.pc-task-layout {
  display: grid;
  gap: 14px;
}

.pc-note-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.pc-note,
.pc-note-card,
.pc-task-group,
.pc-empty {
  border-radius: 18px;
  background: rgba(18, 87, 58, 0.06);
}

.pc-note {
  padding: 14px 16px;
  color: #4f6355;
  line-height: 1.7;
}

.pc-note-card {
  padding: 18px;
}

.pc-note-card strong {
  display: block;
  margin-bottom: 8px;
}

.pc-note-card p,
.pc-mini {
  margin: 0;
  color: #5d6d62;
  line-height: 1.7;
  font-size: 14px;
}

.pc-task-title {
  width: 100%;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.pc-title-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pc-task-group {
  padding: 20px;
}

.pc-group-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.pc-task-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-top: 6px;
}

.pc-empty {
  padding: 24px;
  color: #46614f;
}

.is-dark-theme .pc-config {
  color: #ecf4ee;
}

.is-dark-theme .pc-hero,
.is-dark-theme .pc-panel {
  background: rgba(18, 25, 22, 0.9);
  border-color: rgba(133, 190, 162, 0.16);
  box-shadow: 0 24px 56px rgba(0, 0, 0, 0.34);
}

.is-dark-theme .pc-subtitle,
.is-dark-theme .pc-note,
.is-dark-theme .pc-note-card p,
.is-dark-theme .pc-mini,
.is-dark-theme .pc-empty {
  color: #b8c9be;
}

.is-dark-theme .pc-badge,
.is-dark-theme .pc-kicker {
  background: rgba(74, 182, 120, 0.16);
  color: #98efb0;
}

.is-dark-theme .pc-note,
.is-dark-theme .pc-note-card,
.is-dark-theme .pc-task-group,
.is-dark-theme .pc-empty {
  background: rgba(90, 132, 110, 0.12);
}

@media (max-width: 980px) {
  .pc-config {
    padding: 16px 14px 36px;
  }

  .pc-hero,
  .pc-group-head,
  .pc-task-title,
  .pc-task-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
