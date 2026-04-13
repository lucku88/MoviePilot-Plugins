import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_e97043ac_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock,renderList:_renderList,Fragment:_Fragment,normalizeStyle:_normalizeStyle,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-e97043ac"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vpc-shell" };
const _hoisted_2 = { class: "vpc-card vpc-hero" };
const _hoisted_3 = { class: "vpc-copy" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-badge" }, "Vue-面板", -1));
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h1", { class: "vpc-title" }, "卡片配置", -1));
const _hoisted_6 = { class: "vpc-chip-row" };
const _hoisted_7 = { class: "vpc-chip" };
const _hoisted_8 = { class: "vpc-chip" };
const _hoisted_9 = { class: "vpc-chip" };
const _hoisted_10 = { class: "vpc-action-grid" };
const _hoisted_11 = { class: "vpc-card" };
const _hoisted_12 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "插件级设置", -1));
const _hoisted_13 = { class: "vpc-switch-grid" };
const _hoisted_14 = { class: "vpc-switch-card" };
const _hoisted_15 = { class: "vpc-switch-card" };
const _hoisted_16 = { class: "vpc-switch-card" };
const _hoisted_17 = { class: "vpc-switch-card" };
const _hoisted_18 = { class: "vpc-switch-card" };
const _hoisted_19 = { class: "vpc-field-grid plugin" };
const _hoisted_20 = { class: "vpc-card" };
const _hoisted_21 = { class: "vpc-toolbar" };
const _hoisted_22 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("h2", { class: "vpc-section-title" }, "配置卡片"),
  /*#__PURE__*/_createElementVNode("div", { class: "vpc-note" }, "一张配置卡片只控制一张状态卡片。展示 / 隐藏 / 样式 / 功能都在这里独立配置。")
], -1));
const _hoisted_23 = { class: "vpc-toolbar-actions" };
const _hoisted_24 = {
  key: 1,
  class: "vpc-card vpc-empty"
};
const _hoisted_25 = { class: "vpc-group-head" };
const _hoisted_26 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "网站分组", -1));
const _hoisted_27 = { class: "vpc-group-title" };
const _hoisted_28 = { class: "vpc-note" };
const _hoisted_29 = { class: "vpc-note" };
const _hoisted_30 = { class: "vpc-module-stack" };
const _hoisted_31 = { class: "vpc-module-head" };
const _hoisted_32 = { class: "vpc-card-grid" };
const _hoisted_33 = { class: "vpc-editor-head" };
const _hoisted_34 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpc-kicker" }, "状态卡片绑定", -1));
const _hoisted_35 = { class: "vpc-inline-actions" };
const _hoisted_36 = { class: "vpc-switch-grid compact" };
const _hoisted_37 = { class: "vpc-switch-card" };
const _hoisted_38 = { class: "vpc-switch-card" };
const _hoisted_39 = { class: "vpc-switch-card" };
const _hoisted_40 = { class: "vpc-switch-card" };
const _hoisted_41 = { class: "vpc-field-grid" };

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Config',
  props: { initialConfig: { type: Object, default: () => ({}) }, api: { type: Object, default: () => ({}) } },
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;




const rootEl = ref(null);
const isDarkTheme = ref(false);
const saving = ref(false);
const message = reactive({ text: '', type: 'success' });
const moduleItems = ref([]);
const toneItems = ref([]);
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  cron: '5 8 * * *',
  http_timeout: 15,
  http_retry_times: 3,
  random_delay_max_seconds: 5,
  cards: [],
});

let themeObserver = null;
let mediaQuery = null;

const groupedCards = computed(() => {
  const groups = new Map();
  for (const card of config.cards) {
    const siteKey = `${card.site_name}|${card.site_url}`.toLowerCase();
    if (!groups.has(siteKey)) {
      groups.set(siteKey, {
        site_key: siteKey,
        site_name: card.site_name || '未命名网站',
        site_url: card.site_url || '',
        cards_count: 0,
        modules: new Map(),
      });
    }
    const group = groups.get(siteKey);
    group.cards_count += 1;
    const moduleKey = card.module_key || 'siqi_sign';
    const moduleMeta = moduleItems.value.find((item) => item.key === moduleKey) || { key: moduleKey, label: moduleKey, icon: '🧩' };
    if (!group.modules.has(moduleKey)) {
      group.modules.set(moduleKey, {
        module_key: moduleKey,
        module_name: moduleMeta.label,
        module_icon: moduleMeta.icon || '🧩',
        cards: [],
      });
    }
    group.modules.get(moduleKey).cards.push(card);
  }
  return Array.from(groups.values()).map((group) => ({ ...group, modules: Array.from(group.modules.values()) }))
});

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
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

function deepClone(value) {
  return JSON.parse(JSON.stringify(value))
}

function nextCardId(moduleKey) {
  return `${moduleKey}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`
}

function createCard(moduleKey = 'siqi_sign') {
  const moduleMeta = moduleItems.value.find((item) => item.key === moduleKey) || {
    key: moduleKey,
    label: moduleKey,
    default_site_name: '新站点',
    default_site_url: '',
  };
  return {
    id: nextCardId(moduleKey),
    title: moduleMeta.label,
    module_key: moduleKey,
    site_name: moduleMeta.default_site_name || '新站点',
    site_url: moduleMeta.default_site_url || '',
    enabled: false,
    auto_run: true,
    show_status: true,
    notify: true,
    tone: toneItems.value[0]?.key || 'azure',
    cookie: '',
    uid: moduleKey === 'newapi_checkin' ? '225' : '',
    note: '',
  }
}

function addCard(moduleKey) {
  config.cards.push(createCard(moduleKey));
}

function duplicateCard(card) {
  const copied = deepClone(card);
  copied.id = nextCardId(card.module_key);
  copied.title = `${card.title || '卡片'} 复制`;
  config.cards.push(copied);
}

function removeCard(cardId) {
  const index = config.cards.findIndex((card) => card.id === cardId);
  if (index >= 0) config.cards.splice(index, 1);
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VuePanel/config');
    moduleItems.value = res.module_options || [];
    toneItems.value = res.tone_options || [];
    Object.assign(config, {
      enabled: !!res.enabled,
      notify: !!res.notify,
      onlyonce: !!res.onlyonce,
      use_proxy: !!res.use_proxy,
      force_ipv4: res.force_ipv4 !== false,
      cron: res.cron || '5 8 * * *',
      http_timeout: Number(res.http_timeout || 15),
      http_retry_times: Number(res.http_retry_times || 3),
      random_delay_max_seconds: Number(res.random_delay_max_seconds || 5),
      cards: deepClone(res.cards || []),
    });
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error');
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const payload = deepClone(config);
    const res = await props.api.post('/plugin/VuePanel/config', payload);
    moduleItems.value = res.config?.module_options || moduleItems.value;
    toneItems.value = res.config?.tone_options || toneItems.value;
    flash(res.message || '配置已保存');
    await loadConfig();
  } catch (error) {
    flash(error?.message || '保存失败', 'error');
  } finally {
    saving.value = false;
  }
}

function findThemeNode() {
  let current = rootEl.value;
  while (current) {
    if (current.getAttribute?.('data-theme')) return current
    const cls = String(current.className || '').toLowerCase();
    if (cls.includes('theme') || cls.includes('v-theme--') || cls.includes('dark') || cls.includes('light')) return current
    current = current.parentElement;
  }
  return document.body
}

function detectTheme() {
  const nodes = [findThemeNode(), document.documentElement, document.body].filter(Boolean);
  const isDark = nodes.some((node) => {
    const theme = String(node?.getAttribute?.('data-theme') || '').toLowerCase();
    const cls = String(node?.className || '').toLowerCase();
    return ['dark', 'purple', 'transparent'].includes(theme) || cls.includes('dark') || cls.includes('theme-dark') || cls.includes('v-theme--dark')
  });
  isDarkTheme.value = isDark || !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

function bindThemeObserver() {
  detectTheme();
  if (window.MutationObserver) {
    themeObserver = new MutationObserver(detectTheme)
    ;[findThemeNode(), document.documentElement, document.body].filter(Boolean).forEach((node) => {
      themeObserver.observe(node, { attributes: true, attributeFilter: ['data-theme', 'class'] });
    });
  }
  if (window.matchMedia) {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener?.('change', detectTheme);
  }
}

function closePlugin() {
  emit('close');
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
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_textarea = _resolveComponent("v-textarea");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["vuepanel-config", { 'is-dark-theme': isDarkTheme.value }])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("header", _hoisted_2, [
        _createElementVNode("div", _hoisted_3, [
          _hoisted_4,
          _hoisted_5,
          _createElementVNode("div", _hoisted_6, [
            _createElementVNode("span", _hoisted_7, "配置卡片 " + _toDisplayString(config.cards.length), 1),
            _createElementVNode("span", _hoisted_8, "启用插件 " + _toDisplayString(config.enabled ? '是' : '否'), 1),
            _createElementVNode("span", _hoisted_9, "计划执行 " + _toDisplayString(config.cron || '未设置'), 1)
          ])
        ]),
        _createElementVNode("div", _hoisted_10, [
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
      _createElementVNode("section", _hoisted_11, [
        _hoisted_12,
        _createElementVNode("div", _hoisted_13, [
          _createElementVNode("div", _hoisted_14, [
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
              label: "启用插件",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_15, [
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.notify) = $event)),
              label: "发送通知",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_16, [
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.onlyonce) = $event)),
              label: "保存后执行一次",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_17, [
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.use_proxy) = $event)),
              label: "使用代理环境",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_18, [
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.force_ipv4) = $event)),
              label: "强制 IPv4",
              density: "compact",
              "hide-details": "",
              inset: ""
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("div", _hoisted_19, [
          _createVNode(_component_v_text_field, {
            modelValue: config.cron,
            "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.cron) = $event)),
            label: "Cron",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_timeout,
            "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.http_timeout) = $event)),
            modelModifiers: { number: true },
            label: "超时秒数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_retry_times,
            "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.http_retry_times) = $event)),
            modelModifiers: { number: true },
            label: "重试次数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.random_delay_max_seconds,
            "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.random_delay_max_seconds) = $event)),
            modelModifiers: { number: true },
            label: "随机延迟秒数",
            type: "number",
            variant: "outlined",
            density: "comfortable",
            "hide-details": "auto"
          }, null, 8, ["modelValue"])
        ])
      ]),
      _createElementVNode("section", _hoisted_20, [
        _createElementVNode("div", _hoisted_21, [
          _hoisted_22,
          _createElementVNode("div", _hoisted_23, [
            _createVNode(_component_v_btn, {
              color: "success",
              variant: "flat",
              onClick: _cache[10] || (_cache[10] = $event => (addCard('siqi_sign')))
            }, {
              default: _withCtx(() => [
                _createTextVNode("新增思齐签到")
              ]),
              _: 1
            }),
            _createVNode(_component_v_btn, {
              color: "warning",
              variant: "flat",
              onClick: _cache[11] || (_cache[11] = $event => (addCard('hnr_claim')))
            }, {
              default: _withCtx(() => [
                _createTextVNode("新增 HNR 领取")
              ]),
              _: 1
            }),
            _createVNode(_component_v_btn, {
              color: "info",
              variant: "flat",
              onClick: _cache[12] || (_cache[12] = $event => (addCard('newapi_checkin')))
            }, {
              default: _withCtx(() => [
                _createTextVNode("新增 New API")
              ]),
              _: 1
            })
          ])
        ])
      ]),
      (!groupedCards.value.length)
        ? (_openBlock(), _createElementBlock("section", _hoisted_24, " 当前没有配置卡片。点击上面的新增按钮创建第一张卡片。 "))
        : _createCommentVNode("", true),
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(groupedCards.value, (group) => {
        return (_openBlock(), _createElementBlock("section", {
          key: group.site_key,
          class: "vpc-card"
        }, [
          _createElementVNode("div", _hoisted_25, [
            _createElementVNode("div", null, [
              _hoisted_26,
              _createElementVNode("h2", _hoisted_27, _toDisplayString(group.site_name), 1),
              _createElementVNode("div", _hoisted_28, _toDisplayString(group.site_url), 1)
            ]),
            _createElementVNode("div", _hoisted_29, _toDisplayString(group.cards_count) + " 张配置卡片", 1)
          ]),
          _createElementVNode("div", _hoisted_30, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(group.modules, (module) => {
              return (_openBlock(), _createElementBlock("div", {
                key: module.module_key,
                class: "vpc-module"
              }, [
                _createElementVNode("div", _hoisted_31, [
                  _createElementVNode("h3", null, _toDisplayString(module.module_icon) + " " + _toDisplayString(module.module_name), 1),
                  _createElementVNode("span", null, _toDisplayString(module.cards.length) + " 张", 1)
                ]),
                _createElementVNode("div", _hoisted_32, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(module.cards, (card) => {
                    return (_openBlock(), _createElementBlock("article", {
                      key: card.id,
                      class: "vpc-editor",
                      style: _normalizeStyle(toneStyle(card.tone))
                    }, [
                      _createElementVNode("div", _hoisted_33, [
                        _createElementVNode("div", null, [
                          _hoisted_34,
                          _createElementVNode("h4", null, _toDisplayString(card.title || module.module_name), 1)
                        ]),
                        _createElementVNode("div", _hoisted_35, [
                          _createVNode(_component_v_btn, {
                            size: "small",
                            variant: "text",
                            onClick: $event => (duplicateCard(card))
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode("复制")
                            ]),
                            _: 2
                          }, 1032, ["onClick"]),
                          _createVNode(_component_v_btn, {
                            size: "small",
                            variant: "text",
                            color: "error",
                            onClick: $event => (removeCard(card.id))
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode("删除")
                            ]),
                            _: 2
                          }, 1032, ["onClick"])
                        ])
                      ]),
                      _createElementVNode("div", _hoisted_36, [
                        _createElementVNode("div", _hoisted_37, [
                          _createVNode(_component_v_switch, {
                            modelValue: card.enabled,
                            "onUpdate:modelValue": $event => ((card.enabled) = $event),
                            label: "启用",
                            density: "compact",
                            "hide-details": "",
                            inset: ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ]),
                        _createElementVNode("div", _hoisted_38, [
                          _createVNode(_component_v_switch, {
                            modelValue: card.auto_run,
                            "onUpdate:modelValue": $event => ((card.auto_run) = $event),
                            label: "自动执行",
                            density: "compact",
                            "hide-details": "",
                            inset: ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ]),
                        _createElementVNode("div", _hoisted_39, [
                          _createVNode(_component_v_switch, {
                            modelValue: card.show_status,
                            "onUpdate:modelValue": $event => ((card.show_status) = $event),
                            label: "显示状态卡片",
                            density: "compact",
                            "hide-details": "",
                            inset: ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ]),
                        _createElementVNode("div", _hoisted_40, [
                          _createVNode(_component_v_switch, {
                            modelValue: card.notify,
                            "onUpdate:modelValue": $event => ((card.notify) = $event),
                            label: "发送通知",
                            density: "compact",
                            "hide-details": "",
                            inset: ""
                          }, null, 8, ["modelValue", "onUpdate:modelValue"])
                        ])
                      ]),
                      _createElementVNode("div", _hoisted_41, [
                        _createVNode(_component_v_text_field, {
                          modelValue: card.title,
                          "onUpdate:modelValue": $event => ((card.title) = $event),
                          label: "卡片标题",
                          variant: "outlined",
                          density: "comfortable",
                          "hide-details": "auto"
                        }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                        _createVNode(_component_v_select, {
                          modelValue: card.module_key,
                          "onUpdate:modelValue": $event => ((card.module_key) = $event),
                          items: moduleItems.value,
                          "item-title": "label",
                          "item-value": "key",
                          label: "功能模块",
                          variant: "outlined",
                          density: "comfortable",
                          "hide-details": "auto"
                        }, null, 8, ["modelValue", "onUpdate:modelValue", "items"]),
                        _createVNode(_component_v_select, {
                          modelValue: card.tone,
                          "onUpdate:modelValue": $event => ((card.tone) = $event),
                          items: toneItems.value,
                          "item-title": "label",
                          "item-value": "key",
                          label: "卡片样式",
                          variant: "outlined",
                          density: "comfortable",
                          "hide-details": "auto"
                        }, null, 8, ["modelValue", "onUpdate:modelValue", "items"]),
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
                        (card.module_key === 'newapi_checkin')
                          ? (_openBlock(), _createBlock(_component_v_text_field, {
                              key: 0,
                              modelValue: card.uid,
                              "onUpdate:modelValue": $event => ((card.uid) = $event),
                              label: "UID",
                              variant: "outlined",
                              density: "comfortable",
                              "hide-details": "auto"
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]))
                          : _createCommentVNode("", true),
                        _createVNode(_component_v_textarea, {
                          modelValue: card.cookie,
                          "onUpdate:modelValue": $event => ((card.cookie) = $event),
                          label: "Cookie",
                          variant: "outlined",
                          density: "comfortable",
                          rows: "2",
                          "auto-grow": "",
                          "hide-details": "auto",
                          class: "vpc-span-2"
                        }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                        _createVNode(_component_v_textarea, {
                          modelValue: card.note,
                          "onUpdate:modelValue": $event => ((card.note) = $event),
                          label: "备注 / 状态卡片补充说明",
                          variant: "outlined",
                          density: "comfortable",
                          rows: "2",
                          "auto-grow": "",
                          "hide-details": "auto",
                          class: "vpc-span-2"
                        }, null, 8, ["modelValue", "onUpdate:modelValue"])
                      ])
                    ], 4))
                  }), 128))
                ])
              ]))
            }), 128))
          ])
        ]))
      }), 128))
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-e97043ac"]]);

export { ConfigView as default };
