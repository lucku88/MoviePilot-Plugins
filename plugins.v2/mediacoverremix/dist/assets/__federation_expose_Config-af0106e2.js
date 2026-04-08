import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_8218022d_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-8218022d"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "cover-config" };
const _hoisted_2 = { class: "cover-shell" };
const _hoisted_3 = { class: "hero-card" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "hero-kicker" }, "媒体库封面生成魔改"),
  /*#__PURE__*/_createElementVNode("h1", { class: "hero-title" }, "配置页"),
  /*#__PURE__*/_createElementVNode("p", { class: "hero-subtitle" }, " 读取 MoviePilot 已配置的飞牛影视媒体库，按媒体库现有海报拼贴出新的封面图，并尝试自动回写。 ")
], -1));
const _hoisted_5 = { class: "hero-actions" };
const _hoisted_6 = { class: "panel-card" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "panel-kicker" }, "运行控制"),
    /*#__PURE__*/_createElementVNode("h2", null, "基础参数")
  ])
], -1));
const _hoisted_8 = { class: "switch-grid" };
const _hoisted_9 = { class: "form-grid mt-4" };
const _hoisted_10 = { class: "panel-card" };
const _hoisted_11 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "panel-kicker" }, "数据源"),
    /*#__PURE__*/_createElementVNode("h2", null, "MoviePilot 与媒体库选择")
  ])
], -1));
const _hoisted_12 = { class: "form-grid" };
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("p", { class: "panel-note" }, " 不选媒体库时默认处理所选服务器下的全部媒体库。飞牛影视推荐只勾选需要替换封面的库，便于控制频率和回写风险。 ", -1));
const _hoisted_14 = { class: "panel-card" };
const _hoisted_15 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "panel-kicker" }, "样式"),
    /*#__PURE__*/_createElementVNode("h2", null, "封面输出")
  ])
], -1));
const _hoisted_16 = { class: "form-grid" };
const _hoisted_17 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("p", { class: "panel-note" }, " 默认从首张海报提取背景氛围。如果你希望统一风格，可以填一个十六进制颜色覆盖背景色调。 ", -1));
const _hoisted_18 = { class: "panel-card" };
const _hoisted_19 = { class: "panel-head" };
const _hoisted_20 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "panel-kicker" }, "标题规则"),
  /*#__PURE__*/_createElementVNode("h2", null, "媒体库命名映射")
], -1));
const _hoisted_21 = {
  key: 0,
  class: "rule-list"
};
const _hoisted_22 = {
  key: 1,
  class: "empty-box"
};
const _hoisted_23 = { class: "panel-card" };
const _hoisted_24 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "panel-kicker" }, "说明"),
    /*#__PURE__*/_createElementVNode("h2", null, "当前行为")
  ])
], -1));
const _hoisted_25 = { class: "note-list" };

const {onMounted,reactive,ref} = await importShared('vue');


const pluginBase = '/plugin/MediaCoverRemix';

const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['switch'],
  setup(__props, { emit }) {

const props = __props;





const loading = ref(false);
const saving = ref(false);
const serverOptions = ref([]);
const libraryOptions = ref([]);
const notes = ref([]);
const message = reactive({ text: '', type: 'success' });
const config = reactive({
  enabled: false,
  notify: false,
  onlyonce: false,
  auto_upload: true,
  cron: '',
  moviepilot_url: '',
  moviepilot_api_token: '',
  selected_servers: [],
  include_libraries: [],
  title_rules: [],
  image_count: 4,
  history_limit: 30,
  http_timeout: 20,
  poster_width: 1600,
  poster_height: 900,
  custom_bg_color: '',
});

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function applyConfig(data = {}) {
  serverOptions.value = data.server_options || [];
  libraryOptions.value = data.library_options || [];
  notes.value = data.notes || [];
  Object.assign(config, {
    ...config,
    ...data,
    selected_servers: [...(data.selected_servers || [])],
    include_libraries: [...(data.include_libraries || [])],
    title_rules: [...(data.title_rules || [])],
  });
}

async function loadConfig() {
  loading.value = true;
  try {
    const data = await props.api.get(`${pluginBase}/config`);
    applyConfig(data || {});
  } catch (error) {
    flash(error?.message || '读取配置失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const result = await props.api.post(`${pluginBase}/config`, {
      ...config,
      title_rules: config.title_rules.filter((rule) => rule.match || rule.title || rule.subtitle),
    });
    applyConfig(result?.config || {});
    flash(result?.message || '配置已保存');
  } catch (error) {
    flash(error?.message || '保存配置失败', 'error');
  } finally {
    saving.value = false;
  }
}

async function refreshLibraries() {
  loading.value = true;
  try {
    const result = await props.api.post(`${pluginBase}/refresh`, {});
    libraryOptions.value = result?.library_options || result?.status?.library_options || [];
    flash('媒体库缓存已刷新');
  } catch (error) {
    flash(error?.message || '刷新媒体库失败', 'error');
  } finally {
    loading.value = false;
  }
}

function addRule() {
  config.title_rules.push({ match: '', title: '', subtitle: '' });
}

function removeRule(index) {
  config.title_rules.splice(index, 1);
}

onMounted(() => {
  applyConfig(props.initialConfig || {});
  loadConfig();
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_select = _resolveComponent("v-select");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("section", _hoisted_3, [
        _hoisted_4,
        _createElementVNode("div", _hoisted_5, [
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
            color: "info",
            variant: "flat",
            loading: loading.value,
            onClick: refreshLibraries
          }, {
            default: _withCtx(() => [
              _createTextVNode("刷新媒体库")
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
          }, 8, ["loading"])
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
      _createElementVNode("section", _hoisted_6, [
        _hoisted_7,
        _createElementVNode("div", _hoisted_8, [
          _createVNode(_component_v_switch, {
            modelValue: config.enabled,
            "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
            label: "启用插件",
            color: "success",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.auto_upload,
            "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.auto_upload) = $event)),
            label: "生成后自动替换飞牛封面",
            color: "primary",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.onlyonce,
            "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.onlyonce) = $event)),
            label: "保存后立即执行一次",
            color: "warning",
            "hide-details": ""
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_switch, {
            modelValue: config.notify,
            "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.notify) = $event)),
            label: "保留通知开关",
            color: "secondary",
            "hide-details": ""
          }, null, 8, ["modelValue"])
        ]),
        _createElementVNode("div", _hoisted_9, [
          _createVNode(_component_v_text_field, {
            modelValue: config.cron,
            "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.cron) = $event)),
            label: "定时 Cron",
            placeholder: "0 4 * * *",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.image_count,
            "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.image_count) = $event)),
            label: "拼贴海报数",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.history_limit,
            "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.history_limit) = $event)),
            label: "历史记录数",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.http_timeout,
            "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((config.http_timeout) = $event)),
            label: "HTTP 超时(秒)",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"])
        ])
      ]),
      _createElementVNode("section", _hoisted_10, [
        _hoisted_11,
        _createElementVNode("div", _hoisted_12, [
          _createVNode(_component_v_text_field, {
            modelValue: config.moviepilot_url,
            "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.moviepilot_url) = $event)),
            label: "MoviePilot 地址",
            placeholder: "http://127.0.0.1:3000",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.moviepilot_api_token,
            "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.moviepilot_api_token) = $event)),
            label: "MoviePilot API Token",
            placeholder: "X-API-KEY 对应的 Token",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_select, {
            modelValue: config.selected_servers,
            "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((config.selected_servers) = $event)),
            items: serverOptions.value,
            "item-title": "title",
            "item-value": "value",
            label: "媒体服务器",
            multiple: "",
            chips: "",
            clearable: "",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue", "items"]),
          _createVNode(_component_v_select, {
            modelValue: config.include_libraries,
            "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((config.include_libraries) = $event)),
            items: libraryOptions.value,
            "item-title": "title",
            "item-value": "value",
            label: "限定媒体库",
            multiple: "",
            chips: "",
            clearable: "",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue", "items"])
        ]),
        _hoisted_13
      ]),
      _createElementVNode("section", _hoisted_14, [
        _hoisted_15,
        _createElementVNode("div", _hoisted_16, [
          _createVNode(_component_v_text_field, {
            modelValue: config.poster_width,
            "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((config.poster_width) = $event)),
            label: "封面宽度",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.poster_height,
            "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((config.poster_height) = $event)),
            label: "封面高度",
            type: "number",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"]),
          _createVNode(_component_v_text_field, {
            modelValue: config.custom_bg_color,
            "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((config.custom_bg_color) = $event)),
            label: "背景色覆盖",
            placeholder: "#182233",
            variant: "outlined",
            density: "comfortable"
          }, null, 8, ["modelValue"])
        ]),
        _hoisted_17
      ]),
      _createElementVNode("section", _hoisted_18, [
        _createElementVNode("div", _hoisted_19, [
          _hoisted_20,
          _createVNode(_component_v_btn, {
            size: "small",
            variant: "tonal",
            onClick: addRule
          }, {
            default: _withCtx(() => [
              _createTextVNode("新增规则")
            ]),
            _: 1
          })
        ]),
        (config.title_rules.length)
          ? (_openBlock(), _createElementBlock("div", _hoisted_21, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(config.title_rules, (rule, index) => {
                return (_openBlock(), _createElementBlock("div", {
                  key: index,
                  class: "rule-row"
                }, [
                  _createVNode(_component_v_text_field, {
                    modelValue: rule.match,
                    "onUpdate:modelValue": $event => ((rule.match) = $event),
                    label: "匹配词",
                    variant: "outlined",
                    density: "comfortable"
                  }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                  _createVNode(_component_v_text_field, {
                    modelValue: rule.title,
                    "onUpdate:modelValue": $event => ((rule.title) = $event),
                    label: "主标题",
                    variant: "outlined",
                    density: "comfortable"
                  }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                  _createVNode(_component_v_text_field, {
                    modelValue: rule.subtitle,
                    "onUpdate:modelValue": $event => ((rule.subtitle) = $event),
                    label: "副标题",
                    variant: "outlined",
                    density: "comfortable"
                  }, null, 8, ["modelValue", "onUpdate:modelValue"]),
                  _createVNode(_component_v_btn, {
                    variant: "text",
                    color: "error",
                    onClick: $event => (removeRule(index))
                  }, {
                    default: _withCtx(() => [
                      _createTextVNode("删除")
                    ]),
                    _: 2
                  }, 1032, ["onClick"])
                ]))
              }), 128))
            ]))
          : (_openBlock(), _createElementBlock("div", _hoisted_22, " 暂无标题规则。默认直接使用飞牛影视里的媒体库名称和类型。 "))
      ]),
      _createElementVNode("section", _hoisted_23, [
        _hoisted_24,
        _createElementVNode("ul", _hoisted_25, [
          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(notes.value, (note, index) => {
            return (_openBlock(), _createElementBlock("li", { key: index }, _toDisplayString(note), 1))
          }), 128))
        ])
      ])
    ])
  ]))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-8218022d"]]);

export { ConfigView as default };
