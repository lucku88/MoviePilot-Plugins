import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc, s as safeResponseMessage, i as isStrictSuccess, r as resolveGiftStatsFilters, c as createLatestRequestGuard, e as extractStatusPayload } from './_plugin-vue_export-helper-326068af.js';

const Page_vue_vue_type_style_index_0_scoped_36bf562f_lang = '';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,normalizeClass:_normalizeClass,withCtx:_withCtx,createTextVNode:_createTextVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,createStaticVNode:_createStaticVNode,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-36bf562f"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "siqi-page" };
const _hoisted_2 = { class: "siqi-topbar" };
const _hoisted_3 = { class: "siqi-topbar__left" };
const _hoisted_4 = { class: "siqi-topbar__icon" };
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-topbar__copy" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-topbar__title" }, "Vue-魔丸"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-topbar__sub" }, "搬砖、清理沙滩、兑换、赠送与炼造")
], -1));
const _hoisted_6 = { class: "siqi-topbar__right" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "d-none d-sm-inline" }, "刷新", -1));
const _hoisted_8 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "d-none d-sm-inline" }, "配置", -1));
const _hoisted_9 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "d-none d-sm-inline" }, "关闭", -1));
const _hoisted_10 = { class: "siqi-content" };
const _hoisted_11 = {
  key: 1,
  class: "page-skeleton"
};
const _hoisted_12 = { class: "overview-grid mb-3" };
const _hoisted_13 = /*#__PURE__*/_createStaticVNode("<div class=\"stat-card skeleton-card\" data-v-36bf562f><div class=\"sk sk-icon\" data-v-36bf562f></div><div class=\"sk-lines\" data-v-36bf562f><div class=\"sk sk-line short\" data-v-36bf562f></div><div class=\"sk sk-line\" data-v-36bf562f></div></div></div>", 1);
const _hoisted_14 = [
  _hoisted_13
];
const _hoisted_15 = { class: "primary-grid mb-3" };
const _hoisted_16 = { class: "siqi-card schedule-board skeleton-shell" };
const _hoisted_17 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-card-title" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "sk sk-title" })
], -1));
const _hoisted_18 = { class: "schedule-board-body" };
const _hoisted_19 = { class: "schedule-action-list" };
const _hoisted_20 = { class: "siqi-card exchange-card skeleton-shell exchange-skeleton" };
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-card-title" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "sk sk-title" })
], -1));
const _hoisted_22 = { class: "exchange-body" };
const _hoisted_23 = { class: "exchange-summary" };
const _hoisted_24 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sk sk-row" }, null, -1));
const _hoisted_25 = { class: "resource-grid mb-3" };
const _hoisted_26 = { class: "siqi-card inventory-card skeleton-shell inventory-skeleton" };
const _hoisted_27 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-card-title" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "sk sk-title" })
], -1));
const _hoisted_28 = { class: "inventory-body" };
const _hoisted_29 = { class: "inventory-grid" };
const _hoisted_30 = { class: "siqi-card workshop-card skeleton-shell recipe-skeleton" };
const _hoisted_31 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-card-title" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "sk sk-title" })
], -1));
const _hoisted_32 = { class: "workshop-body" };
const _hoisted_33 = { class: "recipe-grid" };
const _hoisted_34 = { class: "siqi-card history-card skeleton-shell history-skeleton" };
const _hoisted_35 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-card-title" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "sk sk-title" })
], -1));
const _hoisted_36 = { class: "history-body" };
const _hoisted_37 = { class: "stat-icon" };
const _hoisted_38 = { class: "stat-content" };
const _hoisted_39 = { class: "stat-title" };
const _hoisted_40 = { class: "stat-value" };
const _hoisted_41 = { class: "primary-grid mb-3" };
const _hoisted_42 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "card-subtitle" }, "搬砖与沙滩", -1));
const _hoisted_43 = { class: "schedule-action-list" };
const _hoisted_44 = { class: "neu-action-card neu-action-card--brick" };
const _hoisted_45 = { class: "neu-action-icon" };
const _hoisted_46 = { class: "neu-action-content" };
const _hoisted_47 = { class: "neu-action-heading" };
const _hoisted_48 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "neu-action-label" }, "搬砖", -1));
const _hoisted_49 = { class: "neu-action-desc" };
const _hoisted_50 = { class: "schedule-meta" };
const _hoisted_51 = { class: "neu-action-card neu-action-card--beach" };
const _hoisted_52 = { class: "neu-action-icon" };
const _hoisted_53 = { class: "neu-action-content" };
const _hoisted_54 = { class: "neu-action-heading" };
const _hoisted_55 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "neu-action-label" }, "沙滩", -1));
const _hoisted_56 = { class: "neu-action-desc" };
const _hoisted_57 = { class: "schedule-meta" };
const _hoisted_58 = { class: "exchange-summary" };
const _hoisted_59 = { class: "exchange-stat" };
const _hoisted_60 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "当前魔丸", -1));
const _hoisted_61 = { class: "exchange-stat" };
const _hoisted_62 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "单颗价值", -1));
const _hoisted_63 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("small", null, "魔力", -1));
const _hoisted_64 = { class: "exchange-stat" };
const _hoisted_65 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "最多兑换", -1));
const _hoisted_66 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("small", null, "颗", -1));
const _hoisted_67 = { class: "exchange-action-panel" };
const _hoisted_68 = {
  key: 0,
  class: "backend-note"
};
const _hoisted_69 = { class: "resource-grid mb-3" };
const _hoisted_70 = {
  key: 0,
  class: "empty-state"
};
const _hoisted_71 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("strong", null, "物品栏暂无内容", -1));
const _hoisted_72 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("small", null, "刷新后仍为空时，请以后端页面数据为准。", -1));
const _hoisted_73 = {
  key: 1,
  class: "inventory-grid"
};
const _hoisted_74 = ["disabled", "aria-label", "onClick"];
const _hoisted_75 = { class: "gift-item__icon" };
const _hoisted_76 = { class: "gift-item__main" };
const _hoisted_77 = {
  key: 0,
  class: "gift-item__state"
};
const _hoisted_78 = {
  key: 0,
  class: "empty-state"
};
const _hoisted_79 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("strong", null, "后端暂未返回配方", -1));
const _hoisted_80 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("small", null, "页面不会自行补造配方或推测可炼造状态。", -1));
const _hoisted_81 = {
  key: 1,
  class: "recipe-grid"
};
const _hoisted_82 = { class: "recipe-head" };
const _hoisted_83 = { class: "recipe-icon" };
const _hoisted_84 = { class: "recipe-title" };
const _hoisted_85 = { class: "recipe-ingredients" };
const _hoisted_86 = { class: "recipe-controls" };
const _hoisted_87 = {
  key: 0,
  class: "unavailable-reason"
};
const _hoisted_88 = {
  key: 0,
  class: "empty-state compact-empty"
};
const _hoisted_89 = {
  key: 1,
  class: "history-list"
};
const _hoisted_90 = { class: "history-detail" };
const _hoisted_91 = { class: "history-time" };
const _hoisted_92 = { class: "dialog-avatar" };
const _hoisted_93 = { class: "dialog-copy" };
const _hoisted_94 = { class: "dialog-avatar stats-avatar" };
const _hoisted_95 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "dialog-copy" }, [
  /*#__PURE__*/_createElementVNode("strong", null, "赠送统计"),
  /*#__PURE__*/_createElementVNode("small", null, "按后端记录查看赠出或收到的物品汇总。")
], -1));
const _hoisted_96 = { class: "stats-filters" };
const _hoisted_97 = {
  key: 1,
  class: "empty-state"
};
const _hoisted_98 = { class: "stats-applied-filter" };
const _hoisted_99 = { class: "gift-stats summary-grid" };
const _hoisted_100 = { class: "summary-stat" };
const _hoisted_101 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "总事件数", -1));
const _hoisted_102 = { class: "summary-stat" };
const _hoisted_103 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "总数量", -1));
const _hoisted_104 = {
  key: 0,
  class: "empty-state compact-empty"
};
const _hoisted_105 = {
  key: 1,
  class: "stats-columns"
};
const _hoisted_106 = { class: "stats-section" };
const _hoisted_107 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h3", null, "用户汇总", -1));
const _hoisted_108 = {
  key: 0,
  class: "stats-empty"
};
const _hoisted_109 = {
  key: 1,
  class: "stats-list"
};
const _hoisted_110 = { class: "stats-section" };
const _hoisted_111 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h3", null, "物品汇总", -1));
const _hoisted_112 = {
  key: 0,
  class: "stats-empty"
};
const _hoisted_113 = {
  key: 1,
  class: "stats-list"
};

const {computed,onBeforeUnmount,onMounted,reactive,ref,watch} = await importShared('vue');

const PLUGIN_ID = 'VuePill';

const _sfc_main = {
  __name: 'Page',
  props: { api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } },
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;




const apiGet = (path) => props.api.get(`/plugin/${PLUGIN_ID}${path}`);
const apiPost = (path, data = {}) => props.api.post(`/plugin/${PLUGIN_ID}${path}`, data);

const status = reactive({
  enabled: false,
  next_run_time: '',
  next_trigger_time: '',
  next_trigger_action: '',
  pill_status: {},
  history: [],
});
const message = reactive({ text: '', type: 'success' });
const initialLoading = ref(true);
const actionLoading = ref('');
const exchangeQuantity = ref('1');
const recipeQuantities = reactive({});
const showGiftDialog = ref(false);
const selectedGiftItem = ref(null);
const giftForm = reactive({ target_uid: '', quantity: '1' });
const giftConfirming = ref(false);
const giftConfirmationSnapshot = ref(null);
const giftLoading = ref(false);
const showGiftStatsDialog = ref(false);
const giftStatsDraftDirection = ref('out');
const giftStatsDraftRange = ref('30');
const giftStatsAppliedDirection = ref('');
const giftStatsAppliedRange = ref('');
const giftStats = ref(null);
const giftStatsLoading = ref(false);
const giftStatsError = ref('');
const statusRequestGuard = createLatestRequestGuard();
const actionRequestGuard = createLatestRequestGuard();
const giftRequestGuard = createLatestRequestGuard();
const giftStatsRequestGuard = createLatestRequestGuard();
let giftDialogToken = 0;
let messageTimer = null;

const pill = computed(() => status.pill_status || {});
const overview = computed(() => Array.isArray(pill.value.overview) ? pill.value.overview.slice(0, 4) : []);
const brick = computed(() => pill.value.brick || {});
const beach = computed(() => pill.value.beach || {});
const beachActionable = computed(() => (
  beach.value.ready === true
  || beach.value.can_collect === true
  || beach.value.has_trash === true
  || beach.value.collect_enabled === true
));
const brickStatusLabel = computed(() => {
  if (brick.value.ready === true) return '可以搬砖'
  const daily = Number(brick.value.daily_bricks || 0);
  const limit = Number(brick.value.daily_limit || 0);
  if (limit > 0 && daily >= limit) return '今日已完成'
  if (
    Object.prototype.hasOwnProperty.call(brick.value, 'available_count')
    && Number(brick.value.available_count || 0) <= 0
  ) return '暂无砖块'
  return '等待刷新'
});
const beachStatusLabel = computed(() => {
  if (beachActionable.value) return '可以清理'
  const statusText = String(beach.value.status_text || '');
  if (beach.value.next_ready_time || statusText.includes('冷却')) return '冷却中'
  return '等待刷新'
});

function compactScheduleTime(value) {
  const text = String(value ?? '');
  const matched = text.match(/^\d{4}-(\d{2})-(\d{2}) (\d{2}:\d{2}):\d{2}$/);
  return matched ? `${matched[1]}-${matched[2]} ${matched[3]}` : text
}

function applyStatusMeta(target, meta) {
  Object.assign(target, meta || {});
  return target
}

function buildScheduleSummary(state = {}) {
  if (!state.enabled) return { active: false, text: '自动运行未启用' }
  const nextTime = state.next_trigger_time || state.next_run_time;
  if (!nextTime) return { active: false, text: '等待识别下一次任务' }
  const action = state.next_trigger_action || '任务';
  return {
    active: true,
    text: `自动运行正常 · 下一项：${action} ${compactScheduleTime(nextTime)}`,
  }
}

const scheduleSummary = computed(() => buildScheduleSummary(status));

const exchange = computed(() => pill.value.exchange || {});
const inventoryItems = computed(() => {
  const inventory = pill.value.inventory || {};
  return Array.isArray(inventory.items) ? inventory.items : []
});

function normalizedInventoryCount(value) {
  const number = Number(value);
  return Number.isSafeInteger(number) && number >= 0 ? number : 0
}

function normalizedIngredientRequirement(value) {
  const number = Number(value);
  return Number.isSafeInteger(number) && number > 0 ? number : null
}

function buildInventoryCounts(items = []) {
  const counts = new Map();
  items.forEach((item) => {
    const name = String(item?.name || '').trim();
    if (!name) return
    const current = counts.get(name) || 0;
    const added = normalizedInventoryCount(item?.count);
    counts.set(name, Math.min(Number.MAX_SAFE_INTEGER, current + added));
  });
  return counts
}

const inventoryCounts = computed(() => buildInventoryCounts(inventoryItems.value));
const recipes = computed(() => Array.isArray(pill.value.recipes) ? pill.value.recipes : []);
const historyItems = computed(() => Array.isArray(status.history) ? status.history : []);
const isBusy = computed(() => !!actionLoading.value);
const writeActionsDisabled = computed(() => initialLoading.value || isBusy.value || giftLoading.value || showGiftDialog.value);

const exchangeReserveHint = computed(() => `后端保留 ${exchange.value.reserve} 个魔丸，实际兑换以后端校验为准。`);
const exchangeQuantityError = computed(() => quantityError(exchangeQuantity.value, Number(exchange.value.max_count || 0), '兑换'));

const giftMaxQuantity = computed(() => Math.min(normalizedInventoryCount(selectedGiftItem.value?.count), 500));
const normalizedGiftQuantity = computed(() => Number.parseInt(giftForm.quantity, 10) || 0);
const giftFormError = computed(() => {
  if (!selectedGiftItem.value) return '请选择要赠送的物品'
  if (!giftForm.target_uid.trim()) return '请填写接收方 UID'
  return quantityError(giftForm.quantity, giftMaxQuantity.value, '赠送')
});
const giftQuantityHint = computed(() => `前端提示范围 1-${giftMaxQuantity.value || 0}，最终以后端校验为准。`);

const giftStatsUsers = computed(() => Array.isArray(giftStats.value?.users) ? giftStats.value.users : []);
const giftStatsItems = computed(() => Array.isArray(giftStats.value?.items) ? giftStats.value.items : []);
const giftStatsEmpty = computed(() => Number(giftStats.value?.total_events || 0) <= 0 && !giftStatsUsers.value.length && !giftStatsItems.value.length);
const giftStatsAppliedDirectionLabel = computed(() => giftStatsAppliedDirection.value === 'in' ? '收到' : '赠出');
const giftStatsAppliedRangeLabel = computed(() => giftStatsAppliedRange.value === 'all' ? '全部' : '最近30天');

watch(() => exchange.value.max_count, (maxCount) => {
  const maximum = Number(maxCount || 0);
  if (maximum > 0 && Number(exchangeQuantity.value) > maximum) exchangeQuantity.value = String(maximum);
}, { immediate: true });

watch(recipes, (rows) => {
  rows.forEach((recipe) => {
    const key = recipe.craft_id;
    const maximum = Number(recipe.max_count || 0);
    const current = Number(recipeQuantities[key]);
    if (!Number.isInteger(current) || current < 1) recipeQuantities[key] = '1';
    else if (maximum > 0 && current > maximum) recipeQuantities[key] = String(maximum);
  });
}, { immediate: true });

watch(() => [giftForm.target_uid, giftForm.quantity], () => {
  giftConfirming.value = false;
  giftConfirmationSnapshot.value = null;
});

watch(() => [giftStatsDraftDirection.value, giftStatsDraftRange.value], ([direction, range]) => {
  if (direction === giftStatsAppliedDirection.value && range === giftStatsAppliedRange.value) return
  giftStatsRequestGuard.invalidate();
  giftStatsLoading.value = false;
  giftStats.value = null;
  giftStatsError.value = '';
});

function flash(text, type = 'success') {
  message.text = String(text || '');
  message.type = type;
  if (messageTimer) window.clearTimeout(messageTimer);
  messageTimer = window.setTimeout(() => {
    message.text = '';
    messageTimer = null;
  }, 3600);
}

function applyStatusPayload(payload = {}) {
  const update = extractStatusPayload(payload);
  if (!update) return false

  applyStatusMeta(status, update.statusMeta);
  status.pill_status = update.pillStatus;
  status.history = update.history;
  return true
}

async function loadStatus({ silent = false } = {}) {
  const requestId = statusRequestGuard.begin();
  try {
    const result = await apiGet('/status');
    if (!statusRequestGuard.isCurrent(requestId)) return false
    if (!result || typeof result !== 'object') throw new Error('状态响应无效')
    if (result.success === false) throw new Error(safeResponseMessage(result, '状态加载失败'))
    if (!applyStatusPayload(result)) throw new Error('状态响应无效')
    return true
  } catch (error) {
    if (!statusRequestGuard.isCurrent(requestId)) return false
    if (!silent) flash(safeResponseMessage(error, '状态加载失败'), 'error');
    return false
  } finally {
    if (statusRequestGuard.isCurrent(requestId)) initialLoading.value = false;
  }
}

async function runAction(key, request, fallbackMessage) {
  if (initialLoading.value || actionLoading.value) return null
  const requestId = actionRequestGuard.begin();
  actionLoading.value = key;
  try {
    const result = await request();
    if (!actionRequestGuard.isCurrent(requestId)) return null
    statusRequestGuard.invalidate();
    const statusApplied = applyStatusPayload(result);
    if (!isStrictSuccess(result)) {
      flash(safeResponseMessage(result, `${fallbackMessage}失败`), 'error');
      if (!statusApplied) await loadStatus({ silent: true });
      return null
    }
    flash(safeResponseMessage(result, fallbackMessage));
    await loadStatus({ silent: true });
    return result
  } catch (error) {
    if (!actionRequestGuard.isCurrent(requestId)) return null
    flash(safeResponseMessage(error, `${fallbackMessage}失败`), 'error');
    statusRequestGuard.invalidate();
    await loadStatus({ silent: true });
    return null
  } finally {
    if (actionRequestGuard.isCurrent(requestId)) actionLoading.value = '';
  }
}

function quantityError(value, maximum, actionName) {
  const quantity = Number(value);
  if (!Number.isInteger(quantity) || quantity < 1) return `${actionName}数量必须是正整数`
  if (maximum <= 0) return `当前暂不可${actionName}`
  if (quantity > maximum) return `${actionName}数量不能超过当前最多可${actionName}数量 ${maximum}`
  return ''
}

function overviewTone(item) {
  const label = String(item?.label || '');
  if (label.includes('兑换')) return 'green'
  if (label.includes('魔丸')) return 'blue'
  if (label.includes('搬砖')) return 'orange'
  return 'red'
}

function overviewIcon(item) {
  const label = String(item?.label || '');
  if (label.includes('兑换')) return 'mdi-cash-multiple'
  if (label.includes('魔丸')) return 'mdi-flask-round-bottom'
  if (label.includes('搬砖')) return 'mdi-wall'
  return 'mdi-star-four-points'
}

function ingredientCount(name) {
  return inventoryCounts.value.get(String(name || '').trim()) || 0
}

function ingredientEnough(name, required) {
  const requirement = normalizedIngredientRequirement(required);
  return requirement !== null && ingredientCount(name) >= requirement
}

function canGiftItem(item) {
  return !writeActionsDisabled.value && item?.giftable === true && normalizedInventoryCount(item?.count) > 0
}

function openGiftDialog(item) {
  if (initialLoading.value || isBusy.value || giftLoading.value || showGiftDialog.value) return
  if (!canGiftItem(item)) return
  giftRequestGuard.invalidate();
  giftDialogToken += 1;
  selectedGiftItem.value = item;
  giftForm.target_uid = '';
  giftForm.quantity = '1';
  giftConfirming.value = false;
  giftConfirmationSnapshot.value = null;
  showGiftDialog.value = true;
}

function closeGiftDialog() {
  if (giftLoading.value) return
  giftRequestGuard.invalidate();
  giftDialogToken += 1;
  showGiftDialog.value = false;
  giftConfirming.value = false;
  giftConfirmationSnapshot.value = null;
  selectedGiftItem.value = null;
}

function currentGiftSnapshot() {
  return {
    dialogToken: giftDialogToken,
    itemName: String(selectedGiftItem.value?.name || '').trim(),
    targetUid: String(giftForm.target_uid || '').trim(),
    quantity: normalizedGiftQuantity.value,
  }
}

function sameGiftSnapshot(left, right) {
  return !!left && !!right
    && left.dialogToken === right.dialogToken
    && left.itemName === right.itemName
    && left.targetUid === right.targetUid
    && left.quantity === right.quantity
}

function requestGiftConfirmation() {
  if (initialLoading.value || !showGiftDialog.value) return
  if (giftFormError.value) return flash(giftFormError.value, 'warning')
  giftConfirmationSnapshot.value = currentGiftSnapshot();
  giftConfirming.value = true;
}

async function submitGift() {
  if (giftLoading.value) return
  if (initialLoading.value || !showGiftDialog.value) return
  if (giftFormError.value) return flash(giftFormError.value, 'warning')
  const snapshot = currentGiftSnapshot();
  if (!giftConfirming.value || !sameGiftSnapshot(snapshot, giftConfirmationSnapshot.value)) {
    giftConfirming.value = false;
    giftConfirmationSnapshot.value = null;
    flash('赠送信息已变化，请重新确认', 'warning');
    return
  }

  const requestId = giftRequestGuard.begin();
  const requestDialogToken = snapshot.dialogToken;
  giftLoading.value = true;
  try {
    const result = await apiPost('/gift-item', {
      item_name: snapshot.itemName,
      target_uid: snapshot.targetUid,
      quantity: snapshot.quantity,
    });
    if (!giftRequestGuard.isCurrent(requestId)) return
    statusRequestGuard.invalidate();
    const statusApplied = applyStatusPayload(result);
    if (!isStrictSuccess(result)) {
      flash(safeResponseMessage(result, '赠送失败'), 'error');
      if (!statusApplied) await loadStatus({ silent: true });
      return
    }

    flash(safeResponseMessage(result, '赠送成功'));
    if (
      showGiftDialog.value
      && giftDialogToken === requestDialogToken
      && sameGiftSnapshot(currentGiftSnapshot(), snapshot)
    ) {
      showGiftDialog.value = false;
      giftConfirming.value = false;
      giftConfirmationSnapshot.value = null;
      selectedGiftItem.value = null;
      giftDialogToken += 1;
    }
    await loadStatus({ silent: true });
  } catch (error) {
    if (giftRequestGuard.isCurrent(requestId)) {
      flash(safeResponseMessage(error, '赠送失败'), 'error');
      statusRequestGuard.invalidate();
      await loadStatus({ silent: true });
    }
  } finally {
    if (giftRequestGuard.isCurrent(requestId)) giftLoading.value = false;
  }
}

async function openGiftStats() {
  if (initialLoading.value) return
  showGiftStatsDialog.value = true;
  await loadGiftStats();
}

async function loadGiftStats() {
  if (initialLoading.value) return
  const requestedFilters = resolveGiftStatsFilters(null, {
    direction: giftStatsDraftDirection.value,
    range: giftStatsDraftRange.value,
  });
  const requestId = giftStatsRequestGuard.begin();
  giftStatsLoading.value = true;
  giftStatsError.value = '';
  giftStats.value = null;
  giftStatsAppliedDirection.value = '';
  giftStatsAppliedRange.value = '';
  try {
    const result = await apiPost('/gift-stats', {
      direction: requestedFilters.direction,
      range: requestedFilters.range,
    });
    if (!giftStatsRequestGuard.isCurrent(requestId)) return
    if (!isStrictSuccess(result)) {
      giftStatsError.value = safeResponseMessage(result, '赠送统计加载失败');
      return
    }

    const appliedFilters = resolveGiftStatsFilters(result, requestedFilters);
    giftStatsAppliedDirection.value = appliedFilters.direction;
    giftStatsAppliedRange.value = appliedFilters.range;
    giftStatsDraftDirection.value = appliedFilters.direction;
    giftStatsDraftRange.value = appliedFilters.range;
    giftStats.value = {
      total_events: Number(result?.total_events || 0),
      total_quantity: Number(result?.total_quantity || 0),
      users: Array.isArray(result?.users) ? result.users : [],
      items: Array.isArray(result?.items) ? result.items : [],
    };
  } catch (error) {
    if (giftStatsRequestGuard.isCurrent(requestId)) {
      giftStatsError.value = safeResponseMessage(error, '赠送统计加载失败');
    }
  } finally {
    if (giftStatsRequestGuard.isCurrent(requestId)) giftStatsLoading.value = false;
  }
}

function rowEvents(row) {
  return Number(row?.total_events ?? row?.events ?? row?.count ?? 0)
}

function rowQuantity(row) {
  return Number(row?.total_quantity ?? row?.quantity ?? row?.count ?? 0)
}

function recipeQuantityError(recipe) {
  const maximum = Number(recipe.max_count || 0);
  if (maximum <= 0) return ''
  return quantityError(recipeQuantities[recipe.craft_id], maximum, '炼造')
}

function recipeUnavailableReason(recipe) {
  if (recipe.supported === false) return '后端标记该配方暂不支持。'
  if (Number(recipe.max_count || 0) <= 0) return ''
  if (recipe.status && !/材料不足|炼造上限为\s*0|最大可炼造数量为\s*0/.test(recipe.status)) return recipe.status
  return recipe.enabled !== true ? '后端标记该配方当前不可炼造。' : ''
}

function historyText(item) {
  return [item?.title, ...(Array.isArray(item?.lines) ? item.lines : [])].filter(Boolean).join(' / ') || '未提供执行内容'
}

function historyKey(item) {
  return `${item?.time || ''}-${item?.title || ''}-${historyText(item)}`
}

async function refreshData() { await runAction('refresh', () => apiPost('/refresh'), '状态已刷新'); }
async function moveBricks() { await runAction('brick', () => apiPost('/move-bricks'), '搬砖完成'); }
async function cleanBeach() { await runAction('beach', () => apiPost('/clean-beach'), '沙滩清理完成'); }

async function exchangePoints() {
  if (exchangeQuantityError.value) return flash(exchangeQuantityError.value, 'warning')
  await runAction('exchange', () => apiPost('/exchange-points', { quantity: Number(exchangeQuantity.value) }), '兑换完成');
}

async function craftRecipe(recipe) {
  const error = recipeQuantityError(recipe);
  if (error) return flash(error, 'warning')
  await runAction(
    `craft-${recipe.craft_id}`,
    () => apiPost('/craft-item', { recipe_id: Number(recipe.craft_id), quantity: Number(recipeQuantities[recipe.craft_id]) }),
    '炼造完成',
  );
}

async function craftMaxPill() {
  await runAction('craft-max', () => apiPost('/craft-max-pill'), '一键炼造完成');
}

onMounted(loadStatus);

onBeforeUnmount(() => {
  statusRequestGuard.invalidate();
  actionRequestGuard.invalidate();
  giftRequestGuard.invalidate();
  giftStatsRequestGuard.invalidate();
  if (messageTimer) window.clearTimeout(messageTimer);
});

return (_ctx, _cache) => {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_btn_group = _resolveComponent("v-btn-group");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_dialog = _resolveComponent("v-dialog");
  const _component_v_btn_toggle = _resolveComponent("v-btn-toggle");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("div", _hoisted_3, [
        _createElementVNode("div", _hoisted_4, [
          _createVNode(_component_v_icon, {
            icon: "mdi-flask-round-bottom",
            size: "24"
          })
        ]),
        _hoisted_5
      ]),
      _createElementVNode("div", _hoisted_6, [
        _createElementVNode("div", {
          class: _normalizeClass(["schedule-summary", { active: scheduleSummary.value.active }]),
          role: "status",
          "aria-live": "polite"
        }, [
          _createVNode(_component_v_icon, {
            icon: "mdi-timer-outline",
            size: "15"
          }),
          _createElementVNode("span", null, _toDisplayString(scheduleSummary.value.text), 1)
        ], 2),
        _createVNode(_component_v_btn_group, {
          variant: "tonal",
          density: "compact",
          class: "elevation-0"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_btn, {
              color: "success",
              size: "small",
              class: "px-0 px-sm-3",
              "min-width": "40",
              "aria-label": "刷新 Vue-魔丸状态",
              loading: actionLoading.value === 'refresh',
              disabled: writeActionsDisabled.value,
              onClick: refreshData
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-refresh",
                  size: "18",
                  class: "mr-sm-1"
                }),
                _hoisted_7
              ]),
              _: 1
            }, 8, ["loading", "disabled"]),
            _createVNode(_component_v_btn, {
              color: "success",
              size: "small",
              class: "px-0 px-sm-3",
              "min-width": "40",
              "aria-label": "打开 Vue-魔丸配置",
              disabled: isBusy.value,
              onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'config')))
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-cog",
                  size: "18",
                  class: "mr-sm-1"
                }),
                _hoisted_8
              ]),
              _: 1
            }, 8, ["disabled"]),
            _createVNode(_component_v_btn, {
              color: "success",
              size: "small",
              class: "px-0 px-sm-3",
              "min-width": "40",
              "aria-label": "关闭 Vue-魔丸",
              disabled: isBusy.value,
              onClick: _cache[1] || (_cache[1] = $event => (emit('close')))
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-close",
                  size: "18",
                  class: "mr-sm-1"
                }),
                _hoisted_9
              ]),
              _: 1
            }, 8, ["disabled"])
          ]),
          _: 1
        })
      ])
    ]),
    _createElementVNode("div", _hoisted_10, [
      (message.text)
        ? (_openBlock(), _createBlock(_component_v_alert, {
            key: 0,
            type: message.type,
            density: "compact",
            class: "siqi-toast",
            closable: "",
            "onClick:close": _cache[2] || (_cache[2] = $event => (message.text = ''))
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(message.text), 1)
            ]),
            _: 1
          }, 8, ["type"]))
        : _createCommentVNode("", true),
      (initialLoading.value)
        ? (_openBlock(), _createElementBlock("div", _hoisted_11, [
            _createElementVNode("div", _hoisted_12, [
              (_openBlock(), _createElementBlock(_Fragment, null, _renderList(4, (index) => {
                return _createElementVNode("div", {
                  key: `overview-skeleton-${index}`
                }, _hoisted_14)
              }), 64))
            ]),
            _createElementVNode("div", _hoisted_15, [
              _createElementVNode("div", _hoisted_16, [
                _hoisted_17,
                _createElementVNode("div", _hoisted_18, [
                  _createElementVNode("div", _hoisted_19, [
                    (_openBlock(), _createElementBlock(_Fragment, null, _renderList(2, (index) => {
                      return _createElementVNode("div", {
                        key: `schedule-skeleton-${index}`,
                        class: "sk sk-action"
                      })
                    }), 64))
                  ])
                ])
              ]),
              _createElementVNode("div", _hoisted_20, [
                _hoisted_21,
                _createElementVNode("div", _hoisted_22, [
                  _createElementVNode("div", _hoisted_23, [
                    (_openBlock(), _createElementBlock(_Fragment, null, _renderList(3, (index) => {
                      return _createElementVNode("div", {
                        key: `exchange-skeleton-${index}`,
                        class: "sk sk-exchange-stat"
                      })
                    }), 64))
                  ]),
                  _hoisted_24
                ])
              ])
            ]),
            _createElementVNode("div", _hoisted_25, [
              _createElementVNode("div", _hoisted_26, [
                _hoisted_27,
                _createElementVNode("div", _hoisted_28, [
                  _createElementVNode("div", _hoisted_29, [
                    (_openBlock(), _createElementBlock(_Fragment, null, _renderList(7, (index) => {
                      return _createElementVNode("div", {
                        key: `inventory-skeleton-${index}`,
                        class: "sk sk-inventory-item"
                      })
                    }), 64))
                  ])
                ])
              ]),
              _createElementVNode("div", _hoisted_30, [
                _hoisted_31,
                _createElementVNode("div", _hoisted_32, [
                  _createElementVNode("div", _hoisted_33, [
                    (_openBlock(), _createElementBlock(_Fragment, null, _renderList(3, (index) => {
                      return _createElementVNode("div", {
                        key: `recipe-skeleton-${index}`,
                        class: "sk sk-recipe-item"
                      })
                    }), 64))
                  ])
                ])
              ])
            ]),
            _createElementVNode("div", _hoisted_34, [
              _hoisted_35,
              _createElementVNode("div", _hoisted_36, [
                (_openBlock(), _createElementBlock(_Fragment, null, _renderList(3, (index) => {
                  return _createElementVNode("div", {
                    key: `history-skeleton-${index}`,
                    class: "sk sk-history-row"
                  })
                }), 64))
              ])
            ])
          ]))
        : (_openBlock(), _createElementBlock(_Fragment, { key: 2 }, [
            _createVNode(_component_v_row, {
              dense: "",
              class: "mb-3 overview-grid"
            }, {
              default: _withCtx(() => [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(overview.value, (item) => {
                  return (_openBlock(), _createBlock(_component_v_col, {
                    key: item.label,
                    cols: "6",
                    md: "3"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", {
                        class: _normalizeClass(["stat-card", `stat-${overviewTone(item)}`])
                      }, [
                        _createElementVNode("div", _hoisted_37, [
                          _createVNode(_component_v_icon, {
                            icon: overviewIcon(item),
                            size: "22"
                          }, null, 8, ["icon"])
                        ]),
                        _createElementVNode("div", _hoisted_38, [
                          _createElementVNode("div", _hoisted_39, _toDisplayString(item.label), 1),
                          _createElementVNode("div", _hoisted_40, _toDisplayString(item.value), 1)
                        ])
                      ], 2)
                    ]),
                    _: 2
                  }, 1024))
                }), 128))
              ]),
              _: 1
            }),
            _createElementVNode("div", _hoisted_41, [
              _createVNode(_component_v_card, {
                flat: "",
                class: "siqi-card schedule-board mb-3"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "siqi-card-title d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_icon, {
                        icon: "mdi-calendar-clock",
                        class: "mr-2",
                        color: "green"
                      }),
                      _createTextVNode("动态任务 "),
                      _hoisted_42
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_card_text, { class: "schedule-board-body" }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_43, [
                        _createElementVNode("div", _hoisted_44, [
                          _createElementVNode("div", _hoisted_45, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-wall",
                              size: "19"
                            })
                          ]),
                          _createElementVNode("div", _hoisted_46, [
                            _createElementVNode("div", _hoisted_47, [
                              _hoisted_48,
                              _createElementVNode("span", {
                                class: _normalizeClass(["schedule-status", {
                          'schedule-status--ready': brick.value.ready === true,
                          'schedule-status--done': brickStatusLabel.value === '今日已完成',
                        }])
                              }, _toDisplayString(brickStatusLabel.value), 3)
                            ]),
                            _createElementVNode("div", _hoisted_49, _toDisplayString(brick.value.status_text || '等待刷新搬砖状态'), 1),
                            _createElementVNode("div", _hoisted_50, [
                              _createElementVNode("span", null, "今日 " + _toDisplayString(brick.value.daily_bricks ?? 0) + "/" + _toDisplayString(brick.value.daily_limit ?? 50), 1),
                              _createElementVNode("span", null, "可搬 " + _toDisplayString(brick.value.available_count ?? 0), 1),
                              _createElementVNode("span", null, "重置 " + _toDisplayString(brick.value.next_reset_time || '等待刷新'), 1)
                            ])
                          ]),
                          _createVNode(_component_v_btn, {
                            color: "deep-orange",
                            size: "small",
                            class: "neu-btn schedule-action",
                            loading: actionLoading.value === 'brick',
                            disabled: writeActionsDisabled.value || brick.value.ready !== true,
                            onClick: moveBricks
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode(_toDisplayString(brick.value.ready === true ? '立即搬砖' : brickStatusLabel.value), 1)
                            ]),
                            _: 1
                          }, 8, ["loading", "disabled"])
                        ]),
                        _createElementVNode("div", _hoisted_51, [
                          _createElementVNode("div", _hoisted_52, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-beach",
                              size: "19"
                            })
                          ]),
                          _createElementVNode("div", _hoisted_53, [
                            _createElementVNode("div", _hoisted_54, [
                              _hoisted_55,
                              _createElementVNode("span", {
                                class: _normalizeClass(["schedule-status", {
                          'schedule-status--ready': beachActionable.value,
                          'schedule-status--cooldown': beachStatusLabel.value === '冷却中',
                        }])
                              }, _toDisplayString(beachStatusLabel.value), 3)
                            ]),
                            _createElementVNode("div", _hoisted_56, _toDisplayString(beach.value.status_text || '等待刷新沙滩状态'), 1),
                            _createElementVNode("div", _hoisted_57, [
                              _createElementVNode("span", null, _toDisplayString(beach.value.level_text || '等级待刷新'), 1),
                              _createElementVNode("span", null, _toDisplayString(beach.value.hnr_text || 'HNR 待刷新'), 1),
                              _createElementVNode("span", null, "可用 " + _toDisplayString(beach.value.next_ready_time || '等待刷新'), 1)
                            ])
                          ]),
                          _createVNode(_component_v_btn, {
                            color: "teal",
                            size: "small",
                            class: "neu-btn schedule-action",
                            loading: actionLoading.value === 'beach',
                            disabled: writeActionsDisabled.value || !beachActionable.value,
                            onClick: cleanBeach
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode(_toDisplayString(beachActionable.value ? '清理沙滩' : beachStatusLabel.value), 1)
                            ]),
                            _: 1
                          }, 8, ["loading", "disabled"])
                        ])
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }),
              _createVNode(_component_v_card, {
                flat: "",
                class: "siqi-card exchange-card mb-3"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "siqi-card-title siqi-card-title--exchange d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_icon, {
                        icon: "mdi-swap-horizontal-circle",
                        class: "mr-2",
                        color: "amber-darken-2"
                      }),
                      _createTextVNode("兑换魔力 ")
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_card_text, { class: "exchange-body" }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_58, [
                        _createElementVNode("div", _hoisted_59, [
                          _hoisted_60,
                          _createElementVNode("strong", null, _toDisplayString(exchange.value.magic_pills ?? 0), 1)
                        ]),
                        _createElementVNode("div", _hoisted_61, [
                          _hoisted_62,
                          _createElementVNode("strong", null, _toDisplayString(exchange.value.pill_price ?? 0), 1),
                          _hoisted_63
                        ]),
                        _createElementVNode("div", _hoisted_64, [
                          _hoisted_65,
                          _createElementVNode("strong", null, _toDisplayString(exchange.value.max_count ?? 0), 1),
                          _hoisted_66
                        ])
                      ]),
                      _createElementVNode("div", _hoisted_67, [
                        _createVNode(_component_v_text_field, {
                          modelValue: exchangeQuantity.value,
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((exchangeQuantity).value = $event)),
                          type: "number",
                          min: "1",
                          max: exchange.value.max_count,
                          label: "兑换数量",
                          variant: "outlined",
                          density: "compact",
                          "error-messages": exchangeQuantityError.value ? [exchangeQuantityError.value] : [],
                          hint: exchangeReserveHint.value,
                          "persistent-hint": ""
                        }, null, 8, ["modelValue", "max", "error-messages", "hint"]),
                        _createVNode(_component_v_btn, {
                          color: "amber-darken-2",
                          variant: "tonal",
                          loading: actionLoading.value === 'exchange',
                          disabled: writeActionsDisabled.value || exchange.value.enabled !== true || exchange.value.action_ready !== true || !!exchangeQuantityError.value,
                          onClick: exchangePoints
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode("兑换魔力")
                          ]),
                          _: 1
                        }, 8, ["loading", "disabled"])
                      ]),
                      (exchange.value.note)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_68, _toDisplayString(exchange.value.note), 1))
                        : _createCommentVNode("", true)
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _createElementVNode("div", _hoisted_69, [
              _createVNode(_component_v_card, {
                flat: "",
                class: "siqi-card inventory-card"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "siqi-card-title siqi-card-title--inventory d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_icon, {
                        icon: "mdi-package-variant-closed",
                        class: "mr-2",
                        color: "orange"
                      }),
                      _createTextVNode("物品栏 "),
                      _createVNode(_component_v_spacer),
                      _createVNode(_component_v_btn, {
                        color: "blue",
                        variant: "tonal",
                        "prepend-icon": "mdi-chart-box-outline",
                        "aria-label": "查看赠送统计",
                        loading: giftStatsLoading.value,
                        disabled: initialLoading.value || giftStatsLoading.value,
                        onClick: openGiftStats
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode("赠送统计")
                        ]),
                        _: 1
                      }, 8, ["loading", "disabled"])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_card_text, { class: "inventory-body" }, {
                    default: _withCtx(() => [
                      (!inventoryItems.value.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_70, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-package-variant",
                              size: "34"
                            }),
                            _hoisted_71,
                            _hoisted_72
                          ]))
                        : (_openBlock(), _createElementBlock("div", _hoisted_73, [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(inventoryItems.value, (item) => {
                              return (_openBlock(), _createElementBlock("button", {
                                key: item.name,
                                type: "button",
                                class: _normalizeClass(["gift-item", {
                  'gift-item--available': canGiftItem(item),
                  'gift-item--static': !canGiftItem(item),
                }]),
                                disabled: !canGiftItem(item),
                                "aria-label": canGiftItem(item) ? `赠送 ${item.name}` : `${item.name} 当前不可赠送`,
                                onClick: $event => (openGiftDialog(item))
                              }, [
                                _createElementVNode("span", _hoisted_75, _toDisplayString(item.icon || '📦'), 1),
                                _createElementVNode("span", _hoisted_76, [
                                  _createElementVNode("strong", null, _toDisplayString(item.name), 1),
                                  _createElementVNode("small", null, "数量 " + _toDisplayString(item.count ?? 0), 1)
                                ]),
                                (canGiftItem(item))
                                  ? (_openBlock(), _createElementBlock("span", _hoisted_77, "赠送"))
                                  : _createCommentVNode("", true)
                              ], 10, _hoisted_74))
                            }), 128))
                          ]))
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }),
              _createVNode(_component_v_card, {
                flat: "",
                class: "siqi-card workshop-card"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "siqi-card-title siqi-card-title--workshop d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_icon, {
                        icon: "mdi-anvil",
                        class: "mr-2",
                        color: "cyan-darken-1"
                      }),
                      _createTextVNode("炼造工坊 "),
                      _createVNode(_component_v_spacer),
                      _createVNode(_component_v_btn, {
                        color: "cyan-darken-1",
                        variant: "tonal",
                        "prepend-icon": "mdi-flask-round-bottom",
                        loading: actionLoading.value === 'craft-max',
                        disabled: writeActionsDisabled.value,
                        onClick: craftMaxPill
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode("一键炼造魔丸")
                        ]),
                        _: 1
                      }, 8, ["loading", "disabled"])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_card_text, { class: "workshop-body" }, {
                    default: _withCtx(() => [
                      (!recipes.value.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_78, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-flask-empty-outline",
                              size: "34"
                            }),
                            _hoisted_79,
                            _hoisted_80
                          ]))
                        : (_openBlock(), _createElementBlock("div", _hoisted_81, [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(recipes.value, (recipe) => {
                              return (_openBlock(), _createElementBlock("article", {
                                key: recipe.craft_id,
                                class: _normalizeClass(["recipe-card", { 'recipe-card--disabled': recipe.enabled !== true }])
                              }, [
                                _createElementVNode("div", _hoisted_82, [
                                  _createElementVNode("span", _hoisted_83, _toDisplayString(recipe.icon || '⚒️'), 1),
                                  _createElementVNode("div", _hoisted_84, [
                                    _createElementVNode("strong", null, _toDisplayString(recipe.output_item || recipe.name || recipe.title), 1),
                                    _createElementVNode("small", null, [
                                      _createTextVNode(" 配方 ID " + _toDisplayString(recipe.craft_id) + " ", 1),
                                      (Number(recipe.max_count || 0) > 0)
                                        ? (_openBlock(), _createElementBlock(_Fragment, { key: 0 }, [
                                            _createTextVNode(" · 最多 " + _toDisplayString(recipe.max_count), 1)
                                          ], 64))
                                        : _createCommentVNode("", true)
                                    ])
                                  ])
                                ]),
                                _createElementVNode("div", _hoisted_85, [
                                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(recipe.ingredients || {}, (required, name) => {
                                    return (_openBlock(), _createElementBlock("span", {
                                      key: `${recipe.craft_id}-${name}`,
                                      class: _normalizeClass({ 'ingredient-ready': ingredientEnough(name, required) })
                                    }, _toDisplayString(name) + " " + _toDisplayString(ingredientCount(name)) + "/" + _toDisplayString(required), 3))
                                  }), 128))
                                ]),
                                _createElementVNode("div", _hoisted_86, [
                                  _createVNode(_component_v_text_field, {
                                    modelValue: recipeQuantities[recipe.craft_id],
                                    "onUpdate:modelValue": $event => ((recipeQuantities[recipe.craft_id]) = $event),
                                    type: "number",
                                    min: "1",
                                    max: recipe.max_count,
                                    label: "数量",
                                    variant: "outlined",
                                    density: "compact",
                                    "hide-details": "auto",
                                    "error-messages": recipeQuantityError(recipe) ? [recipeQuantityError(recipe)] : [],
                                    disabled: writeActionsDisabled.value || recipe.enabled !== true || Number(recipe.max_count || 0) <= 0
                                  }, null, 8, ["modelValue", "onUpdate:modelValue", "max", "error-messages", "disabled"]),
                                  _createVNode(_component_v_btn, {
                                    color: "cyan-darken-1",
                                    variant: "tonal",
                                    loading: actionLoading.value === `craft-${recipe.craft_id}`,
                                    disabled: writeActionsDisabled.value || recipe.enabled !== true || Number(recipe.max_count || 0) <= 0 || !!recipeQuantityError(recipe),
                                    onClick: $event => (craftRecipe(recipe))
                                  }, {
                                    default: _withCtx(() => [
                                      _createTextVNode("炼造")
                                    ]),
                                    _: 2
                                  }, 1032, ["loading", "disabled", "onClick"])
                                ]),
                                (recipeUnavailableReason(recipe))
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_87, _toDisplayString(recipeUnavailableReason(recipe)), 1))
                                  : _createCommentVNode("", true)
                              ], 2))
                            }), 128))
                          ]))
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _createVNode(_component_v_card, {
              flat: "",
              class: "siqi-card history-card"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "siqi-card-title siqi-card-title--logs d-flex align-center" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_icon, {
                      icon: "mdi-history",
                      class: "mr-2",
                      color: "blue"
                    }),
                    _createTextVNode("执行历史 ")
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card_text, { class: "history-body" }, {
                  default: _withCtx(() => [
                    (!historyItems.value.length)
                      ? (_openBlock(), _createElementBlock("div", _hoisted_88, "暂无执行记录"))
                      : (_openBlock(), _createElementBlock("div", _hoisted_89, [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(historyItems.value, (item) => {
                            return (_openBlock(), _createElementBlock("div", {
                              key: historyKey(item),
                              class: "history-item"
                            }, [
                              _createElementVNode("span", _hoisted_90, _toDisplayString(historyText(item)), 1),
                              _createElementVNode("time", _hoisted_91, _toDisplayString(item.time || ''), 1)
                            ]))
                          }), 128))
                        ]))
                  ]),
                  _: 1
                })
              ]),
              _: 1
            })
          ], 64))
    ]),
    _createVNode(_component_v_dialog, {
      modelValue: showGiftDialog.value,
      "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((showGiftDialog).value = $event)),
      "max-width": "560",
      persistent: giftLoading.value
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, {
          flat: "",
          class: "siqi-dialog gift-dialog"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "dialog-header" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_92, _toDisplayString(selectedGiftItem.value?.icon || '🎁'), 1),
                _createElementVNode("div", _hoisted_93, [
                  _createElementVNode("strong", null, "赠送 " + _toDisplayString(selectedGiftItem.value?.name || '物品'), 1),
                  _createElementVNode("small", null, "当前库存 " + _toDisplayString(selectedGiftItem.value?.count ?? 0) + "，网站单次最多接受 500 个。", 1)
                ]),
                _createVNode(_component_v_btn, {
                  icon: "",
                  variant: "text",
                  "aria-label": "取消赠送并关闭对话框",
                  disabled: giftLoading.value,
                  onClick: closeGiftDialog
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_icon, { icon: "mdi-close" })
                  ]),
                  _: 1
                }, 8, ["disabled"])
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "dialog-body" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_text_field, {
                  modelValue: giftForm.target_uid,
                  "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((giftForm.target_uid) = $event)),
                  label: "接收方 UID",
                  variant: "outlined",
                  autocomplete: "off",
                  disabled: giftLoading.value
                }, null, 8, ["modelValue", "disabled"]),
                _createVNode(_component_v_text_field, {
                  modelValue: giftForm.quantity,
                  "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((giftForm.quantity) = $event)),
                  type: "number",
                  min: "1",
                  max: giftMaxQuantity.value,
                  label: "赠送数量",
                  variant: "outlined",
                  hint: giftQuantityHint.value,
                  "persistent-hint": "",
                  "error-messages": giftFormError.value ? [giftFormError.value] : [],
                  disabled: giftLoading.value
                }, null, 8, ["modelValue", "max", "hint", "error-messages", "disabled"]),
                (giftConfirming.value)
                  ? (_openBlock(), _createBlock(_component_v_alert, {
                      key: 0,
                      type: "warning",
                      variant: "tonal",
                      density: "compact",
                      class: "confirm-alert"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(" 再次确认：向 UID " + _toDisplayString(giftForm.target_uid.trim()) + " 赠送 " + _toDisplayString(selectedGiftItem.value?.name) + " ×" + _toDisplayString(normalizedGiftQuantity.value) + "。提交后由后端进行最终校验。 ", 1)
                      ]),
                      _: 1
                    }))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "dialog-actions" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_btn, {
                  variant: "tonal",
                  disabled: giftLoading.value,
                  onClick: closeGiftDialog
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("取消")
                  ]),
                  _: 1
                }, 8, ["disabled"]),
                _createVNode(_component_v_spacer),
                (giftConfirming.value)
                  ? (_openBlock(), _createBlock(_component_v_btn, {
                      key: 0,
                      variant: "text",
                      disabled: giftLoading.value,
                      onClick: _cache[6] || (_cache[6] = $event => (giftConfirming.value = false))
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode("返回修改")
                      ]),
                      _: 1
                    }, 8, ["disabled"]))
                  : _createCommentVNode("", true),
                (!giftConfirming.value)
                  ? (_openBlock(), _createBlock(_component_v_btn, {
                      key: 1,
                      color: "orange-darken-1",
                      variant: "tonal",
                      disabled: giftLoading.value || !!giftFormError.value,
                      onClick: requestGiftConfirmation
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode("确认赠送")
                      ]),
                      _: 1
                    }, 8, ["disabled"]))
                  : (_openBlock(), _createBlock(_component_v_btn, {
                      key: 2,
                      color: "error",
                      variant: "tonal",
                      loading: giftLoading.value,
                      disabled: giftLoading.value || !!giftFormError.value,
                      onClick: submitGift
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode("再次确认并赠送")
                      ]),
                      _: 1
                    }, 8, ["loading", "disabled"]))
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue", "persistent"]),
    _createVNode(_component_v_dialog, {
      modelValue: showGiftStatsDialog.value,
      "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((showGiftStatsDialog).value = $event)),
      "max-width": "820",
      scrollable: ""
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, {
          flat: "",
          class: "siqi-dialog stats-dialog"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "dialog-header" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_94, [
                  _createVNode(_component_v_icon, { icon: "mdi-chart-box-outline" })
                ]),
                _hoisted_95,
                _createVNode(_component_v_btn, {
                  icon: "",
                  variant: "text",
                  "aria-label": "关闭赠送统计",
                  disabled: giftStatsLoading.value,
                  onClick: _cache[8] || (_cache[8] = $event => (showGiftStatsDialog.value = false))
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_icon, { icon: "mdi-close" })
                  ]),
                  _: 1
                }, 8, ["disabled"])
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "stats-dialog-body" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_96, [
                  _createVNode(_component_v_btn_toggle, {
                    modelValue: giftStatsDraftDirection.value,
                    "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((giftStatsDraftDirection).value = $event)),
                    mandatory: "",
                    disabled: giftStatsLoading.value,
                    color: "blue",
                    variant: "tonal",
                    divided: ""
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_btn, { value: "out" }, {
                        default: _withCtx(() => [
                          _createTextVNode("赠出")
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_btn, { value: "in" }, {
                        default: _withCtx(() => [
                          _createTextVNode("收到")
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  }, 8, ["modelValue", "disabled"]),
                  _createVNode(_component_v_btn_toggle, {
                    modelValue: giftStatsDraftRange.value,
                    "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((giftStatsDraftRange).value = $event)),
                    mandatory: "",
                    disabled: giftStatsLoading.value,
                    color: "blue",
                    variant: "tonal",
                    divided: ""
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_btn, { value: "30" }, {
                        default: _withCtx(() => [
                          _createTextVNode("最近30天")
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_btn, { value: "all" }, {
                        default: _withCtx(() => [
                          _createTextVNode("全部")
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  }, 8, ["modelValue", "disabled"]),
                  _createVNode(_component_v_btn, {
                    color: "blue",
                    variant: "tonal",
                    loading: giftStatsLoading.value,
                    disabled: initialLoading.value || giftStatsLoading.value,
                    onClick: loadGiftStats
                  }, {
                    default: _withCtx(() => [
                      _createTextVNode("查询统计")
                    ]),
                    _: 1
                  }, 8, ["loading", "disabled"])
                ]),
                (giftStatsError.value)
                  ? (_openBlock(), _createBlock(_component_v_alert, {
                      key: 0,
                      type: "error",
                      variant: "tonal",
                      density: "compact",
                      class: "mb-3"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(giftStatsError.value), 1)
                      ]),
                      _: 1
                    }))
                  : (giftStatsLoading.value && !giftStats.value)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_97, "正在加载赠送统计..."))
                    : (giftStats.value)
                      ? (_openBlock(), _createElementBlock(_Fragment, { key: 2 }, [
                          _createElementVNode("div", _hoisted_98, "当前数据：" + _toDisplayString(giftStatsAppliedDirectionLabel.value) + " · " + _toDisplayString(giftStatsAppliedRangeLabel.value), 1),
                          _createElementVNode("div", _hoisted_99, [
                            _createElementVNode("div", _hoisted_100, [
                              _hoisted_101,
                              _createElementVNode("strong", null, _toDisplayString(giftStats.value.total_events ?? 0), 1)
                            ]),
                            _createElementVNode("div", _hoisted_102, [
                              _hoisted_103,
                              _createElementVNode("strong", null, _toDisplayString(giftStats.value.total_quantity ?? 0), 1)
                            ])
                          ]),
                          (giftStatsEmpty.value)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_104, "当前筛选范围暂无赠送记录"))
                            : (_openBlock(), _createElementBlock("div", _hoisted_105, [
                                _createElementVNode("section", _hoisted_106, [
                                  _hoisted_107,
                                  (!giftStatsUsers.value.length)
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_108, "暂无用户数据"))
                                    : (_openBlock(), _createElementBlock("div", _hoisted_109, [
                                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(giftStatsUsers.value, (row) => {
                                          return (_openBlock(), _createElementBlock("div", {
                                            key: row.uid || row.name || row.display_name,
                                            class: "stats-row"
                                          }, [
                                            _createElementVNode("span", null, _toDisplayString(row.display_name || row.name || row.uid || '未知用户'), 1),
                                            _createElementVNode("small", null, _toDisplayString(rowEvents(row)) + " 次 · " + _toDisplayString(rowQuantity(row)) + " 个", 1)
                                          ]))
                                        }), 128))
                                      ]))
                                ]),
                                _createElementVNode("section", _hoisted_110, [
                                  _hoisted_111,
                                  (!giftStatsItems.value.length)
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_112, "暂无物品数据"))
                                    : (_openBlock(), _createElementBlock("div", _hoisted_113, [
                                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(giftStatsItems.value, (row) => {
                                          return (_openBlock(), _createElementBlock("div", {
                                            key: row.item_name || row.name,
                                            class: "stats-row"
                                          }, [
                                            _createElementVNode("span", null, _toDisplayString(row.item_name || row.name || '未知物品'), 1),
                                            _createElementVNode("small", null, _toDisplayString(rowEvents(row)) + " 次 · " + _toDisplayString(rowQuantity(row)) + " 个", 1)
                                          ]))
                                        }), 128))
                                      ]))
                                ])
                              ]))
                        ], 64))
                      : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_actions, { class: "dialog-actions" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_spacer),
                _createVNode(_component_v_btn, {
                  variant: "tonal",
                  disabled: giftStatsLoading.value,
                  onClick: _cache[11] || (_cache[11] = $event => (showGiftStatsDialog.value = false))
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("关闭")
                  ]),
                  _: 1
                }, 8, ["disabled"])
              ]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    }, 8, ["modelValue"])
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-36bf562f"]]);

export { PageView as default };
