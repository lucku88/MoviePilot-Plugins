import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_7dfb3d42_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-7dfb3d42"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "farm-shell" };
const _hoisted_2 = { class: "farm-hero" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "farm-copy" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "farm-badge" }, "SQ农场"),
  /*#__PURE__*/_createElementVNode("h1", { class: "farm-title" }, "插件配置"),
  /*#__PURE__*/_createElementVNode("p", { class: "farm-subtitle" }, "收菜、种植、出售、获取执行记录。")
], -1));
const _hoisted_4 = { class: "farm-actions" };
const _hoisted_5 = { class: "farm-card" };
const _hoisted_6 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "farm-section-title" }, "⚙️ 基本设置", -1));
const _hoisted_7 = { class: "farm-switch-grid farm-switch-grid-basic" };
const _hoisted_8 = { class: "farm-switch-item" };
const _hoisted_9 = { class: "farm-switch-item" };
const _hoisted_10 = { class: "farm-switch-item" };
const _hoisted_11 = { class: "farm-switch-item" };
const _hoisted_12 = { class: "farm-card" };
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "farm-section-title" }, "🧩 功能设置", -1));
const _hoisted_14 = { class: "farm-switch-grid" };
const _hoisted_15 = { class: "farm-switch-item" };
const _hoisted_16 = { class: "farm-switch-item" };
const _hoisted_17 = { class: "farm-switch-item" };
const _hoisted_18 = { class: "farm-field-grid" };
const _hoisted_19 = { class: "farm-field-card" };
const _hoisted_20 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "farm-field-title" }, "站点 Cookie", -1));
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "farm-field-note" }, " 启用【使用站点 Cookie】后会自动读取已配置站点的 Cookie，关闭后才可以手动修改。 ", -1));
const _hoisted_22 = { class: "farm-field-card" };
const _hoisted_23 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "farm-field-title" }, "优先种子", -1));
const _hoisted_24 = { class: "farm-field-card" };
const _hoisted_25 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "farm-field-title" }, "OCR API 地址", -1));
const _hoisted_26 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "farm-section-title" }, "📝 OCR 说明", -1));
const _hoisted_27 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "farm-note" }, " 批量收菜验证码依赖 OCR。未配置 OCR 时，插件仍可刷新状态，并在批量收菜失败后尝试逐坑位兜底收菜。 ", -1));
const _hoisted_28 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "farm-note" }, [
  /*#__PURE__*/_createTextVNode("推荐先部署 "),
  /*#__PURE__*/_createElementVNode("code", null, "trwebocr"),
  /*#__PURE__*/_createTextVNode("，再把 OCR 地址填成 "),
  /*#__PURE__*/_createElementVNode("code", null, "http://ip:8089/api/tr-run/"),
  /*#__PURE__*/_createTextVNode("。")
], -1));

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


const ocrComposeExample = `version: '3.8'
services:
  trwebocr:
    image: mmmz/trwebocr:latest
    container_name: trwebocr
    ports:
      - "8089:8089"
    restart: always
    environment:
      - TZ=Asia/Shanghai`;


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
const seedOptions = ref(['西红柿']);
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_sell: true,
  enable_plant: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  ocr_api_url: 'http://ip:8089/api/tr-run/',
  prefer_seed: '西红柿',
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
  return text.length > 36 ? `${text.slice(0, 36)}...` : text
}

function normalizeSeeds(items) {
  const normalized = (items || [])
    .map((item) => (typeof item === 'string' ? item : item?.value || item?.name || ''))
    .filter(Boolean);

  if (config.prefer_seed && !normalized.includes(config.prefer_seed)) {
    normalized.unshift(config.prefer_seed);
  }

  return normalized.length ? normalized : ['西红柿', '萝卜', '玉米', '茄子', '蘑菇', '樱桃']
}

function applySeedOptions(items) {
  seedOptions.value = normalizeSeeds(items);
}

function applyStatusSeedOptions(seedShop) {
  const unlocked = (seedShop || [])
    .filter((seed) => seed.unlocked && seed.name)
    .map((seed) => seed.name);
  if (unlocked.length) {
    applySeedOptions(unlocked);
  }
}

async function loadStatusSeedOptions() {
  try {
    const res = await props.api.get('/plugin/SQFarm/status');
    applyStatusSeedOptions(res?.farm_status?.seed_shop);
  } catch (error) {
    // 保留当前种子列表
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/SQFarm/config');
    Object.assign(config, res || {});
    applySeedOptions(res?.seed_options);
    await loadStatusSeedOptions();
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error');
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/config', { ...config });
    if (res.config) {
      Object.assign(config, res.config);
      applySeedOptions(res.config.seed_options);
    }
    flash(res.message || '配置已保存');
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
    const res = await props.api.get('/plugin/SQFarm/cookie');
    if (res.config) {
      Object.assign(config, res.config);
      applySeedOptions(res.config.seed_options);
    }
    await loadStatusSeedOptions();
    flash(res.message || 'Cookie 已同步');
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error');
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
  const hasDark = nodes.some((node) => nodeHasDarkHint(node));
  const hasLight = nodes.some((node) => nodeHasLightHint(node));
  if (hasDark) {
    isDarkTheme.value = true;
    return
  }
  if (hasLight) {
    isDarkTheme.value = false;
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

function bindThemeObserver() {
  themeObserver?.disconnect();
  themeObserver = new MutationObserver(() => {
    detectTheme();
  });

  for (const node of getThemeNodes()) {
    themeObserver.observe(node, {
      attributes: true,
      subtree: true,
      attributeFilter: ['data-theme', 'class'],
    });
  }
}

function closePlugin() {
  emit('close');
}

onMounted(() => {
  detectTheme();
  mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)');
  mediaQuery?.addEventListener?.('change', detectTheme);
  bindThemeObserver();
  loadConfig();
});

onBeforeUnmount(() => {
  themeObserver?.disconnect();
  mediaQuery?.removeEventListener?.('change', detectTheme);
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_select = _resolveComponent("v-select");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["farm-config", { 'is-dark-theme': isDarkTheme.value }])
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
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              class: "farm-switch",
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
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.use_proxy) = $event)),
              class: "farm-switch",
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
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.notify) = $event)),
              class: "farm-switch",
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
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.onlyonce) = $event)),
              class: "farm-switch",
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
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.auto_cookie) = $event)),
              class: "farm-switch",
              label: "使用站点 Cookie",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_16, [
            _createVNode(_component_v_switch, {
              modelValue: config.enable_sell,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.enable_sell) = $event)),
              class: "farm-switch",
              label: "自动出售",
              color: "#7c5cff",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_17, [
            _createVNode(_component_v_switch, {
              modelValue: config.enable_plant,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.enable_plant) = $event)),
              class: "farm-switch",
              label: "自动种植",
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
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((cookieFieldValue).value = $event)),
              label: "站点 Cookie",
              variant: "outlined",
              density: "comfortable",
              disabled: cookieReadonly.value,
              readonly: cookieReadonly.value,
              placeholder: cookieReadonly.value ? '启用站点 Cookie 后自动同步' : '例如 c_secure_pass=...',
              "hide-details": "auto"
            }, null, 8, ["modelValue", "disabled", "readonly", "placeholder"]),
            _hoisted_21
          ]),
          _createElementVNode("div", _hoisted_22, [
            _hoisted_23,
            _createVNode(_component_v_select, {
              modelValue: config.prefer_seed,
              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.prefer_seed) = $event)),
              items: seedOptions.value,
              label: "优先种子",
              variant: "outlined",
              density: "comfortable",
              "menu-props": { maxHeight: 280 },
              "hide-details": "auto"
            }, null, 8, ["modelValue", "items"])
          ]),
          _createElementVNode("div", _hoisted_24, [
            _hoisted_25,
            _createVNode(_component_v_text_field, {
              modelValue: config.ocr_api_url,
              "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.ocr_api_url) = $event)),
              label: "OCR API 地址",
              variant: "outlined",
              density: "comfortable",
              placeholder: "http://ip:8089/api/tr-run/",
              "hide-details": "auto"
            }, null, 8, ["modelValue"])
          ])
        ])
      ]),
      _createElementVNode("section", { class: "farm-card" }, [
        _hoisted_26,
        _hoisted_27,
        _hoisted_28,
        _createElementVNode("pre", { class: "farm-code" }, _toDisplayString(ocrComposeExample))
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-7dfb3d42"]]);

export { ConfigView as default };
