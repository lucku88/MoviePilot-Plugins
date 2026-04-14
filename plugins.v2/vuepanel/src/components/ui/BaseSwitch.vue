<template>
  <div class="mp-switch-shell">
    <v-switch
      v-bind="$attrs"
      :model-value="modelValue"
      class="mp-switch"
      density="compact"
      hide-details
      inset
      @update:model-value="emit('update:modelValue', $event)"
    />
    <div v-if="hint" class="mp-switch-hint">{{ hint }}</div>
  </div>
</template>

<script setup>
defineOptions({ inheritAttrs: false })

defineProps({
  modelValue: { type: Boolean, default: false },
  hint: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<style scoped>
.mp-switch-shell {
  display: grid;
  gap: 6px;
}

.mp-switch-hint {
  font-size: var(--mp-font-xs);
  color: var(--mp-text-secondary);
  line-height: 1.5;
}

:deep(.mp-switch) {
  width: 100%;
  margin: 0;
}

:deep(.mp-switch .v-selection-control) {
  min-height: 28px;
}

:deep(.mp-switch .v-label) {
  opacity: 1;
  color: var(--mp-text-primary);
  font-size: var(--mp-font-sm);
  font-weight: 650;
}

:deep(.mp-switch .v-selection-control__wrapper) {
  width: 32px;
  height: 18px;
  margin-right: 6px;
}

:deep(.mp-switch .v-switch__track) {
  min-width: 32px;
  width: 32px;
  height: 18px;
  border-radius: 999px;
  color: var(--mp-color-primary);
}

:deep(.mp-switch .v-switch__thumb) {
  width: 12px;
  height: 12px;
}

:deep(.mp-switch .v-switch__track),
:deep(.mp-switch .v-selection-control--dirty .v-switch__track) {
  opacity: 1;
}
</style>
