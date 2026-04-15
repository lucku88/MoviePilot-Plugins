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

const Page_vue_vue_type_style_index_0_scoped_2594591a_lang = '';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,normalizeStyle:_normalizeStyle,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-2594591a"),n=n(),_popScopeId(),n);
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
const _hoisted_25 = { class: "vpp-card-body" };
const _hoisted_26 = { class: "vpp-card-state-row" };
const _hoisted_27 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-card-state-label" }, "状态", -1));
const _hoisted_28 = { class: "vpp-action-row" };
const _hoisted_29 = {
  key: 0,
  class: "vpp-empty-state vpp-grid-empty"
};
const _hoisted_30 = { class: "vpp-dialog-head" };
const _hoisted_31 = { class: "vpp-dialog-title-wrap" };
const _hoisted_32 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-kicker" }, "配置", -1));
const _hoisted_33 = { class: "vpp-dialog-title" };
const _hoisted_34 = { class: "vpp-dialog-body" };
const _hoisted_35 = { class: "vpp-dialog-meta" };
const _hoisted_36 = { class: "vpp-meta-chip" };
const _hoisted_37 = { class: "vpp-meta-chip" };
const _hoisted_38 = { class: "vpp-meta-chip" };
const _hoisted_39 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-dialog-hint" }, " 保存后会直接更新当前卡片，多站点请通过复制卡片后独立修改。 ", -1));
const _hoisted_40 = { class: "vpp-dialog-panel" };
const _hoisted_41 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-section-title" }, "开关", -1));
const _hoisted_42 = { class: "vpp-switch-grid" };
const _hoisted_43 = { class: "vpp-switch-card" };
const _hoisted_44 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-switch-label" }, "启用功能", -1));
const _hoisted_45 = { class: "vpp-switch-card" };
const _hoisted_46 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-switch-label" }, "定时执行", -1));
const _hoisted_47 = { class: "vpp-switch-card" };
const _hoisted_48 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-switch-label" }, "发送通知", -1));
const _hoisted_49 = { class: "vpp-dialog-panel" };
const _hoisted_50 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-section-title" }, "基础设置", -1));
const _hoisted_51 = { class: "vpp-form-grid" };
const _hoisted_52 = { class: "vpp-dialog-actions" };
const _hoisted_53 = { class: "vpp-dialog-actions-left" };
const _hoisted_54 = { class: "vpp-dialog-actions-right" };
const _hoisted_55 = { class: "vpp-dialog-head" };
const _hoisted_56 = { class: "vpp-dialog-title-wrap" };
const _hoisted_57 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-kicker" }, "日志", -1));
const _hoisted_58 = { class: "vpp-dialog-title" };
const _hoisted_59 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-log-state" }, [
  /*#__PURE__*/_createElementVNode("span", { class: "vpp-live-dot" }),
  /*#__PURE__*/_createElementVNode("span", null, "实时轮询中")
], -1));
const _hoisted_60 = { class: "vpp-dialog-body" };
const _hoisted_61 = { class: "vpp-dialog-meta" };
const _hoisted_62 = { class: "vpp-meta-chip" };
const _hoisted_63 = { class: "vpp-meta-chip" };
const _hoisted_64 = { class: "vpp-meta-chip" };
const _hoisted_65 = { class: "vpp-dialog-panel vpp-log-panel" };
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
const _hoisted_85 = { class: "vpp-meta-chip" };
const _hoisted_86 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-dialog-hint" }, " 复制会生成一张全新的功能卡片，你可以再手动改网站地址、Cookie、UID 和描述。 ", -1));
const _hoisted_87 = { class: "vpp-dialog-panel" };
const _hoisted_88 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-section-title" }, "复制设置", -1));
const _hoisted_89 = { class: "vpp-form-grid is-single" };
const _hoisted_90 = { class: "vpp-dialog-actions" };
const _hoisted_91 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-dialog-actions-left" }, null, -1));
const _hoisted_92 = { class: "vpp-dialog-actions-right" };

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

let logTimer = null;

const themeValue = computed(() => String(props.themeName || 'light').toLowerCase());
const themeClasses = computed(() => ({
  'is-light-theme': themeValue.value === 'light' || themeValue.value === 'custom',
  'is-dark-theme': themeValue.value === 'dark',
  'is-purple-theme': themeValue.value === 'purple',
  'is-transparent-theme': themeValue.value === 'transparent',
}));

const dashboard = computed(() => status.dashboard || {});
const dashboardCards = computed(() => Array.isArray(dashboard.value.cards) ? dashboard.value.cards : []);
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
const toneSelectItems = computed(() =>
  (panelConfig.value.tone_options || []).map((item) => ({ label: item.label, value: item.key })),
);
const activeDashboardCard = computed(() => cards.value.find((item) => item.card_id === selectedCardId.value) || null);
const selectedLogs = computed(() => {
  const cardId = selectedCardId.value;
  const fallbackLogs = activeDashboardCard.value?.log_items || [];
  const merged = new Map();
  for (const item of [...fallbackLogs, ...(status.history || [])]) {
    if (!item || item.card_id !== cardId) continue
    const key = item.id || `${item.time || ''}-${item.summary || ''}`;
    if (!merged.has(key)) merged.set(key, item);
  }
  return [...merged.values()].sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
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
    const logItems = (status.history || [])
      .filter((item) => item?.card_id === card.id)
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

function toneStyle(tone) {
  const map = {
    emerald: { '--vpp-tone-rgb': '38, 183, 120' },
    azure: { '--vpp-tone-rgb': '67, 126, 255' },
    amber: { '--vpp-tone-rgb': '255, 171, 67' },
    rose: { '--vpp-tone-rgb': '231, 92, 128' },
    violet: { '--vpp-tone-rgb': '150, 117, 255' },
    slate: { '--vpp-tone-rgb': '128, 140, 158' },
  };
  return map[tone] || map.azure
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

function scheduleText(card) {
  if (!card?.enabled) return '已停用'
  if (!card?.auto_run) return '仅手动执行'
  return card?.next_run_time || card?.cron || '等待调度'
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
  selectedCardId.value = card.card_id;
  dialog.config = true;
}

function openLogsDialog(card) {
  selectedCardId.value = card.card_id;
  dialog.logs = true;
}

function openCopyDialog(card) {
  selectedCardId.value = card.card_id;
  copyForm.title = `${card.title} 副本`;
  copyForm.note = card.note || card.module_description || '';
  dialog.copy = true;
}

async function loadStatus(showError = true) {
  try {
    const payload = await props.api.get('/plugin/VuePanel/status');
    status.enabled = !!payload.enabled;
    status.next_run_time = payload.next_run_time || '';
    status.last_run = payload.last_run || '';
    status.history = Array.isArray(payload.history) ? payload.history : [];
    status.dashboard = payload.dashboard || {};
    panelConfig.value = normalizeConfig(payload.config || {});
    lastLogRefresh.value = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error');
    return false
  }
}

async function persistCards(nextCards, successText) {
  const payload = serializeConfig(nextCards);
  const response = await props.api.post('/plugin/VuePanel/config', payload);
  flash(response.message || successText || '配置已保存');
  await loadStatus(false);
  return response
}

async function refreshStatus() {
  loading.refreshAll = true;
  try {
    const response = await props.api.post('/plugin/VuePanel/refresh', {});
    flash(response.message || '状态已刷新');
    await loadStatus(false);
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
    flash(response.message || '已执行启用任务');
    await loadStatus(false);
  } catch (error) {
    flash(error?.message || '执行任务失败', 'error');
  } finally {
    loading.runAll = false;
  }
}

async function saveCardConfig() {
  saving.config = true;
  try {
    let matched = false;
    const nextCards = (panelConfig.value.cards || []).map((item) => {
      if (item.id === editor.id) {
        matched = true;
        return normalizeCard(editor)
      }
      return normalizeCard(item)
    });
    if (!matched) nextCards.push(normalizeCard(editor));
    await persistCards(nextCards, '卡片配置已保存');
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
    flash(response.message || '卡片执行完成');
    await loadStatus(false);
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
    flash(response.message || '卡片状态已刷新');
    await loadStatus(false);
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
    else stopLogPolling();
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
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_textarea = _resolveComponent("v-textarea");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_dialog = _resolveComponent("v-dialog");

  return (_openBlock(), _createElementBlock("div", {
    class: _normalizeClass(["vuepanel-page", themeClasses.value])
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
            class: _normalizeClass(["vpp-card", [{ 'is-enabled': card.enabled, 'is-disabled': !card.enabled }, `level-${runtimeTone(card.level)}`]]),
            style: _normalizeStyle(toneStyle(card.tone))
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
                    _createElementVNode("p", _hoisted_21, _toDisplayString(card.module_summary || 'plugin card'), 1)
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
            _createElementVNode("div", _hoisted_25, [
              _createElementVNode("div", _hoisted_26, [
                _hoisted_27,
                _createElementVNode("span", {
                  class: _normalizeClass(["vpp-mini-pill", `is-${card.enabled ? 'enabled' : 'disabled'}`])
                }, _toDisplayString(card.enabled ? '启用' : '停用'), 3)
              ])
            ]),
            _createElementVNode("div", _hoisted_28, [
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
              }, 1032, ["onClick"]),
              (canDeleteCard(card))
                ? (_openBlock(), _createBlock(_component_v_btn, {
                    key: 0,
                    class: "vpp-action-btn is-delete",
                    variant: "text",
                    "prepend-icon": "mdi-delete-outline",
                    loading: saving.delete && deletingCardId.value === getCardId(card),
                    onClick: $event => (deleteCard(card))
                  }, {
                    default: _withCtx(() => [
                      _createTextVNode(" 删除 ")
                    ]),
                    _: 2
                  }, 1032, ["loading", "onClick"]))
                : _createCommentVNode("", true)
            ])
          ], 6))
        }), 128)),
        (!displayCards.value.length)
          ? (_openBlock(), _createElementBlock("div", _hoisted_29, _toDisplayString(searchQuery.value ? '没有找到匹配的功能模块。' : '当前还没有可展示的功能卡片。'), 1))
          : _createCommentVNode("", true)
      ])
    ]),
    _createVNode(_component_v_dialog, {
      modelValue: dialog.config,
      "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((dialog.config) = $event)),
      "max-width": "760"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, { class: "vpp-dialog-card" }, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_30, [
              _createElementVNode("div", _hoisted_31, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-cog-outline",
                  size: "22",
                  class: "vpp-dialog-icon is-config"
                }),
                _createElementVNode("div", null, [
                  _hoisted_32,
                  _createElementVNode("h3", _hoisted_33, _toDisplayString(editor.title || activeDashboardCard.value?.title || '功能配置'), 1)
                ])
              ]),
              _createElementVNode("span", {
                class: _normalizeClass(["vpp-status-pill", `is-${editor.enabled ? 'enabled' : 'disabled'}`])
              }, _toDisplayString(editor.enabled ? '启用' : '停用'), 3)
            ]),
            _createElementVNode("div", _hoisted_34, [
              _createElementVNode("div", _hoisted_35, [
                _createElementVNode("span", _hoisted_36, _toDisplayString(moduleMeta(editor.module_key).label), 1),
                _createElementVNode("span", _hoisted_37, _toDisplayString(editor.site_name || '--'), 1),
                _createElementVNode("span", _hoisted_38, _toDisplayString(scheduleText(editor)), 1)
              ]),
              _hoisted_39,
              _createElementVNode("div", _hoisted_40, [
                _hoisted_41,
                _createElementVNode("div", _hoisted_42, [
                  _createElementVNode("label", _hoisted_43, [
                    _hoisted_44,
                    _createVNode(_component_v_switch, {
                      modelValue: editor.enabled,
                      "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((editor.enabled) = $event)),
                      "hide-details": "",
                      color: "primary",
                      density: "compact"
                    }, null, 8, ["modelValue"])
                  ]),
                  _createElementVNode("label", _hoisted_45, [
                    _hoisted_46,
                    _createVNode(_component_v_switch, {
                      modelValue: editor.auto_run,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((editor.auto_run) = $event)),
                      "hide-details": "",
                      color: "primary",
                      density: "compact"
                    }, null, 8, ["modelValue"])
                  ]),
                  _createElementVNode("label", _hoisted_47, [
                    _hoisted_48,
                    _createVNode(_component_v_switch, {
                      modelValue: editor.notify,
                      "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((editor.notify) = $event)),
                      "hide-details": "",
                      color: "primary",
                      density: "compact"
                    }, null, 8, ["modelValue"])
                  ])
                ])
              ]),
              _createElementVNode("div", _hoisted_49, [
                _hoisted_50,
                _createElementVNode("div", _hoisted_51, [
                  _createVNode(_component_v_text_field, {
                    modelValue: editor.title,
                    "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((editor.title) = $event)),
                    label: "功能名称",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_v_text_field, {
                    modelValue: editor.site_name,
                    "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((editor.site_name) = $event)),
                    label: "网站名称",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_v_text_field, {
                    modelValue: editor.site_url,
                    "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((editor.site_url) = $event)),
                    label: "网站地址",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto",
                    class: "vpp-field-span-2"
                  }, null, 8, ["modelValue"]),
                  (editor.module_key === 'newapi_checkin')
                    ? (_openBlock(), _createBlock(_component_v_text_field, {
                        key: 0,
                        modelValue: editor.uid,
                        "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((editor.uid) = $event)),
                        label: "UID",
                        variant: "outlined",
                        density: "compact",
                        "hide-details": "auto"
                      }, null, 8, ["modelValue"]))
                    : _createCommentVNode("", true),
                  _createVNode(BaseCronField, {
                    modelValue: editor.cron,
                    "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((editor.cron) = $event)),
                    label: "Cron",
                    class: "vpp-field-span-2 vpp-cron-field"
                  }, null, 8, ["modelValue"]),
                  _createVNode(_component_v_select, {
                    modelValue: editor.tone,
                    "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((editor.tone) = $event)),
                    items: toneSelectItems.value,
                    "item-title": "label",
                    "item-value": "value",
                    label: "卡片色调",
                    variant: "outlined",
                    density: "compact",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue", "items"]),
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
            _createElementVNode("div", _hoisted_52, [
              _createElementVNode("div", _hoisted_53, [
                (canDeleteCard(activeDashboardCard.value || editor))
                  ? (_openBlock(), _createBlock(_component_v_btn, {
                      key: 0,
                      class: "vpp-action-btn is-delete",
                      variant: "text",
                      "prepend-icon": "mdi-delete-outline",
                      loading: saving.delete && deletingCardId.value === editor.id,
                      onClick: deleteCurrentCard
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(" 删除卡片 ")
                      ]),
                      _: 1
                    }, 8, ["loading"]))
                  : _createCommentVNode("", true)
              ]),
              _createElementVNode("div", _hoisted_54, [
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
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: dialog.logs,
      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((dialog.logs) = $event)),
      "max-width": "900"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, { class: "vpp-dialog-card" }, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_55, [
              _createElementVNode("div", _hoisted_56, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-text-box-outline",
                  size: "22",
                  class: "vpp-dialog-icon is-logs"
                }),
                _createElementVNode("div", null, [
                  _hoisted_57,
                  _createElementVNode("h3", _hoisted_58, _toDisplayString(activeDashboardCard.value?.title || '实时日志'), 1)
                ])
              ]),
              _hoisted_59
            ]),
            _createElementVNode("div", _hoisted_60, [
              _createElementVNode("div", _hoisted_61, [
                _createElementVNode("span", _hoisted_62, _toDisplayString(activeDashboardCard.value?.site_name || '--'), 1),
                _createElementVNode("span", _hoisted_63, _toDisplayString(activeDashboardCard.value?.site_domain || activeDashboardCard.value?.site_url || '--'), 1),
                _createElementVNode("span", _hoisted_64, "最近刷新 " + _toDisplayString(lastLogRefresh.value || '--'), 1)
              ]),
              _createElementVNode("div", _hoisted_65, [
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
        })
      ]),
      _: 1
    }, 8, ["modelValue"]),
    _createVNode(_component_v_dialog, {
      modelValue: dialog.copy,
      "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((dialog.copy) = $event)),
      "max-width": "560"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, { class: "vpp-dialog-card" }, {
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
                _createElementVNode("span", _hoisted_84, _toDisplayString(activeDashboardCard.value?.module_name || '--'), 1),
                _createElementVNode("span", _hoisted_85, _toDisplayString(activeDashboardCard.value?.site_name || '--'), 1)
              ]),
              _hoisted_86,
              _createElementVNode("div", _hoisted_87, [
                _hoisted_88,
                _createElementVNode("div", _hoisted_89, [
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
            _createElementVNode("div", _hoisted_90, [
              _hoisted_91,
              _createElementVNode("div", _hoisted_92, [
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
        })
      ]),
      _: 1
    }, 8, ["modelValue"])
  ], 2))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-2594591a"]]);

export { _export_sfc as _, PageView as default };
