<template>
  <div ref="rootEl" class="siqi-farm-config" :class="{ 'is-dark': isDarkTheme }">
    <v-snackbar v-model="notice.show" :color="notice.type" location="top" timeout="3200">
      {{ notice.text }}
    </v-snackbar>

    <div class="siqi-config-shell">
      <header class="siqi-topbar">
        <div class="topbar-left">
          <div class="topbar-mark">⚙️</div>
          <div>
            <h1>Vue-农场配置</h1>
            <p>动态收菜、自动化策略与农场互动设置</p>
          </div>
        </div>
        <div class="topbar-actions">
          <v-btn color="success" variant="flat" :loading="saving" @click="saveConfig">保存配置</v-btn>
          <v-btn icon="mdi-view-dashboard-outline" variant="text" title="返回状态页" @click="emit('switch', 'page')" />
          <v-btn icon="mdi-close" variant="text" title="关闭" @click="emit('close')" />
        </div>
      </header>

      <section class="siqi-card config-hero">
        <div>
          <div class="eyebrow">动态调度说明</div>
          <h2>收菜时间不使用固定周期</h2>
          <p>插件会读取每块田的真实成熟时间，在成熟后再延迟 {{ config.schedule_buffer_seconds }} 秒执行。萝卜不会卡在正好 4 小时但还差 1 秒的情况。</p>
        </div>
        <div class="hero-chips">
          <span>优先种子 {{ config.prefer_seed || '未选择' }}</span>
          <span>偷菜 {{ config.auto_steal ? '已开启' : '已关闭' }}</span>
          <span>点赞 {{ config.auto_like ? '已开启' : '已关闭' }}</span>
        </div>
      </section>

      <section class="siqi-card">
        <div class="section-head">
          <div>
            <div class="eyebrow">自动化开关</div>
            <h2>基础功能</h2>
          </div>
        </div>
        <div class="switch-grid">
          <label class="switch-card" :class="{ active: config.enabled }">
            <div><span>🔌</span><strong>启用插件</strong><small>开启动态调度和页面操作</small></div>
            <v-switch v-model="config.enabled" color="success" hide-details density="compact" />
          </label>
          <label class="switch-card" :class="{ active: config.notify }">
            <div><span>🔔</span><strong>任务通知</strong><small>有实际操作或异常时发送</small></div>
            <v-switch v-model="config.notify" color="primary" hide-details density="compact" />
          </label>
          <label class="switch-card" :class="{ active: config.auto_cookie }">
            <div><span>🍪</span><strong>自动同步 Cookie</strong><small>优先读取 MoviePilot 站点 Cookie</small></div>
            <v-switch v-model="config.auto_cookie" color="primary" hide-details density="compact" />
          </label>
          <label class="switch-card" :class="{ active: config.enable_plant }">
            <div><span>🌱</span><strong>自动种植</strong><small>收菜后按优先种子补满空地</small></div>
            <v-switch v-model="config.enable_plant" color="green" hide-details density="compact" />
          </label>
          <label class="switch-card" :class="{ active: config.enable_sell }">
            <div><span>🧺</span><strong>自动出售</strong><small>自动出售背包中的作物</small></div>
            <v-switch v-model="config.enable_sell" color="orange" hide-details density="compact" />
          </label>
          <label class="switch-card" :class="{ active: config.enable_ocr_harvest }">
            <div><span>🔎</span><strong>OCR 批量收菜</strong><small>关闭时直接逐坑位快速收菜</small></div>
            <v-switch v-model="config.enable_ocr_harvest" color="orange" hide-details density="compact" />
          </label>
          <label class="switch-card" :class="{ active: config.auto_steal }">
            <div><span>🥷</span><strong>自动偷菜</strong><small>每个设置时段只执行一轮</small></div>
            <v-switch v-model="config.auto_steal" color="red" hide-details density="compact" />
          </label>
          <label class="switch-card" :class="{ active: config.auto_like }">
            <div><span>👍</span><strong>自动点赞</strong><small>每天随机批量点赞一轮</small></div>
            <v-switch v-model="config.auto_like" color="pink" hide-details density="compact" />
          </label>
        </div>
      </section>

      <section class="siqi-card">
        <div class="section-head">
          <div>
            <div class="eyebrow">种植与连接</div>
            <h2>常用设置</h2>
          </div>
          <v-btn color="primary" variant="tonal" :loading="syncingCookie" @click="syncCookie">同步站点 Cookie</v-btn>
        </div>
        <div class="field-grid three">
          <div class="field-card seed-field">
            <label>优先种植</label>
            <v-select v-model="config.prefer_seed" :items="seedOptions" variant="outlined" density="comfortable" hide-details="auto" />
            <small>只有已经解锁的种子才会真正种植。</small>
          </div>
          <div class="field-card">
            <label>成熟后缓冲秒数</label>
            <v-text-field v-model.number="config.schedule_buffer_seconds" type="number" min="1" max="120" variant="outlined" density="comfortable" hide-details="auto" suffix="秒" />
            <small>建议保留 5 秒，避免成熟临界时间。</small>
          </div>
          <div class="field-card">
            <label>执行前随机延迟</label>
            <v-text-field v-model.number="config.random_delay_max_seconds" type="number" min="0" max="60" variant="outlined" density="comfortable" hide-details="auto" suffix="秒" />
            <small>在 0 到设置值之间随机等待。</small>
          </div>
        </div>
        <div class="field-grid connection-grid">
          <div class="field-card wide">
            <label>站点 Cookie</label>
            <v-textarea v-model="config.cookie" :class="{ 'cookie-masked': !showCookie }" rows="2" auto-grow variant="outlined" density="comfortable" hide-details="auto" placeholder="开启自动同步后通常无需手动填写" />
            <div class="inline-actions">
              <v-btn size="small" variant="text" @click="showCookie = !showCookie">{{ showCookie ? '隐藏 Cookie' : '显示 Cookie' }}</v-btn>
              <span>{{ config.auto_cookie ? '已开启自动同步' : '当前使用手动 Cookie' }}</span>
            </div>
          </div>
          <div class="field-card">
            <label>OCR API 地址</label>
            <v-text-field v-model="config.ocr_api_url" variant="outlined" density="comfortable" hide-details="auto" placeholder="http://ip:8089/api/tr-run/" />
            <small>只有开启 OCR 批量收菜时才需要。</small>
          </div>
        </div>
      </section>

      <section class="siqi-card social-card">
        <div class="section-head">
          <div>
            <div class="eyebrow">农场互动</div>
            <h2>偷菜策略</h2>
          </div>
          <span class="section-note">本时段没找到目标，就等下一个时段，不会每 10 分钟重复刷历史。</span>
        </div>
        <div class="field-grid three">
          <div class="field-card">
            <label>只偷哪种作物</label>
            <v-select v-model="config.steal_crop" :items="stealCropOptions" variant="outlined" density="comfortable" hide-details="auto" />
          </div>
          <div class="field-card">
            <label>每轮访问人数</label>
            <v-text-field v-model.number="config.steal_visit_count" type="number" min="1" max="30" variant="outlined" density="comfortable" hide-details="auto" suffix="人" />
            <small>默认 5 人，重复抽到同一个人不会占名额。</small>
          </div>
          <div class="field-card">
            <label>时段检查间隔</label>
            <v-select v-model="config.social_cron" :items="socialIntervalOptions" item-title="title" item-value="value" variant="outlined" density="comfortable" hide-details="auto" />
            <small>只用于发现时段开始，不影响动态收菜。</small>
          </div>
        </div>

        <div class="window-head">
          <div>
            <strong>偷菜时间段</strong>
            <small>每个时间段每天最多自动执行一轮，支持跨午夜。</small>
          </div>
          <v-btn color="red" variant="tonal" size="small" :disabled="stealWindows.length >= 6" @click="addStealWindow">添加时间段</v-btn>
        </div>
        <div class="window-list">
          <div v-for="(window, index) in stealWindows" :key="window.id" class="window-row">
            <span>时段 {{ index + 1 }}</span>
            <v-text-field v-model="window.start" type="time" label="开始" variant="outlined" density="compact" hide-details />
            <span class="window-separator">至</span>
            <v-text-field v-model="window.end" type="time" label="结束" variant="outlined" density="compact" hide-details />
            <v-btn icon="mdi-delete-outline" color="red" variant="text" :disabled="stealWindows.length <= 1" @click="removeStealWindow(index)" />
          </div>
        </div>
      </section>

      <section class="siqi-card advanced-card">
        <v-expansion-panels variant="accordion">
          <v-expansion-panel>
            <v-expansion-panel-title>高级设置</v-expansion-panel-title>
            <v-expansion-panel-text>
              <div class="switch-grid compact">
                <label class="switch-card" :class="{ active: config.use_proxy }">
                  <div><span>🌐</span><strong>使用系统代理</strong><small>通过 MoviePilot 代理访问站点</small></div>
                  <v-switch v-model="config.use_proxy" color="primary" hide-details density="compact" />
                </label>
                <label class="switch-card" :class="{ active: config.force_ipv4 }">
                  <div><span>4️⃣</span><strong>强制 IPv4</strong><small>避免部分环境 IPv6 连接异常</small></div>
                  <v-switch v-model="config.force_ipv4" color="primary" hide-details density="compact" />
                </label>
                <label class="switch-card" :class="{ active: config.onlyonce }">
                  <div><span>▶️</span><strong>保存后执行一次</strong><small>用于临时手动触发</small></div>
                  <v-switch v-model="config.onlyonce" color="primary" hide-details density="compact" />
                </label>
              </div>
              <div class="field-grid four advanced-fields">
                <div class="field-card"><label>请求超时</label><v-text-field v-model.number="config.http_timeout" type="number" min="3" max="60" suffix="秒" variant="outlined" density="compact" hide-details /></div>
                <div class="field-card"><label>网络重试次数</label><v-text-field v-model.number="config.http_retry_times" type="number" min="1" max="5" variant="outlined" density="compact" hide-details /></div>
                <div class="field-card"><label>重试间隔</label><v-text-field v-model.number="config.http_retry_delay" type="number" min="200" max="10000" suffix="毫秒" variant="outlined" density="compact" hide-details /></div>
                <div class="field-card"><label>OCR 尝试次数</label><v-text-field v-model.number="config.ocr_retry_times" type="number" min="1" max="3" variant="outlined" density="compact" hide-details /></div>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </section>

      <div class="save-bar">
        <span>保存后会立即刷新农场状态；如果已经成熟或错过执行时间，会自动补跑。</span>
        <v-btn color="success" size="large" variant="flat" :loading="saving" @click="saveConfig">保存配置</v-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({ api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } })
const emit = defineEmits(['switch', 'close'])

const rootEl = ref(null)
const isDarkTheme = ref(false)
const saving = ref(false)
const syncingCookie = ref(false)
const showCookie = ref(false)
const notice = reactive({ show: false, text: '', type: 'success' })
const seedOptions = ref(['西红柿'])
const windowId = ref(0)
const stealWindows = ref([])

let themeObserver = null
let mediaQuery = null

const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_sell: true,
  enable_plant: true,
  enable_ocr_harvest: false,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  ocr_api_url: 'http://ip:8089/api/tr-run/',
  prefer_seed: '西红柿',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
  ocr_retry_times: 2,
  auto_steal: false,
  auto_like: false,
  steal_crop: '全部作物',
  steal_visit_count: 5,
  steal_time_windows: '07:00-09:00,12:00-14:00,18:00-23:00',
  social_cron: '*/5 * * * *',
  ...props.initialConfig,
})

const socialIntervalOptions = [
  { title: '每 5 分钟检查时段', value: '*/5 * * * *' },
  { title: '每 10 分钟检查时段', value: '*/10 * * * *' },
  { title: '每 15 分钟检查时段', value: '*/15 * * * *' },
  { title: '每 30 分钟检查时段', value: '*/30 * * * *' },
]

const stealCropOptions = computed(() => ['全部作物', ...seedOptions.value.filter((name) => name !== '全部作物')])

function flash(text, type = 'success') {
  notice.text = text
  notice.type = type
  notice.show = true
}

function normalizeSeedOptions(values) {
  const result = [...new Set((values || []).map((item) => String(item || '').trim()).filter(Boolean))]
  if (config.prefer_seed && !result.includes(config.prefer_seed)) result.unshift(config.prefer_seed)
  seedOptions.value = result.length ? result : ['西红柿', '萝卜', '玉米', '茄子', '蘑菇', '樱桃']
}

function createWindow(start = '07:00', end = '09:00') {
  windowId.value += 1
  return { id: windowId.value, start, end }
}

function parseStealWindows(value) {
  const parsed = String(value || '')
    .split(/[,，;；\n]+/)
    .map((item) => item.trim().match(/^(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$/))
    .filter(Boolean)
    .map((match) => createWindow(match[1].padStart(5, '0'), match[2].padStart(5, '0')))
  stealWindows.value = parsed.length ? parsed : [createWindow('07:00', '09:00')]
}

function serializeStealWindows() {
  return stealWindows.value
    .filter((item) => item.start && item.end)
    .map((item) => `${item.start}-${item.end}`)
    .join(',')
}

function addStealWindow() {
  if (stealWindows.value.length < 6) stealWindows.value.push(createWindow('18:00', '23:00'))
}

function removeStealWindow(index) {
  if (stealWindows.value.length > 1) stealWindows.value.splice(index, 1)
}

function applyConfig(data) {
  const incoming = data?.config || data || {}
  Object.assign(config, incoming)
  normalizeSeedOptions(incoming.seed_options || data?.seed_options)
  parseStealWindows(config.steal_time_windows)
}

function clampNumber(value, min, max, fallback) {
  const number = Number(value)
  if (!Number.isFinite(number)) return fallback
  return Math.min(max, Math.max(min, Math.round(number)))
}

async function loadConfig() {
  try {
    applyConfig(await props.api.get('/plugin/VueFarm/config'))
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const payload = {
      ...config,
      steal_time_windows: serializeStealWindows(),
      schedule_buffer_seconds: clampNumber(config.schedule_buffer_seconds, 1, 120, 5),
      random_delay_max_seconds: clampNumber(config.random_delay_max_seconds, 0, 60, 5),
      steal_visit_count: clampNumber(config.steal_visit_count, 1, 30, 5),
      http_timeout: clampNumber(config.http_timeout, 3, 60, 12),
      http_retry_times: clampNumber(config.http_retry_times, 1, 5, 5),
      http_retry_delay: clampNumber(config.http_retry_delay, 200, 10000, 1500),
      ocr_retry_times: clampNumber(config.ocr_retry_times, 1, 3, 2),
    }
    const res = await props.api.post('/plugin/VueFarm/config', payload)
    applyConfig(res)
    flash(res.message || '配置已保存', res.success === false ? 'error' : 'success')
  } catch (error) {
    flash(error?.message || '保存配置失败', 'error')
  } finally {
    saving.value = false
  }
}

async function syncCookie() {
  syncingCookie.value = true
  try {
    const res = await props.api.get('/plugin/VueFarm/cookie')
    applyConfig(res)
    flash(res.message || 'Cookie 已同步', res.success === false ? 'error' : 'success')
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error')
  } finally {
    syncingCookie.value = false
  }
}

function detectTheme() {
  const themeNode = rootEl.value?.closest?.('.v-theme--dark, .v-theme--light')
  if (themeNode?.classList?.contains('v-theme--dark')) {
    isDarkTheme.value = true
    return
  }
  if (themeNode?.classList?.contains('v-theme--light')) {
    isDarkTheme.value = false
    return
  }
  const root = document.documentElement
  const body = document.body
  const text = `${root?.getAttribute('data-theme') || ''} ${root?.className || ''} ${body?.getAttribute('data-theme') || ''} ${body?.className || ''}`.toLowerCase()
  if (text.includes('dark')) isDarkTheme.value = true
  else if (text.includes('light')) isDarkTheme.value = false
  else isDarkTheme.value = Boolean(mediaQuery?.matches)
}

onMounted(async () => {
  mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)') || null
  mediaQuery?.addEventListener?.('change', detectTheme)
  themeObserver = new MutationObserver(detectTheme)
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] })
  if (document.body) themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class', 'data-theme'] })
  detectTheme()
  parseStealWindows(config.steal_time_windows)
  await loadConfig()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect()
  mediaQuery?.removeEventListener?.('change', detectTheme)
})
</script>

<style scoped>
.siqi-farm-config{--panel:#fff;--panel-2:#f8faf9;--text:#1f2d25;--muted:#6f7d75;--line:#dfe7e2;--green:#22a35a;--green-soft:#e8f7ee;--shadow:0 8px 24px rgba(32,72,48,.07);min-height:100%;padding:12px 0 28px;color:var(--text);background:transparent}.siqi-farm-config.is-dark{--panel:#1d2420;--panel-2:#242d28;--text:#eef7f1;--muted:#a4b3aa;--line:#344039;--green:#4ade80;--green-soft:rgba(74,222,128,.12);--shadow:0 10px 30px rgba(0,0,0,.25)}.siqi-farm-config,.siqi-farm-config *{box-sizing:border-box}.siqi-config-shell{max-width:1120px;margin:0 auto;padding:0 14px;display:grid;gap:14px}.siqi-topbar,.section-head,.config-hero,.window-head,.window-row,.save-bar{display:flex;align-items:center}.siqi-topbar{justify-content:space-between;gap:16px;padding:8px 4px 12px;border-bottom:1px solid var(--line)}.topbar-left{display:flex;align-items:center;gap:12px}.topbar-mark{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;background:var(--green-soft);font-size:22px}.topbar-left h1{margin:0;font-size:21px;font-weight:900}.topbar-left p{margin:2px 0 0;color:var(--muted);font-size:12px}.topbar-actions{display:flex;align-items:center;gap:5px}.siqi-card{padding:16px;border:1px solid var(--line);border-radius:12px;background:var(--panel);box-shadow:var(--shadow)}.config-hero{justify-content:space-between;gap:18px;border-left:4px solid var(--green)}.config-hero h2,.section-head h2{margin:0;font-size:18px;font-weight:900}.config-hero p{max-width:700px;margin:7px 0 0;color:var(--muted);font-size:12px;line-height:1.65}.eyebrow{margin-bottom:5px;color:var(--green);font-size:11px;font-weight:900;letter-spacing:.12em;text-transform:uppercase}.hero-chips{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:7px}.hero-chips span{padding:6px 9px;border:1px solid var(--line);border-radius:999px;background:var(--panel-2);font-size:11px;font-weight:700}.section-head{justify-content:space-between;gap:12px;margin-bottom:14px}.section-note{max-width:560px;color:var(--muted);font-size:11px;line-height:1.5;text-align:right}.switch-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.switch-grid.compact{grid-template-columns:repeat(3,minmax(0,1fr))}.switch-card{display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:88px;padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2);cursor:pointer}.switch-card.active{border-color:rgba(34,163,90,.45);background:var(--green-soft)}.switch-card>div{display:grid;grid-template-columns:24px minmax(0,1fr);gap:2px 6px;min-width:0}.switch-card>div>span{grid-row:1/3;font-size:17px}.switch-card strong{font-size:12px}.switch-card small{color:var(--muted);font-size:10px;line-height:1.35}.field-grid{display:grid;gap:11px}.field-grid.three{grid-template-columns:repeat(3,minmax(0,1fr))}.field-grid.four{grid-template-columns:repeat(4,minmax(0,1fr))}.connection-grid{grid-template-columns:2fr 1fr;margin-top:11px}.field-card{padding:12px;border:1px solid var(--line);border-radius:10px;background:var(--panel-2)}.field-card label{display:block;margin-bottom:8px;font-size:12px;font-weight:800}.field-card small{display:block;margin-top:7px;color:var(--muted);font-size:10px;line-height:1.45}.inline-actions{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:5px;color:var(--muted);font-size:10px}.social-card{border-left:4px solid #ef4444}.window-head{justify-content:space-between;gap:12px;margin:16px 0 10px}.window-head>div{display:grid;gap:2px}.window-head strong{font-size:13px}.window-head small{color:var(--muted);font-size:10px}.window-list{display:grid;gap:8px}.window-row{display:grid;grid-template-columns:70px minmax(130px,1fr) 24px minmax(130px,1fr) 38px;gap:8px;padding:10px;border:1px solid var(--line);border-radius:9px;background:var(--panel-2)}.window-row>span:first-child{font-size:11px;font-weight:800}.window-separator{color:var(--muted);font-size:11px;text-align:center}.advanced-card{padding:0;overflow:hidden}.advanced-card :deep(.v-expansion-panel){background:var(--panel)!important;color:var(--text)!important}.advanced-card :deep(.v-expansion-panel-title){font-weight:800}.advanced-fields{margin-top:12px}.save-bar{position:sticky;bottom:10px;z-index:4;justify-content:space-between;gap:14px;padding:12px 14px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--panel) 92%,transparent);box-shadow:0 12px 34px rgba(19,48,31,.15);backdrop-filter:blur(14px)}.save-bar span{color:var(--muted);font-size:11px}.siqi-farm-config :deep(.v-field){border-radius:8px}.siqi-farm-config :deep(.v-btn){border-radius:7px;font-weight:800}
@media(max-width:980px){.switch-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.field-grid.three,.field-grid.four,.connection-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.connection-grid .wide{grid-column:1/-1}.section-note{text-align:left}}
@media(max-width:680px){.siqi-config-shell{padding:0 9px}.siqi-topbar,.config-hero,.section-head,.save-bar{align-items:flex-start;flex-direction:column}.topbar-actions{width:100%;justify-content:flex-end}.config-hero{align-items:flex-start}.hero-chips{justify-content:flex-start}.switch-grid,.switch-grid.compact,.field-grid.three,.field-grid.four,.connection-grid{grid-template-columns:1fr}.window-row{grid-template-columns:58px 1fr 20px 1fr 34px}.save-bar{bottom:6px}.save-bar :deep(.v-btn){width:100%}.section-note{text-align:left}.topbar-left p{display:none}}
@media(max-width:480px){.window-row{grid-template-columns:1fr 32px}.window-row>span:first-child{grid-column:1/-1}.window-row :deep(.v-input){grid-column:1/-1}.window-separator{display:none}.window-row :deep(.v-btn){grid-column:2;grid-row:1}}
.siqi-farm-config{width:100%;max-width:100%;overflow-x:hidden}.siqi-config-shell{width:100%;min-width:0}.siqi-card,.switch-card,.field-card,.window-row{min-width:0;max-width:100%}
.cookie-masked :deep(textarea){-webkit-text-security:disc}
@media(max-width:680px){.siqi-topbar,.config-hero,.section-head,.save-bar,.topbar-actions{width:100%}.topbar-actions{justify-content:flex-start;flex-wrap:wrap}.window-row{grid-template-columns:58px minmax(0,1fr) 20px minmax(0,1fr) 34px}.siqi-farm-config :deep(.v-input),.siqi-farm-config :deep(.v-field){min-width:0;max-width:100%}}
</style>
