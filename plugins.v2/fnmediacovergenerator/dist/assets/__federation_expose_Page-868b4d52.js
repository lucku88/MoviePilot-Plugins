import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_9c595c5a_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,withModifiers:_withModifiers,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-9c595c5a"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "cover-page" };
const _hoisted_2 = { class: "hero-card" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "hero-kicker" }, "FnMediaCoverGenerator", -1));
const _hoisted_4 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("h1", { class: "hero-title" }, "飞牛影视媒体库封面生成", -1));
const _hoisted_5 = { class: "hero-meta" };
const _hoisted_6 = { class: "hero-actions" };
const _hoisted_7 = { class: "summary-main" };
const _hoisted_8 = { class: "summary-sub" };
const _hoisted_9 = { class: "action-row" };
const _hoisted_10 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "text-body-2 text-medium-emphasis" }, "点击风格卡片可直接切换；风格切换后会同步刷新当前状态。", -1));
const _hoisted_11 = { class: "d-flex align-center justify-space-between ga-2" };
const _hoisted_12 = { class: "text-subtitle-1 font-weight-medium" };
const _hoisted_13 = { class: "text-caption text-medium-emphasis" };
const _hoisted_14 = { class: "action-row" };
const _hoisted_15 = { class: "text-body-2 text-medium-emphasis" };
const _hoisted_16 = { class: "d-flex flex-wrap ga-2 justify-end" };
const _hoisted_17 = { class: "history-check" };
const _hoisted_18 = { class: "text-body-2 history-name" };
const _hoisted_19 = { class: "text-caption text-medium-emphasis" };

const {computed,onMounted,reactive,ref} = await importShared('vue');


const PLUGIN_ID = 'FnMediaCoverGenerator';

const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: Object, required: true },
  show_switch: { type: Boolean, default: true },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;

const pluginBase = `plugin/${PLUGIN_ID}`;





const loading = ref(false);
const actionKey = ref('');
const tab = ref('generate');
const state = reactive({
  latest_message: '',
  latest_time: '',
  setup_warnings: [],
  cover_style: 'static_1',
  cover_style_index: 1,
  history_limit: 0,
  history_items: [],
  style_cards: [],
});
const selectedPaths = ref([]);
const message = reactive({ text: '', type: 'info' });

const historyItems = computed(() => state.history_items || []);
const show_switch = computed(() => props.show_switch !== false);

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value ?? {}))
}

function assignState(payload) {
  const next = cloneValue(payload);
  Object.keys(state).forEach((key) => {
    state[key] = next[key] ?? (Array.isArray(state[key]) ? [] : '');
  });
  Object.entries(next).forEach(([key, value]) => {
    state[key] = value;
  });
  const visible = new Set((next.history_items || []).map((item) => item.path));
  selectedPaths.value = selectedPaths.value.filter((item) => visible.has(item));
}

async function refreshData() {
  loading.value = true;
  try {
    const result = await props.api.get(`${pluginBase}/page_data`);
    assignState(result?.data || {});
  } catch (error) {
    message.type = 'error';
    message.text = error?.message || '页面数据加载失败';
  } finally {
    loading.value = false;
  }
}

async function runAction(key, apiPath, payload = {}) {
  actionKey.value = key;
  try {
    const result = await props.api.post(apiPath, payload);
    message.type = result?.success === false ? 'warning' : 'success';
    message.text = result?.message || '操作已完成';
    await refreshData();
  } catch (error) {
    message.type = 'error';
    message.text = error?.message || '操作失败';
  } finally {
    actionKey.value = '';
  }
}

function isSelected(path) {
  return selectedPaths.value.includes(path)
}

function toggleHistorySelection(path) {
  if (!path) {
    return
  }
  if (isSelected(path)) {
    selectedPaths.value = selectedPaths.value.filter((item) => item !== path);
    return
  }
  selectedPaths.value = [...selectedPaths.value, path];
}

function selectAllHistory() {
  selectedPaths.value = historyItems.value.map((item) => item.path).filter(Boolean);
}

function clearHistorySelection() {
  selectedPaths.value = [];
}

async function deleteSelectedHistory() {
  if (!selectedPaths.value.length) {
    return
  }
  if (!window.confirm(`确认删除已选的 ${selectedPaths.value.length} 张历史封面吗？`)) {
    return
  }
  const current = [...selectedPaths.value];
  await runAction('delete-selected', `${pluginBase}/delete_saved_cover`, { files: current });
  selectedPaths.value = [];
}

async function deleteSingleHistory(item) {
  if (!item?.path) {
    return
  }
  if (!window.confirm(`确认删除 ${item.name || '这张封面'} 吗？`)) {
    return
  }
  await runAction(`delete-${item.path}`, `${pluginBase}/delete_saved_cover`, { file: item.path });
  selectedPaths.value = selectedPaths.value.filter((path) => path !== item.path);
}

onMounted(() => {
  refreshData();
});

return (_ctx, _cache) => {
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_tab = _resolveComponent("v-tab");
  const _component_v_tabs = _resolveComponent("v-tabs");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_img = _resolveComponent("v-img");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_window_item = _resolveComponent("v-window-item");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_window = _resolveComponent("v-window");

  return (_openBlock(), _createElementBlock("section", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("div", null, [
        _hoisted_3,
        _hoisted_4,
        _createElementVNode("div", _hoisted_5, [
          _createVNode(_component_v_chip, {
            size: "small",
            color: "primary",
            variant: "flat"
          }, {
            default: _withCtx(() => [
              _createTextVNode("当前风格 " + _toDisplayString(state.cover_style || 'static_1'), 1)
            ]),
            _: 1
          }),
          _createElementVNode("span", null, "最近执行时间：" + _toDisplayString(state.latest_time || '-'), 1)
        ])
      ]),
      _createElementVNode("div", _hoisted_6, [
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
        (show_switch.value)
          ? (_openBlock(), _createBlock(_component_v_btn, {
              key: 0,
              color: "primary",
              variant: "text",
              onClick: _cache[0] || (_cache[0] = $event => (emit('switch')))
            }, {
              default: _withCtx(() => [
                _createTextVNode("配置")
              ]),
              _: 1
            }))
          : _createCommentVNode("", true),
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
          variant: "tonal"
        }, {
          default: _withCtx(() => [
            _createTextVNode(_toDisplayString(message.text), 1)
          ]),
          _: 1
        }, 8, ["type"]))
      : _createCommentVNode("", true),
    _createVNode(_component_v_card, { variant: "outlined" }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_text, { class: "summary-card" }, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_7, _toDisplayString(state.latest_message || '还没有执行记录'), 1),
            _createElementVNode("div", _hoisted_8, _toDisplayString(state.latest_time || '-'), 1),
            _createVNode(_component_v_alert, {
              type: state.setup_warnings?.length ? 'warning' : 'info',
              variant: "tonal",
              density: "compact",
              class: "mt-4"
            }, {
              default: _withCtx(() => [
                _createTextVNode(_toDisplayString(state.setup_warnings?.length ? state.setup_warnings.join('；') : '当前风格会直接作用于飞牛媒体库静态封面。'), 1)
              ]),
              _: 1
            }, 8, ["type"])
          ]),
          _: 1
        })
      ]),
      _: 1
    }),
    _createVNode(_component_v_card, { variant: "outlined" }, {
      default: _withCtx(() => [
        _createVNode(_component_v_tabs, {
          modelValue: tab.value,
          "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((tab).value = $event)),
          color: "primary",
          grow: ""
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_tab, { value: "generate" }, {
              default: _withCtx(() => [
                _createTextVNode("封面生成")
              ]),
              _: 1
            }),
            _createVNode(_component_v_tab, { value: "history" }, {
              default: _withCtx(() => [
                _createTextVNode("历史封面")
              ]),
              _: 1
            }),
            _createVNode(_component_v_tab, { value: "clean" }, {
              default: _withCtx(() => [
                _createTextVNode("清理缓存")
              ]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["modelValue"]),
        _createVNode(_component_v_divider),
        _createVNode(_component_v_window, {
          modelValue: tab.value,
          "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((tab).value = $event))
        }, {
          default: _withCtx(() => [
            _createVNode(_component_v_window_item, { value: "generate" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_text, null, {
                  default: _withCtx(() => [
                    _createElementVNode("div", _hoisted_9, [
                      _hoisted_10,
                      _createVNode(_component_v_btn, {
                        color: "primary",
                        variant: "flat",
                        loading: actionKey.value === 'generate',
                        onClick: _cache[3] || (_cache[3] = $event => (runAction('generate', `${pluginBase}/generate_now`)))
                      }, {
                        default: _withCtx(() => [
                          _createTextVNode(" 立即生成当前风格 ")
                        ]),
                        _: 1
                      }, 8, ["loading"])
                    ]),
                    _createVNode(_component_v_row, null, {
                      default: _withCtx(() => [
                        (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(state.style_cards || [], (card) => {
                          return (_openBlock(), _createBlock(_component_v_col, {
                            key: card.index,
                            cols: "12",
                            sm: "6",
                            md: "3"
                          }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_card, {
                                class: _normalizeClass(["style-card", { selected: card.selected }]),
                                elevation: card.selected ? 6 : 2,
                                onClick: $event => (runAction(`style-${card.index}`, `${pluginBase}/select_style_${card.index}`))
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_img, {
                                    src: card.preview_src,
                                    "aspect-ratio": "16/9",
                                    cover: ""
                                  }, null, 8, ["src"]),
                                  _createVNode(_component_v_card_text, { class: "py-3" }, {
                                    default: _withCtx(() => [
                                      _createElementVNode("div", _hoisted_11, [
                                        _createElementVNode("div", null, [
                                          _createElementVNode("div", _hoisted_12, _toDisplayString(card.name), 1),
                                          _createElementVNode("div", _hoisted_13, _toDisplayString(card.variant), 1)
                                        ]),
                                        _createVNode(_component_v_chip, {
                                          color: card.selected ? 'primary' : 'default',
                                          size: "small",
                                          variant: card.selected ? 'flat' : 'outlined'
                                        }, {
                                          default: _withCtx(() => [
                                            _createTextVNode(_toDisplayString(card.selected ? '当前' : '切换'), 1)
                                          ]),
                                          _: 2
                                        }, 1032, ["color", "variant"])
                                      ])
                                    ]),
                                    _: 2
                                  }, 1024)
                                ]),
                                _: 2
                              }, 1032, ["class", "elevation", "onClick"])
                            ]),
                            _: 2
                          }, 1024))
                        }), 128))
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_window_item, { value: "history" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_text, null, {
                  default: _withCtx(() => [
                    _createElementVNode("div", _hoisted_14, [
                      _createElementVNode("div", _hoisted_15, " 最多展示 " + _toDisplayString(state.history_limit || 0) + " 张历史封面。现在勾选只在当前页面本地生效，删除时才会请求后端，所以不会再一张一闪。 ", 1),
                      _createElementVNode("div", _hoisted_16, [
                        _createVNode(_component_v_btn, {
                          variant: "text",
                          size: "small",
                          disabled: !historyItems.value.length,
                          onClick: selectAllHistory
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode("全选当前页")
                          ]),
                          _: 1
                        }, 8, ["disabled"]),
                        _createVNode(_component_v_btn, {
                          variant: "text",
                          size: "small",
                          disabled: !selectedPaths.value.length,
                          onClick: clearHistorySelection
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode("清空选择")
                          ]),
                          _: 1
                        }, 8, ["disabled"]),
                        _createVNode(_component_v_btn, {
                          color: "error",
                          variant: "flat",
                          size: "small",
                          disabled: !selectedPaths.value.length,
                          loading: actionKey.value === 'delete-selected',
                          onClick: deleteSelectedHistory
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(" 删除已选（" + _toDisplayString(selectedPaths.value.length) + "） ", 1)
                          ]),
                          _: 1
                        }, 8, ["disabled", "loading"])
                      ])
                    ]),
                    (historyItems.value.length)
                      ? (_openBlock(), _createBlock(_component_v_row, { key: 0 }, {
                          default: _withCtx(() => [
                            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(historyItems.value, (item) => {
                              return (_openBlock(), _createBlock(_component_v_col, {
                                key: item.path,
                                cols: "12",
                                sm: "6",
                                md: "4",
                                lg: "3"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_v_card, {
                                    class: _normalizeClass(["history-card", { selected: isSelected(item.path) }]),
                                    variant: "flat",
                                    elevation: "3"
                                  }, {
                                    default: _withCtx(() => [
                                      _createElementVNode("div", _hoisted_17, [
                                        _createVNode(_component_v_btn, {
                                          size: "small",
                                          color: isSelected(item.path) ? 'primary' : 'default',
                                          variant: isSelected(item.path) ? 'flat' : 'outlined',
                                          onClick: _withModifiers($event => (toggleHistorySelection(item.path)), ["stop"])
                                        }, {
                                          default: _withCtx(() => [
                                            _createTextVNode(_toDisplayString(isSelected(item.path) ? '已选' : '选择'), 1)
                                          ]),
                                          _: 2
                                        }, 1032, ["color", "variant", "onClick"])
                                      ]),
                                      _createVNode(_component_v_img, {
                                        src: item.src,
                                        "aspect-ratio": "16/9",
                                        cover: "",
                                        onClick: $event => (toggleHistorySelection(item.path))
                                      }, null, 8, ["src", "onClick"]),
                                      _createVNode(_component_v_card_text, { class: "pb-2" }, {
                                        default: _withCtx(() => [
                                          _createElementVNode("div", _hoisted_18, _toDisplayString(item.name), 1),
                                          _createElementVNode("div", _hoisted_19, _toDisplayString(item.mtime) + " / " + _toDisplayString(item.size), 1)
                                        ]),
                                        _: 2
                                      }, 1024),
                                      _createVNode(_component_v_card_actions, { class: "pt-0" }, {
                                        default: _withCtx(() => [
                                          _createVNode(_component_v_btn, {
                                            color: "error",
                                            variant: "text",
                                            size: "small",
                                            loading: actionKey.value === `delete-${item.path}`,
                                            onClick: _withModifiers($event => (deleteSingleHistory(item)), ["stop"])
                                          }, {
                                            default: _withCtx(() => [
                                              _createTextVNode(" 删除 ")
                                            ]),
                                            _: 2
                                          }, 1032, ["loading", "onClick"])
                                        ]),
                                        _: 2
                                      }, 1024)
                                    ]),
                                    _: 2
                                  }, 1032, ["class"])
                                ]),
                                _: 2
                              }, 1024))
                            }), 128))
                          ]),
                          _: 1
                        }))
                      : (_openBlock(), _createBlock(_component_v_alert, {
                          key: 1,
                          type: "info",
                          variant: "tonal"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode("还没有可展示的历史封面。")
                          ]),
                          _: 1
                        }))
                  ]),
                  _: 1
                })
              ]),
              _: 1
            }),
            _createVNode(_component_v_window_item, { value: "clean" }, {
              default: _withCtx(() => [
                _createVNode(_component_v_card_text, { class: "clean-grid" }, {
                  default: _withCtx(() => [
                    _createVNode(_component_v_card, {
                      variant: "tonal",
                      color: "error"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_card_title, null, {
                          default: _withCtx(() => [
                            _createTextVNode("清理图片缓存")
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_card_text, null, {
                          default: _withCtx(() => [
                            _createTextVNode("只会清理生成源图缓存，不会删除已保存的历史封面。")
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_card_actions, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_btn, {
                              color: "error",
                              variant: "flat",
                              loading: actionKey.value === 'clean-images',
                              onClick: _cache[4] || (_cache[4] = $event => (runAction('clean-images', `${pluginBase}/clean_images`)))
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode(" 立即清理 ")
                              ]),
                              _: 1
                            }, 8, ["loading"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_v_card, {
                      variant: "tonal",
                      color: "warning"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_card_title, null, {
                          default: _withCtx(() => [
                            _createTextVNode("清理字体缓存")
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_card_text, null, {
                          default: _withCtx(() => [
                            _createTextVNode("清理后会重新下载或重新读取你配置的字体资源。")
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_card_actions, null, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_btn, {
                              color: "warning",
                              variant: "flat",
                              loading: actionKey.value === 'clean-fonts',
                              onClick: _cache[5] || (_cache[5] = $event => (runAction('clean-fonts', `${pluginBase}/clean_fonts`)))
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode(" 立即清理 ")
                              ]),
                              _: 1
                            }, 8, ["loading"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              _: 1
            })
          ]),
          _: 1
        }, 8, ["modelValue"])
      ]),
      _: 1
    })
  ]))
}
}

};
const PageView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-9c595c5a"]]);

export { PageView as default };
