import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_9461f0ff_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,normalizeStyle:_normalizeStyle,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-9461f0ff"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "vuepanel-page" };
const _hoisted_2 = { class: "vpp-shell" };
const _hoisted_3 = { class: "vpp-card vpp-hero" };
const _hoisted_4 = { class: "vpp-copy" };
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "vpp-badge" }, "Vue-面板", -1));
const _hoisted_6 = { class: "vpp-title" };
const _hoisted_7 = { class: "vpp-chip-row" };
const _hoisted_8 = { class: "vpp-chip" };
const _hoisted_9 = { class: "vpp-chip" };
const _hoisted_10 = { class: "vpp-chip" };
const _hoisted_11 = { class: "vpp-chip" };
const _hoisted_12 = { class: "vpp-chip" };
const _hoisted_13 = { class: "vpp-action-grid" };
const _hoisted_14 = { class: "vpp-stat-grid" };
const _hoisted_15 = { class: "vpp-stat-label" };
const _hoisted_16 = { class: "vpp-stat-value" };
const _hoisted_17 = { class: "vpp-module-head" };
const _hoisted_18 = { class: "vpp-kicker" };
const _hoisted_19 = { class: "vpp-section-title" };
const _hoisted_20 = { class: "vpp-pill-row" };
const _hoisted_21 = {
  key: 0,
  class: "vpp-pill"
};
const _hoisted_22 = { class: "vpp-panel-top" };
const _hoisted_23 = { class: "vpp-panel-kicker" };
const _hoisted_24 = { class: "vpp-panel-title" };
const _hoisted_25 = {
  key: 0,
  class: "vpp-panel-site"
};
const _hoisted_26 = { class: "vpp-panel-text" };
const _hoisted_27 = {
  key: 1,
  class: "vpp-metric-grid"
};
const _hoisted_28 = { class: "vpp-metric-label" };
const _hoisted_29 = { class: "vpp-metric-value" };
const _hoisted_30 = {
  key: 2,
  class: "vpp-tag-row"
};
const _hoisted_31 = {
  key: 3,
  class: "vpp-detail-list"
};
const _hoisted_32 = { class: "vpp-meta-grid" };
const _hoisted_33 = { class: "vpp-meta-item" };
const _hoisted_34 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-meta-label" }, "执行", -1));
const _hoisted_35 = { class: "vpp-meta-item" };
const _hoisted_36 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "vpp-meta-label" }, "计划", -1));
const _hoisted_37 = { class: "vpp-btn-row" };
const _hoisted_38 = {
  key: 0,
  class: "vpp-empty"
};
const _hoisted_39 = { class: "vpp-side-stack" };
const _hoisted_40 = {
  key: 0,
  class: "vpp-side-card"
};
const _hoisted_41 = { class: "vpp-side-head" };
const _hoisted_42 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "vpp-kicker" }, "模块通知"),
  /*#__PURE__*/_createElementVNode("div", { class: "vpp-side-title" }, "需要关注的变化")
], -1));
const _hoisted_43 = { class: "vpp-side-count" };
const _hoisted_44 = { class: "vpp-side-list" };
const _hoisted_45 = { class: "vpp-side-top" };
const _hoisted_46 = { class: "vpp-side-time" };
const _hoisted_47 = { class: "vpp-side-summary" };
const _hoisted_48 = { class: "vpp-side-card" };
const _hoisted_49 = { class: "vpp-side-head" };
const _hoisted_50 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "vpp-kicker" }, "执行记录"),
  /*#__PURE__*/_createElementVNode("div", { class: "vpp-side-title" }, "最近日志")
], -1));
const _hoisted_51 = { class: "vpp-side-count" };
const _hoisted_52 = {
  key: 0,
  class: "vpp-empty"
};
const _hoisted_53 = {
  key: 1,
  class: "vpp-side-list"
};
const _hoisted_54 = { class: "vpp-side-top" };
const _hoisted_55 = { class: "vpp-side-time" };
const _hoisted_56 = {
  key: 0,
  class: "vpp-side-meta"
};
const _hoisted_57 = { class: "vpp-side-summary" };
const _hoisted_58 = {
  key: 1,
  class: "vpp-side-lines"
};

const {computed,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;





const loading = ref(false);
const runningCardId = ref('');
const refreshingCardId = ref('');
const status = reactive({ dashboard: {}, history: [] });
const message = reactive({ text: '', type: 'success' });

const dashboard = computed(() => status.dashboard || {});
const moduleSections = computed(() => dashboard.value.module_sections || []);
const activityLogCount = computed(() => moduleSections.value.reduce((total, section) => total + sectionLogs(section).length, 0));
const summaryCards = computed(() => {
  const overview = dashboard.value.overview || [];
  const map = new Map(overview.map((item) => [item.label, item]));
  const preferred = ['配置卡片', '状态卡片', '自动执行', '成功状态', '异常状态'];
  const picked = preferred.map((label) => map.get(label)).filter(Boolean);
  return picked.length ? picked : overview.slice(0, 5)
});

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function toneStyle(tone) {
  const map = {
    emerald: { '--vpp-tone-rgb': '40,181,120' },
    azure: { '--vpp-tone-rgb': '46,134,255' },
    amber: { '--vpp-tone-rgb': '255,170,63' },
    rose: { '--vpp-tone-rgb': '230,92,124' },
    violet: { '--vpp-tone-rgb': '132,108,255' },
    slate: { '--vpp-tone-rgb': '120,132,155' },
  };
  return map[tone] || map.azure
}

function cardLevel(level) {
  if (level === 'success') return 'success'
  if (level === 'warning') return 'warning'
  if (level === 'error') return 'danger'
  return 'info'
}

function levelLabel(level) {
  return ({ success: '正常', warning: '待处理', error: '异常', info: '信息' })[level] || '信息'
}

function tagTone(tag) {
  if (tag.includes('已启用')) return 'success'
  if (tag.includes('已停用')) return 'disabled'
  if (tag.includes('Cron 无效')) return 'danger'
  if (tag.includes('Cookie')) return 'primary'
  if (tag.includes('UID')) return 'info'
  return 'warning'
}

function scheduleText(card) {
  if (!card?.auto_run) return '仅手动'
  if (!status.enabled) return '插件停用'
  return card?.next_run_time || 'Cron 无效'
}

function fallbackLogFromCard(section, card) {
  const time = String(card?.last_run || card?.last_checked || '').trim();
  if (!time) return null
  return {
    id: `fallback-${card.card_id}-${time}`,
    title: card.status_title || card.site_name || section.module_name,
    summary: card.status_text || '',
    level: card.level || 'info',
    time,
    lines: card.detail_lines || [],
    site_name: card.site_name || '',
    site_url: card.site_url || '',
  }
}

function historySummary(item) {
  return item.summary || (item.lines || []).join(' / ') || '暂无详情'
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

function sectionLogs(section) {
  const activityLogs = Array.isArray(section?.activity_logs) ? section.activity_logs.filter(Boolean) : [];
  if (activityLogs.length) {
    return activityLogs.slice().sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
  }

  const historyLogs = Array.isArray(section?.history)
    ? section.history
        .filter(Boolean)
        .map((item) => ({
          id: item.id || `${section.module_key}-${item.time || item.title}`,
          title: item.title || item.status_title || section.module_name,
          summary: item.summary || '',
          level: item.level || 'info',
          time: item.time || '',
          lines: item.lines || [],
          site_name: item.site_name || '',
          site_url: item.site_url || '',
        }))
        .filter((item) => item.time)
    : [];
  if (historyLogs.length) {
    return historyLogs.slice().sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
  }

  return (section?.cards || [])
    .map((card) => fallbackLogFromCard(section, card))
    .filter(Boolean)
    .sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
}

function sectionNotifications(section) {
  const notices = Array.isArray(section?.notifications) ? section.notifications.filter(Boolean) : [];
  if (notices.length) {
    return notices.slice().sort((a, b) => String(b.time || '').localeCompare(String(a.time || '')))
  }
  return sectionLogs(section).filter((item) => item.level === 'warning' || item.level === 'error').slice(0, 4)
}

async function loadStatus(showError = true) {
  try {
    Object.assign(status, (await props.api.get('/plugin/VuePanel/status')) || {});
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

function closePlugin() {
  emit('close');
}

onMounted(async () => {
  await loadStatus();
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("header", _hoisted_3, [
        _createElementVNode("div", _hoisted_4, [
          _hoisted_5,
          _createElementVNode("h1", _hoisted_6, _toDisplayString(dashboard.value.title || '状态页'), 1),
          _createElementVNode("div", _hoisted_7, [
            _createElementVNode("span", _hoisted_8, "主题 " + _toDisplayString(__props.themeLabel), 1),
            _createElementVNode("span", _hoisted_9, "计划执行 " + _toDisplayString(status.next_run_time || dashboard.value.next_run_time || '未启用'), 1),
            _createElementVNode("span", _hoisted_10, "最近执行 " + _toDisplayString(status.last_run || '暂无'), 1),
            _createElementVNode("span", _hoisted_11, "模块 " + _toDisplayString(moduleSections.value.length) + " 个", 1),
            _createElementVNode("span", _hoisted_12, "日志 " + _toDisplayString(activityLogCount.value), 1)
          ])
        ]),
        _createElementVNode("div", _hoisted_13, [
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
      _createElementVNode("section", _hoisted_14, [
        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(summaryCards.value, (item) => {
          return (_openBlock(), _createElementBlock("article", {
            key: item.label,
            class: "vpp-card vpp-stat"
          }, [
            _createElementVNode("div", _hoisted_15, _toDisplayString(item.label), 1),
            _createElementVNode("div", _hoisted_16, _toDisplayString(item.value), 1)
          ]))
        }), 128))
      ]),
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(moduleSections.value, (section) => {
        return (_openBlock(), _createElementBlock("section", {
          key: section.module_key,
          class: "vpp-card vpp-module",
          style: _normalizeStyle(toneStyle(section.tone))
        }, [
          _createElementVNode("div", _hoisted_17, [
            _createElementVNode("div", null, [
              _createElementVNode("div", _hoisted_18, _toDisplayString(section.singleton ? '固定模块' : '多站点模块'), 1),
              _createElementVNode("h2", _hoisted_19, _toDisplayString(section.module_icon) + " " + _toDisplayString(section.module_name), 1)
            ]),
            _createElementVNode("div", _hoisted_20, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.stats || [], (stat) => {
                return (_openBlock(), _createElementBlock("span", {
                  key: `${section.module_key}-${stat.label}`,
                  class: "vpp-pill"
                }, _toDisplayString(stat.label) + " " + _toDisplayString(stat.value), 1))
              }), 128)),
              (section.latest_run)
                ? (_openBlock(), _createElementBlock("span", _hoisted_21, "最近 " + _toDisplayString(section.latest_run), 1))
                : _createCommentVNode("", true)
            ])
          ]),
          _createElementVNode("div", {
            class: _normalizeClass(["vpp-module-body", { single: section.singleton }])
          }, [
            _createElementVNode("div", {
              class: _normalizeClass(["vpp-card-grid", { single: section.singleton, multi: !section.singleton }])
            }, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.cards || [], (card) => {
                return (_openBlock(), _createElementBlock("article", {
                  key: card.card_id,
                  class: "vpp-panel",
                  style: _normalizeStyle(toneStyle(card.tone || section.tone))
                }, [
                  _createElementVNode("div", _hoisted_22, [
                    _createElementVNode("div", null, [
                      _createElementVNode("div", _hoisted_23, _toDisplayString(card.site_name), 1),
                      _createElementVNode("div", _hoisted_24, _toDisplayString(card.status_title), 1)
                    ]),
                    _createElementVNode("span", {
                      class: _normalizeClass(["vpp-level", `is-${cardLevel(card.level)}`])
                    }, _toDisplayString(levelLabel(card.level)), 3)
                  ]),
                  (!section.singleton)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_25, _toDisplayString(card.site_url), 1))
                    : _createCommentVNode("", true),
                  _createElementVNode("div", _hoisted_26, _toDisplayString(card.status_text), 1),
                  (card.metrics?.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_27, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.metrics, (metric) => {
                          return (_openBlock(), _createElementBlock("div", {
                            key: `${card.card_id}-${metric.label}`,
                            class: "vpp-metric"
                          }, [
                            _createElementVNode("div", _hoisted_28, _toDisplayString(metric.label), 1),
                            _createElementVNode("div", _hoisted_29, _toDisplayString(metric.value), 1)
                          ]))
                        }), 128))
                      ]))
                    : _createCommentVNode("", true),
                  (card.tags?.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_30, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.tags, (tag) => {
                          return (_openBlock(), _createElementBlock("span", {
                            key: `${card.card_id}-${tag}`,
                            class: _normalizeClass(["vpp-tag", `is-${tagTone(tag)}`])
                          }, _toDisplayString(tag), 3))
                        }), 128))
                      ]))
                    : _createCommentVNode("", true),
                  (card.detail_lines?.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_31, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.detail_lines, (line) => {
                          return (_openBlock(), _createElementBlock("div", {
                            key: `${card.card_id}-${line}`,
                            class: "vpp-detail-item"
                          }, _toDisplayString(line), 1))
                        }), 128))
                      ]))
                    : _createCommentVNode("", true),
                  _createElementVNode("div", _hoisted_32, [
                    _createElementVNode("div", _hoisted_33, [
                      _hoisted_34,
                      _createElementVNode("strong", null, _toDisplayString(card.last_run || '未执行'), 1)
                    ]),
                    _createElementVNode("div", _hoisted_35, [
                      _hoisted_36,
                      _createElementVNode("strong", null, _toDisplayString(scheduleText(card)), 1)
                    ])
                  ]),
                  _createElementVNode("div", _hoisted_37, [
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
                ], 4))
              }), 128)),
              (!(section.cards || []).length)
                ? (_openBlock(), _createElementBlock("div", _hoisted_38, " 当前模块还没有可显示的状态卡片。 "))
                : _createCommentVNode("", true)
            ], 2),
            _createElementVNode("aside", _hoisted_39, [
              (sectionNotifications(section).length)
                ? (_openBlock(), _createElementBlock("section", _hoisted_40, [
                    _createElementVNode("div", _hoisted_41, [
                      _hoisted_42,
                      _createElementVNode("span", _hoisted_43, _toDisplayString(sectionNotifications(section).length), 1)
                    ]),
                    _createElementVNode("div", _hoisted_44, [
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(sectionNotifications(section).slice(0, 3), (item) => {
                        return (_openBlock(), _createElementBlock("article", {
                          key: `${section.module_key}-notice-${item.id}`,
                          class: "vpp-side-item notice"
                        }, [
                          _createElementVNode("div", _hoisted_45, [
                            _createElementVNode("strong", null, _toDisplayString(item.title), 1),
                            _createElementVNode("span", _hoisted_46, _toDisplayString(item.time), 1)
                          ]),
                          _createElementVNode("div", _hoisted_47, _toDisplayString(item.summary), 1)
                        ]))
                      }), 128))
                    ])
                  ]))
                : _createCommentVNode("", true),
              _createElementVNode("section", _hoisted_48, [
                _createElementVNode("div", _hoisted_49, [
                  _hoisted_50,
                  _createElementVNode("span", _hoisted_51, _toDisplayString(sectionLogs(section).length), 1)
                ]),
                (!sectionLogs(section).length)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_52, " 当前模块还没有执行记录。 "))
                  : (_openBlock(), _createElementBlock("div", _hoisted_53, [
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(sectionLogs(section).slice(0, 6), (item) => {
                        return (_openBlock(), _createElementBlock("article", {
                          key: `${section.module_key}-log-${item.id}`,
                          class: "vpp-side-item log"
                        }, [
                          _createElementVNode("div", _hoisted_54, [
                            _createElementVNode("strong", null, _toDisplayString(historyTitle(section, item)), 1),
                            _createElementVNode("span", _hoisted_55, _toDisplayString(item.time), 1)
                          ]),
                          (historyMeta(section, item))
                            ? (_openBlock(), _createElementBlock("div", _hoisted_56, _toDisplayString(historyMeta(section, item)), 1))
                            : _createCommentVNode("", true),
                          _createElementVNode("div", _hoisted_57, _toDisplayString(historySummary(item)), 1),
                          (item.lines?.length)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_58, _toDisplayString(item.lines.join(' / ')), 1))
                            : _createCommentVNode("", true)
                        ]))
                      }), 128))
                    ]))
              ])
            ])
          ], 2)
        ], 4))
      }), 128))
    ])
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-9461f0ff"]]);

export { PageView as default };
