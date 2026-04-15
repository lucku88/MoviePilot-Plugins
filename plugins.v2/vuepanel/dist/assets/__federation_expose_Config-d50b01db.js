import { importShared } from './__federation_fn_import-b37dd681.js';
import PageView from './__federation_expose_Page-527f9281.js';

const {openBlock:_openBlock,createBlock:_createBlock} = await importShared('vue');


const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
},
  emits: ['close'],
  setup(__props, { emit }) {





return (_ctx, _cache) => {
  return (_openBlock(), _createBlock(PageView, {
    api: __props.api,
    "initial-config": __props.initialConfig,
    "theme-name": __props.themeName,
    "theme-label": __props.themeLabel,
    onClose: _cache[0] || (_cache[0] = $event => (emit('close')))
  }, null, 8, ["api", "initial-config", "theme-name", "theme-label"]))
}
}

};

export { _sfc_main as default };
