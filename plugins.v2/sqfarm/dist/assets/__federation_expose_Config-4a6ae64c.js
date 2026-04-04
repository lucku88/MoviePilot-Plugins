import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_82a88e4d_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-82a88e4d"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "sq-shell" };
const _hoisted_2 = { class: "sq-hero" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-hero-copy" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "sq-badge" }, "SQ农场"),
  /*#__PURE__*/_createElementVNode("h1", { class: "sq-title" }, "配置中心"),
  /*#__PURE__*/_createElementVNode("p", { class: "sq-subtitle" }, "使用站点 Cookie、动态调度和 OCR 自动收菜，售出与种植都可以单独开关。")
], -1));
const _hoisted_4 = { class: "sq-actions" };
const _hoisted_5 = { class: "sq-grid" };
const _hoisted_6 = { class: "sq-panel" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-kicker" }, "基础开关"),
    /*#__PURE__*/_createElementVNode("h2", null, "运行控制")
  ])
], -1));
const _hoisted_8 = { class: "sq-switch-grid" };
const _hoisted_9 = { class: "sq-panel" };
const _hoisted_10 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-kicker" }, "种植与调度"),
    /*#__PURE__*/_createElementVNode("h2", null, "策略配置")
  ])
], -1));
const _hoisted_11 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-note" }, "优先显示当前已解锁种子；如果站点状态还没拉到，会先显示默认种子列表。", -1));
const _hoisted_12 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-note" }, "插件不再固定轮询。启用或保存后会先获取一次农场信息，之后只在最近可收时间触发。", -1));
const _hoisted_13 = { class: "sq-panel" };
const _hoisted_14 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-kicker" }, "网络与 OCR"),
    /*#__PURE__*/_createElementVNode("h2", null, "连接设置")
  ])
], -1));
const _hoisted_15 = { class: "sq-panel" };
const _hoisted_16 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-kicker" }, "OCR 说明"),
    /*#__PURE__*/_createElementVNode("h2", null, "trwebocr 容器")
  ])
], -1));
const _hoisted_17 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("code", null, "trwebocr", -1));
const _hoisted_18 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-note" }, [
  /*#__PURE__*/_createTextVNode("推荐先部署 "),
  /*#__PURE__*/_createElementVNode("code", null, "trwebocr"),
  /*#__PURE__*/_createTextVNode("，再把 OCR 地址填成 "),
  /*#__PURE__*/_createElementVNode("code", null, "http://ip:8089/api/tr-run/"),
  /*#__PURE__*/_createTextVNode("。")
], -1));
const _hoisted_19 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-note" }, "容器安装参考如下：", -1));
const _hoisted_20 = { class: "sq-panel sq-panel-wide" };
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-kicker" }, "手动 Cookie"),
    /*#__PURE__*/_createElementVNode("h2", null, "兜底配置")
  ])
], -1));
const _hoisted_22 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-note" }, [
  /*#__PURE__*/_createTextVNode(" 开启站点 Cookie 后，插件会优先读取 MoviePilot 站点管理中的 "),
  /*#__PURE__*/_createElementVNode("code", null, "si-qi.xyz"),
  /*#__PURE__*/_createTextVNode(" Cookie。 这里仍可作为手动兜底。 ")
], -1));

const {onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');


const ocrComposeExample = `version: '3.8'
services:
  trwebocr:
    image: mmmz/trwebocr:latest
    container_name: trwebocr
    ports:
      - "8089:8089"
    restart: always
    volumes:
      - ./data:/app/data
    environment:
      - TZ=Asia/Shanghai
    network_mode: bridge`;


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
  schedule_buffer_seconds: 5,
  random_delay_max_seconds: 5,
  http_timeout: 12,
  http_retry_times: 3,
  http_retry_delay: 1500,
  ocr_retry_times: 2,
});

let themeObserver = null;
let mediaQuery = null;

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function detectTheme() {
  const docTheme = document.documentElement.getAttribute('data-theme');
  const bodyTheme = document.body?.getAttribute('data-theme');
  const themeValue = bodyTheme || docTheme || '';
  const darkThemes = new Set(['dark', 'purple', 'transparent']);
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  isDarkTheme.value = darkThemes.has(themeValue) || (!themeValue && !!prefersDark);
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
    // 保留当前种子选项
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

function closePlugin() {
  emit('close');
}

onMounted(() => {
  detectTheme();
  mediaQuery = window.matchMedia?.('(prefers-color-scheme: dark)');
  mediaQuery?.addEventListener?.('change', detectTheme);

  themeObserver = new MutationObserver(detectTheme);
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  if (document.body) {
    themeObserver.observe(document.body, { attributes: true, attributeFilter: ['data-theme'] });
  }

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
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_textarea = _resolveComponent("v-textarea");

  return (_openBlock(), _createElementBlock("div", {
    class: _normalizeClass(["sq-config", { 'is-dark-theme': isDarkTheme.value }])
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
        _createElementVNode("article", _hoisted_6, [
          _hoisted_7,
          _createElementVNode("div", _hoisted_8, [
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              label: "启用插件",
              color: "success",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.notify) = $event)),
              label: "发送通知",
              color: "primary",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.onlyonce) = $event)),
              label: "保存后立即执行一次",
              color: "warning",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.auto_cookie,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.auto_cookie) = $event)),
              label: "优先使用站点 Cookie",
              color: "info",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.enable_sell,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.enable_sell) = $event)),
              label: "自动售出",
              color: "secondary",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.enable_plant,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.enable_plant) = $event)),
              label: "自动种植",
              color: "secondary",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.use_proxy) = $event)),
              label: "使用系统代理",
              color: "info",
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
          _createVNode(_component_v_select, {
            modelValue: config.prefer_seed,
            "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.prefer_seed) = $event)),
            items: seedOptions.value,
            label: "优先种植",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3",
            "menu-props": { maxHeight: 280 }
          }, null, 8, ["modelValue", "items"]),
          _hoisted_11,
          _hoisted_12,
          _createVNode(_component_v_text_field, {
            modelValue: config.schedule_buffer_seconds,
            "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.schedule_buffer_seconds) = $event)),
            label: "智能调度缓冲秒数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mt-3"
          }, null, 8, ["modelValue"])
        ]),
        _createElementVNode("article", _hoisted_13, [
          _hoisted_14,
          _createVNode(_component_v_text_field, {
            modelValue: config.ocr_api_url,
            "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.ocr_api_url) = $event)),
            label: "OCR API 地址",
            placeholder: "http://ip:8089/api/tr-run/",
            hint: "默认推荐 http://ip:8089/api/tr-run/，请把 ip 替换成 Docker 宿主机 IP。",
            "persistent-hint": "",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.random_delay_max_seconds,
            "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.random_delay_max_seconds) = $event)),
            label: "随机延迟上限(秒)",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_timeout,
            "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.http_timeout) = $event)),
            label: "HTTP 超时(秒)",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_times,
            "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.http_retry_times) = $event)),
            label: "网络重试次数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_delay,
            "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((config.http_retry_delay) = $event)),
            label: "网络重试间隔(ms)",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            class: "mb-3"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.ocr_retry_times,
            "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((config.ocr_retry_times) = $event)),
            label: "OCR 重试次数",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"])
        ]),
        _createElementVNode("article", _hoisted_15, [
          _hoisted_16,
          _createVNode(_component_v_alert, {
            type: "info",
            variant: "tonal",
            class: "mb-3"
          }, {
            default: _withCtx(() => [
              _createTextVNode(" 自动收菜验证码依赖 "),
              _hoisted_17,
              _createTextVNode(" 容器。未部署 OCR 时，插件仍可刷新状态，但自动收菜会失败。 ")
            ]),
            _: 1
          }),
          _hoisted_18,
          _hoisted_19,
          _createElementVNode("pre", { class: "sq-code" }, _toDisplayString(ocrComposeExample))
        ]),
        _createElementVNode("article", _hoisted_20, [
          _hoisted_21,
          _createVNode(_component_v_textarea, {
            modelValue: config.cookie,
            "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((config.cookie) = $event)),
            label: "SQ Cookie",
            rows: "7",
            variant: "outlined",
            density: "comfortable",
            placeholder: "例如 c_secure_pass=..."
          }, null, 8, ["modelValue"]),
          _hoisted_22
        ])
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-82a88e4d"]]);

export { ConfigView as default };
