<template>
  <div class="mp-empty">
    <strong class="mp-empty-title">{{ title }}</strong>
    <div v-if="description" class="mp-empty-text">{{ description }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '暂无内容' },
  description: { type: String, default: '' },
})
</script>

<style scoped>
.mp-empty {
  padding: 18px 16px;
  border: 1px dashed var(--mp-border-color);
  border-radius: var(--mp-radius-lg);
  background: color-mix(in srgb, var(--mp-bg-card) 86%, transparent);
  color: var(--mp-text-secondary);
  text-align: center;
}

.mp-empty-title {
  display: block;
  color: var(--mp-text-primary);
  font-size: var(--mp-font-md);
}

.mp-empty-text {
  margin-top: 6px;
  font-size: var(--mp-font-sm);
  line-height: 1.6;
}
</style>
