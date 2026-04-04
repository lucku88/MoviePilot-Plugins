<template>
  <div class="sq-page">
    <div class="sq-shell">
      <section class="sq-hero">
        <div class="sq-hero-copy">
          <div class="sq-badge">SQ农场</div>
          <h1 class="sq-title">{{ farm.title || 'SQ农场' }}</h1>
          <p class="sq-subtitle">
            最近执行 {{ status.last_run || '暂无' }}，下次可收 {{ farm.next_run_time || '待识别' }}。
          </p>
        </div>
        <div class="sq-actions">
          <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
          <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新状态</v-btn>
          <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步 Cookie</v-btn>
          <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
          <v-btn variant="text" @click="closePlugin">关闭</v-btn>
        </div>
        <div class="sq-hero-meta">
          <div class="sq-meta-chip">计划触发 {{ farm.next_trigger_time || status.next_trigger_time || '等待下一次运行' }}</div>
          <div class="sq-meta-chip">Cookie {{ farm.cookie_source || status.cookie_source || '未同步' }}</div>
        </div>
      </section>

      <v-alert v-if="message.text" :type="message.type" variant="tonal">
        {{ message.text }}
      </v-alert>

      <section class="sq-stat-grid">
        <article v-for="item in farm.overview || []" :key="item.label" class="sq-stat-card">
          <div class="sq-stat-label">{{ item.label }}</div>
          <div class="sq-stat-value">{{ item.value }}</div>
        </article>
      </section>

      <section class="sq-grid sq-grid-top">
        <article class="sq-panel">
          <div class="sq-panel-head">
            <div>
              <div class="sq-panel-kicker">执行说明</div>
              <h2>动态调度</h2>
            </div>
          </div>
          <p class="sq-panel-text">
            {{ farm.page_note || '插件会先动态识别最近可收时间并记录下一次运行；如果当前还没有可收时间，会自动运行一次获取农场信息。' }}
          </p>
          <div class="sq-highlight-row">
            <div class="sq-highlight-pill">成熟 {{ farm.highlights?.ready_count || 0 }}</div>
            <div class="sq-highlight-pill">成长 {{ farm.highlights?.growing_count || 0 }}</div>
            <div class="sq-highlight-pill">空地 {{ farm.highlights?.empty_count || 0 }}</div>
            <div class="sq-highlight-pill">农场 {{ farm.highlights?.land_count || 0 }}</div>
          </div>
        </article>

        <article class="sq-panel" v-if="summaryLines.length">
          <div class="sq-panel-head">
            <div>
              <div class="sq-panel-kicker">本次摘要</div>
              <h2>任务结果</h2>
            </div>
          </div>
          <div class="sq-summary-list">
            <div v-for="line in summaryLines" :key="line" class="sq-summary-line">{{ line }}</div>
          </div>
        </article>
      </section>

      <section class="sq-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">收获背包</div>
            <h2>当前库存</h2>
          </div>
        </div>
        <div v-if="farm.inventory?.empty" class="sq-empty">{{ farm.inventory?.empty_text }}</div>
        <div v-else class="sq-bag-grid">
          <article v-for="item in farm.inventory?.items || []" :key="item.name" class="sq-bag-card">
            <div class="sq-bag-icon">{{ item.icon }}</div>
            <div class="sq-bag-name">{{ item.name }}</div>
            <div class="sq-bag-meta">数量 {{ item.quantity }}</div>
            <div class="sq-bag-meta">单价 {{ item.unit_reward }}</div>
            <div class="sq-bag-total">+{{ item.total_reward }} 魔力</div>
          </article>
        </div>
      </section>

      <section class="sq-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">种子商店</div>
            <h2>优先种植参考</h2>
          </div>
        </div>
        <div class="sq-seed-grid">
          <article
            v-for="seed in farm.seed_shop || []"
            :key="seed.id"
            class="sq-seed-card"
            :class="{ 'is-locked': !seed.unlocked, 'is-preferred': seed.preferred }"
          >
            <div class="sq-seed-icon">{{ seed.icon }}</div>
            <div class="sq-seed-name">{{ seed.name }}</div>
            <div class="sq-seed-line">消耗 {{ seed.cost }}</div>
            <div class="sq-seed-line">收获 {{ seed.reward }}</div>
            <div class="sq-seed-line">生长 {{ seed.grow_text }}</div>
            <div class="sq-seed-note">
              {{ seed.unlocked ? (seed.preferred ? '当前优先种子' : '已解锁') : seed.unlock_text }}
            </div>
          </article>
        </div>
      </section>

      <section class="sq-panel sq-farm-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">农场坑位</div>
            <h2>分组状态</h2>
          </div>
        </div>
        <div class="sq-land-stack">
          <article v-for="group in farm.land_groups || []" :key="group.id" class="sq-land-group">
            <header class="sq-group-head">
              <div class="sq-group-name">{{ group.name }}</div>
              <div class="sq-group-subtitle">{{ group.subtitle }}</div>
            </header>
            <div class="sq-slot-grid">
              <div
                v-for="slot in group.slots"
                :key="`${group.id}-${slot.slot_index}`"
                class="sq-slot"
                :class="`is-${slot.state}`"
              >
                <div class="sq-slot-icon">{{ slot.icon }}</div>
                <div class="sq-slot-name">{{ slot.title }}</div>
                <div class="sq-slot-badge">{{ slot.badge }}</div>
                <div class="sq-slot-desc">{{ slot.description }}</div>
                <div class="sq-slot-time">{{ slotText(slot) }}</div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="sq-panel">
        <div class="sq-panel-head">
          <div>
            <div class="sq-panel-kicker">最近记录</div>
            <h2>执行历史</h2>
          </div>
        </div>
        <div v-if="!historyItems.length" class="sq-empty">暂无执行记录</div>
        <div v-else class="sq-history-list">
          <article v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="sq-history-item">
            <div class="sq-history-top">
              <strong>{{ item.title }}</strong>
              <span>{{ item.time }}</span>
            </div>
            <div class="sq-history-lines">{{ (item.lines || []).join(' / ') }}</div>
          </article>
        </div>
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

const loading = ref(false)
const status = reactive({ farm_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const nowTs = ref(Math.floor(Date.now() / 1000))
let timer = null

const farm = computed(() => status.farm_status || {})
const historyItems = computed(() => status.history || farm.value.history || [])
const summaryLines = computed(() => (farm.value.summary || []).filter(Boolean))

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

async function loadStatus() {
  loading.value = true
  try {
    const res = await props.api.get('/plugin/SQFarm/status')
    Object.assign(status, res || {})
  } catch (error) {
    flash(error?.message || '加载状态失败', 'error')
  } finally {
    loading.value = false
  }
}

async function refreshData() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/refresh', {})
    flash(res.message || '已刷新')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '刷新失败', 'error')
  } finally {
    loading.value = false
  }
}

async function runNow() {
  loading.value = true
  try {
    const res = await props.api.post('/plugin/SQFarm/run', {})
    flash(res.message || '执行完成')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '执行失败', 'error')
  } finally {
    loading.value = false
  }
}

async function syncCookie() {
  loading.value = true
  try {
    const res = await props.api.get('/plugin/SQFarm/cookie')
    flash(res.message || 'Cookie 已同步')
    await loadStatus()
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error')
  } finally {
    loading.value = false
  }
}

function formatRemain(seconds) {
  const sec = Math.max(0, Number(seconds) || 0)
  if (!sec) return '现在可收'
  const hours = Math.floor(sec / 3600)
  const minutes = Math.floor((sec % 3600) / 60)
  const secs = sec % 60
  if (hours) return `${hours}小时${minutes}分钟`
  if (minutes) return `${minutes}分钟${secs}秒`
  return `${secs}秒`
}

function slotText(slot) {
  if (slot.harvest_ts) {
    const remain = slot.harvest_ts - nowTs.value
    if (slot.state === 'growing') return formatRemain(remain)
    if (slot.state === 'ready') return '现在可收'
  }
  return slot.remaining_label || slot.reward_text || ''
}

function closePlugin() {
  emit('close')
}

onMounted(async () => {
  await loadStatus()
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000)
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
.sq-page {
  --sq-bg: linear-gradient(180deg, #f5efe4 0%, #fbf8f2 45%, #f7f4ee 100%);
  --sq-surface: rgba(255, 255, 255, 0.82);
  --sq-surface-strong: rgba(255, 252, 246, 0.96);
  --sq-muted-surface: rgba(247, 239, 224, 0.72);
  --sq-border: rgba(169, 138, 81, 0.18);
  --sq-shadow: 0 20px 45px rgba(97, 75, 34, 0.08);
  --sq-text: #2f281d;
  --sq-subtle: #726754;
  --sq-soft: #8e846f;
  --sq-accent: #77b05d;
  --sq-accent-strong: #4f8d3a;
  --sq-accent-soft: rgba(119, 176, 93, 0.14);
  --sq-ready: linear-gradient(180deg, #d8ffd5 0%, #9fe0a5 100%);
  --sq-growing: linear-gradient(180deg, #fff2c2 0%, #ffd96b 100%);
  --sq-empty: linear-gradient(180deg, #eef8ea 0%, #e1f4db 100%);
  --sq-expand: linear-gradient(180deg, #edf7ef 0%, #dcedd9 100%);
  --sq-locked: linear-gradient(180deg, #eef1f4 0%, #e3e7eb 100%);
  min-height: 100%;
  padding: clamp(18px, 2.6vw, 30px);
  background: var(--sq-bg);
  color: var(--sq-text);
}

.sq-shell {
  max-width: 1320px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.sq-hero,
.sq-panel,
.sq-stat-card,
.sq-land-group {
  border: 1px solid var(--sq-border);
  box-shadow: var(--sq-shadow);
}

.sq-hero {
  position: relative;
  overflow: hidden;
  padding: clamp(22px, 3vw, 34px);
  border-radius: 30px;
  background:
    radial-gradient(circle at top right, rgba(136, 202, 115, 0.2), transparent 32%),
    radial-gradient(circle at bottom left, rgba(255, 208, 119, 0.18), transparent 28%),
    var(--sq-surface-strong);
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px 24px;
  align-items: start;
}

.sq-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--sq-accent-soft);
  color: var(--sq-accent-strong);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.sq-title {
  margin: 14px 0 8px;
  font-size: clamp(28px, 4vw, 38px);
  line-height: 1.05;
  font-weight: 900;
}

.sq-subtitle {
  margin: 0;
  max-width: 720px;
  color: var(--sq-subtle);
  line-height: 1.7;
  font-size: 14px;
}

.sq-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.sq-hero-meta {
  grid-column: 1 / -1;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.sq-meta-chip,
.sq-highlight-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 16px;
  background: var(--sq-muted-surface);
  color: var(--sq-subtle);
  border: 1px solid rgba(169, 138, 81, 0.12);
  font-size: 13px;
  font-weight: 600;
}

.sq-stat-grid,
.sq-grid {
  display: grid;
  gap: 18px;
}

.sq-stat-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.sq-grid-top {
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
}

.sq-stat-card {
  border-radius: 24px;
  padding: 20px;
  background: var(--sq-surface);
  backdrop-filter: blur(10px);
  text-align: center;
}

.sq-stat-label {
  color: var(--sq-soft);
  font-size: 13px;
}

.sq-stat-value {
  margin-top: 8px;
  font-size: clamp(28px, 3vw, 36px);
  font-weight: 900;
}

.sq-panel {
  border-radius: 28px;
  padding: 22px;
  background: var(--sq-surface);
  backdrop-filter: blur(10px);
}

.sq-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.sq-panel-kicker {
  color: var(--sq-soft);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sq-panel-head h2 {
  margin: 6px 0 0;
  font-size: 24px;
  line-height: 1.1;
  font-weight: 800;
}

.sq-panel-text {
  margin: 0;
  color: var(--sq-subtle);
  line-height: 1.8;
}

.sq-highlight-row,
.sq-summary-list,
.sq-history-list,
.sq-land-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.sq-summary-list,
.sq-history-list,
.sq-land-stack {
  flex-direction: column;
}

.sq-summary-line {
  padding: 14px 16px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(246, 239, 224, 0.9));
  border: 1px solid rgba(169, 138, 81, 0.12);
  color: var(--sq-text);
  font-weight: 600;
}

.sq-empty {
  padding: 42px 20px;
  text-align: center;
  color: var(--sq-soft);
  border-radius: 22px;
  background: var(--sq-muted-surface);
}

.sq-bag-grid,
.sq-seed-grid,
.sq-slot-grid {
  display: grid;
  gap: 14px;
}

.sq-bag-grid,
.sq-seed-grid {
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.sq-bag-card,
.sq-seed-card {
  padding: 18px 16px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255, 252, 246, 0.98), rgba(251, 244, 228, 0.88));
  border: 1px solid rgba(169, 138, 81, 0.16);
  text-align: center;
}

.sq-bag-icon,
.sq-seed-icon,
.sq-slot-icon {
  font-size: 30px;
  line-height: 1;
}

.sq-bag-name,
.sq-seed-name,
.sq-slot-name,
.sq-group-name {
  font-weight: 800;
}

.sq-bag-meta,
.sq-bag-total,
.sq-seed-line,
.sq-seed-note,
.sq-slot-badge,
.sq-slot-desc,
.sq-slot-time,
.sq-group-subtitle,
.sq-history-top span,
.sq-history-lines {
  color: var(--sq-subtle);
  font-size: 13px;
}

.sq-bag-total {
  margin-top: 8px;
  color: #d88918;
  font-weight: 800;
}

.sq-seed-card.is-locked {
  opacity: 0.56;
  filter: grayscale(0.22);
}

.sq-seed-card.is-preferred {
  background: linear-gradient(180deg, rgba(236, 251, 229, 0.98), rgba(225, 247, 215, 0.88));
  border-color: rgba(92, 166, 93, 0.32);
  box-shadow: inset 0 0 0 1px rgba(92, 166, 93, 0.08);
}

.sq-farm-panel {
  padding: 24px;
}

.sq-land-group {
  padding: 18px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.74), rgba(243, 238, 229, 0.82));
}

.sq-group-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
  margin-bottom: 14px;
}

.sq-group-subtitle {
  text-align: right;
}

.sq-slot-grid {
  grid-template-columns: repeat(auto-fit, minmax(128px, 1fr));
}

.sq-slot {
  min-height: 156px;
  padding: 14px 12px;
  border-radius: 22px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: center;
}

.sq-slot.is-growing { background: var(--sq-growing); }
.sq-slot.is-ready { background: var(--sq-ready); }
.sq-slot.is-empty { background: var(--sq-empty); }
.sq-slot.is-expand { background: var(--sq-expand); }
.sq-slot.is-locked { background: var(--sq-locked); }

.sq-slot-badge {
  font-weight: 700;
}

.sq-slot-time {
  font-weight: 800;
  color: var(--sq-text);
}

.sq-history-item {
  padding: 16px 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.84), rgba(246, 239, 224, 0.9));
  border: 1px solid rgba(169, 138, 81, 0.12);
}

.sq-history-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

@media (max-width: 1100px) {
  .sq-stat-grid,
  .sq-grid-top {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 900px) {
  .sq-hero {
    grid-template-columns: 1fr;
  }

  .sq-actions {
    justify-content: flex-start;
  }

  .sq-stat-grid,
  .sq-grid-top {
    grid-template-columns: 1fr;
  }

  .sq-group-head,
  .sq-panel-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .sq-group-subtitle {
    text-align: left;
  }
}

@media (prefers-color-scheme: dark) {
  .sq-page {
    --sq-bg: linear-gradient(180deg, #141818 0%, #101413 48%, #0c100f 100%);
    --sq-surface: rgba(24, 30, 29, 0.88);
    --sq-surface-strong: rgba(28, 35, 33, 0.95);
    --sq-muted-surface: rgba(53, 63, 58, 0.68);
    --sq-border: rgba(133, 157, 123, 0.18);
    --sq-shadow: 0 22px 50px rgba(0, 0, 0, 0.34);
    --sq-text: #edf3ea;
    --sq-subtle: #b9c4b4;
    --sq-soft: #8f9d91;
    --sq-accent: #9dd37b;
    --sq-accent-strong: #d1f0c2;
    --sq-accent-soft: rgba(119, 176, 93, 0.18);
    --sq-ready: linear-gradient(180deg, rgba(73, 123, 79, 0.94), rgba(58, 102, 67, 0.98));
    --sq-growing: linear-gradient(180deg, rgba(153, 116, 44, 0.96), rgba(122, 91, 30, 0.98));
    --sq-empty: linear-gradient(180deg, rgba(47, 82, 55, 0.82), rgba(36, 67, 43, 0.9));
    --sq-expand: linear-gradient(180deg, rgba(56, 76, 60, 0.86), rgba(39, 56, 44, 0.92));
    --sq-locked: linear-gradient(180deg, rgba(63, 71, 72, 0.88), rgba(47, 54, 55, 0.94));
  }

  .sq-summary-line,
  .sq-history-item,
  .sq-bag-card,
  .sq-seed-card,
  .sq-land-group {
    background: linear-gradient(180deg, rgba(28, 35, 33, 0.96), rgba(22, 27, 26, 0.92));
  }

  .sq-bag-total {
    color: #f2bf65;
  }
}

[data-theme="dark"] .sq-page,
[data-theme="purple"] .sq-page,
[data-theme="transparent"] .sq-page {
  --sq-bg: linear-gradient(180deg, #141818 0%, #101413 48%, #0c100f 100%);
  --sq-surface: rgba(24, 30, 29, 0.88);
  --sq-surface-strong: rgba(28, 35, 33, 0.95);
  --sq-muted-surface: rgba(53, 63, 58, 0.68);
  --sq-border: rgba(133, 157, 123, 0.18);
  --sq-shadow: 0 22px 50px rgba(0, 0, 0, 0.34);
  --sq-text: #edf3ea;
  --sq-subtle: #b9c4b4;
  --sq-soft: #8f9d91;
  --sq-accent: #9dd37b;
  --sq-accent-strong: #d1f0c2;
  --sq-accent-soft: rgba(119, 176, 93, 0.18);
  --sq-ready: linear-gradient(180deg, rgba(73, 123, 79, 0.94), rgba(58, 102, 67, 0.98));
  --sq-growing: linear-gradient(180deg, rgba(153, 116, 44, 0.96), rgba(122, 91, 30, 0.98));
  --sq-empty: linear-gradient(180deg, rgba(47, 82, 55, 0.82), rgba(36, 67, 43, 0.9));
  --sq-expand: linear-gradient(180deg, rgba(56, 76, 60, 0.86), rgba(39, 56, 44, 0.92));
  --sq-locked: linear-gradient(180deg, rgba(63, 71, 72, 0.88), rgba(47, 54, 55, 0.94));
}

[data-theme="dark"] .sq-summary-line,
[data-theme="dark"] .sq-history-item,
[data-theme="dark"] .sq-bag-card,
[data-theme="dark"] .sq-seed-card,
[data-theme="dark"] .sq-land-group,
[data-theme="purple"] .sq-summary-line,
[data-theme="purple"] .sq-history-item,
[data-theme="purple"] .sq-bag-card,
[data-theme="purple"] .sq-seed-card,
[data-theme="purple"] .sq-land-group,
[data-theme="transparent"] .sq-summary-line,
[data-theme="transparent"] .sq-history-item,
[data-theme="transparent"] .sq-bag-card,
[data-theme="transparent"] .sq-seed-card,
[data-theme="transparent"] .sq-land-group {
  background: linear-gradient(180deg, rgba(28, 35, 33, 0.96), rgba(22, 27, 26, 0.92));
}

[data-theme="dark"] .sq-bag-total,
[data-theme="purple"] .sq-bag-total,
[data-theme="transparent"] .sq-bag-total {
  color: #f2bf65;
}
</style>
