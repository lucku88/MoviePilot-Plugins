import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_162a4a8c_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,createBlock:_createBlock,renderList:_renderList,Fragment:_Fragment,normalizeStyle:_normalizeStyle,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-162a4a8c"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vuepanel-config" };
const _hoisted_2 = { class: "vpc-shell" };
const _hoisted_3 = { class: "vpc-card vpc-hero" };
const _hoisted_4 = { class: "vpc-copy" };
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-badge" }, "Vue-面板", -1));
const _hoisted_6 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h1", { class: "vpc-title" }, "配置页", -1));
const _hoisted_7 = { class: "vpc-chip-row" };
const _hoisted_8 = { class: "vpc-chip" };
const _hoisted_9 = { class: "vpc-chip" };
const _hoisted_10 = {
  key: 0,
  class: "vpc-chip"
};
const _hoisted_11 = { class: "vpc-chip" };
const _hoisted_12 = { class: "vpc-action-grid" };
const _hoisted_13 = { class: "vpc-card" };
const _hoisted_14 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-section-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "插件级设置"),
    /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "全局选项")
  ])
], -1));
const _hoisted_15 = { class: "vpc-switch-grid plugin" };
const _hoisted_16 = { class: "vpc-switch-card" };
const _hoisted_17 = { class: "vpc-switch-card" };
const _hoisted_18 = { class: "vpc-switch-card" };
const _hoisted_19 = { class: "vpc-switch-card" };
const _hoisted_20 = { class: "vpc-switch-card" };
const _hoisted_21 = {
  key: 1,
  class: "vpc-card"
};
const _hoisted_22 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-section-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "固定模块"),
    /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "固定功能卡片")
  ]),
  /*#__PURE__*/_createElementVNode("div", { class: "vpc-note" }, "模块默认都是固定单卡，只有你明确说明为多站点模块时，才会开放新增站点。")
], -1));
const _hoisted_23 = { class: "vpc-fixed-grid" };
const _hoisted_24 = { class: "vpc-editor-head" };
const _hoisted_25 = { class: "vpc-kicker" };
const _hoisted_26 = { class: "vpc-editor-title" };
const _hoisted_27 = { class: "vpc-editor-site" };
const _hoisted_28 = { class: "vpc-switch-grid compact" };
const _hoisted_29 = { class: "vpc-switch-card" };
const _hoisted_30 = { class: "vpc-switch-card" };
const _hoisted_31 = { class: "vpc-field-stack" };
const _hoisted_32 = { class: "vpc-field-card" };
const _hoisted_33 = { class: "vpc-field-card" };
const _hoisted_34 = { class: "vpc-note" };
const _hoisted_35 = { class: "vpc-section-head" };
const _hoisted_36 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "多站点模块", -1));
const _hoisted_37 = { class: "vpc-section-title" };
const _hoisted_38 = { class: "vpc-toolbar-actions" };
const _hoisted_39 = { class: "vpc-note" };
const _hoisted_40 = {
  key: 0,
  class: "vpc-empty"
};
const _hoisted_41 = {
  key: 1,
  class: "vpc-site-grid"
};
const _hoisted_42 = { class: "vpc-editor-head" };
const _hoisted_43 = { class: "vpc-kicker" };
const _hoisted_44 = { class: "vpc-editor-title" };
const _hoisted_45 = { class: "vpc-inline-actions" };
const _hoisted_46 = { class: "vpc-switch-grid compact" };
const _hoisted_47 = { class: "vpc-switch-card" };
const _hoisted_48 = { class: "vpc-switch-card" };
const _hoisted_49 = { class: "vpc-field-stack" };
const _hoisted_50 = { class: "vpc-field-card" };
const _hoisted_51 = { class: "vpc-field-card" };

const {computed,onMounted,reactive,ref} = await importShared('vue');


const DEFAULT_CARD_CRON = '5 8 * * *';


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
const moduleItems = ref([]);
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  cron: DEFAULT_CARD_CRON,
  http_timeout: 15,
  http_retry_times: 3,
  random_delay_max_seconds: 5,
  cards: [],
});

const singletonModules = computed(() => moduleItems.value.filter((item) => item.singleton !== false));
const collectionModules = computed(() => moduleItems.value.filter((item) => item.singleton === false));
const fixedCards = computed(() => singletonModules.value.map((module) => ensureFixedCard(module.key)));
const scheduledCards = computed(() => config.cards.filter((card) => card.enabled && card.auto_run));

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function deepClone(value) {
  return JSON.parse(JSON.stringify(value))
}

function moduleMeta(moduleKey) {
  return moduleItems.value.find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    icon: '🧩',
    default_site_name: '',
    default_site_url: '',
    tone: 'azure',
    singleton: true,
  }
}

function nextCardId(moduleKey) {
  return `${moduleKey}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpc-tone-rgb': '40,181,120' },
    azure: { '--vpc-tone-rgb': '46,134,255' },
    amber: { '--vpc-tone-rgb': '255,170,63' },
    rose: { '--vpc-tone-rgb': '230,92,124' },
    violet: { '--vpc-tone-rgb': '132,108,255' },
    slate: { '--vpc-tone-rgb': '120,132,155' },
  };
  return map[tone] || map.azure
}

function fixedCookieNote(moduleKey) {
  return moduleKey === 'hnr_claim' ? '和思齐签到共用同站 Cookie。' : '填写思齐站点 Cookie 后可执行。'
}

function showUidField(moduleKey) {
  return moduleKey === 'newapi_checkin'
}

function buildFixedCard(moduleKey, current = {}) {
  const meta = moduleMeta(moduleKey);
  return {
    id: moduleKey,
    title: current.title || meta.label,
    module_key: moduleKey,
    site_name: current.site_name || meta.default_site_name || meta.label,
    site_url: current.site_url || meta.default_site_url || '',
    enabled: !!current.enabled,
    auto_run: current.auto_run !== false,
    cron: String(current.cron || DEFAULT_CARD_CRON),
    show_status: true,
    notify: current.notify !== false,
    tone: current.tone || meta.tone || 'azure',
    cookie: String(current.cookie || ''),
    uid: '',
    note: String(current.note || ''),
  }
}

function buildCollectionCard(moduleKey, current = {}) {
  const meta = moduleMeta(moduleKey);
  return {
    id: current.id || nextCardId(moduleKey),
    title: current.title || current.site_name || meta.label,
    module_key: moduleKey,
    site_name: current.site_name || meta.default_site_name || '',
    site_url: current.site_url || meta.default_site_url || '',
    enabled: !!current.enabled,
    auto_run: current.auto_run !== false,
    cron: String(current.cron || DEFAULT_CARD_CRON),
    show_status: true,
    notify: current.notify !== false,
    tone: current.tone || meta.tone || 'azure',
    cookie: String(current.cookie || ''),
    uid: showUidField(moduleKey) ? String(current.uid || '225') : '',
    note: String(current.note || ''),
  }
}

function ensureStructure(cards = []) {
  const fixedMap = new Map();
  const collectionMap = new Map();

  for (const module of collectionModules.value) collectionMap.set(module.key, []);

  for (const item of cards) {
    if (!item || typeof item !== 'object') continue
    const moduleKey = String(item.module_key || '');
    if (singletonModules.value.some((module) => module.key === moduleKey)) {
      if (!fixedMap.has(moduleKey)) fixedMap.set(moduleKey, buildFixedCard(moduleKey, item));
      continue
    }
    if (collectionMap.has(moduleKey)) collectionMap.get(moduleKey).push(buildCollectionCard(moduleKey, item));
  }

  const normalized = [
    ...singletonModules.value.map((module) => fixedMap.get(module.key) || buildFixedCard(module.key)),
    ...collectionModules.value.flatMap((module) => {
      const items = collectionMap.get(module.key) || [];
      return items.length ? items : [buildCollectionCard(module.key)]
    }),
  ];

  config.cards.splice(0, config.cards.length, ...normalized);
}

function ensureFixedCard(moduleKey) {
  let card = config.cards.find((item) => item.module_key === moduleKey);
  if (!card) {
    card = buildFixedCard(moduleKey);
    config.cards.push(card);
  }
  return card
}

function cardsForModule(moduleKey) {
  return config.cards.filter((card) => card.module_key === moduleKey)
}

function addCollectionCard(moduleKey) {
  config.cards.push(buildCollectionCard(moduleKey));
}

function removeCollectionCard(moduleKey, cardId) {
  const index = config.cards.findIndex((card) => card.id === cardId && card.module_key === moduleKey);
  if (index >= 0) config.cards.splice(index, 1);
  if (!cardsForModule(moduleKey).length) addCollectionCard(moduleKey);
}

function serializeConfig() {
  const cards = [
    ...singletonModules.value.map((module) => buildFixedCard(module.key, ensureFixedCard(module.key))),
    ...collectionModules.value.flatMap((module) =>
      cardsForModule(module.key).map((card) =>
        buildCollectionCard(module.key, {
          ...card,
          title: String(card.site_name || card.title || module.label).trim() || module.label,
        }),
      ),
    ),
  ];

  return {
    ...deepClone(config),
    cards,
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VuePanel/config');
    moduleItems.value = res.module_options || [];
    Object.assign(config, {
      enabled: !!res.enabled,
      notify: !!res.notify,
      onlyonce: !!res.onlyonce,
      use_proxy: !!res.use_proxy,
      force_ipv4: res.force_ipv4 !== false,
      cron: res.cron || DEFAULT_CARD_CRON,
      http_timeout: Number(res.http_timeout || 15),
      http_retry_times: Number(res.http_retry_times || 3),
      random_delay_max_seconds: Number(res.random_delay_max_seconds || 5),
      cards: [],
    });
    ensureStructure(deepClone(res.cards || []));
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error');
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const res = await props.api.post('/plugin/VuePanel/config', serializeConfig());
    flash(res.message || '配置已保存');
    await loadConfig();
  } catch (error) {
    flash(error?.message || '保存失败', 'error');
  } finally {
    saving.value = false;
  }
}

function closePlugin() {
  emit('close');
}

onMounted(async () => {
  await loadConfig();
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_v_text_field = _resolveComponent("v-text-field");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("header", _hoisted_3, [
        _createElementVNode("div", _hoisted_4, [
          _hoisted_5,
          _hoisted_6,
          _createElementVNode("div", _hoisted_7, [
            _createElementVNode("span", _hoisted_8, "主题 " + _toDisplayString(__props.themeLabel), 1),
            _createElementVNode("span", _hoisted_9, "固定任务 " + _toDisplayString(fixedCards.value.length) + " 个", 1),
            (collectionModules.value.length)
              ? (_openBlock(), _createElementBlock("span", _hoisted_10, "多站点模块 " + _toDisplayString(collectionModules.value.length) + " 个", 1))
              : _createCommentVNode("", true),
            _createElementVNode("span", _hoisted_11, "定时卡片 " + _toDisplayString(scheduledCards.value.length), 1)
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
      _createElementVNode("section", _hoisted_13, [
        _hoisted_14,
        _createElementVNode("div", _hoisted_15, [
          _createElementVNode("div", _hoisted_16, [
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              class: "vpc-switch",
              label: "启用插件",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_17, [
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.notify) = $event)),
              class: "vpc-switch",
              label: "开启通知",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_18, [
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.onlyonce) = $event)),
              class: "vpc-switch",
              label: "保存后执行一次",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_19, [
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.use_proxy) = $event)),
              class: "vpc-switch",
              label: "使用代理",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_20, [
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.force_ipv4) = $event)),
              class: "vpc-switch",
              label: "优先 IPv4",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ])
      ]),
      (fixedCards.value.length)
        ? (_openBlock(), _createElementBlock("section", _hoisted_21, [
            _hoisted_22,
            _createElementVNode("div", _hoisted_23, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(fixedCards.value, (card) => {
                return (_openBlock(), _createElementBlock("article", {
                  key: card.id,
                  class: "vpc-editor fixed",
                  style: _normalizeStyle(toneStyle(card.tone))
                }, [
                  _createElementVNode("div", _hoisted_24, [
                    _createElementVNode("div", null, [
                      _createElementVNode("div", _hoisted_25, _toDisplayString(moduleMeta(card.module_key).label), 1),
                      _createElementVNode("h3", _hoisted_26, _toDisplayString(card.title), 1)
                    ]),
                    _createElementVNode("span", _hoisted_27, _toDisplayString(card.site_url), 1)
                  ]),
                  _createElementVNode("div", _hoisted_28, [
                    _createElementVNode("div", _hoisted_29, [
                      _createVNode(_component_v_switch, {
                        modelValue: card.enabled,
                        "onUpdate:modelValue": $event => ((card.enabled) = $event),
                        class: "vpc-switch",
                        label: "启用",
                        density: "compact",
                        "hide-details": "",
                        inset: ""
                      }, null, 8, ["modelValue", "onUpdate:modelValue"])
                    ]),
                    _createElementVNode("div", _hoisted_30, [
                      _createVNode(_component_v_switch, {
                        modelValue: card.auto_run,
                        "onUpdate:modelValue": $event => ((card.auto_run) = $event),
                        class: "vpc-switch",
                        label: "定时运行",
                        density: "compact",
                        "hide-details": "",
                        inset: ""
                      }, null, 8, ["modelValue", "onUpdate:modelValue"])
                    ])
                  ]),
                  _createElementVNode("div", _hoisted_31, [
                    _createElementVNode("div", _hoisted_32, [
                      _createVNode(_component_VCronField, {
                        modelValue: card.cron,
                        "onUpdate:modelValue": $event => ((card.cron) = $event),
                        label: "定时运行 Cron",
                        density: "comfortable",
                        class: "vpc-cron-field"
                      }, null, 8, ["modelValue", "onUpdate:modelValue"])
                    ]),
                    _createElementVNode("div", _hoisted_33, [
                      _createVNode(_component_v_text_field, {
                        modelValue: card.cookie,
                        "onUpdate:modelValue": $event => ((card.cookie) = $event),
                        label: "站点 Cookie",
                        variant: "outlined",
                        density: "comfortable",
                        "hide-details": "auto"
                      }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                      _createElementVNode("div", _hoisted_34, _toDisplayString(fixedCookieNote(card.module_key)), 1)
                    ])
                  ])
                ], 4))
              }), 128))
            ])
          ]))
        : _createCommentVNode("", true),
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(collectionModules.value, (module) => {
        return (_openBlock(), _createElementBlock("section", {
          key: module.key,
          class: "vpc-card"
        }, [
          _createElementVNode("div", _hoisted_35, [
            _createElementVNode("div", null, [
              _hoisted_36,
              _createElementVNode("h2", _hoisted_37, _toDisplayString(module.icon) + " " + _toDisplayString(module.label), 1)
            ]),
            _createElementVNode("div", _hoisted_38, [
              _createVNode(_component_v_btn, {
                color: "info",
                variant: "flat",
                onClick: $event => (addCollectionCard(module.key))
              }, {
                default: _withCtx(() => [
                  _createTextVNode("新增站点")
                ]),
                _: 2
              }, 1032, ["onClick"])
            ])
          ]),
          _createElementVNode("div", _hoisted_39, _toDisplayString(module.description) + " 只有这类显式多站点模块才支持新增站点卡。", 1),
          (!cardsForModule(module.key).length)
            ? (_openBlock(), _createElementBlock("div", _hoisted_40, "当前没有站点卡片，点击“新增站点”创建。"))
            : (_openBlock(), _createElementBlock("div", _hoisted_41, [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(cardsForModule(module.key), (card, index) => {
                  return (_openBlock(), _createElementBlock("article", {
                    key: card.id,
                    class: "vpc-editor",
                    style: _normalizeStyle(toneStyle(card.tone || module.tone))
                  }, [
                    _createElementVNode("div", _hoisted_42, [
                      _createElementVNode("div", null, [
                        _createElementVNode("div", _hoisted_43, "站点 " + _toDisplayString(index + 1), 1),
                        _createElementVNode("h3", _hoisted_44, _toDisplayString(card.site_name || `${module.label} 站点 ${index + 1}`), 1)
                      ]),
                      _createElementVNode("div", _hoisted_45, [
                        _createVNode(_component_v_btn, {
                          size: "small",
                          variant: "text",
                          color: "error",
                          onClick: $event => (removeCollectionCard(module.key, card.id))
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode("删除")
                          ]),
                          _: 2
                        }, 1032, ["onClick"])
                      ])
                    ]),
                    _createElementVNode("div", _hoisted_46, [
                      _createElementVNode("div", _hoisted_47, [
                        _createVNode(_component_v_switch, {
                          modelValue: card.enabled,
                          "onUpdate:modelValue": $event => ((card.enabled) = $event),
                          class: "vpc-switch",
                          label: "启用",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue", "onUpdate:modelValue"])
                      ]),
                      _createElementVNode("div", _hoisted_48, [
                        _createVNode(_component_v_switch, {
                          modelValue: card.auto_run,
                          "onUpdate:modelValue": $event => ((card.auto_run) = $event),
                          class: "vpc-switch",
                          label: "定时运行",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue", "onUpdate:modelValue"])
                      ])
                    ]),
                    _createElementVNode("div", {
                      class: _normalizeClass(["vpc-field-grid collection", { 'with-uid': showUidField(module.key) }])
                    }, [
                      _createVNode(_component_v_text_field, {
                        modelValue: card.site_name,
                        "onUpdate:modelValue": $event => ((card.site_name) = $event),
                        label: "网站名称",
                        variant: "outlined",
                        density: "comfortable",
                        "hide-details": "auto"
                      }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                      _createVNode(_component_v_text_field, {
                        modelValue: card.site_url,
                        "onUpdate:modelValue": $event => ((card.site_url) = $event),
                        label: "网站地址",
                        variant: "outlined",
                        density: "comfortable",
                        "hide-details": "auto"
                      }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                      (showUidField(module.key))
                        ? (_openBlock(), _createBlock(_component_v_text_field, {
                            key: 0,
                            modelValue: card.uid,
                            "onUpdate:modelValue": $event => ((card.uid) = $event),
                            label: "UID",
                            variant: "outlined",
                            density: "comfortable",
                            "hide-details": "auto"
                          }, null, 8, ["modelValue", "onUpdate:modelValue"]))
                        : _createCommentVNode("", true)
                    ], 2),
                    _createElementVNode("div", _hoisted_49, [
                      _createElementVNode("div", _hoisted_50, [
                        _createVNode(_component_VCronField, {
                          modelValue: card.cron,
                          "onUpdate:modelValue": $event => ((card.cron) = $event),
                          label: "定时运行 Cron",
                          density: "comfortable",
                          class: "vpc-cron-field"
                        }, null, 8, ["modelValue", "onUpdate:modelValue"])
                      ]),
                      _createElementVNode("div", _hoisted_51, [
                        _createVNode(_component_v_text_field, {
                          modelValue: card.cookie,
                          "onUpdate:modelValue": $event => ((card.cookie) = $event),
                          label: "站点 Cookie",
                          variant: "outlined",
                          density: "comfortable",
                          "hide-details": "auto"
                        }, null, 8, ["modelValue", "onUpdate:modelValue"])
                      ])
                    ])
                  ], 4))
                }), 128))
              ]))
        ]))
      }), 128))
    ])
  ]))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-162a4a8c"]]);

export { ConfigView as default };
