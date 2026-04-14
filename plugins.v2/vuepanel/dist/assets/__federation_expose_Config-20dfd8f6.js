import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_3dd2c72e_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,normalizeStyle:_normalizeStyle,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-3dd2c72e"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vuepanel-config" };
const _hoisted_2 = { class: "vpc-shell" };
const _hoisted_3 = { class: "vpc-hero" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "Global Settings", -1));
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h1", { class: "vpc-title" }, "Vue-面板设置", -1));
const _hoisted_6 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("p", { class: "vpc-subtitle" }, "这里负责插件级开关与运行参数。单卡片的配置、日志和复制，请回到功能面板操作。", -1));
const _hoisted_7 = { class: "vpc-chip-row" };
const _hoisted_8 = { class: "vpc-chip" };
const _hoisted_9 = { class: "vpc-chip" };
const _hoisted_10 = { class: "vpc-chip" };
const _hoisted_11 = { class: "vpc-chip" };
const _hoisted_12 = { class: "vpc-hero-actions" };
const _hoisted_13 = { class: "vpc-panel" };
const _hoisted_14 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-section-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "Plugin"),
    /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "插件级开关")
  ])
], -1));
const _hoisted_15 = { class: "vpc-switch-grid" };
const _hoisted_16 = { class: "vpc-switch-card" };
const _hoisted_17 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "启用插件", -1));
const _hoisted_18 = { class: "vpc-switch-card" };
const _hoisted_19 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "发送通知", -1));
const _hoisted_20 = { class: "vpc-switch-card" };
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "保存后执行一次", -1));
const _hoisted_22 = { class: "vpc-switch-card" };
const _hoisted_23 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "使用代理", -1));
const _hoisted_24 = { class: "vpc-switch-card" };
const _hoisted_25 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "优先 IPv4", -1));
const _hoisted_26 = { class: "vpc-form-grid" };
const _hoisted_27 = { class: "vpc-panel" };
const _hoisted_28 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-section-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "Cards"),
    /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "功能卡片清单")
  ]),
  /*#__PURE__*/_createElementVNode("span", { class: "vpc-note" }, "复制与编辑入口已移动到主面板卡片内。")
], -1));
const _hoisted_29 = { class: "vpc-card-list" };
const _hoisted_30 = { class: "vpc-card-top" };
const _hoisted_31 = { class: "vpc-card-title" };
const _hoisted_32 = { class: "vpc-card-desc" };
const _hoisted_33 = { class: "vpc-card-meta" };

const {computed,onMounted,reactive,ref} = await importShared('vue');


const DEFAULT_CRON = '5 8 * * *';


const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;





const saving = ref(false);
const message = reactive({ text: '', type: 'success' });
const config = reactive(createConfigState());
const moduleOptions = ref([]);

const enabledCards = computed(() => config.cards.filter((item) => item.enabled).length);
const autoCards = computed(() => config.cards.filter((item) => item.enabled && item.auto_run).length);

function createConfigState() {
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
  return moduleOptions.value.find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    summary: String(moduleKey || '').replaceAll('_', ' '),
    tone: 'azure',
  }
}

function moduleSummary(moduleKey) {
  return String(moduleMeta(moduleKey).summary || moduleKey).toLowerCase()
}

function normalizeCard(source = {}) {
  const meta = moduleMeta(source.module_key || 'siqi_sign');
  return {
    id: String(source.id || ''),
    title: String(source.title || meta.label || ''),
    module_key: meta.key,
    site_name: String(source.site_name || meta.default_site_name || ''),
    site_url: String(source.site_url || meta.default_site_url || ''),
    enabled: !!source.enabled,
    auto_run: source.auto_run !== false,
    notify: source.notify !== false,
    cron: String(source.cron || DEFAULT_CRON),
    tone: String(source.tone || meta.tone || 'azure'),
    cookie: String(source.cookie || ''),
    uid: String(source.uid || ''),
    note: String(source.note || ''),
  }
}

function normalizeConfig(source = {}) {
  Object.assign(config, createConfigState(), {
    enabled: !!source.enabled,
    notify: source.notify !== false,
    onlyonce: !!source.onlyonce,
    use_proxy: !!source.use_proxy,
    force_ipv4: source.force_ipv4 !== false,
    cron: String(source.cron || DEFAULT_CRON),
    http_timeout: Number(source.http_timeout || 15),
    http_retry_times: Number(source.http_retry_times || 3),
    random_delay_max_seconds: Number(source.random_delay_max_seconds || 5),
    cards: [],
  });
  config.cards.push(...(Array.isArray(source.cards) ? source.cards.map((item) => normalizeCard(item)) : []));
}

function serializeConfig() {
  return {
    enabled: !!config.enabled,
    notify: !!config.notify,
    onlyonce: !!config.onlyonce,
    use_proxy: !!config.use_proxy,
    force_ipv4: config.force_ipv4 !== false,
    cron: String(config.cron || DEFAULT_CRON),
    http_timeout: Number(config.http_timeout || 15),
    http_retry_times: Number(config.http_retry_times || 3),
    random_delay_max_seconds: Number(config.random_delay_max_seconds || 5),
    cards: config.cards.map((item) => normalizeCard(item)),
  }
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpc-tone-rgb': '38, 183, 120' },
    azure: { '--vpc-tone-rgb': '67, 126, 255' },
    amber: { '--vpc-tone-rgb': '255, 171, 67' },
    rose: { '--vpc-tone-rgb': '231, 92, 128' },
    violet: { '--vpc-tone-rgb': '150, 117, 255' },
    slate: { '--vpc-tone-rgb': '128, 140, 158' },
  };
  return map[tone] || map.azure
}

async function loadConfig() {
  try {
    const payload = await props.api.get('/plugin/VuePanel/config');
    moduleOptions.value = Array.isArray(payload.module_options) ? deepClone(payload.module_options) : [];
    normalizeConfig(payload || {});
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error');
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const response = await props.api.post('/plugin/VuePanel/config', serializeConfig());
    flash(response.message || '设置已保存');
    await loadConfig();
  } catch (error) {
    flash(error?.message || '保存配置失败', 'error');
  } finally {
    saving.value = false;
  }
}

function closePlugin() {
  emit('close');
}

onMounted(async () => {
  moduleOptions.value = Array.isArray(props.initialConfig?.module_options)
    ? deepClone(props.initialConfig.module_options)
    : [];
  normalizeConfig(props.initialConfig || {});
  await loadConfig();
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_text_field = _resolveComponent("v-text-field");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("header", _hoisted_3, [
        _createElementVNode("div", null, [
          _hoisted_4,
          _hoisted_5,
          _hoisted_6,
          _createElementVNode("div", _hoisted_7, [
            _createElementVNode("span", _hoisted_8, "主题 " + _toDisplayString(__props.themeLabel), 1),
            _createElementVNode("span", _hoisted_9, "卡片 " + _toDisplayString(config.cards.length), 1),
            _createElementVNode("span", _hoisted_10, "启用 " + _toDisplayString(enabledCards.value), 1),
            _createElementVNode("span", _hoisted_11, "自动运行 " + _toDisplayString(autoCards.value), 1)
          ])
        ]),
        _createElementVNode("div", _hoisted_12, [
          _createVNode(_component_v_btn, {
            color: "primary",
            variant: "flat",
            loading: saving.value,
            onClick: saveConfig
          }, {
            default: _withCtx(() => [
              _createTextVNode("保存设置")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            variant: "text",
            onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'page')))
          }, {
            default: _withCtx(() => [
              _createTextVNode("返回面板")
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
      _createElementVNode("section", _hoisted_13, [
        _hoisted_14,
        _createElementVNode("div", _hoisted_15, [
          _createElementVNode("label", _hoisted_16, [
            _hoisted_17,
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              "hide-details": "",
              density: "compact",
              color: "primary"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("label", _hoisted_18, [
            _hoisted_19,
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.notify) = $event)),
              "hide-details": "",
              density: "compact",
              color: "primary"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("label", _hoisted_20, [
            _hoisted_21,
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.onlyonce) = $event)),
              "hide-details": "",
              density: "compact",
              color: "primary"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("label", _hoisted_22, [
            _hoisted_23,
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.use_proxy) = $event)),
              "hide-details": "",
              density: "compact",
              color: "primary"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("label", _hoisted_24, [
            _hoisted_25,
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.force_ipv4) = $event)),
              "hide-details": "",
              density: "compact",
              color: "primary"
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("div", _hoisted_26, [
          _createVNode(_component_v_text_field, {
            modelValue: config.http_timeout,
            "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.http_timeout) = $event)),
            label: "HTTP 超时（秒）",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_times,
            "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.http_retry_times) = $event)),
            label: "HTTP 重试次数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.random_delay_max_seconds,
            "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.random_delay_max_seconds) = $event)),
            label: "随机延迟上限（秒）",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"])
        ])
      ]),
      _createElementVNode("section", _hoisted_27, [
        _hoisted_28,
        _createElementVNode("div", _hoisted_29, [
          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(config.cards, (card) => {
            return (_openBlock(), _createElementBlock("article", {
              key: card.id,
              class: "vpc-card",
              style: _normalizeStyle(toneStyle(card.tone))
            }, [
              _createElementVNode("div", _hoisted_30, [
                _createElementVNode("div", null, [
                  _createElementVNode("strong", _hoisted_31, _toDisplayString(card.title), 1),
                  _createElementVNode("p", _hoisted_32, _toDisplayString(moduleSummary(card.module_key)), 1)
                ]),
                _createElementVNode("span", {
                  class: _normalizeClass(["vpc-status", `is-${card.enabled ? 'enabled' : 'disabled'}`])
                }, _toDisplayString(card.enabled ? '启用' : '停用'), 3)
              ]),
              _createElementVNode("div", _hoisted_33, [
                _createElementVNode("span", null, _toDisplayString(card.site_name || '--'), 1),
                _createElementVNode("span", null, _toDisplayString(card.site_url || '--'), 1)
              ])
            ], 4))
          }), 128))
        ])
      ])
    ])
  ]))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-3dd2c72e"]]);

export { ConfigView as default };
