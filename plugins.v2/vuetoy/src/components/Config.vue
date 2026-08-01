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

      <fieldset v-else class="config-fieldset" :disabled="formLocked" :aria-busy="formLocked">
        <div class="config-column">
          <section class="siqi-card">
            <div class="siqi-card__header">
              <span class="siqi-card__title">
                <v-icon icon="mdi-toggle-switch-outline" size="19" color="success" />
                基础设置
              </span>
            </div>
            <div class="switch-grid">
              <div class="switch-item" :class="{ 'switch-item--active': config.enabled }" style="--accent:34,197,94">
                <div class="switch-main">
                  <v-icon icon="mdi-power-plug-outline" size="20" />
                  <div><div class="switch-label">启用插件</div><div class="switch-desc">开启动态调度和自动任务</div></div>
                </div>
                <v-switch v-model="config.enabled" color="success" density="compact" hide-details inset />
              </div>

              <div class="switch-item" :class="{ 'switch-item--active': config.notify }" style="--accent:59,130,246">
                <div class="switch-main">
                  <v-icon icon="mdi-bell-outline" size="20" />
                  <div><div class="switch-label">开启通知</div><div class="switch-desc">有实际收回或展出结果时通知</div></div>
                </div>
                <v-switch v-model="config.notify" color="blue" density="compact" hide-details inset />
              </div>

              <div class="switch-item" :class="{ 'switch-item--active': config.use_proxy }" style="--accent:139,92,246">
                <div class="switch-main">
                  <v-icon icon="mdi-lan-connect" size="20" />
                  <div><div class="switch-label">使用代理</div><div class="switch-desc">请求站点时使用 MoviePilot 代理</div></div>
                </div>
                <v-switch v-model="config.use_proxy" color="purple" density="compact" hide-details inset />
              </div>

              <div class="switch-item" :class="{ 'switch-item--active': config.onlyonce }" style="--accent:245,158,11">
                <div class="switch-main">
                  <v-icon icon="mdi-play-circle-outline" size="20" />
                  <div><div class="switch-label">立即运行一次</div><div class="switch-desc">保存后执行一次完整玩偶任务</div></div>
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
            <div class="switch-grid switch-grid--two">
              <div class="switch-item" :class="{ 'switch-item--active': config.auto_collect }" style="--accent:34,197,94">
                <div class="switch-main">
                  <v-icon icon="mdi-package-down" size="20" />
                  <div><div class="switch-label">自动收回</div><div class="switch-desc">到点先收回自己和外展玩偶</div></div>
                </div>
                <v-switch v-model="config.auto_collect" color="success" density="compact" hide-details inset />
              </div>

              <div class="switch-item" :class="{ 'switch-item--active': config.auto_place }" style="--accent:249,115,22">
                <div class="switch-main">
                  <v-icon icon="mdi-storefront-plus-outline" size="20" />
                  <div><div class="switch-label">自动展出</div><div class="switch-desc">先补满自己展位，再寻找外展位</div></div>
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
            <div class="parameter-grid">
              <div class="parameter-item">
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
                  class="siqi-number-input"
                />
                <div class="field-help">默认 1 小时。自己展位快到期且有可用玩偶时暂停外展；设置 0 可关闭。</div>
              </div>

              <div class="parameter-item">
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
                  class="siqi-number-input"
                />
                <div class="field-help">任务触发后随机等待 0 到该秒数，设置 0 表示不延迟。</div>
              </div>
            </div>
          </section>

          <section class="siqi-card cookie-card">
            <div class="siqi-card__header">
              <span class="siqi-card__title">
                <v-icon icon="mdi-cookie-outline" size="19" color="teal" />
                站点 Cookie
              </span>
              <v-chip size="small" color="teal" variant="tonal">默认自动同步</v-chip>
            </div>
            <div class="cookie-body">
              <v-text-field
                v-model="config.cookie"
                :type="cookieVisible ? 'text' : 'password'"
                label="Cookie 备用值"
                placeholder="优先使用 MoviePilot 站点管理中的 si-qi.xyz Cookie"
                prepend-inner-icon="mdi-key-outline"
                :append-inner-icon="cookieVisible ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
                variant="outlined"
                density="comfortable"
                hide-details
                autocomplete="off"
                @click:append-inner="cookieVisible = !cookieVisible"
              />
              <div class="cookie-note">
                插件每次运行前都会自动读取 MoviePilot 的 si-qi.xyz Cookie；读取失败时才使用这里已保存的值。网络由系统自动选择 IPv4 或 IPv6。
              </div>
              <div class="cookie-actions">
                <v-btn color="teal" variant="tonal" :loading="syncingCookie" :disabled="formLocked" @click="syncCookie">
                  <v-icon icon="mdi-sync" size="18" class="mr-1" />立即同步站点 Cookie
                </v-btn>
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
  min-height: 100%;
  overflow-x: hidden;
  color: rgb(var(--v-theme-on-background));
}

.siqi-topbar {
  position: sticky;
  top: 0;
  z-index: 8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 62px;
  padding: 9px 16px;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-surface), .92);
  backdrop-filter: blur(14px);
}
.siqi-topbar__left,
.siqi-topbar__right,
.siqi-card__title,
.switch-main {
  display: flex;
  align-items: center;
}
.siqi-topbar__left { gap: 10px; min-width: 0; }
.siqi-topbar__right { flex: 0 0 auto; }
.siqi-topbar__copy { min-width: 0; }
.siqi-topbar__icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 13px;
  color: #16a34a;
  background: rgba(34, 197, 94, .13);
}
.siqi-topbar__title { font-size: 1.08rem; font-weight: 750; line-height: 1.25; }
.siqi-topbar__sub { margin-top: 2px; color: rgba(var(--v-theme-on-surface), .62); font-size: .78rem; }

.config-content { width: min(100%, 1120px); margin: 0 auto; padding: 14px 16px 26px; }
.siqi-toast { margin-bottom: 12px; }
.loading-state {
  display: grid;
  gap: 12px;
  padding: 28px 18px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 16px;
  color: rgba(var(--v-theme-on-surface), .68);
  background: rgb(var(--v-theme-surface));
}
.config-fieldset { min-width: 0; margin: 0; padding: 0; border: 0; }
.config-column { display: grid; gap: 12px; }
.siqi-card {
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 16px;
  background: rgb(var(--v-theme-surface));
  box-shadow: 0 6px 22px rgba(15, 23, 42, .055);
}
.siqi-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 44px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(var(--v-border-color), calc(var(--v-border-opacity) * .75));
}
.siqi-card__title { gap: 7px; font-size: .94rem; font-weight: 700; }

.switch-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; padding: 12px; }
.switch-grid--two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 74px;
  padding: 11px 12px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 14px;
  background: rgba(var(--v-theme-on-surface), .025);
  transition: border-color .18s ease, background .18s ease;
}
.switch-item--active { border-color: rgba(var(--accent), .46); background: rgba(var(--accent), .07); }
.switch-main { gap: 10px; min-width: 0; }
.switch-main > .v-icon { flex: 0 0 auto; color: rgb(var(--accent)); }
.switch-label { font-size: .84rem; font-weight: 700; }
.switch-desc { margin-top: 3px; color: rgba(var(--v-theme-on-surface), .58); font-size: .69rem; line-height: 1.35; }
.switch-item :deep(.v-input) { flex: 0 0 auto; }

.parameter-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding: 14px; }
.parameter-item { min-width: 0; }
.field-help { margin: 7px 4px 0; color: rgba(var(--v-theme-on-surface), .58); font-size: .69rem; line-height: 1.45; }
.siqi-number-input :deep(.v-field__input) { min-height: 48px; align-items: center; padding-top: 8px; padding-bottom: 8px; }
.siqi-number-input :deep(input) { align-self: center; line-height: 24px; text-align: center; }
.siqi-number-input :deep(.v-field__prepend-inner),
.siqi-number-input :deep(.v-field__append-inner) { align-self: center; padding-top: 0; }

.cookie-body { display: grid; gap: 9px; padding: 14px; }
.cookie-note { color: rgba(var(--v-theme-on-surface), .6); font-size: .72rem; line-height: 1.5; }
.cookie-actions { display: flex; justify-content: flex-end; }
.cookie-actions .v-btn { min-height: 44px; }

@media (prefers-reduced-motion: reduce) {
  .switch-item { transition: none; }
}

@media (max-width: 720px) {
  .siqi-topbar { align-items: flex-start; padding: 8px 10px; }
  .siqi-topbar__sub { display: none; }
  .siqi-topbar__icon { width: 38px; height: 38px; border-radius: 11px; }
  .config-content { padding: 10px 9px 22px; }
  .switch-grid,
  .switch-grid--two,
  .parameter-grid { grid-template-columns: 1fr; }
  .switch-grid { padding: 10px; }
  .switch-item { min-height: 70px; }
  .cookie-actions .v-btn { width: 100%; }
}
</style>
