import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc, s as safeResponseMessage, i as isStrictSuccess, r as resolveGiftStatsFilters, c as createLatestRequestGuard, e as extractStatusPayload } from './_plugin-vue_export-helper-66d70fe2.js';

const Page_vue_vue_type_style_index_0_scoped_8524c21b_lang = '';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,withCtx:_withCtx,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-8524c21b"),n=n(),_popScopeId(),n);
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
const _hoisted_12 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "stat-card skeleton-card" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "sk sk-icon" }),
  /*#__PURE__*/_createElementVNode("div", { class: "sk-lines" }, [
    /*#__PURE__*/_createElementVNode("div", { class: "sk sk-line short" }),
    /*#__PURE__*/_createElementVNode("div", { class: "sk sk-line" })
  ])
], -1));
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sk sk-title" }, null, -1));
const _hoisted_14 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sk sk-title" }, null, -1));
const _hoisted_15 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sk sk-row" }, null, -1));
const _hoisted_16 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sk sk-row" }, null, -1));
const _hoisted_17 = [
  _hoisted_14,
  _hoisted_15,
  _hoisted_16
];
const _hoisted_18 = { class: "stat-icon" };
const _hoisted_19 = { class: "stat-content" };
const _hoisted_20 = { class: "stat-title" };
const _hoisted_21 = { class: "stat-value" };
const _hoisted_22 = { class: "primary-grid mb-3" };
const _hoisted_23 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "card-subtitle" }, "搬砖与沙滩", -1));
const _hoisted_24 = { class: "schedule-action-list" };
const _hoisted_25 = { class: "neu-action-card neu-action-card--brick" };
const _hoisted_26 = { class: "neu-action-icon" };
const _hoisted_27 = { class: "neu-action-content" };
const _hoisted_28 = { class: "neu-action-heading" };
const _hoisted_29 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "neu-action-label" }, "搬砖", -1));
const _hoisted_30 = { class: "neu-action-desc" };
const _hoisted_31 = { class: "schedule-meta" };
const _hoisted_32 = { class: "neu-action-card neu-action-card--beach" };
const _hoisted_33 = { class: "neu-action-icon" };
const _hoisted_34 = { class: "neu-action-content" };
const _hoisted_35 = { class: "neu-action-heading" };
const _hoisted_36 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "neu-action-label" }, "沙滩", -1));
const _hoisted_37 = { class: "neu-action-desc" };
const _hoisted_38 = { class: "schedule-meta" };
const _hoisted_39 = { class: "exchange-summary" };
const _hoisted_40 = { class: "exchange-stat" };
const _hoisted_41 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "当前魔丸", -1));
const _hoisted_42 = { class: "exchange-stat" };
const _hoisted_43 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "单颗价值", -1));
const _hoisted_44 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("small", null, "魔力", -1));
const _hoisted_45 = { class: "exchange-stat" };
const _hoisted_46 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "后端上限", -1));
const _hoisted_47 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("small", null, "颗", -1));
const _hoisted_48 = { class: "exchange-action-panel" };
const _hoisted_49 = { class: "resource-grid mb-3" };
const _hoisted_50 = { class: "inventory-title-actions" };
const _hoisted_51 = {
  key: 0,
  class: "empty-state"
};
const _hoisted_52 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("strong", null, "物品栏暂无内容", -1));
const _hoisted_53 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("small", null, "刷新后仍为空时，请以后端页面数据为准。", -1));
const _hoisted_54 = {
  key: 1,
  class: "inventory-grid"
};
const _hoisted_55 = ["disabled", "aria-label", "onClick"];
const _hoisted_56 = { class: "gift-item__icon" };
const _hoisted_57 = { class: "gift-item__main" };
const _hoisted_58 = { class: "gift-item__state" };
const _hoisted_59 = {
  key: 0,
  class: "empty-state"
};
const _hoisted_60 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("strong", null, "后端暂未返回配方", -1));
const _hoisted_61 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("small", null, "页面不会自行补造配方或推测可炼造状态。", -1));
const _hoisted_62 = {
  key: 1,
  class: "recipe-grid"
};
const _hoisted_63 = { class: "recipe-head" };
const _hoisted_64 = { class: "recipe-icon" };
const _hoisted_65 = { class: "recipe-title" };
const _hoisted_66 = { class: "recipe-ingredients" };
const _hoisted_67 = { class: "recipe-controls" };
const _hoisted_68 = {
  key: 0,
  class: "unavailable-reason"
};
const _hoisted_69 = {
  key: 0,
  class: "empty-state compact-empty"
};
const _hoisted_70 = {
  key: 1,
  class: "history-list"
};
const _hoisted_71 = { class: "history-detail" };
const _hoisted_72 = { class: "history-time" };
const _hoisted_73 = { class: "dialog-avatar" };
const _hoisted_74 = { class: "dialog-copy" };
const _hoisted_75 = { class: "dialog-avatar batch-gift-avatar" };
const _hoisted_76 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "dialog-copy" }, [
  /*#__PURE__*/_createElementVNode("strong", null, "批量赠送"),
  /*#__PURE__*/_createElementVNode("small", null, "勾选多种物品，共用一个接收方 UID；每种物品单次最多赠送 500 个。")
], -1));
const _hoisted_77 = { class: "batch-gift-list" };
const _hoisted_78 = { class: "batch-gift-item" };
const _hoisted_79 = { class: "batch-gift-item__icon" };
const _hoisted_80 = { class: "batch-gift-item__copy" };
const _hoisted_81 = { class: "dialog-avatar stats-avatar" };
const _hoisted_82 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "dialog-copy" }, [
  /*#__PURE__*/_createElementVNode("strong", null, "赠送统计"),
  /*#__PURE__*/_createElementVNode("small", null, "按后端记录查看赠出或收到的物品汇总。")
], -1));
const _hoisted_83 = { class: "stats-filters" };
const _hoisted_84 = {
  key: 1,
  class: "empty-state"
};
const _hoisted_85 = { class: "stats-applied-filter" };
const _hoisted_86 = { class: "gift-stats summary-grid" };
const _hoisted_87 = { class: "summary-stat" };
const _hoisted_88 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "总事件数", -1));
const _hoisted_89 = { class: "summary-stat" };
const _hoisted_90 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "总数量", -1));
const _hoisted_91 = {
  key: 0,
  class: "empty-state compact-empty"
};
const _hoisted_92 = {
  key: 1,
  class: "stats-columns"
};
const _hoisted_93 = { class: "stats-section" };
const _hoisted_94 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h3", null, "用户汇总", -1));
const _hoisted_95 = {
  key: 0,
  class: "stats-empty"
};
const _hoisted_96 = {
  key: 1,
  class: "stats-list"
};
const _hoisted_97 = { class: "stats-section" };
const _hoisted_98 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h3", null, "物品汇总", -1));
const _hoisted_99 = {
  key: 0,
  class: "stats-empty"
};
const _hoisted_100 = {
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

const status = reactive({ pill_status: {}, history: [] });
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
const showBatchGiftDialog = ref(false);
const batchGiftForm = reactive({ target_uid: '' });
const batchGiftRows = ref([]);
const batchGiftConfirming = ref(false);
const batchGiftConfirmationSnapshot = ref(null);
const batchGiftLoading = ref(false);
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
const batchGiftRequestGuard = createLatestRequestGuard();
const giftStatsRequestGuard = createLatestRequestGuard();
const batchGiftPendingRequests = new Map();
let giftDialogToken = 0;
let batchGiftDialogToken = 0;
let batchGiftRequestSequence = 0;
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
const exchange = computed(() => pill.value.exchange || {});
const inventoryItems = computed(() => {
  const inventory = pill.value.inventory || {};
  return Array.isArray(inventory.items) ? inventory.items : []
});
const recipes = computed(() => Array.isArray(pill.value.recipes) ? pill.value.recipes : []);
const historyItems = computed(() => Array.isArray(status.history) ? status.history : []);
const isBusy = computed(() => !!actionLoading.value);
const writeActionsDisabled = computed(() => (
  initialLoading.value
  || isBusy.value
  || giftLoading.value
  || batchGiftLoading.value
  || showGiftDialog.value
  || showBatchGiftDialog.value
));

const exchangeQuantityError = computed(() => quantityError(exchangeQuantity.value, Number(exchange.value.max_count || 0), '兑换'));

const giftMaxQuantity = computed(() => Math.min(Math.max(Number(selectedGiftItem.value?.count || 0), 0), 500));
const normalizedGiftQuantity = computed(() => Number.parseInt(giftForm.quantity, 10) || 0);
const giftFormError = computed(() => {
  if (!selectedGiftItem.value) return '请选择要赠送的物品'
  if (!giftForm.target_uid.trim()) return '请填写接收方 UID'
  return quantityError(giftForm.quantity, giftMaxQuantity.value, '赠送')
});
const giftQuantityHint = computed(() => `前端提示范围 1-${giftMaxQuantity.value || 0}，最终以后端校验为准。`);

const batchGiftableItems = computed(() => inventoryItems.value.filter((item) => (
  item?.giftable === true && Number(item?.count || 0) > 0
)));
const batchGiftSelectedRows = computed(() => batchGiftRows.value.filter((item) => item.selected));
const batchGiftSummary = computed(() => batchGiftSelectedRows.value
  .map((item) => `${item.name}×${Number.parseInt(item.quantity, 10) || 0}`)
  .join('、'));
const batchGiftFormError = computed(() => {
  if (!batchGiftForm.target_uid.trim()) return '请填写接收方 UID'
  if (!batchGiftSelectedRows.value.length) return '请至少选择一种物品'
  for (const item of batchGiftSelectedRows.value) {
    const error = batchGiftRowError(item);
    if (error) return `${item.name}：${error}`
  }
  return ''
});

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

watch(
  () => [
    batchGiftForm.target_uid,
    ...batchGiftRows.value.flatMap((item) => [item.selected, item.quantity]),
  ],
  () => {
    batchGiftConfirming.value = false;
    batchGiftConfirmationSnapshot.value = null;
  },
);

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

  status.pill_status = update.pillStatus;
  if (update.history) status.history = update.history;
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
  if (maximum <= 0) return `后端返回的${actionName}上限为 0`
  if (quantity > maximum) return `${actionName}数量不能超过后端上限 ${maximum}`
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

function canGiftItem(item) {
  return !writeActionsDisabled.value && item?.giftable === true && Number(item?.count || 0) > 0
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

function batchGiftRowError(item) {
  const maximum = Math.min(Math.max(Number(item?.maxQuantity || item?.count || 0), 0), 500);
  return quantityError(item?.quantity, maximum, '赠送')
}

function openBatchGiftDialog() {
  if (
    initialLoading.value
    || isBusy.value
    || giftLoading.value
    || batchGiftLoading.value
    || showGiftDialog.value
    || showBatchGiftDialog.value
  ) return
  if (!batchGiftableItems.value.length) {
    flash('当前没有可批量赠送的物品', 'warning');
    return
  }

  batchGiftRequestGuard.invalidate();
  batchGiftDialogToken += 1;
  batchGiftForm.target_uid = '';
  batchGiftRows.value = batchGiftableItems.value.map((item) => ({
    name: String(item.name || '').trim(),
    icon: item.icon || '📦',
    count: Math.max(Number(item.count || 0), 0),
    maxQuantity: Math.min(Math.max(Number(item.count || 0), 0), 500),
    selected: false,
    quantity: '1',
  }));
  batchGiftConfirming.value = false;
  batchGiftConfirmationSnapshot.value = null;
  showBatchGiftDialog.value = true;
}

function resetBatchGiftDialog() {
  showBatchGiftDialog.value = false;
  batchGiftConfirming.value = false;
  batchGiftConfirmationSnapshot.value = null;
  batchGiftRows.value = [];
  batchGiftForm.target_uid = '';
  batchGiftDialogToken += 1;
}

function closeBatchGiftDialog() {
  if (batchGiftLoading.value) return
  batchGiftRequestGuard.invalidate();
  resetBatchGiftDialog();
}

function currentBatchGiftSnapshot() {
  return {
    dialogToken: batchGiftDialogToken,
    targetUid: String(batchGiftForm.target_uid || '').trim(),
    items: batchGiftSelectedRows.value.map((item) => ({
      item_name: item.name,
      quantity: Number.parseInt(item.quantity, 10) || 0,
    })),
  }
}

function sameBatchGiftSnapshot(left, right) {
  if (!left || !right) return false
  if (left.dialogToken !== right.dialogToken || left.targetUid !== right.targetUid) return false
  if (!Array.isArray(left.items) || !Array.isArray(right.items) || left.items.length !== right.items.length) return false
  return left.items.every((item, index) => (
    item.item_name === right.items[index]?.item_name
    && item.quantity === right.items[index]?.quantity
  ))
}

function requestBatchGiftConfirmation() {
  if (initialLoading.value || !showBatchGiftDialog.value) return
  if (batchGiftFormError.value) return flash(batchGiftFormError.value, 'warning')
  const snapshot = currentBatchGiftSnapshot();
  const contentKey = batchGiftContentKey(snapshot);
  const pendingRequestId = batchGiftPendingRequests.get(contentKey);
  batchGiftConfirmationSnapshot.value = {
    ...snapshot,
    requestId: pendingRequestId || createBatchGiftRequestId(),
  };
  batchGiftConfirming.value = true;
}

function batchGiftContentKey(snapshot) {
  return JSON.stringify({
    targetUid: String(snapshot?.targetUid || '').trim(),
    items: Array.isArray(snapshot?.items) ? snapshot.items : [],
  })
}

function createBatchGiftRequestId() {
  const randomUuid = globalThis.crypto?.randomUUID?.();
  if (randomUuid) return `batch-${randomUuid}`
  batchGiftRequestSequence += 1;
  return `batch-${Date.now().toString(36)}-${batchGiftRequestSequence.toString(36)}-${Math.random().toString(36).slice(2, 14)}`
}

function dismissBatchGiftDialog(snapshot) {
  if (
    showBatchGiftDialog.value
    && batchGiftDialogToken === snapshot.dialogToken
    && sameBatchGiftSnapshot(currentBatchGiftSnapshot(), snapshot)
  ) resetBatchGiftDialog();
}

async function submitBatchGift() {
  if (batchGiftLoading.value) return
  if (initialLoading.value || !showBatchGiftDialog.value) return
  if (batchGiftFormError.value) return flash(batchGiftFormError.value, 'warning')
  const currentSnapshot = currentBatchGiftSnapshot();
  const snapshot = batchGiftConfirmationSnapshot.value;
  if (
    !batchGiftConfirming.value
    || !sameBatchGiftSnapshot(currentSnapshot, snapshot)
    || !snapshot?.requestId
  ) {
    batchGiftConfirming.value = false;
    batchGiftConfirmationSnapshot.value = null;
    flash('批量赠送信息已变化，请重新确认', 'warning');
    return
  }

  const requestId = batchGiftRequestGuard.begin();
  const contentKey = batchGiftContentKey(snapshot);
  batchGiftPendingRequests.delete(contentKey);
  batchGiftPendingRequests.set(contentKey, snapshot.requestId);
  while (batchGiftPendingRequests.size > 20) {
    batchGiftPendingRequests.delete(batchGiftPendingRequests.keys().next().value);
  }
  batchGiftLoading.value = true;
  try {
    const result = await apiPost('/gift-items', {
      request_id: snapshot.requestId,
      target_uid: snapshot.targetUid,
      items: snapshot.items,
    });
    if (!batchGiftRequestGuard.isCurrent(requestId)) return
    statusRequestGuard.invalidate();
    const statusApplied = applyStatusPayload(result);
    const gifted = Array.isArray(result?.gifted) ? result.gifted : [];
    if (result?.request_id === snapshot.requestId && result?.pending !== true) {
      batchGiftPendingRequests.delete(contentKey);
    }

    if (isStrictSuccess(result)) {
      flash(safeResponseMessage(result, '批量赠送成功'));
      dismissBatchGiftDialog(snapshot);
      await loadStatus({ silent: true });
      return
    }

    if (result?.partial === true && gifted.length) {
      flash(safeResponseMessage(result, '批量赠送部分完成'), 'warning');
      dismissBatchGiftDialog(snapshot);
      await loadStatus({ silent: true });
      return
    }

    flash(safeResponseMessage(result, '批量赠送失败'), 'error');
    if (!statusApplied) await loadStatus({ silent: true });
  } catch (error) {
    if (batchGiftRequestGuard.isCurrent(requestId)) {
      flash(safeResponseMessage(error, '批量赠送失败'), 'error');
      statusRequestGuard.invalidate();
      await loadStatus({ silent: true });
    }
  } finally {
    if (batchGiftRequestGuard.isCurrent(requestId)) batchGiftLoading.value = false;
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
  batchGiftRequestGuard.invalidate();
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
  const _component_v_checkbox_btn = _resolveComponent("v-checkbox-btn");
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
            _createVNode(_component_v_row, {
              dense: "",
              class: "mb-3"
            }, {
              default: _withCtx(() => [
                (_openBlock(), _createElementBlock(_Fragment, null, _renderList(4, (index) => {
                  return _createVNode(_component_v_col, {
                    key: `overview-skeleton-${index}`,
                    cols: "6",
                    md: "3"
                  }, {
                    default: _withCtx(() => [
                      _hoisted_12
                    ]),
                    _: 2
                  }, 1024)
                }), 64))
              ]),
              _: 1
            }),
            _createVNode(_component_v_card, {
              flat: "",
              class: "siqi-card schedule-board mb-3 skeleton-shell"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_title, { class: "siqi-card-title" }, {
                  default: _withCtx(() => [
                    _hoisted_13
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_card_text, { class: "schedule-board-body" }, {
                  default: _withCtx(() => [
                    (_openBlock(), _createElementBlock(_Fragment, null, _renderList(2, (index) => {
                      return _createElementVNode("div", {
                        key: `schedule-skeleton-${index}`,
                        class: "sk sk-action"
                      })
                    }), 64))
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            (_openBlock(), _createElementBlock(_Fragment, null, _renderList(4, (index) => {
              return _createElementVNode("div", {
                key: `panel-skeleton-${index}`,
                class: "siqi-card skeleton-panel mb-3"
              }, _hoisted_17)
            }), 64))
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
                        _createElementVNode("div", _hoisted_18, [
                          _createVNode(_component_v_icon, {
                            icon: overviewIcon(item),
                            size: "22"
                          }, null, 8, ["icon"])
                        ]),
                        _createElementVNode("div", _hoisted_19, [
                          _createElementVNode("div", _hoisted_20, _toDisplayString(item.label), 1),
                          _createElementVNode("div", _hoisted_21, _toDisplayString(item.value), 1)
                        ])
                      ], 2)
                    ]),
                    _: 2
                  }, 1024))
                }), 128))
              ]),
              _: 1
            }),
            _createElementVNode("div", _hoisted_22, [
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
                      _hoisted_23
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_card_text, { class: "schedule-board-body" }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_24, [
                        _createElementVNode("div", _hoisted_25, [
                          _createElementVNode("div", _hoisted_26, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-wall",
                              size: "19"
                            })
                          ]),
                          _createElementVNode("div", _hoisted_27, [
                            _createElementVNode("div", _hoisted_28, [
                              _hoisted_29,
                              _createElementVNode("span", {
                                class: _normalizeClass(["schedule-status", {
                          'schedule-status--ready': brick.value.ready === true,
                          'schedule-status--done': brickStatusLabel.value === '今日已完成',
                        }])
                              }, _toDisplayString(brickStatusLabel.value), 3)
                            ]),
                            _createElementVNode("div", _hoisted_30, _toDisplayString(brick.value.status_text || '等待刷新搬砖状态'), 1),
                            _createElementVNode("div", _hoisted_31, [
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
                              _createTextVNode("立即搬砖")
                            ]),
                            _: 1
                          }, 8, ["loading", "disabled"])
                        ]),
                        _createElementVNode("div", _hoisted_32, [
                          _createElementVNode("div", _hoisted_33, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-beach",
                              size: "19"
                            })
                          ]),
                          _createElementVNode("div", _hoisted_34, [
                            _createElementVNode("div", _hoisted_35, [
                              _hoisted_36,
                              _createElementVNode("span", {
                                class: _normalizeClass(["schedule-status", {
                          'schedule-status--ready': beachActionable.value,
                          'schedule-status--cooldown': beachStatusLabel.value === '冷却中',
                        }])
                              }, _toDisplayString(beachStatusLabel.value), 3)
                            ]),
                            _createElementVNode("div", _hoisted_37, _toDisplayString(beach.value.status_text || '等待刷新沙滩状态'), 1),
                            _createElementVNode("div", _hoisted_38, [
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
                              _createTextVNode("清理沙滩")
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
                      _createElementVNode("div", _hoisted_39, [
                        _createElementVNode("div", _hoisted_40, [
                          _hoisted_41,
                          _createElementVNode("strong", null, _toDisplayString(exchange.value.magic_pills ?? 0), 1)
                        ]),
                        _createElementVNode("div", _hoisted_42, [
                          _hoisted_43,
                          _createElementVNode("strong", null, _toDisplayString(exchange.value.pill_price ?? 0), 1),
                          _hoisted_44
                        ]),
                        _createElementVNode("div", _hoisted_45, [
                          _hoisted_46,
                          _createElementVNode("strong", null, _toDisplayString(exchange.value.max_count ?? 0), 1),
                          _hoisted_47
                        ])
                      ]),
                      _createElementVNode("div", _hoisted_48, [
                        _createVNode(_component_v_text_field, {
                          modelValue: exchangeQuantity.value,
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((exchangeQuantity).value = $event)),
                          type: "number",
                          min: "1",
                          max: exchange.value.max_count,
                          label: "兑换数量",
                          variant: "outlined",
                          density: "compact",
                          "error-messages": exchangeQuantityError.value ? [exchangeQuantityError.value] : []
                        }, null, 8, ["modelValue", "max", "error-messages"]),
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
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _createElementVNode("div", _hoisted_49, [
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
                      _createElementVNode("div", _hoisted_50, [
                        _createVNode(_component_v_btn, {
                          color: "orange-darken-1",
                          variant: "tonal",
                          "prepend-icon": "mdi-gift-open-outline",
                          "aria-label": "打开批量赠送",
                          disabled: writeActionsDisabled.value || !batchGiftableItems.value.length,
                          onClick: openBatchGiftDialog
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode("批量赠送")
                          ]),
                          _: 1
                        }, 8, ["disabled"]),
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
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_card_text, { class: "inventory-body" }, {
                    default: _withCtx(() => [
                      (!inventoryItems.value.length)
                        ? (_openBlock(), _createElementBlock("div", _hoisted_51, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-package-variant",
                              size: "34"
                            }),
                            _hoisted_52,
                            _hoisted_53
                          ]))
                        : (_openBlock(), _createElementBlock("div", _hoisted_54, [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(inventoryItems.value, (item) => {
                              return (_openBlock(), _createElementBlock("button", {
                                key: item.name,
                                type: "button",
                                class: _normalizeClass(["gift-item", { 'gift-item--available': canGiftItem(item) }]),
                                disabled: !canGiftItem(item),
                                "aria-label": canGiftItem(item) ? `赠送 ${item.name}` : `${item.name} 当前不可赠送`,
                                onClick: $event => (openGiftDialog(item))
                              }, [
                                _createElementVNode("span", _hoisted_56, _toDisplayString(item.icon || '📦'), 1),
                                _createElementVNode("span", _hoisted_57, [
                                  _createElementVNode("strong", null, _toDisplayString(item.name), 1),
                                  _createElementVNode("small", null, "数量 " + _toDisplayString(item.count ?? 0), 1)
                                ]),
                                _createElementVNode("span", _hoisted_58, _toDisplayString(canGiftItem(item) ? '点击赠送' : '不可赠送'), 1)
                              ], 10, _hoisted_55))
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
                        ? (_openBlock(), _createElementBlock("div", _hoisted_59, [
                            _createVNode(_component_v_icon, {
                              icon: "mdi-flask-empty-outline",
                              size: "34"
                            }),
                            _hoisted_60,
                            _hoisted_61
                          ]))
                        : (_openBlock(), _createElementBlock("div", _hoisted_62, [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(recipes.value, (recipe) => {
                              return (_openBlock(), _createElementBlock("article", {
                                key: recipe.craft_id,
                                class: _normalizeClass(["recipe-card", { 'recipe-card--disabled': recipe.enabled !== true }])
                              }, [
                                _createElementVNode("div", _hoisted_63, [
                                  _createElementVNode("span", _hoisted_64, _toDisplayString(recipe.icon || '⚒️'), 1),
                                  _createElementVNode("div", _hoisted_65, [
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
                                _createElementVNode("div", _hoisted_66, [
                                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(recipe.ingredients || {}, (required, name) => {
                                    return (_openBlock(), _createElementBlock("span", {
                                      key: `${recipe.craft_id}-${name}`
                                    }, _toDisplayString(name) + " ×" + _toDisplayString(required), 1))
                                  }), 128))
                                ]),
                                _createElementVNode("div", _hoisted_67, [
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
                                  ? (_openBlock(), _createElementBlock("div", _hoisted_68, _toDisplayString(recipeUnavailableReason(recipe)), 1))
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
                      ? (_openBlock(), _createElementBlock("div", _hoisted_69, "暂无执行记录"))
                      : (_openBlock(), _createElementBlock("div", _hoisted_70, [
                          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(historyItems.value, (item) => {
                            return (_openBlock(), _createElementBlock("div", {
                              key: historyKey(item),
                              class: "history-item"
                            }, [
                              _createElementVNode("span", _hoisted_71, _toDisplayString(historyText(item)), 1),
                              _createElementVNode("time", _hoisted_72, _toDisplayString(item.time || ''), 1)
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
                _createElementVNode("div", _hoisted_73, _toDisplayString(selectedGiftItem.value?.icon || '🎁'), 1),
                _createElementVNode("div", _hoisted_74, [
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
      modelValue: showBatchGiftDialog.value,
      "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((showBatchGiftDialog).value = $event)),
      "max-width": "720",
      scrollable: "",
      persistent: batchGiftLoading.value
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card, {
          flat: "",
          class: "siqi-dialog batch-gift-dialog"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_card_title, { class: "dialog-header" }, {
              default: _withCtx(() => [
                _createElementVNode("div", _hoisted_75, [
                  _createVNode(_component_v_icon, { icon: "mdi-gift-open-outline" })
                ]),
                _hoisted_76,
                _createVNode(_component_v_btn, {
                  icon: "",
                  variant: "text",
                  "aria-label": "取消批量赠送并关闭对话框",
                  disabled: batchGiftLoading.value,
                  onClick: closeBatchGiftDialog
                }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_icon, { icon: "mdi-close" })
                  ]),
                  _: 1
                }, 8, ["disabled"])
              ]),
              _: 1
            }),
            _createVNode(_component_v_card_text, { class: "dialog-body batch-gift-body" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_text_field, {
                  modelValue: batchGiftForm.target_uid,
                  "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((batchGiftForm.target_uid) = $event)),
                  label: "接收方 UID",
                  variant: "outlined",
                  autocomplete: "off",
                  disabled: batchGiftLoading.value
                }, null, 8, ["modelValue", "disabled"]),
                _createElementVNode("div", _hoisted_77, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(batchGiftRows.value, (item) => {
                    return (_openBlock(), _createElementBlock("div", {
                      key: item.name,
                      class: _normalizeClass(["batch-gift-row", { 'batch-gift-row--selected': item.selected }])
                    }, [
                      _createVNode(_component_v_checkbox_btn, {
                        modelValue: item.selected,
                        "onUpdate:modelValue": $event => ((item.selected) = $event),
                        color: "orange-darken-1",
                        "aria-label": `${item.name} 加入批量赠送`,
                        disabled: batchGiftLoading.value
                      }, null, 8, ["modelValue", "onUpdate:modelValue", "aria-label", "disabled"]),
                      _createElementVNode("div", _hoisted_78, [
                        _createElementVNode("span", _hoisted_79, _toDisplayString(item.icon || '📦'), 1),
                        _createElementVNode("span", _hoisted_80, [
                          _createElementVNode("strong", null, _toDisplayString(item.name), 1),
                          _createElementVNode("small", null, "库存 " + _toDisplayString(item.count) + " · 最多 " + _toDisplayString(item.maxQuantity), 1)
                        ])
                      ]),
                      _createVNode(_component_v_text_field, {
                        modelValue: item.quantity,
                        "onUpdate:modelValue": $event => ((item.quantity) = $event),
                        type: "number",
                        min: "1",
                        max: item.maxQuantity,
                        label: "数量",
                        variant: "outlined",
                        density: "compact",
                        "hide-details": "auto",
                        "error-messages": item.selected && batchGiftRowError(item) ? [batchGiftRowError(item)] : [],
                        disabled: batchGiftLoading.value || !item.selected
                      }, null, 8, ["modelValue", "onUpdate:modelValue", "max", "error-messages", "disabled"])
                    ], 2))
                  }), 128))
                ]),
                (batchGiftConfirming.value)
                  ? (_openBlock(), _createBlock(_component_v_alert, {
                      key: 0,
                      type: "warning",
                      variant: "tonal",
                      density: "compact",
                      class: "confirm-alert"
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode(" 再次确认：向 UID " + _toDisplayString(batchGiftForm.target_uid.trim()) + " 批量赠送 " + _toDisplayString(batchGiftSummary.value) + "。提交后将按顺序处理，遇到失败会立即停止。 ", 1)
                      ]),
                      _: 1
                    }))
                  : (batchGiftFormError.value)
                    ? (_openBlock(), _createBlock(_component_v_alert, {
                        key: 1,
                        type: "info",
                        variant: "tonal",
                        density: "compact",
                        class: "confirm-alert"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(batchGiftFormError.value), 1)
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
                  disabled: batchGiftLoading.value,
                  onClick: closeBatchGiftDialog
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("取消")
                  ]),
                  _: 1
                }, 8, ["disabled"]),
                _createVNode(_component_v_spacer),
                (batchGiftConfirming.value)
                  ? (_openBlock(), _createBlock(_component_v_btn, {
                      key: 0,
                      variant: "text",
                      disabled: batchGiftLoading.value,
                      onClick: _cache[9] || (_cache[9] = $event => (batchGiftConfirming.value = false))
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode("返回修改")
                      ]),
                      _: 1
                    }, 8, ["disabled"]))
                  : _createCommentVNode("", true),
                (!batchGiftConfirming.value)
                  ? (_openBlock(), _createBlock(_component_v_btn, {
                      key: 1,
                      color: "orange-darken-1",
                      variant: "tonal",
                      disabled: batchGiftLoading.value || !!batchGiftFormError.value,
                      onClick: requestBatchGiftConfirmation
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode("确认批量赠送")
                      ]),
                      _: 1
                    }, 8, ["disabled"]))
                  : (_openBlock(), _createBlock(_component_v_btn, {
                      key: 2,
                      color: "error",
                      variant: "tonal",
                      loading: batchGiftLoading.value,
                      disabled: batchGiftLoading.value || !!batchGiftFormError.value,
                      onClick: submitBatchGift
                    }, {
                      default: _withCtx(() => [
                        _createTextVNode("再次确认并批量赠送")
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
      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((showGiftStatsDialog).value = $event)),
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
                _createElementVNode("div", _hoisted_81, [
                  _createVNode(_component_v_icon, { icon: "mdi-chart-box-outline" })
                ]),
                _hoisted_82,
                _createVNode(_component_v_btn, {
                  icon: "",
                  variant: "text",
                  "aria-label": "关闭赠送统计",
                  disabled: giftStatsLoading.value,
                  onClick: _cache[11] || (_cache[11] = $event => (showGiftStatsDialog.value = false))
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
                _createElementVNode("div", _hoisted_83, [
                  _createVNode(_component_v_btn_toggle, {
                    modelValue: giftStatsDraftDirection.value,
                    "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((giftStatsDraftDirection).value = $event)),
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
                    "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((giftStatsDraftRange).value = $event)),
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
                    ? (_openBlock(), _createElementBlock("div", _hoisted_84, "正在加载赠送统计..."))
                    : (giftStats.value)
                      ? (_openBlock(), _createElementBlock(_Fragment, { key: 2 }, [
                          _createElementVNode("div", _hoisted_85, "当前数据：" + _toDisplayString(giftStatsAppliedDirectionLabel.value) + " · " + _toDisplayString(giftStatsAppliedRangeLabel.value), 1),
                          _createElementVNode("div", _hoisted_86, [
                            _createElementVNode("div", _hoisted_87, [
                              _hoisted_88,
                              _createElementVNode("strong", null, _toDisplayString(giftStats.value.total_events ?? 0), 1)
                            ]),
                            _createElementVNode("div", _hoisted_89, [
                              _hoisted_90,
                              _createElementVNode("strong", null, _toDisplayString(giftStats.value.total_quantity ?? 0), 1)
                            ])
                          ]),
                          (giftStatsEmpty.value)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_91, "当前筛选范围暂无赠送记录"))
                            : (_openBlock(), _createElementBlock("div", _hoisted_92, [
                                _createElementVNode("section", _hoisted_93, [
                                  _hoisted_94,
                                  (!giftStatsUsers.value.length)
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_95, "暂无用户数据"))
                                    : (_openBlock(), _createElementBlock("div", _hoisted_96, [
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
                                _createElementVNode("section", _hoisted_97, [
                                  _hoisted_98,
                                  (!giftStatsItems.value.length)
                                    ? (_openBlock(), _createElementBlock("div", _hoisted_99, "暂无物品数据"))
                                    : (_openBlock(), _createElementBlock("div", _hoisted_100, [
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
                  onClick: _cache[14] || (_cache[14] = $event => (showGiftStatsDialog.value = false))
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
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-8524c21b"]]);

export { PageView as default };
