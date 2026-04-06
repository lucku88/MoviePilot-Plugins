import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_c62c646d_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-c62c646d"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "pill-shell" };
const _hoisted_2 = { class: "pill-hero" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "pill-badge" }, "SQ魔丸"),
  /*#__PURE__*/_createElementVNode("h1", { class: "pill-title" }, "配置中心"),
  /*#__PURE__*/_createElementVNode("p", { class: "pill-subtitle" }, "当前已接入自动搬砖、自动清沙滩、动态调度和站点 Cookie 同步。")
], -1));
const _hoisted_4 = { class: "pill-actions" };
const _hoisted_5 = { class: "pill-grid" };
const _hoisted_6 = { class: "pill-panel" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-kicker" }, "基础开关"),
    /*#__PURE__*/_createElementVNode("h2", null, "运行控制")
  ])
], -1));
const _hoisted_8 = { class: "pill-switch-grid" };
const _hoisted_9 = { class: "pill-panel pill-panel-wide" };
const _hoisted_10 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-kicker" }, "调度策略"),
    /*#__PURE__*/_createElementVNode("h2", null, "时间配置")
  ])
], -1));
const _hoisted_11 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pill-note" }, " 搬砖按你填写的 CRON 执行，默认是每天 00:05。沙滩仍按冷却时间动态调度；如果搬砖后检测到还没达到 50 次，会在 60 秒后自动重试。 ", -1));
const _hoisted_12 = { class: "pill-panel" };
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-kicker" }, "搬砖节奏"),
    /*#__PURE__*/_createElementVNode("h2", null, "动作配置")
  ])
], -1));
const _hoisted_14 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pill-note" }, " 每天搬砖次数固定按 50 次处理，不再需要手动配置循环次数。 ", -1));
const _hoisted_15 = { class: "pill-panel" };
const _hoisted_16 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-kicker" }, "网络设置"),
    /*#__PURE__*/_createElementVNode("h2", null, "连接参数")
  ])
], -1));
const _hoisted_17 = { class: "pill-panel pill-panel-wide" };
const _hoisted_18 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-kicker" }, "手动 Cookie"),
    /*#__PURE__*/_createElementVNode("h2", null, "兜底配置")
  ])
], -1));
const _hoisted_19 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pill-note" }, [
  /*#__PURE__*/_createTextVNode(" 默认站点固定为 "),
  /*#__PURE__*/_createElementVNode("code", null, "si-qi.xyz"),
  /*#__PURE__*/_createTextVNode("。开启站点 Cookie 同步后，插件会优先读取 MoviePilot 站点管理里的 Cookie。 ")
], -1));
const _hoisted_20 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("article", { class: "pill-panel pill-panel-wide" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-head" }, [
    /*#__PURE__*/_createElementVNode("div", null, [
      /*#__PURE__*/_createElementVNode("div", { class: "pill-panel-kicker" }, "当前说明"),
      /*#__PURE__*/_createElementVNode("h2", null, "功能状态")
    ])
  ]),
  /*#__PURE__*/_createElementVNode("div", { class: "pill-note" }, " 当前版本已经支持自动搬砖、自动清沙滩、手动兑换魔力和一键炼造魔丸。赠送按钮暂时不接入，物品栏仅展示当前数量。 ")
], -1));

const {onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


const pluginBase = '/plugin/SQPill';

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
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  isDarkTheme.value = darkThemes.has(themeValue) || (!themeValue && !!prefersDark);
}

function bindThemeObserver() {
  themeObserver?.disconnect();
  themeObserver = new MutationObserver(() => {
    const nextNode = findThemeNode();
    if (nextNode && nextNode !== observedThemeNode) {
      bindThemeObserver();
      return
    }
    detectTheme();
  });
  observedThemeNode = findThemeNode();
  if (observedThemeNode) {
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme', 'class'] });
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
  themeObserver?.disconnect();
  mediaQuery?.removeEventListener?.('change', detectTheme);
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_textarea = _resolveComponent("v-textarea");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["pill-config", { 'is-dark-theme': isDarkTheme.value }])
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
              modelValue: config.enable_brick,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.enable_brick) = $event)),
              label: "自动搬砖",
              color: "deep-orange",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.enable_beach,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.enable_beach) = $event)),
              label: "自动清沙滩",
              color: "teal",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.use_proxy) = $event)),
              label: "使用系统代理",
              color: "info",
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
        _createElementVNode("article", _hoisted_9, [
          _hoisted_10,
          _createVNode(_component_v_row, null, {
            default: _withCtx(() => [
              _createVNode(_component_v_col, {
                cols: "12",
                md: "7"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCronField, {
                    modelValue: config.brick_cron,
                    "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.brick_cron) = $event)),
                    label: "执行周期(cron)",
                    hint: "例如：5 0 * * *",
                    "persistent-hint": "",
                    density: "compact"
                  }, null, 8, ["modelValue"])
                ]),
                _: 1
              }),
              _createVNode(_component_v_col, {
                cols: "12",
                md: "3"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_text_field, {
                    modelValue: config.schedule_buffer_seconds,
                    "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.schedule_buffer_seconds) = $event)),
                    label: "调度缓冲秒数",
                    type: "number",
                    variant: "outlined",
                    density: "compact"
                  }, null, 8, ["modelValue"])
                ]),
                _: 1
              }),
              _createVNode(_component_v_col, {
                cols: "12",
                md: "2"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_text_field, {
                    modelValue: config.ready_retry_seconds,
                    "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.ready_retry_seconds) = $event)),
                    label: "快速重试秒数",
                    type: "number",
                    variant: "outlined",
                    density: "compact"
                  }, null, 8, ["modelValue"])
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _hoisted_11
        ]),
        _createElementVNode("article", _hoisted_12, [
          _hoisted_13,
          _createVNode(_component_v_text_field, {
            modelValue: config.move_delay_min_ms,
            "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.move_delay_min_ms) = $event)),
            label: "搬砖间隔最小毫秒",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.move_delay_max_ms,
            "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.move_delay_max_ms) = $event)),
            label: "搬砖间隔最大毫秒",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _hoisted_14
        ]),
        _createElementVNode("article", _hoisted_15, [
          _hoisted_16,
          _createVNode(_component_v_text_field, {
            modelValue: config.random_delay_max_seconds,
            "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((config.random_delay_max_seconds) = $event)),
            label: "随机延迟上限(秒)",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_timeout,
            "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((config.http_timeout) = $event)),
            label: "HTTP 超时(秒)",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_times,
            "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((config.http_retry_times) = $event)),
            label: "GET 重试次数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_delay,
            "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((config.http_retry_delay) = $event)),
            label: "GET 重试间隔(ms)",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"])
        ]),
        _createElementVNode("article", _hoisted_17, [
          _hoisted_18,
          _createVNode(_component_v_textarea, {
            modelValue: config.cookie,
            "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((config.cookie) = $event)),
            label: "SQ Cookie",
            rows: "6",
            variant: "outlined",
            density: "comfortable",
            placeholder: "例如 c_secure_pass=..."
          }, null, 8, ["modelValue"]),
          _hoisted_19
        ]),
        _hoisted_20
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-c62c646d"]]);

export { ConfigView as default };
