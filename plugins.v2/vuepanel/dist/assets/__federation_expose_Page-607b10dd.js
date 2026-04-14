import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc, B as BasePanelCard, a as BaseInput, E as EmptyState, b as BaseTag, c as BaseButton } from './EmptyState-040be838.js';

const ActivityLogList_vue_vue_type_style_index_0_scoped_04f93ed4_lang = '';

const {createVNode:_createVNode$2,resolveComponent:_resolveComponent$2,createElementVNode:_createElementVNode$3,openBlock:_openBlock$3,createBlock:_createBlock$3,createCommentVNode:_createCommentVNode$3,toDisplayString:_toDisplayString$3,createTextVNode:_createTextVNode$2,withCtx:_withCtx$3,createElementBlock:_createElementBlock$3,renderList:_renderList$2,Fragment:_Fragment$2,pushScopeId:_pushScopeId$3,popScopeId:_popScopeId$3} = await importShared('vue');
const _hoisted_1$3 = { class: "log-toolbar" };
const _hoisted_2$3 = { class: "log-item" };
const _hoisted_3$3 = { class: "log-top" };
const _hoisted_4$2 = { class: "log-title-wrap" };
const _hoisted_5$2 = { class: "log-title" };
const _hoisted_6$2 = { class: "log-time" };
const _hoisted_7$2 = { class: "log-meta" };
const _hoisted_8$2 = { key: 0 };
const _hoisted_9$2 = { key: 1 };
const _hoisted_10$2 = { class: "log-summary" };
const _hoisted_11$1 = { class: "log-actions" };
const _hoisted_12$1 = {
  key: 0,
  class: "log-detail"
};

const {computed: computed$2,reactive: reactive$2,ref: ref$2} = await importShared('vue');


const _sfc_main$3 = {
  __name: 'ActivityLogList',
  props: {
  items: { type: Array, default: () => [] },
},
  setup(__props) {

const props = __props;



const keyword = ref$2('');
const moduleFilter = ref$2('全部模块');
const statusFilter = ref$2('全部状态');
const expanded = reactive$2({});

const moduleOptions = computed$2(() => {
  const labels = Array.from(new Set(props.items.map((item) => item.module_name).filter(Boolean)));
  return ['全部模块', ...labels]
});

const statusOptions = ['全部状态', '成功', '异常', '警告', '信息'];

const filteredItems = computed$2(() => {
  const query = keyword.value.trim().toLowerCase();
  return props.items.filter((item) => {
    if (moduleFilter.value !== '全部模块' && item.module_name !== moduleFilter.value) return false
    if (statusFilter.value !== '全部状态' && levelText(item.level) !== statusFilter.value) return false
    if (!query) return true
    const text = [
      item.title,
      item.summary,
      item.module_name,
      item.site_name,
      item.site_url,
      ...(item.lines || []),
    ].join(' ').toLowerCase();
    return text.includes(query)
  })
});

function tagTone(level) {
  if (level === 'success') return 'success'
  if (level === 'error') return 'error'
  if (level === 'warning') return 'warning'
  return 'info'
}

function levelText(level) {
  return ({ success: '成功', error: '异常', warning: '警告', info: '信息' })[level] || '信息'
}

function toggle(id) {
  expanded[id] = !expanded[id];
}

async function copyText(text) {
  if (!text) return
  await navigator.clipboard?.writeText?.(text);
}

function copyOne(item) {
  return copyText(
    [
      `${item.module_icon || ''} ${item.module_name || ''} ${item.title || ''}`.trim(),
      item.summary || '',
      ...(item.lines || []),
    ].filter(Boolean).join('\n')
  )
}

return (_ctx, _cache) => {
  const _component_v_select = _resolveComponent$2("v-select");
  const _component_VVirtualScroll = _resolveComponent$2("VVirtualScroll");

  return (_openBlock$3(), _createBlock$3(BasePanelCard, {
    kicker: "执行记录",
    title: "结构化日志",
    subtitle: "支持按模块、状态和关键字筛选，适合快速定位失败、跳过和待处理任务。",
    tone: "primary",
    class: "log-board"
  }, {
    actions: _withCtx$3(() => [
      _createElementVNode$3("div", _hoisted_1$3, [
        _createVNode$2(BaseInput, {
          modelValue: keyword.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((keyword).value = $event)),
          label: "搜索日志",
          placeholder: "搜索任务 / 站点 / 结果",
          clearable: ""
        }, null, 8, ["modelValue"]),
        _createVNode$2(_component_v_select, {
          modelValue: moduleFilter.value,
          "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((moduleFilter).value = $event)),
          class: "log-select",
          items: moduleOptions.value,
          label: "模块",
          variant: "outlined",
          density: "comfortable",
          "hide-details": ""
        }, null, 8, ["modelValue", "items"]),
        _createVNode$2(_component_v_select, {
          modelValue: statusFilter.value,
          "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((statusFilter).value = $event)),
          class: "log-select",
          items: statusOptions,
          label: "状态",
          variant: "outlined",
          density: "comfortable",
          "hide-details": ""
        }, null, 8, ["modelValue"])
      ])
    ]),
    default: _withCtx$3(() => [
      (!filteredItems.value.length)
        ? (_openBlock$3(), _createBlock$3(EmptyState, {
            key: 0,
            title: "暂无执行记录",
            description: "执行完成后会按时间排序展示在这里。"
          }))
        : (_openBlock$3(), _createBlock$3(_component_VVirtualScroll, {
            key: 1,
            class: "log-scroll mp-scroll",
            items: filteredItems.value,
            height: 420,
            "item-height": "118"
          }, {
            default: _withCtx$3(({ item }) => [
              _createElementVNode$3("article", _hoisted_2$3, [
                _createElementVNode$3("div", _hoisted_3$3, [
                  _createElementVNode$3("div", _hoisted_4$2, [
                    _createVNode$2(BaseTag, {
                      tone: tagTone(item.level),
                      size: "sm",
                      dot: ""
                    }, {
                      default: _withCtx$3(() => [
                        _createTextVNode$2(_toDisplayString$3(levelText(item.level)), 1)
                      ]),
                      _: 2
                    }, 1032, ["tone"]),
                    _createElementVNode$3("strong", _hoisted_5$2, _toDisplayString$3(item.title), 1)
                  ]),
                  _createElementVNode$3("span", _hoisted_6$2, _toDisplayString$3(item.time), 1)
                ]),
                _createElementVNode$3("div", _hoisted_7$2, [
                  _createElementVNode$3("span", null, _toDisplayString$3(item.module_icon) + " " + _toDisplayString$3(item.module_name), 1),
                  (item.site_name)
                    ? (_openBlock$3(), _createElementBlock$3("span", _hoisted_8$2, _toDisplayString$3(item.site_name), 1))
                    : _createCommentVNode$3("", true),
                  (item.site_url)
                    ? (_openBlock$3(), _createElementBlock$3("span", _hoisted_9$2, _toDisplayString$3(item.site_url), 1))
                    : _createCommentVNode$3("", true)
                ]),
                _createElementVNode$3("div", _hoisted_10$2, _toDisplayString$3(item.summary), 1),
                _createElementVNode$3("div", _hoisted_11$1, [
                  _createVNode$2(BaseButton, {
                    variant: "ghost",
                    size: "sm",
                    onClick: $event => (toggle(item.id))
                  }, {
                    default: _withCtx$3(() => [
                      _createTextVNode$2(_toDisplayString$3(expanded[item.id] ? '收起' : '详情'), 1)
                    ]),
                    _: 2
                  }, 1032, ["onClick"]),
                  _createVNode$2(BaseButton, {
                    variant: "ghost",
                    size: "sm",
                    onClick: $event => (copyOne(item))
                  }, {
                    default: _withCtx$3(() => [
                      _createTextVNode$2("复制")
                    ]),
                    _: 2
                  }, 1032, ["onClick"])
                ]),
                (expanded[item.id])
                  ? (_openBlock$3(), _createElementBlock$3("div", _hoisted_12$1, [
                      (_openBlock$3(true), _createElementBlock$3(_Fragment$2, null, _renderList$2(item.lines || [], (line) => {
                        return (_openBlock$3(), _createElementBlock$3("div", {
                          key: `${item.id}-${line}`,
                          class: "log-line"
                        }, _toDisplayString$3(line), 1))
                      }), 128))
                    ]))
                  : _createCommentVNode$3("", true)
              ])
            ]),
            _: 1
          }, 8, ["items"]))
    ]),
    _: 1
  }))
}
}

};
const ActivityLogList = /*#__PURE__*/_export_sfc(_sfc_main$3, [['__scopeId',"data-v-04f93ed4"]]);

const NotificationList_vue_vue_type_style_index_0_scoped_6c784360_lang = '';

const {createVNode:_createVNode$1,createTextVNode:_createTextVNode$1,withCtx:_withCtx$2,createElementVNode:_createElementVNode$2,openBlock:_openBlock$2,createBlock:_createBlock$2,createCommentVNode:_createCommentVNode$2,toDisplayString:_toDisplayString$2,renderList:_renderList$1,Fragment:_Fragment$1,createElementBlock:_createElementBlock$2,resolveComponent:_resolveComponent$1,pushScopeId:_pushScopeId$2,popScopeId:_popScopeId$2} = await importShared('vue');
const _hoisted_1$2 = { class: "notify-toolbar" };
const _hoisted_2$2 = { class: "notify-item" };
const _hoisted_3$2 = { class: "notify-item-top" };
const _hoisted_4$1 = { class: "notify-title-wrap" };
const _hoisted_5$1 = { class: "notify-title" };
const _hoisted_6$1 = { class: "notify-time" };
const _hoisted_7$1 = { class: "notify-summary" };
const _hoisted_8$1 = {
  key: 0,
  class: "notify-parts"
};
const _hoisted_9$1 = { class: "notify-actions" };
const _hoisted_10$1 = {
  key: 1,
  class: "notify-detail"
};

const {computed: computed$1,reactive: reactive$1,ref: ref$1} = await importShared('vue');


const _sfc_main$2 = {
  __name: 'NotificationList',
  props: {
  items: { type: Array, default: () => [] },
},
  setup(__props) {

const props = __props;



const keyword = ref$1('');
const expanded = reactive$1({});

const filteredItems = computed$1(() => {
  const query = keyword.value.trim().toLowerCase();
  if (!query) return props.items
  return props.items.filter((item) => {
    const text = [
      item.title,
      item.summary,
      item.module_name,
      item.site_name,
      ...(item.detail_lines || []),
      ...((item.parts || []).map((part) => `${part.label} ${part.value}`)),
    ].join(' ').toLowerCase();
    return text.includes(query)
  })
});

function tagTone(level) {
  if (level === 'success') return 'success'
  if (level === 'error') return 'error'
  if (level === 'warning') return 'warning'
  return 'info'
}

function levelText(level) {
  return ({ success: '成功', error: '异常', warning: '警告', info: '信息' })[level] || '信息'
}

function toggle(id) {
  expanded[id] = !expanded[id];
}

async function copyText(text) {
  if (!text) return
  await navigator.clipboard?.writeText?.(text);
}

function formatItem(item) {
  return [
    `${item.module_icon || ''} ${item.module_name || ''} ${item.title || ''}`.trim(),
    item.summary || '',
    ...(item.detail_lines || []),
  ].filter(Boolean).join('\n')
}

function copyOne(item) {
  return copyText(formatItem(item))
}

function copyAll() {
  return copyText(filteredItems.value.map(formatItem).join('\n\n'))
}

return (_ctx, _cache) => {
  const _component_VVirtualScroll = _resolveComponent$1("VVirtualScroll");

  return (_openBlock$2(), _createBlock$2(BasePanelCard, {
    kicker: "通知区",
    title: "最新通知",
    subtitle: "聚合最近的执行结果，优先展示需要关注的变化和异常。",
    tone: "violet",
    class: "notify-board"
  }, {
    actions: _withCtx$2(() => [
      _createElementVNode$2("div", _hoisted_1$2, [
        _createVNode$1(BaseInput, {
          modelValue: keyword.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((keyword).value = $event)),
          label: "搜索通知",
          placeholder: "搜索模块 / 站点 / 结果",
          clearable: ""
        }, null, 8, ["modelValue"]),
        _createVNode$1(BaseButton, {
          variant: "ghost",
          size: "sm",
          onClick: copyAll
        }, {
          default: _withCtx$2(() => [
            _createTextVNode$1("复制摘要")
          ]),
          _: 1
        })
      ])
    ]),
    default: _withCtx$2(() => [
      (!filteredItems.value.length)
        ? (_openBlock$2(), _createBlock$2(EmptyState, {
            key: 0,
            title: "暂无通知",
            description: "新的执行结果会以卡片列表的形式显示在这里。"
          }))
        : (_openBlock$2(), _createBlock$2(_component_VVirtualScroll, {
            key: 1,
            class: "notify-scroll mp-scroll",
            items: filteredItems.value,
            height: 360,
            "item-height": "120"
          }, {
            default: _withCtx$2(({ item }) => [
              _createElementVNode$2("article", _hoisted_2$2, [
                _createElementVNode$2("div", _hoisted_3$2, [
                  _createElementVNode$2("div", _hoisted_4$1, [
                    _createVNode$1(BaseTag, {
                      tone: tagTone(item.level),
                      size: "sm",
                      dot: ""
                    }, {
                      default: _withCtx$2(() => [
                        _createTextVNode$1(_toDisplayString$2(levelText(item.level)), 1)
                      ]),
                      _: 2
                    }, 1032, ["tone"]),
                    _createElementVNode$2("strong", _hoisted_5$1, _toDisplayString$2(item.title), 1)
                  ]),
                  _createElementVNode$2("span", _hoisted_6$1, _toDisplayString$2(item.time), 1)
                ]),
                _createElementVNode$2("div", _hoisted_7$1, _toDisplayString$2(item.summary), 1),
                (item.parts?.length)
                  ? (_openBlock$2(), _createElementBlock$2("div", _hoisted_8$1, [
                      (_openBlock$2(true), _createElementBlock$2(_Fragment$1, null, _renderList$1(item.parts, (part) => {
                        return (_openBlock$2(), _createElementBlock$2("span", {
                          key: `${item.id}-${part.label}`,
                          class: "notify-part"
                        }, _toDisplayString$2(part.label) + "：" + _toDisplayString$2(part.value), 1))
                      }), 128))
                    ]))
                  : _createCommentVNode$2("", true),
                _createElementVNode$2("div", _hoisted_9$1, [
                  _createVNode$1(BaseTag, {
                    tone: "primary",
                    size: "sm"
                  }, {
                    default: _withCtx$2(() => [
                      _createTextVNode$1(_toDisplayString$2(item.module_icon) + " " + _toDisplayString$2(item.module_name), 1)
                    ]),
                    _: 2
                  }, 1024),
                  _createVNode$1(BaseButton, {
                    variant: "ghost",
                    size: "sm",
                    onClick: $event => (toggle(item.id))
                  }, {
                    default: _withCtx$2(() => [
                      _createTextVNode$1(_toDisplayString$2(expanded[item.id] ? '收起' : '详情'), 1)
                    ]),
                    _: 2
                  }, 1032, ["onClick"]),
                  _createVNode$1(BaseButton, {
                    variant: "ghost",
                    size: "sm",
                    onClick: $event => (copyOne(item))
                  }, {
                    default: _withCtx$2(() => [
                      _createTextVNode$1("复制")
                    ]),
                    _: 2
                  }, 1032, ["onClick"])
                ]),
                (expanded[item.id])
                  ? (_openBlock$2(), _createElementBlock$2("div", _hoisted_10$1, [
                      (_openBlock$2(true), _createElementBlock$2(_Fragment$1, null, _renderList$1(item.detail_lines || [], (line) => {
                        return (_openBlock$2(), _createElementBlock$2("div", {
                          key: `${item.id}-${line}`,
                          class: "notify-line"
                        }, _toDisplayString$2(line), 1))
                      }), 128))
                    ]))
                  : _createCommentVNode$2("", true)
              ])
            ]),
            _: 1
          }, 8, ["items"]))
    ]),
    _: 1
  }))
}
}

};
const NotificationList = /*#__PURE__*/_export_sfc(_sfc_main$2, [['__scopeId',"data-v-6c784360"]]);

const SummaryStatCard_vue_vue_type_style_index_0_scoped_e4332c3a_lang = '';

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
const SummaryStatCard = /*#__PURE__*/_export_sfc(_sfc_main$1, [['__scopeId',"data-v-e4332c3a"]]);

const Page_vue_vue_type_style_index_0_scoped_ef8b5d5b_lang = '';

const {createTextVNode:_createTextVNode,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,resolveComponent:_resolveComponent,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-ef8b5d5b"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "page-board" };
const _hoisted_2 = { class: "hero-actions" };
const _hoisted_3 = { class: "hero-chips" };
const _hoisted_4 = { class: "stats-grid" };
const _hoisted_5 = { class: "module-grid" };
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
const _hoisted_16 = { class: "task-meta" };
const _hoisted_17 = { class: "meta-block" };
const _hoisted_18 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "meta-label" }, "上次执行", -1));
const _hoisted_19 = { class: "meta-block" };
const _hoisted_20 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "meta-label" }, "下次计划", -1));
const _hoisted_21 = {
  key: 2,
  class: "task-detail"
};
const _hoisted_22 = { class: "task-actions" };
const _hoisted_23 = { class: "feed-grid" };

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
const notifications = computed(() => dashboard.value.notifications || []);
const activityLogs = computed(() => dashboard.value.activity_logs || []);

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
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
  return section.singleton ? '固定任务卡片，适合快速查看执行和调度状态。' : '多站点模块，适合批量管理同类站点卡片。'
}

function scheduleText(card) {
  if (!card?.auto_run) return '仅手动'
  if (!status.enabled) return '插件停用'
  return card?.next_run_time || 'Cron 无效'
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
      subtitle: dashboard.value.subtitle || `当前主题：${__props.themeLabel}。模块状态、通知和执行记录都在同一套看板里集中查看。`,
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
              _createTextVNode("通知 " + _toDisplayString(notifications.value.length), 1)
            ]),
            _: 1
          }),
          _createVNode(BaseTag, { tone: "warning" }, {
            default: _withCtx(() => [
              _createTextVNode("日志 " + _toDisplayString(activityLogs.value.length), 1)
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
          tone: section.tone
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
            (!(section.cards || []).length)
              ? (_openBlock(), _createBlock(EmptyState, {
                  key: 0,
                  title: "暂无状态卡片",
                  description: "当前模块还没有可展示的状态信息。"
                }))
              : (_openBlock(), _createElementBlock("div", {
                  key: 1,
                  class: _normalizeClass(["task-grid", { single: section.singleton }])
                }, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.cards, (card) => {
                    return (_openBlock(), _createElementBlock("article", {
                      key: card.card_id,
                      class: "task-card"
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
                      _createElementVNode("div", _hoisted_16, [
                        _createElementVNode("div", _hoisted_17, [
                          _hoisted_18,
                          _createElementVNode("strong", null, _toDisplayString(card.last_run || '未执行'), 1)
                        ]),
                        _createElementVNode("div", _hoisted_19, [
                          _hoisted_20,
                          _createElementVNode("strong", null, _toDisplayString(scheduleText(card)), 1)
                        ])
                      ]),
                      (card.detail_lines?.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_21, [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(card.detail_lines, (line) => {
                              return (_openBlock(), _createElementBlock("div", {
                                key: `${card.card_id}-${line}`,
                                class: "detail-line"
                              }, _toDisplayString(line), 1))
                            }), 128))
                          ]))
                        : _createCommentVNode("", true),
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
                    ]))
                  }), 128))
                ], 2))
          ]),
          _: 2
        }, 1032, ["kicker", "title", "subtitle", "tone"]))
      }), 128))
    ]),
    _createElementVNode("section", _hoisted_23, [
      _createVNode(NotificationList, { items: notifications.value }, null, 8, ["items"]),
      _createVNode(ActivityLogList, { items: activityLogs.value }, null, 8, ["items"])
    ])
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-ef8b5d5b"]]);

export { PageView as default };
