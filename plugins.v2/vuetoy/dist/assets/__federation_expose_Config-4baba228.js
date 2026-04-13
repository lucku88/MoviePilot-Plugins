import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_664098f1_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-664098f1"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vtc-shell" };
const _hoisted_2 = { class: "vtc-card vtc-hero" };
const _hoisted_3 = { class: "vtc-copy" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vtc-badge" }, "Vue-玩偶", -1));
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h1", { class: "vtc-title" }, "插件配置", -1));
const _hoisted_6 = { class: "vtc-chip-row" };
const _hoisted_7 = { class: "vtc-chip" };
const _hoisted_8 = { class: "vtc-action-grid" };
const _hoisted_9 = { class: "vtc-card" };
const _hoisted_10 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "vtc-section-title" }, "⚙️ 基本设置", -1));
const _hoisted_11 = { class: "vtc-switch-grid" };
const _hoisted_12 = { class: "vtc-switch-card" };
const _hoisted_13 = { class: "vtc-switch-card" };
const _hoisted_14 = { class: "vtc-switch-card" };
const _hoisted_15 = { class: "vtc-switch-card" };
const _hoisted_16 = { class: "vtc-card" };
const _hoisted_17 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "vtc-section-title" }, "🧩 功能设置", -1));
const _hoisted_18 = { class: "vtc-switch-grid" };
const _hoisted_19 = { class: "vtc-switch-card" };
const _hoisted_20 = { class: "vtc-switch-card" };
const _hoisted_21 = { class: "vtc-switch-card" };
const _hoisted_22 = { class: "vtc-switch-card" };
const _hoisted_23 = { class: "vtc-field-grid" };
const _hoisted_24 = { class: "vtc-field-card" };
const _hoisted_25 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vtc-field-label" }, "站点 Cookie", -1));
const _hoisted_26 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vtc-note" }, "开启使用站点 Cookie 后会自动获取已配置站点的 Cookie，关闭后才可以手动修改。", -1));

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


const pluginBase = '/plugin/VueToy';

const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;





const rootEl = ref(null);
const isDarkTheme = ref(false);
const saving = ref(false);
const message = reactive({ text: '', type: 'success' });
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  auto_collect: true,
  auto_place: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
});

const cookieReadonly = computed(() => !!config.auto_cookie);
const cookieFieldValue = computed({
  get() {
    if (config.auto_cookie) {
      return truncateCookie(config.cookie)
    }
    return config.cookie
  },
  set(value) {
    if (!config.auto_cookie) {
      config.cookie = value || '';
    }
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
  return text.length > 48 ? `${text.slice(0, 48)}...` : text
}

function applyConfig(data = {}) {
  const { capture_tips, ...rest } = data || {};
  Object.assign(config, { ...config, ...rest });
}

async function loadConfig() {
  try {
    const data = await props.api.get(`${pluginBase}/config`);
    applyConfig(data || {});
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error');
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const result = await props.api.post(`${pluginBase}/config`, { ...config });
    applyConfig(result?.config || {});
    flash(result?.message || '配置已保存');
    if (config.onlyonce) {
      config.onlyonce = false;
    }
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

function closePlugin() {
  emit('close');
}

function findThemeNode() {
  let current = rootEl.value;
  while (current) {
    if (current.getAttribute?.('data-theme') || current.className) return current
    current = current.parentElement;
  }
  if (document.body?.getAttribute('data-theme') || document.body?.className) return document.body
  if (document.documentElement?.getAttribute('data-theme') || document.documentElement?.className) return document.documentElement
  return null
}

function getThemeNodes() {
  return [...new Set([findThemeNode(), document.documentElement, document.body].filter(Boolean))]
}

function nodeHasDarkHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase();
  if (['dark', 'purple', 'transparent'].includes(themeValue)) return true
  const className = String(node?.className || '').toLowerCase();
  return ['v-theme--dark', 'theme--dark', 'theme-dark', 'dark'].some((token) => className.includes(token))
}

function nodeHasLightHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase();
  if (themeValue === 'light') return true
  const className = String(node?.className || '').toLowerCase();
  return ['v-theme--light', 'theme--light', 'theme-light', 'light'].some((token) => className.includes(token))
}

function detectTheme() {
  const themeNodes = getThemeNodes();
  if (themeNodes.some(nodeHasDarkHint)) {
    isDarkTheme.value = true;
    return
  }
  if (themeNodes.some(nodeHasLightHint)) {
    isDarkTheme.value = false;
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

function bindThemeObserver() {
  themeObserver?.disconnect?.();
  detectTheme();
  if (!window.MutationObserver) {
    return
  }
  themeObserver = new MutationObserver(detectTheme);
  getThemeNodes().forEach((node) => {
    themeObserver.observe(node, {
      attributes: true,
      subtree: node === document.documentElement || node === document.body,
      attributeFilter: ['data-theme', 'class'],
    });
  });
}

onMounted(async () => {
  detectTheme();
  bindThemeObserver();
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener?.('change', detectTheme);
  }
  applyConfig(props.initialConfig || {});
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
    class: _normalizeClass(["vuetoy-config", { 'is-dark-theme': isDarkTheme.value }])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("header", _hoisted_2, [
        _createElementVNode("div", _hoisted_3, [
          _hoisted_4,
          _hoisted_5,
          _createElementVNode("div", _hoisted_6, [
            _createElementVNode("span", _hoisted_7, _toDisplayString(config.auto_cookie ? '站点 Cookie：自动同步' : '站点 Cookie：手动填写'), 1)
          ])
        ]),
        _createElementVNode("div", _hoisted_8, [
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
      _createElementVNode("section", _hoisted_9, [
        _hoisted_10,
        _createElementVNode("div", _hoisted_11, [
          _createElementVNode("div", _hoisted_12, [
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              class: "vtc-switch",
              label: "启用插件",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_13, [
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.use_proxy) = $event)),
              class: "vtc-switch",
              label: "使用代理",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_14, [
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.notify) = $event)),
              class: "vtc-switch",
              label: "开启通知",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_15, [
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.onlyonce) = $event)),
              class: "vtc-switch",
              label: "立即运行一次",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ])
      ]),
      _createElementVNode("section", _hoisted_16, [
        _hoisted_17,
        _createElementVNode("div", _hoisted_18, [
          _createElementVNode("div", _hoisted_19, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_cookie,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.auto_cookie) = $event)),
              class: "vtc-switch",
              label: "使用站点 Cookie",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_20, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_collect,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.auto_collect) = $event)),
              class: "vtc-switch",
              label: "自动回收",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_21, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_place,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.auto_place) = $event)),
              class: "vtc-switch",
              label: "自动展出",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_22, [
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.force_ipv4) = $event)),
              class: "vtc-switch",
              label: "优先 IPv4",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("div", _hoisted_23, [
          _createElementVNode("div", _hoisted_24, [
            _hoisted_25,
            _createVNode(_component_v_text_field, {
              modelValue: cookieFieldValue.value,
              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((cookieFieldValue).value = $event)),
              label: "站点 Cookie",
              variant: "outlined",
              density: "comfortable",
              disabled: cookieReadonly.value,
              readonly: cookieReadonly.value,
              placeholder: cookieReadonly.value ? '开启后自动同步站点 Cookie' : '例如 c_secure_pass=...',
              "hide-details": "auto"
            }, null, 8, ["modelValue", "disabled", "readonly", "placeholder"]),
            _hoisted_26
          ])
        ])
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-664098f1"]]);

export { ConfigView as default };
