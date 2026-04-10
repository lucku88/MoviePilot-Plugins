import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_29e41fca_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-29e41fca"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "toy-shell" };
const _hoisted_2 = { class: "toy-config-header" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-header-copy" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "toy-badge" }, "SQ玩偶"),
  /*#__PURE__*/_createElementVNode("h1", { class: "toy-page-title" }, "插件配置"),
  /*#__PURE__*/_createElementVNode("p", { class: "toy-page-subtitle" }, "盲盒、回收、展出、获取执行记录。")
], -1));
const _hoisted_4 = { class: "toy-header-actions" };
const _hoisted_5 = { class: "toy-settings-card" };
const _hoisted_6 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "toy-settings-title" }, "⚙️ 基本设置", -1));
const _hoisted_7 = { class: "toy-switch-grid toy-switch-grid-basic" };
const _hoisted_8 = { class: "toy-switch-item" };
const _hoisted_9 = { class: "toy-switch-item" };
const _hoisted_10 = { class: "toy-switch-item" };
const _hoisted_11 = { class: "toy-switch-item" };
const _hoisted_12 = { class: "toy-settings-card" };
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "toy-settings-title" }, "🧩 功能设置", -1));
const _hoisted_14 = { class: "toy-switch-grid" };
const _hoisted_15 = { class: "toy-switch-item" };
const _hoisted_16 = { class: "toy-switch-item" };
const _hoisted_17 = { class: "toy-switch-item" };
const _hoisted_18 = { class: "toy-field-grid" };
const _hoisted_19 = { class: "toy-field-block" };
const _hoisted_20 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-field-label" }, "站点Cookie", -1));
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-note" }, "启用【使用站点Cookie】后自动同步，关闭后才可手动填写。", -1));
const _hoisted_22 = { class: "toy-field-block" };
const _hoisted_23 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-field-label" }, "动作参数", -1));
const _hoisted_24 = { class: "toy-inline-grid" };

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


const pluginBase = '/plugin/SQToy';

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
  enable_target: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  skip_before_seconds: 60,
  collect_retry: 3,
  collect_retry_delay: 1200,
  place_loop_limit: 10,
  place_retry_delay: 1500,
  max_target_try: 3,
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
  return text.length > 22 ? `${text.slice(0, 22)}...` : text
}

function applyConfig(data = {}) {
  const { capture_tips, ...rest } = data || {};
  Object.assign(config, { ...config, ...rest });
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
      themeObserver.observe(node, {
        attributes: true,
        subtree: node === document.documentElement || node === document.body,
        attributeFilter: ['data-theme', 'class'],
      });
    });
  }
}

onMounted(async () => {
  detectTheme();
  bindThemeObserver();
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener?.('change', detectTheme);
  }
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
    class: _normalizeClass(["toy-config", { 'is-dark-theme': isDarkTheme.value }])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("header", _hoisted_2, [
        _hoisted_3,
        _createElementVNode("div", _hoisted_4, [
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
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            variant: "text",
            onClick: _cache[1] || (_cache[1] = $event => (emit('close')))
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
            variant: "tonal"
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(message.text), 1)
            ]),
            _: 1
          }, 8, ["type"]))
        : _createCommentVNode("", true),
      _createElementVNode("section", _hoisted_5, [
        _hoisted_6,
        _createElementVNode("div", _hoisted_7, [
          _createElementVNode("div", _hoisted_8, [
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.enabled) = $event)),
              class: "toy-switch-control",
              label: "启用插件",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_9, [
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.use_proxy) = $event)),
              class: "toy-switch-control",
              label: "使用代理",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_10, [
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.notify) = $event)),
              class: "toy-switch-control",
              label: "开启通知",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_11, [
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.onlyonce) = $event)),
              class: "toy-switch-control",
              label: "立即运行一次",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ])
      ]),
      _createElementVNode("section", _hoisted_12, [
        _hoisted_13,
        _createElementVNode("div", _hoisted_14, [
          _createElementVNode("div", _hoisted_15, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_cookie,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.auto_cookie) = $event)),
              class: "toy-switch-control",
              label: "使用站点Cookie",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_16, [
            _createVNode(_component_v_switch, {
              modelValue: config.enable_target,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.enable_target) = $event)),
              class: "toy-switch-control",
              label: "允许外展抢位",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_17, [
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.force_ipv4) = $event)),
              class: "toy-switch-control",
              label: "优先 IPv4",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("div", _hoisted_18, [
          _createElementVNode("div", _hoisted_19, [
            _hoisted_20,
            _createVNode(_component_v_text_field, {
              modelValue: cookieFieldValue.value,
              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((cookieFieldValue).value = $event)),
              label: "站点Cookie",
              variant: "outlined",
              density: "comfortable",
              disabled: cookieReadonly.value,
              readonly: cookieReadonly.value,
              placeholder: cookieReadonly.value ? '使用站点Cookie后自动同步' : '例如 c_secure_pass=...'
            }, null, 8, ["modelValue", "disabled", "readonly", "placeholder"]),
            _hoisted_21
          ]),
          _createElementVNode("div", _hoisted_22, [
            _hoisted_23,
            _createElementVNode("div", _hoisted_24, [
              _createVNode(_component_v_text_field, {
                modelValue: config.collect_retry,
                "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.collect_retry) = $event)),
                label: "回收重试次数",
                type: "number",
                variant: "outlined",
                density: "comfortable"
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_text_field, {
                modelValue: config.collect_retry_delay,
                "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.collect_retry_delay) = $event)),
                label: "回收重试间隔(ms)",
                type: "number",
                variant: "outlined",
                density: "comfortable"
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_text_field, {
                modelValue: config.place_loop_limit,
                "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.place_loop_limit) = $event)),
                label: "单轮放置循环上限",
                type: "number",
                variant: "outlined",
                density: "comfortable"
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_text_field, {
                modelValue: config.place_retry_delay,
                "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.place_retry_delay) = $event)),
                label: "放置循环间隔(ms)",
                type: "number",
                variant: "outlined",
                density: "comfortable"
              }, null, 8, ["modelValue"]),
              _createVNode(_component_v_text_field, {
                modelValue: config.max_target_try,
                "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.max_target_try) = $event)),
                label: "随机目标尝试次数",
                type: "number",
                variant: "outlined",
                density: "comfortable"
              }, null, 8, ["modelValue"])
            ])
          ])
        ])
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-29e41fca"]]);

export { ConfigView as default };
