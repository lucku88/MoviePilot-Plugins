<template>
  <span :class="['mp-tag', `is-${tone}`, `is-${size}`, { 'has-dot': dot }]">
    <span v-if="dot" class="mp-tag-dot" />
    <slot />
  </span>
</template>

<script setup>
defineProps({
  tone: { type: String, default: 'info' },
  size: { type: String, default: 'md' },
  dot: { type: Boolean, default: false },
})
</script>

<style scoped>
.mp-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  border: 1px solid transparent;
  font-weight: 700;
  white-space: nowrap;
}

.mp-tag-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: currentColor;
}

.mp-tag.is-sm {
  padding: 4px 8px;
  font-size: var(--mp-font-xs);
}

.mp-tag.is-md {
  padding: 6px 10px;
  font-size: var(--mp-font-sm);
}

.mp-tag.is-primary {
  background: color-mix(in srgb, var(--mp-color-primary) 14%, transparent);
  color: var(--mp-color-primary);
  border-color: color-mix(in srgb, var(--mp-color-primary) 24%, transparent);
}

.mp-tag.is-success {
  background: color-mix(in srgb, var(--mp-color-success) 16%, transparent);
  color: var(--mp-color-success);
  border-color: color-mix(in srgb, var(--mp-color-success) 28%, transparent);
}

.mp-tag.is-warning {
  background: color-mix(in srgb, var(--mp-color-warning) 18%, transparent);
  color: var(--mp-color-warning);
  border-color: color-mix(in srgb, var(--mp-color-warning) 28%, transparent);
}

.mp-tag.is-error,
.mp-tag.is-danger {
  background: color-mix(in srgb, var(--mp-color-danger) 14%, transparent);
  color: var(--mp-color-danger);
  border-color: color-mix(in srgb, var(--mp-color-danger) 26%, transparent);
}

.mp-tag.is-info {
  background: color-mix(in srgb, var(--mp-text-secondary) 12%, transparent);
  color: var(--mp-text-secondary);
  border-color: color-mix(in srgb, var(--mp-text-secondary) 18%, transparent);
}

.mp-tag.is-disabled {
  background: color-mix(in srgb, var(--mp-color-disabled) 16%, transparent);
  color: var(--mp-color-disabled);
  border-color: color-mix(in srgb, var(--mp-color-disabled) 26%, transparent);
}
</style>
