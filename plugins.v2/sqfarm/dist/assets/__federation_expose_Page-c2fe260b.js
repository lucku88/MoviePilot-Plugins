import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_ed64d811_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,withModifiers:_withModifiers,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-ed64d811"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "sqfarm-page" };
const _hoisted_2 = { class: "sqfarm-shell" };
const _hoisted_3 = { class: "sqfarm-hero__header" };
const _hoisted_4 = { class: "sqfarm-hero__copy" };
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-badge" }, "SQ农场", -1));
const _hoisted_6 = { class: "sqfarm-title" };
const _hoisted_7 = { class: "sqfarm-subtitle" };
const _hoisted_8 = { class: "sqfarm-actions" };
const _hoisted_9 = { class: "sqfarm-chip-row" };
const _hoisted_10 = { class: "sqfarm-chip" };
const _hoisted_11 = { class: "sqfarm-chip" };
const _hoisted_12 = { class: "sqfarm-chip" };
const _hoisted_13 = { class: "sqfarm-chip" };
const _hoisted_14 = { class: "sqfarm-stat-label" };
const _hoisted_15 = { class: "sqfarm-stat-value" };
const _hoisted_16 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-section-kicker" }, "本次摘要", -1));
const _hoisted_17 = { class: "sqfarm-summary-list" };
const _hoisted_18 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-section-kicker" }, "收获背包", -1));
const _hoisted_19 = {
  key: 0,
  class: "sqfarm-empty"
};
const _hoisted_20 = {
  key: 1,
  class: "sqfarm-bag-grid"
};
const _hoisted_21 = { class: "sqfarm-bag-icon" };
const _hoisted_22 = { class: "sqfarm-bag-name" };
const _hoisted_23 = { class: "sqfarm-bag-meta" };
const _hoisted_24 = { class: "sqfarm-bag-meta" };
const _hoisted_25 = { class: "sqfarm-bag-bonus" };
const _hoisted_26 = { class: "sqfarm-inline-actions" };
const _hoisted_27 = ["max", "value", "disabled", "onInput"];
const _hoisted_28 = ["disabled", "onClick"];
const _hoisted_29 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-section-kicker" }, "种子商店", -1));
const _hoisted_30 = { class: "sqfarm-toolbar" };
const _hoisted_31 = { class: "sqfarm-chip" };
const _hoisted_32 = { key: 0 };
const _hoisted_33 = { key: 1 };
const _hoisted_34 = { class: "sqfarm-actions" };
const _hoisted_35 = { class: "sqfarm-seed-grid" };
const _hoisted_36 = ["disabled", "onClick"];
const _hoisted_37 = { class: "sqfarm-seed-icon" };
const _hoisted_38 = { class: "sqfarm-seed-name" };
const _hoisted_39 = { class: "sqfarm-seed-line" };
const _hoisted_40 = { class: "sqfarm-seed-line" };
const _hoisted_41 = { class: "sqfarm-seed-note" };
const _hoisted_42 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-section-kicker" }, "农场坑位", -1));
const _hoisted_43 = { class: "sqfarm-group-head" };
const _hoisted_44 = { class: "sqfarm-group-name" };
const _hoisted_45 = { class: "sqfarm-group-subtitle" };
const _hoisted_46 = { class: "sqfarm-slot-grid" };
const _hoisted_47 = ["disabled", "onClick"];
const _hoisted_48 = { class: "sqfarm-slot-top" };
const _hoisted_49 = { class: "sqfarm-slot-index" };
const _hoisted_50 = { class: "sqfarm-slot-badge" };
const _hoisted_51 = { class: "sqfarm-slot-icon" };
const _hoisted_52 = { class: "sqfarm-slot-name" };
const _hoisted_53 = { class: "sqfarm-slot-time" };
const _hoisted_54 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-section-kicker" }, "最近记录", -1));
const _hoisted_55 = {
  key: 0,
  class: "sqfarm-empty"
};
const _hoisted_56 = {
  key: 1,
  class: "sqfarm-history-list"
};
const _hoisted_57 = { class: "sqfarm-history-top" };
const _hoisted_58 = { class: "sqfarm-history-lines" };

const {computed,onBeforeUnmount,onMounted,reactive,ref,watch} = await importShared('vue');



const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;





const loading = ref(false);
const actingSlotKey = ref('');
const sellingSeedId = ref(0);
const status = reactive({ farm_status: {}, history: [] });
const message = reactive({ text: '', type: 'success' });
const nowTs = ref(Math.floor(Date.now() / 1000));
const selectedSeedId = ref(null);
const lastRunAutoRefreshTs = ref(0);
const lastTriggerAutoRefreshTs = ref(0);
const sellInputs = reactive({});
const dismissedSummaryKey = ref('');

let timer = null;

const farm = computed(() => status.farm_status || {});
const historyItems = computed(() => status.history || farm.value.history || []);
const summaryLines = computed(() => (farm.value.summary || []).filter(Boolean));
const summaryKey = computed(() => summaryLines.value.join('||'));
const showSummary = computed(() => !!summaryLines.value.length && dismissedSummaryKey.value !== summaryKey.value);
const seedShop = computed(() => farm.value.seed_shop || []);
const inventoryItems = computed(() => farm.value.inventory?.items || []);
const unlockedSeeds = computed(() => seedShop.value.filter((seed) => seed.unlocked));
const selectedSeed = computed(() => {
  return seedShop.value.find((seed) => Number(seed.id) === Number(selectedSeedId.value)) || null
});
const allSlots = computed(() => {
  return (farm.value.land_groups || []).flatMap((group) => group.slots || [])
});
const readySlots = computed(() => allSlots.value.filter((slot) => slot.state === 'ready'));
const emptySlots = computed(() => allSlots.value.filter((slot) => slot.state === 'empty'));
const nextRunTs = computed(() => Number(farm.value.next_run_ts || 0) || parseDateTime(farm.value.next_run_time));
const nextTriggerTs = computed(() => Number(farm.value.next_trigger_ts || 0) || parseDateTime(farm.value.next_trigger_time));

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function parseDateTime(value) {
  if (!value || typeof value !== 'string') {
    return 0
  }
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/);
  if (!match) {
    return 0
  }
  const [, year, month, day, hour, minute, second] = match;
  return Math.floor(
    new Date(
      Number(year),
      Number(month) - 1,
      Number(day),
      Number(hour),
      Number(minute),
      Number(second),
    ).getTime() / 1000,
  )
}

function loadDismissedSummaryKey() {
  if (typeof window === 'undefined' || !window.sessionStorage) {
    dismissedSummaryKey.value = '';
    return
  }
  dismissedSummaryKey.value = window.sessionStorage.getItem('sqfarm-dismissed-summary') || '';
}

function dismissSummary() {
  const key = summaryKey.value;
  dismissedSummaryKey.value = key;
  if (typeof window !== 'undefined' && window.sessionStorage) {
    if (key) {
      window.sessionStorage.setItem('sqfarm-dismissed-summary', key);
    } else {
      window.sessionStorage.removeItem('sqfarm-dismissed-summary');
    }
  }
}

function syncSelectedSeed() {
  const available = unlockedSeeds.value;
  if (!available.length) {
    selectedSeedId.value = null;
    return
  }
  const current = available.find((seed) => Number(seed.id) === Number(selectedSeedId.value));
  if (current) {
    return
  }
  const preferred = available.find((seed) => seed.preferred);
  selectedSeedId.value = Number((preferred || available[0]).id);
}

watch(seedShop, syncSelectedSeed, { immediate: true, deep: true });
watch(summaryKey, () => loadDismissedSummaryKey());
watch(
  inventoryItems,
  (items) => {
    const activeKeys = new Set();
    for (const item of items) {
      const key = String(item.seed_id || item.name);
      activeKeys.add(key);
      const current = Number(sellInputs[key]);
      sellInputs[key] = current > 0 ? Math.min(current, Number(item.quantity || 1)) : 1;
    }
    for (const key of Object.keys(sellInputs)) {
      if (!activeKeys.has(key)) {
        delete sellInputs[key];
      }
    }
  },
  { immediate: true, deep: true },
);

watch(nextRunTs, (value) => {
  if (!value || value > nowTs.value) lastRunAutoRefreshTs.value = 0;
});
watch(nextTriggerTs, (value) => {
  if (!value || value > nowTs.value) lastTriggerAutoRefreshTs.value = 0;
});

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

async function maybeAutoRefreshStatus() {
  if (loading.value) return
  let shouldRefresh = false;
  if (nextRunTs.value && nowTs.value >= nextRunTs.value && nextRunTs.value !== lastRunAutoRefreshTs.value) {
    lastRunAutoRefreshTs.value = nextRunTs.value;
    shouldRefresh = true;
  }
  if (nextTriggerTs.value && nowTs.value >= nextTriggerTs.value && nextTriggerTs.value !== lastTriggerAutoRefreshTs.value) {
    lastTriggerAutoRefreshTs.value = nextTriggerTs.value;
    shouldRefresh = true;
  }
  if (shouldRefresh) {
    await loadStatus();
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
    flash(res.message || 'Cookie 已同步');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error');
  } finally {
    loading.value = false;
  }
}

function selectSeed(seed) {
  if (!seed?.unlocked) return
  selectedSeedId.value = Number(seed.id);
  flash(`已选择 ${seed.icon} ${seed.name}`);
}

function slotKey(slot) {
  return `${slot.land_id}-${slot.slot_index}`
}

function isInteractiveSlot(slot) {
  return slot.state === 'ready' || slot.state === 'empty'
}

function inventoryKey(item) {
  return String(item.seed_id || item.name)
}

function getSellQuantity(item) {
  const key = inventoryKey(item);
  const current = Number(sellInputs[key]);
  if (!current || current < 1) return 1
  return Math.min(current, Number(item.quantity || 1))
}

function updateSellQuantity(item, event) {
  const raw = Number(event?.target?.value || 1);
  const safe = Math.min(Math.max(1, raw || 1), Number(item.quantity || 1));
  sellInputs[inventoryKey(item)] = safe;
}

async function plantPlot(slot, seedId) {
  actingSlotKey.value = slotKey(slot);
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/plant-plot', {
      land_id: slot.land_id,
      slot_index: slot.slot_index,
      seed_id: seedId,
    });
    flash(res.message || '种植完成');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '种植失败', 'error');
  } finally {
    actingSlotKey.value = '';
    loading.value = false;
  }
}

async function harvestPlot(slot) {
  actingSlotKey.value = slotKey(slot);
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/harvest-plot', {
      land_id: slot.land_id,
      slot_index: slot.slot_index,
    });
    flash(res.message || '收菜完成');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '收菜失败', 'error');
  } finally {
    actingSlotKey.value = '';
    loading.value = false;
  }
}

async function sellInventory(item) {
  const seedId = Number(item.seed_id || 0);
  const quantity = getSellQuantity(item);
  if (!seedId || quantity <= 0) {
    flash('出售参数无效', 'warning');
    return
  }
  sellingSeedId.value = seedId;
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/sell-inventory', {
      seed_id: seedId,
      quantity,
    });
    flash(res.message || '出售完成');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '出售失败', 'error');
  } finally {
    sellingSeedId.value = 0;
    loading.value = false;
  }
}

async function plantAllEmpty() {
  if (!emptySlots.value.length) {
    flash('当前没有可种植空地', 'warning');
    return
  }
  if (!selectedSeed.value) {
    flash('请先选择种子', 'warning');
    return
  }
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/plant-empty', {
      seed_id: selectedSeed.value.id,
    });
    flash(res.message || '一键种植完成');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '一键种植失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function harvestAllReady() {
  if (!readySlots.value.length) {
    flash('当前没有可收获田块', 'warning');
    return
  }
  loading.value = true;
  try {
    const res = await props.api.post('/plugin/SQFarm/harvest-all', {});
    flash(res.message || '一键收获完成');
    await loadStatus();
  } catch (error) {
    flash(error?.message || '一键收获失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function handleSlotClick(slot) {
  if (loading.value) return
  if (slot.state === 'ready') return harvestPlot(slot)
  if (slot.state === 'empty') {
    if (!selectedSeed.value) {
      flash('请先在种子商店选择一个种子', 'warning');
      return
    }
    return plantPlot(slot, selectedSeed.value.id)
  }
  if (slot.state === 'growing') {
    flash(`${slot.title} 还需 ${slot.remaining_label || slot.reward_text || '等待成熟'}`, 'info');
    return
  }
  if (slot.state === 'expand') {
    flash(`${slot.land_name} 可扩展：${slot.description}`, 'info');
    return
  }
  if (slot.state === 'locked') {
    flash(`${slot.land_name} 这块田暂未解锁`, 'info');
  }
}

function formatRemain(seconds) {
  const sec = Math.max(0, Number(seconds) || 0);
  if (!sec) return '现在可收'
  const hours = Math.floor(sec / 3600);
  const minutes = Math.floor((sec % 3600) / 60);
  const secs = sec % 60;
  if (hours) return `${hours}小时${minutes}分钟`
  if (minutes) return `${minutes}分钟${secs}秒`
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
  if (showSummary.value) dismissSummary();
  emit('close');
}

onMounted(async () => {
  loadDismissedSummaryKey();
  await loadStatus();
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000);
    void maybeAutoRefreshStatus();
  }, 1000);
});

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer);
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_item = _resolveComponent("v-card-item");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createVNode(_component_v_card, {
        class: "sqfarm-card sqfarm-hero",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_text, { class: "sqfarm-hero__body" }, {
            default: _withCtx(() => [
              _createElementVNode("div", _hoisted_3, [
                _createElementVNode("div", _hoisted_4, [
                  _hoisted_5,
                  _createElementVNode("h1", _hoisted_6, _toDisplayString(farm.value.title || '种菜赚魔力'), 1),
                  _createElementVNode("p", _hoisted_7, " 最近执行 " + _toDisplayString(status.last_run || '暂无') + " · 下次可收 " + _toDisplayString(farm.value.next_run_time || '待识别'), 1)
                ]),
                _createElementVNode("div", _hoisted_8, [
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
                      _createTextVNode("刷新状态")
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
                      _createTextVNode("同步 Cookie")
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
              _createElementVNode("div", _hoisted_9, [
                _createElementVNode("div", _hoisted_10, "计划触发 " + _toDisplayString(farm.value.next_trigger_time || status.next_trigger_time || '等待下一次运行'), 1),
                _createElementVNode("div", _hoisted_11, "站点同步 " + _toDisplayString(farm.value.cookie_source || status.cookie_source || '未同步'), 1),
                _createElementVNode("div", _hoisted_12, "成熟 " + _toDisplayString(readySlots.value.length) + " 块", 1),
                _createElementVNode("div", _hoisted_13, "空地 " + _toDisplayString(emptySlots.value.length) + " 块", 1)
              ])
            ]),
            _: 1
          })
        ]),
        _: 1
      }),
      (message.text)
        ? (_openBlock(), _createBlock(_component_v_alert, {
            key: 0,
            type: message.type,
            variant: "tonal",
            rounded: "xl",
            class: "sqfarm-alert"
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(message.text), 1)
            ]),
            _: 1
          }, 8, ["type"]))
        : _createCommentVNode("", true),
      _createVNode(_component_v_row, {
        class: "sqfarm-stat-row",
        dense: ""
      }, {
        default: _withCtx(() => [
          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.overview || [], (item) => {
            return (_openBlock(), _createBlock(_component_v_col, {
              key: item.label,
              cols: "12",
              sm: "6",
              lg: "3"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card, {
                  class: "sqfarm-card sqfarm-stat-card",
                  rounded: "xl",
                  flat: ""
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card_text, null, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_14, _toDisplayString(item.label), 1),
                        _createElementVNode("div", _hoisted_15, _toDisplayString(item.value), 1)
                      ]),
                      _: 2
                    }, 1024)
                  ]),
                  _: 2
                }, 1024)
              ]),
              _: 2
            }, 1024))
          }), 128))
        ]),
        _: 1
      }),
      (showSummary.value)
        ? (_openBlock(), _createBlock(_component_v_card, {
            key: 1,
            class: "sqfarm-card",
            rounded: "xl",
            flat: ""
          }, {
            default: _withCtx(() => [
              _createVNode(_component_v_card_item, null, {
                prepend: _withCtx(() => [
                  _hoisted_16
                ]),
                append: _withCtx(() => [
                  _createVNode(_component_v_btn, {
                    variant: "text",
                    size: "small",
                    onClick: dismissSummary
                  }, {
                    default: _withCtx(() => [
                      _createTextVNode("关闭")
                    ]),
                    _: 1
                  })
                ]),
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, null, {
                    default: _withCtx(() => [
                      _createTextVNode("任务结果")
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }),
              _createVNode(_component_v_card_text, null, {
                default: _withCtx(() => [
                  _createElementVNode("div", _hoisted_17, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(summaryLines.value, (line) => {
                      return (_openBlock(), _createElementBlock("div", {
                        key: line,
                        class: "sqfarm-summary-line"
                      }, _toDisplayString(line), 1))
                    }), 128))
                  ])
                ]),
                _: 1
              })
            ]),
            _: 1
          }))
        : _createCommentVNode("", true),
      _createVNode(_component_v_card, {
        class: "sqfarm-card",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_item, null, {
            prepend: _withCtx(() => [
              _hoisted_18
            ]),
            default: _withCtx(() => [
              _createVNode(_component_v_card_title, null, {
                default: _withCtx(() => [
                  _createTextVNode("当前库存")
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_v_card_text, null, {
            default: _withCtx(() => [
              (farm.value.inventory?.empty)
                ? (_openBlock(), _createElementBlock("div", _hoisted_19, _toDisplayString(farm.value.inventory?.empty_text), 1))
                : (_openBlock(), _createElementBlock("div", _hoisted_20, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(inventoryItems.value, (item) => {
                      return (_openBlock(), _createElementBlock("article", {
                        key: item.seed_id || item.name,
                        class: "sqfarm-bag-card"
                      }, [
                        _createElementVNode("div", _hoisted_21, _toDisplayString(item.icon), 1),
                        _createElementVNode("div", _hoisted_22, _toDisplayString(item.name), 1),
                        _createElementVNode("div", _hoisted_23, "数量 " + _toDisplayString(item.quantity), 1),
                        _createElementVNode("div", _hoisted_24, [
                          _createTextVNode(" 售：" + _toDisplayString(item.unit_reward) + " 魔力/份 ", 1),
                          _createElementVNode("span", _hoisted_25, "+" + _toDisplayString(item.sell_bonus_percent || 0) + "%", 1)
                        ]),
                        _createElementVNode("div", _hoisted_26, [
                          _createElementVNode("input", {
                            class: "sqfarm-number",
                            type: "number",
                            min: "1",
                            max: item.quantity,
                            value: getSellQuantity(item),
                            disabled: loading.value || sellingSeedId.value === item.seed_id,
                            onClick: _cache[1] || (_cache[1] = _withModifiers(() => {}, ["stop"])),
                            onInput: $event => (updateSellQuantity(item, $event))
                          }, null, 40, _hoisted_27),
                          _createElementVNode("button", {
                            type: "button",
                            class: "sqfarm-action-btn is-warning",
                            disabled: loading.value || !item.quantity || sellingSeedId.value === item.seed_id,
                            onClick: _withModifiers($event => (sellInventory(item)), ["stop"])
                          }, _toDisplayString(sellingSeedId.value === item.seed_id ? '出售中' : '出售'), 9, _hoisted_28)
                        ])
                      ]))
                    }), 128))
                  ]))
            ]),
            _: 1
          })
        ]),
        _: 1
      }),
      _createVNode(_component_v_card, {
        class: "sqfarm-card",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_item, null, {
            prepend: _withCtx(() => [
              _hoisted_29
            ]),
            default: _withCtx(() => [
              _createVNode(_component_v_card_title, null, {
                default: _withCtx(() => [
                  _createTextVNode("选择种子后点击空地种植")
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_v_card_text, null, {
            default: _withCtx(() => [
              _createElementVNode("div", _hoisted_30, [
                _createElementVNode("div", _hoisted_31, [
                  _createTextVNode(" 当前种子： "),
                  (selectedSeed.value)
                    ? (_openBlock(), _createElementBlock("strong", _hoisted_32, _toDisplayString(selectedSeed.value.icon) + " " + _toDisplayString(selectedSeed.value.name), 1))
                    : (_openBlock(), _createElementBlock("strong", _hoisted_33, "未选择"))
                ]),
                _createElementVNode("div", _hoisted_34, [
                  _createVNode(_component_v_btn, {
                    color: "success",
                    variant: "flat",
                    disabled: !selectedSeed.value || !emptySlots.value.length || loading.value,
                    onClick: plantAllEmpty
                  }, {
                    default: _withCtx(() => [
                      _createTextVNode(" 一键种植空地 ")
                    ]),
                    _: 1
                  }, 8, ["disabled"]),
                  _createVNode(_component_v_btn, {
                    color: "warning",
                    variant: "flat",
                    disabled: !readySlots.value.length || loading.value,
                    onClick: harvestAllReady
                  }, {
                    default: _withCtx(() => [
                      _createTextVNode(" 一键收获 ")
                    ]),
                    _: 1
                  }, 8, ["disabled"])
                ])
              ]),
              _createElementVNode("div", _hoisted_35, [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.seed_shop || [], (seed) => {
                  return (_openBlock(), _createElementBlock("button", {
                    key: seed.id,
                    type: "button",
                    class: _normalizeClass(["sqfarm-seed-card", {
                'is-locked': !seed.unlocked,
                'is-selected': selectedSeed.value && Number(selectedSeed.value.id) === Number(seed.id),
              }]),
                    disabled: !seed.unlocked || loading.value,
                    onClick: $event => (selectSeed(seed))
                  }, [
                    _createElementVNode("div", _hoisted_37, _toDisplayString(seed.icon), 1),
                    _createElementVNode("div", _hoisted_38, _toDisplayString(seed.name), 1),
                    _createElementVNode("div", _hoisted_39, "消耗 " + _toDisplayString(seed.cost), 1),
                    _createElementVNode("div", _hoisted_40, "生长 " + _toDisplayString(seed.grow_text), 1),
                    _createElementVNode("div", _hoisted_41, _toDisplayString(seed.unlocked ? (selectedSeed.value && Number(selectedSeed.value.id) === Number(seed.id) ? '已选中' : '点击选择') : seed.unlock_text), 1)
                  ], 10, _hoisted_36))
                }), 128))
              ])
            ]),
            _: 1
          })
        ]),
        _: 1
      }),
      _createVNode(_component_v_card, {
        class: "sqfarm-card",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_item, null, {
            prepend: _withCtx(() => [
              _hoisted_42
            ]),
            default: _withCtx(() => [
              _createVNode(_component_v_card_title, null, {
                default: _withCtx(() => [
                  _createTextVNode("分组状态")
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_v_card_text, { class: "sqfarm-land-stack" }, {
            default: _withCtx(() => [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(farm.value.land_groups || [], (group) => {
                return (_openBlock(), _createElementBlock("article", {
                  key: group.id,
                  class: "sqfarm-group-card"
                }, [
                  _createElementVNode("header", _hoisted_43, [
                    _createElementVNode("div", _hoisted_44, _toDisplayString(group.name), 1),
                    _createElementVNode("div", _hoisted_45, _toDisplayString(group.subtitle), 1)
                  ]),
                  _createElementVNode("div", _hoisted_46, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(group.slots, (slot) => {
                      return (_openBlock(), _createElementBlock("button", {
                        key: `${group.id}-${slot.slot_index}`,
                        type: "button",
                        class: _normalizeClass(["sqfarm-slot", [
                  `is-${slot.state}`,
                  { 'is-clickable': isInteractiveSlot(slot), 'is-busy': actingSlotKey.value === slotKey(slot) }
                ]]),
                        disabled: loading.value || actingSlotKey.value === slotKey(slot),
                        onClick: $event => (handleSlotClick(slot))
                      }, [
                        _createElementVNode("div", _hoisted_48, [
                          _createElementVNode("span", _hoisted_49, "#" + _toDisplayString(slot.slot_index), 1),
                          _createElementVNode("span", _hoisted_50, _toDisplayString(slot.badge), 1)
                        ]),
                        _createElementVNode("div", _hoisted_51, _toDisplayString(slot.icon), 1),
                        _createElementVNode("div", _hoisted_52, _toDisplayString(slot.title), 1),
                        _createElementVNode("div", _hoisted_53, _toDisplayString(slotText(slot)), 1)
                      ], 10, _hoisted_47))
                    }), 128))
                  ])
                ]))
              }), 128))
            ]),
            _: 1
          })
        ]),
        _: 1
      }),
      _createVNode(_component_v_card, {
        class: "sqfarm-card",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_item, null, {
            prepend: _withCtx(() => [
              _hoisted_54
            ]),
            default: _withCtx(() => [
              _createVNode(_component_v_card_title, null, {
                default: _withCtx(() => [
                  _createTextVNode("执行历史")
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_v_card_text, null, {
            default: _withCtx(() => [
              (!historyItems.value.length)
                ? (_openBlock(), _createElementBlock("div", _hoisted_55, "暂无执行记录"))
                : (_openBlock(), _createElementBlock("div", _hoisted_56, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(historyItems.value, (item) => {
                      return (_openBlock(), _createElementBlock("article", {
                        key: `${item.time}-${item.title}`,
                        class: "sqfarm-history-item"
                      }, [
                        _createElementVNode("div", _hoisted_57, [
                          _createElementVNode("strong", null, _toDisplayString(item.title), 1),
                          _createElementVNode("span", null, _toDisplayString(item.time), 1)
                        ]),
                        _createElementVNode("div", _hoisted_58, _toDisplayString((item.lines || []).join(' / ')), 1)
                      ]))
                    }), 128))
                  ]))
            ]),
            _: 1
          })
        ]),
        _: 1
      })
    ])
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-ed64d811"]]);

export { PageView as default };
