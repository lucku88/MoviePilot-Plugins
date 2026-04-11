import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_14d8dc9e_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-14d8dc9e"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vp-shell" };
const _hoisted_2 = { class: "vp-card vp-hero" };
const _hoisted_3 = { class: "vp-hero-topbar" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-badge" }, "Vue-魔丸", -1));
const _hoisted_5 = { class: "vp-hero-bottom" };
const _hoisted_6 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-copy" }, [
  /*#__PURE__*/_createElementVNode("h1", { class: "vp-title" }, "插件配置"),
  /*#__PURE__*/_createElementVNode("p", { class: "vp-subtitle" }, "兑换、搬砖、清沙滩、炼造、获取执行记录。")
], -1));
const _hoisted_7 = { class: "vp-actions" };
const _hoisted_8 = { class: "vp-card" };
const _hoisted_9 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "vp-section-title" }, "⚙️ 基本设置", -1));
const _hoisted_10 = { class: "vp-switch-grid" };
const _hoisted_11 = { class: "vp-switch-card" };
const _hoisted_12 = { class: "vp-switch-card" };
const _hoisted_13 = { class: "vp-switch-card" };
const _hoisted_14 = { class: "vp-switch-card" };
const _hoisted_15 = { class: "vp-card vp-panel" };
const _hoisted_16 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "vp-section-title" }, "🧩 功能设置", -1));
const _hoisted_17 = { class: "vp-switch-grid" };
const _hoisted_18 = { class: "vp-switch-card" };
const _hoisted_19 = { class: "vp-switch-card" };
const _hoisted_20 = { class: "vp-switch-card" };
const _hoisted_21 = { class: "vp-switch-card" };
const _hoisted_22 = { class: "vp-switch-card" };
const _hoisted_23 = { class: "vp-switch-card" };
const _hoisted_24 = { class: "vp-field-grid" };
const _hoisted_25 = { class: "vp-field-card vp-field-span-2" };
const _hoisted_26 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-field-label" }, "站点 Cookie", -1));
const _hoisted_27 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-note" }, "启用【使用站点 Cookie】后自动读取站点配置，关闭后才可手动修改。", -1));
const _hoisted_28 = { class: "vp-field-card" };
const _hoisted_29 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-field-label" }, "执行周期", -1));
const _hoisted_30 = { class: "vp-field-card" };
const _hoisted_31 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-field-label" }, "保留材料数量", -1));
const _hoisted_32 = { class: "vp-field-card" };
const _hoisted_33 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-field-label" }, "保留魔丸数量", -1));

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


const pluginBase = '/plugin/VuePill';

const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;





const saving = ref(false);
const rootEl = ref(null);
const isDarkTheme = ref(false);
const message = reactive({ text: '', type: 'success' });
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  move_delay_min_ms: 30,
  move_delay_max_ms: 80,
  ready_retry_seconds: 60,
  reserve_material_count: 0,
  reserve_magic_pill_count: 0,
});

const cookieReadonly = computed(() => !!config.auto_cookie);
const cookieFieldValue = computed({
  get() {
    if (config.auto_cookie) return truncateCookie(config.cookie)
    return config.cookie
  },
  set(value) {
    if (!config.auto_cookie) config.cookie = value || '';
  },
});

let themeObserver = null;
let mediaQuery = null;

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function truncateCookie(value) {
  const text = String(value || '').trim();
  if (!text) return ''
  return text.length > 36 ? `${text.slice(0, 36)}...` : text
}

function applyConfig(data = {}) {
  Object.assign(config, {
    ...config,
    ...data,
  });
}

async function loadConfig() {
  const data = await props.api.get(`${pluginBase}/config`);
  applyConfig(data || {});
}

async function saveConfig() {
  saving.value = true;
  try {
    const result = await props.api.post(`${pluginBase}/config`, { ...config });
    applyConfig(result?.config || {});
    flash(result?.message || '配置已保存');
  } catch (error) {
    flash(error?.message || '保存失败', 'error');
  } finally {
    saving.value = false;
  }
}

async function syncCookie() {
  saving.value = true;
  try {
    const result = await props.api.get(`${pluginBase}/cookie`);
    applyConfig(result?.config || {});
    flash(result?.message || 'Cookie 已同步');
  } catch (error) {
    flash(error?.message || '同步失败', 'error');
  } finally {
    saving.value = false;
  }
}

function findThemeNode() {
  let current = rootEl.value;
  while (current) {
    if (current.getAttribute?.('data-theme')) return current
    const classValue = String(current.className || '').toLowerCase();
    if (classValue.includes('theme') || classValue.includes('v-theme--') || classValue.includes('dark') || classValue.includes('light')) {
      return current
    }
    current = current.parentElement;
  }
  const bodyClass = String(document.body?.className || '').toLowerCase();
  if (document.body?.getAttribute('data-theme') || bodyClass.includes('theme') || bodyClass.includes('v-theme--') || bodyClass.includes('dark') || bodyClass.includes('light')) {
    return document.body
  }
  const rootClass = String(document.documentElement?.className || '').toLowerCase();
  if (document.documentElement?.getAttribute('data-theme') || rootClass.includes('theme') || rootClass.includes('v-theme--') || rootClass.includes('dark') || rootClass.includes('light')) {
    return document.documentElement
  }
  return null
}

function getThemeNodes() {
  return [...new Set([findThemeNode(), document.documentElement, document.body].filter(Boolean))]
}

function nodeHasDarkHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase();
  const classValue = String(node?.className || '').toLowerCase();
  return ['dark', 'purple', 'transparent'].includes(themeValue)
    || classValue.includes('dark')
    || classValue.includes('theme-dark')
    || classValue.includes('v-theme--dark')
}

function nodeHasLightHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase();
  const classValue = String(node?.className || '').toLowerCase();
  return themeValue === 'light'
    || classValue.includes('light')
    || classValue.includes('theme-light')
    || classValue.includes('v-theme--light')
}

function detectTheme() {
  const nodes = getThemeNodes();
  if (nodes.some(nodeHasDarkHint)) {
    isDarkTheme.value = true;
    return
  }
  if (nodes.some(nodeHasLightHint)) {
    isDarkTheme.value = false;
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

function bindThemeObserver() {
  detectTheme();
  if (window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme);
    getThemeNodes().forEach((node) => {
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
  const _component_VCronField = _resolveComponent("VCronField");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["vp-config", { 'is-dark-theme': isDarkTheme.value }])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("header", _hoisted_2, [
        _createElementVNode("div", _hoisted_3, [
          _hoisted_4,
          _createVNode(_component_v_btn, {
            variant: "text",
            class: "vp-close-btn",
            onClick: closePlugin
          }, {
            default: _withCtx(() => [
              _createTextVNode("关闭")
            ]),
            _: 1
          })
        ]),
        _createElementVNode("div", _hoisted_5, [
          _hoisted_6,
          _createElementVNode("div", _hoisted_7, [
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
              color: "warning",
              variant: "flat",
              loading: saving.value,
              onClick: syncCookie
            }, {
              default: _withCtx(() => [
                _createTextVNode("同步 Cookie")
              ]),
              _: 1
            }, 8, ["loading"]),
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
            }, 8, ["loading"])
          ])
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
      _createElementVNode("section", _hoisted_8, [
        _hoisted_9,
        _createElementVNode("div", _hoisted_10, [
          _createElementVNode("div", _hoisted_11, [
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              class: "vp-switch",
              label: "启用插件",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_12, [
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.use_proxy) = $event)),
              class: "vp-switch",
              label: "使用代理",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_13, [
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.notify) = $event)),
              class: "vp-switch",
              label: "开启通知",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_14, [
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.onlyonce) = $event)),
              class: "vp-switch",
              label: "立即运行一次",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ])
      ]),
      _createElementVNode("section", _hoisted_15, [
        _hoisted_16,
        _createElementVNode("div", _hoisted_17, [
          _createElementVNode("div", _hoisted_18, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_cookie,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.auto_cookie) = $event)),
              class: "vp-switch",
              label: "使用站点 Cookie",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_19, [
            _createVNode(_component_v_switch, {
              modelValue: config.enable_brick,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.enable_brick) = $event)),
              class: "vp-switch",
              label: "搬砖",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_20, [
            _createVNode(_component_v_switch, {
              modelValue: config.enable_beach,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.enable_beach) = $event)),
              class: "vp-switch",
              label: "清沙滩",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_21, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_craft,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.auto_craft) = $event)),
              class: "vp-switch",
              label: "炼造",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_22, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_exchange,
              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.auto_exchange) = $event)),
              class: "vp-switch",
              label: "兑换",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_23, [
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.force_ipv4) = $event)),
              class: "vp-switch",
              label: "优先 IPv4",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("div", _hoisted_24, [
          _createElementVNode("div", _hoisted_25, [
            _hoisted_26,
            _createVNode(_component_v_text_field, {
              modelValue: cookieFieldValue.value,
              "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((cookieFieldValue).value = $event)),
              label: "站点 Cookie",
              variant: "outlined",
              density: "comfortable",
              disabled: cookieReadonly.value,
              readonly: cookieReadonly.value,
              placeholder: cookieReadonly.value ? '启用站点 Cookie 后自动同步' : '例如 c_secure_pass=...',
              "hide-details": "auto"
            }, null, 8, ["modelValue", "disabled", "readonly", "placeholder"]),
            _hoisted_27
          ]),
          _createElementVNode("div", _hoisted_28, [
            _hoisted_29,
            _createVNode(_component_VCronField, {
              modelValue: config.brick_cron,
              "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.brick_cron) = $event)),
              label: "搬砖执行周期(cron)",
              density: "comfortable",
              class: "vp-cron-field"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_30, [
            _hoisted_31,
            _createVNode(_component_v_text_field, {
              modelValue: config.reserve_material_count,
              "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.reserve_material_count) = $event)),
              label: "每种材料保留数量",
              type: "number",
              variant: "outlined",
              density: "comfortable",
              "hide-details": "auto"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_32, [
            _hoisted_33,
            _createVNode(_component_v_text_field, {
              modelValue: config.reserve_magic_pill_count,
              "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.reserve_magic_pill_count) = $event)),
              label: "魔丸保留数量",
              type: "number",
              variant: "outlined",
              density: "comfortable",
              "hide-details": "auto"
            }, null, 8, ["modelValue"])
          ])
        ])
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-14d8dc9e"]]);

export { ConfigView as default };
