<template>
  <div ref="rootEl" class="pill-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="pill-shell">
      <section class="pill-hero">
        <div>
          <div class="pill-badge">SQ魔丸</div>
          <h1 class="pill-title">配置中心</h1>
          <p class="pill-subtitle">当前已接入自动搬砖、自动清沙滩、动态调度和站点 Cookie 同步。</p>
        </div>
        <div class="pill-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">
        {{ message.text }}
      </v-alert>

      <section class="pill-grid">
        <article class="pill-panel">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">基础开关</div>
              <h2>运行控制</h2>
            </div>
          </div>
          <div class="pill-switch-grid">
            <v-switch v-model="config.enabled" label="启用插件" color="success" hide-details />
            <v-switch v-model="config.notify" label="发送通知" color="primary" hide-details />
            <v-switch v-model="config.onlyonce" label="保存后执行一次" color="warning" hide-details />
            <v-switch v-model="config.auto_cookie" label="优先使用站点 Cookie" color="info" hide-details />
            <v-switch v-model="config.enable_brick" label="自动搬砖" color="deep-orange" hide-details />
            <v-switch v-model="config.enable_beach" label="自动清沙滩" color="teal" hide-details />
            <v-switch v-model="config.use_proxy" label="使用系统代理" color="info" hide-details />
            <v-switch v-model="config.force_ipv4" label="优先 IPv4" color="secondary" hide-details />
          </div>
        </article>

        <article class="pill-panel">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">调度策略</div>
              <h2>时间配置</h2>
            </div>
          </div>
          <v-menu v-model="cronMenu" :close-on-content-click="false" location="bottom start" max-width="440">
            <template #activator="{ props: menuProps }">
              <v-text-field
                v-bind="menuProps"
                v-model="config.brick_cron"
                label="执行周期(cron)"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                readonly
                append-inner-icon="mdi-clock-edit-outline"
                @click="openCronMenu"
              />
            </template>
            <div class="pill-cron-menu">
              <div class="pill-cron-group">
                <div class="pill-cron-label">周期</div>
                <div class="pill-cron-chip-row">
                  <button type="button" class="pill-cron-chip" :class="{ active: cronDraft.mode === 'daily' }" @click="cronDraft.mode = 'daily'">每日</button>
                  <button type="button" class="pill-cron-chip" :class="{ active: cronDraft.mode === 'weekdays' }" @click="cronDraft.mode = 'weekdays'">工作日</button>
                  <button type="button" class="pill-cron-chip" :class="{ active: cronDraft.mode === 'weekly' }" @click="cronDraft.mode = 'weekly'">每周</button>
                </div>
              </div>
              <div class="pill-cron-selects">
                <v-select v-model="cronDraft.hour" :items="hourItems" label="时" variant="outlined" density="comfortable" hide-details />
                <v-select v-model="cronDraft.minute" :items="minuteItems" label="分" variant="outlined" density="comfortable" hide-details />
                <v-select
                  v-if="cronDraft.mode === 'weekly'"
                  v-model="cronDraft.weekday"
                  :items="weekdayItems"
                  label="星期"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                />
              </div>
              <div class="pill-cron-preview">将生成：{{ cronPreview }}</div>
              <div class="pill-cron-actions">
                <v-btn variant="text" @click="cronMenu = false">取消</v-btn>
                <v-btn color="primary" variant="flat" @click="applyCronDraft">应用</v-btn>
              </div>
            </div>
          </v-menu>
          <v-text-field v-model="config.schedule_buffer_seconds" label="调度缓冲秒数" type="number" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="config.ready_retry_seconds" label="失败后快速重试秒数" type="number" variant="outlined" density="comfortable" class="mb-3" />
          <div class="pill-note">
            搬砖按你填写的 CRON 执行，默认是每天 00:05。沙滩仍按冷却时间动态调度；如果搬砖后检测到还没达到 50 次，会在 60 秒后自动重试。
          </div>
        </article>

        <article class="pill-panel">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">搬砖节奏</div>
              <h2>动作配置</h2>
            </div>
          </div>
          <v-text-field v-model="config.move_delay_min_ms" label="搬砖间隔最小毫秒" type="number" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="config.move_delay_max_ms" label="搬砖间隔最大毫秒" type="number" variant="outlined" density="comfortable" />
          <div class="pill-note">
            每天搬砖次数固定按 50 次处理，不再需要手动配置循环次数。
          </div>
        </article>

        <article class="pill-panel">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">网络设置</div>
              <h2>连接参数</h2>
            </div>
          </div>
          <v-text-field v-model="config.random_delay_max_seconds" label="随机延迟上限(秒)" type="number" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="config.http_timeout" label="HTTP 超时(秒)" type="number" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="config.http_retry_times" label="GET 重试次数" type="number" variant="outlined" density="comfortable" class="mb-3" />
          <v-text-field v-model="config.http_retry_delay" label="GET 重试间隔(ms)" type="number" variant="outlined" density="comfortable" />
        </article>

        <article class="pill-panel pill-panel-wide">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">手动 Cookie</div>
              <h2>兜底配置</h2>
            </div>
          </div>
          <v-textarea
            v-model="config.cookie"
            label="SQ Cookie"
            rows="6"
            variant="outlined"
            density="comfortable"
            placeholder="例如 c_secure_pass=..."
          />
          <div class="pill-note">
            默认站点固定为 <code>si-qi.xyz</code>。开启站点 Cookie 同步后，插件会优先读取 MoviePilot 站点管理里的 Cookie。
          </div>
        </article>

        <article class="pill-panel pill-panel-wide">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">当前说明</div>
              <h2>功能状态</h2>
            </div>
          </div>
          <div class="pill-note">
            当前版本已经支持自动搬砖、自动清沙滩、手动兑换魔力和炼造工坊交互。赠送按钮暂时不接入，物品栏只展示当前数量。
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])

const saving = ref(false)
const rootEl = ref(null)
const isDarkTheme = ref(false)
const pluginBase = '/plugin/SQPill'
const cronMenu = ref(false)
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_brick: true,
  enable_beach: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  move_delay_min_ms: 30,
  move_delay_max_ms: 80,
  ready_retry_seconds: 60,
})
const cronDraft = reactive({
  mode: 'daily',
  hour: '00',
  minute: '05',
  weekday: '1',
})
const hourItems = Array.from({ length: 24 }, (_, i) => ({ title: String(i).padStart(2, '0'), value: String(i).padStart(2, '0') }))
const minuteItems = Array.from({ length: 60 }, (_, i) => ({ title: String(i).padStart(2, '0'), value: String(i).padStart(2, '0') }))
const weekdayItems = [
  { title: '周一', value: '1' },
  { title: '周二', value: '2' },
  { title: '周三', value: '3' },
  { title: '周四', value: '4' },
  { title: '周五', value: '5' },
  { title: '周六', value: '6' },
  { title: '周日', value: '0' },
]

let themeObserver = null
let mediaQuery = null
let observedThemeNode = null

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function applyConfig(data = {}) {
  Object.assign(config, {
    ...config,
    ...data,
  })
  syncCronDraft(config.brick_cron)
}

function syncCronDraft(expr) {
  const raw = String(expr || '').trim()
  const parts = raw.split(/\s+/)
  if (parts.length !== 5) {
    return
  }
  cronDraft.minute = String(parts[0]).padStart(2, '0')
  cronDraft.hour = String(parts[1]).padStart(2, '0')
  if (parts[2] === '*' && parts[3] === '*' && parts[4] === '*') {
    cronDraft.mode = 'daily'
    cronDraft.weekday = '1'
    return
  }
  if (parts[2] === '*' && parts[3] === '*' && parts[4] === '1-5') {
    cronDraft.mode = 'weekdays'
    cronDraft.weekday = '1'
    return
  }
  if (parts[2] === '*' && parts[3] === '*' && weekdayItems.some((item) => item.value === parts[4])) {
    cronDraft.mode = 'weekly'
    cronDraft.weekday = parts[4]
  }
}

function buildCronPreview() {
  if (cronDraft.mode === 'weekdays') {
    return `${Number(cronDraft.minute)} ${Number(cronDraft.hour)} * * 1-5`
  }
  if (cronDraft.mode === 'weekly') {
    return `${Number(cronDraft.minute)} ${Number(cronDraft.hour)} * * ${cronDraft.weekday}`
  }
  return `${Number(cronDraft.minute)} ${Number(cronDraft.hour)} * * *`
}

const cronPreview = computed(() => buildCronPreview())

function openCronMenu() {
  syncCronDraft(config.brick_cron)
  cronMenu.value = true
}

function applyCronDraft() {
  config.brick_cron = cronPreview.value
  cronMenu.value = false
}

async function loadConfig() {
  const data = await props.api.get(`${pluginBase}/config`)
  applyConfig(data || {})
}

async function saveConfig() {
  saving.value = true
  try {
    const result = await props.api.post(`${pluginBase}/config`, { ...config })
    applyConfig(result?.config || {})
    flash(result?.message || '配置已保存')
  } catch (error) {
    flash(error?.message || '保存失败', 'error')
  } finally {
    saving.value = false
  }
}

async function syncCookie() {
  saving.value = true
  try {
    const result = await props.api.get(`${pluginBase}/cookie`)
    applyConfig(result?.config || {})
    flash(result?.message || 'Cookie 已同步')
  } catch (error) {
    flash(error?.message || '同步失败', 'error')
  } finally {
    saving.value = false
  }
}

function findThemeNode() {
  let current = rootEl.value
  while (current) {
    if (current.getAttribute?.('data-theme')) return current
    current = current.parentElement
  }
  if (document.body?.getAttribute('data-theme')) return document.body
  if (document.documentElement?.getAttribute('data-theme')) return document.documentElement
  return null
}

function detectTheme() {
  const themeNode = findThemeNode()
  const themeValue = themeNode?.getAttribute?.('data-theme') || ''
  const darkThemes = new Set(['dark', 'purple', 'transparent'])
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  isDarkTheme.value = darkThemes.has(themeValue) || (!themeValue && !!prefersDark)
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
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme', 'class'] })
  }
}

onMounted(async () => {
  detectTheme()
  bindThemeObserver()
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
  await loadConfig()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.pill-config {
  --pill-bg: linear-gradient(180deg, #f7f2e8 0%, #f0ece2 100%);
  --pill-card: rgba(255, 255, 255, 0.88);
  --pill-card-strong: #ffffff;
  --pill-text: #203135;
  --pill-muted: #60757c;
  --pill-border: rgba(60, 83, 84, 0.16);
  --pill-shadow: 0 16px 30px rgba(90, 78, 36, 0.08);
  --pill-accent: #ff8f3d;
  --pill-accent-soft: rgba(255, 143, 61, 0.14);
  min-height: 100%;
  padding: 20px 0 32px;
  background: var(--pill-bg);
  color: var(--pill-text);
  overflow-x: hidden;
}

.pill-config,
.pill-config * {
  box-sizing: border-box;
}

.pill-config.is-dark-theme {
  --pill-bg: linear-gradient(180deg, #151b1b 0%, #101515 100%);
  --pill-card: rgba(26, 34, 34, 0.92);
  --pill-card-strong: #1f2727;
  --pill-text: #f2f0e7;
  --pill-muted: #98aca8;
  --pill-border: rgba(166, 192, 183, 0.16);
  --pill-shadow: 0 20px 40px rgba(0, 0, 0, 0.28);
  --pill-accent: #ffb24c;
  --pill-accent-soft: rgba(255, 178, 76, 0.18);
}

.pill-shell {
  width: 100%;
  max-width: 1180px;
  min-width: 0;
  padding: 0 12px;
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.pill-hero,
.pill-panel {
  border-radius: 28px;
  padding: 24px;
  background: var(--pill-card);
  border: 1px solid var(--pill-border);
  box-shadow: var(--pill-shadow);
}

.pill-hero {
  display: grid;
  gap: 16px;
}

.pill-badge,
.pill-tip-item {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: var(--pill-accent-soft);
  color: var(--pill-accent);
}

.pill-title {
  margin: 10px 0 6px;
  font-size: clamp(28px, 4vw, 40px);
}

.pill-subtitle,
.pill-note {
  color: var(--pill-muted);
}

.pill-actions,
.pill-grid,
.pill-switch-grid,
.pill-tip-list {
  display: grid;
  gap: 12px;
}

.pill-actions {
  grid-template-columns: repeat(auto-fit, minmax(min(120px, 100%), 1fr));
}

.pill-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.pill-panel-wide {
  grid-column: 1 / -1;
}

.pill-panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.pill-panel-head h2 {
  margin: 6px 0 0;
  font-size: 28px;
}

.pill-panel-kicker {
  color: var(--pill-muted);
  font-size: 13px;
  font-weight: 700;
}

.pill-tip-list {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.pill-cron-menu {
  padding: 16px;
  border-radius: 20px;
  background: var(--pill-card-strong);
  border: 1px solid var(--pill-border);
  box-shadow: var(--pill-shadow);
  display: grid;
  gap: 14px;
}

.pill-cron-group {
  display: grid;
  gap: 10px;
}

.pill-cron-label,
.pill-cron-preview {
  font-size: 13px;
  color: var(--pill-muted);
}

.pill-cron-chip-row,
.pill-cron-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill-cron-chip {
  border: 1px solid var(--pill-border);
  border-radius: 999px;
  background: var(--pill-card);
  color: var(--pill-text);
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.pill-cron-chip.active {
  background: var(--pill-accent-soft);
  color: var(--pill-accent);
  border-color: rgba(255, 143, 61, 0.4);
}

.pill-cron-selects {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 10px;
}

@media (max-width: 880px) {
  .pill-grid {
    grid-template-columns: 1fr;
  }

  .pill-shell {
    padding: 0 8px;
  }

  .pill-hero,
  .pill-panel {
    padding: 18px;
    border-radius: 22px;
  }
}
</style>
