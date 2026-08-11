<template>
  <div class="siqi-config">
    <div class="siqi-topbar">
      <div class="siqi-topbar__left">
        <div class="siqi-topbar__icon">
          <v-icon icon="mdi-cog-outline" size="24" />
        </div>
        <div class="siqi-topbar__copy">
          <div class="siqi-topbar__title">Vue-玩偶 · 配置</div>
          <div class="siqi-topbar__sub">管理自己展位保护、动态收回和外展策略</div>
        </div>
      </div>
      <div class="siqi-topbar__right">
        <v-btn-group variant="tonal" density="compact" class="elevation-0">
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="返回 Vue-玩偶状态页"
            :disabled="formLocked"
            @click="emit('switch', 'page')"
          >
            <v-icon icon="mdi-view-dashboard-outline" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">状态页</span>
          </v-btn>
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="保存 Vue-玩偶配置"
            :loading="saving"
            :disabled="formLocked"
            @click="saveConfig"
          >
            <v-icon icon="mdi-content-save-outline" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">保存</span>
          </v-btn>
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="关闭 Vue-玩偶配置"
            @click="emit('close')"
          >
            <v-icon icon="mdi-close" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">关闭</span>
          </v-btn>
        </v-btn-group>
      </div>
    </div>

    <div class="config-content">
      <v-alert
        v-if="message.text"
        :type="message.type"
        density="compact"
        class="siqi-toast"
        closable
        @click:close="message.text = ''"
      >
        {{ message.text }}
      </v-alert>

      <div v-if="loading" class="loading-state" role="status" aria-live="polite">
        <v-progress-linear color="success" indeterminate rounded />
        <span>正在加载配置，请稍候</span>
      </div>

      <fieldset v-else class="siqi-form-lock" :disabled="formLocked" :aria-busy="formLocked">
        <div class="siqi-config-col">
          <section class="siqi-card">
            <div class="siqi-card__header">
              <span class="siqi-card__title">
                <v-icon icon="mdi-toggle-switch-outline" size="19" color="success" />
                基础设置
              </span>
            </div>
            <div class="siqi-switch-grid">
              <div class="siqi-switch-item" :class="{ 'siqi-switch-item--active': config.enabled }" style="--siqi-accent:34,197,94">
                <div class="siqi-switch-main">
                  <v-icon icon="mdi-power-plug-outline" size="20" />
                  <div><div class="siqi-switch-label">启用插件</div><div class="siqi-switch-desc">开启动态调度和自动任务</div></div>
                </div>
                <v-switch v-model="config.enabled" color="success" density="compact" hide-details inset />
              </div>

              <div class="siqi-switch-item" :class="{ 'siqi-switch-item--active': config.notify }" style="--siqi-accent:59,130,246">
                <div class="siqi-switch-main">
                  <v-icon icon="mdi-bell-outline" size="20" />
                  <div><div class="siqi-switch-label">开启通知</div><div class="siqi-switch-desc">有实际收回或展出结果时通知</div></div>
                </div>
                <v-switch v-model="config.notify" color="blue" density="compact" hide-details inset />
              </div>

              <div class="siqi-switch-item" :class="{ 'siqi-switch-item--active': config.use_proxy }" style="--siqi-accent:139,92,246">
                <div class="siqi-switch-main">
                  <v-icon icon="mdi-lan-connect" size="20" />
                  <div><div class="siqi-switch-label">使用代理</div><div class="siqi-switch-desc">请求站点时使用 MoviePilot 代理</div></div>
                </div>
                <v-switch v-model="config.use_proxy" color="purple" density="compact" hide-details inset />
              </div>

              <div class="siqi-switch-item" :class="{ 'siqi-switch-item--active': config.onlyonce }" style="--siqi-accent:245,158,11">
                <div class="siqi-switch-main">
                  <v-icon icon="mdi-play-circle-outline" size="20" />
                  <div><div class="siqi-switch-label">立即运行一次</div><div class="siqi-switch-desc">保存后执行一次完整玩偶任务</div></div>
                </div>
                <v-switch v-model="config.onlyonce" color="orange" density="compact" hide-details inset />
              </div>
            </div>
          </section>

          <section class="siqi-card">
            <div class="siqi-card__header">
              <span class="siqi-card__title">
                <v-icon icon="mdi-robot-outline" size="19" color="orange" />
                自动化策略
              </span>
            </div>
            <div class="siqi-switch-grid">
              <div class="siqi-switch-item" :class="{ 'siqi-switch-item--active': config.auto_collect }" style="--siqi-accent:34,197,94">
                <div class="siqi-switch-main">
                  <v-icon icon="mdi-package-down" size="20" />
                  <div><div class="siqi-switch-label">自动收回</div><div class="siqi-switch-desc">到点先收回自己和外展玩偶</div></div>
                </div>
                <v-switch v-model="config.auto_collect" color="success" density="compact" hide-details inset />
              </div>

              <div class="siqi-switch-item" :class="{ 'siqi-switch-item--active': config.auto_place }" style="--siqi-accent:249,115,22">
                <div class="siqi-switch-main">
                  <v-icon icon="mdi-storefront-plus-outline" size="20" />
                  <div><div class="siqi-switch-label">自动展出</div><div class="siqi-switch-desc">先补满自己展位，再寻找外展位</div></div>
                </div>
                <v-switch v-model="config.auto_place" color="orange" density="compact" hide-details inset />
              </div>
            </div>
          </section>

          <section class="siqi-card">
            <div class="siqi-card__header">
              <span class="siqi-card__title">
                <v-icon icon="mdi-tune-variant" size="19" color="blue" />
                参数设置
              </span>
            </div>
            <div class="siqi-form-grid">
              <div class="siqi-field">
                <v-text-field
                  v-model="config.self_slot_guard_hours"
                  type="number"
                  min="0"
                  max="24"
                  step="1"
                  label="自家展位保护时间"
                  suffix="小时"
                  prepend-inner-icon="mdi-shield-home-outline"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  class="siqi-input siqi-number-input"
                />
                <div class="siqi-field-hint">默认 1 小时。按即将空出的自家展位数量预留玩偶，其余继续外展；设置 0 可关闭。</div>
              </div>

              <div class="siqi-field">
                <v-text-field
                  v-model="config.random_delay_max_seconds"
                  type="number"
                  min="0"
                  max="60"
                  step="1"
                  label="随机延迟"
                  suffix="秒"
                  prepend-inner-icon="mdi-timer-random"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  class="siqi-input siqi-number-input"
                />
                <div class="siqi-field-hint">任务触发后随机等待 0 到该秒数，设置 0 表示不延迟。</div>
              </div>
            </div>
          </section>

          <section class="siqi-card cookie-card">
            <div class="siqi-card__header">
              <span class="siqi-card__title">
                <v-icon icon="mdi-cookie-outline" size="19" color="teal" />
                站点 Cookie
              </span>
            </div>
            <div class="cookie-body">
              <v-text-field
                v-model="config.cookie"
                :type="cookieVisible ? 'text' : 'password'"
                label="站点 Cookie"
                placeholder="自动读取 MoviePilot 站点管理中的 si-qi.xyz Cookie"
                prepend-inner-icon="mdi-cookie"
                variant="outlined"
                density="compact"
                hide-details
                autocomplete="off"
                class="siqi-input"
                :disabled="loading || saving"
              >
                <template #append-inner>
                  <div class="siqi-cookie-actions">
                    <v-btn variant="text" density="comfortable" size="x-small" icon class="siqi-secret-toggle" :aria-label="cookieVisible ? '隐藏 Cookie' : '显示 Cookie'" @click.stop="cookieVisible = !cookieVisible">
                      <v-icon :icon="cookieVisible ? 'mdi-eye-off-outline' : 'mdi-eye-outline'" size="18" />
                    </v-btn>
                    <v-btn variant="tonal" color="teal" density="comfortable" size="x-small" icon class="siqi-cookie-sync" :loading="syncingCookie" :disabled="loading || saving" aria-label="使用 MoviePilot 站点 Cookie" @click.stop="syncCookie">
                      <v-icon icon="mdi-content-paste" size="17" />
                    </v-btn>
                  </div>
                </template>
              </v-text-field>
              <div class="cookie-note">
                插件默认使用 MoviePilot 站点管理中的 Cookie；输入框内容仅在站点同步失败时作为备用，右侧按钮可立即重新读取。网络由系统自动选择 IPv4 或 IPv6。
              </div>
            </div>
          </section>
        </div>
      </fieldset>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])
const pluginBase = '/plugin/VueToy'

const loading = ref(true)
const saving = ref(false)
const syncingCookie = ref(false)
const cookieVisible = ref(false)
const message = reactive({ text: '', type: 'success' })
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  auto_collect: true,
  auto_place: true,
  self_slot_guard_hours: 1,
  random_delay_max_seconds: 5,
  cookie: '',
})

const formLocked = computed(() => loading.value || saving.value || syncingCookie.value)

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function normalizeNumber(value, fallback, min, max) {
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) return fallback
  return Math.max(min, Math.min(max, Math.round(parsed)))
}

function applyConfig(data = {}) {
  const { capture_tips, ...rest } = data || {}
  Object.assign(config, rest)
  config.self_slot_guard_hours = normalizeNumber(config.self_slot_guard_hours, 1, 0, 24)
  config.random_delay_max_seconds = normalizeNumber(config.random_delay_max_seconds, 5, 0, 60)
}

async function loadConfig() {
  loading.value = true
  try {
    const data = await props.api.get(`${pluginBase}/config`)
    applyConfig(data || {})
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error')
  } finally {
    loading.value = false
  }
}

async function saveConfig() {
  saving.value = true
  try {
    const payload = {
      ...config,
      self_slot_guard_hours: normalizeNumber(config.self_slot_guard_hours, 1, 0, 24),
      random_delay_max_seconds: normalizeNumber(config.random_delay_max_seconds, 5, 0, 60),
    }
    const result = await props.api.post(`${pluginBase}/config`, payload)
    if (result?.config) applyConfig(result.config)
    flash(result?.message || '配置已保存')
  } catch (error) {
    flash(error?.message || '保存配置失败', 'error')
  } finally {
    saving.value = false
  }
}

async function syncCookie() {
  syncingCookie.value = true
  try {
    const result = await props.api.get(`${pluginBase}/cookie`)
    if (result?.config) applyConfig(result.config)
    flash(result?.message || 'Cookie 已同步')
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error')
  } finally {
    syncingCookie.value = false
  }
}

onMounted(async () => {
  applyConfig(props.initialConfig || {})
  await loadConfig()
})
</script>

<style scoped>
.siqi-config {
  width: 100%;
  max-width: 100%;
  min-height: 400px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-x: hidden;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', sans-serif;
  color: rgba(var(--v-theme-on-surface), .85);
  border: 1px solid rgba(var(--v-theme-on-surface), .12);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(76,175,80,.025));
}
.siqi-config * { box-sizing: border-box; }
.siqi-config :deep(.v-btn) { min-height: 44px; }

.siqi-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 8px;
  min-width: 0;
}
.siqi-topbar__left,
.siqi-topbar__right {
  display: flex;
  align-items: center;
}
.siqi-topbar__left { gap: 12px; min-width: 0; flex: 1; }
.siqi-topbar__right { gap: 10px; flex-shrink: 0; }
.siqi-topbar__right :deep(.v-btn-group) { flex-wrap: nowrap; }
.siqi-topbar__copy { min-width: 0; }
.siqi-topbar__icon {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #2e7d32;
  background: rgba(76,175,80,.14);
}
.siqi-topbar__title { font-size: 16px; font-weight: 700; letter-spacing: -.3px; color: rgba(var(--v-theme-on-surface), .88); }
.siqi-topbar__sub { margin-top: 2px; overflow: hidden; color: rgba(var(--v-theme-on-surface), .55); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }

.config-content { width: 100%; min-width: 0; display: flex; flex-direction: column; gap: 16px; }
.siqi-toast {
  position: fixed !important;
  top: 18px !important;
  left: 50% !important;
  z-index: 99999 !important;
  width: min(520px, calc(100vw - 32px)) !important;
  margin: 0 !important;
  border-radius: 12px !important;
  box-shadow: 0 12px 36px rgba(15,23,42,.18) !important;
  transform: translateX(-50%) !important;
}
.loading-state {
  display: grid;
  gap: 12px;
  padding: 28px 18px;
  border: .5px solid rgba(var(--v-theme-on-surface), .08);
  border-radius: 14px;
  color: rgba(var(--v-theme-on-surface), .68);
  background: rgba(var(--v-theme-on-surface), .03);
  backdrop-filter: blur(20px) saturate(150%);
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
}
.siqi-form-lock { min-width: 0; margin: 0; padding: 0; border: 0; }
.siqi-config-col { display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.siqi-card {
  min-width: 0;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  border: .5px solid rgba(var(--v-theme-on-surface), .08);
  border-radius: 14px;
  background: rgba(var(--v-theme-on-surface), .03);
  backdrop-filter: blur(20px) saturate(150%);
  box-shadow: inset 0 1px 0 rgba(var(--v-theme-surface), .2), 0 2px 10px rgba(0,0,0,.05);
}
.siqi-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.siqi-card__title { display: flex; align-items: center; gap: 7px; font-size: 13px; font-weight: 700; color: rgba(var(--v-theme-on-surface), .85); }

.siqi-switch-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; min-width: 0; }
.siqi-switch-item {
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px;
  border: .5px solid rgba(var(--v-theme-on-surface), .06);
  border-radius: 12px;
  background: rgba(var(--v-theme-on-surface), .025);
  transition: background .2s ease, border-color .2s ease, transform .2s ease;
}
.siqi-switch-item:hover { transform: translateY(-1px); }
.siqi-switch-item--active { border-color: rgba(var(--siqi-accent,34,197,94), .18); background: rgba(var(--siqi-accent,34,197,94), .07); }
.siqi-switch-main { min-width: 0; flex: 1; display: flex; align-items: center; gap: 10px; color: rgba(var(--v-theme-on-surface), .58); }
.siqi-switch-main > div { min-width: 0; }
.siqi-switch-item--active .siqi-switch-main { color: rgb(var(--siqi-accent,34,197,94)); }
.siqi-switch-label { font-size: 13px; font-weight: 600; color: rgba(var(--v-theme-on-surface), .86); }
.siqi-switch-desc { margin-top: 1px; color: rgba(var(--v-theme-on-surface), .46); font-size: 11px; line-height: 1.35; }
.siqi-switch-item :deep(.v-switch) { flex: 0 0 auto; }
.siqi-switch-item :deep(.v-selection-control) { min-width: 44px; min-height: 44px; }
.siqi-switch-item :deep(.v-input__details) { display: none; }

.siqi-form-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; min-width: 0; }
.siqi-field { min-width: 0; display: flex; flex-direction: column; gap: 7px; }
.siqi-input { min-width: 0; }
.siqi-input :deep(.v-field),
.siqi-number-input :deep(.v-field) { border-radius: 12px; }
.siqi-input :deep(.v-field__input) { min-height: 44px; }
.siqi-field-hint { color: rgba(var(--v-theme-on-surface), .5); font-size: 11px; line-height: 1.5; padding-inline: 2px; }
.siqi-number-input :deep(.v-field__input) { min-height: 44px; align-items: center; padding-top: 8px; padding-bottom: 8px; }
.siqi-number-input :deep(input) { align-self: center; line-height: 24px; text-align: center; }
.siqi-number-input :deep(.v-field__prepend-inner),
.siqi-number-input :deep(.v-field__append-inner) { align-self: center; padding-top: 0; }

.cookie-body { display: grid; gap: 10px; }
.cookie-note { color: rgba(var(--v-theme-on-surface), .6); font-size: .72rem; line-height: 1.5; }
.siqi-cookie-actions { display: flex; align-items: center; gap: 3px; }
.siqi-secret-toggle,
.siqi-cookie-sync { min-width: 28px !important; min-height: 28px !important; width: 28px; height: 28px; }
.siqi-secret-toggle { color: rgba(var(--v-theme-on-surface), .55); }

@media (prefers-reduced-motion: reduce) {
  .siqi-switch-item { transition: none; }
}

@media (max-width: 900px) {
  .siqi-switch-grid,
  .siqi-form-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 600px) {
  .siqi-config { padding: 14px; }
  .siqi-topbar { flex-direction: column; align-items: stretch; gap: 10px; }
  .siqi-topbar__left { width: 100%; min-width: 0; }
  .siqi-topbar__right { width: 100%; justify-content: flex-end; }
  .siqi-topbar__right :deep(.v-btn-group) { width: 100%; }
  .siqi-topbar__right :deep(.v-btn) { flex: 1 1 0; min-width: 44px !important; padding-inline: 0 !important; }
  .siqi-switch-grid,
  .siqi-form-grid { grid-template-columns: 1fr; }
  .siqi-switch-item { align-items: center; }
  .siqi-topbar__sub { max-width: 100%; }
}
</style>
