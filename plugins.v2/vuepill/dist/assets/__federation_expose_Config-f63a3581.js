import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc, i as isStrictSuccess, s as safeResponseMessage, c as createLatestRequestGuard } from './_plugin-vue_export-helper-41a74a79.js';

const BOOLEAN_CONFIG_FIELDS = Object.freeze([
  'enabled',
  'notify',
  'onlyonce',
  'use_proxy',
  'enable_brick',
  'enable_beach',
  'auto_craft',
  'auto_exchange',
]);

const INTEGER_CONFIG_RULES = Object.freeze({
  schedule_buffer_seconds: Object.freeze({ label: '冷却缓冲', min: 0, max: 3600 }),
  reserve_magic_pill_count: Object.freeze({ label: '保留魔丸', min: 0, max: Number.MAX_SAFE_INTEGER }),
  random_delay_max_seconds: Object.freeze({ label: '随机延迟', min: 0, max: 300 }),
  http_timeout: Object.freeze({ label: '请求超时', min: 5, max: 120 }),
  http_retry_times: Object.freeze({ label: '网络重试次数', min: 1, max: 5 }),
  http_retry_delay: Object.freeze({ label: '重试间隔', min: 200, max: 60000 }),
});

const CANONICAL_UNSIGNED_INTEGER = /^(?:0|[1-9]\d*)$/;
const CRON_NUMBER = /^\d+$/;
const MONTH_NAMES = Object.freeze({
  jan: 1,
  feb: 2,
  mar: 3,
  apr: 4,
  may: 5,
  jun: 6,
  jul: 7,
  aug: 8,
  sep: 9,
  oct: 10,
  nov: 11,
  dec: 12,
});
const DAY_OF_WEEK_NAMES = Object.freeze({
  mon: 0,
  tue: 1,
  wed: 2,
  thu: 3,
  fri: 4,
  sat: 5,
  sun: 6,
});
const CRON_FIELD_RULES = Object.freeze([
  Object.freeze({ label: '分钟', min: 0, max: 59 }),
  Object.freeze({ label: '小时', min: 0, max: 23 }),
  Object.freeze({ label: '日期', min: 1, max: 31 }),
  Object.freeze({ label: '月份', min: 1, max: 12, names: MONTH_NAMES }),
  Object.freeze({ label: '星期', min: 0, max: 7, names: DAY_OF_WEEK_NAMES }),
]);

function parseStrictInteger(value, rule) {
  let parsed;
  if (typeof value === 'number') {
    if (!Number.isSafeInteger(value)) {
      return { valid: false, value: null, error: `${rule.label}必须填写规范整数` }
    }
    parsed = value;
  } else if (typeof value === 'string' && CANONICAL_UNSIGNED_INTEGER.test(value)) {
    parsed = Number(value);
    if (!Number.isSafeInteger(parsed)) {
      return { valid: false, value: null, error: `${rule.label}必须填写安全整数` }
    }
  } else {
    return { valid: false, value: null, error: `${rule.label}必须填写规范整数` }
  }

  if (parsed < rule.min || parsed > rule.max) {
    return {
      valid: false,
      value: null,
      error: `${rule.label}必须在 ${rule.min} 到 ${rule.max} 之间`,
    }
  }
  return { valid: true, value: parsed, error: '' }
}

function parseCronValue(value, rule) {
  if (CRON_NUMBER.test(value)) {
    const parsed = Number(value);
    return Number.isSafeInteger(parsed) && parsed >= rule.min && parsed <= rule.max
      ? parsed
      : null
  }
  return rule.names && Object.hasOwn(rule.names, value)
    ? rule.names[value]
    : null
}

function validateCronItem(item, rule) {
  const stepParts = item.split('/');
  if (stepParts.length > 2 || stepParts.some(part => !part)) return false

  const base = stepParts[0];
  let step = null;
  if (stepParts.length === 2) {
    if (!CRON_NUMBER.test(stepParts[1])) return false
    step = Number(stepParts[1]);
    if (!Number.isSafeInteger(step) || step <= 0) return false
  }

  let start;
  let end;
  if (base === '*') {
    start = rule.min;
    end = rule.max;
  } else if (base.includes('-')) {
    const rangeParts = base.split('-');
    if (rangeParts.length !== 2 || rangeParts.some(part => !part)) return false
    start = parseCronValue(rangeParts[0], rule);
    end = parseCronValue(rangeParts[1], rule);
    if (start === null || end === null || start > end) return false
  } else {
    if (step !== null) return false
    return parseCronValue(base, rule) !== null
  }

  return step === null || step <= end - start
}

function validateCronField(field, rule) {
  const items = field.split(',');
  if (!items.length || items.some(item => !item)) return false
  if (items.length > 1 && items.some(item => item.startsWith('*'))) return false
  return items.every(item => validateCronItem(item, rule))
}

function validateCronExpression(value) {
  if (typeof value !== 'string' || !value.trim()) {
    return { valid: false, value: '', error: '搬砖 Cron 不能为空' }
  }
  if (/\r|\n/.test(value)) {
    return { valid: false, value: '', error: '搬砖 Cron 不能包含换行' }
  }

  const fields = value.trim().split(/[ \t]+/);
  if (fields.length !== 5) {
    return { valid: false, value: '', error: '搬砖 Cron 必须是 5 段表达式' }
  }
  const normalizedFields = fields.map(field => field.toLowerCase());
  const invalidIndex = normalizedFields.findIndex(
    (field, index) => !validateCronField(field, CRON_FIELD_RULES[index]),
  );
  if (invalidIndex >= 0) {
    return {
      valid: false,
      value: '',
      error: `搬砖 Cron 的${CRON_FIELD_RULES[invalidIndex].label}段不合法`,
    }
  }
  return { valid: true, value: normalizedFields.join(' '), error: '' }
}

function validateVuePillConfig(source) {
  const safeSource = source && typeof source === 'object' ? source : {};
  const payload = {};
  const errors = {};

  for (const field of BOOLEAN_CONFIG_FIELDS) {
    payload[field] = safeSource[field] === true;
  }

  const cron = validateCronExpression(safeSource.brick_cron);
  if (cron.valid) payload.brick_cron = cron.value;
  else errors.brick_cron = cron.error;

  for (const [field, rule] of Object.entries(INTEGER_CONFIG_RULES)) {
    const parsed = parseStrictInteger(safeSource[field], rule);
    if (parsed.valid) payload[field] = parsed.value;
    else errors[field] = parsed.error;
  }

  const errorFields = Object.keys(errors);
  return {
    valid: errorFields.length === 0,
    payload,
    errors,
    firstErrorField: errorFields[0] || '',
  }
}

const Config_vue_vue_type_style_index_0_scoped_e2955237_lang = '';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,withCtx:_withCtx,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-e2955237"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "siqi-config" };
const _hoisted_2 = { class: "siqi-topbar" };
const _hoisted_3 = { class: "siqi-topbar__left" };
const _hoisted_4 = { class: "siqi-topbar__icon" };
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-topbar__copy" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-topbar__title" }, "Vue-魔丸 · 配置"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-topbar__sub" }, "管理搬砖、清沙滩、炼造与兑换任务")
], -1));
const _hoisted_6 = { class: "siqi-topbar__right" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "d-none d-sm-inline" }, "状态页", -1));
const _hoisted_8 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "d-none d-sm-inline" }, "保存", -1));
const _hoisted_9 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", { class: "d-none d-sm-inline" }, "关闭", -1));
const _hoisted_10 = {
  key: 1,
  class: "siqi-loading-state",
  role: "status",
  "aria-live": "polite"
};
const _hoisted_11 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("span", null, "正在加载配置，请稍候", -1));
const _hoisted_12 = ["disabled", "inert", "aria-busy"];
const _hoisted_13 = { class: "siqi-config-col" };
const _hoisted_14 = { class: "siqi-card" };
const _hoisted_15 = { class: "siqi-card__header" };
const _hoisted_16 = { class: "siqi-card__title d-flex align-center" };
const _hoisted_17 = { class: "siqi-switch-grid" };
const _hoisted_18 = { class: "siqi-switch-main" };
const _hoisted_19 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-label" }, "启用插件"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-desc" }, "开启后注册搬砖与沙滩自动任务")
], -1));
const _hoisted_20 = { class: "siqi-switch-main" };
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-label" }, "通知"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-desc" }, "任务完成或异常时发送 MoviePilot 通知")
], -1));
const _hoisted_22 = { class: "siqi-switch-main" };
const _hoisted_23 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-label" }, "代理"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-desc" }, "使用 MoviePilot 已配置的网络代理访问站点")
], -1));
const _hoisted_24 = { class: "siqi-card" };
const _hoisted_25 = { class: "siqi-card__header" };
const _hoisted_26 = { class: "siqi-card__title d-flex align-center" };
const _hoisted_27 = { class: "siqi-switch-grid" };
const _hoisted_28 = { class: "siqi-switch-main" };
const _hoisted_29 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-label" }, "立即运行一次"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-desc" }, "保存后排队执行一轮，执行后自动关闭此开关")
], -1));
const _hoisted_30 = { class: "siqi-switch-main" };
const _hoisted_31 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-label" }, "自动搬砖"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-desc" }, "按搬砖 Cron 定时执行搬砖")
], -1));
const _hoisted_32 = { class: "siqi-switch-main" };
const _hoisted_33 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-label" }, "动态清沙滩"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-desc" }, "根据站点冷却时间动态安排清理")
], -1));
const _hoisted_34 = { class: "siqi-switch-main" };
const _hoisted_35 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-label" }, "自动炼造"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-desc" }, "清沙滩后按可用材料自动炼造")
], -1));
const _hoisted_36 = { class: "siqi-switch-main" };
const _hoisted_37 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-label" }, "自动兑换"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-switch-desc" }, "保留指定魔丸后自动兑换魔力")
], -1));
const _hoisted_38 = { class: "siqi-card" };
const _hoisted_39 = { class: "siqi-card__header" };
const _hoisted_40 = { class: "siqi-card__title d-flex align-center" };
const _hoisted_41 = { class: "siqi-form-grid" };
const _hoisted_42 = {
  class: "siqi-field siqi-wide-field",
  "data-config-field": "brick_cron"
};
const _hoisted_43 = {
  key: 0,
  class: "siqi-field-error",
  role: "alert"
};
const _hoisted_44 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-field-hint" }, "搬砖 Cron 是定时规则；默认每天 00:05 执行。", -1));
const _hoisted_45 = {
  class: "siqi-field",
  "data-config-field": "schedule_buffer_seconds"
};
const _hoisted_46 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-field-hint" }, "填写 0 到 3600 的整数；站点显示可执行后再等待这段时间。", -1));
const _hoisted_47 = {
  class: "siqi-field",
  "data-config-field": "reserve_magic_pill_count"
};
const _hoisted_48 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-field-hint" }, "填写不小于 0 的整数；自动兑换前默认保留 10 个魔丸。", -1));
const _hoisted_49 = {
  class: "siqi-field",
  "data-config-field": "random_delay_max_seconds"
};
const _hoisted_50 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-field-hint" }, "填写 0 到 300 的整数；0 表示不额外等待。", -1));
const _hoisted_51 = {
  class: "siqi-field",
  "data-config-field": "http_timeout"
};
const _hoisted_52 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-field-hint" }, "填写 5 到 120 的整数；表示单次网络请求最长等待秒数。", -1));
const _hoisted_53 = {
  class: "siqi-field",
  "data-config-field": "http_retry_times"
};
const _hoisted_54 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-field-hint" }, "填写 1 到 5 的整数；网络失败时最多按此次数重试。", -1));
const _hoisted_55 = {
  class: "siqi-field",
  "data-config-field": "http_retry_delay"
};
const _hoisted_56 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "siqi-field-hint" }, "填写 200 到 60000 的整数；默认 1500 毫秒（1.5 秒）。", -1));
const _hoisted_57 = { class: "siqi-card" };
const _hoisted_58 = { class: "siqi-card__header" };
const _hoisted_59 = { class: "siqi-card__title d-flex align-center" };
const _hoisted_60 = { class: "siqi-site-note" };
const _hoisted_61 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-site-note__title" }, "Cookie：从 MoviePilot 站点自动同步。"),
  /*#__PURE__*/_createElementVNode("div", { class: "siqi-site-note__desc" }, "此处无需填写或手动操作，插件每次请求都会读取最新站点凭据。")
], -1));

const {computed,nextTick,onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');

const CONFIG_ENDPOINT = '/plugin/VuePill/config';

const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;




const CONFIG_FIELDS = Object.freeze([
  'enabled',
  'notify',
  'onlyonce',
  'use_proxy',
  'enable_brick',
  'enable_beach',
  'auto_craft',
  'auto_exchange',
  'brick_cron',
  'schedule_buffer_seconds',
  'reserve_magic_pill_count',
  'random_delay_max_seconds',
  'http_timeout',
  'http_retry_times',
  'http_retry_delay',
]);
const DEFAULT_CONFIG = Object.freeze({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  reserve_magic_pill_count: 10,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
});

const config = reactive({ ...DEFAULT_CONFIG });
const configLoading = ref(false);
const configSaving = ref(false);
const upgradeRestartRequired = ref(false);
const formLocked = computed(() => configLoading.value || configSaving.value || upgradeRestartRequired.value);
const fieldErrors = reactive({});
const message = ref('');
const messageType = ref('success');
const loadRequestGuard = createLatestRequestGuard();
const saveRequestGuard = createLatestRequestGuard();
let messageTimer = null;
let disposed = false;

applyPublicConfig(props.initialConfig);

function ownDataValue(source, field) {
  if (!source || typeof source !== 'object' || Array.isArray(source)) return undefined
  try {
    const descriptor = Object.getOwnPropertyDescriptor(source, field);
    return descriptor && Object.prototype.hasOwnProperty.call(descriptor, 'value')
      ? descriptor.value
      : undefined
  } catch {
    return undefined
  }
}

function applyPublicConfig(source) {
  upgradeRestartRequired.value = ownDataValue(source, 'upgrade_restart_required') === true;
  for (const field of CONFIG_FIELDS) {
    const value = ownDataValue(source, field);
    config[field] = value === undefined ? DEFAULT_CONFIG[field] : value;
  }
  clearFieldErrors();
}

function isCompletePublicConfig(source) {
  return CONFIG_FIELDS.every(field => ownDataValue(source, field) !== undefined)
}

function buildConfigPayload() {
  const validation = validateVuePillConfig(config);
  replaceFieldErrors(validation.errors);
  return validation
}

function clearFieldError(field) {
  if (fieldErrors[field]) delete fieldErrors[field];
}

function clearFieldErrors() {
  for (const field of Object.keys(fieldErrors)) delete fieldErrors[field];
}

function replaceFieldErrors(errors) {
  clearFieldErrors();
  for (const [field, error] of Object.entries(errors || {})) {
    if (typeof error === 'string' && error) fieldErrors[field] = error;
  }
}

function publicResponseErrors(result) {
  const source = ownDataValue(result, 'errors');
  const errors = {};
  for (const field of CONFIG_FIELDS) {
    const error = ownDataValue(source, field);
    if (typeof error === 'string' && error.trim()) errors[field] = error.trim();
  }
  return errors
}

async function focusFirstError(field) {
  if (!field) return
  await nextTick();
  if (typeof document === 'undefined') return
  const container = document.querySelector(`[data-config-field="${field}"]`);
  const control = container?.querySelector('input, textarea, button, [tabindex]:not([tabindex="-1"])');
  if (typeof control?.focus === 'function') control.focus();
}

function show(text, type = 'success') {
  if (disposed) return
  message.value = typeof text === 'string' && text.trim() ? text.trim() : '操作失败';
  messageType.value = type;
  if (messageTimer) clearTimeout(messageTimer);
  messageTimer = setTimeout(() => {
    if (!disposed) message.value = '';
    messageTimer = null;
  }, 4000);
}

function errorMessage(error, fallback) {
  return typeof error?.message === 'string' && error.message.trim()
    ? error.message.trim()
    : fallback
}

async function loadConfig({ silent = false } = {}) {
  const requestId = loadRequestGuard.begin();
  configLoading.value = true;
  try {
    const data = await props.api.get(CONFIG_ENDPOINT);
    if (!loadRequestGuard.isCurrent(requestId)) return
    applyPublicConfig(data);
  } catch (error) {
    if (loadRequestGuard.isCurrent(requestId) && !silent) {
      show(`加载失败：${errorMessage(error, '请求异常')}`, 'error');
    }
  } finally {
    if (loadRequestGuard.isCurrent(requestId)) configLoading.value = false;
  }
}

async function saveConfig() {
  if (formLocked.value) return
  const validation = buildConfigPayload();
  if (!validation.valid) {
    show('请检查标红的配置项后再保存', 'error');
    await focusFirstError(validation.firstErrorField);
    return
  }
  const requestId = saveRequestGuard.begin();
  configSaving.value = true;
  const payload = validation.payload;
  try {
    const result = await props.api.post(CONFIG_ENDPOINT, payload);
    if (!saveRequestGuard.isCurrent(requestId)) return
    if (!isStrictSuccess(result)) {
      const backendErrors = publicResponseErrors(result);
      replaceFieldErrors(backendErrors);
      show(safeResponseMessage(result, '保存失败'), 'error');
      const firstErrorField = Object.keys(backendErrors)[0];
      if (firstErrorField) {
        configSaving.value = false;
        await focusFirstError(firstErrorField);
      }
      return
    }
    if (isCompletePublicConfig(result?.config)) {
      applyPublicConfig(result.config);
    } else {
      config.onlyonce = false;
      await loadConfig({ silent: true });
    }
    show(safeResponseMessage(result, '配置已保存'));
  } catch (error) {
    if (saveRequestGuard.isCurrent(requestId)) {
      show(`保存失败：${errorMessage(error, '请求异常')}`, 'error');
    }
  } finally {
    if (saveRequestGuard.isCurrent(requestId)) configSaving.value = false;
  }
}

onMounted(loadConfig);

onBeforeUnmount(() => {
  disposed = true;
  loadRequestGuard.invalidate();
  saveRequestGuard.invalidate();
  if (messageTimer) clearTimeout(messageTimer);
});

return (_ctx, _cache) => {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_btn_group = _resolveComponent("v-btn-group");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_progress_linear = _resolveComponent("v-progress-linear");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_v_text_field = _resolveComponent("v-text-field");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("div", _hoisted_3, [
        _createElementVNode("div", _hoisted_4, [
          _createVNode(_component_v_icon, {
            icon: "mdi-cog-outline",
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
              "min-width": "40",
              class: "px-0 px-sm-3",
              "aria-label": "状态页",
              disabled: formLocked.value,
              onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'page')))
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-view-dashboard",
                  size: "18",
                  class: "mr-sm-1"
                }),
                _hoisted_7
              ]),
              _: 1
            }, 8, ["disabled"]),
            _createVNode(_component_v_btn, {
              color: "success",
              size: "small",
              "min-width": "40",
              class: "px-0 px-sm-3",
              "aria-label": "保存配置",
              loading: configSaving.value,
              disabled: formLocked.value,
              onClick: saveConfig
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, {
                  icon: "mdi-content-save",
                  size: "18",
                  class: "mr-sm-1"
                }),
                _hoisted_8
              ]),
              _: 1
            }, 8, ["loading", "disabled"]),
            _createVNode(_component_v_btn, {
              color: "success",
              size: "small",
              "min-width": "40",
              class: "px-0 px-sm-3",
              "aria-label": "关闭配置",
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
            })
          ]),
          _: 1
        })
      ])
    ]),
    (message.value)
      ? (_openBlock(), _createBlock(_component_v_alert, {
          key: 0,
          type: messageType.value,
          density: "compact",
          class: "siqi-toast",
          closable: "",
          "onClick:close": _cache[2] || (_cache[2] = $event => (message.value = ''))
        }, {
          default: _withCtx(() => [
            _createTextVNode(_toDisplayString(message.value), 1)
          ]),
          _: 1
        }, 8, ["type"]))
      : _createCommentVNode("", true),
    (configLoading.value)
      ? (_openBlock(), _createElementBlock("div", _hoisted_10, [
          _createVNode(_component_v_progress_linear, {
            color: "success",
            indeterminate: "",
            rounded: ""
          }),
          _hoisted_11
        ]))
      : _createCommentVNode("", true),
    (upgradeRestartRequired.value)
      ? (_openBlock(), _createBlock(_component_v_alert, {
          key: 2,
          type: "warning",
          density: "compact",
          role: "alert"
        }, {
          default: _withCtx(() => [
            _createTextVNode(" 请重启 MoviePilot 完成 Vue-魔丸 v0.2.0 升级 ")
          ]),
          _: 1
        }))
      : _createCommentVNode("", true),
    _createElementVNode("fieldset", {
      class: "siqi-form-lock",
      disabled: formLocked.value,
      inert: formLocked.value,
      "aria-busy": formLocked.value
    }, [
      _createElementVNode("div", _hoisted_13, [
        _createElementVNode("div", _hoisted_14, [
          _createElementVNode("div", _hoisted_15, [
            _createElementVNode("span", _hoisted_16, [
              _createVNode(_component_v_icon, {
                icon: "mdi-toggle-switch-outline",
                size: "18",
                color: "#22c55e",
                class: "mr-1"
              }),
              _createTextVNode("基础设置 ")
            ])
          ]),
          _createElementVNode("div", _hoisted_17, [
            _createElementVNode("div", {
              class: _normalizeClass(["siqi-switch-item", {'siqi-switch-item--active': config.enabled}]),
              style: {"--siqi-accent":"34,197,94"}
            }, [
              _createElementVNode("div", _hoisted_18, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-power-plug",
                  size: "18"
                }),
                _hoisted_19
              ]),
              _createVNode(_component_v_switch, {
                modelValue: config.enabled,
                "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.enabled) = $event)),
                color: "green",
                "hide-details": "",
                density: "compact",
                "aria-label": "启用插件",
                disabled: formLocked.value
              }, null, 8, ["modelValue", "disabled"])
            ], 2),
            _createElementVNode("div", {
              class: _normalizeClass(["siqi-switch-item", {'siqi-switch-item--active': config.notify}]),
              style: {"--siqi-accent":"59,130,246"}
            }, [
              _createElementVNode("div", _hoisted_20, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-bell-outline",
                  size: "18"
                }),
                _hoisted_21
              ]),
              _createVNode(_component_v_switch, {
                modelValue: config.notify,
                "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.notify) = $event)),
                color: "blue",
                "hide-details": "",
                density: "compact",
                "aria-label": "通知",
                disabled: formLocked.value
              }, null, 8, ["modelValue", "disabled"])
            ], 2),
            _createElementVNode("div", {
              class: _normalizeClass(["siqi-switch-item", {'siqi-switch-item--active': config.use_proxy}]),
              style: {"--siqi-accent":"139,92,246"}
            }, [
              _createElementVNode("div", _hoisted_22, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-lan-connect",
                  size: "18"
                }),
                _hoisted_23
              ]),
              _createVNode(_component_v_switch, {
                modelValue: config.use_proxy,
                "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.use_proxy) = $event)),
                color: "purple",
                "hide-details": "",
                density: "compact",
                "aria-label": "代理",
                disabled: formLocked.value
              }, null, 8, ["modelValue", "disabled"])
            ], 2)
          ])
        ]),
        _createElementVNode("div", _hoisted_24, [
          _createElementVNode("div", _hoisted_25, [
            _createElementVNode("span", _hoisted_26, [
              _createVNode(_component_v_icon, {
                icon: "mdi-robot-outline",
                size: "18",
                color: "#f59e0b",
                class: "mr-1"
              }),
              _createTextVNode("自动化策略 ")
            ])
          ]),
          _createElementVNode("div", _hoisted_27, [
            _createElementVNode("div", {
              class: _normalizeClass(["siqi-switch-item", {'siqi-switch-item--active': config.onlyonce}]),
              style: {"--siqi-accent":"245,158,11"}
            }, [
              _createElementVNode("div", _hoisted_28, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-play-circle-outline",
                  size: "18"
                }),
                _hoisted_29
              ]),
              _createVNode(_component_v_switch, {
                modelValue: config.onlyonce,
                "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.onlyonce) = $event)),
                color: "orange",
                "hide-details": "",
                density: "compact",
                "aria-label": "立即运行一次",
                disabled: formLocked.value
              }, null, 8, ["modelValue", "disabled"])
            ], 2),
            _createElementVNode("div", {
              class: _normalizeClass(["siqi-switch-item", {'siqi-switch-item--active': config.enable_brick}]),
              style: {"--siqi-accent":"34,197,94"}
            }, [
              _createElementVNode("div", _hoisted_30, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-wall",
                  size: "18"
                }),
                _hoisted_31
              ]),
              _createVNode(_component_v_switch, {
                modelValue: config.enable_brick,
                "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.enable_brick) = $event)),
                color: "green",
                "hide-details": "",
                density: "compact",
                "aria-label": "自动搬砖",
                disabled: formLocked.value
              }, null, 8, ["modelValue", "disabled"])
            ], 2),
            _createElementVNode("div", {
              class: _normalizeClass(["siqi-switch-item", {'siqi-switch-item--active': config.enable_beach}]),
              style: {"--siqi-accent":"14,165,233"}
            }, [
              _createElementVNode("div", _hoisted_32, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-beach",
                  size: "18"
                }),
                _hoisted_33
              ]),
              _createVNode(_component_v_switch, {
                modelValue: config.enable_beach,
                "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.enable_beach) = $event)),
                color: "info",
                "hide-details": "",
                density: "compact",
                "aria-label": "动态清沙滩",
                disabled: formLocked.value
              }, null, 8, ["modelValue", "disabled"])
            ], 2),
            _createElementVNode("div", {
              class: _normalizeClass(["siqi-switch-item", {'siqi-switch-item--active': config.auto_craft}]),
              style: {"--siqi-accent":"239,68,68"}
            }, [
              _createElementVNode("div", _hoisted_34, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-hammer-wrench",
                  size: "18"
                }),
                _hoisted_35
              ]),
              _createVNode(_component_v_switch, {
                modelValue: config.auto_craft,
                "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.auto_craft) = $event)),
                color: "red",
                "hide-details": "",
                density: "compact",
                "aria-label": "自动炼造",
                disabled: formLocked.value
              }, null, 8, ["modelValue", "disabled"])
            ], 2),
            _createElementVNode("div", {
              class: _normalizeClass(["siqi-switch-item", {'siqi-switch-item--active': config.auto_exchange}]),
              style: {"--siqi-accent":"236,72,153"}
            }, [
              _createElementVNode("div", _hoisted_36, [
                _createVNode(_component_v_icon, {
                  icon: "mdi-cash-sync",
                  size: "18"
                }),
                _hoisted_37
              ]),
              _createVNode(_component_v_switch, {
                modelValue: config.auto_exchange,
                "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.auto_exchange) = $event)),
                color: "pink",
                "hide-details": "",
                density: "compact",
                "aria-label": "自动兑换",
                disabled: formLocked.value
              }, null, 8, ["modelValue", "disabled"])
            ], 2)
          ])
        ]),
        _createElementVNode("div", _hoisted_38, [
          _createElementVNode("div", _hoisted_39, [
            _createElementVNode("span", _hoisted_40, [
              _createVNode(_component_v_icon, {
                icon: "mdi-tune-variant",
                size: "18",
                color: "#0ea5e9",
                class: "mr-1"
              }),
              _createTextVNode("参数设置 ")
            ])
          ]),
          _createElementVNode("div", _hoisted_41, [
            _createElementVNode("div", _hoisted_42, [
              _createVNode(_component_VCronField, {
                modelValue: config.brick_cron,
                "onUpdate:modelValue": [
                  _cache[11] || (_cache[11] = $event => ((config.brick_cron) = $event)),
                  _cache[12] || (_cache[12] = $event => (clearFieldError('brick_cron')))
                ],
                label: "搬砖Cron",
                density: "compact",
                class: "siqi-input siqi-cron-field",
                disabled: formLocked.value,
                error: Boolean(fieldErrors.brick_cron),
                "aria-invalid": Boolean(fieldErrors.brick_cron)
              }, null, 8, ["modelValue", "disabled", "error", "aria-invalid"]),
              (fieldErrors.brick_cron)
                ? (_openBlock(), _createElementBlock("div", _hoisted_43, _toDisplayString(fieldErrors.brick_cron), 1))
                : _createCommentVNode("", true),
              _hoisted_44
            ]),
            _createElementVNode("div", _hoisted_45, [
              _createVNode(_component_v_text_field, {
                modelValue: config.schedule_buffer_seconds,
                "onUpdate:modelValue": [
                  _cache[13] || (_cache[13] = $event => ((config.schedule_buffer_seconds) = $event)),
                  _cache[14] || (_cache[14] = $event => (clearFieldError('schedule_buffer_seconds')))
                ],
                label: "冷却缓冲（秒）",
                type: "text",
                inputmode: "numeric",
                min: "0",
                max: "3600",
                density: "compact",
                variant: "outlined",
                "hide-details": "auto",
                class: "siqi-input",
                "prepend-inner-icon": "mdi-clock-fast",
                disabled: formLocked.value,
                "error-messages": fieldErrors.schedule_buffer_seconds ? [fieldErrors.schedule_buffer_seconds] : [],
                "aria-invalid": Boolean(fieldErrors.schedule_buffer_seconds)
              }, null, 8, ["modelValue", "disabled", "error-messages", "aria-invalid"]),
              _hoisted_46
            ]),
            _createElementVNode("div", _hoisted_47, [
              _createVNode(_component_v_text_field, {
                modelValue: config.reserve_magic_pill_count,
                "onUpdate:modelValue": [
                  _cache[15] || (_cache[15] = $event => ((config.reserve_magic_pill_count) = $event)),
                  _cache[16] || (_cache[16] = $event => (clearFieldError('reserve_magic_pill_count')))
                ],
                label: "保留魔丸",
                type: "text",
                inputmode: "numeric",
                min: "0",
                max: "9007199254740991",
                density: "compact",
                variant: "outlined",
                "hide-details": "auto",
                class: "siqi-input",
                "prepend-inner-icon": "mdi-flask-outline",
                disabled: formLocked.value,
                "error-messages": fieldErrors.reserve_magic_pill_count ? [fieldErrors.reserve_magic_pill_count] : [],
                "aria-invalid": Boolean(fieldErrors.reserve_magic_pill_count)
              }, null, 8, ["modelValue", "disabled", "error-messages", "aria-invalid"]),
              _hoisted_48
            ]),
            _createElementVNode("div", _hoisted_49, [
              _createVNode(_component_v_text_field, {
                modelValue: config.random_delay_max_seconds,
                "onUpdate:modelValue": [
                  _cache[17] || (_cache[17] = $event => ((config.random_delay_max_seconds) = $event)),
                  _cache[18] || (_cache[18] = $event => (clearFieldError('random_delay_max_seconds')))
                ],
                label: "随机延迟（秒）",
                type: "text",
                inputmode: "numeric",
                min: "0",
                max: "300",
                density: "compact",
                variant: "outlined",
                "hide-details": "auto",
                class: "siqi-input",
                "prepend-inner-icon": "mdi-timer-sand",
                disabled: formLocked.value,
                "error-messages": fieldErrors.random_delay_max_seconds ? [fieldErrors.random_delay_max_seconds] : [],
                "aria-invalid": Boolean(fieldErrors.random_delay_max_seconds)
              }, null, 8, ["modelValue", "disabled", "error-messages", "aria-invalid"]),
              _hoisted_50
            ]),
            _createElementVNode("div", _hoisted_51, [
              _createVNode(_component_v_text_field, {
                modelValue: config.http_timeout,
                "onUpdate:modelValue": [
                  _cache[19] || (_cache[19] = $event => ((config.http_timeout) = $event)),
                  _cache[20] || (_cache[20] = $event => (clearFieldError('http_timeout')))
                ],
                label: "请求超时（秒）",
                type: "text",
                inputmode: "numeric",
                min: "5",
                max: "120",
                density: "compact",
                variant: "outlined",
                "hide-details": "auto",
                class: "siqi-input",
                "prepend-inner-icon": "mdi-timer-alert-outline",
                disabled: formLocked.value,
                "error-messages": fieldErrors.http_timeout ? [fieldErrors.http_timeout] : [],
                "aria-invalid": Boolean(fieldErrors.http_timeout)
              }, null, 8, ["modelValue", "disabled", "error-messages", "aria-invalid"]),
              _hoisted_52
            ]),
            _createElementVNode("div", _hoisted_53, [
              _createVNode(_component_v_text_field, {
                modelValue: config.http_retry_times,
                "onUpdate:modelValue": [
                  _cache[21] || (_cache[21] = $event => ((config.http_retry_times) = $event)),
                  _cache[22] || (_cache[22] = $event => (clearFieldError('http_retry_times')))
                ],
                label: "网络重试次数",
                type: "text",
                inputmode: "numeric",
                min: "1",
                max: "5",
                density: "compact",
                variant: "outlined",
                "hide-details": "auto",
                class: "siqi-input",
                "prepend-inner-icon": "mdi-reload",
                disabled: formLocked.value,
                "error-messages": fieldErrors.http_retry_times ? [fieldErrors.http_retry_times] : [],
                "aria-invalid": Boolean(fieldErrors.http_retry_times)
              }, null, 8, ["modelValue", "disabled", "error-messages", "aria-invalid"]),
              _hoisted_54
            ]),
            _createElementVNode("div", _hoisted_55, [
              _createVNode(_component_v_text_field, {
                modelValue: config.http_retry_delay,
                "onUpdate:modelValue": [
                  _cache[23] || (_cache[23] = $event => ((config.http_retry_delay) = $event)),
                  _cache[24] || (_cache[24] = $event => (clearFieldError('http_retry_delay')))
                ],
                label: "重试间隔（毫秒）",
                type: "text",
                inputmode: "numeric",
                min: "200",
                max: "60000",
                density: "compact",
                variant: "outlined",
                "hide-details": "auto",
                class: "siqi-input",
                "prepend-inner-icon": "mdi-timer-outline",
                disabled: formLocked.value,
                "error-messages": fieldErrors.http_retry_delay ? [fieldErrors.http_retry_delay] : [],
                "aria-invalid": Boolean(fieldErrors.http_retry_delay)
              }, null, 8, ["modelValue", "disabled", "error-messages", "aria-invalid"]),
              _hoisted_56
            ])
          ])
        ]),
        _createElementVNode("div", _hoisted_57, [
          _createElementVNode("div", _hoisted_58, [
            _createElementVNode("span", _hoisted_59, [
              _createVNode(_component_v_icon, {
                icon: "mdi-web-sync",
                size: "18",
                color: "#22c55e",
                class: "mr-1"
              }),
              _createTextVNode("站点凭据 ")
            ])
          ]),
          _createElementVNode("div", _hoisted_60, [
            _createVNode(_component_v_icon, {
              icon: "mdi-shield-check-outline",
              size: "20"
            }),
            _hoisted_61
          ])
        ])
      ])
    ], 8, _hoisted_12)
  ]))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-e2955237"]]);

export { ConfigView as default };
