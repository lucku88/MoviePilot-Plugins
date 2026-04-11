import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_b9a47b86_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-b9a47b86"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "sqfarm-config-page" };
const _hoisted_2 = { class: "sqfarm-config-shell" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-config-copy" }, [
  /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-config-badge" }, "Vue-农场"),
  /*#__PURE__*/_createElementVNode("h1", { class: "sqfarm-config-title" }, "插件配置"),
  /*#__PURE__*/_createElementVNode("p", { class: "sqfarm-config-subtitle" }, "收菜、种植、出售、获取执行记录。")
], -1));
const _hoisted_4 = { class: "sqfarm-config-actions" };
const _hoisted_5 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-config-kicker" }, "基本设置", -1));
const _hoisted_6 = { class: "sqfarm-switch-card" };
const _hoisted_7 = { class: "sqfarm-switch-card" };
const _hoisted_8 = { class: "sqfarm-switch-card" };
const _hoisted_9 = { class: "sqfarm-switch-card" };
const _hoisted_10 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-config-kicker" }, "功能设置", -1));
const _hoisted_11 = { class: "sqfarm-switch-card" };
const _hoisted_12 = { class: "sqfarm-switch-card" };
const _hoisted_13 = { class: "sqfarm-switch-card" };
const _hoisted_14 = { class: "sqfarm-field-card" };
const _hoisted_15 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-field-title" }, "站点 Cookie", -1));
const _hoisted_16 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-field-note" }, "启用后自动读取站点 Cookie，关闭后才可手动修改。", -1));
const _hoisted_17 = { class: "sqfarm-field-card" };
const _hoisted_18 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-field-title" }, "优先种子", -1));
const _hoisted_19 = { class: "sqfarm-field-card" };
const _hoisted_20 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-field-title" }, "OCR API 地址", -1));
const _hoisted_21 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-config-kicker" }, "OCR 说明", -1));
const _hoisted_22 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-field-note" }, " 批量收菜验证码依赖 OCR。未配置 OCR 时，插件仍可刷新状态，并在批量收获失败后尝试逐坑位兜底收菜。 ", -1));
const _hoisted_23 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", { class: "sqfarm-field-note" }, [
  /*#__PURE__*/_createTextVNode(" 推荐先部署 "),
  /*#__PURE__*/_createElementVNode("code", null, "trwebocr"),
  /*#__PURE__*/_createTextVNode("，再把 OCR 地址填成 "),
  /*#__PURE__*/_createElementVNode("code", null, "http://ip:8089/api/tr-run/"),
  /*#__PURE__*/_createTextVNode("。 ")
], -1));

const {computed,onMounted,reactive,ref} = await importShared('vue');


const ocrComposeExample = `version: '3.8'
services:
  trwebocr:
    image: mmmz/trwebocr:latest
    container_name: trwebocr
    ports:
      - "8089:8089"
    restart: always
    environment:
      - TZ=Asia/Shanghai`;


const _sfc_main = {
  __name: 'Config',
  props: {
  initialConfig: {
    type: Object,
    default: () => ({}),
  },
  api: {
    type: Object,
    default: () => ({}),
  },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;





const saving = ref(false);
const message = reactive({ text: '', type: 'success' });
const seedOptions = ref(['西红柿']);
const config = reactive({
  enabled: false,
  notify: true,
  onlyonce: false,
  auto_cookie: true,
  enable_sell: true,
  enable_plant: true,
  use_proxy: false,
  force_ipv4: true,
  cookie: '',
  ocr_api_url: 'http://ip:8089/api/tr-run/',
  prefer_seed: '西红柿',
});

const cookieReadonly = computed(() => !!config.auto_cookie);
const cookieFieldValue = computed({
  get() {
    if (config.auto_cookie) {
      return truncateCookie(config.cookie)
    }
    return config.cookie
  },
  set(value) {
    if (!config.auto_cookie) {
      config.cookie = value || '';
    }
  },
});

function flash(text, type = 'success') {
  message.text = text;
  message.type = type;
}

function truncateCookie(value) {
  const text = String(value || '').trim();
  if (!text) return ''
  return text.length > 36 ? `${text.slice(0, 36)}...` : text
}

function normalizeSeeds(items) {
  const normalized = (items || [])
    .map((item) => (typeof item === 'string' ? item : item?.value || item?.name || ''))
    .filter(Boolean);

  if (config.prefer_seed && !normalized.includes(config.prefer_seed)) {
    normalized.unshift(config.prefer_seed);
  }

  return normalized.length ? normalized : ['西红柿', '萝卜', '玉米', '茄子', '蘑菇', '樱桃']
}

function applySeedOptions(items) {
  seedOptions.value = normalizeSeeds(items);
}

function applyStatusSeedOptions(seedShop) {
  const unlocked = (seedShop || [])
    .filter((seed) => seed.unlocked && seed.name)
    .map((seed) => seed.name);
  if (unlocked.length) {
    applySeedOptions(unlocked);
  }
}

async function loadStatusSeedOptions() {
  try {
    const res = await props.api.get('/plugin/VueFarm/status');
    applyStatusSeedOptions(res?.farm_status?.seed_shop);
  } catch (error) {
    // 保留当前种子列表
  }
}

async function loadConfig() {
  try {
    const res = await props.api.get('/plugin/VueFarm/config');
    Object.assign(config, res || {});
    applySeedOptions(res?.seed_options);
    await loadStatusSeedOptions();
  } catch (error) {
    flash(error?.message || '加载配置失败', 'error');
  }
}

async function saveConfig() {
  saving.value = true;
  try {
    const res = await props.api.post('/plugin/VueFarm/config', { ...config });
    if (res.config) {
      Object.assign(config, res.config);
      applySeedOptions(res.config.seed_options);
    }
    flash(res.message || '配置已保存');
    if (config.onlyonce) {
      config.onlyonce = false;
    }
  } catch (error) {
    flash(error?.message || '保存失败', 'error');
  } finally {
    saving.value = false;
  }
}

async function syncCookie() {
  saving.value = true;
  try {
    const res = await props.api.get('/plugin/VueFarm/cookie');
    if (res.config) {
      Object.assign(config, res.config);
      applySeedOptions(res.config.seed_options);
    }
    await loadStatusSeedOptions();
    flash(res.message || 'Cookie 已同步');
  } catch (error) {
    flash(error?.message || '同步 Cookie 失败', 'error');
  } finally {
    saving.value = false;
  }
}

function closePlugin() {
  emit('close');
}

onMounted(() => {
  loadConfig();
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_card_item = _resolveComponent("v-card-item");
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_select = _resolveComponent("v-select");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createVNode(_component_v_card, {
        class: "sqfarm-config-card",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_text, { class: "sqfarm-config-hero" }, {
            default: _withCtx(() => [
              _hoisted_3,
              _createElementVNode("div", _hoisted_4, [
                _createVNode(_component_v_btn, {
                  variant: "text",
                  onClick: _cache[0] || (_cache[0] = $event => (emit('switch', 'page')))
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("返回状态页")
                  ]),
                  _: 1
                }),
                _createVNode(_component_v_btn, {
                  color: "warning",
                  variant: "flat",
                  loading: saving.value,
                  onClick: syncCookie
                }, {
                  default: _withCtx(() => [
                    _createTextVNode("同步 Cookie")
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
                    _createTextVNode("保存")
                  ]),
                  _: 1
                }, 8, ["loading"]),
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
            rounded: "xl"
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(message.text), 1)
            ]),
            _: 1
          }, 8, ["type"]))
        : _createCommentVNode("", true),
      _createVNode(_component_v_card, {
        class: "sqfarm-config-card",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_item, null, {
            prepend: _withCtx(() => [
              _hoisted_5
            ]),
            default: _withCtx(() => [
              _createVNode(_component_v_card_title, null, {
                default: _withCtx(() => [
                  _createTextVNode("基础开关")
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_v_card_text, null, {
            default: _withCtx(() => [
              _createVNode(_component_v_row, null, {
                default: _withCtx(() => [
                  _createVNode(_component_v_col, {
                    cols: "12",
                    md: "6",
                    xl: "3"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_6, [
                        _createVNode(_component_v_switch, {
                          modelValue: config.enabled,
                          "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.enabled) = $event)),
                          label: "启用插件",
                          color: "#7c5cff",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, {
                    cols: "12",
                    md: "6",
                    xl: "3"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_7, [
                        _createVNode(_component_v_switch, {
                          modelValue: config.use_proxy,
                          "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.use_proxy) = $event)),
                          label: "使用代理",
                          color: "#7c5cff",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, {
                    cols: "12",
                    md: "6",
                    xl: "3"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_8, [
                        _createVNode(_component_v_switch, {
                          modelValue: config.notify,
                          "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.notify) = $event)),
                          label: "开启通知",
                          color: "#7c5cff",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, {
                    cols: "12",
                    md: "6",
                    xl: "3"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_9, [
                        _createVNode(_component_v_switch, {
                          modelValue: config.onlyonce,
                          "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.onlyonce) = $event)),
                          label: "立即运行一次",
                          color: "#7c5cff",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ])
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
      }),
      _createVNode(_component_v_card, {
        class: "sqfarm-config-card",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_item, null, {
            prepend: _withCtx(() => [
              _hoisted_10
            ]),
            default: _withCtx(() => [
              _createVNode(_component_v_card_title, null, {
                default: _withCtx(() => [
                  _createTextVNode("农场流程")
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_v_card_text, null, {
            default: _withCtx(() => [
              _createVNode(_component_v_row, null, {
                default: _withCtx(() => [
                  _createVNode(_component_v_col, {
                    cols: "12",
                    md: "4"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_11, [
                        _createVNode(_component_v_switch, {
                          modelValue: config.auto_cookie,
                          "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.auto_cookie) = $event)),
                          label: "使用站点 Cookie",
                          color: "#7c5cff",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, {
                    cols: "12",
                    md: "4"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_12, [
                        _createVNode(_component_v_switch, {
                          modelValue: config.enable_sell,
                          "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.enable_sell) = $event)),
                          label: "自动出售",
                          color: "#7c5cff",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, {
                    cols: "12",
                    md: "4"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_13, [
                        _createVNode(_component_v_switch, {
                          modelValue: config.enable_plant,
                          "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.enable_plant) = $event)),
                          label: "自动种植",
                          color: "#7c5cff",
                          density: "compact",
                          "hide-details": "",
                          inset: ""
                        }, null, 8, ["modelValue"])
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }),
              _createVNode(_component_v_row, { class: "mt-1" }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_col, {
                    cols: "12",
                    lg: "4"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_14, [
                        _hoisted_15,
                        _createVNode(_component_v_text_field, {
                          modelValue: cookieFieldValue.value,
                          "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((cookieFieldValue).value = $event)),
                          label: "站点 Cookie",
                          variant: "outlined",
                          density: "comfortable",
                          disabled: cookieReadonly.value,
                          readonly: cookieReadonly.value,
                          placeholder: cookieReadonly.value ? '启用站点 Cookie 后自动同步' : '例如 c_secure_pass=...',
                          "hide-details": "auto"
                        }, null, 8, ["modelValue", "disabled", "readonly", "placeholder"]),
                        _hoisted_16
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, {
                    cols: "12",
                    lg: "4"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_17, [
                        _hoisted_18,
                        _createVNode(_component_v_select, {
                          modelValue: config.prefer_seed,
                          "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((config.prefer_seed) = $event)),
                          items: seedOptions.value,
                          label: "优先种子",
                          variant: "outlined",
                          density: "comfortable",
                          "menu-props": { maxHeight: 280 },
                          "hide-details": "auto"
                        }, null, 8, ["modelValue", "items"])
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, {
                    cols: "12",
                    lg: "4"
                  }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_19, [
                        _hoisted_20,
                        _createVNode(_component_v_text_field, {
                          modelValue: config.ocr_api_url,
                          "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((config.ocr_api_url) = $event)),
                          label: "OCR API 地址",
                          variant: "outlined",
                          density: "comfortable",
                          placeholder: "http://ip:8089/api/tr-run/",
                          "hide-details": "auto"
                        }, null, 8, ["modelValue"])
                      ])
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
      }),
      _createVNode(_component_v_card, {
        class: "sqfarm-config-card",
        rounded: "xl",
        flat: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_card_item, null, {
            prepend: _withCtx(() => [
              _hoisted_21
            ]),
            default: _withCtx(() => [
              _createVNode(_component_v_card_title, null, {
                default: _withCtx(() => [
                  _createTextVNode("验证码识别")
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_v_card_text, null, {
            default: _withCtx(() => [
              _hoisted_22,
              _hoisted_23,
              _createElementVNode("pre", { class: "sqfarm-code" }, _toDisplayString(ocrComposeExample))
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
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-b9a47b86"]]);

export { ConfigView as default };
