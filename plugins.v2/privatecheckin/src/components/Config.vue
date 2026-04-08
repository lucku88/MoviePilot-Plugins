<template>
  <div ref="rootEl" class="pc-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="pc-shell">
      <section class="pc-hero">
        <div>
          <div class="pc-badge">自用签到</div>
          <h1 class="pc-title">配置页</h1>
          <p class="pc-subtitle">把签到页、Cookie、CF 策略和 New API / 思齐类特殊逻辑统一放在一个任务编排面板里。</p>
        </div>
        <div class="pc-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回数据页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="resetDefaults">恢复默认示例</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存配置</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">
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
            <v-text-field v-model="config.cron" label="执行周期" hint="5 位 Cron，例如 0 9 * * *" persistent-hint variant="outlined" density="comfortable" />
            <v-text-field v-model="config.max_workers" type="number" label="并发任务数" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.random_delay_max_seconds" type="number" label="随机延迟上限(秒)" variant="outlined" density="comfortable" />
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
          <div class="pc-note-list">
            <div class="pc-note">`自动` 会按 `请求 -> Playwright -> FlareSolverr` 顺序兜底。</div>
            <div class="pc-note">你提到的 `ourbits / hddolby / ubits / audiences` 已默认给成 `Playwright`，因为它们是浏览器打开签到页即可自动完成的模式。</div>
            <div class="pc-note">如果站点已经配置在 MoviePilot 站点管理里，可以打开“优先使用 MoviePilot Cookie”；否则直接把浏览器 Cookie 贴到任务里。</div>
          </div>
        </article>
      </section>

      <section class="pc-panel">
        <div class="pc-panel-head pc-panel-head-wrap">
          <div>
            <div class="pc-kicker">任务编排</div>
            <h2>签到/领取任务列表</h2>
          </div>
          <div class="pc-actions">
            <v-btn color="success" variant="flat" @click="addTask">新增空白任务</v-btn>
          </div>
        </div>

        <v-alert type="info" variant="tonal" class="mb-4">
          通用任务只需要填签到页地址；特殊任务里 `思齐签到 / 思齐 HNR 领取 / New API 签到` 会走内置逻辑。`New API` 还需要补一个 UID。
        </v-alert>

        <div v-if="!config.tasks.length" class="pc-empty">
          暂无任务，点击“新增空白任务”或“恢复默认示例”开始。
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
                    {{ task.enabled ? '启用' : '停用' }}
                  </v-chip>
                  <v-chip size="small" color="primary" variant="tonal">
                    {{ resolveCfModeLabel(task.cf_mode) }}
                  </v-chip>
                </div>
              </div>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <div class="pc-form-grid">
                <v-text-field v-model="task.name" label="任务名称" variant="outlined" density="comfortable" />
                <v-select
                  v-model="task.task_type"
                  :items="taskTypeOptions"
                  label="任务类型"
                  variant="outlined"
                  density="comfortable"
                />
                <v-text-field v-model="task.site_url" label="站点地址" placeholder="https://example.com" variant="outlined" density="comfortable" />
                <v-text-field v-model="task.target_url" label="签到/任务地址" placeholder="https://example.com/attendance.php" variant="outlined" density="comfortable" />
              </div>

              <div class="pc-switch-grid pc-switch-grid-tight">
                <v-switch v-model="task.enabled" label="启用任务" color="success" hide-details />
                <v-switch v-model="task.use_moviepilot_cookie" label="优先使用 MoviePilot Cookie" color="info" hide-details />
                <v-switch v-model="task.use_proxy" label="该任务使用代理" color="secondary" hide-details />
                <v-switch v-model="task.force_ipv4" label="该任务优先 IPv4" color="secondary" hide-details />
                <v-switch
                  v-if="task.task_type === 'generic_attendance'"
                  v-model="task.allow_logged_in_as_success"
                  label="浏览器访问成功即视为通过"
                  color="warning"
                  hide-details
                />
              </div>

              <div class="pc-form-grid">
                <v-text-field
                  v-model="task.moviepilot_domain"
                  label="MoviePilot 站点域名"
                  placeholder="ourbits.club"
                  hint="用于站点 Cookie 同步；不填会自动从地址里提取。"
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
                  label="New API UID"
                  placeholder="例如 225"
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
                class="mb-4"
              />

              <div v-if="task.task_type === 'generic_attendance'" class="pc-form-grid">
                <v-textarea
                  v-model="task.success_keywords"
                  label="成功关键字 / 正则"
                  rows="3"
                  auto-grow
                  variant="outlined"
                  density="comfortable"
                  placeholder="支持用 | 分隔多个关键字"
                />
                <v-textarea
                  v-model="task.failure_keywords"
                  label="失败关键字 / 正则"
                  rows="3"
                  auto-grow
                  variant="outlined"
                  density="comfortable"
                  placeholder="支持用 | 分隔多个关键字"
                />
              </div>

              <div class="pc-task-footer">
                <div class="pc-mini">
                  {{ taskTypeDescription(task.task_type) }}
                </div>
                <v-btn color="error" variant="tonal" @click="removeTask(index)">删除任务</v-btn>
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

const rootEl = ref(null)
const isDarkTheme = ref(false)
const saving = ref(false)
const taskSeed = ref(1)
const message = reactive({ text: '', type: 'success' })
const taskTypeOptions = ref([
  { title: '通用签到页', value: 'generic_attendance' },
  { title: '思齐签到', value: 'siqi_attendance' },
  { title: '思齐 HNR 领取', value: 'siqi_hnr_claim' },
  { title: 'New API 签到', value: 'new_api_checkin' },
])
const cfModeOptions = ref([
  { title: '自动', value: 'auto' },
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

function createDefaultTasks() {
  return [
    {
      id: 'ourbits-attendance',
      name: '我堡签到',
      enabled: true,
      task_type: 'generic_attendance',
      site_url: 'https://ourbits.club',
      target_url: 'https://ourbits.club/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'ourbits.club',
      cookie: '',
      user_agent: '',
      cf_mode: 'playwright',
      success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
      failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'hddolby-attendance',
      name: '杜比签到',
      enabled: true,
      task_type: 'generic_attendance',
      site_url: 'https://www.hddolby.com',
      target_url: 'https://www.hddolby.com/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'hddolby.com',
      cookie: '',
      user_agent: '',
      cf_mode: 'playwright',
      success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
      failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'ubits-attendance',
      name: 'UBits 签到',
      enabled: true,
      task_type: 'generic_attendance',
      site_url: 'https://ubits.club',
      target_url: 'https://ubits.club/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'ubits.club',
      cookie: '',
      user_agent: '',
      cf_mode: 'playwright',
      success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
      failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'audiences-attendance',
      name: '观众签到',
      enabled: true,
      task_type: 'generic_attendance',
      site_url: 'https://audiences.me',
      target_url: 'https://audiences.me/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'audiences.me',
      cookie: '',
      user_agent: '',
      cf_mode: 'playwright',
      success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
      failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'siqi-attendance',
      name: '思齐签到',
      enabled: true,
      task_type: 'siqi_attendance',
      site_url: 'https://si-qi.xyz',
      target_url: 'https://si-qi.xyz/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'si-qi.xyz',
      cookie: '',
      user_agent: '',
      cf_mode: 'request',
      success_keywords: '',
      failure_keywords: '',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'siqi-hnr',
      name: '思齐 HNR 领取',
      enabled: true,
      task_type: 'siqi_hnr_claim',
      site_url: 'https://si-qi.xyz',
      target_url: 'https://si-qi.xyz/hnrview.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'si-qi.xyz',
      cookie: '',
      user_agent: '',
      cf_mode: 'request',
      success_keywords: '',
      failure_keywords: '',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'new-api-checkin',
      name: 'New API 签到',
      enabled: true,
      task_type: 'new_api_checkin',
      site_url: 'https://open.xingyungept.cn',
      target_url: 'https://open.xingyungept.cn/console/personal',
      use_moviepilot_cookie: false,
      moviepilot_domain: 'open.xingyungept.cn',
      cookie: '',
      user_agent: '',
      cf_mode: 'request',
      success_keywords: '',
      failure_keywords: '',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
  ]
}

function createBlankTask() {
  const id = `task-${Date.now()}-${taskSeed.value++}`
  return {
    id,
    name: `新任务 ${taskSeed.value}`,
    enabled: true,
    task_type: 'generic_attendance',
    site_url: '',
    target_url: '',
    use_moviepilot_cookie: false,
    moviepilot_domain: '',
    cookie: '',
    user_agent: '',
    cf_mode: 'auto',
    success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
    failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
    allow_logged_in_as_success: true,
    use_proxy: false,
    force_ipv4: true,
    new_api_uid: '',
  }
}

function resolveTaskTypeLabel(value) {
  return taskTypeOptions.value.find((item) => item.value === value)?.title || value
}

function resolveCfModeLabel(value) {
  return cfModeOptions.value.find((item) => item.value === value)?.title || value
}

function taskTypeDescription(type) {
  if (type === 'siqi_attendance') return '内置思齐 attendance.php 验证码识别与提交逻辑。'
  if (type === 'siqi_hnr_claim') return '内置思齐 HNR 页面解析与奖励领取逻辑。'
  if (type === 'new_api_checkin') return '内置 New API /api/user/checkin 查询与签到逻辑，需要额外填写 UID。'
  return '适合 PT 站或其他站点的签到页场景；打开目标地址即可触发签到。'
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
  config.tasks = clone(payload.tasks || createDefaultTasks())
  taskTypeOptions.value = payload.task_type_options || taskTypeOptions.value
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

function resetDefaults() {
  config.tasks = createDefaultTasks()
  flash('已恢复默认示例任务，可继续按需修改', 'info')
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
}

.pc-shell {
  display: grid;
  gap: 20px;
}

.pc-hero,
.pc-panel {
  border: 1px solid rgba(21, 70, 52, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(12px);
  box-shadow: 0 18px 50px rgba(18, 48, 39, 0.08);
}

.pc-hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
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
  margin: 14px 0 8px;
  font-size: clamp(30px, 4vw, 42px);
  line-height: 1.08;
}

.pc-subtitle {
  max-width: 760px;
  margin: 0;
  color: #506355;
  line-height: 1.7;
}

.pc-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-start;
}

.pc-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.pc-panel {
  padding: 24px;
}

.pc-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.pc-panel-head-wrap {
  flex-wrap: wrap;
}

.pc-panel-head h2 {
  margin: 10px 0 0;
  font-size: 22px;
}

.pc-switch-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px 18px;
  margin-bottom: 18px;
}

.pc-switch-grid-tight {
  margin: 16px 0 18px;
}

.pc-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.pc-note-list {
  display: grid;
  gap: 8px;
}

.pc-note,
.pc-mini {
  color: #5d6d62;
  line-height: 1.7;
  font-size: 14px;
}

.pc-empty {
  padding: 24px;
  border-radius: 18px;
  background: rgba(18, 87, 58, 0.06);
  color: #46614f;
}

.pc-panels {
  display: grid;
  gap: 12px;
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

.pc-task-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-top: 8px;
}

.is-dark-theme .pc-hero,
.is-dark-theme .pc-panel {
  background: rgba(18, 25, 22, 0.9);
  border-color: rgba(133, 190, 162, 0.16);
  box-shadow: 0 24px 56px rgba(0, 0, 0, 0.34);
}

.is-dark-theme .pc-config {
  color: #ecf4ee;
}

.is-dark-theme .pc-subtitle,
.is-dark-theme .pc-note,
.is-dark-theme .pc-mini,
.is-dark-theme .pc-empty {
  color: #b8c9be;
}

.is-dark-theme .pc-badge,
.is-dark-theme .pc-kicker {
  background: rgba(74, 182, 120, 0.16);
  color: #98efb0;
}

@media (max-width: 980px) {
  .pc-grid,
  .pc-form-grid {
    grid-template-columns: 1fr;
  }

  .pc-switch-grid {
    grid-template-columns: 1fr 1fr;
  }

  .pc-hero,
  .pc-task-footer,
  .pc-task-title {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .pc-switch-grid {
    grid-template-columns: 1fr;
  }
}
</style>
