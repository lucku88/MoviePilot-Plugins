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
          <v-text-field
            v-model="config.brick_cron"
            label="搬砖执行周期 (CRON)"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            placeholder="例如 5 0 * * *"
          />
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
              <div class="pill-panel-kicker">后续需要</div>
              <h2>待补抓包</h2>
            </div>
          </div>
          <div class="pill-tip-list">
            <div v-for="tip in captureTips" :key="tip" class="pill-tip-item">{{ tip }}</div>
          </div>
          <div class="pill-note">
            当前版本已经支持自动搬砖、自动清沙滩和手动兑换魔力。后面只需要补上炼造 craft(id) 的抓包，我就能继续把炼造工坊交互接进去。
          </div>
        </article>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])

const saving = ref(false)
const rootEl = ref(null)
const isDarkTheme = ref(false)
const pluginBase = '/plugin/SQPill'
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
const captureTips = ref([
  '炼造 craft(id) 接口抓包',
])

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
  captureTips.value = data.capture_tips || captureTips.value
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
