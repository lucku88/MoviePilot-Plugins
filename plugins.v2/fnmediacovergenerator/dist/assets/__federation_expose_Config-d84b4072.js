import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const {resolveDynamicComponent:_resolveDynamicComponent,openBlock:_openBlock$1,createBlock:_createBlock$1} = await importShared('vue');


const {h,resolveComponent} = await importShared('vue');



const _sfc_main$1 = {
  __name: 'FormRender',
  props: {
  config: {
    type: Object,
    required: true,
  },
  model: {
    type: Object,
    required: true,
  },
},
  setup(__props) {



const isExpression = (value) => typeof value === 'string' && value.startsWith('{{') && value.endsWith('}}');
const extractExpression = (value) => value.slice(2, -2).trim();

const parseProps = (rawProps = {}, model) => {
  const parsedProps = {};

  Object.entries(rawProps).forEach(([key, value]) => {
    if (key === 'modelvalue') {
      parsedProps.value = model[value];
      parsedProps['onUpdate:value'] = (newValue) => {
        model[value] = newValue;
      };
      return
    }

    if (key === 'model' || key === 'v-model') {
      parsedProps.modelValue = model[value];
      parsedProps['onUpdate:modelValue'] = (newValue) => {
        model[value] = newValue;
      };
      return
    }

    if (key.startsWith('model:') || key.startsWith('v-model:')) {
      const propName = key.split(':')[1];
      parsedProps[propName] = model[value];
      parsedProps[`onUpdate:${propName}`] = (newValue) => {
        model[value] = newValue;
      };
      return
    }

    if (typeof value === 'string' && isExpression(value)) {
      const expression = extractExpression(value);
      parsedProps[key] = new Function('model', `with(model) { return ${expression} }`)(model);
      return
    }

    if (typeof value === 'string' && value in model) {
      parsedProps[key] = model[value];
      return
    }

    parsedProps[key] = value;
  });

  return parsedProps
};

const renderComponent = (config, model) => {
  const { component, props: componentProps = {}, content = [], html, text } = config;
  const Component = resolveComponent(component);
  const parsedProps = parseProps(componentProps, model);

  const renderContent = () => {
    if (html) {
      return h(Component, { innerHTML: typeof html === 'string' ? html : model[html] })
    }
    if (text !== undefined) {
      return typeof text === 'string' ? text : model[text]
    }
    if (Array.isArray(content)) {
      return content.map((childConfig) => renderComponent(childConfig, model))
    }
    return null
  };

  return h(Component, parsedProps, {
    default: renderContent,
  })
};

return (_ctx, _cache) => {
  return (_openBlock$1(), _createBlock$1(_resolveDynamicComponent(renderComponent(__props.config, __props.model))))
}
}

};

const Config_vue_vue_type_style_index_0_scoped_818c5c4b_lang = '';

const {createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');


const _withScopeId = n => (_pushScopeId("data-v-818c5c4b"),n=n(),_popScopeId(),n);
const _hoisted_1 = { class: "cfg-shell" };
const _hoisted_2 = { class: "cfg-head" };
const _hoisted_3 = /*#__PURE__*/ _withScopeId(() => /*#__PURE__*/_createElementVNode("div", null, [
  /*#__PURE__*/_createElementVNode("div", { class: "cfg-kicker" }, "FnMediaCoverGenerator"),
  /*#__PURE__*/_createElementVNode("h2", { class: "cfg-title" }, "插件配置")
], -1));
const _hoisted_4 = { class: "d-flex flex-wrap ga-2" };
const _hoisted_5 = {
  key: 1,
  class: "cfg-form"
};

const {reactive,ref} = await importShared('vue');

const PLUGIN_ID = 'FnMediaCoverGenerator';


const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['switch', 'close'],
  setup(__props, { emit }) {

const props = __props;





const loading = ref(true);
const saving = ref(false);
const loadError = ref('');
const formItems = ref([]);
const configForm = reactive({});
const message = reactive({ text: '', type: 'info' });

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value ?? {}))
}

function assignModel(target, payload) {
  Object.keys(target).forEach((key) => {
    delete target[key];
  });
  Object.entries(payload || {}).forEach(([key, value]) => {
    target[key] = value;
  });
}

async function loadSchema() {
  loading.value = true;
  loadError.value = '';
  try {
    const result = await props.api.get(`plugin/form/${PLUGIN_ID}`);
    formItems.value = Array.isArray(result?.conf) ? result.conf : [];
    assignModel(configForm, cloneValue(result?.model || props.initialConfig));
  } catch (error) {
    formItems.value = [];
    assignModel(configForm, cloneValue(props.initialConfig));
    loadError.value = error?.message || '加载配置表单失败';
  } finally {
    loading.value = false;
  }
}

async function saveConfig() {
  saving.value = true;
  message.text = '';
  try {
    const result = await props.api.put(`plugin/${PLUGIN_ID}`, cloneValue(configForm));
    if (result?.success === false) {
      throw new Error(result?.message || '配置保存失败')
    }
    message.type = 'success';
    message.text = result?.message || '配置已保存';
  } catch (error) {
    message.type = 'error';
    message.text = error?.message || '配置保存失败';
  } finally {
    saving.value = false;
  }
}

loadSchema();

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_skeleton_loader = _resolveComponent("v-skeleton-loader");

  return (_openBlock(), _createElementBlock("section", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _hoisted_3,
      _createElementVNode("div", _hoisted_4, [
        _createVNode(_component_v_btn, {
          variant: "text",
          color: "primary",
          onClick: _cache[0] || (_cache[0] = $event => (emit('switch')))
        }, {
          default: _withCtx(() => [
            _createTextVNode("查看页面")
          ]),
          _: 1
        }),
        _createVNode(_component_v_btn, {
          variant: "flat",
          color: "primary",
          loading: saving.value,
          disabled: loading.value || !formItems.value.length,
          onClick: saveConfig
        }, {
          default: _withCtx(() => [
            _createTextVNode("保存配置")
          ]),
          _: 1
        }, 8, ["loading", "disabled"])
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
    (loading.value)
      ? (_openBlock(), _createBlock(_component_v_skeleton_loader, {
          key: 1,
          type: "article, article, article"
        }))
      : (_openBlock(), _createElementBlock(_Fragment, { key: 2 }, [
          (loadError.value)
            ? (_openBlock(), _createBlock(_component_v_alert, {
                key: 0,
                type: "error",
                variant: "tonal",
                class: "mb-4"
              }, {
                default: _withCtx(() => [
                  _createTextVNode(_toDisplayString(loadError.value), 1)
                ]),
                _: 1
              }))
            : _createCommentVNode("", true),
          (formItems.value.length)
            ? (_openBlock(), _createElementBlock("div", _hoisted_5, [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(formItems.value, (item, index) => {
                  return (_openBlock(), _createBlock(_sfc_main$1, {
                    key: index,
                    config: item,
                    model: configForm
                  }, null, 8, ["config", "model"]))
                }), 128))
              ]))
            : (_openBlock(), _createBlock(_component_v_alert, {
                key: 2,
                type: "warning",
                variant: "tonal"
              }, {
                default: _withCtx(() => [
                  _createTextVNode(" 未读取到配置表单，请检查插件是否已正确加载。 ")
                ]),
                _: 1
              }))
        ], 64))
  ]))
}
}

};
const ConfigView = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-818c5c4b"]]);

export { ConfigView as default };
