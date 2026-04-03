<template>
  <div class="sq-page">
    <div class="sq-toolbar">
      <div>
        <h1 class="sq-title">{{ farm.title || '思齐种菜赚魔力' }}</h1>
        <div class="sq-subtitle">最近执行 {{ status.last_run || '暂无' }} · 下次收菜 {{ farm.next_run_time || '待计算' }}</div>
      </div>
      <div class="sq-actions">
        <v-btn color="success" variant="flat" :loading="loading" @click="runNow">立即执行</v-btn>
        <v-btn color="primary" variant="flat" :loading="loading" @click="refreshData">刷新</v-btn>
        <v-btn color="warning" variant="flat" :loading="loading" @click="syncCookie">同步Cookie</v-btn>
        <v-btn variant="text" @click="emit('switch', 'config')">配置</v-btn>
        <v-btn variant="text" @click="closePlugin">关闭</v-btn>
      </div>
    </div>

    <v-alert v-if="message.text" :type="message.type" variant="tonal" class="mb-4">{{ message.text }}</v-alert>

    <div class="sq-stats">
      <div v-for="item in farm.overview || []" :key="item.label" class="sq-stat-card">
        <div class="sq-stat-label">{{ item.label }}</div>
        <div class="sq-stat-value">{{ item.value }}</div>
      </div>
    </div>

    <div class="sq-panel">
      <div class="sq-panel-head">
        <span>收获背包</span>
        <div class="sq-chip-row">
          <span class="sq-chip">成熟 {{ farm.highlights?.ready_count || 0 }}</span>
          <span class="sq-chip">成长 {{ farm.highlights?.growing_count || 0 }}</span>
          <span class="sq-chip">空地 {{ farm.highlights?.empty_count || 0 }}</span>
          <span class="sq-chip">{{ farm.cookie_source || status.cookie_source || '未同步 Cookie' }}</span>
        </div>
      </div>
      <div v-if="farm.inventory?.empty" class="sq-empty">{{ farm.inventory?.empty_text }}</div>
      <div v-else class="sq-bag-grid">
        <div v-for="item in farm.inventory?.items || []" :key="item.name" class="sq-bag-card">
          <div class="sq-bag-icon">{{ item.icon }}</div>
          <div class="sq-bag-name">{{ item.name }}</div>
          <div class="sq-bag-meta">数量 {{ item.quantity }}</div>
          <div class="sq-bag-meta">单价 {{ item.unit_reward }}</div>
          <div class="sq-bag-total">+{{ item.total_reward }} 魔力</div>
        </div>
      </div>
    </div>

    <div class="sq-panel">
      <div class="sq-panel-head">
        <span>种子商店</span>
        <div class="sq-submeta">计划触发 {{ farm.next_trigger_time || status.next_trigger_time || '等待轮询' }}</div>
      </div>
      <div class="sq-seed-grid">
        <div v-for="seed in farm.seed_shop || []" :key="seed.id" class="sq-seed-card" :class="{ 'is-locked': !seed.unlocked, 'is-preferred': seed.preferred }">
          <div class="sq-seed-icon">{{ seed.icon }}</div>
          <div class="sq-seed-name">{{ seed.name }}</div>
          <div class="sq-seed-line">消耗：{{ seed.cost }}</div>
          <div class="sq-seed-line">收获：{{ seed.reward }}</div>
          <div class="sq-seed-line">生长：{{ seed.grow_text }}</div>
          <div class="sq-seed-note">{{ seed.unlocked ? (seed.preferred ? '当前优先种子' : '已解锁') : seed.unlock_text }}</div>
        </div>
      </div>
    </div>

    <div class="sq-farm-shell">
      <div v-for="group in farm.land_groups || []" :key="group.id" class="sq-land-group">
        <div class="sq-group-title">{{ group.name }} <span>{{ group.subtitle }}</span></div>
        <div class="sq-slot-grid">
          <div v-for="slot in group.slots" :key="`${group.id}-${slot.slot_index}`" class="sq-slot" :class="`is-${slot.state}`">
            <div class="sq-slot-icon">{{ slot.icon }}</div>
            <div class="sq-slot-name">{{ slot.title }}</div>
            <div class="sq-slot-badge">{{ slot.badge }}</div>
            <div class="sq-slot-desc">{{ slot.description }}</div>
            <div class="sq-slot-time">{{ slotText(slot) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="sq-panel">
      <div class="sq-panel-head"><span>最近记录</span></div>
      <div v-if="!(historyItems.length)" class="sq-empty">暂无执行记录</div>
      <div v-else class="sq-history-list">
        <div v-for="item in historyItems" :key="`${item.time}-${item.title}`" class="sq-history-item">
          <div class="sq-history-top">
            <strong>{{ item.title }}</strong>
            <span>{{ item.time }}</span>
          </div>
          <div class="sq-history-lines">{{ (item.lines || []).join(' / ') }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const props = defineProps({ api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } })
const emit = defineEmits(['switch', 'close'])

const loading = ref(false)
const status = reactive({ farm_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const nowTs = ref(Math.floor(Date.now() / 1000))
let timer = null

const farm = computed(() => status.farm_status || {})
const historyItems = computed(() => status.history || farm.value.history || [])

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
    flash(res.message || '已同步 Cookie')
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
  if (hours) return `${hours}小时${minutes}分`
  if (minutes) return `${minutes}分${secs}秒`
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
.sq-page { color: #2b2b2b; }
.sq-toolbar { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 20px; }
.sq-title { margin: 0; font-size: 30px; font-weight: 800; }
.sq-subtitle, .sq-submeta { color: #6e6a60; font-size: 13px; }
.sq-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.sq-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 18px; }
.sq-stat-card, .sq-panel, .sq-land-group { background: rgba(255,255,255,0.9); border-radius: 24px; box-shadow: 0 10px 30px rgba(160,123,55,0.08); border: 1px solid rgba(219,205,181,0.7); }
.sq-stat-card { padding: 18px 20px; text-align: center; }
.sq-stat-label { color: #8a826d; font-size: 13px; }
.sq-stat-value { font-size: 28px; font-weight: 800; margin-top: 6px; }
.sq-panel { padding: 20px; margin-bottom: 18px; }
.sq-panel-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 16px; font-size: 22px; font-weight: 800; }
.sq-chip-row { display: flex; gap: 8px; flex-wrap: wrap; }
.sq-chip { padding: 6px 12px; border-radius: 999px; background: #f4efe3; color: #7d7259; font-size: 12px; }
.sq-empty { padding: 36px 0; text-align: center; color: #9e9a90; }
.sq-bag-grid, .sq-seed-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 14px; }
.sq-bag-card, .sq-seed-card { padding: 18px 14px; border-radius: 20px; background: #fffaf0; border: 1px solid #f0ddaa; text-align: center; }
.sq-bag-icon, .sq-seed-icon { font-size: 28px; margin-bottom: 6px; }
.sq-bag-name, .sq-seed-name { font-weight: 700; }
.sq-bag-meta, .sq-seed-line, .sq-seed-note { font-size: 12px; color: #766d5c; margin-top: 4px; }
.sq-bag-total { margin-top: 6px; font-weight: 700; color: #db8a00; }
.sq-seed-card.is-locked { opacity: 0.45; filter: grayscale(0.3); }
.sq-seed-card.is-preferred { box-shadow: 0 10px 24px rgba(111, 202, 151, 0.24); border-color: #78d49d; }
.sq-farm-shell { background: rgba(245, 245, 245, 0.6); border: 1px solid rgba(158,158,158,0.25); border-radius: 28px; padding: 16px; margin-bottom: 18px; }
.sq-land-group { padding: 18px; margin-bottom: 14px; }
.sq-land-group:last-child { margin-bottom: 0; }
.sq-group-title { font-size: 20px; font-weight: 800; margin-bottom: 12px; }
.sq-group-title span { font-size: 13px; color: #7a7365; margin-left: 8px; font-weight: 500; }
.sq-slot-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; }
.sq-slot { min-height: 150px; border-radius: 22px; padding: 14px 12px; text-align: center; border: 1px solid transparent; display: flex; flex-direction: column; justify-content: space-between; }
.sq-slot.is-growing { background: linear-gradient(180deg, #fff4ba 0%, #ffe188 100%); border-color: #f0cc5b; }
.sq-slot.is-ready { background: linear-gradient(180deg, #d8ffd5 0%, #9ae2a2 100%); border-color: #76c580; }
.sq-slot.is-empty { background: #eef9ea; border-color: #9ed1a7; }
.sq-slot.is-expand { background: #eef7ef; border-color: #7ccd88; }
.sq-slot.is-locked { background: #edf0f2; border-color: #c9d0d6; color: #9ca3aa; }
.sq-slot-icon { font-size: 30px; }
.sq-slot-name { font-weight: 800; }
.sq-slot-badge, .sq-slot-desc, .sq-slot-time { font-size: 12px; }
.sq-slot-time { font-weight: 700; color: #6e5e3d; }
.sq-history-list { display: flex; flex-direction: column; gap: 12px; }
.sq-history-item { padding: 14px 16px; background: #f8f5ef; border-radius: 18px; border: 1px solid #ebe3d2; }
.sq-history-top { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 6px; }
.sq-history-top span, .sq-history-lines { color: #746f62; font-size: 13px; }
@media (max-width: 900px) { .sq-toolbar, .sq-panel-head { flex-direction: column; align-items: stretch; } }
</style>
