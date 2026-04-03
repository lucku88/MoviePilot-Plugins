import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_83d021fa_lang = '';

const {toDisplayString:_toDisplayString,createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-83d021fa"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "sq-page" };
const _hoisted_2 = { class: "sq-toolbar" };
const _hoisted_3 = { class: "sq-title" };
const _hoisted_4 = { class: "sq-subtitle" };
const _hoisted_5 = { class: "sq-actions" };
const _hoisted_6 = { class: "sq-stats" };
const _hoisted_7 = { class: "sq-stat-label" };
const _hoisted_8 = { class: "sq-stat-value" };
const _hoisted_9 = { class: "sq-panel" };
const _hoisted_10 = { class: "sq-panel-head" };
const _hoisted_11 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "收获背包", -1));
const _hoisted_12 = { class: "sq-chip-row" };
const _hoisted_13 = { class: "sq-chip" };
const _hoisted_14 = { class: "sq-chip" };
const _hoisted_15 = { class: "sq-chip" };
const _hoisted_16 = { class: "sq-chip" };
const _hoisted_17 = {
  key: 0,
  class: "sq-empty"
};
const _hoisted_18 = {
  key: 1,
  class: "sq-bag-grid"
};
const _hoisted_19 = { class: "sq-bag-icon" };
const _hoisted_20 = { class: "sq-bag-name" };
const _hoisted_21 = { class: "sq-bag-meta" };
const _hoisted_22 = { class: "sq-bag-meta" };
const _hoisted_23 = { class: "sq-bag-total" };
const _hoisted_24 = { class: "sq-panel" };
const _hoisted_25 = { class: "sq-panel-head" };
const _hoisted_26 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "种子商店", -1));
const _hoisted_27 = { class: "sq-submeta" };
const _hoisted_28 = { class: "sq-seed-toolbar" };
const _hoisted_29 = { class: "sq-interaction-note" };
const _hoisted_30 = { class: "sq-current-seed" };
const _hoisted_31 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "当前种子", -1));
const _hoisted_32 = { class: "sq-seed-grid" };
const _hoisted_33 = ["disabled", "onClick"];
const _hoisted_34 = { class: "sq-seed-icon" };
const _hoisted_35 = { class: "sq-seed-name" };
const _hoisted_36 = { class: "sq-seed-line" };
const _hoisted_37 = { class: "sq-seed-line" };
const _hoisted_38 = { class: "sq-seed-line" };
const _hoisted_39 = { class: "sq-seed-note" };
const _hoisted_40 = { class: "sq-farm-shell" };
const _hoisted_41 = { class: "sq-farm-banner" };
const _hoisted_42 = { class: "sq-group-title" };
const _hoisted_43 = { class: "sq-slot-grid" };
const _hoisted_44 = ["disabled", "onClick"];
const _hoisted_45 = { class: "sq-slot-icon" };
const _hoisted_46 = { class: "sq-slot-name" };
const _hoisted_47 = { class: "sq-slot-badge" };
const _hoisted_48 = { class: "sq-slot-desc" };
const _hoisted_49 = { class: "sq-slot-time" };
const _hoisted_50 = {
  key: 0,
  class: "sq-slot-action"
};
const _hoisted_51 = { class: "sq-panel" };
const _hoisted_52 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sq-panel-head" }, [
  /*#__PURE__*/_createElementVNode("span", null, "最近记录")
], -1));
const _hoisted_53 = {
  key: 0,
  class: "sq-empty"
};
const _hoisted_54 = {
  key: 1,
  class: "sq-history-list"
};
const _hoisted_55 = { class: "sq-history-top" };
const _hoisted_56 = { class: "sq-history-lines" };

const {computed,onBeforeUnmount,onMounted,reactive,ref,watch} = await importShared('vue');



const _sfc_main = {
  __name: 'Page',
  props: { api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } },
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;




const loading = ref(false);
const status = reactive({ farm_status: {}, history: [], config: {} });
const message = reactive({ text: '', type: 'success' });
const nowTs = ref(Math.floor(Date.now() / 1000));
const selectedSeedId = ref(null);
let timer = null;

const farm = computed(() => status.farm_status || {});
const historyItems = computed(() => status.history || farm.value.history || []);
const unlockedSeeds = computed(() => (farm.value.seed_shop || []).filter(seed => seed.unlocked));
const selectedSeed = computed(() => unlockedSeeds.value.find(seed => seed.id === selectedSeedId.value) || null);

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function syncSelectedSeed() {
  if (!unlockedSeeds.value.length) {
    selectedSeedId.value = null;
    return
  }
  if (unlockedSeeds.value.some(seed => seed.id === selectedSeedId.value)) {
    return
  }
  const preferred = unlockedSeeds.value.find(seed => seed.name === status.config?.prefer_seed || seed.preferred);
  selectedSeedId.value = (preferred || unlockedSeeds.value[0]).id;
}

async function loadStatus() {
  loading.value = true;
  try {
    const res = await props.api.get('/plugin/SQFarm/status');
    Object.assign(status, res || {});
    syncSelectedSeed();
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

async function harvestPlot(slot) {
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/plot/harvest', {
      land_id: slot.land_id,
      slot_index: slot.slot_index,
    });
    flash(res.message || `已处理 ${slot.land_name} #${slot.slot_index}`);
    await loadStatus();
  } catch (error) {
    flash(error?.message || '手动收菜失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function plantPlot(slot) {
  if (!selectedSeed.value) {
    flash('请先在上方选择种子', 'warning');
    return
  }
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/plot/plant', {
      land_id: slot.land_id,
      slot_index: slot.slot_index,
      seed_id: selectedSeedId.value,
    });
    flash(res.message || `已处理 ${slot.land_name} #${slot.slot_index}`);
    await loadStatus();
  } catch (error) {
    flash(error?.message || '手动种植失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function onSlotClick(slot) {
  if (slot.can_harvest) {
    await harvestPlot(slot);
    return
  }
  if (slot.can_plant) {
    await plantPlot(slot);
  }
}

function selectSeed(seed) {
  if (!seed?.unlocked || loading.value) {
    return
  }
  selectedSeedId.value = seed.id;
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

function slotActionText(slot) {
  if (slot.can_harvest) {
    return '点击收菜'
  }
  if (slot.can_plant) {
    return selectedSeed.value ? `点击种植 ${selectedSeed.value.icon}${selectedSeed.value.name}` : '先选种子'
  }
  return slot.action_label || ''
}

function closePlugin() {
  emit('close');
}

watch(unlockedSeeds, syncSelectedSeed, { deep: true });
watch(() => status.config?.prefer_seed, syncSelectedSeed);

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
      _createElementVNode("div", _hoisted_10, [
        _hoisted_11,
        _createElementVNode("div", _hoisted_12, [
          _createElementVNode("span", _hoisted_13, "成熟 " + _toDisplayString(farm.value.highlights?.ready_count || 0), 1),
          _createElementVNode("span", _hoisted_14, "成长 " + _toDisplayString(farm.value.highlights?.growing_count || 0), 1),
          _createElementVNode("span", _hoisted_15, "空地 " + _toDisplayString(farm.value.highlights?.empty_count || 0), 1),
          _createElementVNode("span", _hoisted_16, _toDisplayString(farm.value.cookie_source || status.cookie_source || '未同步 Cookie'), 1)
        ])
      ]),
      (farm.value.inventory?.empty)
        ? (_openBlock(), _createElementBlock("div", _hoisted_17, _toDisplayString(farm.value.inventory?.empty_text), 1))
        : (_openBlock(), _createElementBlock("div", _hoisted_18, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.inventory?.items || [], (item) => {
              return (_openBlock(), _createElementBlock("div", {
                key: item.name,
                class: "sq-bag-card"
              }, [
                _createElementVNode("div", _hoisted_19, _toDisplayString(item.icon), 1),
                _createElementVNode("div", _hoisted_20, _toDisplayString(item.name), 1),
                _createElementVNode("div", _hoisted_21, "数量 " + _toDisplayString(item.quantity), 1),
                _createElementVNode("div", _hoisted_22, "单价 " + _toDisplayString(item.unit_reward), 1),
                _createElementVNode("div", _hoisted_23, "+" + _toDisplayString(item.total_reward) + " 魔力", 1)
              ]))
            }), 128))
          ]))
    ]),
    _createElementVNode("div", _hoisted_24, [
      _createElementVNode("div", _hoisted_25, [
        _hoisted_26,
        _createElementVNode("div", _hoisted_27, "计划触发 " + _toDisplayString(farm.value.next_trigger_time || status.next_trigger_time || '等待轮询'), 1)
      ]),
      _createElementVNode("div", _hoisted_28, [
        _createElementVNode("div", _hoisted_29, _toDisplayString(farm.value.interaction_note || '先选种子，再点击空地种植；点击成熟田可手动收菜。'), 1),
        _createElementVNode("div", _hoisted_30, [
          _hoisted_31,
          _createElementVNode("strong", null, _toDisplayString(selectedSeed.value ? `${selectedSeed.value.icon} ${selectedSeed.value.name}` : '暂无可用种子'), 1)
        ])
      ]),
      _createElementVNode("div", _hoisted_32, [
        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.seed_shop || [], (seed) => {
          return (_openBlock(), _createElementBlock("button", {
            key: seed.id,
            type: "button",
            class: _normalizeClass(["sq-seed-card", {
            'is-locked': !seed.unlocked,
            'is-preferred': seed.preferred,
            'is-selected': seed.id === selectedSeedId.value,
          }]),
            disabled: !seed.unlocked || loading.value,
            onClick: $event => (selectSeed(seed))
          }, [
            _createElementVNode("div", _hoisted_34, _toDisplayString(seed.icon), 1),
            _createElementVNode("div", _hoisted_35, _toDisplayString(seed.name), 1),
            _createElementVNode("div", _hoisted_36, "消耗：" + _toDisplayString(seed.cost), 1),
            _createElementVNode("div", _hoisted_37, "收获：" + _toDisplayString(seed.reward), 1),
            _createElementVNode("div", _hoisted_38, "生长：" + _toDisplayString(seed.grow_text), 1),
            _createElementVNode("div", _hoisted_39, _toDisplayString(seed.unlocked ? (seed.id === selectedSeedId.value ? '当前已选种子' : (seed.preferred ? '默认优先种子' : '已解锁')) : seed.unlock_text), 1)
          ], 10, _hoisted_33))
        }), 128))
      ])
    ]),
    _createElementVNode("div", _hoisted_40, [
      _createElementVNode("div", _hoisted_41, [
        _createElementVNode("div", null, _toDisplayString(farm.value.interaction_note || '点击成熟田收菜；先选种子，再点击空地种植。'), 1),
        _createElementVNode("div", null, "当前准备种植：" + _toDisplayString(selectedSeed.value ? `${selectedSeed.value.icon} ${selectedSeed.value.name}` : '请先在上方选择种子'), 1)
      ]),
      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.land_groups || [], (group) => {
        return (_openBlock(), _createElementBlock("div", {
          key: group.id,
          class: "sq-land-group"
        }, [
          _createElementVNode("div", _hoisted_42, [
            _createTextVNode(_toDisplayString(group.name) + " ", 1),
            _createElementVNode("span", null, _toDisplayString(group.subtitle), 1)
          ]),
          _createElementVNode("div", _hoisted_43, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(group.slots, (slot) => {
              return (_openBlock(), _createElementBlock("button", {
                key: `${group.id}-${slot.slot_index}`,
                type: "button",
                class: _normalizeClass(["sq-slot", {
              [`is-${slot.state}`]: true,
              'is-clickable': slot.can_harvest || slot.can_plant,
              'is-busy': loading.value,
            }]),
                disabled: loading.value || (!slot.can_harvest && !slot.can_plant),
                onClick: $event => (onSlotClick(slot))
              }, [
                _createElementVNode("div", _hoisted_45, _toDisplayString(slot.icon), 1),
                _createElementVNode("div", _hoisted_46, _toDisplayString(slot.title), 1),
                _createElementVNode("div", _hoisted_47, _toDisplayString(slot.badge), 1),
                _createElementVNode("div", _hoisted_48, _toDisplayString(slot.description), 1),
                _createElementVNode("div", _hoisted_49, _toDisplayString(slotText(slot)), 1),
                (slot.can_harvest || slot.can_plant)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_50, _toDisplayString(slotActionText(slot)), 1))
                  : _createCommentVNode("", true)
              ], 10, _hoisted_44))
            }), 128))
          ])
        ]))
      }), 128))
    ]),
    _createElementVNode("div", _hoisted_51, [
      _hoisted_52,
      (!historyItems.value.length)
        ? (_openBlock(), _createElementBlock("div", _hoisted_53, "暂无执行记录"))
        : (_openBlock(), _createElementBlock("div", _hoisted_54, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(historyItems.value, (item) => {
              return (_openBlock(), _createElementBlock("div", {
                key: `${item.time}-${item.title}`,
                class: "sq-history-item"
              }, [
                _createElementVNode("div", _hoisted_55, [
                  _createElementVNode("strong", null, _toDisplayString(item.title), 1),
                  _createElementVNode("span", null, _toDisplayString(item.time), 1)
                ]),
                _createElementVNode("div", _hoisted_56, _toDisplayString((item.lines || []).join(' / ')), 1)
              ]))
            }), 128))
          ]))
    ])
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-83d021fa"]]);

export { PageView as default };
