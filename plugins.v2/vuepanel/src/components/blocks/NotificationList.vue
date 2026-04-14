<template>
  <BasePanelCard
    kicker="通知区"
    title="最新通知"
    subtitle="聚合最近的执行结果，优先展示需要关注的变化和异常。"
    tone="violet"
    class="notify-board"
  >
    <template #actions>
      <div class="notify-toolbar">
        <BaseInput v-model="keyword" label="搜索通知" placeholder="搜索模块 / 站点 / 结果" clearable />
        <BaseButton variant="ghost" size="sm" @click="copyAll">复制摘要</BaseButton>
      </div>
    </template>

    <EmptyState
      v-if="!filteredItems.length"
      title="暂无通知"
      description="新的执行结果会以卡片列表的形式显示在这里。"
    />

    <VVirtualScroll
      v-else
      class="notify-scroll mp-scroll"
      :items="filteredItems"
      :height="360"
      item-height="120"
    >
      <template #default="{ item }">
        <article class="notify-item">
          <div class="notify-item-top">
            <div class="notify-title-wrap">
              <BaseTag :tone="tagTone(item.level)" size="sm" dot>{{ levelText(item.level) }}</BaseTag>
              <strong class="notify-title">{{ item.title }}</strong>
            </div>
            <span class="notify-time">{{ item.time }}</span>
          </div>

          <div class="notify-summary">{{ item.summary }}</div>

          <div v-if="item.parts?.length" class="notify-parts">
            <span v-for="part in item.parts" :key="`${item.id}-${part.label}`" class="notify-part">{{ part.label }}：{{ part.value }}</span>
          </div>

          <div class="notify-actions">
            <BaseTag tone="primary" size="sm">{{ item.module_icon }} {{ item.module_name }}</BaseTag>
            <BaseButton variant="ghost" size="sm" @click="toggle(item.id)">{{ expanded[item.id] ? '收起' : '详情' }}</BaseButton>
            <BaseButton variant="ghost" size="sm" @click="copyOne(item)">复制</BaseButton>
          </div>

          <div v-if="expanded[item.id]" class="notify-detail">
            <div v-for="line in item.detail_lines || []" :key="`${item.id}-${line}`" class="notify-line">{{ line }}</div>
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
const expanded = reactive({})

const filteredItems = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  if (!query) return props.items
  return props.items.filter((item) => {
    const text = [
      item.title,
      item.summary,
      item.module_name,
      item.site_name,
      ...(item.detail_lines || []),
      ...((item.parts || []).map((part) => `${part.label} ${part.value}`)),
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

function formatItem(item) {
  return [
    `${item.module_icon || ''} ${item.module_name || ''} ${item.title || ''}`.trim(),
    item.summary || '',
    ...(item.detail_lines || []),
  ].filter(Boolean).join('\n')
}

function copyOne(item) {
  return copyText(formatItem(item))
}

function copyAll() {
  return copyText(filteredItems.value.map(formatItem).join('\n\n'))
}
</script>

<style scoped>
.notify-board {
  min-height: 100%;
}

.notify-toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.notify-toolbar :deep(.mp-input) {
  min-width: 240px;
}

.notify-scroll {
  border: 1px solid var(--mp-border-color);
  border-radius: var(--mp-radius-lg);
  background: color-mix(in srgb, var(--mp-bg-card) 84%, transparent);
}

.notify-item {
  display: grid;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid color-mix(in srgb, var(--mp-border-color) 70%, transparent);
}

.notify-item:last-child {
  border-bottom: 0;
}

.notify-item-top,
.notify-title-wrap,
.notify-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.notify-item-top {
  justify-content: space-between;
  align-items: flex-start;
}

.notify-title-wrap {
  align-items: center;
  min-width: 0;
}

.notify-title {
  min-width: 0;
  font-size: var(--mp-font-md);
  line-height: 1.45;
  color: var(--mp-text-primary);
}

.notify-time,
.notify-summary,
.notify-part,
.notify-line {
  font-size: var(--mp-font-sm);
  line-height: 1.65;
  color: var(--mp-text-secondary);
}

.notify-parts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.notify-part {
  padding: 5px 8px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--mp-text-secondary) 8%, transparent);
}

.notify-actions {
  align-items: center;
}

.notify-detail {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: var(--mp-radius-md);
  background: color-mix(in srgb, var(--mp-bg-soft) 60%, transparent);
}

@media (max-width: 760px) {
  .notify-toolbar {
    width: 100%;
  }

  .notify-toolbar :deep(.mp-input) {
    width: 100%;
    min-width: 0;
  }
}
</style>
