<template>
  <section class="vpc-shell" :class="themeClass">
    <div class="vpc-card">
      <div class="vpc-kicker">Vue-面板</div>
      <h2 class="vpc-title">插件配置页已停用</h2>
      <p class="vpc-description">
        当前插件已经改为全部通过前端状态页里的功能卡片进行配置、执行、查看日志和复制，这个页面不再承担实际配置职责。
      </p>

      <div class="vpc-panel">
        <div class="vpc-panel-title">现在的使用方式</div>
        <p class="vpc-line">1. 进入插件状态页。</p>
        <p class="vpc-line">2. 直接在对应功能卡片上点“配置 / 日志 / 复制”。</p>
        <p class="vpc-line">3. 保存后会立即同步当前卡片的启用、定时、通知和站点参数。</p>
      </div>

      <div class="vpc-note">
        当前主题：{{ themeLabel || '自动适配' }}。无需在此页保存任何内容。
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  api: { type: Object, required: false, default: null },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
})

defineEmits(['close'])

const themeClass = computed(() => `vpc-theme--${props.themeName || 'light'}`)
</script>

<style scoped>
.vpc-shell {
  --vpc-surface: rgba(var(--v-theme-surface), 0.96);
  --vpc-surface-soft: rgba(var(--v-theme-surface), 0.92);
  --vpc-line: rgba(var(--v-border-color), 0.18);
  --vpc-line-strong: rgba(var(--v-theme-primary), 0.22);
  --vpc-shadow: 0 14px 32px rgba(var(--v-border-color), 0.16);
  --vpc-kicker: rgba(var(--v-theme-primary), 0.86);
  --vpc-title: rgba(var(--v-theme-on-surface), 0.96);
  --vpc-text: rgba(var(--v-theme-on-surface), 0.78);
  --vpc-muted: rgba(var(--v-theme-on-surface), 0.62);
  --vpc-bg:
    linear-gradient(180deg, rgba(var(--v-theme-primary), 0.05), transparent 42%),
    linear-gradient(to right, rgba(var(--v-theme-surface), 0.98), rgba(var(--v-theme-surface), 0.94));
  display: grid;
  place-items: center;
  min-height: 100%;
  padding: 24px;
}

.vpc-theme--dark,
.vpc-theme--transparent {
  --vpc-shadow: 0 16px 34px rgba(0, 0, 0, 0.28);
}

.vpc-card {
  width: min(720px, 100%);
  padding: 28px;
  border-radius: 24px;
  border: 1px solid var(--vpc-line);
  background: var(--vpc-bg);
  box-shadow: var(--vpc-shadow);
  position: relative;
  overflow: hidden;
}

.vpc-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 18%, rgba(var(--v-theme-primary), 0.08) 50%, transparent 82%);
  pointer-events: none;
}

.vpc-kicker {
  position: relative;
  z-index: 1;
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--vpc-kicker);
}

.vpc-title {
  position: relative;
  z-index: 1;
  margin: 0;
  font-size: 26px;
  line-height: 1.2;
  color: var(--vpc-title);
}

.vpc-description {
  position: relative;
  z-index: 1;
  margin: 14px 0 0;
  line-height: 1.7;
  color: var(--vpc-text);
}

.vpc-panel {
  position: relative;
  z-index: 1;
  margin-top: 18px;
  padding: 16px 18px;
  border-radius: 18px;
  border: 1px solid var(--vpc-line-strong);
  background: linear-gradient(to right, rgba(var(--v-theme-primary), 0.08), var(--vpc-surface-soft));
}

.vpc-panel-title {
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 700;
  color: var(--vpc-title);
}

.vpc-line {
  margin: 0;
  line-height: 1.8;
  color: var(--vpc-text);
}

.vpc-note {
  position: relative;
  z-index: 1;
  margin-top: 14px;
  color: var(--vpc-muted);
  font-size: 13px;
}

@media (max-width: 640px) {
  .vpc-shell {
    padding: 16px;
  }

  .vpc-card {
    padding: 22px 18px;
    border-radius: 20px;
  }

  .vpc-title {
    font-size: 22px;
  }
}
</style>
