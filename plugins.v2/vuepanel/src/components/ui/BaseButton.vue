<template>
  <v-btn
    v-bind="$attrs"
    :class="['mp-btn', `is-${variant}`, `is-${size}`]"
    :variant="resolvedVariant"
    :loading="loading"
  >
    <slot />
  </v-btn>
</template>

<script setup>
import { computed } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  loading: { type: Boolean, default: false },
})

const resolvedVariant = computed(() => {
  if (props.variant === 'ghost') return 'text'
  return 'flat'
})
</script>

<style scoped>
.mp-btn {
  border-radius: var(--mp-radius-sm);
  font-weight: 800;
  letter-spacing: 0;
  text-transform: none;
  transition: transform .16s ease, box-shadow .16s ease, background-color .16s ease, color .16s ease;
}

.mp-btn:hover {
  transform: translateY(-1px);
}

.mp-btn.is-primary {
  background: var(--mp-color-primary);
  color: white;
  box-shadow: 0 10px 22px color-mix(in srgb, var(--mp-color-primary) 22%, transparent);
}

.mp-btn.is-secondary {
  background: color-mix(in srgb, var(--mp-color-primary) 10%, var(--mp-bg-card));
  color: var(--mp-color-primary);
}

.mp-btn.is-ghost {
  color: var(--mp-text-secondary);
}

.mp-btn.is-danger {
  background: color-mix(in srgb, var(--mp-color-danger) 88%, #f87171);
  color: white;
}

.mp-btn.is-sm {
  min-height: 32px;
  padding-inline: 11px;
  font-size: var(--mp-font-sm);
}

.mp-btn.is-md {
  min-height: 36px;
  padding-inline: 13px;
  font-size: var(--mp-font-md);
}
</style>
