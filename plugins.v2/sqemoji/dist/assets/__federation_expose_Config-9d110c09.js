import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_8a539df0_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-8a539df0"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "emoji-shell" };
const _hoisted_2 = { class: "emoji-config-header" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-header-copy" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "emoji-badge" }, "SQ表情"),
  /*#__PURE__*/_createElementVNode("h1", { class: "emoji-page-title" }, "SQ表情 · 插件配置"),
  /*#__PURE__*/_createElementVNode("p", { class: "emoji-page-subtitle" }, "老虎机、开包、舞台演出、获取执行记录。")
], -1));
const _hoisted_4 = { class: "emoji-header-actions" };
const _hoisted_5 = { class: "emoji-settings-card" };
const _hoisted_6 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "emoji-settings-title" }, "⚙️ 基本设置", -1));
const _hoisted_7 = { class: "emoji-switch-grid" };
const _hoisted_8 = { class: "emoji-switch-item" };
const _hoisted_9 = { class: "emoji-switch-item" };
const _hoisted_10 = { class: "emoji-switch-item" };
const _hoisted_11 = { class: "emoji-switch-item" };
const _hoisted_12 = { class: "emoji-settings-card" };
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "emoji-settings-title" }, "🧩 功能设置", -1));
const _hoisted_14 = { class: "emoji-switch-grid" };
const _hoisted_15 = { class: "emoji-switch-item" };
const _hoisted_16 = { class: "emoji-switch-item" };
const _hoisted_17 = { class: "emoji-switch-item" };
const _hoisted_18 = { class: "emoji-switch-item" };
const _hoisted_19 = { class: "emoji-switch-item" };
const _hoisted_20 = { class: "emoji-field-grid" };
const _hoisted_21 = { class: "emoji-field-block emoji-field-block-wide" };
const _hoisted_22 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-field-label" }, "站点Cookie", -1));
const _hoisted_23 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-note" }, " 启用【使用站点Cookie】功能后，插件会自动获取已配置站点的cookie，关闭使用站点Cookie功能才可以手动改cookie。 ", -1));
const _hoisted_24 = { class: "emoji-settings-card" };
const _hoisted_25 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "emoji-settings-title" }, "⏰ 时间配置", -1));
const _hoisted_26 = { class: "emoji-settings-card" };
const _hoisted_27 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "emoji-settings-title" }, "🎭 演出设置", -1));
const _hoisted_28 = { class: "emoji-field-grid" };
const _hoisted_29 = { class: "emoji-field-block" };
const _hoisted_30 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-field-label" }, "演出舞台效果", -1));

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


const pluginBase = '/plugin/SQEmoji';

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
const effectOptions = ref([{ title: '自动选择演出舞台效果', value: 'auto' }]);
const message = reactive({ text: '', type: 'success' });
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  auto_stage: true,
  auto_spin: false,
  auto_open_bags: false,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  spin_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  skip_before_seconds: 60,
  auto_stage_effect_key: 'auto',
});

const cookieReadonly = computed(() => !!config.auto_cookie);

let themeObserver = null;
let mediaQuery = null;

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function applyConfig(data = {}) {
  if (Array.isArray(data.effect_options) && data.effect_options.length) {
    effectOptions.value = data.effect_options;
  } else {
    effectOptions.value = [{ title: '自动选择演出舞台效果', value: 'auto' }];
  }
  const { effect_options, capture_tips, ...rest } = data || {};
  Object.assign(config, { ...config, ...rest });
  if (!effectOptions.value.some((item) => item.value === config.auto_stage_effect_key)) {
    config.auto_stage_effect_key = 'auto';
  }
}

function buildPayload() {
  return { ...config }
}

async function loadConfig() {
  const data = await props.api.get(`${pluginBase}/config`);
  applyConfig(data || {});
}

async function saveConfig() {
  saving.value = true;
  try {
    const result = await props.api.post(`${pluginBase}/config`, buildPayload());
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
  const _component_v_textarea = _resolveComponent("v-textarea");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_v_select = _resolveComponent("v-select");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["emoji-config", { 'is-dark-theme': isDarkTheme.value }])
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
              label: "启用插件",
              color: "#7c5cff",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_9, [
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.use_proxy) = $event)),
              label: "使用代理",
              color: "#7c5cff",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_10, [
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.notify) = $event)),
              label: "开启通知",
              color: "#7c5cff",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_11, [
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.onlyonce) = $event)),
              label: "立即运行一次",
              color: "#7c5cff",
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
              label: "使用站点Cookie",
              color: "#7c5cff",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_16, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_stage,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.auto_stage) = $event)),
              label: "自动舞台演出",
              color: "#7c5cff",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_17, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_spin,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.auto_spin) = $event)),
              label: "自动老虎机",
              color: "#7c5cff",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_18, [
            _createVNode(_component_v_switch, {
              modelValue: config.auto_open_bags,
              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.auto_open_bags) = $event)),
              label: "自动开包并收下",
              color: "#7c5cff",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_19, [
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.force_ipv4) = $event)),
              label: "优先 IPv4",
              color: "#7c5cff",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("div", _hoisted_20, [
          _createElementVNode("div", _hoisted_21, [
            _hoisted_22,
            _createVNode(_component_v_textarea, {
              modelValue: config.cookie,
              "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.cookie) = $event)),
              label: "站点Cookie",
              rows: "4",
              "auto-grow": "",
              variant: "outlined",
              density: "comfortable",
              placeholder: "例如 c_secure_pass=...",
              disabled: cookieReadonly.value,
              readonly: cookieReadonly.value
            }, null, 8, ["modelValue", "disabled", "readonly"]),
            _hoisted_23
          ])
        ])
      ]),
      _createElementVNode("section", _hoisted_24, [
        _hoisted_25,
        _createVNode(_component_VCronField, {
          modelValue: config.spin_cron,
          "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.spin_cron) = $event)),
          label: "老虎机/开包执行周期(cron)",
          density: "comfortable",
          class: "emoji-cron-field"
        }, null, 8, ["modelValue"])
      ]),
      _createElementVNode("section", _hoisted_26, [
        _hoisted_27,
        _createElementVNode("div", _hoisted_28, [
          _createElementVNode("div", _hoisted_29, [
            _hoisted_30,
            _createVNode(_component_v_select, {
              modelValue: config.auto_stage_effect_key,
              "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.auto_stage_effect_key) = $event)),
              items: effectOptions.value,
              "item-title": "title",
              "item-value": "value",
              label: "演出舞台效果",
              variant: "outlined",
              density: "comfortable",
              disabled: !config.auto_stage
            }, null, 8, ["modelValue", "items", "disabled"])
          ])
        ])
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-8a539df0"]]);

export { ConfigView as default };
