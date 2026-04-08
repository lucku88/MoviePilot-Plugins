import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_89cf5756_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock,renderList:_renderList,Fragment:_Fragment,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-89cf5756"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "pc-shell" };
const _hoisted_2 = { class: "pc-hero" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "pc-badge" }, "自用签到"),
  /*#__PURE__*/_createElementVNode("h1", { class: "pc-title" }, "配置页"),
  /*#__PURE__*/_createElementVNode("p", { class: "pc-subtitle" }, "把签到页、Cookie、CF 策略和 New API / 思齐类特殊逻辑统一放在一个任务编排面板里。")
], -1));
const _hoisted_4 = { class: "pc-actions" };
const _hoisted_5 = { class: "pc-grid" };
const _hoisted_6 = { class: "pc-panel" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pc-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "pc-kicker" }, "运行控制"),
    /*#__PURE__*/_createElementVNode("h2", null, "全局调度")
  ])
], -1));
const _hoisted_8 = { class: "pc-switch-grid" };
const _hoisted_9 = { class: "pc-form-grid" };
const _hoisted_10 = { class: "pc-panel" };
const _hoisted_11 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pc-panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "pc-kicker" }, "CF 与网络"),
    /*#__PURE__*/_createElementVNode("h2", null, "请求环境")
  ])
], -1));
const _hoisted_12 = { class: "pc-form-grid" };
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "pc-note-list" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "pc-note" }, "`自动` 会按 `请求 -> Playwright -> FlareSolverr` 顺序兜底。"),
  /*#__PURE__*/_createElementVNode("div", { class: "pc-note" }, "你提到的 `ourbits / hddolby / ubits / audiences` 已默认给成 `Playwright`，因为它们是浏览器打开签到页即可自动完成的模式。"),
  /*#__PURE__*/_createElementVNode("div", { class: "pc-note" }, "如果站点已经配置在 MoviePilot 站点管理里，可以打开“优先使用 MoviePilot Cookie”；否则直接把浏览器 Cookie 贴到任务里。")
], -1));
const _hoisted_14 = { class: "pc-panel" };
const _hoisted_15 = { class: "pc-panel-head pc-panel-head-wrap" };
const _hoisted_16 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "pc-kicker" }, "任务编排"),
  /*#__PURE__*/_createElementVNode("h2", null, "签到/领取任务列表")
], -1));
const _hoisted_17 = { class: "pc-actions" };
const _hoisted_18 = {
  key: 0,
  class: "pc-empty"
};
const _hoisted_19 = { class: "pc-task-title" };
const _hoisted_20 = { class: "pc-mini" };
const _hoisted_21 = { class: "pc-title-meta" };
const _hoisted_22 = { class: "pc-form-grid" };
const _hoisted_23 = { class: "pc-switch-grid pc-switch-grid-tight" };
const _hoisted_24 = { class: "pc-form-grid" };
const _hoisted_25 = {
  key: 0,
  class: "pc-form-grid"
};
const _hoisted_26 = { class: "pc-task-footer" };
const _hoisted_27 = { class: "pc-mini" };

const {onBeforeUnmount,onMounted,reactive,ref} = await importShared('vue');



const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;





const rootEl = ref(null);
const isDarkTheme = ref(false);
const saving = ref(false);
const taskSeed = ref(1);
const message = reactive({ text: '', type: 'success' });
const taskTypeOptions = ref([
  { title: '通用签到页', value: 'generic_attendance' },
  { title: '思齐签到', value: 'siqi_attendance' },
  { title: '思齐 HNR 领取', value: 'siqi_hnr_claim' },
  { title: 'New API 签到', value: 'new_api_checkin' },
]);
const cfModeOptions = ref([
  { title: '自动', value: 'auto' },
  { title: '仅请求', value: 'request' },
  { title: '仅 Playwright', value: 'playwright' },
  { title: '仅 FlareSolverr', value: 'flaresolverr' },
]);

const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  force_ipv4: true,
  cron: '0 9 * * *',
  max_workers: 2,
  random_delay_max_seconds: 5,
  http_timeout: 18,
  http_retry_times: 3,
  http_retry_delay: 1500,
  flaresolverr_url: '',
  tasks: [],
});

let themeObserver = null;
let observedThemeNode = null;

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function clone(value) {
  return JSON.parse(JSON.stringify(value))
}

function createDefaultTasks() {
  return [
    {
      id: 'ourbits-attendance',
      name: '我堡签到',
      enabled: true,
      task_type: 'generic_attendance',
      site_url: 'https://ourbits.club',
      target_url: 'https://ourbits.club/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'ourbits.club',
      cookie: '',
      user_agent: '',
      cf_mode: 'playwright',
      success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
      failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'hddolby-attendance',
      name: '杜比签到',
      enabled: true,
      task_type: 'generic_attendance',
      site_url: 'https://www.hddolby.com',
      target_url: 'https://www.hddolby.com/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'hddolby.com',
      cookie: '',
      user_agent: '',
      cf_mode: 'playwright',
      success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
      failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'ubits-attendance',
      name: 'UBits 签到',
      enabled: true,
      task_type: 'generic_attendance',
      site_url: 'https://ubits.club',
      target_url: 'https://ubits.club/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'ubits.club',
      cookie: '',
      user_agent: '',
      cf_mode: 'playwright',
      success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
      failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'audiences-attendance',
      name: '观众签到',
      enabled: true,
      task_type: 'generic_attendance',
      site_url: 'https://audiences.me',
      target_url: 'https://audiences.me/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'audiences.me',
      cookie: '',
      user_agent: '',
      cf_mode: 'playwright',
      success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
      failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'siqi-attendance',
      name: '思齐签到',
      enabled: true,
      task_type: 'siqi_attendance',
      site_url: 'https://si-qi.xyz',
      target_url: 'https://si-qi.xyz/attendance.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'si-qi.xyz',
      cookie: '',
      user_agent: '',
      cf_mode: 'request',
      success_keywords: '',
      failure_keywords: '',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'siqi-hnr',
      name: '思齐 HNR 领取',
      enabled: true,
      task_type: 'siqi_hnr_claim',
      site_url: 'https://si-qi.xyz',
      target_url: 'https://si-qi.xyz/hnrview.php',
      use_moviepilot_cookie: true,
      moviepilot_domain: 'si-qi.xyz',
      cookie: '',
      user_agent: '',
      cf_mode: 'request',
      success_keywords: '',
      failure_keywords: '',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
    {
      id: 'new-api-checkin',
      name: 'New API 签到',
      enabled: true,
      task_type: 'new_api_checkin',
      site_url: 'https://open.xingyungept.cn',
      target_url: 'https://open.xingyungept.cn/console/personal',
      use_moviepilot_cookie: false,
      moviepilot_domain: 'open.xingyungept.cn',
      cookie: '',
      user_agent: '',
      cf_mode: 'request',
      success_keywords: '',
      failure_keywords: '',
      allow_logged_in_as_success: true,
      use_proxy: false,
      force_ipv4: true,
      new_api_uid: '',
    },
  ]
}

function createBlankTask() {
  const id = `task-${Date.now()}-${taskSeed.value++}`;
  return {
    id,
    name: `新任务 ${taskSeed.value}`,
    enabled: true,
    task_type: 'generic_attendance',
    site_url: '',
    target_url: '',
    use_moviepilot_cookie: false,
    moviepilot_domain: '',
    cookie: '',
    user_agent: '',
    cf_mode: 'auto',
    success_keywords: '签到成功|今日已签到|已经签到|已签到|签到已得|already signed|already attended|check-in completed',
    failure_keywords: 'Cookie已失效|未登录|请先登录|重新登录|login required',
    allow_logged_in_as_success: true,
    use_proxy: false,
    force_ipv4: true,
    new_api_uid: '',
  }
}

function resolveTaskTypeLabel(value) {
  return taskTypeOptions.value.find((item) => item.value === value)?.title || value
}

function resolveCfModeLabel(value) {
  return cfModeOptions.value.find((item) => item.value === value)?.title || value
}

function taskTypeDescription(type) {
  if (type === 'siqi_attendance') return '内置思齐 attendance.php 验证码识别与提交逻辑。'
  if (type === 'siqi_hnr_claim') return '内置思齐 HNR 页面解析与奖励领取逻辑。'
  if (type === 'new_api_checkin') return '内置 New API /api/user/checkin 查询与签到逻辑，需要额外填写 UID。'
  return '适合 PT 站或其他站点的签到页场景；打开目标地址即可触发签到。'
}

function findThemeNode() {
  let current = rootEl.value;
  while (current) {
    if (current.getAttribute?.('data-theme')) {
      return current
    }
    current = current.parentElement;
  }
  if (document.body?.getAttribute('data-theme')) return document.body
  if (document.documentElement?.getAttribute('data-theme')) return document.documentElement
  return null
}

function detectTheme() {
  const node = findThemeNode();
  const themeValue = node?.getAttribute?.('data-theme') || '';
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  isDarkTheme.value = ['dark', 'purple', 'transparent'].includes(themeValue) || (!themeValue && !!prefersDark);
}

function bindThemeObserver() {
  themeObserver?.disconnect();
  themeObserver = new MutationObserver(() => {
    const nextNode = findThemeNode();
    if (nextNode && nextNode !== observedThemeNode) {
      bindThemeObserver();
      return
    }
    detectTheme();
  });

  observedThemeNode = findThemeNode();
  if (observedThemeNode) {
    themeObserver.observe(observedThemeNode, { attributes: true, attributeFilter: ['data-theme'] });
  }
  themeObserver.observe(document.documentElement, { attributes: true, subtree: true, attributeFilter: ['data-theme'] });
  if (document.body) {
    themeObserver.observe(document.body, { attributes: true, subtree: true, attributeFilter: ['data-theme'] });
  }
}

function applyConfig(payload) {
  config.enabled = !!payload.enabled;
  config.notify = !!payload.notify;
  config.onlyonce = !!payload.onlyonce;
  config.use_proxy = !!payload.use_proxy;
  config.force_ipv4 = payload.force_ipv4 !== false;
  config.cron = payload.cron || '0 9 * * *';
  config.max_workers = payload.max_workers ?? 2;
  config.random_delay_max_seconds = payload.random_delay_max_seconds ?? 5;
  config.http_timeout = payload.http_timeout ?? 18;
  config.http_retry_times = payload.http_retry_times ?? 3;
  config.http_retry_delay = payload.http_retry_delay ?? 1500;
  config.flaresolverr_url = payload.flaresolverr_url || '';
  config.tasks = clone(payload.tasks || createDefaultTasks());
  taskTypeOptions.value = payload.task_type_options || taskTypeOptions.value;
  cfModeOptions.value = payload.cf_mode_options || cfModeOptions.value;
}

async function loadConfig() {
  try {
    const payload = await props.api.get('/plugin/PrivateCheckin/config');
    applyConfig(payload || {});
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error');
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const payload = await props.api.post('/plugin/PrivateCheckin/config', clone(config));
    applyConfig(payload?.config || config);
    flash(payload?.message || '配置已保存');
  } catch (error) {
    flash(error?.message || '保存配置失败', 'error');
  } finally {
    saving.value = false;
  }
}

function addTask() {
  config.tasks.push(createBlankTask());
}

function removeTask(index) {
  config.tasks.splice(index, 1);
}

function resetDefaults() {
  config.tasks = createDefaultTasks();
  flash('已恢复默认示例任务，可继续按需修改', 'info');
}

onMounted(() => {
  loadConfig();
  detectTheme();
  bindThemeObserver();
});

onBeforeUnmount(() => {
  themeObserver?.disconnect();
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_expansion_panel_title = _resolveComponent("v-expansion-panel-title");
  const _component_v_select = _resolveComponent("v-select");
  const _component_v_textarea = _resolveComponent("v-textarea");
  const _component_v_expansion_panel_text = _resolveComponent("v-expansion-panel-text");
  const _component_v_expansion_panel = _resolveComponent("v-expansion-panel");
  const _component_v_expansion_panels = _resolveComponent("v-expansion-panels");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "rootEl",
    ref: rootEl,
    class: _normalizeClass(["pc-config", { 'is-dark-theme': isDarkTheme.value }])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _createElementVNode("section", _hoisted_2, [
        _hoisted_3,
        _createElementVNode("div", _hoisted_4, [
          _createVNode(_component_v_btn, {
            variant: "text",
            onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'page')))
          }, {
            default: _withCtx(() => [
              _createTextVNode("返回数据页")
            ]),
            _: 1
          }),
          _createVNode(_component_v_btn, {
            color: "warning",
            variant: "flat",
            loading: saving.value,
            onClick: resetDefaults
          }, {
            default: _withCtx(() => [
              _createTextVNode("恢复默认示例")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            color: "primary",
            variant: "flat",
            loading: saving.value,
            onClick: saveConfig
          }, {
            default: _withCtx(() => [
              _createTextVNode("保存配置")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            variant: "text",
            onClick: _cache[1] || (_cache[1] = $event => (emit('close')))
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
      _createElementVNode("section", _hoisted_5, [
        _createElementVNode("article", _hoisted_6, [
          _hoisted_7,
          _createElementVNode("div", _hoisted_8, [
            _createVNode(_component_v_switch, {
              modelValue: config.enabled,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.enabled) = $event)),
              label: "启用插件",
              color: "success",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.notify,
              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.notify) = $event)),
              label: "发送通知",
              color: "primary",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.onlyonce,
              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.onlyonce) = $event)),
              label: "保存后立即运行一次",
              color: "warning",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.use_proxy,
              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.use_proxy) = $event)),
              label: "默认使用系统代理",
              color: "info",
              "hide-details": ""
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_switch, {
              modelValue: config.force_ipv4,
              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.force_ipv4) = $event)),
              label: "默认优先 IPv4",
              color: "secondary",
              "hide-details": ""
            }, null, 8, ["modelValue"])
          ]),
          _createElementVNode("div", _hoisted_9, [
            _createVNode(_component_v_text_field, {
              modelValue: config.cron,
              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.cron) = $event)),
              label: "执行周期",
              hint: "5 位 Cron，例如 0 9 * * *",
              "persistent-hint": "",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.max_workers,
              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.max_workers) = $event)),
              type: "number",
              label: "并发任务数",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.random_delay_max_seconds,
              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.random_delay_max_seconds) = $event)),
              type: "number",
              label: "随机延迟上限(秒)",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"])
          ])
        ]),
        _createElementVNode("article", _hoisted_10, [
          _hoisted_11,
          _createElementVNode("div", _hoisted_12, [
            _createVNode(_component_v_text_field, {
              modelValue: config.http_timeout,
              "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.http_timeout) = $event)),
              type: "number",
              label: "HTTP 超时(秒)",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.http_retry_times,
              "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.http_retry_times) = $event)),
              type: "number",
              label: "重试次数",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.http_retry_delay,
              "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.http_retry_delay) = $event)),
              type: "number",
              label: "重试间隔(ms)",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"]),
            _createVNode(_component_v_text_field, {
              modelValue: config.flaresolverr_url,
              "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.flaresolverr_url) = $event)),
              label: "FlareSolverr 地址",
              placeholder: "http://flaresolverr:8191/v1",
              hint: "MoviePilot V2 已自带 Playwright。只有强 CF 仍过不去时，再额外部署 FlareSolverr。",
              "persistent-hint": "",
              variant: "outlined",
              density: "comfortable"
            }, null, 8, ["modelValue"])
          ]),
          _hoisted_13
        ])
      ]),
      _createElementVNode("section", _hoisted_14, [
        _createElementVNode("div", _hoisted_15, [
          _hoisted_16,
          _createElementVNode("div", _hoisted_17, [
            _createVNode(_component_v_btn, {
              color: "success",
              variant: "flat",
              onClick: addTask
            }, {
              default: _withCtx(() => [
                _createTextVNode("新增空白任务")
              ]),
              _: 1
            })
          ])
        ]),
        _createVNode(_component_v_alert, {
          type: "info",
          variant: "tonal",
          class: "mb-4"
        }, {
          default: _withCtx(() => [
            _createTextVNode(" 通用任务只需要填签到页地址；特殊任务里 `思齐签到 / 思齐 HNR 领取 / New API 签到` 会走内置逻辑。`New API` 还需要补一个 UID。 ")
          ]),
          _: 1
        }),
        (!config.tasks.length)
          ? (_openBlock(), _createElementBlock("div", _hoisted_18, " 暂无任务，点击“新增空白任务”或“恢复默认示例”开始。 "))
          : (_openBlock(), _createBlock(_component_v_expansion_panels, {
              key: 1,
              multiple: "",
              class: "pc-panels"
            }, {
              default: _withCtx(() => [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(config.tasks, (task, index) => {
                  return (_openBlock(), _createBlock(_component_v_expansion_panel, {
                    key: task.id
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_expansion_panel_title, null, {
                        default: _withCtx(() => [
                          _createElementVNode("div", _hoisted_19, [
                            _createElementVNode("div", null, [
                              _createElementVNode("strong", null, _toDisplayString(task.name || `任务 ${index + 1}`), 1),
                              _createElementVNode("div", _hoisted_20, _toDisplayString(resolveTaskTypeLabel(task.task_type)), 1)
                            ]),
                            _createElementVNode("div", _hoisted_21, [
                              _createVNode(_component_v_chip, {
                                size: "small",
                                color: task.enabled ? 'success' : 'default',
                                variant: "tonal"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(task.enabled ? '启用' : '停用'), 1)
                                ]),
                                _: 2
                              }, 1032, ["color"]),
                              _createVNode(_component_v_chip, {
                                size: "small",
                                color: "primary",
                                variant: "tonal"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(resolveCfModeLabel(task.cf_mode)), 1)
                                ]),
                                _: 2
                              }, 1024)
                            ])
                          ])
                        ]),
                        _: 2
                      }, 1024),
                      _createVNode(_component_v_expansion_panel_text, null, {
                        default: _withCtx(() => [
                          _createElementVNode("div", _hoisted_22, [
                            _createVNode(_component_v_text_field, {
                              modelValue: task.name,
                              "onUpdate:modelValue": $event => ((task.name) = $event),
                              label: "任务名称",
                              variant: "outlined",
                              density: "comfortable"
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_v_select, {
                              modelValue: task.task_type,
                              "onUpdate:modelValue": $event => ((task.task_type) = $event),
                              items: taskTypeOptions.value,
                              label: "任务类型",
                              variant: "outlined",
                              density: "comfortable"
                            }, null, 8, ["modelValue", "onUpdate:modelValue", "items"]),
                            _createVNode(_component_v_text_field, {
                              modelValue: task.site_url,
                              "onUpdate:modelValue": $event => ((task.site_url) = $event),
                              label: "站点地址",
                              placeholder: "https://example.com",
                              variant: "outlined",
                              density: "comfortable"
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_v_text_field, {
                              modelValue: task.target_url,
                              "onUpdate:modelValue": $event => ((task.target_url) = $event),
                              label: "签到/任务地址",
                              placeholder: "https://example.com/attendance.php",
                              variant: "outlined",
                              density: "comfortable"
                            }, null, 8, ["modelValue", "onUpdate:modelValue"])
                          ]),
                          _createElementVNode("div", _hoisted_23, [
                            _createVNode(_component_v_switch, {
                              modelValue: task.enabled,
                              "onUpdate:modelValue": $event => ((task.enabled) = $event),
                              label: "启用任务",
                              color: "success",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_v_switch, {
                              modelValue: task.use_moviepilot_cookie,
                              "onUpdate:modelValue": $event => ((task.use_moviepilot_cookie) = $event),
                              label: "优先使用 MoviePilot Cookie",
                              color: "info",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_v_switch, {
                              modelValue: task.use_proxy,
                              "onUpdate:modelValue": $event => ((task.use_proxy) = $event),
                              label: "该任务使用代理",
                              color: "secondary",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_v_switch, {
                              modelValue: task.force_ipv4,
                              "onUpdate:modelValue": $event => ((task.force_ipv4) = $event),
                              label: "该任务优先 IPv4",
                              color: "secondary",
                              "hide-details": ""
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            (task.task_type === 'generic_attendance')
                              ? (_openBlock(), _createBlock(_component_v_switch, {
                                  key: 0,
                                  modelValue: task.allow_logged_in_as_success,
                                  "onUpdate:modelValue": $event => ((task.allow_logged_in_as_success) = $event),
                                  label: "浏览器访问成功即视为通过",
                                  color: "warning",
                                  "hide-details": ""
                                }, null, 8, ["modelValue", "onUpdate:modelValue"]))
                              : _createCommentVNode("", true)
                          ]),
                          _createElementVNode("div", _hoisted_24, [
                            _createVNode(_component_v_text_field, {
                              modelValue: task.moviepilot_domain,
                              "onUpdate:modelValue": $event => ((task.moviepilot_domain) = $event),
                              label: "MoviePilot 站点域名",
                              placeholder: "ourbits.club",
                              hint: "用于站点 Cookie 同步；不填会自动从地址里提取。",
                              "persistent-hint": "",
                              variant: "outlined",
                              density: "comfortable"
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            _createVNode(_component_v_select, {
                              modelValue: task.cf_mode,
                              "onUpdate:modelValue": $event => ((task.cf_mode) = $event),
                              items: cfModeOptions.value,
                              label: "CF 策略",
                              variant: "outlined",
                              density: "comfortable"
                            }, null, 8, ["modelValue", "onUpdate:modelValue", "items"]),
                            _createVNode(_component_v_text_field, {
                              modelValue: task.user_agent,
                              "onUpdate:modelValue": $event => ((task.user_agent) = $event),
                              label: "自定义 User-Agent",
                              placeholder: "留空则使用内置默认 UA",
                              variant: "outlined",
                              density: "comfortable"
                            }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                            (task.task_type === 'new_api_checkin')
                              ? (_openBlock(), _createBlock(_component_v_text_field, {
                                  key: 0,
                                  modelValue: task.new_api_uid,
                                  "onUpdate:modelValue": $event => ((task.new_api_uid) = $event),
                                  label: "New API UID",
                                  placeholder: "例如 225",
                                  variant: "outlined",
                                  density: "comfortable"
                                }, null, 8, ["modelValue", "onUpdate:modelValue"]))
                              : _createCommentVNode("", true)
                          ]),
                          _createVNode(_component_v_textarea, {
                            modelValue: task.cookie,
                            "onUpdate:modelValue": $event => ((task.cookie) = $event),
                            label: "手动 Cookie",
                            rows: "4",
                            "auto-grow": "",
                            variant: "outlined",
                            density: "comfortable",
                            placeholder: "例如 cf_clearance=...; passkey=...",
                            class: "mb-4"
                          }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                          (task.task_type === 'generic_attendance')
                            ? (_openBlock(), _createElementBlock("div", _hoisted_25, [
                                _createVNode(_component_v_textarea, {
                                  modelValue: task.success_keywords,
                                  "onUpdate:modelValue": $event => ((task.success_keywords) = $event),
                                  label: "成功关键字 / 正则",
                                  rows: "3",
                                  "auto-grow": "",
                                  variant: "outlined",
                                  density: "comfortable",
                                  placeholder: "支持用 | 分隔多个关键字"
                                }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                                _createVNode(_component_v_textarea, {
                                  modelValue: task.failure_keywords,
                                  "onUpdate:modelValue": $event => ((task.failure_keywords) = $event),
                                  label: "失败关键字 / 正则",
                                  rows: "3",
                                  "auto-grow": "",
                                  variant: "outlined",
                                  density: "comfortable",
                                  placeholder: "支持用 | 分隔多个关键字"
                                }, null, 8, ["modelValue", "onUpdate:modelValue"])
                              ]))
                            : _createCommentVNode("", true),
                          _createElementVNode("div", _hoisted_26, [
                            _createElementVNode("div", _hoisted_27, _toDisplayString(taskTypeDescription(task.task_type)), 1),
                            _createVNode(_component_v_btn, {
                              color: "error",
                              variant: "tonal",
                              onClick: $event => (removeTask(index))
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode("删除任务")
                              ]),
                              _: 2
                            }, 1032, ["onClick"])
                          ])
                        ]),
                        _: 2
                      }, 1024)
                    ]),
                    _: 2
                  }, 1024))
                }), 128))
              ]),
              _: 1
            }))
      ])
    ])
  ], 2))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-89cf5756"]]);

export { ConfigView as default };
