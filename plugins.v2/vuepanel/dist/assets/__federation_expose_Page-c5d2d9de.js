import { importShared } from './__federation_fn_import-b37dd681.js';

const BaseCronField_vue_vue_type_style_index_0_scoped_1ed25d38_lang = '';

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

const {resolveComponent:_resolveComponent$1,mergeProps:_mergeProps,openBlock:_openBlock$1,createBlock:_createBlock$1} = await importShared('vue');



const _sfc_main$1 = /*#__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'BaseCronField',
  props: {
  modelValue: { type: String, default: '' },
},
  emits: ['update:modelValue'],
  setup(__props, { emit }) {







return (_ctx, _cache) => {
  const _component_VCronField = _resolveComponent$1("VCronField");

  return (_openBlock$1(), _createBlock$1(_component_VCronField, _mergeProps(_ctx.$attrs, {
    "model-value": __props.modelValue,
    class: "mp-cron",
    density: "compact",
    "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => (emit('update:modelValue', $event)))
  }), null, 16, ["model-value"]))
}
}

});
const BaseCronField = /*#__PURE__*/_export_sfc(_sfc_main$1, [['__scopeId',"data-v-1ed25d38"]]);

const {computed: computed$1,onBeforeUnmount: onBeforeUnmount$1,onMounted: onMounted$1,reactive: reactive$1,ref: ref$1} = await importShared('vue');


const THEME_MAP = [
  { match: /transparent|glass|blur|透明/i, value: 'transparent', label: '透明' },
  { match: /purple|violet|fantasy|幻紫/i, value: 'purple', label: '幻紫' },
  { match: /dark|night|深色/i, value: 'dark', label: '深色' },
  { match: /light|浅色/i, value: 'light', label: '浅色' },
];

function parseColorToken(value, fallback) {
  const text = String(value || '').trim();
  if (!text) return fallback
  if (/^\d+\s*,\s*\d+\s*,\s*\d+/.test(text)) return `rgb(${text})`
  return text
}

function luminanceFromColor(color) {
  const match = String(color || '').match(/rgba?\(([^)]+)\)/i);
  if (!match) return 255
  const [r, g, b] = match[1].split(',').slice(0, 3).map((item) => Number.parseFloat(item.trim()) || 0);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function hasThemeHint(className = '') {
  return className.includes('theme')
    || className.includes('v-theme--')
    || className.includes('dark')
    || className.includes('light')
    || className.includes('purple')
    || className.includes('transparent')
}

function isInternalThemeNode(node) {
  const className = String(node?.className || '').toLowerCase();
  return className.includes('mp-theme-')
    || className.includes('vpp-theme-')
    || className.includes('mp-panel')
    || className.includes('vuepanel-page')
}

function usePanelTheme(rootEl) {
  const themeName = ref$1('light');
  const themeLabel = ref$1('浅色');
  const themeStyle = reactive$1({});

  let themeObserver = null;
  let mediaQuery = null;

  function resolveThemeNode() {
    let current = rootEl?.value?.parentElement || rootEl?.value;
    while (current) {
      if (!isInternalThemeNode(current) && current.getAttribute?.('data-theme')) return current
      const className = String(current.className || '').toLowerCase();
      if (!isInternalThemeNode(current) && hasThemeHint(className)) return current
      current = current.parentElement;
    }

    const body = document.body;
    const root = document.documentElement;
    if (body && !isInternalThemeNode(body)) {
      const bodyClass = String(body.className || '').toLowerCase();
      if (body.getAttribute?.('data-theme') || hasThemeHint(bodyClass)) return body
    }
    if (root && !isInternalThemeNode(root)) {
      const rootClass = String(root.className || '').toLowerCase();
      if (root.getAttribute?.('data-theme') || hasThemeHint(rootClass)) return root
    }
    return body || root
  }

  function resolveThemeValue(node) {
    const raw = `${node?.getAttribute?.('data-theme') || ''} ${node?.className || ''}`.trim();
    for (const item of THEME_MAP) {
      if (item.match.test(raw)) return item
    }
    return null
  }

  function readHostColor(node, names, fallback) {
    const style = window.getComputedStyle(node);
    for (const name of names) {
      const value = style.getPropertyValue(name);
      if (value) return parseColorToken(value, fallback)
    }
    return fallback
  }

  function updateTheme() {
    const node = resolveThemeNode();
    const detected = resolveThemeValue(node);
    const style = window.getComputedStyle(node);
    const pageBg = parseColorToken(style.backgroundColor, '#eef3fb');
    const text = parseColorToken(style.color, '#182132');
    const prefersDark = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;

    if (detected) {
      themeName.value = detected.value;
      themeLabel.value = detected.label;
    } else {
      const bgLuminance = luminanceFromColor(pageBg);
      themeName.value = bgLuminance < 140 || prefersDark ? 'dark' : 'custom';
      themeLabel.value = themeName.value === 'dark' ? '深色' : '自定义';
    }

    themeStyle['--mp-host-primary'] = readHostColor(node, ['--v-theme-primary', '--theme-primary'], '#4f86ff');
    themeStyle['--mp-host-secondary'] = readHostColor(node, ['--v-theme-secondary', '--theme-secondary'], '#8b5cf6');
    themeStyle['--mp-host-surface'] = readHostColor(node, ['--v-theme-surface', '--theme-surface'], '#ffffff');
    themeStyle['--mp-host-background'] = readHostColor(node, ['--v-theme-background', '--theme-background'], pageBg);
    themeStyle['--mp-host-on-surface'] = readHostColor(node, ['--v-theme-on-surface', '--theme-on-surface'], text);
    themeStyle['--mp-host-muted'] = readHostColor(node, ['--v-theme-on-surface-variant', '--theme-muted'], '#64748b');
    themeStyle['--mp-host-outline'] = readHostColor(node, ['--v-border-color', '--theme-border'], 'rgba(15, 23, 42, 0.14)');
  }

  function bindThemeObserver() {
    updateTheme();
    if (window.MutationObserver) {
      themeObserver = new MutationObserver(updateTheme)
      ;[resolveThemeNode(), document.documentElement, document.body].filter(Boolean).forEach((node) => {
        themeObserver.observe(node, { attributes: true, attributeFilter: ['data-theme', 'class', 'style'] });
      });
    }
    if (window.matchMedia) {
      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener?.('change', updateTheme);
    }
  }

  onMounted$1(bindThemeObserver);
  onBeforeUnmount$1(() => {
    themeObserver?.disconnect?.();
    mediaQuery?.removeEventListener?.('change', updateTheme);
  });

  return {
    themeName,
    themeLabel,
    themeStyle,
    themeClass: computed$1(() => `mp-theme-${themeName.value}`),
  }
}

const Page_vue_vue_type_style_index_0_scoped_757c56d0_lang = '';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-757c56d0"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vpp-shell" };
const _hoisted_2 = { class: "vpp-control-panel" };
const _hoisted_3 = { class: "vpp-panel-left" };
const _hoisted_4 = { class: "vpp-panel-right" };
const _hoisted_5 = { class: "vpp-toolbar-badge" };
const _hoisted_6 = { class: "vpp-stat-grid" };
const _hoisted_7 = { class: "vpp-stat-icon-wrap" };
const _hoisted_8 = { class: "vpp-stat-copy" };
const _hoisted_9 = { class: "vpp-stat-value" };
const _hoisted_10 = { class: "vpp-stat-label" };
const _hoisted_11 = { class: "vpp-card-grid" };
const _hoisted_12 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-card-glow" }, null, -1));
const _hoisted_13 = { class: "vpp-card-head" };
const _hoisted_14 = { class: "vpp-logo-wrap" };
const _hoisted_15 = ["src", "alt", "onError"];
const _hoisted_16 = {
  key: 1,
  class: "vpp-logo-fallback"
};
const _hoisted_17 = { class: "vpp-card-copy" };
const _hoisted_18 = { class: "vpp-card-title-row" };
const _hoisted_19 = { class: "vpp-card-title-group" };
const _hoisted_20 = { class: "vpp-card-title" };
const _hoisted_21 = { class: "vpp-card-desc" };
const _hoisted_22 = { class: "vpp-card-meta" };
const _hoisted_23 = { class: "vpp-card-meta-item" };
const _hoisted_24 = { class: "vpp-card-meta-item" };
const _hoisted_25 = {
  key: 0,
  class: "vpp-card-body"
};
const _hoisted_26 = { class: "vpp-card-note" };
const _hoisted_27 = { class: "vpp-action-row" };
const _hoisted_28 = {
  key: 0,
  class: "vpp-empty-state vpp-grid-empty"
};
const _hoisted_29 = { class: "vpp-dialog-head" };
const _hoisted_30 = { class: "vpp-dialog-title-wrap" };
const _hoisted_31 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-kicker" }, "配置", -1));
const _hoisted_32 = { class: "vpp-dialog-title" };
const _hoisted_33 = { class: "vpp-dialog-body" };
const _hoisted_34 = { class: "vpp-dialog-meta" };
const _hoisted_35 = { class: "vpp-meta-chip" };
const _hoisted_36 = { class: "vpp-meta-chip" };
const _hoisted_37 = { class: "vpp-dialog-panel" };
const _hoisted_38 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-section-title" }, "开关", -1));
const _hoisted_39 = { class: "vpp-switch-grid" };
const _hoisted_40 = { class: "vpp-switch-card" };
const _hoisted_41 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-switch-label" }, "启用功能", -1));
const _hoisted_42 = { class: "vpp-switch-card" };
const _hoisted_43 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-switch-label" }, "定时执行", -1));
const _hoisted_44 = { class: "vpp-switch-card" };
const _hoisted_45 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-switch-label" }, "发送通知", -1));
const _hoisted_46 = { class: "vpp-switch-card is-emphasis" };
const _hoisted_47 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-switch-label" }, "立即运行一次", -1));
const _hoisted_48 = { class: "vpp-dialog-panel" };
const _hoisted_49 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-section-title" }, "基础设置", -1));
const _hoisted_50 = { class: "vpp-form-grid" };
const _hoisted_51 = { class: "vpp-dialog-actions" };
const _hoisted_52 = { class: "vpp-dialog-actions-left" };
const _hoisted_53 = { class: "vpp-dialog-actions-right" };
const _hoisted_54 = { class: "vpp-dialog-head" };
const _hoisted_55 = { class: "vpp-dialog-title-wrap" };
const _hoisted_56 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-kicker" }, "日志", -1));
const _hoisted_57 = { class: "vpp-dialog-title" };
const _hoisted_58 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-log-state" }, [
  /*#__PURE__*/_createElementVNode("span", { class: "vpp-live-dot" }),
  /*#__PURE__*/_createElementVNode("span", null, "实时轮询中")
], -1));
const _hoisted_59 = { class: "vpp-dialog-body" };
const _hoisted_60 = { class: "vpp-dialog-meta" };
const _hoisted_61 = { class: "vpp-meta-chip" };
const _hoisted_62 = { class: "vpp-meta-chip" };
const _hoisted_63 = { class: "vpp-meta-chip" };
const _hoisted_64 = { class: "vpp-dialog-panel vpp-log-panel" };
const _hoisted_65 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-section-title" }, "日志列表", -1));
const _hoisted_66 = {
  key: 0,
  class: "vpp-empty-state"
};
const _hoisted_67 = {
  key: 1,
  class: "vpp-log-table"
};
const _hoisted_68 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-log-table-head" }, [
  /*#__PURE__*/_createElementVNode("span", null, "时间"),
  /*#__PURE__*/_createElementVNode("span", null, "状态"),
  /*#__PURE__*/_createElementVNode("span", null, "详情")
], -1));
const _hoisted_69 = { class: "vpp-log-table-body mp-scroll" };
const _hoisted_70 = { class: "vpp-log-time" };
const _hoisted_71 = { class: "vpp-log-status" };
const _hoisted_72 = { class: "vpp-log-detail" };
const _hoisted_73 = { class: "vpp-log-summary" };
const _hoisted_74 = {
  key: 0,
  class: "vpp-log-lines"
};
const _hoisted_75 = { class: "vpp-dialog-actions" };
const _hoisted_76 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-dialog-actions-left" }, null, -1));
const _hoisted_77 = { class: "vpp-dialog-actions-right" };
const _hoisted_78 = { class: "vpp-dialog-head" };
const _hoisted_79 = { class: "vpp-dialog-title-wrap" };
const _hoisted_80 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-kicker" }, "复制", -1));
const _hoisted_81 = { class: "vpp-dialog-title" };
const _hoisted_82 = { class: "vpp-dialog-body" };
const _hoisted_83 = { class: "vpp-dialog-meta" };
const _hoisted_84 = { class: "vpp-meta-chip" };
const _hoisted_85 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-dialog-hint" }, " 复制会生成一张全新的功能卡片，你可以再手动改网站地址、Cookie、UID 和描述。 ", -1));
const _hoisted_86 = { class: "vpp-dialog-panel" };
const _hoisted_87 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-section-title" }, "复制设置", -1));
const _hoisted_88 = { class: "vpp-form-grid is-single" };
const _hoisted_89 = { class: "vpp-dialog-actions" };
const _hoisted_90 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-dialog-actions-left" }, null, -1));
const _hoisted_91 = { class: "vpp-dialog-actions-right" };

const {computed,onBeforeUnmount,onMounted,reactive,ref,watch} = await importShared('vue');

const DEFAULT_CRON = '5 8 * * *';


const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
},
  emits: ['close'],
  setup(__props, { emit }) {

const props = __props;





const status = reactive({
  enabled: false,
  next_run_time: '',
  last_run: '',
  history: [],
  dashboard: {},
});

const panelConfig = ref(createEmptyConfig());
const message = reactive({ text: '', type: 'success' });
const dialog = reactive({ config: false, logs: false, copy: false });
const loading = reactive({ refreshAll: false, runAll: false, cardRefresh: false, cardRun: false });
const saving = reactive({ config: false, copy: false, delete: false });
const failedLogos = reactive({});
const editor = reactive(createCardDraft());
const copyForm = reactive({ title: '', note: '' });
const selectedCardId = ref('');
const lastLogRefresh = ref('');
const searchQuery = ref('');
const deletingCardId = ref('');
const logCardSeed = ref(null);
const rootEl = ref(null);

let logTimer = null;

const { themeName: detectedThemeName } = usePanelTheme(rootEl);
const themeValue = computed(() => String(props.themeName || 'light').toLowerCase());
const fallbackThemeName = computed(() => (themeValue.value === 'custom' ? 'light' : themeValue.value));
const resolvedThemeName = computed(() => {
  const detected = String(detectedThemeName.value || '').toLowerCase();
  if (['light', 'dark', 'purple', 'transparent'].includes(detected)) return detected
  return fallbackThemeName.value
});
const themeClass = computed(() => `vpp-theme--${resolvedThemeName.value}`);

const dashboard = computed(() => status.dashboard || {});
const dashboardCards = computed(() => Array.isArray(dashboard.value.cards) ? dashboard.value.cards : []);
const historyItems = computed(() => {
  if (Array.isArray(status.history) && status.history.length) return status.history
  return Array.isArray(dashboard.value.history) ? dashboard.value.history : []
});
const cards = computed(() => (dashboardCards.value.length ? dashboardCards.value : buildFallbackCards()));
const enabledCount = computed(() => cards.value.filter((card) => card.enabled).length);
const autoCount = computed(() => cards.value.filter((card) => card.auto_run).length);
const copyCount = computed(() => cards.value.filter((card) => canDeleteCard(card)).length);
const displayCards = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase();
  if (!keyword) return cards.value
  return cards.value.filter((card) =>
    [
      card.title,
      card.site_name,
      card.site_domain,
      card.site_url,
      card.module_name,
      card.module_summary,
      card.module_description,
      card.status_text,
      card.note,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(keyword)),
  )
});
const controlStats = computed(() => [
  { label: '功能卡片', value: String(cards.value.length), icon: 'mdi-view-grid-outline' },
  { label: '启用中', value: String(enabledCount.value), icon: 'mdi-toggle-switch-outline' },
  { label: '定时执行', value: String(autoCount.value), icon: 'mdi-clock-outline' },
  { label: '可删除复制卡', value: String(copyCount.value), icon: 'mdi-content-copy' },
]);
const activeDashboardCard = computed(() => cards.value.find((item) => item.card_id === selectedCardId.value) || null);
const currentLogCard = computed(() => activeDashboardCard.value || logCardSeed.value || null);
const latestStateLog = computed(() => {
  const card = currentLogCard.value;
  if (!card) return null
  const entry = cardToLogEntry(card);
  if (!entry) return null
  return {
    ...entry,
    id: `latest-${entry.card_id || card.card_id || card.id || 'item'}-${entry.time || 'state'}`,
  }
});
const selectedLogs = computed(() => {
  const card = currentLogCard.value;
  if (!card) return []
  const fallbackLogs = card.log_items || [];
  const merged = new Map();
  for (const item of [latestStateLog.value, ...fallbackLogs, ...historyItems.value]) {
    if (!logMatchesCard(item, card)) continue
    const key = logEntryKey(item);
    if (!merged.has(key)) merged.set(key, item);
  }
  const items = [...merged.values()].sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')));
  if (items.length) return items
  const fallbackItem = cardToLogEntry(card);
  return fallbackItem ? [fallbackItem] : []
});

function createEmptyConfig() {
  return {
    enabled: false,
    notify: true,
    onlyonce: false,
    use_proxy: false,
    force_ipv4: true,
    cron: DEFAULT_CRON,
    http_timeout: 15,
    http_retry_times: 3,
    random_delay_max_seconds: 5,
    cards: [],
    module_options: [],
    tone_options: [],
  }
}

function createCardDraft(source = {}) {
  return {
    id: String(source.id || source.card_id || ''),
    title: String(source.title || ''),
    module_key: String(source.module_key || 'siqi_sign'),
    site_name: String(source.site_name || ''),
    site_url: String(source.site_url || ''),
    enabled: !!source.enabled,
    auto_run: source.auto_run !== false,
    notify: source.notify !== false,
    cron: String(source.cron || DEFAULT_CRON),
    tone: String(source.tone || 'azure'),
    cookie: String(source.cookie || ''),
    uid: String(source.uid || ''),
    note: String(source.note || ''),
    run_once: false,
  }
}

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value ?? null))
}

function moduleMeta(moduleKey) {
  return (panelConfig.value.module_options || []).find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    icon: '•',
    description: '',
    summary: String(moduleKey || '').replaceAll('_', ' '),
    default_site_name: '',
    default_site_url: '',
    tone: 'azure',
  }
}

function nextCardId(moduleKey) {
  return `${moduleKey}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}

function getCardId(card) {
  return String(card?.id || card?.card_id || '')
}

function normalizeCard(source = {}, options = {}) {
  const meta = moduleMeta(String(source.module_key || source.module || 'siqi_sign'));
  const toneValues = new Set((panelConfig.value.tone_options || []).map((item) => item.key));
  const tone = toneValues.has(source.tone) ? source.tone : (meta.tone || 'azure');
  return {
    id: String(options.newId ? nextCardId(meta.key) : (source.id || source.card_id || nextCardId(meta.key))),
    title: String(source.title || meta.label || '').trim() || meta.label,
    module_key: meta.key,
    site_name: String(source.site_name || meta.default_site_name || meta.label || '').trim() || meta.label,
    site_url: String(source.site_url || meta.default_site_url || '').trim(),
    enabled: !!source.enabled,
    auto_run: source.auto_run !== false,
    notify: source.notify !== false,
    cron: String(source.cron || DEFAULT_CRON).trim() || DEFAULT_CRON,
    tone,
    cookie: String(source.cookie || '').trim(),
    uid: meta.key === 'newapi_checkin' ? String(source.uid || '').trim() : '',
    note: String(source.note || '').trim(),
  }
}

function normalizeConfig(source = {}) {
  const next = createEmptyConfig();
  next.enabled = !!source.enabled;
  next.notify = source.notify !== false;
  next.onlyonce = !!source.onlyonce;
  next.use_proxy = !!source.use_proxy;
  next.force_ipv4 = source.force_ipv4 !== false;
  next.cron = String(source.cron || DEFAULT_CRON);
  next.http_timeout = Number(source.http_timeout || 15);
  next.http_retry_times = Number(source.http_retry_times || 3);
  next.random_delay_max_seconds = Number(source.random_delay_max_seconds || 5);
  next.module_options = Array.isArray(source.module_options) ? deepClone(source.module_options) : [];
  next.tone_options = Array.isArray(source.tone_options) ? deepClone(source.tone_options) : [];
  next.cards = Array.isArray(source.cards) ? source.cards.map((item) => normalizeCard(item)) : [];
  return next
}

function siteDomain(siteUrl) {
  try {
    return new URL(siteUrl).host || ''
  } catch {
    return String(siteUrl || '').replace(/^https?:\/\//i, '').split('/')[0] || ''
  }
}

function siteLogo(siteUrl) {
  try {
    const parsed = new URL(siteUrl);
    if (!parsed.protocol || !parsed.host) return ''
    return `${parsed.protocol}//${parsed.host}/favicon.ico`
  } catch {
    return ''
  }
}

function fallbackStatus(card, meta) {
  if (!card.enabled) {
    return {
      level: 'info',
      status_title: '已停用',
      status_text: '当前功能卡片已停用，启用后即可手动执行或参与定时调度。',
    }
  }
  if (!card.cookie) {
    return {
      level: 'warning',
      status_title: '待配置 Cookie',
      status_text: '请先在配置弹窗中填写 Cookie，保存后再刷新或执行。',
    }
  }
  if (meta.key === 'newapi_checkin' && !card.uid) {
    return {
      level: 'warning',
      status_title: '待配置 UID',
      status_text: 'New API 签到卡片还需要填写 UID 才能正常执行。',
    }
  }
  if (!card.auto_run) {
    return {
      level: 'info',
      status_title: '仅手动执行',
      status_text: '当前已启用，但只会在你手动点击执行时运行。',
    }
  }
  return {
    level: 'info',
    status_title: '等待刷新',
    status_text: '卡片配置已经加载，可以点击刷新或执行启用查看实时状态。',
  }
}

function fallbackTags(card) {
  const tags = [];
  tags.push(card.enabled ? '启用' : '停用');
  tags.push(card.auto_run ? '自动执行' : '手动执行');
  if (card.cookie) tags.push('Cookie 已配置');
  if (card.uid) tags.push(`UID ${card.uid}`);
  return tags
}

function buildFallbackCards() {
  return (panelConfig.value.cards || []).map((source) => {
    const card = normalizeCard(source);
    const meta = moduleMeta(card.module_key);
    const fallbackCard = { ...card, card_id: card.id };
    const logItems = historyItems.value
      .filter((item) => logMatchesCard(item, fallbackCard))
      .sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
      .slice(0, 12);
    const fallback = fallbackStatus(card, meta);

    return {
      ...card,
      card_id: card.id,
      site_domain: siteDomain(card.site_url),
      site_logo: siteLogo(card.site_url),
      module_name: meta.label,
      module_icon: meta.icon || '•',
      module_summary: String(meta.summary || meta.key || '').toLowerCase(),
      module_description: String(meta.description || ''),
      status_label: card.enabled ? '启用' : '停用',
      status_key: card.enabled ? 'enabled' : 'disabled',
      next_run_time: '',
      last_run: logItems[0]?.time || '',
      log_items: logItems,
      log_count: logItems.length,
      cookie_configured: !!card.cookie,
      copy_title: card.title,
      copy_description: card.note || String(meta.description || ''),
      tags: fallbackTags(card),
      metrics: [],
      detail_lines: [],
      ...fallback,
    }
  })
}

function serializeConfig(cardsOverride = null) {
  const cards = Array.isArray(cardsOverride) ? cardsOverride : panelConfig.value.cards;
  return {
    enabled: !!panelConfig.value.enabled,
    notify: !!panelConfig.value.notify,
    onlyonce: !!panelConfig.value.onlyonce,
    use_proxy: !!panelConfig.value.use_proxy,
    force_ipv4: panelConfig.value.force_ipv4 !== false,
    cron: String(panelConfig.value.cron || DEFAULT_CRON),
    http_timeout: Number(panelConfig.value.http_timeout || 15),
    http_retry_times: Number(panelConfig.value.http_retry_times || 3),
    random_delay_max_seconds: Number(panelConfig.value.random_delay_max_seconds || 5),
    cards: cards.map((item) => normalizeCard(item)),
  }
}

function runtimeTone(level) {
  if (level === 'success') return 'success'
  if (level === 'warning') return 'warning'
  if (level === 'error') return 'danger'
  return 'info'
}

function runtimeLabel(level) {
  return {
    success: '正常',
    warning: '待处理',
    error: '异常',
    info: '信息',
  }[level] || '信息'
}

function logTone(item) {
  const level = String(item?.level || '').toLowerCase();
  if (level === 'success') return 'success'
  if (level === 'warning') return 'warning'
  if (level === 'error') return 'danger'
  const text = `${item?.status_title || ''} ${item?.summary || ''}`.toLowerCase();
  if (/(error|fail|异常|失败)/.test(text)) return 'danger'
  if (/(warning|待|cookie|uid)/.test(text)) return 'warning'
  if (/(success|完成|成功|签到|领取)/.test(text)) return 'success'
  return 'info'
}

function logStatusLabel(item) {
  return item?.status_title || item?.title || runtimeLabel(item?.level)
}

function logDetail(item) {
  if (item?.summary) return item.summary
  const lines = Array.isArray(item?.lines) ? item.lines.filter(Boolean) : [];
  if (lines.length) return lines[0]
  return '暂无详情'
}

function logEntryKey(item) {
  if (!item) return ''
  return [
    String(item.card_id || '').trim(),
    String(item.time || '').trim(),
    String(item.status_title || item.title || '').trim(),
    String(item.summary || '').trim(),
    Array.isArray(item.lines) ? item.lines.filter(Boolean).join('|') : '',
  ].join('::')
}

function cardToLogEntry(card) {
  if (!card) return null
  const time = String(card.last_run || card.last_checked || '').trim();
  const summary = String(card.status_text || '').trim();
  const lines = Array.isArray(card.detail_lines) ? card.detail_lines.filter(Boolean) : [];
  const title = String(card.title || '').trim();
  if (!time && !summary && !lines.length && !title) return null
  return {
    id: `card-fallback-${card.card_id || card.id || 'item'}-${time || 'now'}`,
    time: time || '--',
    title: title || '最近状态',
    summary,
    status_title: String(card.status_title || '最近状态').trim(),
    level: String(card.level || 'info').trim(),
    lines,
    card_id: String(card.card_id || card.id || '').trim(),
    module_key: String(card.module_key || '').trim(),
    site_name: String(card.site_name || '').trim(),
    site_url: String(card.site_url || '').trim(),
  }
}

function logMatchesCard(item, card) {
  if (!item || !card) return false
  const cardId = String(card.card_id || card.id || '').trim();
  const itemCardId = String(item.card_id || '').trim();
  if (cardId && itemCardId && cardId === itemCardId) return true

  const cardModule = String(card.module_key || '').trim();
  const itemModule = String(item.module_key || '').trim();
  if (!cardModule || !itemModule || cardModule !== itemModule) return false

  const cardSiteUrl = String(card.site_url || '').trim().toLowerCase();
  const itemSiteUrl = String(item.site_url || '').trim().toLowerCase();
  if (cardSiteUrl && itemSiteUrl && cardSiteUrl === itemSiteUrl) return true

  const cardSiteName = String(card.site_name || '').trim().toLowerCase();
  const itemSiteName = String(item.site_name || '').trim().toLowerCase();
  if (cardSiteName && itemSiteName && cardSiteName === itemSiteName) return true

  const cardTitle = String(card.title || '').trim().toLowerCase();
  const itemTitle = String(item.title || '').trim().toLowerCase();
  return Boolean(cardTitle && itemTitle && cardTitle === itemTitle)
}

function scheduleText(card) {
  if (!card?.enabled) return '已停用'
  if (!card?.auto_run) return '仅手动执行'
  return card?.next_run_time || card?.cron || '等待调度'
}

function cardSubtitle(card) {
  return String(cardDescription(card) || card?.module_summary || 'plugin card').trim()
}

function cardDescription(card) {
  return String(card?.note || card?.module_description || card?.status_text || '暂无说明').trim()
}

function cardStatusSummary(card) {
  const summary = String(card?.status_text || scheduleText(card) || '').trim();
  if (!summary) return ''
  if (summary === '卡片配置已经加载，可以点击刷新或执行启用查看实时状态。') return ''
  return summary
}

function logoSrc(card) {
  return failedLogos[card.card_id] ? '' : (card.site_logo || '')
}

function markLogoFailed(cardId) {
  failedLogos[cardId] = true;
}

function rawCardById(cardId) {
  return (panelConfig.value.cards || []).find((item) => item.id === cardId) || null
}

function canDeleteCard(card) {
  const cardId = getCardId(card);
  return Boolean(cardId) && !cardId.endsWith('-default')
}

function openConfigDialog(card) {
  const source = rawCardById(card.card_id) || card;
  Object.assign(editor, normalizeCard(source));
  editor.run_once = false;
  selectedCardId.value = card.card_id;
  dialog.config = true;
}

function openLogsDialog(card) {
  selectedCardId.value = card.card_id;
  logCardSeed.value = deepClone(card);
  dialog.logs = true;
}

function openCopyDialog(card) {
  selectedCardId.value = card.card_id;
  copyForm.title = `${card.title} 副本`;
  copyForm.note = card.note || card.module_description || '';
  dialog.copy = true;
}

function applyStatusPayload(payload = {}) {
  const source = payload?.status && typeof payload.status === 'object' ? payload.status : payload;
  if (!source || typeof source !== 'object') return false

  if ('enabled' in source) status.enabled = !!source.enabled;
  status.next_run_time = source.next_run_time || '';
  status.last_run = source.last_run || '';
  status.history = Array.isArray(source.history)
    ? source.history
    : (Array.isArray(source.dashboard?.history) ? source.dashboard.history : []);
  status.dashboard = source.dashboard || payload.dashboard || {};
  if (source.config || payload.config) panelConfig.value = normalizeConfig(source.config || payload.config || {});
  lastLogRefresh.value = new Date().toLocaleTimeString('zh-CN', { hour12: false });
  return true
}

async function loadStatus(showError = true) {
  try {
    const payload = await props.api.get('/plugin/VuePanel/status');
    applyStatusPayload(payload);
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error');
    return false
  }
}

async function persistCards(nextCards, successText) {
  const payload = serializeConfig(nextCards);
  const response = await props.api.post('/plugin/VuePanel/config', payload);
  applyStatusPayload(response);
  flash(response.message || successText || '配置已保存');
  if (!response?.status) await loadStatus(false);
  return response
}

async function refreshStatus() {
  loading.refreshAll = true;
  try {
    const response = await props.api.post('/plugin/VuePanel/refresh', {});
    applyStatusPayload(response);
    flash(response.message || '状态已刷新');
    if (!response?.status) await loadStatus(false);
  } catch (error) {
    flash(error?.message || '刷新状态失败', 'error');
  } finally {
    loading.refreshAll = false;
  }
}

async function runAll() {
  loading.runAll = true;
  try {
    const response = await props.api.post('/plugin/VuePanel/run', {});
    applyStatusPayload(response);
    flash(response.message || '已执行启用任务');
    if (!response?.status) await loadStatus(false);
  } catch (error) {
    flash(error?.message || '执行任务失败', 'error');
  } finally {
    loading.runAll = false;
  }
}

async function saveCardConfig() {
  saving.config = true;
  try {
    const runAfterSave = !!editor.run_once;
    let matched = false;
    const nextCards = (panelConfig.value.cards || []).map((item) => {
      if (item.id === editor.id) {
        matched = true;
        return normalizeCard(editor)
      }
      return normalizeCard(item)
    });
    if (!matched) nextCards.push(normalizeCard(editor));
    await persistCards(nextCards, runAfterSave ? '卡片配置已保存，准备立即执行' : '卡片配置已保存');
    if (runAfterSave) {
      const response = await props.api.post('/plugin/VuePanel/card/run', { card_id: editor.id });
      applyStatusPayload(response);
      flash(response.message || '卡片已保存并立即执行一次');
    }
    editor.run_once = false;
    dialog.config = false;
  } catch (error) {
    flash(error?.message || '保存卡片配置失败', 'error');
  } finally {
    saving.config = false;
  }
}

async function confirmCopyCard() {
  saving.copy = true;
  try {
    const source = rawCardById(selectedCardId.value);
    if (!source) throw new Error('未找到复制来源')
    const copyCard = normalizeCard(
      {
        ...source,
        id: nextCardId(source.module_key),
        title: copyForm.title || `${source.title} 副本`,
        note: copyForm.note,
      },
      { newId: true },
    );
    const nextCards = [...(panelConfig.value.cards || []).map((item) => normalizeCard(item)), copyCard];
    await persistCards(nextCards, '卡片已复制');
    dialog.copy = false;
  } catch (error) {
    flash(error?.message || '复制卡片失败', 'error');
  } finally {
    saving.copy = false;
  }
}

async function deleteCard(card) {
  const cardId = getCardId(card);
  if (!canDeleteCard(card)) return
  const target = rawCardById(cardId) || normalizeCard(card);
  const title = target.title || '当前卡片';
  if (typeof window !== 'undefined' && !window.confirm(`确认删除“${title}”吗？`)) return

  saving.delete = true;
  deletingCardId.value = cardId;
  try {
    const nextCards = (panelConfig.value.cards || [])
      .filter((item) => item.id !== cardId)
      .map((item) => normalizeCard(item));
    await persistCards(nextCards, '卡片已删除');
    if (selectedCardId.value === cardId) {
      dialog.config = false;
      dialog.logs = false;
      dialog.copy = false;
      selectedCardId.value = '';
    }
  } catch (error) {
    flash(error?.message || '删除卡片失败', 'error');
  } finally {
    saving.delete = false;
    deletingCardId.value = '';
  }
}

async function deleteCurrentCard() {
  await deleteCard(activeDashboardCard.value || editor);
}

async function runFocusedCard() {
  if (!selectedCardId.value) return
  loading.cardRun = true;
  try {
    const response = await props.api.post('/plugin/VuePanel/card/run', { card_id: selectedCardId.value });
    applyStatusPayload(response);
    flash(response.message || '卡片执行完成');
    if (!response?.status) await loadStatus(false);
  } catch (error) {
    flash(error?.message || '卡片执行失败', 'error');
  } finally {
    loading.cardRun = false;
  }
}

async function refreshFocusedCard() {
  if (!selectedCardId.value) return
  loading.cardRefresh = true;
  try {
    const response = await props.api.post('/plugin/VuePanel/card/refresh', { card_id: selectedCardId.value });
    applyStatusPayload(response);
    flash(response.message || '卡片状态已刷新');
    if (!response?.status) await loadStatus(false);
  } catch (error) {
    flash(error?.message || '卡片刷新失败', 'error');
  } finally {
    loading.cardRefresh = false;
  }
}

function stopLogPolling() {
  if (logTimer) {
    window.clearInterval(logTimer);
    logTimer = null;
  }
}

function startLogPolling() {
  stopLogPolling();
  loadStatus(false);
  logTimer = window.setInterval(() => {
    loadStatus(false);
  }, 5000);
}

function closePlugin() {
  emit('close');
}

watch(
  () => dialog.logs,
  (opened) => {
    if (opened) startLogPolling();
    else {
      stopLogPolling();
      logCardSeed.value = null;
    }
  },
);

onMounted(async () => {
  panelConfig.value = normalizeConfig(props.initialConfig || {});
  await loadStatus();
});

onBeforeUnmount(() => {
  stopLogPolling();
});

return (_ctx, _cache) => {
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_textarea = _resolveComponent("v-textarea");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_dialog = _resolveComponent("v-dialog");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["vuepanel-page", themeClass.value])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("header", _hoisted_2, [
        _createElementVNode("div", _hoisted_3, [
          _createVNode(_component_v_text_field, {
            modelValue: searchQuery.value,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((searchQuery).value = $event)),
            class: "vpp-search-field",
            variant: "outlined",
            density: "compact",
            "hide-details": "",
            clearable: "",
            placeholder: "搜索功能模块...",
            "prepend-inner-icon": "mdi-magnify"
          }, null, 8, ["modelValue"])
        ]),
        _createElementVNode("div", _hoisted_4, [
          _createVNode(_component_v_btn, {
            class: "vpp-toolbar-btn",
            variant: "text",
            "prepend-icon": "mdi-flash",
            loading: loading.runAll,
            onClick: runAll
          }, {
            default: _withCtx(() => [
              _createTextVNode(" 执行启用 "),
              _createElementVNode("span", _hoisted_5, _toDisplayString(enabledCount.value), 1)
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            class: "vpp-toolbar-btn",
            variant: "text",
            "prepend-icon": "mdi-refresh",
            loading: loading.refreshAll,
            onClick: refreshStatus
          }, {
            default: _withCtx(() => [
              _createTextVNode("刷新")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            class: "vpp-toolbar-btn is-icon",
            icon: "mdi-close",
            variant: "text",
            onClick: closePlugin
          })
        ])
      ]),
      (message.text)
        ? (_openBlock(), _createBlock(_component_v_alert, {
            key: 0,
            type: message.type,
            variant: "tonal",
            rounded: "xl",
            class: "vpp-alert"
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(message.text), 1)
            ]),
            _: 1
          }, 8, ["type"]))
        : _createCommentVNode("", true),
      _createElementVNode("section", _hoisted_6, [
        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(controlStats.value, (item) => {
          return (_openBlock(), _createElementBlock("article", {
            key: item.label,
            class: "vpp-stat-card"
          }, [
            _createElementVNode("div", _hoisted_7, [
              _createVNode(_component_v_icon, {
                icon: item.icon,
                size: "18"
              }, null, 8, ["icon"])
            ]),
            _createElementVNode("div", _hoisted_8, [
              _createElementVNode("strong", _hoisted_9, _toDisplayString(item.value), 1),
              _createElementVNode("span", _hoisted_10, _toDisplayString(item.label), 1)
            ])
          ]))
        }), 128))
      ]),
      _createElementVNode("section", _hoisted_11, [
        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(displayCards.value, (card) => {
          return (_openBlock(), _createElementBlock("article", {
            key: card.card_id,
            class: _normalizeClass(["vpp-card", [{ 'is-enabled': card.enabled, 'is-disabled': !card.enabled }, `level-${runtimeTone(card.level)}`]])
          }, [
            _hoisted_12,
            _createElementVNode("div", _hoisted_13, [
              _createElementVNode("div", _hoisted_14, [
                (logoSrc(card))
                  ? (_openBlock(), _createElementBlock("img", {
                      key: 0,
                      src: logoSrc(card),
                      alt: `${card.site_name} logo`,
                      class: "vpp-logo",
                      onError: $event => (markLogoFailed(card.card_id))
                    }, null, 40, _hoisted_15))
                  : (_openBlock(), _createElementBlock("span", _hoisted_16, _toDisplayString(card.module_icon || '•'), 1))
              ]),
              _createElementVNode("div", _hoisted_17, [
                _createElementVNode("div", _hoisted_18, [
                  _createElementVNode("div", _hoisted_19, [
                    _createElementVNode("h2", _hoisted_20, _toDisplayString(card.title), 1),
                    _createElementVNode("p", _hoisted_21, _toDisplayString(cardSubtitle(card)), 1)
                  ]),
                  _createElementVNode("span", {
                    class: _normalizeClass(["vpp-status-pill", `is-${card.status_key}`])
                  }, _toDisplayString(card.status_label), 3)
                ]),
                _createElementVNode("div", _hoisted_22, [
                  _createElementVNode("span", _hoisted_23, _toDisplayString(card.site_name || card.module_name), 1),
                  _createElementVNode("span", _hoisted_24, _toDisplayString(card.site_domain || card.site_url || '--'), 1)
                ])
              ])
            ]),
            (cardStatusSummary(card))
              ? (_openBlock(), _createElementBlock("div", _hoisted_25, [
                  _createElementVNode("p", _hoisted_26, _toDisplayString(cardStatusSummary(card)), 1)
                ]))
              : _createCommentVNode("", true),
            _createElementVNode("div", _hoisted_27, [
              _createVNode(_component_v_btn, {
                class: "vpp-action-btn is-config",
                variant: "text",
                "prepend-icon": "mdi-cog-outline",
                onClick: $event => (openConfigDialog(card))
              }, {
                default: _withCtx(() => [
                  _createTextVNode("配置")
                ]),
                _: 2
              }, 1032, ["onClick"]),
              _createVNode(_component_v_btn, {
                class: "vpp-action-btn is-logs",
                variant: "text",
                "prepend-icon": "mdi-text-box-outline",
                onClick: $event => (openLogsDialog(card))
              }, {
                default: _withCtx(() => [
                  _createTextVNode("日志")
                ]),
                _: 2
              }, 1032, ["onClick"]),
              _createVNode(_component_v_btn, {
                class: "vpp-action-btn is-copy",
                variant: "text",
                "prepend-icon": "mdi-content-copy",
                onClick: $event => (openCopyDialog(card))
              }, {
                default: _withCtx(() => [
                  _createTextVNode("复制")
                ]),
                _: 2
              }, 1032, ["onClick"])
            ])
          ], 2))
        }), 128)),
        (!displayCards.value.length)
          ? (_openBlock(), _createElementBlock("div", _hoisted_28, _toDisplayString(searchQuery.value ? '没有找到匹配的功能模块。' : '当前还没有可展示的功能卡片。'), 1))
          : _createCommentVNode("", true)
      ])
    ]),
    _createVNode(_component_v_dialog, {
      modelValue: dialog.config,
      "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((dialog.config) = $event)),
      "max-width": "760"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, {
          class: _normalizeClass(["vpp-dialog-card is-config", themeClass.value])
        }, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_29, [
              _createElementVNode("div", _hoisted_30, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-cog-outline",
                  size: "22",
                  class: "vpp-dialog-icon is-config"
                }),
                _createElementVNode("div", null, [
                  _hoisted_31,
                  _createElementVNode("h3", _hoisted_32, _toDisplayString(editor.title || activeDashboardCard.value?.title || '功能配置'), 1)
                ])
              ]),
              _createElementVNode("span", {
                class: _normalizeClass(["vpp-status-pill", `is-${editor.enabled ? 'enabled' : 'disabled'}`])
              }, _toDisplayString(editor.enabled ? '启用' : '停用'), 3)
            ]),
            _createElementVNode("div", _hoisted_33, [
              _createElementVNode("div", _hoisted_34, [
                _createElementVNode("span", _hoisted_35, _toDisplayString(editor.site_name || '--'), 1),
                _createElementVNode("span", _hoisted_36, _toDisplayString(editor.cron || DEFAULT_CRON), 1)
              ]),
              _createElementVNode("div", _hoisted_37, [
                _hoisted_38,
                _createElementVNode("div", _hoisted_39, [
                  _createElementVNode("label", _hoisted_40, [
                    _hoisted_41,
                    _createVNode(_component_v_switch, {
                      modelValue: editor.enabled,
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((editor.enabled) = $event)),
                      "hide-details": "",
                      color: "primary",
                      density: "compact"
                    }, null, 8, ["modelValue"])
                  ]),
                  _createElementVNode("label", _hoisted_42, [
                    _hoisted_43,
                    _createVNode(_component_v_switch, {
                      modelValue: editor.auto_run,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((editor.auto_run) = $event)),
                      "hide-details": "",
                      color: "primary",
                      density: "compact"
                    }, null, 8, ["modelValue"])
                  ]),
                  _createElementVNode("label", _hoisted_44, [
                    _hoisted_45,
                    _createVNode(_component_v_switch, {
                      modelValue: editor.notify,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((editor.notify) = $event)),
                      "hide-details": "",
                      color: "primary",
                      density: "compact"
                    }, null, 8, ["modelValue"])
                  ]),
                  _createElementVNode("label", _hoisted_46, [
                    _hoisted_47,
                    _createVNode(_component_v_switch, {
                      modelValue: editor.run_once,
                      "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((editor.run_once) = $event)),
                      "hide-details": "",
                      color: "primary",
                      density: "compact"
                    }, null, 8, ["modelValue"])
                  ])
                ])
              ]),
              _createElementVNode("div", _hoisted_48, [
                _hoisted_49,
                _createElementVNode("div", _hoisted_50, [
                  _createVNode(_component_v_text_field, {
                    modelValue: editor.title,
                    "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((editor.title) = $event)),
                    label: "功能名称",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_v_text_field, {
                    modelValue: editor.site_name,
                    "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((editor.site_name) = $event)),
                    label: "网站名称",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_v_text_field, {
                    modelValue: editor.site_url,
                    "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((editor.site_url) = $event)),
                    label: "网站地址",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue"]),
                  _createVNode(BaseCronField, {
                    modelValue: editor.cron,
                    "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((editor.cron) = $event)),
                    label: "Cron",
                    class: "vpp-cron-field"
                  }, null, 8, ["modelValue"]),
                  (editor.module_key === 'newapi_checkin')
                    ? (_openBlock(), _createBlock(_component_v_text_field, {
                        key: 0,
                        modelValue: editor.uid,
                        "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((editor.uid) = $event)),
                        label: "UID",
                        variant: "outlined",
                        density: "compact",
                        "hide-details": "auto"
                      }, null, 8, ["modelValue"]))
                    : _createCommentVNode("", true),
                  _createVNode(_component_v_text_field, {
                    modelValue: editor.cookie,
                    "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((editor.cookie) = $event)),
                    label: "Cookie",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto",
                    class: "vpp-field-span-2"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_v_textarea, {
                    modelValue: editor.note,
                    "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((editor.note) = $event)),
                    label: "功能描述",
                    variant: "outlined",
                    rows: "2",
                    "auto-grow": "",
                    density: "compact",
                    "hide-details": "auto",
                    class: "vpp-field-span-2"
                  }, null, 8, ["modelValue"])
                ])
              ])
            ]),
            _createElementVNode("div", _hoisted_51, [
              _createElementVNode("div", _hoisted_52, [
                _createVNode(_component_v_btn, {
                  class: _normalizeClass(["vpp-action-btn is-delete", { 'is-disabled-control': !canDeleteCard(activeDashboardCard.value || editor) }]),
                  variant: "text",
                  "prepend-icon": "mdi-delete-outline",
                  disabled: !canDeleteCard(activeDashboardCard.value || editor),
                  loading: saving.delete && deletingCardId.value === editor.id,
                  onClick: deleteCurrentCard
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(" 删除卡片 ")
                  ]),
                  _: 1
                }, 8, ["class", "disabled", "loading"])
              ]),
              _createElementVNode("div", _hoisted_53, [
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: _cache[12] || (_cache[12] = $event => (dialog.config = false))
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("取消")
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_btn, {
                  class: "vpp-confirm-btn",
                  variant: "text",
                  loading: saving.config,
                  onClick: saveCardConfig
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("保存配置")
                  ]),
                  _: 1
                }, 8, ["loading"])
              ])
            ])
          ]),
          _: 1
        }, 8, ["class"])
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: dialog.logs,
      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((dialog.logs) = $event)),
      "max-width": "900"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, {
          class: _normalizeClass(["vpp-dialog-card is-logs", themeClass.value])
        }, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_54, [
              _createElementVNode("div", _hoisted_55, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-text-box-outline",
                  size: "22",
                  class: "vpp-dialog-icon is-logs"
                }),
                _createElementVNode("div", null, [
                  _hoisted_56,
                  _createElementVNode("h3", _hoisted_57, _toDisplayString(currentLogCard.value?.title || '实时日志'), 1)
                ])
              ]),
              _hoisted_58
            ]),
            _createElementVNode("div", _hoisted_59, [
              _createElementVNode("div", _hoisted_60, [
                _createElementVNode("span", _hoisted_61, _toDisplayString(currentLogCard.value?.site_name || '--'), 1),
                _createElementVNode("span", _hoisted_62, _toDisplayString(currentLogCard.value?.site_domain || currentLogCard.value?.site_url || '--'), 1),
                _createElementVNode("span", _hoisted_63, "最近刷新 " + _toDisplayString(lastLogRefresh.value || '--'), 1)
              ]),
              _createElementVNode("div", _hoisted_64, [
                _hoisted_65,
                (!selectedLogs.value.length)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_66, " 当前卡片还没有执行日志，先执行一次或等待下次轮询。 "))
                  : (_openBlock(), _createElementBlock("div", _hoisted_67, [
                      _hoisted_68,
                      _createElementVNode("div", _hoisted_69, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(selectedLogs.value, (item) => {
                          return (_openBlock(), _createElementBlock("article", {
                            key: item.id || `${item.time}-${item.summary}`,
                            class: "vpp-log-row"
                          }, [
                            _createElementVNode("div", _hoisted_70, _toDisplayString(item.time || '--'), 1),
                            _createElementVNode("div", _hoisted_71, [
                              _createElementVNode("span", {
                                class: _normalizeClass(["vpp-runtime-pill", `is-${logTone(item)}`])
                              }, _toDisplayString(logStatusLabel(item)), 3)
                            ]),
                            _createElementVNode("div", _hoisted_72, [
                              _createElementVNode("div", _hoisted_73, _toDisplayString(logDetail(item)), 1),
                              (item.lines?.length)
                                ? (_openBlock(), _createElementBlock("div", _hoisted_74, [
                                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(item.lines, (line) => {
                                      return (_openBlock(), _createElementBlock("span", {
                                        key: `${item.id}-${line}`,
                                        class: "vpp-log-line"
                                      }, _toDisplayString(line), 1))
                                    }), 128))
                                  ]))
                                : _createCommentVNode("", true)
                            ])
                          ]))
                        }), 128))
                      ])
                    ]))
              ])
            ]),
            _createElementVNode("div", _hoisted_75, [
              _hoisted_76,
              _createElementVNode("div", _hoisted_77, [
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: _cache[14] || (_cache[14] = $event => (dialog.logs = false))
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("关闭")
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_btn, {
                  class: "vpp-action-btn is-logs",
                  variant: "text",
                  "prepend-icon": "mdi-refresh",
                  loading: loading.cardRefresh,
                  onClick: refreshFocusedCard
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("刷新状态")
                  ]),
                  _: 1
                }, 8, ["loading"]),
                _createVNode(_component_v_btn, {
                  class: "vpp-confirm-btn",
                  variant: "text",
                  "prepend-icon": "mdi-play-circle-outline",
                  loading: loading.cardRun,
                  onClick: runFocusedCard
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("立即执行")
                  ]),
                  _: 1
                }, 8, ["loading"])
              ])
            ])
          ]),
          _: 1
        }, 8, ["class"])
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: dialog.copy,
      "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((dialog.copy) = $event)),
      "max-width": "560"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, {
          class: _normalizeClass(["vpp-dialog-card is-copy", themeClass.value])
        }, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_78, [
              _createElementVNode("div", _hoisted_79, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-content-copy",
                  size: "22",
                  class: "vpp-dialog-icon is-copy"
                }),
                _createElementVNode("div", null, [
                  _hoisted_80,
                  _createElementVNode("h3", _hoisted_81, _toDisplayString(activeDashboardCard.value?.title || '复制功能卡片'), 1)
                ])
              ])
            ]),
            _createElementVNode("div", _hoisted_82, [
              _createElementVNode("div", _hoisted_83, [
                _createElementVNode("span", _hoisted_84, _toDisplayString(activeDashboardCard.value?.site_name || '--'), 1)
              ]),
              _hoisted_85,
              _createElementVNode("div", _hoisted_86, [
                _hoisted_87,
                _createElementVNode("div", _hoisted_88, [
                  _createVNode(_component_v_text_field, {
                    modelValue: copyForm.title,
                    "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((copyForm.title) = $event)),
                    label: "复制功能名称",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_v_textarea, {
                    modelValue: copyForm.note,
                    "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((copyForm.note) = $event)),
                    label: "功能描述",
                    variant: "outlined",
                    rows: "2",
                    "auto-grow": "",
                    density: "compact",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue"])
                ])
              ])
            ]),
            _createElementVNode("div", _hoisted_89, [
              _hoisted_90,
              _createElementVNode("div", _hoisted_91, [
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: _cache[18] || (_cache[18] = $event => (dialog.copy = false))
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("取消")
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_btn, {
                  class: "vpp-confirm-btn",
                  variant: "text",
                  loading: saving.copy,
                  onClick: confirmCopyCard
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("确定复制")
                  ]),
                  _: 1
                }, 8, ["loading"])
              ])
            ])
          ]),
          _: 1
        }, 8, ["class"])
      ]),
      _: 1
    }, 8, ["modelValue"])
  ], 2))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-757c56d0"]]);

export { _export_sfc as _, PageView as default, usePanelTheme as u };
