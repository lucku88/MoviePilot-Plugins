import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_219b7add_lang = '';

const {toDisplayString:_toDisplayString,createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-219b7add"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "sq-page" };
const _hoisted_2 = { class: "sq-toolbar" };
const _hoisted_3 = { class: "sq-title" };
const _hoisted_4 = { class: "sq-subtitle" };
const _hoisted_5 = { class: "sq-actions" };
const _hoisted_6 = { class: "sq-stats" };
const _hoisted_7 = { class: "sq-stat-label" };
const _hoisted_8 = { class: "sq-stat-value" };
const _hoisted_9 = { class: "sq-panel sq-panel-note" };
const _hoisted_10 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-note-title" }, "执行说明", -1));
const _hoisted_11 = { class: "sq-note-text" };
const _hoisted_12 = { class: "sq-panel" };
const _hoisted_13 = { class: "sq-panel-head" };
const _hoisted_14 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "收获背包", -1));
const _hoisted_15 = { class: "sq-chip-row" };
const _hoisted_16 = { class: "sq-chip" };
const _hoisted_17 = { class: "sq-chip" };
const _hoisted_18 = { class: "sq-chip" };
const _hoisted_19 = { class: "sq-chip" };
const _hoisted_20 = {
  key: 0,
  class: "sq-empty"
};
const _hoisted_21 = {
  key: 1,
  class: "sq-bag-grid"
};
const _hoisted_22 = { class: "sq-bag-icon" };
const _hoisted_23 = { class: "sq-bag-name" };
const _hoisted_24 = { class: "sq-bag-meta" };
const _hoisted_25 = { class: "sq-bag-meta" };
const _hoisted_26 = { class: "sq-bag-total" };
const _hoisted_27 = { class: "sq-panel" };
const _hoisted_28 = { class: "sq-panel-head" };
const _hoisted_29 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "种子商店", -1));
const _hoisted_30 = { class: "sq-submeta" };
const _hoisted_31 = { class: "sq-seed-grid" };
const _hoisted_32 = { class: "sq-seed-icon" };
const _hoisted_33 = { class: "sq-seed-name" };
const _hoisted_34 = { class: "sq-seed-line" };
const _hoisted_35 = { class: "sq-seed-line" };
const _hoisted_36 = { class: "sq-seed-line" };
const _hoisted_37 = { class: "sq-seed-note" };
const _hoisted_38 = { class: "sq-farm-shell" };
const _hoisted_39 = { class: "sq-group-title" };
const _hoisted_40 = { class: "sq-slot-grid" };
const _hoisted_41 = { class: "sq-slot-icon" };
const _hoisted_42 = { class: "sq-slot-name" };
const _hoisted_43 = { class: "sq-slot-badge" };
const _hoisted_44 = { class: "sq-slot-desc" };
const _hoisted_45 = { class: "sq-slot-time" };
const _hoisted_46 = { class: "sq-panel" };
const _hoisted_47 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-head" }, [
  /*#__PURE__*/_createElementVNode("span", null, "最近记录")
], -1));
const _hoisted_48 = {
  key: 0,
  class: "sq-empty"
};
const _hoisted_49 = {
  key: 1,
  class: "sq-history-list"
};
const _hoisted_50 = { class: "sq-history-top" };
const _hoisted_51 = { class: "sq-history-lines" };

const {computed,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Page',
  props: { api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } },
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;




const loading = ref(false);
const status = reactive({ farm_status: {}, history: [] });
const message = reactive({ text: '', type: 'success' });
const nowTs = ref(Math.floor(Date.now() / 1000));
let timer = null;

const farm = computed(() => status.farm_status || {});
const historyItems = computed(() => status.history || farm.value.history || []);

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

async function loadStatus() {
  loading.value = true;
  try {
    const res = await props.api.get('/plugin/SQFarm/status');
    Object.assign(status, res || {});
  } catch (error) {
    flash(error?.message || '加载状态失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function refreshData() {
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/refresh', {});
    flash(res.message || '已刷新');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '刷新失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function runNow() {
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/run', {});
    flash(res.message || '执行完成');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '执行失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function syncCookie() {
  loading.value = true;
  try {
    const res = await props.api.get('/plugin/SQFarm/cookie');
    flash(res.message || '已同步 Cookie');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error');
  } finally {
    loading.value = false;
  }
}

function formatRemain(seconds) {
  const sec = Math.max(0, Number(seconds) || 0);
  if (!sec) return '现在可收'
  const hours = Math.floor(sec / 3600);
  const minutes = Math.floor((sec % 3600) / 60);
  const secs = sec % 60;
  if (hours) return `${hours}小时${minutes}分`
  if (minutes) return `${minutes}分${secs}秒`
  return `${secs}秒`
}

function slotText(slot) {
  if (slot.harvest_ts) {
    const remain = slot.harvest_ts - nowTs.value;
    if (slot.state === 'growing') return formatRemain(remain)
    if (slot.state === 'ready') return '现在可收'
  }
  return slot.remaining_label || slot.reward_text || ''
}

function closePlugin() {
  emit('close');
}

onMounted(async () => {
  await loadStatus();
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000);
  }, 1000);
});

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer);
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("div", null, [
        _createElementVNode("h1", _hoisted_3, _toDisplayString(farm.value.title || '思齐种菜赚魔力'), 1),
        _createElementVNode("div", _hoisted_4, "最近执行 " + _toDisplayString(status.last_run || '暂无') + " · 下次收菜 " + _toDisplayString(farm.value.next_run_time || '待计算'), 1)
      ]),
      _createElementVNode("div", _hoisted_5, [
        _createVNode(_component_v_btn, {
          color: "success",
          variant: "flat",
          loading: loading.value,
          onClick: runNow
        }, {
          default: _withCtx(() => [
            _createTextVNode("立即执行")
          ]),
          _: 1
        }, 8, ["loading"]),
        _createVNode(_component_v_btn, {
          color: "primary",
          variant: "flat",
          loading: loading.value,
          onClick: refreshData
        }, {
          default: _withCtx(() => [
            _createTextVNode("刷新")
          ]),
          _: 1
        }, 8, ["loading"]),
        _createVNode(_component_v_btn, {
          color: "warning",
          variant: "flat",
          loading: loading.value,
          onClick: syncCookie
        }, {
          default: _withCtx(() => [
            _createTextVNode("同步Cookie")
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
          class: "mb-4"
        }, {
          default: _withCtx(() => [
            _createTextVNode(_toDisplayString(message.text), 1)
          ]),
          _: 1
        }, 8, ["type"]))
      : _createCommentVNode("", true),
    _createElementVNode("div", _hoisted_6, [
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.overview || [], (item) => {
        return (_openBlock(), _createElementBlock("div", {
          key: item.label,
          class: "sq-stat-card"
        }, [
          _createElementVNode("div", _hoisted_7, _toDisplayString(item.label), 1),
          _createElementVNode("div", _hoisted_8, _toDisplayString(item.value), 1)
        ]))
      }), 128))
    ]),
    _createElementVNode("div", _hoisted_9, [
      _hoisted_10,
      _createElementVNode("div", _hoisted_11, _toDisplayString(farm.value.page_note || '插件会先动态识别最近收菜时间并记录下一次运行；如果当前还没有收菜时间，会自动运行一次获取农场信息。'), 1)
    ]),
    _createElementVNode("div", _hoisted_12, [
      _createElementVNode("div", _hoisted_13, [
        _hoisted_14,
        _createElementVNode("div", _hoisted_15, [
          _createElementVNode("span", _hoisted_16, "成熟 " + _toDisplayString(farm.value.highlights?.ready_count || 0), 1),
          _createElementVNode("span", _hoisted_17, "成长 " + _toDisplayString(farm.value.highlights?.growing_count || 0), 1),
          _createElementVNode("span", _hoisted_18, "空地 " + _toDisplayString(farm.value.highlights?.empty_count || 0), 1),
          _createElementVNode("span", _hoisted_19, _toDisplayString(farm.value.cookie_source || status.cookie_source || '未同步 Cookie'), 1)
        ])
      ]),
      (farm.value.inventory?.empty)
        ? (_openBlock(), _createElementBlock("div", _hoisted_20, _toDisplayString(farm.value.inventory?.empty_text), 1))
        : (_openBlock(), _createElementBlock("div", _hoisted_21, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.inventory?.items || [], (item) => {
              return (_openBlock(), _createElementBlock("div", {
                key: item.name,
                class: "sq-bag-card"
              }, [
                _createElementVNode("div", _hoisted_22, _toDisplayString(item.icon), 1),
                _createElementVNode("div", _hoisted_23, _toDisplayString(item.name), 1),
                _createElementVNode("div", _hoisted_24, "数量 " + _toDisplayString(item.quantity), 1),
                _createElementVNode("div", _hoisted_25, "单价 " + _toDisplayString(item.unit_reward), 1),
                _createElementVNode("div", _hoisted_26, "+" + _toDisplayString(item.total_reward) + " 魔力", 1)
              ]))
            }), 128))
          ]))
    ]),
    _createElementVNode("div", _hoisted_27, [
      _createElementVNode("div", _hoisted_28, [
        _hoisted_29,
        _createElementVNode("div", _hoisted_30, "计划触发 " + _toDisplayString(farm.value.next_trigger_time || status.next_trigger_time || '等待轮询'), 1)
      ]),
      _createElementVNode("div", _hoisted_31, [
        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.seed_shop || [], (seed) => {
          return (_openBlock(), _createElementBlock("div", {
            key: seed.id,
            class: _normalizeClass(["sq-seed-card", { 'is-locked': !seed.unlocked, 'is-preferred': seed.preferred }])
          }, [
            _createElementVNode("div", _hoisted_32, _toDisplayString(seed.icon), 1),
            _createElementVNode("div", _hoisted_33, _toDisplayString(seed.name), 1),
            _createElementVNode("div", _hoisted_34, "消耗：" + _toDisplayString(seed.cost), 1),
            _createElementVNode("div", _hoisted_35, "收获：" + _toDisplayString(seed.reward), 1),
            _createElementVNode("div", _hoisted_36, "生长：" + _toDisplayString(seed.grow_text), 1),
            _createElementVNode("div", _hoisted_37, _toDisplayString(seed.unlocked ? (seed.preferred ? '当前优先种子' : '已解锁') : seed.unlock_text), 1)
          ], 2))
        }), 128))
      ])
    ]),
    _createElementVNode("div", _hoisted_38, [
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.land_groups || [], (group) => {
        return (_openBlock(), _createElementBlock("div", {
          key: group.id,
          class: "sq-land-group"
        }, [
          _createElementVNode("div", _hoisted_39, [
            _createTextVNode(_toDisplayString(group.name) + " ", 1),
            _createElementVNode("span", null, _toDisplayString(group.subtitle), 1)
          ]),
          _createElementVNode("div", _hoisted_40, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(group.slots, (slot) => {
              return (_openBlock(), _createElementBlock("div", {
                key: `${group.id}-${slot.slot_index}`,
                class: _normalizeClass(["sq-slot", `is-${slot.state}`])
              }, [
                _createElementVNode("div", _hoisted_41, _toDisplayString(slot.icon), 1),
                _createElementVNode("div", _hoisted_42, _toDisplayString(slot.title), 1),
                _createElementVNode("div", _hoisted_43, _toDisplayString(slot.badge), 1),
                _createElementVNode("div", _hoisted_44, _toDisplayString(slot.description), 1),
                _createElementVNode("div", _hoisted_45, _toDisplayString(slotText(slot)), 1)
              ], 2))
            }), 128))
          ])
        ]))
      }), 128))
    ]),
    _createElementVNode("div", _hoisted_46, [
      _hoisted_47,
      (!historyItems.value.length)
        ? (_openBlock(), _createElementBlock("div", _hoisted_48, "暂无执行记录"))
        : (_openBlock(), _createElementBlock("div", _hoisted_49, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(historyItems.value, (item) => {
              return (_openBlock(), _createElementBlock("div", {
                key: `${item.time}-${item.title}`,
                class: "sq-history-item"
              }, [
                _createElementVNode("div", _hoisted_50, [
                  _createElementVNode("strong", null, _toDisplayString(item.title), 1),
                  _createElementVNode("span", null, _toDisplayString(item.time), 1)
                ]),
                _createElementVNode("div", _hoisted_51, _toDisplayString((item.lines || []).join(' / ')), 1)
              ]))
            }), 128))
          ]))
    ])
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-219b7add"]]);

export { PageView as default };
