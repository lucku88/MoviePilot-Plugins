<template>
  <section :class="['mp-card', `is-${tone}`, { compact }]">
    <div v-if="$slots.header || title || kicker || $slots.actions" class="mp-card-head">
      <div class="mp-card-copy">
        <slot name="header">
          <div v-if="kicker" class="mp-card-kicker">{{ kicker }}</div>
          <h3 v-if="title" class="mp-card-title">{{ title }}</h3>
          <p v-if="subtitle" class="mp-card-subtitle">{{ subtitle }}</p>
        </slot>
      </div>
      <div v-if="$slots.actions" class="mp-card-actions">
        <slot name="actions" />
      </div>
    </div>

    <div class="mp-card-body">
      <slot />
    </div>

    <div v-if="$slots.footer" class="mp-card-footer">
      <slot name="footer" />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  kicker: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  tone: { type: String, default: 'default' },
  compact: { type: Boolean, default: false },
})
</script>

<style scoped>
.mp-card {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: 10px;
  padding: 12px 14px;
  border: 1px solid var(--mp-border-color);
  border-radius: var(--mp-radius-xl);
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--mp-card-accent, var(--mp-color-primary)) 7%, transparent), transparent 42%),
    var(--mp-bg-panel-strong);
  box-shadow: var(--mp-shadow-card);
  backdrop-filter: blur(16px);
}

.mp-card::before {
  content: '';
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 3px;
  background: color-mix(in srgb, var(--mp-card-accent, var(--mp-color-primary)) 40%, transparent);
}

.mp-card::after {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: calc(var(--mp-radius-xl) - 2px);
  border: 1px solid color-mix(in srgb, white 28%, transparent);
  pointer-events: none;
}

.mp-card.is-default {
  --mp-card-accent: var(--mp-color-primary);
}

.mp-card.is-primary,
.mp-card.is-azure {
  --mp-card-accent: var(--mp-color-primary);
}

.mp-card.is-emerald,
.mp-card.is-success {
  --mp-card-accent: var(--mp-color-success);
}

.mp-card.is-amber,
.mp-card.is-warning {
  --mp-card-accent: var(--mp-color-warning);
}

.mp-card.is-rose,
.mp-card.is-danger,
.mp-card.is-error {
  --mp-card-accent: var(--mp-color-danger);
}

.mp-card.is-violet,
.mp-card.is-purple {
  --mp-card-accent: var(--mp-color-secondary);
}

.mp-card.compact {
  gap: 8px;
  padding: 10px 12px;
}

.mp-card-head,
.mp-card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mp-card-head {
  justify-content: space-between;
  align-items: flex-start;
}

.mp-card-copy {
  min-width: 0;
}

.mp-card-kicker {
  font-size: var(--mp-font-xs);
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--mp-card-accent);
}

.mp-card-title {
  margin: 2px 0 0;
  font-size: var(--mp-font-xl);
  font-weight: 900;
  letter-spacing: -.02em;
  color: var(--mp-text-primary);
}

.mp-card-subtitle {
  margin: 4px 0 0;
  color: var(--mp-text-secondary);
  font-size: var(--mp-font-sm);
  line-height: 1.55;
}

.mp-card-body,
.mp-card-footer {
  min-width: 0;
}
</style>
