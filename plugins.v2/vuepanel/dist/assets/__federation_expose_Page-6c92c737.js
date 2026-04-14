import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc, B as BasePanelCard, a as BaseButton, b as BaseTag, E as EmptyState } from './EmptyState-c135b286.js';

const SummaryStatCard_vue_vue_type_style_index_0_scoped_8ed98e3c_lang = '';

const {toDisplayString:_toDisplayString$1,createElementVNode:_createElementVNode$1,openBlock:_openBlock$1,createElementBlock:_createElementBlock$1,createCommentVNode:_createCommentVNode$1,withCtx:_withCtx$1,createBlock:_createBlock$1,pushScopeId:_pushScopeId$1,popScopeId:_popScopeId$1} = await importShared('vue');
const _hoisted_1$1 = { class: "mp-stat-label" };
const _hoisted_2$1 = { class: "mp-stat-value" };
const _hoisted_3$1 = {
  key: 0,
  class: "mp-stat-hint"
};


const _sfc_main$1 = {
  __name: 'SummaryStatCard',
  props: {
  label: { type: String, default: '' },
  value: { type: [String, Number], default: '' },
  hint: { type: String, default: '' },
  tone: { type: String, default: 'default' },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$1(), _createBlock$1(BasePanelCard, {
    tone: __props.tone,
    compact: "",
    class: "mp-stat-card"
  }, {
    default: _withCtx$1(() => [
      _createElementVNode$1("div", _hoisted_1$1, _toDisplayString$1(__props.label), 1),
      _createElementVNode$1("div", _hoisted_2$1, _toDisplayString$1(__props.value), 1),
      (__props.hint)
        ? (_openBlock$1(), _createElementBlock$1("div", _hoisted_3$1, _toDisplayString$1(__props.hint), 1))
        : _createCommentVNode$1("", true)
    ]),
    _: 1
  }, 8, ["tone"]))
}
}

};
const SummaryStatCard = /*#__PURE__*/_export_sfc(_sfc_main$1, [['__scopeId',"data-v-8ed98e3c"]]);

const Page_vue_vue_type_style_index_0_scoped_e8074884_lang = '';

const {createTextVNode:_createTextVNode,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,resolveComponent:_resolveComponent,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeStyle:_normalizeStyle,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-e8074884"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "page-board" };
const _hoisted_2 = { class: "hero-actions" };
const _hoisted_3 = { class: "hero-chips" };
const _hoisted_4 = { class: "stats-grid" };
const _hoisted_5 = { class: "module-stack" };
const _hoisted_6 = { class: "module-head-actions" };
const _hoisted_7 = { class: "task-card-head" };
const _hoisted_8 = { class: "task-card-site" };
const _hoisted_9 = { class: "task-card-title" };
const _hoisted_10 = {
  key: 0,
  class: "task-card-url"
};
const _hoisted_11 = { class: "task-card-summary" };
const _hoisted_12 = {
  key: 1,
  class: "metric-grid"
};
const _hoisted_13 = { class: "metric-label" };
const _hoisted_14 = { class: "metric-value" };
const _hoisted_15 = { class: "tag-row" };
const _hoisted_16 = {
  key: 2,
  class: "task-detail"
};
const _hoisted_17 = { class: "task-meta" };
const _hoisted_18 = { class: "meta-block" };
const _hoisted_19 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "meta-label" }, "上次执行", -1));
const _hoisted_20 = { class: "meta-block" };
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "meta-label" }, "下次计划", -1));
const _hoisted_22 = { class: "task-actions" };
const _hoisted_23 = { class: "module-side" };
const _hoisted_24 = { class: "side-block" };
const _hoisted_25 = { class: "side-head" };
const _hoisted_26 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "side-title" }, "通知", -1));
const _hoisted_27 = {
  key: 0,
  class: "side-empty"
};
const _hoisted_28 = {
  key: 1,
  class: "side-list"
};
const _hoisted_29 = { class: "side-item-head" };
const _hoisted_30 = { class: "side-time" };
const _hoisted_31 = { class: "side-item-title" };
const _hoisted_32 = { class: "side-item-summary" };
const _hoisted_33 = { class: "side-block" };
const _hoisted_34 = { class: "side-head" };
const _hoisted_35 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "side-title" }, "最近记录", -1));
const _hoisted_36 = {
  key: 0,
  class: "side-empty"
};
const _hoisted_37 = {
  key: 1,
  class: "side-list"
};
const _hoisted_38 = { class: "side-item-head" };
const _hoisted_39 = { class: "side-item-title" };
const _hoisted_40 = { class: "side-time" };
const _hoisted_41 = {
  key: 0,
  class: "side-item-meta"
};
const _hoisted_42 = { class: "side-item-summary" };
const _hoisted_43 = {
  key: 1,
  class: "side-item-detail"
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

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
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

function statTone(label) {
  if (/成功/.test(label)) return 'success'
  if (/异常/.test(label)) return 'danger'
  if (/待处理|通知/.test(label)) return 'warning'
  return 'default'
}

function levelTone(level) {
  if (level === 'success') return 'success'
  if (level === 'error') return 'danger'
  if (level === 'warning') return 'warning'
  return 'info'
}

function levelText(level) {
  return ({ success: '成功', error: '异常', warning: '待处理', info: '信息' })[level] || '信息'
}

function tagColor(tag) {
  if (tag.includes('已启用')) return 'success'
  if (tag.includes('已停用') || tag.includes('仅手动')) return 'disabled'
  if (tag.includes('Cron 无效')) return 'danger'
  if (tag.includes('Cookie')) return 'primary'
  if (tag.includes('UID')) return 'info'
  return 'warning'
}

function moduleSubtitle(section) {
  if (section.latest_run) return `最近一次执行：${section.latest_run}`
  return section.singleton ? '固定任务单卡，适合快速查看当前状态和调度信息。' : '显式多站点模块，站点卡之间完全独立。'
}

function scheduleText(card) {
  if (!card?.auto_run) return '仅手动'
  if (!status.enabled) return '插件停用'
  return card?.next_run_time || 'Cron 无效'
}

function fallbackLogFromCard(section, card) {
  const time = card.last_run || card.last_checked || '';
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

function sectionLogs(section) {
  const logs = Array.isArray(section?.activity_logs) ? section.activity_logs.filter(Boolean) : [];
  if (logs.length) return logs
  return (section?.cards || []).map((card) => fallbackLogFromCard(section, card)).filter(Boolean)
}

function sectionNotifications(section) {
  const notices = Array.isArray(section?.notifications) ? section.notifications.filter(Boolean) : [];
  if (notices.length) return notices
  return sectionLogs(section).filter((item) => item.level === 'warning' || item.level === 'error').slice(0, 4)
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

function closePlugin() {
  emit('close');
}

onMounted(async () => {
  await loadStatus();
});

return (_ctx, _cache) => {
  const _component_v_alert = _resolveComponent("v-alert");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(BasePanelCard, {
      kicker: "Vue-面板",
      title: "运行监控看板",
      subtitle: dashboard.value.subtitle || `当前主题：${__props.themeLabel}。模块状态、调度和最近执行记录按模块拆开查看。`,
      tone: "primary",
      class: "board-hero"
    }, {
      actions: _withCtx(() => [
        _createElementVNode("div", _hoisted_2, [
          _createVNode(BaseButton, {
            loading: loading.value,
            onClick: runAll
          }, {
            default: _withCtx(() => [
              _createTextVNode("执行启用任务")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(BaseButton, {
            variant: "secondary",
            loading: loading.value,
            onClick: refreshStatus
          }, {
            default: _withCtx(() => [
              _createTextVNode("刷新状态")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(BaseButton, {
            variant: "ghost",
            onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'config')))
          }, {
            default: _withCtx(() => [
              _createTextVNode("配置")
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
          _createVNode(BaseTag, { tone: "info" }, {
            default: _withCtx(() => [
              _createTextVNode("计划执行 " + _toDisplayString(status.next_run_time || dashboard.value.next_run_time || '未启用'), 1)
            ]),
            _: 1
          }),
          _createVNode(BaseTag, { tone: "info" }, {
            default: _withCtx(() => [
              _createTextVNode("最近执行 " + _toDisplayString(status.last_run || '暂无'), 1)
            ]),
            _: 1
          }),
          _createVNode(BaseTag, { tone: "success" }, {
            default: _withCtx(() => [
              _createTextVNode("模块 " + _toDisplayString(moduleSections.value.length), 1)
            ]),
            _: 1
          }),
          _createVNode(BaseTag, { tone: "warning" }, {
            default: _withCtx(() => [
              _createTextVNode("日志 " + _toDisplayString(activityLogCount.value), 1)
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
    _createElementVNode("section", _hoisted_4, [
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(dashboard.value.overview || [], (item) => {
        return (_openBlock(), _createBlock(SummaryStatCard, {
          key: item.label,
          label: item.label,
          value: item.value,
          tone: statTone(item.label)
        }, null, 8, ["label", "value", "tone"]))
      }), 128))
    ]),
    _createElementVNode("section", _hoisted_5, [
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(moduleSections.value, (section) => {
        return (_openBlock(), _createBlock(BasePanelCard, {
          key: section.module_key,
          kicker: section.singleton ? '固定模块' : '多站点模块',
          title: `${section.module_icon} ${section.module_name}`,
          subtitle: moduleSubtitle(section),
          tone: section.tone,
          compact: ""
        }, {
          actions: _withCtx(() => [
            _createElementVNode("div", _hoisted_6, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.stats || [], (stat) => {
                return (_openBlock(), _createBlock(BaseTag, {
                  key: `${section.module_key}-${stat.label}`,
                  tone: "primary",
                  size: "sm"
                }, {
                  default: _withCtx(() => [
                    _createTextVNode(_toDisplayString(stat.label) + " " + _toDisplayString(stat.value), 1)
                  ]),
                  _: 2
                }, 1024))
              }), 128))
            ])
          ]),
          default: _withCtx(() => [
            _createElementVNode("div", {
              class: _normalizeClass(["module-layout", { single: section.singleton }])
            }, [
              _createElementVNode("div", {
                class: _normalizeClass(["task-grid", { single: section.singleton }])
              }, [
                (!(section.cards || []).length)
                  ? (_openBlock(), _createBlock(EmptyState, {
                      key: 0,
                      title: "暂无状态卡片",
                      description: "当前模块还没有可展示的状态信息。"
                    }))
                  : _createCommentVNode("", true),
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.cards || [], (card) => {
                  return (_openBlock(), _createElementBlock("article", {
                    key: card.card_id,
                    class: "task-card",
                    style: _normalizeStyle(toneStyle(card.tone || section.tone))
                  }, [
                    _createElementVNode("div", _hoisted_7, [
                      _createElementVNode("div", null, [
                        _createElementVNode("div", _hoisted_8, _toDisplayString(card.site_name), 1),
                        _createElementVNode("div", _hoisted_9, _toDisplayString(card.status_title), 1)
                      ]),
                      _createVNode(BaseTag, {
                        tone: levelTone(card.level),
                        size: "sm",
                        dot: ""
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(levelText(card.level)), 1)
                        ]),
                        _: 2
                      }, 1032, ["tone"])
                    ]),
                    (!section.singleton)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_10, _toDisplayString(card.site_url), 1))
                      : _createCommentVNode("", true),
                    _createElementVNode("div", _hoisted_11, _toDisplayString(card.status_text), 1),
                    (card.metrics?.length)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_12, [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.metrics, (metric) => {
                            return (_openBlock(), _createElementBlock("div", {
                              key: `${card.card_id}-${metric.label}`,
                              class: "metric-item"
                            }, [
                              _createElementVNode("div", _hoisted_13, _toDisplayString(metric.label), 1),
                              _createElementVNode("div", _hoisted_14, _toDisplayString(metric.value), 1)
                            ]))
                          }), 128))
                        ]))
                      : _createCommentVNode("", true),
                    _createElementVNode("div", _hoisted_15, [
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.tags || [], (tag) => {
                        return (_openBlock(), _createBlock(BaseTag, {
                          key: `${card.card_id}-${tag}`,
                          tone: tagColor(tag),
                          size: "sm"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(tag), 1)
                          ]),
                          _: 2
                        }, 1032, ["tone"]))
                      }), 128))
                    ]),
                    (card.detail_lines?.length)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_16, [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.detail_lines, (line) => {
                            return (_openBlock(), _createElementBlock("div", {
                              key: `${card.card_id}-${line}`,
                              class: "detail-line"
                            }, _toDisplayString(line), 1))
                          }), 128))
                        ]))
                      : _createCommentVNode("", true),
                    _createElementVNode("div", _hoisted_17, [
                      _createElementVNode("div", _hoisted_18, [
                        _hoisted_19,
                        _createElementVNode("strong", null, _toDisplayString(card.last_run || '未执行'), 1)
                      ]),
                      _createElementVNode("div", _hoisted_20, [
                        _hoisted_21,
                        _createElementVNode("strong", null, _toDisplayString(scheduleText(card)), 1)
                      ])
                    ]),
                    _createElementVNode("div", _hoisted_22, [
                      _createVNode(BaseButton, {
                        size: "sm",
                        loading: runningCardId.value === card.card_id,
                        onClick: $event => (runCard(card))
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode("执行")
                        ]),
                        _: 2
                      }, 1032, ["loading", "onClick"]),
                      _createVNode(BaseButton, {
                        variant: "secondary",
                        size: "sm",
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
                }), 128))
              ], 2),
              _createElementVNode("aside", _hoisted_23, [
                _createElementVNode("section", _hoisted_24, [
                  _createElementVNode("div", _hoisted_25, [
                    _hoisted_26,
                    _createVNode(BaseTag, {
                      tone: "violet",
                      size: "sm"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(sectionNotifications(section).length), 1)
                      ]),
                      _: 2
                    }, 1024)
                  ]),
                  (!sectionNotifications(section).length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_27, "当前模块暂无需要关注的通知。"))
                    : (_openBlock(), _createElementBlock("div", _hoisted_28, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(sectionNotifications(section).slice(0, 4), (item) => {
                          return (_openBlock(), _createElementBlock("article", {
                            key: `${section.module_key}-notice-${item.id}`,
                            class: "side-item notice"
                          }, [
                            _createElementVNode("div", _hoisted_29, [
                              _createVNode(BaseTag, {
                                tone: levelTone(item.level),
                                size: "sm",
                                dot: ""
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(levelText(item.level)), 1)
                                ]),
                                _: 2
                              }, 1032, ["tone"]),
                              _createElementVNode("span", _hoisted_30, _toDisplayString(item.time), 1)
                            ]),
                            _createElementVNode("div", _hoisted_31, _toDisplayString(item.title), 1),
                            _createElementVNode("div", _hoisted_32, _toDisplayString(item.summary), 1)
                          ]))
                        }), 128))
                      ]))
                ]),
                _createElementVNode("section", _hoisted_33, [
                  _createElementVNode("div", _hoisted_34, [
                    _hoisted_35,
                    _createVNode(BaseTag, {
                      tone: "primary",
                      size: "sm"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(sectionLogs(section).length), 1)
                      ]),
                      _: 2
                    }, 1024)
                  ]),
                  (!sectionLogs(section).length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_36, "执行或刷新后，最近记录会显示在这里。"))
                    : (_openBlock(), _createElementBlock("div", _hoisted_37, [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(sectionLogs(section).slice(0, 6), (item) => {
                          return (_openBlock(), _createElementBlock("article", {
                            key: `${section.module_key}-log-${item.id}`,
                            class: "side-item log"
                          }, [
                            _createElementVNode("div", _hoisted_38, [
                              _createElementVNode("div", _hoisted_39, _toDisplayString(item.title), 1),
                              _createElementVNode("span", _hoisted_40, _toDisplayString(item.time), 1)
                            ]),
                            (item.site_name)
                              ? (_openBlock(), _createElementBlock("div", _hoisted_41, _toDisplayString(item.site_name), 1))
                              : _createCommentVNode("", true),
                            _createElementVNode("div", _hoisted_42, _toDisplayString(item.summary), 1),
                            (item.lines?.length)
                              ? (_openBlock(), _createElementBlock("div", _hoisted_43, _toDisplayString(item.lines.join(' / ')), 1))
                              : _createCommentVNode("", true)
                          ]))
                        }), 128))
                      ]))
                ])
              ])
            ], 2)
          ]),
          _: 2
        }, 1032, ["kicker", "title", "subtitle", "tone"]))
      }), 128))
    ])
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-e8074884"]]);

export { PageView as default };
