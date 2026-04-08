import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_7379666b_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-7379666b"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "cover-page" };
const _hoisted_2 = { class: "cover-shell" };
const _hoisted_3 = { class: "hero-card" };
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "hero-kicker" }, "媒体库封面生成魔改"),
  /*#__PURE__*/_createElementVNode("h1", { class: "hero-title" }, "数据页"),
  /*#__PURE__*/_createElementVNode("p", { class: "hero-subtitle" }, " 手动触发媒体库封面生成，查看最新输出、飞牛回写结果，以及当前媒体服务器探测信息。 ")
], -1));
const _hoisted_5 = { class: "hero-actions" };
const _hoisted_6 = { class: "metric-grid" };
const _hoisted_7 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "metric-label" }, "运行状态", -1));
const _hoisted_8 = { class: "metric-value" };
const _hoisted_9 = { class: "metric-desc" };
const _hoisted_10 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "metric-label" }, "最近运行", -1));
const _hoisted_11 = { class: "metric-value small" };
const _hoisted_12 = { class: "metric-desc" };
const _hoisted_13 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "metric-label" }, "生成数量", -1));
const _hoisted_14 = { class: "metric-value" };
const _hoisted_15 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "metric-desc" }, "最近一次执行成功生成的媒体库数量", -1));
const _hoisted_16 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "metric-label" }, "回写数量", -1));
const _hoisted_17 = { class: "metric-value" };
const _hoisted_18 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "metric-desc" }, "最近一次成功自动替换的飞牛媒体库数量", -1));
const _hoisted_19 = { class: "panel-card" };
const _hoisted_20 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "panel-kicker" }, "最新输出"),
    /*#__PURE__*/_createElementVNode("h2", null, "媒体库封面预览")
  ])
], -1));
const _hoisted_21 = {
  key: 0,
  class: "preview-grid"
};
const _hoisted_22 = {
  key: 1,
  class: "preview-fallback"
};
const _hoisted_23 = { class: "preview-body" };
const _hoisted_24 = { class: "preview-title" };
const _hoisted_25 = { class: "preview-meta" };
const _hoisted_26 = { class: "chip-row" };
const _hoisted_27 = { class: "preview-message" };
const _hoisted_28 = { class: "preview-file" };
const _hoisted_29 = {
  key: 1,
  class: "empty-box"
};
const _hoisted_30 = { class: "dual-grid" };
const _hoisted_31 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "panel-kicker" }, "执行历史"),
    /*#__PURE__*/_createElementVNode("h2", null, "最近任务")
  ])
], -1));
const _hoisted_32 = {
  key: 0,
  class: "history-list"
};
const _hoisted_33 = { class: "history-time" };
const _hoisted_34 = { class: "history-message" };
const _hoisted_35 = {
  key: 1,
  class: "empty-box"
};
const _hoisted_36 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "panel-head" }, [
  /*#__PURE__*/_createElementVNode("div", null, [
    /*#__PURE__*/_createElementVNode("div", { class: "panel-kicker" }, "运行探测"),
    /*#__PURE__*/_createElementVNode("h2", null, "飞牛连接信息")
  ])
], -1));
const _hoisted_37 = { class: "inspect-box" };

const {computed,onMounted,reactive,ref} = await importShared('vue');


const pluginBase = '/plugin/MediaCoverRemix';

const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['switch'],
  setup(__props, { emit }) {

const props = __props;





const loading = ref(false);
const running = ref(false);
const inspecting = ref(false);
const message = reactive({ text: '', type: 'success' });
const status = reactive({
  enabled: false,
  running: false,
  last_run: '',
  latest_result: {},
  history: [],
  inspect: {},
});

const resultItems = computed(() => status.latest_result?.items || []);
const historyItems = computed(() => status.history || []);
const inspectText = computed(() => JSON.stringify(status.inspect || {}, null, 2));

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function applyStatus(data = {}) {
  Object.assign(status, {
    ...status,
    ...data,
  });
}

async function loadStatus() {
  loading.value = true;
  try {
    const data = await props.api.get(`${pluginBase}/status`);
    applyStatus(data || {});
  } catch (error) {
    flash(error?.message || '读取状态失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function refreshStatus() {
  loading.value = true;
  try {
    const data = await props.api.post(`${pluginBase}/refresh`, {});
    applyStatus(data?.status || data || {});
    flash('状态已刷新');
  } catch (error) {
    flash(error?.message || '刷新状态失败', 'error');
  } finally {
    loading.value = false;
  }
}

async function inspectRuntime() {
  inspecting.value = true;
  try {
    const data = await props.api.get(`${pluginBase}/inspect`);
    status.inspect = data || {};
    flash('飞牛连接探测已更新');
  } catch (error) {
    flash(error?.message || '探测失败', 'error');
  } finally {
    inspecting.value = false;
  }
}

async function runNow() {
  running.value = true;
  try {
    const data = await props.api.post(`${pluginBase}/run`, {});
    applyStatus(data?.status || status);
    status.latest_result = data || {};
    flash(data?.message || '任务已执行');
  } catch (error) {
    flash(error?.message || '执行失败', 'error');
  } finally {
    running.value = false;
  }
}

onMounted(() => {
  loadStatus();
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_img = _resolveComponent("v-img");
  const _component_v_chip = _resolveComponent("v-chip");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("section", _hoisted_3, [
        _hoisted_4,
        _createElementVNode("div", _hoisted_5, [
          _createVNode(_component_v_btn, {
            variant: "text",
            onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'config')))
          }, {
            default: _withCtx(() => [
              _createTextVNode("打开配置页")
            ]),
            _: 1
          }),
          _createVNode(_component_v_btn, {
            color: "info",
            variant: "flat",
            loading: loading.value,
            onClick: refreshStatus
          }, {
            default: _withCtx(() => [
              _createTextVNode("刷新状态")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            color: "secondary",
            variant: "flat",
            loading: inspecting.value,
            onClick: inspectRuntime
          }, {
            default: _withCtx(() => [
              _createTextVNode("探测飞牛连接")
            ]),
            _: 1
          }, 8, ["loading"]),
          _createVNode(_component_v_btn, {
            color: "primary",
            variant: "flat",
            loading: running.value,
            onClick: runNow
          }, {
            default: _withCtx(() => [
              _createTextVNode("立即生成")
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
        _createVNode(_component_v_card, {
          class: "metric-card",
          rounded: "xl"
        }, {
          default: _withCtx(() => [
            _hoisted_7,
            _createElementVNode("div", _hoisted_8, _toDisplayString(status.running ? '执行中' : '空闲'), 1),
            _createElementVNode("div", _hoisted_9, "启用状态：" + _toDisplayString(status.enabled ? '已启用' : '未启用'), 1)
          ]),
          _: 1
        }),
        _createVNode(_component_v_card, {
          class: "metric-card",
          rounded: "xl"
        }, {
          default: _withCtx(() => [
            _hoisted_10,
            _createElementVNode("div", _hoisted_11, _toDisplayString(status.last_run || '-'), 1),
            _createElementVNode("div", _hoisted_12, _toDisplayString(status.latest_result?.message || '暂无执行记录'), 1)
          ]),
          _: 1
        }),
        _createVNode(_component_v_card, {
          class: "metric-card",
          rounded: "xl"
        }, {
          default: _withCtx(() => [
            _hoisted_13,
            _createElementVNode("div", _hoisted_14, _toDisplayString(status.latest_result?.generated_count || 0), 1),
            _hoisted_15
          ]),
          _: 1
        }),
        _createVNode(_component_v_card, {
          class: "metric-card",
          rounded: "xl"
        }, {
          default: _withCtx(() => [
            _hoisted_16,
            _createElementVNode("div", _hoisted_17, _toDisplayString(status.latest_result?.uploaded_count || 0), 1),
            _hoisted_18
          ]),
          _: 1
        })
      ]),
      _createElementVNode("section", _hoisted_19, [
        _hoisted_20,
        (resultItems.value.length)
          ? (_openBlock(), _createElementBlock("div", _hoisted_21, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(resultItems.value, (item) => {
                return (_openBlock(), _createBlock(_component_v_card, {
                  key: `${item.server}-${item.library_id}`,
                  class: "preview-card",
                  rounded: "xl"
                }, {
                  default: _withCtx(() => [
                    (item.preview_url)
                      ? (_openBlock(), _createBlock(_component_v_img, {
                          key: 0,
                          src: item.preview_url,
                          cover: "",
                          class: "preview-image"
                        }, null, 8, ["src"]))
                      : (_openBlock(), _createElementBlock("div", _hoisted_22, "无预览")),
                    _createElementVNode("div", _hoisted_23, [
                      _createElementVNode("div", _hoisted_24, _toDisplayString(item.library_name), 1),
                      _createElementVNode("div", _hoisted_25, _toDisplayString(item.server) + " / " + _toDisplayString(item.library_id), 1),
                      _createElementVNode("div", _hoisted_26, [
                        _createVNode(_component_v_chip, {
                          color: item.success ? 'success' : 'error',
                          size: "small",
                          variant: "tonal"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(item.success ? '已生成' : '失败'), 1)
                          ]),
                          _: 2
                        }, 1032, ["color"]),
                        _createVNode(_component_v_chip, {
                          color: item.uploaded ? 'primary' : 'default',
                          size: "small",
                          variant: "tonal"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(item.uploaded ? '已回写' : '未回写'), 1)
                          ]),
                          _: 2
                        }, 1032, ["color"])
                      ]),
                      _createElementVNode("p", _hoisted_27, _toDisplayString(item.message), 1),
                      _createElementVNode("div", _hoisted_28, _toDisplayString(item.output_name || item.output_file), 1)
                    ])
                  ]),
                  _: 2
                }, 1024))
              }), 128))
            ]))
          : (_openBlock(), _createElementBlock("div", _hoisted_29, " 暂无生成结果。先到配置页选中飞牛影视媒体库，再点击“立即生成”。 "))
      ]),
      _createElementVNode("section", _hoisted_30, [
        _createVNode(_component_v_card, {
          class: "panel-card",
          rounded: "xl"
        }, {
          default: _withCtx(() => [
            _hoisted_31,
            (historyItems.value.length)
              ? (_openBlock(), _createElementBlock("div", _hoisted_32, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(historyItems.value, (item, index) => {
                    return (_openBlock(), _createElementBlock("div", {
                      key: index,
                      class: "history-item"
                    }, [
                      _createElementVNode("div", null, [
                        _createElementVNode("div", _hoisted_33, _toDisplayString(item.time), 1),
                        _createElementVNode("div", _hoisted_34, _toDisplayString(item.message), 1)
                      ]),
                      _createVNode(_component_v_chip, {
                        color: item.success ? 'success' : 'error',
                        size: "small",
                        variant: "tonal"
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(item.success ? '成功' : '失败'), 1)
                        ]),
                        _: 2
                      }, 1032, ["color"])
                    ]))
                  }), 128))
                ]))
              : (_openBlock(), _createElementBlock("div", _hoisted_35, "暂无历史记录。"))
          ]),
          _: 1
        }),
        _createVNode(_component_v_card, {
          class: "panel-card",
          rounded: "xl"
        }, {
          default: _withCtx(() => [
            _hoisted_36,
            _createElementVNode("div", _hoisted_37, [
              _createElementVNode("pre", null, _toDisplayString(inspectText.value), 1)
            ])
          ]),
          _: 1
        })
      ])
    ])
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-7379666b"]]);

export { PageView as default };
