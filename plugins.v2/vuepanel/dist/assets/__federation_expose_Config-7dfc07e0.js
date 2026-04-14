import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc, B as BasePanelCard, a as BaseButton, b as BaseTag, E as EmptyState } from './EmptyState-c135b286.js';

const BaseCronField_vue_vue_type_style_index_0_scoped_5d451913_lang = '';

const {resolveComponent:_resolveComponent$4,mergeProps:_mergeProps$3,openBlock:_openBlock$4,createBlock:_createBlock$3} = await importShared('vue');



const _sfc_main$4 = /*#__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'BaseCronField',
  props: {
  modelValue: { type: String, default: '' },
},
  emits: ['update:modelValue'],
  setup(__props, { emit }) {







return (_ctx, _cache) => {
  const _component_VCronField = _resolveComponent$4("VCronField");

  return (_openBlock$4(), _createBlock$3(_component_VCronField, _mergeProps$3(_ctx.$attrs, {
    "model-value": __props.modelValue,
    class: "mp-cron",
    density: "comfortable",
    "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => (emit('update:modelValue', $event)))
  }), null, 16, ["model-value"]))
}
}

});
const BaseCronField = /*#__PURE__*/_export_sfc(_sfc_main$4, [['__scopeId',"data-v-5d451913"]]);

const BaseInput_vue_vue_type_style_index_0_scoped_8b299c74_lang = '';

const {resolveComponent:_resolveComponent$3,mergeProps:_mergeProps$2,openBlock:_openBlock$3,createBlock:_createBlock$2} = await importShared('vue');



const _sfc_main$3 = /*#__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'BaseInput',
  props: {
  modelValue: { type: [String, Number], default: '' },
},
  emits: ['update:modelValue'],
  setup(__props, { emit }) {







return (_ctx, _cache) => {
  const _component_v_text_field = _resolveComponent$3("v-text-field");

  return (_openBlock$3(), _createBlock$2(_component_v_text_field, _mergeProps$2(_ctx.$attrs, {
    "model-value": __props.modelValue,
    class: "mp-input",
    variant: "outlined",
    density: "comfortable",
    "hide-details": "auto",
    "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => (emit('update:modelValue', $event)))
  }), null, 16, ["model-value"]))
}
}

});
const BaseInput = /*#__PURE__*/_export_sfc(_sfc_main$3, [['__scopeId',"data-v-8b299c74"]]);

const BaseSwitch_vue_vue_type_style_index_0_scoped_bf1c6152_lang = '';

const {resolveComponent:_resolveComponent$2,mergeProps:_mergeProps$1,createVNode:_createVNode$1,toDisplayString:_toDisplayString$1,openBlock:_openBlock$2,createElementBlock:_createElementBlock$1,createCommentVNode:_createCommentVNode$1,pushScopeId:_pushScopeId$1,popScopeId:_popScopeId$1} = await importShared('vue');
const _hoisted_1$1 = { class: "mp-switch-shell" };
const _hoisted_2$1 = {
  key: 0,
  class: "mp-switch-hint"
};


const _sfc_main$2 = /*#__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'BaseSwitch',
  props: {
  modelValue: { type: Boolean, default: false },
  hint: { type: String, default: '' },
},
  emits: ['update:modelValue'],
  setup(__props, { emit }) {







return (_ctx, _cache) => {
  const _component_v_switch = _resolveComponent$2("v-switch");

  return (_openBlock$2(), _createElementBlock$1("div", _hoisted_1$1, [
    _createVNode$1(_component_v_switch, _mergeProps$1(_ctx.$attrs, {
      "model-value": __props.modelValue,
      class: "mp-switch",
      density: "compact",
      "hide-details": "",
      inset: "",
      "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => (emit('update:modelValue', $event)))
    }), null, 16, ["model-value"]),
    (__props.hint)
      ? (_openBlock$2(), _createElementBlock$1("div", _hoisted_2$1, _toDisplayString$1(__props.hint), 1))
      : _createCommentVNode$1("", true)
  ]))
}
}

});
const BaseSwitch = /*#__PURE__*/_export_sfc(_sfc_main$2, [['__scopeId',"data-v-bf1c6152"]]);

const BaseTextarea_vue_vue_type_style_index_0_scoped_932085c2_lang = '';

const {resolveComponent:_resolveComponent$1,mergeProps:_mergeProps,openBlock:_openBlock$1,createBlock:_createBlock$1} = await importShared('vue');



const _sfc_main$1 = /*#__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'BaseTextarea',
  props: {
  modelValue: { type: String, default: '' },
},
  emits: ['update:modelValue'],
  setup(__props, { emit }) {







return (_ctx, _cache) => {
  const _component_v_textarea = _resolveComponent$1("v-textarea");

  return (_openBlock$1(), _createBlock$1(_component_v_textarea, _mergeProps(_ctx.$attrs, {
    "model-value": __props.modelValue,
    class: "mp-textarea",
    variant: "outlined",
    density: "comfortable",
    "auto-grow": "",
    rows: "2",
    "max-rows": "4",
    "hide-details": "auto",
    "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => (emit('update:modelValue', $event)))
  }), null, 16, ["model-value"]))
}
}

});
const BaseTextarea = /*#__PURE__*/_export_sfc(_sfc_main$1, [['__scopeId',"data-v-932085c2"]]);

const Config_vue_vue_type_style_index_0_scoped_5e61d6cf_lang = '';

const {createTextVNode:_createTextVNode,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,resolveComponent:_resolveComponent,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeStyle:_normalizeStyle,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');
const _hoisted_1 = { class: "config-page" };
const _hoisted_2 = { class: "hero-actions" };
const _hoisted_3 = { class: "hero-chips" };
const _hoisted_4 = { class: "global-grid" };
const _hoisted_5 = { class: "switch-tile" };
const _hoisted_6 = { class: "switch-tile" };
const _hoisted_7 = { class: "switch-tile" };
const _hoisted_8 = { class: "switch-tile" };
const _hoisted_9 = { class: "switch-tile" };
const _hoisted_10 = { class: "module-stack" };
const _hoisted_11 = { class: "task-head" };
const _hoisted_12 = { class: "task-kicker" };
const _hoisted_13 = { class: "task-title" };
const _hoisted_14 = { class: "task-subtitle" };
const _hoisted_15 = { class: "task-switch-row" };
const _hoisted_16 = { class: "switch-tile compact" };
const _hoisted_17 = { class: "switch-tile compact" };
const _hoisted_18 = { class: "task-field-grid fixed-grid" };
const _hoisted_19 = { class: "field-block" };
const _hoisted_20 = { class: "field-block field-span-2" };
const _hoisted_21 = { class: "field-note" };
const _hoisted_22 = {
  key: 1,
  class: "site-grid"
};
const _hoisted_23 = { class: "task-head" };
const _hoisted_24 = { class: "task-kicker" };
const _hoisted_25 = { class: "task-title" };
const _hoisted_26 = { class: "task-subtitle" };
const _hoisted_27 = { class: "task-head-actions" };
const _hoisted_28 = { class: "task-switch-row" };
const _hoisted_29 = { class: "switch-tile compact" };
const _hoisted_30 = { class: "switch-tile compact" };
const _hoisted_31 = { class: "task-field-grid collection-grid" };
const _hoisted_32 = { class: "field-block" };
const _hoisted_33 = { class: "field-block" };
const _hoisted_34 = {
  key: 0,
  class: "field-block"
};
const _hoisted_35 = { class: "field-block field-span-3" };

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
    description: '',
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
    emerald: { '--task-tone': '31, 168, 104' },
    azure: { '--task-tone': '79, 134, 255' },
    amber: { '--task-tone': '229, 155, 47' },
    rose: { '--task-tone': '220, 87, 87' },
    violet: { '--task-tone': '139, 92, 246' },
    slate: { '--task-tone': '120, 132, 155' },
  };
  return map[tone] || map.azure
}

function fixedCookieNote(moduleKey) {
  return moduleKey === 'hnr_claim' ? '和思齐签到共用同站 Cookie。' : '填写思齐站点 Cookie 后即可执行。'
}

function showUidField(moduleKey) {
  return moduleKey === 'newapi_checkin'
}

function cardsForModule(moduleKey) {
  return config.cards.filter((card) => card.module_key === moduleKey)
}

function buildFixedCard(moduleKey, current = {}) {
  const meta = moduleMeta(moduleKey);
  return {
    id: moduleKey,
    title: meta.label,
    module_key: moduleKey,
    site_name: meta.default_site_name || meta.label,
    site_url: meta.default_site_url || '',
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
  const _component_v_alert = _resolveComponent("v-alert");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(BasePanelCard, {
      kicker: "Vue-面板",
      title: "模块化配置后台",
      subtitle: `当前主题：${__props.themeLabel}。模块默认按固定单卡管理，只有明确声明的功能才会开放站点子卡。`,
      tone: "primary",
      class: "config-hero"
    }, {
      actions: _withCtx(() => [
        _createElementVNode("div", _hoisted_2, [
          _createVNode(BaseButton, {
            loading: saving.value,
            onClick: saveConfig
          }, {
            default: _withCtx(() => [
              _createTextVNode("保存")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(BaseButton, {
            variant: "secondary",
            onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'page')))
          }, {
            default: _withCtx(() => [
              _createTextVNode("运行看板")
            ]),
            _: 1
          }),
          _createVNode(BaseButton, {
            variant: "ghost",
            onClick: closePlugin
          }, {
            default: _withCtx(() => [
              _createTextVNode("关闭")
            ]),
            _: 1
          })
        ])
      ]),
      default: _withCtx(() => [
        _createElementVNode("div", _hoisted_3, [
          _createVNode(BaseTag, { tone: "primary" }, {
            default: _withCtx(() => [
              _createTextVNode("主题 " + _toDisplayString(__props.themeLabel), 1)
            ]),
            _: 1
          }),
          _createVNode(BaseTag, { tone: "success" }, {
            default: _withCtx(() => [
              _createTextVNode("固定模块 " + _toDisplayString(singletonModules.value.length), 1)
            ]),
            _: 1
          }),
          _createVNode(BaseTag, { tone: "info" }, {
            default: _withCtx(() => [
              _createTextVNode("多站点模块 " + _toDisplayString(collectionModules.value.length), 1)
            ]),
            _: 1
          }),
          _createVNode(BaseTag, { tone: "warning" }, {
            default: _withCtx(() => [
              _createTextVNode("定时卡 " + _toDisplayString(scheduledCards.value.length), 1)
            ]),
            _: 1
          })
        ])
      ]),
      _: 1
    }, 8, ["subtitle"]),
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
    _createVNode(BasePanelCard, {
      kicker: "插件级设置",
      title: "全局选项",
      subtitle: "这里只保留插件级开关，不把单卡 Cron、Cookie 和站点字段混进全局层。",
      tone: "azure",
      compact: ""
    }, {
      default: _withCtx(() => [
        _createElementVNode("div", _hoisted_4, [
          _createElementVNode("div", _hoisted_5, [
            _createVNode(BaseSwitch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              label: "启用插件",
              hint: "关闭后所有卡片都不会自动执行。"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_6, [
            _createVNode(BaseSwitch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.notify) = $event)),
              label: "开启通知",
              hint: "执行结果会写入状态页通知区。"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_7, [
            _createVNode(BaseSwitch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.onlyonce) = $event)),
              label: "保存后执行一次",
              hint: "用于快速校验配置是否可用。"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_8, [
            _createVNode(BaseSwitch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.use_proxy) = $event)),
              label: "使用代理",
              hint: "请求跟随宿主代理设置。"
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_9, [
            _createVNode(BaseSwitch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.force_ipv4) = $event)),
              label: "优先 IPv4",
              hint: "保留原有网络访问偏好。"
            }, null, 8, ["modelValue"])
          ])
        ])
      ]),
      _: 1
    }),
    _createElementVNode("section", _hoisted_10, [
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(singletonModules.value, (module) => {
        return (_openBlock(), _createBlock(BasePanelCard, {
          key: module.key,
          kicker: "固定模块",
          title: `${module.icon} ${module.label}`,
          subtitle: module.description,
          tone: module.tone,
          compact: ""
        }, {
          default: _withCtx(() => [
            _createElementVNode("article", {
              class: "task-editor fixed",
              style: _normalizeStyle(toneStyle(ensureFixedCard(module.key).tone || module.tone))
            }, [
              _createElementVNode("div", _hoisted_11, [
                _createElementVNode("div", null, [
                  _createElementVNode("div", _hoisted_12, _toDisplayString(module.label), 1),
                  _createElementVNode("div", _hoisted_13, _toDisplayString(ensureFixedCard(module.key).title), 1),
                  _createElementVNode("div", _hoisted_14, _toDisplayString(ensureFixedCard(module.key).site_url), 1)
                ]),
                _createVNode(BaseTag, {
                  tone: ensureFixedCard(module.key).enabled ? 'success' : 'disabled',
                  size: "sm"
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(ensureFixedCard(module.key).enabled ? '已启用' : '已停用'), 1)
                  ]),
                  _: 2
                }, 1032, ["tone"])
              ]),
              _createElementVNode("div", _hoisted_15, [
                _createElementVNode("div", _hoisted_16, [
                  _createVNode(BaseSwitch, {
                    modelValue: ensureFixedCard(module.key).enabled,
                    "onUpdate:modelValue": $event => ((ensureFixedCard(module.key).enabled) = $event),
                    label: "启用"
                  }, null, 8, ["modelValue", "onUpdate:modelValue"])
                ]),
                _createElementVNode("div", _hoisted_17, [
                  _createVNode(BaseSwitch, {
                    modelValue: ensureFixedCard(module.key).auto_run,
                    "onUpdate:modelValue": $event => ((ensureFixedCard(module.key).auto_run) = $event),
                    label: "定时运行"
                  }, null, 8, ["modelValue", "onUpdate:modelValue"])
                ])
              ]),
              _createElementVNode("div", _hoisted_18, [
                _createElementVNode("div", _hoisted_19, [
                  _createVNode(BaseCronField, {
                    modelValue: ensureFixedCard(module.key).cron,
                    "onUpdate:modelValue": $event => ((ensureFixedCard(module.key).cron) = $event),
                    label: "定时运行 Cron"
                  }, null, 8, ["modelValue", "onUpdate:modelValue"])
                ]),
                _createElementVNode("div", _hoisted_20, [
                  _createVNode(BaseTextarea, {
                    modelValue: ensureFixedCard(module.key).cookie,
                    "onUpdate:modelValue": $event => ((ensureFixedCard(module.key).cookie) = $event),
                    label: "站点 Cookie",
                    placeholder: "例如 c_secure_pass=..."
                  }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                  _createElementVNode("div", _hoisted_21, _toDisplayString(fixedCookieNote(module.key)), 1)
                ])
              ])
            ], 4)
          ]),
          _: 2
        }, 1032, ["title", "subtitle", "tone"]))
      }), 128)),
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(collectionModules.value, (module) => {
        return (_openBlock(), _createBlock(BasePanelCard, {
          key: module.key,
          kicker: "多站点模块",
          title: `${module.icon} ${module.label}`,
          subtitle: `${module.description} 只有这类显式多站点模块才支持在模块内继续新增站点卡。`,
          tone: module.tone,
          compact: ""
        }, {
          actions: _withCtx(() => [
            _createVNode(BaseButton, {
              variant: "secondary",
              onClick: $event => (addCollectionCard(module.key))
            }, {
              default: _withCtx(() => [
                _createTextVNode("新增站点")
              ]),
              _: 2
            }, 1032, ["onClick"])
          ]),
          default: _withCtx(() => [
            (!cardsForModule(module.key).length)
              ? (_openBlock(), _createBlock(EmptyState, {
                  key: 0,
                  title: "暂无站点卡片",
                  description: "点击右上角新增站点，把不同网站和 Cookie 独立管理。"
                }))
              : (_openBlock(), _createElementBlock("div", _hoisted_22, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(cardsForModule(module.key), (card, index) => {
                    return (_openBlock(), _createElementBlock("article", {
                      key: card.id,
                      class: "task-editor",
                      style: _normalizeStyle(toneStyle(card.tone || module.tone))
                    }, [
                      _createElementVNode("div", _hoisted_23, [
                        _createElementVNode("div", null, [
                          _createElementVNode("div", _hoisted_24, "站点 " + _toDisplayString(index + 1), 1),
                          _createElementVNode("div", _hoisted_25, _toDisplayString(card.site_name || `${module.label} 站点 ${index + 1}`), 1),
                          _createElementVNode("div", _hoisted_26, _toDisplayString(card.site_url || '未填写站点地址'), 1)
                        ]),
                        _createElementVNode("div", _hoisted_27, [
                          _createVNode(BaseTag, {
                            tone: card.enabled ? 'success' : 'disabled',
                            size: "sm"
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode(_toDisplayString(card.enabled ? '已启用' : '已停用'), 1)
                            ]),
                            _: 2
                          }, 1032, ["tone"]),
                          _createVNode(BaseButton, {
                            variant: "ghost",
                            size: "sm",
                            onClick: $event => (removeCollectionCard(module.key, card.id))
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode("删除")
                            ]),
                            _: 2
                          }, 1032, ["onClick"])
                        ])
                      ]),
                      _createElementVNode("div", _hoisted_28, [
                        _createElementVNode("div", _hoisted_29, [
                          _createVNode(BaseSwitch, {
                            modelValue: card.enabled,
                            "onUpdate:modelValue": $event => ((card.enabled) = $event),
                            label: "启用"
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ]),
                        _createElementVNode("div", _hoisted_30, [
                          _createVNode(BaseSwitch, {
                            modelValue: card.auto_run,
                            "onUpdate:modelValue": $event => ((card.auto_run) = $event),
                            label: "定时运行"
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ])
                      ]),
                      _createElementVNode("div", _hoisted_31, [
                        _createElementVNode("div", _hoisted_32, [
                          _createVNode(BaseInput, {
                            modelValue: card.site_name,
                            "onUpdate:modelValue": $event => ((card.site_name) = $event),
                            label: "网站名称",
                            placeholder: "例如 Open 站点"
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ]),
                        _createElementVNode("div", _hoisted_33, [
                          _createVNode(BaseInput, {
                            modelValue: card.site_url,
                            "onUpdate:modelValue": $event => ((card.site_url) = $event),
                            label: "网站地址",
                            placeholder: "https://example.com"
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ]),
                        (showUidField(module.key))
                          ? (_openBlock(), _createElementBlock("div", _hoisted_34, [
                              _createVNode(BaseInput, {
                                modelValue: card.uid,
                                "onUpdate:modelValue": $event => ((card.uid) = $event),
                                label: "UID",
                                placeholder: "例如 225"
                              }, null, 8, ["modelValue", "onUpdate:modelValue"])
                            ]))
                          : _createCommentVNode("", true),
                        _createElementVNode("div", {
                          class: _normalizeClass(["field-block", { 'field-span-2': !showUidField(module.key) }])
                        }, [
                          _createVNode(BaseCronField, {
                            modelValue: card.cron,
                            "onUpdate:modelValue": $event => ((card.cron) = $event),
                            label: "定时运行 Cron"
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ], 2),
                        _createElementVNode("div", _hoisted_35, [
                          _createVNode(BaseTextarea, {
                            modelValue: card.cookie,
                            "onUpdate:modelValue": $event => ((card.cookie) = $event),
                            label: "站点 Cookie",
                            placeholder: "每个站点使用各自 Cookie"
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ])
                      ])
                    ], 4))
                  }), 128))
                ]))
          ]),
          _: 2
        }, 1032, ["title", "subtitle", "tone"]))
      }), 128))
    ])
  ]))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-5e61d6cf"]]);

export { ConfigView as default };
