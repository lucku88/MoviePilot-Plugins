<template>
  <BasePanelCard
    kicker="执行记录"
    title="结构化日志"
    subtitle="支持按模块、状态和关键字筛选，适合快速定位失败、跳过和待处理任务。"
    tone="primary"
    class="log-board"
  >
    <template #actions>
      <div class="log-toolbar">
        <BaseInput v-model="keyword" label="搜索日志" placeholder="搜索任务 / 站点 / 结果" clearable />
        <v-select
          v-model="moduleFilter"
          class="log-select"
          :items="moduleOptions"
          label="模块"
          variant="outlined"
          density="comfortable"
          hide-details
        />
        <v-select
          v-model="statusFilter"
          class="log-select"
          :items="statusOptions"
          label="状态"
          variant="outlined"
          density="comfortable"
          hide-details
        />
      </div>
    </template>

    <EmptyState
      v-if="!filteredItems.length"
      title="暂无执行记录"
      description="执行完成后会按时间排序展示在这里。"
    />

    <VVirtualScroll
      v-else
      class="log-scroll mp-scroll"
      :items="filteredItems"
      :height="420"
      item-height="118"
    >
      <template #default="{ item }">
        <article class="log-item">
          <div class="log-top">
            <div class="log-title-wrap">
              <BaseTag :tone="tagTone(item.level)" size="sm" dot>{{ levelText(item.level) }}</BaseTag>
              <strong class="log-title">{{ item.title }}</strong>
            </div>
            <span class="log-time">{{ item.time }}</span>
          </div>

          <div class="log-meta">
            <span>{{ item.module_icon }} {{ item.module_name }}</span>
            <span v-if="item.site_name">{{ item.site_name }}</span>
            <span v-if="item.site_url">{{ item.site_url }}</span>
          </div>

          <div class="log-summary">{{ item.summary }}</div>

          <div class="log-actions">
            <BaseButton variant="ghost" size="sm" @click="toggle(item.id)">{{ expanded[item.id] ? '收起' : '详情' }}</BaseButton>
            <BaseButton variant="ghost" size="sm" @click="copyOne(item)">复制</BaseButton>
          </div>

          <div v-if="expanded[item.id]" class="log-detail">
            <div v-for="line in item.lines || []" :key="`${item.id}-${line}`" class="log-line">{{ line }}</div>
          </div>
        </article>
      </template>
    </VVirtualScroll>
  </BasePanelCard>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import BaseButton from '../ui/BaseButton.vue'
import BaseInput from '../ui/BaseInput.vue'
import BasePanelCard from '../ui/BasePanelCard.vue'
import BaseTag from '../ui/BaseTag.vue'
import EmptyState from '../ui/EmptyState.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const keyword = ref('')
const moduleFilter = ref('全部模块')
const statusFilter = ref('全部状态')
const expanded = reactive({})

const moduleOptions = computed(() => {
  const labels = Array.from(new Set(props.items.map((item) => item.module_name).filter(Boolean)))
  return ['全部模块', ...labels]
})

const statusOptions = ['全部状态', '成功', '异常', '警告', '信息']

const filteredItems = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  return props.items.filter((item) => {
    if (moduleFilter.value !== '全部模块' && item.module_name !== moduleFilter.value) return false
    if (statusFilter.value !== '全部状态' && levelText(item.level) !== statusFilter.value) return false
    if (!query) return true
    const text = [
      item.title,
      item.summary,
      item.module_name,
      item.site_name,
      item.site_url,
      ...(item.lines || []),
    ].join(' ').toLowerCase()
    return text.includes(query)
  })
})

function tagTone(level) {
  if (level === 'success') return 'success'
  if (level === 'error') return 'error'
  if (level === 'warning') return 'warning'
  return 'info'
}

function levelText(level) {
  return ({ success: '成功', error: '异常', warning: '警告', info: '信息' })[level] || '信息'
}

function toggle(id) {
  expanded[id] = !expanded[id]
}

async function copyText(text) {
  if (!text) return
  await navigator.clipboard?.writeText?.(text)
}

function copyOne(item) {
  return copyText(
    [
      `${item.module_icon || ''} ${item.module_name || ''} ${item.title || ''}`.trim(),
      item.summary || '',
      ...(item.lines || []),
    ].filter(Boolean).join('\n')
  )
}
</script>

<style scoped>
.log-toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.log-toolbar :deep(.mp-input) {
  min-width: 240px;
}

.log-select {
  min-width: 150px;
}

:deep(.log-select .v-field) {
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-card) 88%, transparent);
}

.log-scroll {
  border: 1px solid var(--mp-border-color);
  border-radius: var(--mp-radius-lg);
  background: color-mix(in srgb, var(--mp-bg-card) 84%, transparent);
}

.log-item {
  display: grid;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid color-mix(in srgb, var(--mp-border-color) 70%, transparent);
}

.log-item:last-child {
  border-bottom: 0;
}

.log-top,
.log-title-wrap,
.log-meta,
.log-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.log-top {
  justify-content: space-between;
  align-items: flex-start;
}

.log-title-wrap {
  align-items: center;
  min-width: 0;
}

.log-title {
  min-width: 0;
  font-size: var(--mp-font-md);
  line-height: 1.45;
  color: var(--mp-text-primary);
}

.log-time,
.log-meta span,
.log-summary,
.log-line {
  font-size: var(--mp-font-sm);
  line-height: 1.65;
  color: var(--mp-text-secondary);
}

.log-meta span {
  padding: 4px 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--mp-text-secondary) 8%, transparent);
}

.log-detail {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-soft) 60%, transparent);
}

@media (max-width: 760px) {
  .log-toolbar {
    width: 100%;
  }

  .log-toolbar :deep(.mp-input),
  .log-select {
    width: 100%;
    min-width: 0;
  }
}
</style>
