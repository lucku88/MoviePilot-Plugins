import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_28fe8944_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-28fe8944"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "toy-shell" };
const _hoisted_2 = { class: "toy-hero" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "toy-badge" }, "SQ玩偶"),
  /*#__PURE__*/_createElementVNode("h1", { class: "toy-title" }, "配置中心"),
  /*#__PURE__*/_createElementVNode("p", { class: "toy-subtitle" }, "自动回收、自展位放置、外展抢位和站点 Cookie 同步都可以在这里调整。")
], -1));
const _hoisted_4 = { class: "toy-actions" };
const _hoisted_5 = { class: "toy-grid" };
const _hoisted_6 = { class: "toy-panel" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-kicker" }, "基础开关"),
    /*#__PURE__*/_createElementVNode("h2", null, "运行控制")
  ])
], -1));
const _hoisted_8 = { class: "toy-switch-grid" };
const _hoisted_9 = { class: "toy-panel" };
const _hoisted_10 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-kicker" }, "调度策略"),
    /*#__PURE__*/_createElementVNode("h2", null, "动态调度")
  ])
], -1));
const _hoisted_11 = { class: "toy-form-grid" };
const _hoisted_12 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-note" }, "插件不走固定 CRON，而是根据最近可回收时间动态注册下一次运行。未识别到时间时，会在启用或刷新后先拉一次页面状态。", -1));
const _hoisted_13 = { class: "toy-panel" };
const _hoisted_14 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-kicker" }, "回收与展出"),
    /*#__PURE__*/_createElementVNode("h2", null, "动作参数")
  ])
], -1));
const _hoisted_15 = { class: "toy-form-grid" };
const _hoisted_16 = { class: "toy-panel" };
const _hoisted_17 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-kicker" }, "网络参数"),
    /*#__PURE__*/_createElementVNode("h2", null, "连接设置")
  ])
], -1));
const _hoisted_18 = { class: "toy-form-grid" };
const _hoisted_19 = { class: "toy-panel" };
const _hoisted_20 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-kicker" }, "手动 Cookie"),
    /*#__PURE__*/_createElementVNode("h2", null, "Cookie 兜底")
  ])
], -1));
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "toy-note" }, [
  /*#__PURE__*/_createTextVNode("默认站点固定为 "),
  /*#__PURE__*/_createElementVNode("code", null, "si-qi.xyz"),
  /*#__PURE__*/_createTextVNode("。如果开启“优先使用站点 Cookie”，插件会优先读取 MoviePilot 站点管理中的 Cookie。")
], -1));
const _hoisted_22 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("article", { class: "toy-panel" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-head" }, [
    /*#__PURE__*/_createElementVNode("div", null, [
      /*#__PURE__*/_createElementVNode("div", { class: "toy-panel-kicker" }, "当前说明"),
      /*#__PURE__*/_createElementVNode("h2", null, "功能状态")
    ])
  ]),
  /*#__PURE__*/_createElementVNode("div", { class: "toy-note" }, [
    /*#__PURE__*/_createTextVNode(" 当前版本已支持：状态展示、自动回收、自展位放置、随机外展、按用户名或 ID 查看目标展台、盲盒购买与开启、手动收回和手动上架。"),
    /*#__PURE__*/_createElementVNode("br"),
    /*#__PURE__*/_createTextVNode(" 站点固定为 "),
    /*#__PURE__*/_createElementVNode("code", null, "si-qi.xyz"),
    /*#__PURE__*/_createTextVNode("，开启“优先使用站点 Cookie”后会优先读取 MoviePilot 站点管理中的 Cookie。 ")
  ])
], -1));

const {onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


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
  self_wait_window_seconds: 60,
  remote_wait_window_seconds: 60,
  max_target_try: 3,
  max_target_place: 3,
});

let themeObserver = null;
let mediaQuery = null;
let observedThemeNode = null;

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
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
  if (['dark', 'purple', 'transparent'].includes(themeValue)) {
    return true
  }
  const className = String(node?.className || '').toLowerCase();
  return ['v-theme--dark', 'theme--dark', 'theme-dark', 'dark'].some((token) => className.includes(token))
}

function nodeHasLightHint(node) {
  const themeValue = String(node?.getAttribute?.('data-theme') || '').toLowerCase();
  if (['light'].includes(themeValue)) {
    return true
  }
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
  observedThemeNode = findThemeNode();
  if (!window.MutationObserver) {
    return
  }
  themeObserver = new MutationObserver(() => {
    const nextNode = findThemeNode();
    if (nextNode !== observedThemeNode) {
      bindThemeObserver();
      return
    }
    detectTheme();
  });
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
    class: _normalizeClass(["toy-config", { 'is-dark-theme': isDarkTheme.value }])
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
            variant: "tonal",
            class: "mb-4"
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(message.text), 1)
            ]),
            _: 1
          }, 8, ["type"]))
        : _createCommentVNode("", true),
      _createElementVNode("section", _hoisted_5, [
        _createElementVNode("article", _hoisted_6, [
          _hoisted_7,
          _createElementVNode("div", _hoisted_8, [
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
              modelValue: config.enable_target,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.enable_target) = $event)),
              label: "允许外展抢位",
              color: "deep-orange",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.use_proxy) = $event)),
              label: "使用系统代理",
              color: "secondary",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.force_ipv4) = $event)),
              label: "优先 IPv4",
              color: "secondary",
              "hide-details": ""
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("article", _hoisted_9, [
          _hoisted_10,
          _createElementVNode("div", _hoisted_11, [
            _createVNode(_component_v_text_field, {
              modelValue: config.schedule_buffer_seconds,
              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.schedule_buffer_seconds) = $event)),
              label: "调度缓冲秒数",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.skip_before_seconds,
              "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.skip_before_seconds) = $event)),
              label: "提前跳过阈值(秒)",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.self_wait_window_seconds,
              "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.self_wait_window_seconds) = $event)),
              label: "自展位等待窗口(秒)",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.remote_wait_window_seconds,
              "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.remote_wait_window_seconds) = $event)),
              label: "外展等待窗口(秒)",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"])
          ]),
          _hoisted_12
        ]),
        _createElementVNode("article", _hoisted_13, [
          _hoisted_14,
          _createElementVNode("div", _hoisted_15, [
            _createVNode(_component_v_text_field, {
              modelValue: config.collect_retry,
              "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.collect_retry) = $event)),
              label: "回收重试次数",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.collect_retry_delay,
              "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.collect_retry_delay) = $event)),
              label: "回收重试间隔(ms)",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.place_loop_limit,
              "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((config.place_loop_limit) = $event)),
              label: "单轮放置循环上限",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.place_retry_delay,
              "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((config.place_retry_delay) = $event)),
              label: "放置循环间隔(ms)",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.max_target_try,
              "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((config.max_target_try) = $event)),
              label: "随机目标尝试次数",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.max_target_place,
              "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((config.max_target_place) = $event)),
              label: "单目标最多放置数",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("article", _hoisted_16, [
          _hoisted_17,
          _createElementVNode("div", _hoisted_18, [
            _createVNode(_component_v_text_field, {
              modelValue: config.random_delay_max_seconds,
              "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((config.random_delay_max_seconds) = $event)),
              label: "随机延迟上限(秒)",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.http_timeout,
              "onUpdate:modelValue": _cache[20] || (_cache[20] = $event => ((config.http_timeout) = $event)),
              label: "HTTP 超时(秒)",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.http_retry_times,
              "onUpdate:modelValue": _cache[21] || (_cache[21] = $event => ((config.http_retry_times) = $event)),
              label: "GET 重试次数",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.http_retry_delay,
              "onUpdate:modelValue": _cache[22] || (_cache[22] = $event => ((config.http_retry_delay) = $event)),
              label: "GET 重试间隔(ms)",
              type: "number",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("article", _hoisted_19, [
          _hoisted_20,
          _createVNode(_component_v_textarea, {
            modelValue: config.cookie,
            "onUpdate:modelValue": _cache[23] || (_cache[23] = $event => ((config.cookie) = $event)),
            label: "SQ Cookie",
            rows: "6",
            variant: "outlined",
            density: "comfortable",
            placeholder: "例如 c_secure_pass=..."
          }, null, 8, ["modelValue"]),
          _hoisted_21
        ]),
        _hoisted_22
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-28fe8944"]]);

export { ConfigView as default };
