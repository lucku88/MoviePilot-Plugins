import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_76672841_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,normalizeStyle:_normalizeStyle,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-76672841"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vp-shell" };
const _hoisted_2 = { class: "vp-card vp-hero" };
const _hoisted_3 = { class: "vp-hero-copy" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-badge" }, "Vue-面板", -1));
const _hoisted_5 = { class: "vp-title" };
const _hoisted_6 = { class: "vp-subtitle" };
const _hoisted_7 = { class: "vp-chip-row" };
const _hoisted_8 = { class: "vp-chip" };
const _hoisted_9 = { class: "vp-chip" };
const _hoisted_10 = { class: "vp-chip" };
const _hoisted_11 = { class: "vp-action-grid" };
const _hoisted_12 = { class: "vp-stat-grid" };
const _hoisted_13 = { class: "vp-stat-label" };
const _hoisted_14 = { class: "vp-stat-value" };
const _hoisted_15 = {
  key: 1,
  class: "vp-card vp-empty"
};
const _hoisted_16 = { class: "vp-site-head" };
const _hoisted_17 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-site-kicker" }, "网站分组", -1));
const _hoisted_18 = { class: "vp-site-title" };
const _hoisted_19 = { class: "vp-site-url" };
const _hoisted_20 = { class: "vp-site-note" };
const _hoisted_21 = { class: "vp-module-stack" };
const _hoisted_22 = { class: "vp-module-head" };
const _hoisted_23 = { class: "vp-card-grid" };
const _hoisted_24 = { class: "vp-panel-top" };
const _hoisted_25 = { class: "vp-panel-kicker" };
const _hoisted_26 = { class: "vp-panel-title" };
const _hoisted_27 = { class: "vp-level" };
const _hoisted_28 = { class: "vp-panel-text" };
const _hoisted_29 = {
  key: 0,
  class: "vp-metric-grid"
};
const _hoisted_30 = { class: "vp-metric-label" };
const _hoisted_31 = { class: "vp-metric-value" };
const _hoisted_32 = { class: "vp-tag-row" };
const _hoisted_33 = {
  key: 1,
  class: "vp-detail-list"
};
const _hoisted_34 = { class: "vp-meta-row" };
const _hoisted_35 = { class: "vp-btn-row" };
const _hoisted_36 = { class: "vp-card" };
const _hoisted_37 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-site-head compact" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "vp-site-kicker" }, "执行历史"),
    /*#__PURE__*/_createElementVNode("h2", { class: "vp-site-title" }, "最近记录")
  ])
], -1));
const _hoisted_38 = {
  key: 0,
  class: "vp-empty mini"
};
const _hoisted_39 = {
  key: 1,
  class: "vp-history-list"
};
const _hoisted_40 = { class: "vp-history-top" };
const _hoisted_41 = {
  key: 0,
  class: "vp-history-lines"
};

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Page',
  props: { api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } },
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;




const rootEl = ref(null);
const isDarkTheme = ref(false);
const loading = ref(false);
const runningCardId = ref('');
const refreshingCardId = ref('');
const status = reactive({ dashboard: {}, history: [] });
const message = reactive({ text: '', type: 'success' });

let themeObserver = null;
let mediaQuery = null;

const dashboard = computed(() => status.dashboard || {});
const groups = computed(() => dashboard.value.groups || []);
const historyItems = computed(() => status.history || dashboard.value.history || []);

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vp-tone-rgb': '40,181,120' },
    azure: { '--vp-tone-rgb': '46,134,255' },
    amber: { '--vp-tone-rgb': '255,170,63' },
    rose: { '--vp-tone-rgb': '230,92,124' },
    violet: { '--vp-tone-rgb': '132,108,255' },
    slate: { '--vp-tone-rgb': '120,132,155' },
  };
  return map[tone] || map.azure
}

function levelLabel(level) {
  return ({ success: '正常', warning: '待处理', error: '异常', info: '信息' })[level] || '信息'
}

async function loadStatus(showError = true) {
  try {
    Object.assign(status, await props.api.get('/plugin/VuePanel/status') || {});
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error');
    return false
  }
}

async function refreshStatus() {
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/VuePanel/refresh', {});
    flash(res.message || '已刷新');
    await loadStatus(false);
  } catch (error) {
    flash(error?.message || '刷新失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function runAll() {
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/VuePanel/run', {});
    flash(res.message || '执行完成');
    await loadStatus(false);
  } catch (error) {
    flash(error?.message || '执行失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function runCard(card) {
  runningCardId.value = card.card_id;
  try {
    const res = await props.api.post('/plugin/VuePanel/card/run', { card_id: card.card_id });
    flash(res.message || '卡片执行完成');
    await loadStatus(false);
  } catch (error) {
    flash(error?.message || '卡片执行失败', 'error');
  } finally {
    runningCardId.value = '';
  }
}

async function refreshCard(card) {
  refreshingCardId.value = card.card_id;
  try {
    const res = await props.api.post('/plugin/VuePanel/card/refresh', { card_id: card.card_id });
    flash(res.message || '卡片状态已刷新');
    await loadStatus(false);
  } catch (error) {
    flash(error?.message || '卡片刷新失败', 'error');
  } finally {
    refreshingCardId.value = '';
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
  if (isDark) {
    isDarkTheme.value = true;
    return
  }
  isDarkTheme.value = !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;
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
  await loadStatus();
});

onBeforeUnmount(() => {
  themeObserver?.disconnect?.();
  mediaQuery?.removeEventListener?.('change', detectTheme);
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["vuepanel-page", { 'is-dark-theme': isDarkTheme.value }])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("section", _hoisted_2, [
        _createElementVNode("div", _hoisted_3, [
          _hoisted_4,
          _createElementVNode("h1", _hoisted_5, _toDisplayString(dashboard.value.title || '网站 / 功能模块面板'), 1),
          _createElementVNode("p", _hoisted_6, _toDisplayString(dashboard.value.subtitle || '每张配置卡片都拥有独立站点、独立功能和独立样式。'), 1),
          _createElementVNode("div", _hoisted_7, [
            _createElementVNode("span", _hoisted_8, "计划执行 " + _toDisplayString(status.next_run_time || dashboard.value.next_run_time || '未启用'), 1),
            _createElementVNode("span", _hoisted_9, "最近执行 " + _toDisplayString(status.last_run || '暂无'), 1),
            _createElementVNode("span", _hoisted_10, "隐藏卡片 " + _toDisplayString(dashboard.value.hidden_count || '0'), 1)
          ])
        ]),
        _createElementVNode("div", _hoisted_11, [
          _createVNode(_component_v_btn, {
            color: "success",
            variant: "flat",
            loading: loading.value,
            onClick: runAll
          }, {
            default: _withCtx(() => [
              _createTextVNode("执行启用卡片")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            color: "primary",
            variant: "flat",
            loading: loading.value,
            onClick: refreshStatus
          }, {
            default: _withCtx(() => [
              _createTextVNode("刷新状态")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            variant: "text",
            onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'config')))
          }, {
            default: _withCtx(() => [
              _createTextVNode("配置")
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
      _createElementVNode("section", _hoisted_12, [
        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(dashboard.value.overview || [], (item) => {
          return (_openBlock(), _createElementBlock("article", {
            key: item.label,
            class: "vp-card vp-stat"
          }, [
            _createElementVNode("div", _hoisted_13, _toDisplayString(item.label), 1),
            _createElementVNode("div", _hoisted_14, _toDisplayString(item.value), 1)
          ]))
        }), 128))
      ]),
      (!groups.value.length)
        ? (_openBlock(), _createElementBlock("section", _hoisted_15, " 当前没有可展示的状态卡片。去配置页新增卡片，或把已存在卡片设为显示。 "))
        : _createCommentVNode("", true),
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(groups.value, (group) => {
        return (_openBlock(), _createElementBlock("section", {
          key: group.site_key,
          class: "vp-card vp-site"
        }, [
          _createElementVNode("header", _hoisted_16, [
            _createElementVNode("div", null, [
              _hoisted_17,
              _createElementVNode("h2", _hoisted_18, _toDisplayString(group.site_name), 1),
              _createElementVNode("div", _hoisted_19, _toDisplayString(group.site_url), 1)
            ]),
            _createElementVNode("div", _hoisted_20, _toDisplayString(group.subtitle), 1)
          ]),
          _createElementVNode("div", _hoisted_21, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(group.modules || [], (module) => {
              return (_openBlock(), _createElementBlock("article", {
                key: module.module_key,
                class: "vp-module"
              }, [
                _createElementVNode("div", _hoisted_22, [
                  _createElementVNode("h3", null, _toDisplayString(module.module_icon) + " " + _toDisplayString(module.module_name), 1),
                  _createElementVNode("span", null, _toDisplayString((module.cards || []).length) + " 张卡片", 1)
                ]),
                _createElementVNode("div", _hoisted_23, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(module.cards || [], (card) => {
                    return (_openBlock(), _createElementBlock("article", {
                      key: card.card_id,
                      class: _normalizeClass(["vp-panel", `is-${card.level || 'info'}`]),
                      style: _normalizeStyle(toneStyle(card.tone))
                    }, [
                      _createElementVNode("div", _hoisted_24, [
                        _createElementVNode("div", null, [
                          _createElementVNode("div", _hoisted_25, _toDisplayString(card.title), 1),
                          _createElementVNode("div", _hoisted_26, _toDisplayString(card.status_title), 1)
                        ]),
                        _createElementVNode("span", _hoisted_27, _toDisplayString(levelLabel(card.level)), 1)
                      ]),
                      _createElementVNode("div", _hoisted_28, _toDisplayString(card.status_text), 1),
                      (card.metrics?.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_29, [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.metrics, (metric) => {
                              return (_openBlock(), _createElementBlock("div", {
                                key: `${card.card_id}-${metric.label}`,
                                class: "vp-metric"
                              }, [
                                _createElementVNode("div", _hoisted_30, _toDisplayString(metric.label), 1),
                                _createElementVNode("div", _hoisted_31, _toDisplayString(metric.value), 1)
                              ]))
                            }), 128))
                          ]))
                        : _createCommentVNode("", true),
                      _createElementVNode("div", _hoisted_32, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.tags || [], (tag) => {
                          return (_openBlock(), _createElementBlock("span", {
                            key: `${card.card_id}-${tag}`,
                            class: "vp-tag"
                          }, _toDisplayString(tag), 1))
                        }), 128))
                      ]),
                      (card.detail_lines?.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_33, [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.detail_lines, (line) => {
                              return (_openBlock(), _createElementBlock("div", {
                                key: `${card.card_id}-${line}`,
                                class: "vp-detail-item"
                              }, _toDisplayString(line), 1))
                            }), 128))
                          ]))
                        : _createCommentVNode("", true),
                      _createElementVNode("div", _hoisted_34, [
                        _createElementVNode("span", null, "上次执行 " + _toDisplayString(card.last_run || '未执行'), 1),
                        _createElementVNode("span", null, "最近检查 " + _toDisplayString(card.last_checked || '未检查'), 1)
                      ]),
                      _createElementVNode("div", _hoisted_35, [
                        _createVNode(_component_v_btn, {
                          color: "primary",
                          variant: "flat",
                          loading: runningCardId.value === card.card_id,
                          onClick: $event => (runCard(card))
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode("执行")
                          ]),
                          _: 2
                        }, 1032, ["loading", "onClick"]),
                        _createVNode(_component_v_btn, {
                          variant: "text",
                          loading: refreshingCardId.value === card.card_id,
                          onClick: $event => (refreshCard(card))
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode("刷新")
                          ]),
                          _: 2
                        }, 1032, ["loading", "onClick"])
                      ])
                    ], 6))
                  }), 128))
                ])
              ]))
            }), 128))
          ])
        ]))
      }), 128)),
      _createElementVNode("section", _hoisted_36, [
        _hoisted_37,
        (!historyItems.value.length)
          ? (_openBlock(), _createElementBlock("div", _hoisted_38, "暂无执行记录"))
          : (_openBlock(), _createElementBlock("div", _hoisted_39, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(historyItems.value, (item) => {
                return (_openBlock(), _createElementBlock("article", {
                  key: `${item.time}-${item.title}`,
                  class: "vp-history-item"
                }, [
                  _createElementVNode("div", _hoisted_40, [
                    _createElementVNode("strong", null, _toDisplayString(item.title), 1),
                    _createElementVNode("span", null, _toDisplayString(item.time), 1)
                  ]),
                  (item.lines?.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_41, _toDisplayString(item.lines.join(' / ')), 1))
                    : _createCommentVNode("", true)
                ]))
              }), 128))
            ]))
      ])
    ])
  ], 2))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-76672841"]]);

export { PageView as default };
