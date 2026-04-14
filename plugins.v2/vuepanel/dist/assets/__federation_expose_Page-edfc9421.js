import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_dd691a91_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,normalizeStyle:_normalizeStyle,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-dd691a91"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vp-shell" };
const _hoisted_2 = { class: "vp-card vp-hero" };
const _hoisted_3 = { class: "vp-copy" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vp-badge" }, "Vue-面板", -1));
const _hoisted_5 = { class: "vp-title" };
const _hoisted_6 = { class: "vp-chip-row" };
const _hoisted_7 = { class: "vp-chip" };
const _hoisted_8 = { class: "vp-chip" };
const _hoisted_9 = { class: "vp-chip" };
const _hoisted_10 = { class: "vp-chip" };
const _hoisted_11 = { class: "vp-action-grid" };
const _hoisted_12 = { class: "vp-stat-grid" };
const _hoisted_13 = { class: "vp-stat-label" };
const _hoisted_14 = { class: "vp-stat-value" };
const _hoisted_15 = { class: "vp-module-head" };
const _hoisted_16 = { class: "vp-kicker" };
const _hoisted_17 = { class: "vp-section-title" };
const _hoisted_18 = { class: "vp-pill-row" };
const _hoisted_19 = {
  key: 0,
  class: "vp-pill"
};
const _hoisted_20 = { class: "vp-panel-top" };
const _hoisted_21 = { class: "vp-panel-kicker" };
const _hoisted_22 = { class: "vp-panel-title" };
const _hoisted_23 = { class: "vp-level" };
const _hoisted_24 = {
  key: 0,
  class: "vp-panel-site"
};
const _hoisted_25 = { class: "vp-panel-text" };
const _hoisted_26 = {
  key: 1,
  class: "vp-metric-grid"
};
const _hoisted_27 = { class: "vp-metric-label" };
const _hoisted_28 = { class: "vp-metric-value" };
const _hoisted_29 = { class: "vp-tag-row" };
const _hoisted_30 = {
  key: 2,
  class: "vp-detail-list"
};
const _hoisted_31 = { class: "vp-meta-grid" };
const _hoisted_32 = { class: "vp-meta-item" };
const _hoisted_33 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vp-meta-label" }, "执行", -1));
const _hoisted_34 = { class: "vp-meta-item" };
const _hoisted_35 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vp-meta-label" }, "计划", -1));
const _hoisted_36 = { class: "vp-btn-row" };
const _hoisted_37 = { class: "vp-history-panel" };
const _hoisted_38 = { class: "vp-history-head" };
const _hoisted_39 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "vp-kicker" }, "模块记录"),
  /*#__PURE__*/_createElementVNode("div", { class: "vp-history-title" }, "最近执行信息")
], -1));
const _hoisted_40 = { class: "vp-note" };
const _hoisted_41 = {
  key: 0,
  class: "vp-empty"
};
const _hoisted_42 = {
  key: 1,
  class: "vp-history-list"
};
const _hoisted_43 = { class: "vp-history-top" };
const _hoisted_44 = {
  key: 0,
  class: "vp-history-meta"
};
const _hoisted_45 = {
  key: 1,
  class: "vp-history-lines"
};

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
},
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
const moduleSections = computed(() => dashboard.value.module_sections || []);
const cardCount = computed(() => moduleSections.value.reduce((total, section) => total + (section.cards?.length || 0), 0));

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

function scheduleText(card) {
  if (!card?.auto_run) return '仅手动'
  if (!status.enabled) return '插件停用'
  return card?.next_run_time || 'Cron 无效'
}

function historyTitle(section, item) {
  if (!section?.singleton) return item?.site_name || item?.title || section?.module_name || ''
  return item?.title || section?.module_name || ''
}

function historyMeta(section, item) {
  if (section?.singleton) return item?.site_name || item?.site_url || ''
  const parts = [];
  if (item?.title && item.title !== item?.site_name) parts.push(item.title);
  if (item?.site_url) parts.push(item.site_url);
  return parts.join(' / ')
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
          _createElementVNode("h1", _hoisted_5, _toDisplayString(dashboard.value.title || '模块状态页'), 1),
          _createElementVNode("div", _hoisted_6, [
            _createElementVNode("span", _hoisted_7, "计划执行 " + _toDisplayString(status.next_run_time || dashboard.value.next_run_time || '未启用'), 1),
            _createElementVNode("span", _hoisted_8, "最近执行 " + _toDisplayString(status.last_run || '暂无'), 1),
            _createElementVNode("span", _hoisted_9, "模块 " + _toDisplayString(moduleSections.value.length) + " 个", 1),
            _createElementVNode("span", _hoisted_10, "卡片 " + _toDisplayString(cardCount.value) + " 张", 1)
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
              _createTextVNode("执行启用任务")
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
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(moduleSections.value, (section) => {
        return (_openBlock(), _createElementBlock("section", {
          key: section.module_key,
          class: "vp-card vp-module",
          style: _normalizeStyle(toneStyle(section.tone))
        }, [
          _createElementVNode("div", _hoisted_15, [
            _createElementVNode("div", null, [
              _createElementVNode("div", _hoisted_16, _toDisplayString(section.singleton ? '固定模块' : '多站点模块'), 1),
              _createElementVNode("h2", _hoisted_17, _toDisplayString(section.module_icon) + " " + _toDisplayString(section.module_name), 1)
            ]),
            _createElementVNode("div", _hoisted_18, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.stats || [], (stat) => {
                return (_openBlock(), _createElementBlock("span", {
                  key: `${section.module_key}-${stat.label}`,
                  class: "vp-pill"
                }, _toDisplayString(stat.label) + " " + _toDisplayString(stat.value), 1))
              }), 128)),
              (section.latest_run)
                ? (_openBlock(), _createElementBlock("span", _hoisted_19, "最近 " + _toDisplayString(section.latest_run), 1))
                : _createCommentVNode("", true)
            ])
          ]),
          _createElementVNode("div", {
            class: _normalizeClass(["vp-module-body", { 'is-single': section.singleton }])
          }, [
            _createElementVNode("div", {
              class: _normalizeClass(["vp-card-grid", { single: section.singleton, multi: !section.singleton }])
            }, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.cards || [], (card) => {
                return (_openBlock(), _createElementBlock("article", {
                  key: card.card_id,
                  class: _normalizeClass(["vp-panel", `is-${card.level || 'info'}`]),
                  style: _normalizeStyle(toneStyle(card.tone))
                }, [
                  _createElementVNode("div", _hoisted_20, [
                    _createElementVNode("div", null, [
                      _createElementVNode("div", _hoisted_21, _toDisplayString(card.site_name), 1),
                      _createElementVNode("div", _hoisted_22, _toDisplayString(card.status_title), 1)
                    ]),
                    _createElementVNode("span", _hoisted_23, _toDisplayString(levelLabel(card.level)), 1)
                  ]),
                  (!section.singleton)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_24, _toDisplayString(card.site_url), 1))
                    : _createCommentVNode("", true),
                  _createElementVNode("div", _hoisted_25, _toDisplayString(card.status_text), 1),
                  (card.metrics?.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_26, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.metrics, (metric) => {
                          return (_openBlock(), _createElementBlock("div", {
                            key: `${card.card_id}-${metric.label}`,
                            class: "vp-metric"
                          }, [
                            _createElementVNode("div", _hoisted_27, _toDisplayString(metric.label), 1),
                            _createElementVNode("div", _hoisted_28, _toDisplayString(metric.value), 1)
                          ]))
                        }), 128))
                      ]))
                    : _createCommentVNode("", true),
                  _createElementVNode("div", _hoisted_29, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.tags || [], (tag) => {
                      return (_openBlock(), _createElementBlock("span", {
                        key: `${card.card_id}-${tag}`,
                        class: "vp-tag"
                      }, _toDisplayString(tag), 1))
                    }), 128))
                  ]),
                  (card.detail_lines?.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_30, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.detail_lines, (line) => {
                          return (_openBlock(), _createElementBlock("div", {
                            key: `${card.card_id}-${line}`,
                            class: "vp-detail-item"
                          }, _toDisplayString(line), 1))
                        }), 128))
                      ]))
                    : _createCommentVNode("", true),
                  _createElementVNode("div", _hoisted_31, [
                    _createElementVNode("div", _hoisted_32, [
                      _hoisted_33,
                      _createElementVNode("strong", null, _toDisplayString(card.last_run || '未执行'), 1)
                    ]),
                    _createElementVNode("div", _hoisted_34, [
                      _hoisted_35,
                      _createElementVNode("strong", null, _toDisplayString(scheduleText(card)), 1)
                    ])
                  ]),
                  _createElementVNode("div", _hoisted_36, [
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
            ], 2),
            _createElementVNode("aside", _hoisted_37, [
              _createElementVNode("div", _hoisted_38, [
                _hoisted_39,
                _createElementVNode("span", _hoisted_40, _toDisplayString((section.history || []).length) + " 条", 1)
              ]),
              (!(section.history || []).length)
                ? (_openBlock(), _createElementBlock("div", _hoisted_41, "当前模块还没有执行记录。"))
                : (_openBlock(), _createElementBlock("div", _hoisted_42, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.history, (item) => {
                      return (_openBlock(), _createElementBlock("article", {
                        key: `${section.module_key}-${item.time}-${item.title}`,
                        class: "vp-history-item"
                      }, [
                        _createElementVNode("div", _hoisted_43, [
                          _createElementVNode("strong", null, _toDisplayString(historyTitle(section, item)), 1),
                          _createElementVNode("span", null, _toDisplayString(item.time), 1)
                        ]),
                        (historyMeta(section, item))
                          ? (_openBlock(), _createElementBlock("div", _hoisted_44, _toDisplayString(historyMeta(section, item)), 1))
                          : _createCommentVNode("", true),
                        (item.lines?.length)
                          ? (_openBlock(), _createElementBlock("div", _hoisted_45, _toDisplayString(item.lines.join(' / ')), 1))
                          : _createCommentVNode("", true)
                      ]))
                    }), 128))
                  ]))
            ])
          ], 2)
        ], 4))
      }), 128))
    ])
  ], 2))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-dd691a91"]]);

export { PageView as default };
