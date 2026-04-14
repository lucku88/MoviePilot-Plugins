<template>
  <BasePanelCard :tone="tone" compact class="mp-stat-card">
    <div class="mp-stat-label">{{ label }}</div>
    <div class="mp-stat-value">{{ value }}</div>
    <div v-if="hint" class="mp-stat-hint">{{ hint }}</div>
  </BasePanelCard>
</template>

<script setup>
import BasePanelCard from './BasePanelCard.vue'

defineProps({
  label: { type: String, default: '' },
  value: { type: [String, Number], default: '' },
  hint: { type: String, default: '' },
  tone: { type: String, default: 'default' },
})
</script>

<style scoped>
.mp-stat-card {
  gap: 4px;
}

.mp-stat-label {
  color: var(--mp-text-secondary);
  font-size: var(--mp-font-sm);
  font-weight: 700;
}

.mp-stat-value {
  font-size: clamp(22px, 2.4vw, 28px);
  line-height: 1;
  font-weight: 900;
  letter-spacing: -.03em;
  color: var(--mp-text-primary);
}

.mp-stat-hint {
  color: var(--mp-text-secondary);
  font-size: var(--mp-font-xs);
}
</style>
