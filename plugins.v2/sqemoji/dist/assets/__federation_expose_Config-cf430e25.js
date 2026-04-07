import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_0b95e84e_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-0b95e84e"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "emoji-shell" };
const _hoisted_2 = { class: "emoji-hero" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "emoji-badge" }, "SQ表情"),
  /*#__PURE__*/_createElementVNode("h1", { class: "emoji-title" }, "配置中心"),
  /*#__PURE__*/_createElementVNode("p", { class: "emoji-subtitle" }, "管理老虎机、舞台自动执行、Cookie 同步和网络参数。")
], -1));
const _hoisted_4 = { class: "emoji-actions" };
const _hoisted_5 = { class: "emoji-panel" };
const _hoisted_6 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "emoji-panel-kicker" }, "基础开关"),
    /*#__PURE__*/_createElementVNode("h2", null, "运行控制")
  ])
], -1));
const _hoisted_7 = { class: "emoji-switch-grid" };
const _hoisted_8 = { class: "emoji-panel" };
const _hoisted_9 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "emoji-panel-kicker" }, "调度与网络"),
    /*#__PURE__*/_createElementVNode("h2", null, "执行参数")
  ])
], -1));
const _hoisted_10 = { class: "emoji-form-grid" };
const _hoisted_11 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-note" }, " 自动舞台会在当前演出结束后自动收回并重新开演。自动老虎机会在当天仍有免费次数时自动转完，次日零点后重新识别。 ", -1));
const _hoisted_12 = { class: "emoji-panel" };
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "emoji-panel-kicker" }, "手动 Cookie"),
    /*#__PURE__*/_createElementVNode("h2", null, "Cookie 兜底")
  ])
], -1));
const _hoisted_14 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "emoji-note" }, [
  /*#__PURE__*/_createTextVNode(" 默认读取 "),
  /*#__PURE__*/_createElementVNode("code", null, "si-qi.xyz"),
  /*#__PURE__*/_createTextVNode(" 站点配置中的 Cookie。开启“优先使用站点 Cookie”后，会优先使用 MoviePilot 站点管理中的值。 ")
], -1));
const _hoisted_15 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("section", { class: "emoji-panel" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "emoji-panel-head" }, [
    /*#__PURE__*/_createElementVNode("div", null, [
      /*#__PURE__*/_createElementVNode("div", { class: "emoji-panel-kicker" }, "功能说明"),
      /*#__PURE__*/_createElementVNode("h2", null, "当前能力")
    ])
  ]),
  /*#__PURE__*/_createElementVNode("div", { class: "emoji-note" }, " 当前版本已支持：状态页展示、每日老虎机手动/自动转动、表情包开包、重开、收下、表情包合成、舞台扩展、演员草拟排位、确认演出、收回演出，以及站点 Cookie 同步。 ")
], -1));

const {onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


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
const message = reactive({ text: '', type: 'success' });
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  auto_stage: true,
  auto_spin: false,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  skip_before_seconds: 60,
});

let themeObserver = null;
let mediaQuery = null;
let observedThemeNode = null;

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function applyConfig(data = {}) {
  Object.assign(config, { ...config, ...data });
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
    current = current.parentElement;
  }
  if (document.body?.getAttribute('data-theme')) return document.body
  if (document.documentElement?.getAttribute('data-theme')) return document.documentElement
  return null
}

function detectTheme() {
  const themeNode = findThemeNode();
  const themeValue = themeNode?.getAttribute?.('data-theme') || '';
  const darkThemes = new Set(['dark', 'purple', 'transparent']);
  if (darkThemes.has(themeValue)) {
    isDarkTheme.value = true;
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

function bindTheme() {
  detectTheme();
  observedThemeNode = findThemeNode();
  if (observedThemeNode && window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme);
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme'] });
  }
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener?.('change', detectTheme);
  }
}

onMounted(async () => {
  bindTheme();
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
  const _component_v_textarea = _resolveComponent("v-textarea");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["emoji-config", { 'is-dark-theme': isDarkTheme.value }])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("section", _hoisted_2, [
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
          _createVNode(_component_v_switch, {
            modelValue: config.enabled,
            "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.enabled) = $event)),
            label: "启用插件",
            color: "success",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.notify,
            "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.notify) = $event)),
            label: "发送通知",
            color: "primary",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.onlyonce,
            "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.onlyonce) = $event)),
            label: "保存后执行一次",
            color: "warning",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.auto_cookie,
            "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.auto_cookie) = $event)),
            label: "优先使用站点 Cookie",
            color: "info",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.auto_stage,
            "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.auto_stage) = $event)),
            label: "自动舞台演出",
            color: "deep-orange",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.auto_spin,
            "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.auto_spin) = $event)),
            label: "自动清空当日老虎机次数",
            color: "deep-purple",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.use_proxy,
            "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.use_proxy) = $event)),
            label: "使用系统代理",
            color: "secondary",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.force_ipv4,
            "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.force_ipv4) = $event)),
            label: "优先 IPv4",
            color: "secondary",
            "hide-details": ""
          }, null, 8, ["modelValue"])
        ])
      ]),
      _createElementVNode("section", _hoisted_8, [
        _hoisted_9,
        _createElementVNode("div", _hoisted_10, [
          _createVNode(_component_v_text_field, {
            modelValue: config.schedule_buffer_seconds,
            "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.schedule_buffer_seconds) = $event)),
            label: "调度缓冲秒数",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.skip_before_seconds,
            "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.skip_before_seconds) = $event)),
            label: "提前跳过阈值(秒)",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.random_delay_max_seconds,
            "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.random_delay_max_seconds) = $event)),
            label: "随机延迟上限(秒)",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_timeout,
            "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.http_timeout) = $event)),
            label: "HTTP 超时(秒)",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_times,
            "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.http_retry_times) = $event)),
            label: "GET 重试次数",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_delay,
            "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((config.http_retry_delay) = $event)),
            label: "GET 重试间隔(ms)",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"])
        ]),
        _hoisted_11
      ]),
      _createElementVNode("section", _hoisted_12, [
        _hoisted_13,
        _createVNode(_component_v_textarea, {
          modelValue: config.cookie,
          "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((config.cookie) = $event)),
          label: "SQ Cookie",
          rows: "6",
          variant: "outlined",
          density: "comfortable",
          placeholder: "例如 c_secure_pass=..."
        }, null, 8, ["modelValue"]),
        _hoisted_14
      ]),
      _hoisted_15
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-0b95e84e"]]);

export { ConfigView as default };
