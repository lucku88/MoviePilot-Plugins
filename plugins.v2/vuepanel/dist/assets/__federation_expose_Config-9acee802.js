import { importShared } from './__federation_fn_import-b37dd681.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_4ba35bb6_lang = '';

const {createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,normalizeClass:_normalizeClass,createStaticVNode:_createStaticVNode,openBlock:_openBlock,createElementBlock:_createElementBlock,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');
const _hoisted_1 = { class: "vpc-card" };
const _hoisted_2 = /*#__PURE__*/_createStaticVNode("<div class=\"vpc-kicker\" data-v-4ba35bb6>Vue-面板</div><h2 class=\"vpc-title\" data-v-4ba35bb6>插件配置页已停用</h2><p class=\"vpc-description\" data-v-4ba35bb6> 当前插件已经改为全部通过前端状态页里的功能卡片进行配置、执行、查看日志和复制，这个页面不再承担实际配置职责。 </p><div class=\"vpc-panel\" data-v-4ba35bb6><div class=\"vpc-panel-title\" data-v-4ba35bb6>现在的使用方式</div><p class=\"vpc-line\" data-v-4ba35bb6>1. 进入插件状态页。</p><p class=\"vpc-line\" data-v-4ba35bb6>2. 直接在对应功能卡片上点“配置 / 日志 / 复制”。</p><p class=\"vpc-line\" data-v-4ba35bb6>3. 保存后会立即同步当前卡片的启用、定时、通知和站点参数。</p></div>", 4);
const _hoisted_6 = { class: "vpc-note" };

const {computed} = await importShared('vue');



const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: false, default: null },
  initialConfig: { type: Object, default: () => ({}) },
  themeName: { type: String, default: 'light' },
  themeLabel: { type: String, default: '浅色' },
},
  emits: ['close'],
  setup(__props) {

const props = __props;





const themeClass = computed(() => `vpc-theme--${props.themeName || 'light'}`);

return (_ctx, _cache) => {
  return (_openBlock(), _createElementBlock("section", {
    class: _normalizeClass(["vpc-shell", themeClass.value])
  }, [
    _createElementVNode("div", _hoisted_1, [
      _hoisted_2,
      _createElementVNode("div", _hoisted_6, " 当前主题：" + _toDisplayString(__props.themeLabel || '自动适配') + "。无需在此页保存任何内容。 ", 1)
    ])
  ], 2))
}
}

};
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-4ba35bb6"]]);

export { Config as default };
