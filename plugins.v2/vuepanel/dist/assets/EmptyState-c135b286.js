import { importShared } from './__federation_fn_import-b37dd681.js';

const BaseButton_vue_vue_type_style_index_0_scoped_42b075ba_lang = '';

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

const {renderSlot:_renderSlot$2,resolveComponent:_resolveComponent,mergeProps:_mergeProps,withCtx:_withCtx,openBlock:_openBlock$3,createBlock:_createBlock} = await importShared('vue');


const {computed} = await importShared('vue');



const _sfc_main$3 = /*#__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'BaseButton',
  props: {
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  loading: { type: Boolean, default: false },
},
  setup(__props) {

const props = __props;





const resolvedVariant = computed(() => {
  if (props.variant === 'ghost') return 'text'
  return 'flat'
});

return (_ctx, _cache) => {
  const _component_v_btn = _resolveComponent("v-btn");

  return (_openBlock$3(), _createBlock(_component_v_btn, _mergeProps(_ctx.$attrs, {
    class: ['mp-btn', `is-${__props.variant}`, `is-${__props.size}`],
    variant: resolvedVariant.value,
    loading: __props.loading
  }), {
    default: _withCtx(() => [
      _renderSlot$2(_ctx.$slots, "default", {}, undefined, true)
    ]),
    _: 3
  }, 16, ["class", "variant", "loading"]))
}
}

});
const BaseButton = /*#__PURE__*/_export_sfc(_sfc_main$3, [['__scopeId',"data-v-42b075ba"]]);

const BasePanelCard_vue_vue_type_style_index_0_scoped_f459b691_lang = '';

const {renderSlot:_renderSlot$1,toDisplayString:_toDisplayString$1,openBlock:_openBlock$2,createElementBlock:_createElementBlock$2,createCommentVNode:_createCommentVNode$2,createElementVNode:_createElementVNode$1,normalizeClass:_normalizeClass$1,pushScopeId:_pushScopeId$2,popScopeId:_popScopeId$2} = await importShared('vue');
const _hoisted_1$2 = {
  key: 0,
  class: "mp-card-head"
};
const _hoisted_2$1 = { class: "mp-card-copy" };
const _hoisted_3$1 = {
  key: 0,
  class: "mp-card-kicker"
};
const _hoisted_4 = {
  key: 1,
  class: "mp-card-title"
};
const _hoisted_5 = {
  key: 2,
  class: "mp-card-subtitle"
};
const _hoisted_6 = {
  key: 0,
  class: "mp-card-actions"
};
const _hoisted_7 = { class: "mp-card-body" };
const _hoisted_8 = {
  key: 1,
  class: "mp-card-footer"
};


const _sfc_main$2 = {
  __name: 'BasePanelCard',
  props: {
  title: { type: String, default: '' },
  kicker: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  tone: { type: String, default: 'default' },
  compact: { type: Boolean, default: false },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$2(), _createElementBlock$2("section", {
    class: _normalizeClass$1(['mp-card', `is-${__props.tone}`, { compact: __props.compact }])
  }, [
    (_ctx.$slots.header || __props.title || __props.kicker || _ctx.$slots.actions)
      ? (_openBlock$2(), _createElementBlock$2("div", _hoisted_1$2, [
          _createElementVNode$1("div", _hoisted_2$1, [
            _renderSlot$1(_ctx.$slots, "header", {}, () => [
              (__props.kicker)
                ? (_openBlock$2(), _createElementBlock$2("div", _hoisted_3$1, _toDisplayString$1(__props.kicker), 1))
                : _createCommentVNode$2("", true),
              (__props.title)
                ? (_openBlock$2(), _createElementBlock$2("h3", _hoisted_4, _toDisplayString$1(__props.title), 1))
                : _createCommentVNode$2("", true),
              (__props.subtitle)
                ? (_openBlock$2(), _createElementBlock$2("p", _hoisted_5, _toDisplayString$1(__props.subtitle), 1))
                : _createCommentVNode$2("", true)
            ], true)
          ]),
          (_ctx.$slots.actions)
            ? (_openBlock$2(), _createElementBlock$2("div", _hoisted_6, [
                _renderSlot$1(_ctx.$slots, "actions", {}, undefined, true)
              ]))
            : _createCommentVNode$2("", true)
        ]))
      : _createCommentVNode$2("", true),
    _createElementVNode$1("div", _hoisted_7, [
      _renderSlot$1(_ctx.$slots, "default", {}, undefined, true)
    ]),
    (_ctx.$slots.footer)
      ? (_openBlock$2(), _createElementBlock$2("div", _hoisted_8, [
          _renderSlot$1(_ctx.$slots, "footer", {}, undefined, true)
        ]))
      : _createCommentVNode$2("", true)
  ], 2))
}
}

};
const BasePanelCard = /*#__PURE__*/_export_sfc(_sfc_main$2, [['__scopeId',"data-v-f459b691"]]);

const BaseTag_vue_vue_type_style_index_0_scoped_74d5f500_lang = '';

const {openBlock:_openBlock$1,createElementBlock:_createElementBlock$1,createCommentVNode:_createCommentVNode$1,renderSlot:_renderSlot,normalizeClass:_normalizeClass,pushScopeId:_pushScopeId$1,popScopeId:_popScopeId$1} = await importShared('vue');
const _hoisted_1$1 = {
  key: 0,
  class: "mp-tag-dot"
};


const _sfc_main$1 = {
  __name: 'BaseTag',
  props: {
  tone: { type: String, default: 'info' },
  size: { type: String, default: 'md' },
  dot: { type: Boolean, default: false },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$1(), _createElementBlock$1("span", {
    class: _normalizeClass(['mp-tag', `is-${__props.tone}`, `is-${__props.size}`, { 'has-dot': __props.dot }])
  }, [
    (__props.dot)
      ? (_openBlock$1(), _createElementBlock$1("span", _hoisted_1$1))
      : _createCommentVNode$1("", true),
    _renderSlot(_ctx.$slots, "default", {}, undefined, true)
  ], 2))
}
}

};
const BaseTag = /*#__PURE__*/_export_sfc(_sfc_main$1, [['__scopeId',"data-v-74d5f500"]]);

const EmptyState_vue_vue_type_style_index_0_scoped_3d63d7ef_lang = '';

const {toDisplayString:_toDisplayString,createElementVNode:_createElementVNode,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,pushScopeId:_pushScopeId,popScopeId:_popScopeId} = await importShared('vue');
const _hoisted_1 = { class: "mp-empty" };
const _hoisted_2 = { class: "mp-empty-title" };
const _hoisted_3 = {
  key: 0,
  class: "mp-empty-text"
};


const _sfc_main = {
  __name: 'EmptyState',
  props: {
  title: { type: String, default: '暂无内容' },
  description: { type: String, default: '' },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("strong", _hoisted_2, _toDisplayString(__props.title), 1),
    (__props.description)
      ? (_openBlock(), _createElementBlock("div", _hoisted_3, _toDisplayString(__props.description), 1))
      : _createCommentVNode("", true)
  ]))
}
}

};
const EmptyState = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-3d63d7ef"]]);

export { BasePanelCard as B, EmptyState as E, _export_sfc as _, BaseButton as a, BaseTag as b };
