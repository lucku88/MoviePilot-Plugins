<template>
  <div ref="rootEl" class="toy-config" :class="{ 'is-dark-theme': isDarkTheme }">
    <div class="toy-shell">
      <section class="toy-hero">
        <div>
          <div class="toy-badge">SQ玩偶</div>
          <h1 class="toy-title">配置中心</h1>
          <p class="toy-subtitle">自动回收、自展位放置、外展抢位和站点 Cookie 同步都可以在这里调整。</p>
        </div>
        <div class="toy-actions">
          <v-btn variant="text" @click="emit('switch', 'page')">返回状态页</v-btn>
          <v-btn color="warning" variant="flat" :loading="saving" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="saveConfig">保存</v-btn>
          <v-btn variant="text" @click="emit('close')">关闭</v-btn>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">
        {{ message.text }}
      </v-alert>

      <section class="toy-grid">
        <article class="toy-panel">
          <div class="toy-panel-head">
            <div>
              <div class="toy-panel-kicker">基础开关</div>
              <h2>运行控制</h2>
            </div>
          </div>
          <div class="toy-switch-grid">
            <v-switch v-model="config.enabled" label="启用插件" color="success" hide-details />
            <v-switch v-model="config.notify" label="发送通知" color="primary" hide-details />
            <v-switch v-model="config.onlyonce" label="保存后执行一次" color="warning" hide-details />
            <v-switch v-model="config.auto_cookie" label="优先使用站点 Cookie" color="info" hide-details />
            <v-switch v-model="config.enable_target" label="允许外展抢位" color="deep-orange" hide-details />
            <v-switch v-model="config.use_proxy" label="使用系统代理" color="secondary" hide-details />
            <v-switch v-model="config.force_ipv4" label="优先 IPv4" color="secondary" hide-details />
          </div>
        </article>

        <article class="toy-panel">
          <div class="toy-panel-head">
            <div>
              <div class="toy-panel-kicker">调度策略</div>
              <h2>动态调度</h2>
            </div>
          </div>
          <div class="toy-form-grid">
            <v-text-field v-model="config.schedule_buffer_seconds" label="调度缓冲秒数" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.skip_before_seconds" label="提前跳过阈值(秒)" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.self_wait_window_seconds" label="自展位等待窗口(秒)" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.remote_wait_window_seconds" label="外展等待窗口(秒)" type="number" variant="outlined" density="comfortable" />
          </div>
          <div class="toy-note">插件不走固定 CRON，而是根据最近可回收时间动态注册下一次运行。未识别到时间时，会在启用或刷新后先拉一次页面状态。</div>
        </article>

        <article class="toy-panel">
          <div class="toy-panel-head">
            <div>
              <div class="toy-panel-kicker">回收与展出</div>
              <h2>动作参数</h2>
            </div>
          </div>
          <div class="toy-form-grid">
            <v-text-field v-model="config.collect_retry" label="回收重试次数" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.collect_retry_delay" label="回收重试间隔(ms)" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.place_loop_limit" label="单轮放置循环上限" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.place_retry_delay" label="放置循环间隔(ms)" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.max_target_try" label="随机目标尝试次数" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.max_target_place" label="单目标最多放置数" type="number" variant="outlined" density="comfortable" />
          </div>
        </article>

        <article class="toy-panel">
          <div class="toy-panel-head">
            <div>
              <div class="toy-panel-kicker">网络参数</div>
              <h2>连接设置</h2>
            </div>
          </div>
          <div class="toy-form-grid">
            <v-text-field v-model="config.random_delay_max_seconds" label="随机延迟上限(秒)" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.http_timeout" label="HTTP 超时(秒)" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.http_retry_times" label="GET 重试次数" type="number" variant="outlined" density="comfortable" />
            <v-text-field v-model="config.http_retry_delay" label="GET 重试间隔(ms)" type="number" variant="outlined" density="comfortable" />
          </div>
        </article>

        <article class="toy-panel">
          <div class="toy-panel-head">
            <div>
              <div class="toy-panel-kicker">手动 Cookie</div>
              <h2>Cookie 兜底</h2>
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
          <div class="toy-note">默认站点固定为 <code>si-qi.xyz</code>。如果开启“优先使用站点 Cookie”，插件会优先读取 MoviePilot 站点管理中的 Cookie。</div>
        </article>

        <article class="toy-panel">
          <div class="toy-panel-head">
            <div>
              <div class="toy-panel-kicker">当前说明</div>
              <h2>功能状态</h2>
            </div>
          </div>
          <div class="toy-note">
            当前版本已支持：状态展示、自动回收、自展位放置、随机外展、目标展台查看、手动收回和手动上架。<br />
            还缺少抓包的动作：盲盒购买、盲盒开启、按用户名搜索目标展台。
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

const pluginBase = '/plugin/SQToy'
const saving = ref(false)
const rootEl = ref(null)
const isDarkTheme = ref(false)
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_target: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  skip_before_seconds: 60,
  collect_retry: 3,
  collect_retry_delay: 1200,
  place_loop_limit: 10,
  place_retry_delay: 1500,
  self_wait_window_seconds: 60,
  remote_wait_window_seconds: 60,
  max_target_try: 3,
  max_target_place: 3,
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
  if (darkThemes.has(themeValue)) {
    isDarkTheme.value = true
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches
}

function bindTheme() {
  detectTheme()
  observedThemeNode = findThemeNode()
  if (observedThemeNode && window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme)
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme'] })
  }
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener?.('change', detectTheme)
  }
}

onMounted(async () => {
  bindTheme()
  await loadConfig()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect?.()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.toy-config { min-height: 100vh; background: linear-gradient(180deg, #fff8f1 0%, #f7efe8 100%); color: #402616; }
.toy-config.is-dark-theme { background: linear-gradient(180deg, #141313 0%, #1b1716 100%); color: #f7ebdf; }
.toy-shell { max-width: 1200px; margin: 0 auto; padding: 20px 16px 40px; display: grid; gap: 18px; }
.toy-hero, .toy-panel { border: 1px solid rgba(255, 165, 93, 0.28); border-radius: 24px; background: rgba(255,255,255,0.82); box-shadow: 0 18px 48px rgba(255, 166, 102, 0.08); }
.is-dark-theme .toy-hero, .is-dark-theme .toy-panel { background: rgba(27, 24, 22, 0.88); box-shadow: none; border-color: rgba(255, 171, 111, 0.16); }
.toy-hero, .toy-panel { padding: 22px; }
.toy-hero { display: grid; grid-template-columns: 1.4fr auto; gap: 20px; align-items: center; }
.toy-badge { display: inline-flex; padding: 6px 12px; border-radius: 999px; background: rgba(255, 155, 72, 0.18); color: #d96a21; font-size: 13px; font-weight: 700; }
.toy-title { margin: 12px 0 8px; font-size: 40px; line-height: 1.05; }
.toy-subtitle { margin: 0; font-size: 15px; opacity: 0.86; }
.toy-actions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end; }
.toy-grid { display: grid; gap: 18px; }
.toy-panel-head { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 18px; }
.toy-panel-head h2 { margin: 8px 0 0; font-size: 30px; }
.toy-panel-kicker { font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.72; }
.toy-switch-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 18px; }
.toy-form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.toy-note { font-size: 14px; line-height: 1.8; opacity: 0.82; }

@media (max-width: 900px) {
  .toy-hero { grid-template-columns: 1fr; }
  .toy-actions { justify-content: flex-start; }
  .toy-switch-grid, .toy-form-grid { grid-template-columns: 1fr; }
}
</style>
