<template>
  <div class="siqi-config">
    <div class="siqi-topbar">
      <div class="siqi-topbar__left">
        <div class="siqi-topbar__icon">
          <v-icon icon="mdi-cog-outline" size="24" />
        </div>
        <div class="siqi-topbar__copy">
          <div class="siqi-topbar__title">Vue-魔丸 · 配置</div>
          <div class="siqi-topbar__sub">管理搬砖、清沙滩、炼造与兑换任务</div>
        </div>
      </div>
      <div class="siqi-topbar__right">
        <v-btn-group variant="tonal" density="compact" class="elevation-0">
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="状态页"
            :disabled="formLocked"
            @click="emit('switch', 'page')"
          >
            <v-icon icon="mdi-view-dashboard" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">状态页</span>
          </v-btn>
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="保存配置"
            :loading="configSaving"
            :disabled="formLocked"
            @click="saveConfig"
          >
            <v-icon icon="mdi-content-save" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">保存</span>
          </v-btn>
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="关闭配置"
            @click="emit('close')"
          >
            <v-icon icon="mdi-close" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">关闭</span>
          </v-btn>
        </v-btn-group>
      </div>
    </div>

    <v-alert
      v-if="message"
      :type="messageType"
      density="compact"
      class="siqi-toast"
      closable
      @click:close="message = ''"
    >
      {{ message }}
    </v-alert>

    <v-alert type="warning" variant="tonal" density="compact" class="siqi-migration-note">
      <strong>v0.2.0 升级提示：</strong>首次迁移会保持插件关闭。升级后请先检查并保存新版设置，再手动启用任务。
    </v-alert>

    <div v-if="configLoading" class="siqi-loading-state" role="status" aria-live="polite">
      <v-progress-linear color="success" indeterminate rounded />
      <span>正在加载配置，请稍候</span>
    </div>

    <fieldset
      class="siqi-form-lock"
      :disabled="formLocked"
      :inert="formLocked"
      :aria-busy="formLocked"
    >
      <div class="siqi-config-col">
      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-toggle-switch-outline" size="18" color="#22c55e" class="mr-1" />基础设置
          </span>
        </div>
        <div class="siqi-switch-grid">
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.enabled}" style="--siqi-accent:34,197,94">
            <div class="siqi-switch-main"><v-icon icon="mdi-power-plug" size="18" /><div><div class="siqi-switch-label">启用插件</div><div class="siqi-switch-desc">开启定时任务；升级后请确认设置再手动开启</div></div></div>
            <v-switch v-model="config.enabled" color="green" hide-details density="compact" aria-label="启用插件" :disabled="formLocked" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.notify}" style="--siqi-accent:59,130,246">
            <div class="siqi-switch-main"><v-icon icon="mdi-bell-outline" size="18" /><div><div class="siqi-switch-label">通知</div><div class="siqi-switch-desc">任务完成或异常时发送 MoviePilot 通知</div></div></div>
            <v-switch v-model="config.notify" color="blue" hide-details density="compact" aria-label="通知" :disabled="formLocked" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.use_proxy}" style="--siqi-accent:139,92,246">
            <div class="siqi-switch-main"><v-icon icon="mdi-lan-connect" size="18" /><div><div class="siqi-switch-label">代理</div><div class="siqi-switch-desc">使用 MoviePilot 已配置的网络代理访问站点</div></div></div>
            <v-switch v-model="config.use_proxy" color="purple" hide-details density="compact" aria-label="代理" :disabled="formLocked" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.force_ipv4}" style="--siqi-accent:14,165,233">
            <div class="siqi-switch-main"><v-icon icon="mdi-ip-network-outline" size="18" /><div><div class="siqi-switch-label">强制IPv4</div><div class="siqi-switch-desc">强制 IPv4 可减少部分 IPv6 环境连接不稳</div></div></div>
            <v-switch v-model="config.force_ipv4" color="info" hide-details density="compact" aria-label="强制IPv4" :disabled="formLocked" />
          </div>
        </div>
      </div>

      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-robot-outline" size="18" color="#f59e0b" class="mr-1" />自动化策略
          </span>
        </div>
        <div class="siqi-switch-grid">
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.onlyonce}" style="--siqi-accent:245,158,11">
            <div class="siqi-switch-main"><v-icon icon="mdi-play-circle-outline" size="18" /><div><div class="siqi-switch-label">立即运行一次</div><div class="siqi-switch-desc">保存后排队执行一轮，执行后自动关闭此开关</div></div></div>
            <v-switch v-model="config.onlyonce" color="orange" hide-details density="compact" aria-label="立即运行一次" :disabled="formLocked" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.enable_brick}" style="--siqi-accent:34,197,94">
            <div class="siqi-switch-main"><v-icon icon="mdi-wall" size="18" /><div><div class="siqi-switch-label">自动搬砖</div><div class="siqi-switch-desc">按搬砖 Cron 定时执行搬砖</div></div></div>
            <v-switch v-model="config.enable_brick" color="green" hide-details density="compact" aria-label="自动搬砖" :disabled="formLocked" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.enable_beach}" style="--siqi-accent:14,165,233">
            <div class="siqi-switch-main"><v-icon icon="mdi-beach" size="18" /><div><div class="siqi-switch-label">动态清沙滩</div><div class="siqi-switch-desc">根据站点冷却时间动态安排清理</div></div></div>
            <v-switch v-model="config.enable_beach" color="info" hide-details density="compact" aria-label="动态清沙滩" :disabled="formLocked" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.auto_craft}" style="--siqi-accent:239,68,68">
            <div class="siqi-switch-main"><v-icon icon="mdi-hammer-wrench" size="18" /><div><div class="siqi-switch-label">自动炼造</div><div class="siqi-switch-desc">清沙滩后按可用材料自动炼造</div></div></div>
            <v-switch v-model="config.auto_craft" color="red" hide-details density="compact" aria-label="自动炼造" :disabled="formLocked" />
          </div>
          <div class="siqi-switch-item" :class="{'siqi-switch-item--active': config.auto_exchange}" style="--siqi-accent:236,72,153">
            <div class="siqi-switch-main"><v-icon icon="mdi-cash-sync" size="18" /><div><div class="siqi-switch-label">自动兑换</div><div class="siqi-switch-desc">保留指定魔丸后自动兑换魔力</div></div></div>
            <v-switch v-model="config.auto_exchange" color="pink" hide-details density="compact" aria-label="自动兑换" :disabled="formLocked" />
          </div>
        </div>
      </div>

      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-tune-variant" size="18" color="#0ea5e9" class="mr-1" />参数设置
          </span>
        </div>
        <div class="siqi-form-grid">
          <div class="siqi-field siqi-wide-field">
            <VCronField v-model="config.brick_cron" label="搬砖Cron" density="compact" class="siqi-input siqi-cron-field" :disabled="formLocked" />
            <div class="siqi-field-hint">搬砖 Cron 是定时规则；默认每天 00:05 执行。</div>
          </div>
          <div class="siqi-field">
            <v-text-field v-model.number="config.schedule_buffer_seconds" label="冷却缓冲（秒）" type="number" min="0" max="3600" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-clock-fast" :disabled="formLocked" />
            <div class="siqi-field-hint">站点显示可执行后再等待一小段时间，最小 0 秒。</div>
          </div>
          <div class="siqi-field">
            <v-text-field v-model.number="config.reserve_magic_pill_count" label="保留魔丸" type="number" min="0" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-flask-outline" :disabled="formLocked" />
            <div class="siqi-field-hint">自动兑换前保留的魔丸数量，默认 10。</div>
          </div>
          <div class="siqi-field">
            <v-text-field v-model.number="config.random_delay_max_seconds" label="随机延迟（秒）" type="number" min="0" max="300" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-timer-sand" :disabled="formLocked" />
            <div class="siqi-field-hint">每次操作前随机等待，0 表示不额外等待。</div>
          </div>
          <div class="siqi-field">
            <v-text-field v-model.number="config.http_timeout" label="请求超时（秒）" type="number" min="5" max="120" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-timer-alert-outline" :disabled="formLocked" />
            <div class="siqi-field-hint">单次网络请求最长等待时间，后端最小按 5 秒处理。</div>
          </div>
          <div class="siqi-field">
            <v-text-field v-model.number="config.http_retry_times" label="网络重试次数" type="number" min="1" max="5" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-reload" :disabled="formLocked" />
            <div class="siqi-field-hint">网络失败时重试 1 到 5 次，以后端校验结果为准。</div>
          </div>
          <div class="siqi-field">
            <v-text-field v-model.number="retryDelaySeconds" label="重试间隔（秒）" type="number" min="0.2" max="60" step="0.1" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-timer-outline" :disabled="formLocked" />
            <div class="siqi-field-hint">两次网络重试之间的等待时间，最小 0.2 秒。</div>
          </div>
        </div>
      </div>

      <div class="siqi-card">
        <div class="siqi-card__header">
          <span class="siqi-card__title d-flex align-center">
            <v-icon icon="mdi-web-sync" size="18" color="#22c55e" class="mr-1" />站点凭据
          </span>
        </div>
        <div class="siqi-site-note">
          <v-icon icon="mdi-shield-check-outline" size="20" />
          <div>
            <div class="siqi-site-note__title">Cookie：从 MoviePilot 站点自动同步。</div>
            <div class="siqi-site-note__desc">此处无需填写或手动操作，插件每次请求都会读取最新站点凭据。</div>
          </div>
        </div>
      </div>
      </div>
    </fieldset>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import {
  createLatestRequestGuard,
  isStrictSuccess,
  safeResponseMessage,
} from '../utils/asyncGuards.js'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['switch', 'close'])

const CONFIG_ENDPOINT = '/plugin/VuePill/config'
const CONFIG_FIELDS = Object.freeze([
  'enabled',
  'notify',
  'onlyonce',
  'use_proxy',
  'force_ipv4',
  'enable_brick',
  'enable_beach',
  'auto_craft',
  'auto_exchange',
  'brick_cron',
  'schedule_buffer_seconds',
  'reserve_magic_pill_count',
  'random_delay_max_seconds',
  'http_timeout',
  'http_retry_times',
  'http_retry_delay',
])
const DEFAULT_CONFIG = Object.freeze({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  reserve_magic_pill_count: 10,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
})

const config = reactive({ ...DEFAULT_CONFIG })
const configLoading = ref(false)
const configSaving = ref(false)
const formLocked = computed(() => configLoading.value || configSaving.value)
const message = ref('')
const messageType = ref('success')
const loadRequestGuard = createLatestRequestGuard()
const saveRequestGuard = createLatestRequestGuard()
let messageTimer = null
let disposed = false

applyPublicConfig(props.initialConfig)

const retryDelaySeconds = computed({
  get: () => Number(config.http_retry_delay || 0) / 1000,
  set: (value) => {
    const seconds = Number(value)
    config.http_retry_delay = Math.max(200, Math.round((Number.isFinite(seconds) ? seconds : 0) * 1000))
  },
})

function ownDataValue(source, field) {
  if (!source || typeof source !== 'object' || Array.isArray(source)) return undefined
  try {
    const descriptor = Object.getOwnPropertyDescriptor(source, field)
    return descriptor && Object.prototype.hasOwnProperty.call(descriptor, 'value')
      ? descriptor.value
      : undefined
  } catch {
    return undefined
  }
}

function applyPublicConfig(source) {
  for (const field of CONFIG_FIELDS) {
    const value = ownDataValue(source, field)
    config[field] = value === undefined ? DEFAULT_CONFIG[field] : value
  }
}

function isCompletePublicConfig(source) {
  return CONFIG_FIELDS.every(field => ownDataValue(source, field) !== undefined)
}

function buildConfigPayload() {
  const payload = {}
  for (const field of CONFIG_FIELDS) payload[field] = config[field]
  return payload
}

function show(text, type = 'success') {
  if (disposed) return
  message.value = typeof text === 'string' && text.trim() ? text.trim() : '操作失败'
  messageType.value = type
  if (messageTimer) clearTimeout(messageTimer)
  messageTimer = setTimeout(() => {
    if (!disposed) message.value = ''
    messageTimer = null
  }, 4000)
}

function errorMessage(error, fallback) {
  return typeof error?.message === 'string' && error.message.trim()
    ? error.message.trim()
    : fallback
}

async function loadConfig({ silent = false } = {}) {
  const requestId = loadRequestGuard.begin()
  configLoading.value = true
  try {
    const data = await props.api.get(CONFIG_ENDPOINT)
    if (!loadRequestGuard.isCurrent(requestId)) return
    applyPublicConfig(data)
  } catch (error) {
    if (loadRequestGuard.isCurrent(requestId) && !silent) {
      show(`加载失败：${errorMessage(error, '请求异常')}`, 'error')
    }
  } finally {
    if (loadRequestGuard.isCurrent(requestId)) configLoading.value = false
  }
}

async function saveConfig() {
  if (formLocked.value) return
  const requestId = saveRequestGuard.begin()
  configSaving.value = true
  const payload = buildConfigPayload()
  try {
    const result = await props.api.post(CONFIG_ENDPOINT, payload)
    if (!saveRequestGuard.isCurrent(requestId)) return
    if (!isStrictSuccess(result)) {
      show(safeResponseMessage(result, '保存失败'), 'error')
      return
    }
    if (isCompletePublicConfig(result?.config)) {
      applyPublicConfig(result.config)
    } else {
      config.onlyonce = false
      await loadConfig({ silent: true })
    }
    show(safeResponseMessage(result, '配置已保存'))
  } catch (error) {
    if (saveRequestGuard.isCurrent(requestId)) {
      show(`保存失败：${errorMessage(error, '请求异常')}`, 'error')
    }
  } finally {
    if (saveRequestGuard.isCurrent(requestId)) configSaving.value = false
  }
}

onMounted(loadConfig)

onBeforeUnmount(() => {
  disposed = true
  loadRequestGuard.invalidate()
  saveRequestGuard.invalidate()
  if (messageTimer) clearTimeout(messageTimer)
})
</script>

<style scoped>
.siqi-config{width:100%;max-width:100%;min-height:400px;padding:16px 20px;display:flex;flex-direction:column;gap:16px;overflow-x:hidden;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter',sans-serif;color:rgba(var(--v-theme-on-surface),.85);border:1px solid rgba(var(--v-theme-on-surface),.12);border-radius:8px;background:linear-gradient(180deg,rgba(var(--v-theme-surface),.22),rgba(76,175,80,.025))}
.siqi-config *{box-sizing:border-box}.siqi-topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-bottom:8px;min-width:0}.siqi-topbar__left{display:flex;align-items:center;gap:12px;min-width:0;flex:1}.siqi-topbar__copy{min-width:0}.siqi-topbar__right{display:flex;align-items:center;gap:10px;flex-shrink:0}.siqi-topbar__right :deep(.v-btn-group){flex-wrap:nowrap}.siqi-topbar__icon{width:42px;height:42px;border-radius:11px;background:rgba(76,175,80,.14);display:flex;align-items:center;justify-content:center;color:#2e7d32;flex-shrink:0}.siqi-topbar__title{font-size:16px;font-weight:700;letter-spacing:-.3px;color:rgba(var(--v-theme-on-surface),.88)}.siqi-topbar__sub{font-size:11px;color:rgba(var(--v-theme-on-surface),.55);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.siqi-config :deep(.v-btn){min-height:44px}
.siqi-toast{position:fixed!important;top:18px!important;left:50%!important;transform:translateX(-50%)!important;z-index:99999!important;width:min(520px,calc(100vw - 32px))!important;margin:0!important;box-shadow:0 12px 36px rgba(15,23,42,.18)!important;border-radius:12px!important}.siqi-migration-note{border-radius:12px!important;line-height:1.6}.siqi-loading-state{display:flex;flex-direction:column;gap:7px;font-size:11px;color:rgba(var(--v-theme-on-surface),.58)}.siqi-form-lock{min-inline-size:0;margin:0;padding:0;border:0}.siqi-config-col{display:flex;flex-direction:column;gap:16px;min-width:0}.siqi-card{min-width:0;background:rgba(var(--v-theme-surface),.5);backdrop-filter:blur(20px) saturate(150%);border-radius:14px;border:.5px solid rgba(var(--v-theme-on-surface),.08);box-shadow:0 2px 10px rgba(0,0,0,.05);padding:14px 16px;display:flex;flex-direction:column;gap:14px}.siqi-card__header{display:flex;align-items:center;justify-content:space-between;gap:12px}.siqi-card__title{font-size:13px;font-weight:700;color:rgba(var(--v-theme-on-surface),.85)}
.siqi-switch-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;min-width:0}.siqi-switch-item{min-width:0;min-height:72px;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px;border-radius:12px;background:rgba(var(--v-theme-on-surface),.025);border:.5px solid rgba(var(--v-theme-on-surface),.06);transition:background .2s ease,border-color .2s ease,transform .2s ease}.siqi-switch-item:hover{transform:translateY(-1px)}.siqi-switch-item--active{background:rgba(var(--siqi-accent,34,197,94),.07);border-color:rgba(var(--siqi-accent,34,197,94),.18)}.siqi-switch-main{display:flex;align-items:center;gap:10px;min-width:0;flex:1;color:rgba(var(--v-theme-on-surface),.58)}.siqi-switch-main>div{min-width:0}.siqi-switch-item--active .siqi-switch-main{color:rgb(var(--siqi-accent,34,197,94))}.siqi-switch-label{font-size:13px;font-weight:600;color:rgba(var(--v-theme-on-surface),.86)}.siqi-switch-desc{font-size:11px;color:rgba(var(--v-theme-on-surface),.46);line-height:1.45;margin-top:2px}.siqi-switch-item :deep(.v-switch){flex:0 0 auto}.siqi-switch-item :deep(.v-selection-control){min-width:44px;min-height:44px}.siqi-switch-item :deep(.v-input__details){display:none}
.siqi-form-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px 14px;min-width:0}.siqi-field{min-width:0;display:flex;flex-direction:column;gap:7px}.siqi-wide-field{grid-column:span 2}.siqi-input{min-width:0}.siqi-input :deep(.v-field){border-radius:12px;background:rgba(var(--v-theme-surface),.34)}.siqi-input :deep(.v-field__input){min-height:44px}.siqi-input :deep(.v-field__loader){left:1px;right:1px;width:auto;border-radius:12px 12px 0 0;overflow:hidden}.siqi-cron-field{width:100%}.siqi-field-hint{font-size:11px;line-height:1.5;color:rgba(var(--v-theme-on-surface),.5);padding-inline:2px}.siqi-site-note{display:flex;align-items:flex-start;gap:10px;min-width:0;padding:12px;border-radius:12px;background:rgba(34,197,94,.07);border:.5px solid rgba(34,197,94,.18);color:rgba(var(--v-theme-on-surface),.7)}.siqi-site-note>div{min-width:0}.siqi-site-note__title{font-size:13px;font-weight:650;color:rgba(var(--v-theme-on-surface),.86)}.siqi-site-note__desc{margin-top:3px;font-size:11px;line-height:1.5;color:rgba(var(--v-theme-on-surface),.5)}
@media(max-width:900px){.siqi-switch-grid,.siqi-form-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.siqi-wide-field{grid-column:span 2}}
@media(max-width:600px){.siqi-config{padding:14px}.siqi-topbar{flex-direction:column;align-items:stretch;gap:10px}.siqi-topbar__left{width:100%;min-width:0}.siqi-topbar__right{width:100%;justify-content:flex-end}.siqi-topbar__right :deep(.v-btn-group){width:100%}.siqi-topbar__right :deep(.v-btn){flex:1 1 0;min-width:44px!important;padding-inline:0!important}.siqi-switch-grid,.siqi-form-grid{grid-template-columns:1fr}.siqi-wide-field{grid-column:span 1}.siqi-switch-item{align-items:center}.siqi-topbar__sub{max-width:100%}}
</style>
