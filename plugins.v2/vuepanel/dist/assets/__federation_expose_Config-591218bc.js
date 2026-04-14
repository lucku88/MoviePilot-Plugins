import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_5805791a_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeStyle:_normalizeStyle,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-5805791a"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vpc-shell" };
const _hoisted_2 = { class: "vpc-card vpc-hero" };
const _hoisted_3 = { class: "vpc-copy" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-badge" }, "Vue-面板", -1));
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h1", { class: "vpc-title" }, "配置页", -1));
const _hoisted_6 = { class: "vpc-chip-row" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpc-chip" }, "固定任务 2 个", -1));
const _hoisted_8 = { class: "vpc-chip" };
const _hoisted_9 = { class: "vpc-chip" };
const _hoisted_10 = { class: "vpc-action-grid" };
const _hoisted_11 = { class: "vpc-card" };
const _hoisted_12 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-section-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "插件级设置"),
    /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "全局选项")
  ])
], -1));
const _hoisted_13 = { class: "vpc-switch-grid plugin" };
const _hoisted_14 = { class: "vpc-switch-card" };
const _hoisted_15 = { class: "vpc-switch-card" };
const _hoisted_16 = { class: "vpc-switch-card" };
const _hoisted_17 = { class: "vpc-switch-card" };
const _hoisted_18 = { class: "vpc-switch-card" };
const _hoisted_19 = { class: "vpc-field-grid plugin" };
const _hoisted_20 = { class: "vpc-card" };
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-section-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "固定模块"),
    /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "思齐签到 / HNR领取")
  ]),
  /*#__PURE__*/_createElementVNode("div", { class: "vpc-note" }, "这两个任务固定各 1 张配置卡，不提供新增。")
], -1));
const _hoisted_22 = { class: "vpc-fixed-grid" };
const _hoisted_23 = { class: "vpc-editor-head" };
const _hoisted_24 = { class: "vpc-kicker" };
const _hoisted_25 = { class: "vpc-editor-title" };
const _hoisted_26 = { class: "vpc-editor-site" };
const _hoisted_27 = { class: "vpc-switch-grid compact single" };
const _hoisted_28 = { class: "vpc-switch-card" };
const _hoisted_29 = { class: "vpc-switch-card" };
const _hoisted_30 = { class: "vpc-field-grid fixed" };
const _hoisted_31 = { class: "vpc-field-card vpc-span-2" };
const _hoisted_32 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-field-label" }, "Cookie", -1));
const _hoisted_33 = { class: "vpc-note" };
const _hoisted_34 = { class: "vpc-card" };
const _hoisted_35 = { class: "vpc-section-head" };
const _hoisted_36 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "多站点模块"),
  /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "New API签到")
], -1));
const _hoisted_37 = { class: "vpc-toolbar-actions" };
const _hoisted_38 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-note" }, "所有 New API 站点都归在这个模块里，每个站点独立保存启用、定时运行、网站和 Cookie。", -1));
const _hoisted_39 = {
  key: 0,
  class: "vpc-empty"
};
const _hoisted_40 = {
  key: 1,
  class: "vpc-site-grid"
};
const _hoisted_41 = { class: "vpc-editor-head" };
const _hoisted_42 = { class: "vpc-kicker" };
const _hoisted_43 = { class: "vpc-editor-title" };
const _hoisted_44 = { class: "vpc-inline-actions" };
const _hoisted_45 = { class: "vpc-switch-grid compact" };
const _hoisted_46 = { class: "vpc-switch-card" };
const _hoisted_47 = { class: "vpc-switch-card" };
const _hoisted_48 = { class: "vpc-field-grid newapi" };
const _hoisted_49 = { class: "vpc-field-card vpc-span-2" };
const _hoisted_50 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-field-label" }, "Cookie", -1));

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Config',
  props: { initialConfig: { type: Object, default: () => ({}) }, api: { type: Object, default: () => ({}) } },
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;




const rootEl = ref(null);
const isDarkTheme = ref(false);
const saving = ref(false);
const message = reactive({ text: '', type: 'success' });
const moduleItems = ref([]);
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  cron: '5 8 * * *',
  http_timeout: 15,
  http_retry_times: 3,
  random_delay_max_seconds: 5,
  cards: [],
});

let themeObserver = null;
let mediaQuery = null;

const fixedCards = computed(() => ['siqi_sign', 'hnr_claim'].map((key) => ensureFixedCard(key)));
const newApiCards = computed(() => config.cards.filter((card) => card.module_key === 'newapi_checkin'));

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value))
}

function moduleMeta(moduleKey) {
  return moduleItems.value.find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    icon: '🧩',
    default_site_name: '',
    default_site_url: '',
    tone: 'azure',
  }
}

function nextCardId(moduleKey) {
  return `${moduleKey}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpc-tone-rgb': '40,181,120' },
    azure: { '--vpc-tone-rgb': '46,134,255' },
    amber: { '--vpc-tone-rgb': '255,170,63' },
    rose: { '--vpc-tone-rgb': '230,92,124' },
    violet: { '--vpc-tone-rgb': '132,108,255' },
    slate: { '--vpc-tone-rgb': '120,132,155' },
  };
  return map[tone] || map.azure
}

function buildFixedCard(moduleKey, current = {}) {
  const meta = moduleMeta(moduleKey);
  return {
    id: moduleKey,
    title: meta.label,
    module_key: moduleKey,
    site_name: meta.default_site_name || '思齐主站',
    site_url: meta.default_site_url || 'https://si-qi.xyz',
    enabled: !!current.enabled,
    auto_run: current.auto_run !== false,
    show_status: true,
    notify: current.notify !== false,
    tone: meta.tone || current.tone || 'azure',
    cookie: String(current.cookie || ''),
    uid: '',
    note: String(current.note || ''),
  }
}

function buildNewApiCard(current = {}) {
  const meta = moduleMeta('newapi_checkin');
  return {
    id: current.id || nextCardId('newapi_checkin'),
    title: current.title || current.site_name || meta.label,
    module_key: 'newapi_checkin',
    site_name: current.site_name || meta.default_site_name || '',
    site_url: current.site_url || meta.default_site_url || '',
    enabled: !!current.enabled,
    auto_run: current.auto_run !== false,
    show_status: true,
    notify: current.notify !== false,
    tone: current.tone || meta.tone || 'azure',
    cookie: String(current.cookie || ''),
    uid: String(current.uid || '225'),
    note: String(current.note || ''),
  }
}

function ensureStructure(cards = []) {
  const fixedMap = new Map();
  const newApi = [];
  for (const item of cards) {
    if (!item || typeof item !== 'object') continue
    if (item.module_key === 'siqi_sign' || item.module_key === 'hnr_claim') {
      if (!fixedMap.has(item.module_key)) fixedMap.set(item.module_key, buildFixedCard(item.module_key, item));
      continue
    }
    if (item.module_key === 'newapi_checkin') newApi.push(buildNewApiCard(item));
  }

  const normalized = [
    fixedMap.get('siqi_sign') || buildFixedCard('siqi_sign'),
    fixedMap.get('hnr_claim') || buildFixedCard('hnr_claim'),
    ...(newApi.length ? newApi : [buildNewApiCard()]),
  ];

  config.cards.splice(0, config.cards.length, ...normalized);
}

function ensureFixedCard(moduleKey) {
  let card = config.cards.find((item) => item.module_key === moduleKey);
  if (!card) {
    card = buildFixedCard(moduleKey);
    config.cards.push(card);
  }
  return card
}

function addNewApiCard() {
  config.cards.push(buildNewApiCard());
}

function removeNewApiCard(cardId) {
  const index = config.cards.findIndex((card) => card.id === cardId && card.module_key === 'newapi_checkin');
  if (index >= 0) config.cards.splice(index, 1);
  if (!newApiCards.value.length) addNewApiCard();
}

function serializeConfig() {
  const cards = [
    buildFixedCard('siqi_sign', ensureFixedCard('siqi_sign')),
    buildFixedCard('hnr_claim', ensureFixedCard('hnr_claim')),
    ...newApiCards.value.map((card) => buildNewApiCard({
      ...card,
      title: String(card.site_name || card.title || 'New API签到').trim() || 'New API签到',
    })),
  ];

  return {
    ...deepClone(config),
    cards,
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VuePanel/config');
    moduleItems.value = res.module_options || [];
    Object.assign(config, {
      enabled: !!res.enabled,
      notify: !!res.notify,
      onlyonce: !!res.onlyonce,
      use_proxy: !!res.use_proxy,
      force_ipv4: res.force_ipv4 !== false,
      cron: res.cron || '5 8 * * *',
      http_timeout: Number(res.http_timeout || 15),
      http_retry_times: Number(res.http_retry_times || 3),
      random_delay_max_seconds: Number(res.random_delay_max_seconds || 5),
      cards: [],
    });
    ensureStructure(deepClone(res.cards || []));
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error');
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const res = await props.api.post('/plugin/VuePanel/config', serializeConfig());
    flash(res.message || '配置已保存');
    await loadConfig();
  } catch (error) {
    flash(error?.message || '保存失败', 'error');
  } finally {
    saving.value = false;
  }
}

function findThemeNode() {
  let current = rootEl.value;
  while (current) {
    if (current.getAttribute?.('data-theme')) return current
    const cls = String(current.className || '').toLowerCase();
    if (cls.includes('theme') || cls.includes('v-theme--') || cls.includes('dark') || cls.includes('light')) return current
    current = current.parentElement;
  }
  return document.body
}

function detectTheme() {
  const nodes = [findThemeNode(), document.documentElement, document.body].filter(Boolean);
  const isDark = nodes.some((node) => {
    const theme = String(node?.getAttribute?.('data-theme') || '').toLowerCase();
    const cls = String(node?.className || '').toLowerCase();
    return ['dark', 'purple', 'transparent'].includes(theme) || cls.includes('dark') || cls.includes('theme-dark') || cls.includes('v-theme--dark')
  });
  isDarkTheme.value = isDark || !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

function bindThemeObserver() {
  detectTheme();
  if (window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme)
    ;[findThemeNode(), document.documentElement, document.body].filter(Boolean).forEach((node) => {
      themeObserver.observe(node, { attributes: true, attributeFilter: ['data-theme', 'class'] });
    });
  }
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener?.('change', detectTheme);
  }
}

function closePlugin() {
  emit('close');
}

onMounted(async () => {
  bindThemeObserver();
  await loadConfig();
});

onBeforeUnmount(() => {
  themeObserver?.disconnect?.();
  mediaQuery?.removeEventListener?.('change', detectTheme);
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_text_field = _resolveComponent("v-text-field");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["vuepanel-config", { 'is-dark-theme': isDarkTheme.value }])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("header", _hoisted_2, [
        _createElementVNode("div", _hoisted_3, [
          _hoisted_4,
          _hoisted_5,
          _createElementVNode("div", _hoisted_6, [
            _hoisted_7,
            _createElementVNode("span", _hoisted_8, "New API 站点 " + _toDisplayString(newApiCards.value.length), 1),
            _createElementVNode("span", _hoisted_9, "插件 " + _toDisplayString(config.enabled ? '已启用' : '未启用'), 1)
          ])
        ]),
        _createElementVNode("div", _hoisted_10, [
          _createVNode(_component_v_btn, {
            color: "primary",
            variant: "flat",
            loading: saving.value,
            onClick: saveConfig
          }, {
            default: _withCtx(() => [
              _createTextVNode("保存")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            variant: "text",
            onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'page')))
          }, {
            default: _withCtx(() => [
              _createTextVNode("返回状态页")
            ]),
            _: 1
          }),
          _createVNode(_component_v_btn, {
            variant: "text",
            onClick: closePlugin
          }, {
            default: _withCtx(() => [
              _createTextVNode("关闭")
            ]),
            _: 1
          })
        ])
      ]),
      (message.text)
        ? (_openBlock(), _createBlock(_component_v_alert, {
            key: 0,
            type: message.type,
            variant: "tonal",
            rounded: "xl"
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(message.text), 1)
            ]),
            _: 1
          }, 8, ["type"]))
        : _createCommentVNode("", true),
      _createElementVNode("section", _hoisted_11, [
        _hoisted_12,
        _createElementVNode("div", _hoisted_13, [
          _createElementVNode("div", _hoisted_14, [
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              label: "启用插件",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_15, [
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.notify) = $event)),
              label: "开启通知",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_16, [
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.onlyonce) = $event)),
              label: "保存后执行一次",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_17, [
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.use_proxy) = $event)),
              label: "使用代理",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_18, [
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.force_ipv4) = $event)),
              label: "优先 IPv4",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("div", _hoisted_19, [
          _createVNode(_component_v_text_field, {
            modelValue: config.cron,
            "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.cron) = $event)),
            label: "插件兜底 Cron",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_timeout,
            "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.http_timeout) = $event)),
            modelModifiers: { number: true },
            label: "超时秒数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_times,
            "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.http_retry_times) = $event)),
            modelModifiers: { number: true },
            label: "重试次数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.random_delay_max_seconds,
            "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.random_delay_max_seconds) = $event)),
            modelModifiers: { number: true },
            label: "随机延迟",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"])
        ])
      ]),
      _createElementVNode("section", _hoisted_20, [
        _hoisted_21,
        _createElementVNode("div", _hoisted_22, [
          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(fixedCards.value, (card) => {
            return (_openBlock(), _createElementBlock("article", {
              key: card.id,
              class: "vpc-editor fixed",
              style: _normalizeStyle(toneStyle(card.tone))
            }, [
              _createElementVNode("div", _hoisted_23, [
                _createElementVNode("div", null, [
                  _createElementVNode("div", _hoisted_24, _toDisplayString(moduleMeta(card.module_key).label), 1),
                  _createElementVNode("h3", _hoisted_25, _toDisplayString(card.title), 1)
                ]),
                _createElementVNode("span", _hoisted_26, _toDisplayString(card.site_url), 1)
              ]),
              _createElementVNode("div", _hoisted_27, [
                _createElementVNode("div", _hoisted_28, [
                  _createVNode(_component_v_switch, {
                    modelValue: card.enabled,
                    "onUpdate:modelValue": $event => ((card.enabled) = $event),
                    label: "启用",
                    density: "compact",
                    "hide-details": "",
                    inset: ""
                  }, null, 8, ["modelValue", "onUpdate:modelValue"])
                ]),
                _createElementVNode("div", _hoisted_29, [
                  _createVNode(_component_v_switch, {
                    modelValue: card.auto_run,
                    "onUpdate:modelValue": $event => ((card.auto_run) = $event),
                    label: "定时运行",
                    density: "compact",
                    "hide-details": "",
                    inset: ""
                  }, null, 8, ["modelValue", "onUpdate:modelValue"])
                ])
              ]),
              _createElementVNode("div", _hoisted_30, [
                _createElementVNode("div", _hoisted_31, [
                  _hoisted_32,
                  _createVNode(_component_v_text_field, {
                    modelValue: card.cookie,
                    "onUpdate:modelValue": $event => ((card.cookie) = $event),
                    label: "站点 Cookie",
                    variant: "outlined",
                    density: "comfortable",
                    "hide-details": "auto"
                  }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                  _createElementVNode("div", _hoisted_33, _toDisplayString(card.module_key === 'hnr_claim' ? '和思齐签到共用同站 Cookie。' : '填写思齐站点 Cookie 后可执行。'), 1)
                ])
              ])
            ], 4))
          }), 128))
        ])
      ]),
      _createElementVNode("section", _hoisted_34, [
        _createElementVNode("div", _hoisted_35, [
          _hoisted_36,
          _createElementVNode("div", _hoisted_37, [
            _createVNode(_component_v_btn, {
              color: "info",
              variant: "flat",
              onClick: addNewApiCard
            }, {
              default: _withCtx(() => [
                _createTextVNode("新增站点")
              ]),
              _: 1
            })
          ])
        ]),
        _hoisted_38,
        (!newApiCards.value.length)
          ? (_openBlock(), _createElementBlock("div", _hoisted_39, "当前没有 New API 站点，点击“新增站点”创建。"))
          : (_openBlock(), _createElementBlock("div", _hoisted_40, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(newApiCards.value, (card, index) => {
                return (_openBlock(), _createElementBlock("article", {
                  key: card.id,
                  class: "vpc-editor",
                  style: _normalizeStyle(toneStyle(card.tone))
                }, [
                  _createElementVNode("div", _hoisted_41, [
                    _createElementVNode("div", null, [
                      _createElementVNode("div", _hoisted_42, "站点 " + _toDisplayString(index + 1), 1),
                      _createElementVNode("h3", _hoisted_43, _toDisplayString(card.site_name || `New API 站点 ${index + 1}`), 1)
                    ]),
                    _createElementVNode("div", _hoisted_44, [
                      _createVNode(_component_v_btn, {
                        size: "small",
                        variant: "text",
                        color: "error",
                        onClick: $event => (removeNewApiCard(card.id))
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode("删除")
                        ]),
                        _: 2
                      }, 1032, ["onClick"])
                    ])
                  ]),
                  _createElementVNode("div", _hoisted_45, [
                    _createElementVNode("div", _hoisted_46, [
                      _createVNode(_component_v_switch, {
                        modelValue: card.enabled,
                        "onUpdate:modelValue": $event => ((card.enabled) = $event),
                        label: "启用",
                        density: "compact",
                        "hide-details": "",
                        inset: ""
                      }, null, 8, ["modelValue", "onUpdate:modelValue"])
                    ]),
                    _createElementVNode("div", _hoisted_47, [
                      _createVNode(_component_v_switch, {
                        modelValue: card.auto_run,
                        "onUpdate:modelValue": $event => ((card.auto_run) = $event),
                        label: "定时运行",
                        density: "compact",
                        "hide-details": "",
                        inset: ""
                      }, null, 8, ["modelValue", "onUpdate:modelValue"])
                    ])
                  ]),
                  _createElementVNode("div", _hoisted_48, [
                    _createVNode(_component_v_text_field, {
                      modelValue: card.site_name,
                      "onUpdate:modelValue": $event => ((card.site_name) = $event),
                      label: "网站名称",
                      variant: "outlined",
                      density: "comfortable",
                      "hide-details": "auto"
                    }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: card.site_url,
                      "onUpdate:modelValue": $event => ((card.site_url) = $event),
                      label: "网站地址",
                      variant: "outlined",
                      density: "comfortable",
                      "hide-details": "auto"
                    }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                    _createVNode(_component_v_text_field, {
                      modelValue: card.uid,
                      "onUpdate:modelValue": $event => ((card.uid) = $event),
                      label: "UID",
                      variant: "outlined",
                      density: "comfortable",
                      "hide-details": "auto"
                    }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                    _createElementVNode("div", _hoisted_49, [
                      _hoisted_50,
                      _createVNode(_component_v_text_field, {
                        modelValue: card.cookie,
                        "onUpdate:modelValue": $event => ((card.cookie) = $event),
                        label: "站点 Cookie",
                        variant: "outlined",
                        density: "comfortable",
                        "hide-details": "auto"
                      }, null, 8, ["modelValue", "onUpdate:modelValue"])
                    ])
                  ])
                ], 4))
              }), 128))
            ]))
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-5805791a"]]);

export { ConfigView as default };
