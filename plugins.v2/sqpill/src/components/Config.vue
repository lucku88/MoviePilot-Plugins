<template>
  <div ref="rootEl" class="pill-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="pill-shell">
      <section class="pill-hero">
        <div>
          <div class="pill-badge">SQ魔丸</div>
          <h1 class="pill-title">配置中心</h1>
          <p class="pill-subtitle">
            搬砖按 CRON 运行，沙滩按冷却时间动态调度。自动炼造和自动兑换会在清沙滩后按当前配置执行。
          </p>
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
            <v-switch v-model="config.auto_craft" label="自动炼造魔丸" color="deep-purple" hide-details />
            <v-switch v-model="config.auto_exchange" label="自动兑换魔力" color="amber" hide-details />
            <v-switch v-model="config.use_proxy" label="使用系统代理" color="info" hide-details />
            <v-switch v-model="config.force_ipv4" label="优先 IPv4" color="secondary" hide-details />
          </div>
        </article>

        <article class="pill-panel pill-panel-wide">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">调度策略</div>
              <h2>时间配置</h2>
            </div>
          </div>
          <VCronField
            v-model="config.brick_cron"
            label="执行周期(cron)"
            hint="例如：5 0 * * * 表示每天 00:05 执行搬砖"
            persistent-hint
            density="compact"
            class="pill-cron-field"
          />
          <div class="pill-form-grid pill-form-grid-2">
            <v-text-field v-model="config.schedule_buffer_seconds" label="调度缓冲秒数" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.ready_retry_seconds" label="快速重试秒数" type="number" variant="outlined" density="comfortable" />
          </div>
          <div class="pill-note">
            搬砖严格按上面的 CRON 运行，默认每天 00:05。沙滩不走 CRON，而是按页面返回的冷却时间自动调度。
          </div>
        </article>

        <article class="pill-panel">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">自动处理</div>
              <h2>炼造与兑换</h2>
            </div>
          </div>
          <div class="pill-form-grid">
            <v-text-field
              v-model="config.reserve_material_count"
              label="自动时每种材料保留数量"
              type="number"
              variant="outlined"
              density="comfortable"
            />
            <v-text-field
              v-model="config.reserve_magic_pill_count"
              label="自动时保留魔丸数量"
              type="number"
              variant="outlined"
              density="comfortable"
            />
          </div>
          <div class="pill-note">
            开启自动炼造或自动兑换后，插件会在清沙滩成功后按当前库存执行，不额外创建新的运行周期。
          </div>
        </article>

        <article class="pill-panel">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">搬砖节奏</div>
              <h2>动作配置</h2>
            </div>
          </div>
          <div class="pill-form-grid">
            <v-text-field v-model="config.move_delay_min_ms" label="搬砖间隔最小毫秒" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.move_delay_max_ms" label="搬砖间隔最大毫秒" type="number" variant="outlined" density="comfortable" />
          </div>
          <div class="pill-note">
            每天搬砖次数固定按 50 次处理；若本轮搬完后页面仍显示未达上限，会在 60 秒后自动重试。
          </div>
        </article>

        <article class="pill-panel">
          <div class="pill-panel-head">
            <div>
              <div class="pill-panel-kicker">网络设置</div>
              <h2>连接参数</h2>
            </div>
          </div>
          <div class="pill-form-grid">
            <v-text-field v-model="config.random_delay_max_seconds" label="随机延迟上限(秒)" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.http_timeout" label="HTTP 超时(秒)" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.http_retry_times" label="GET 重试次数" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.http_retry_delay" label="GET 重试间隔(ms)" type="number" variant="outlined" density="comfortable" />
          </div>
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
            当前版本支持自动搬砖、自动清沙滩、手动兑换魔力、一键炼造魔丸，以及清沙滩后自动炼造与自动兑换。物品栏只用于展示当前数量。
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
  auto_craft: false,
  auto_exchange: false,
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
  reserve_material_count: 0,
  reserve_magic_pill_count: 0,
})

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
  max-width: 1080px;
  min-width: 0;
  padding: 0 12px;
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.pill-hero,
.pill-panel {
  border-radius: 28px;
  padding: 22px;
  background: var(--pill-card);
  border: 1px solid var(--pill-border);
  box-shadow: var(--pill-shadow);
}

.pill-hero {
  display: grid;
  gap: 16px;
}

.pill-badge {
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
.pill-form-grid {
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
  font-size: 26px;
}

.pill-panel-kicker {
  color: var(--pill-muted);
  font-size: 13px;
  font-weight: 700;
}

.pill-switch-grid {
  grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr));
}

.pill-form-grid {
  grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr));
}

.pill-form-grid-2 {
  margin-top: 14px;
}

.pill-cron-field {
  width: 100%;
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

  .pill-panel-head {
    flex-direction: column;
  }
}
</style>
