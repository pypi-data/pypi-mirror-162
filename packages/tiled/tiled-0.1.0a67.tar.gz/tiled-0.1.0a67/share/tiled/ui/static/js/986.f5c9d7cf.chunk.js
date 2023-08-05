/*! For license information please see 986.f5c9d7cf.chunk.js.LICENSE.txt */
(self.webpackChunktiled=self.webpackChunktiled||[]).push([[986],{48926:function(e){function t(e,t,o,r,n,i,a){try{var s=e[i](a),d=s.value}catch(c){return void o(c)}s.done?t(d):Promise.resolve(d).then(r,n)}e.exports=function(e){return function(){var o=this,r=arguments;return new Promise((function(n,i){var a=e.apply(o,r);function s(e){t(a,n,i,s,d,"next",e)}function d(e){t(a,n,i,s,d,"throw",e)}s(void 0)}))}},e.exports.__esModule=!0,e.exports.default=e.exports},95318:function(e){e.exports=function(e){return e&&e.__esModule?e:{default:e}},e.exports.__esModule=!0,e.exports.default=e.exports},50194:function(e,t,o){"use strict";var r=o(95318);t.Z=void 0;var n=r(o(45649)),i=o(80184),a=(0,n.default)((0,i.jsx)("path",{d:"M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"}),"ContentCopy");t.Z=a},45649:function(e,t,o){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),Object.defineProperty(t,"default",{enumerable:!0,get:function(){return r.createSvgIcon}});var r=o(28610)},2199:function(e,t,o){"use strict";o.d(t,{Z:function(){return y}});var r=o(4942),n=o(63366),i=o(87462),a=o(72791),s=o(28182),d=o(90767),c=o(12065),l=o(14036),u=o(47630),p=o(93736),v=o(95159);function m(e){return(0,v.Z)("MuiButtonGroup",e)}var f=(0,o(30208).Z)("MuiButtonGroup",["root","contained","outlined","text","disableElevation","disabled","fullWidth","vertical","grouped","groupedHorizontal","groupedVertical","groupedText","groupedTextHorizontal","groupedTextVertical","groupedTextPrimary","groupedTextSecondary","groupedOutlined","groupedOutlinedHorizontal","groupedOutlinedVertical","groupedOutlinedPrimary","groupedOutlinedSecondary","groupedContained","groupedContainedHorizontal","groupedContainedVertical","groupedContainedPrimary","groupedContainedSecondary"]),b=o(91793),g=o(80184),Z=["children","className","color","component","disabled","disableElevation","disableFocusRipple","disableRipple","fullWidth","orientation","size","variant"],h=(0,u.ZP)("div",{name:"MuiButtonGroup",slot:"Root",overridesResolver:function(e,t){var o=e.ownerState;return[(0,r.Z)({},"& .".concat(f.grouped),t.grouped),(0,r.Z)({},"& .".concat(f.grouped),t["grouped".concat((0,l.Z)(o.orientation))]),(0,r.Z)({},"& .".concat(f.grouped),t["grouped".concat((0,l.Z)(o.variant))]),(0,r.Z)({},"& .".concat(f.grouped),t["grouped".concat((0,l.Z)(o.variant)).concat((0,l.Z)(o.orientation))]),(0,r.Z)({},"& .".concat(f.grouped),t["grouped".concat((0,l.Z)(o.variant)).concat((0,l.Z)(o.color))]),t.root,t[o.variant],!0===o.disableElevation&&t.disableElevation,o.fullWidth&&t.fullWidth,"vertical"===o.orientation&&t.vertical]}})((function(e){var t=e.theme,o=e.ownerState;return(0,i.Z)({display:"inline-flex",borderRadius:t.shape.borderRadius},"contained"===o.variant&&{boxShadow:t.shadows[2]},o.disableElevation&&{boxShadow:"none"},o.fullWidth&&{width:"100%"},"vertical"===o.orientation&&{flexDirection:"column"},(0,r.Z)({},"& .".concat(f.grouped),(0,i.Z)({minWidth:40,"&:not(:first-of-type)":(0,i.Z)({},"horizontal"===o.orientation&&{borderTopLeftRadius:0,borderBottomLeftRadius:0},"vertical"===o.orientation&&{borderTopRightRadius:0,borderTopLeftRadius:0},"outlined"===o.variant&&"horizontal"===o.orientation&&{marginLeft:-1},"outlined"===o.variant&&"vertical"===o.orientation&&{marginTop:-1}),"&:not(:last-of-type)":(0,i.Z)({},"horizontal"===o.orientation&&{borderTopRightRadius:0,borderBottomRightRadius:0},"vertical"===o.orientation&&{borderBottomRightRadius:0,borderBottomLeftRadius:0},"text"===o.variant&&"horizontal"===o.orientation&&{borderRight:"1px solid ".concat("light"===t.palette.mode?"rgba(0, 0, 0, 0.23)":"rgba(255, 255, 255, 0.23)")},"text"===o.variant&&"vertical"===o.orientation&&{borderBottom:"1px solid ".concat("light"===t.palette.mode?"rgba(0, 0, 0, 0.23)":"rgba(255, 255, 255, 0.23)")},"text"===o.variant&&"inherit"!==o.color&&{borderColor:(0,c.Fq)(t.palette[o.color].main,.5)},"outlined"===o.variant&&"horizontal"===o.orientation&&{borderRightColor:"transparent"},"outlined"===o.variant&&"vertical"===o.orientation&&{borderBottomColor:"transparent"},"contained"===o.variant&&"horizontal"===o.orientation&&(0,r.Z)({borderRight:"1px solid ".concat(t.palette.grey[400])},"&.".concat(f.disabled),{borderRight:"1px solid ".concat(t.palette.action.disabled)}),"contained"===o.variant&&"vertical"===o.orientation&&(0,r.Z)({borderBottom:"1px solid ".concat(t.palette.grey[400])},"&.".concat(f.disabled),{borderBottom:"1px solid ".concat(t.palette.action.disabled)}),"contained"===o.variant&&"inherit"!==o.color&&{borderColor:t.palette[o.color].dark},{"&:hover":(0,i.Z)({},"outlined"===o.variant&&"horizontal"===o.orientation&&{borderRightColor:"currentColor"},"outlined"===o.variant&&"vertical"===o.orientation&&{borderBottomColor:"currentColor"})}),"&:hover":(0,i.Z)({},"contained"===o.variant&&{boxShadow:"none"})},"contained"===o.variant&&{boxShadow:"none"})))})),y=a.forwardRef((function(e,t){var o=(0,p.Z)({props:e,name:"MuiButtonGroup"}),r=o.children,c=o.className,u=o.color,v=void 0===u?"primary":u,f=o.component,y=void 0===f?"div":f,x=o.disabled,w=void 0!==x&&x,C=o.disableElevation,R=void 0!==C&&C,S=o.disableFocusRipple,I=void 0!==S&&S,k=o.disableRipple,P=void 0!==k&&k,F=o.fullWidth,M=void 0!==F&&F,N=o.orientation,G=void 0===N?"horizontal":N,T=o.size,B=void 0===T?"medium":T,L=o.variant,A=void 0===L?"outlined":L,O=(0,n.Z)(o,Z),V=(0,i.Z)({},o,{color:v,component:y,disabled:w,disableElevation:R,disableFocusRipple:I,disableRipple:P,fullWidth:M,orientation:G,size:B,variant:A}),j=function(e){var t=e.classes,o=e.color,r=e.disabled,n=e.disableElevation,i=e.fullWidth,a=e.orientation,s=e.variant,c={root:["root",s,"vertical"===a&&"vertical",i&&"fullWidth",n&&"disableElevation"],grouped:["grouped","grouped".concat((0,l.Z)(a)),"grouped".concat((0,l.Z)(s)),"grouped".concat((0,l.Z)(s)).concat((0,l.Z)(a)),"grouped".concat((0,l.Z)(s)).concat((0,l.Z)(o)),r&&"disabled"]};return(0,d.Z)(c,m,t)}(V),z=a.useMemo((function(){return{className:j.grouped,color:v,disabled:w,disableElevation:R,disableFocusRipple:I,disableRipple:P,fullWidth:M,size:B,variant:A}}),[v,w,R,I,P,M,B,A,j.grouped]);return(0,g.jsx)(h,(0,i.Z)({as:y,role:"group",className:(0,s.Z)(j.root,c),ref:t,ownerState:V},O,{children:(0,g.jsx)(b.Z.Provider,{value:z,children:r})}))}))},79012:function(e,t,o){"use strict";o.d(t,{Z:function(){return g}});var r=o(63366),n=o(87462),i=o(72791),a=o(28182),s=o(90767),d=o(47630),c=o(93736),l=o(95159);function u(e){return(0,l.Z)("MuiFormGroup",e)}(0,o(30208).Z)("MuiFormGroup",["root","row","error"]);var p=o(52930),v=o(76147),m=o(80184),f=["className","row"],b=(0,d.ZP)("div",{name:"MuiFormGroup",slot:"Root",overridesResolver:function(e,t){var o=e.ownerState;return[t.root,o.row&&t.row]}})((function(e){var t=e.ownerState;return(0,n.Z)({display:"flex",flexDirection:"column",flexWrap:"wrap"},t.row&&{flexDirection:"row"})})),g=i.forwardRef((function(e,t){var o=(0,c.Z)({props:e,name:"MuiFormGroup"}),i=o.className,d=o.row,l=void 0!==d&&d,g=(0,r.Z)(o,f),Z=(0,p.Z)(),h=(0,v.Z)({props:o,muiFormControl:Z,states:["error"]}),y=(0,n.Z)({},o,{row:l,error:h.error}),x=function(e){var t=e.classes,o={root:["root",e.row&&"row",e.error&&"error"]};return(0,s.Z)(o,u,t)}(y);return(0,m.jsx)(b,(0,n.Z)({className:(0,a.Z)(x.root,i),ownerState:y,ref:t},g))}))},15021:function(e,t,o){"use strict";o.d(t,{ZP:function(){return T}});var r=o(4942),n=o(63366),i=o(87462),a=o(72791),s=o(28182),d=o(90767),c=o(20627),l=o(12065),u=o(47630),p=o(93736),v=o(23701),m=o(19103),f=o(40162),b=o(42071),g=o(66199),Z=o(95159),h=o(30208);function y(e){return(0,Z.Z)("MuiListItem",e)}var x=(0,h.Z)("MuiListItem",["root","container","focusVisible","dense","alignItemsFlexStart","disabled","divider","gutters","padding","button","secondaryAction","selected"]),w=o(34065);function C(e){return(0,Z.Z)("MuiListItemSecondaryAction",e)}(0,h.Z)("MuiListItemSecondaryAction",["root","disableGutters"]);var R=o(80184),S=["className"],I=(0,u.ZP)("div",{name:"MuiListItemSecondaryAction",slot:"Root",overridesResolver:function(e,t){var o=e.ownerState;return[t.root,o.disableGutters&&t.disableGutters]}})((function(e){var t=e.ownerState;return(0,i.Z)({position:"absolute",right:16,top:"50%",transform:"translateY(-50%)"},t.disableGutters&&{right:0})})),k=a.forwardRef((function(e,t){var o=(0,p.Z)({props:e,name:"MuiListItemSecondaryAction"}),r=o.className,c=(0,n.Z)(o,S),l=a.useContext(g.Z),u=(0,i.Z)({},o,{disableGutters:l.disableGutters}),v=function(e){var t=e.disableGutters,o=e.classes,r={root:["root",t&&"disableGutters"]};return(0,d.Z)(r,C,o)}(u);return(0,R.jsx)(I,(0,i.Z)({className:(0,s.Z)(v.root,r),ownerState:u,ref:t},c))}));k.muiName="ListItemSecondaryAction";var P=k,F=["className"],M=["alignItems","autoFocus","button","children","className","component","components","componentsProps","ContainerComponent","ContainerProps","dense","disabled","disableGutters","disablePadding","divider","focusVisibleClassName","secondaryAction","selected"],N=(0,u.ZP)("div",{name:"MuiListItem",slot:"Root",overridesResolver:function(e,t){var o=e.ownerState;return[t.root,o.dense&&t.dense,"flex-start"===o.alignItems&&t.alignItemsFlexStart,o.divider&&t.divider,!o.disableGutters&&t.gutters,!o.disablePadding&&t.padding,o.button&&t.button,o.hasSecondaryAction&&t.secondaryAction]}})((function(e){var t,o=e.theme,n=e.ownerState;return(0,i.Z)({display:"flex",justifyContent:"flex-start",alignItems:"center",position:"relative",textDecoration:"none",width:"100%",boxSizing:"border-box",textAlign:"left"},!n.disablePadding&&(0,i.Z)({paddingTop:8,paddingBottom:8},n.dense&&{paddingTop:4,paddingBottom:4},!n.disableGutters&&{paddingLeft:16,paddingRight:16},!!n.secondaryAction&&{paddingRight:48}),!!n.secondaryAction&&(0,r.Z)({},"& > .".concat(w.Z.root),{paddingRight:48}),(t={},(0,r.Z)(t,"&.".concat(x.focusVisible),{backgroundColor:o.palette.action.focus}),(0,r.Z)(t,"&.".concat(x.selected),(0,r.Z)({backgroundColor:(0,l.Fq)(o.palette.primary.main,o.palette.action.selectedOpacity)},"&.".concat(x.focusVisible),{backgroundColor:(0,l.Fq)(o.palette.primary.main,o.palette.action.selectedOpacity+o.palette.action.focusOpacity)})),(0,r.Z)(t,"&.".concat(x.disabled),{opacity:o.palette.action.disabledOpacity}),t),"flex-start"===n.alignItems&&{alignItems:"flex-start"},n.divider&&{borderBottom:"1px solid ".concat(o.palette.divider),backgroundClip:"padding-box"},n.button&&(0,r.Z)({transition:o.transitions.create("background-color",{duration:o.transitions.duration.shortest}),"&:hover":{textDecoration:"none",backgroundColor:o.palette.action.hover,"@media (hover: none)":{backgroundColor:"transparent"}}},"&.".concat(x.selected,":hover"),{backgroundColor:(0,l.Fq)(o.palette.primary.main,o.palette.action.selectedOpacity+o.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:(0,l.Fq)(o.palette.primary.main,o.palette.action.selectedOpacity)}}),n.hasSecondaryAction&&{paddingRight:48})})),G=(0,u.ZP)("li",{name:"MuiListItem",slot:"Container",overridesResolver:function(e,t){return t.container}})({position:"relative"}),T=a.forwardRef((function(e,t){var o=(0,p.Z)({props:e,name:"MuiListItem"}),r=o.alignItems,l=void 0===r?"center":r,u=o.autoFocus,Z=void 0!==u&&u,h=o.button,w=void 0!==h&&h,C=o.children,S=o.className,I=o.component,k=o.components,T=void 0===k?{}:k,B=o.componentsProps,L=void 0===B?{}:B,A=o.ContainerComponent,O=void 0===A?"li":A,V=o.ContainerProps,j=(V=void 0===V?{}:V).className,z=o.dense,E=void 0!==z&&z,W=o.disabled,q=void 0!==W&&W,_=o.disableGutters,D=void 0!==_&&_,H=o.disablePadding,$=void 0!==H&&H,U=o.divider,Y=void 0!==U&&U,J=o.focusVisibleClassName,K=o.secondaryAction,Q=o.selected,X=void 0!==Q&&Q,ee=(0,n.Z)(o.ContainerProps,F),te=(0,n.Z)(o,M),oe=a.useContext(g.Z),re={dense:E||oe.dense||!1,alignItems:l,disableGutters:D},ne=a.useRef(null);(0,f.Z)((function(){Z&&ne.current&&ne.current.focus()}),[Z]);var ie=a.Children.toArray(C),ae=ie.length&&(0,m.Z)(ie[ie.length-1],["ListItemSecondaryAction"]),se=(0,i.Z)({},o,{alignItems:l,autoFocus:Z,button:w,dense:re.dense,disabled:q,disableGutters:D,disablePadding:$,divider:Y,hasSecondaryAction:ae,selected:X}),de=function(e){var t=e.alignItems,o=e.button,r=e.classes,n=e.dense,i=e.disabled,a={root:["root",n&&"dense",!e.disableGutters&&"gutters",!e.disablePadding&&"padding",e.divider&&"divider",i&&"disabled",o&&"button","flex-start"===t&&"alignItemsFlexStart",e.hasSecondaryAction&&"secondaryAction",e.selected&&"selected"],container:["container"]};return(0,d.Z)(a,y,r)}(se),ce=(0,b.Z)(ne,t),le=T.Root||N,ue=L.root||{},pe=(0,i.Z)({className:(0,s.Z)(de.root,ue.className,S),disabled:q},te),ve=I||"li";return w&&(pe.component=I||"div",pe.focusVisibleClassName=(0,s.Z)(x.focusVisible,J),ve=v.Z),ae?(ve=pe.component||I?ve:"div","li"===O&&("li"===ve?ve="div":"li"===pe.component&&(pe.component="div")),(0,R.jsx)(g.Z.Provider,{value:re,children:(0,R.jsxs)(G,(0,i.Z)({as:O,className:(0,s.Z)(de.container,j),ref:ce,ownerState:se},ee,{children:[(0,R.jsx)(le,(0,i.Z)({},ue,!(0,c.Z)(le)&&{as:ve,ownerState:(0,i.Z)({},se,ue.ownerState)},pe,{children:ie})),ie.pop()]}))})):(0,R.jsx)(g.Z.Provider,{value:re,children:(0,R.jsxs)(le,(0,i.Z)({},ue,{as:ve,ref:ce,ownerState:se},!(0,c.Z)(le)&&{ownerState:(0,i.Z)({},se,ue.ownerState)},pe,{children:[ie,K&&(0,R.jsx)(P,{children:K})]}))})}))},76278:function(e,t,o){"use strict";var r=o(4942),n=o(63366),i=o(87462),a=o(72791),s=o(28182),d=o(90767),c=o(12065),l=o(47630),u=o(93736),p=o(23701),v=o(40162),m=o(42071),f=o(66199),b=o(34065),g=o(80184),Z=["alignItems","autoFocus","component","children","dense","disableGutters","divider","focusVisibleClassName","selected"],h=(0,l.ZP)(p.Z,{shouldForwardProp:function(e){return(0,l.FO)(e)||"classes"===e},name:"MuiListItemButton",slot:"Root",overridesResolver:function(e,t){var o=e.ownerState;return[t.root,o.dense&&t.dense,"flex-start"===o.alignItems&&t.alignItemsFlexStart,o.divider&&t.divider,!o.disableGutters&&t.gutters]}})((function(e){var t,o=e.theme,n=e.ownerState;return(0,i.Z)((t={display:"flex",flexGrow:1,justifyContent:"flex-start",alignItems:"center",position:"relative",textDecoration:"none",boxSizing:"border-box",textAlign:"left",paddingTop:8,paddingBottom:8,transition:o.transitions.create("background-color",{duration:o.transitions.duration.shortest}),"&:hover":{textDecoration:"none",backgroundColor:o.palette.action.hover,"@media (hover: none)":{backgroundColor:"transparent"}}},(0,r.Z)(t,"&.".concat(b.Z.selected),(0,r.Z)({backgroundColor:(0,c.Fq)(o.palette.primary.main,o.palette.action.selectedOpacity)},"&.".concat(b.Z.focusVisible),{backgroundColor:(0,c.Fq)(o.palette.primary.main,o.palette.action.selectedOpacity+o.palette.action.focusOpacity)})),(0,r.Z)(t,"&.".concat(b.Z.selected,":hover"),{backgroundColor:(0,c.Fq)(o.palette.primary.main,o.palette.action.selectedOpacity+o.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:(0,c.Fq)(o.palette.primary.main,o.palette.action.selectedOpacity)}}),(0,r.Z)(t,"&.".concat(b.Z.focusVisible),{backgroundColor:o.palette.action.focus}),(0,r.Z)(t,"&.".concat(b.Z.disabled),{opacity:o.palette.action.disabledOpacity}),t),n.divider&&{borderBottom:"1px solid ".concat(o.palette.divider),backgroundClip:"padding-box"},"flex-start"===n.alignItems&&{alignItems:"flex-start"},!n.disableGutters&&{paddingLeft:16,paddingRight:16},n.dense&&{paddingTop:4,paddingBottom:4})})),y=a.forwardRef((function(e,t){var o=(0,u.Z)({props:e,name:"MuiListItemButton"}),r=o.alignItems,c=void 0===r?"center":r,l=o.autoFocus,p=void 0!==l&&l,y=o.component,x=void 0===y?"div":y,w=o.children,C=o.dense,R=void 0!==C&&C,S=o.disableGutters,I=void 0!==S&&S,k=o.divider,P=void 0!==k&&k,F=o.focusVisibleClassName,M=o.selected,N=void 0!==M&&M,G=(0,n.Z)(o,Z),T=a.useContext(f.Z),B={dense:R||T.dense||!1,alignItems:c,disableGutters:I},L=a.useRef(null);(0,v.Z)((function(){p&&L.current&&L.current.focus()}),[p]);var A=(0,i.Z)({},o,{alignItems:c,dense:B.dense,disableGutters:I,divider:P,selected:N}),O=function(e){var t=e.alignItems,o=e.classes,r=e.dense,n=e.disabled,a={root:["root",r&&"dense",!e.disableGutters&&"gutters",e.divider&&"divider",n&&"disabled","flex-start"===t&&"alignItemsFlexStart",e.selected&&"selected"]},s=(0,d.Z)(a,b.t,o);return(0,i.Z)({},o,s)}(A),V=(0,m.Z)(L,t);return(0,g.jsx)(f.Z.Provider,{value:B,children:(0,g.jsx)(h,(0,i.Z)({ref:V,component:x,focusVisibleClassName:(0,s.Z)(O.focusVisible,F),ownerState:A},G,{classes:O,children:w}))})}));t.Z=y},34065:function(e,t,o){"use strict";o.d(t,{t:function(){return n}});var r=o(95159);function n(e){return(0,r.Z)("MuiListItemButton",e)}var i=(0,o(30208).Z)("MuiListItemButton",["root","focusVisible","dense","alignItemsFlexStart","disabled","divider","gutters","selected"]);t.Z=i},49900:function(e,t,o){"use strict";var r=o(4942),n=o(63366),i=o(87462),a=o(72791),s=o(28182),d=o(90767),c=o(20890),l=o(66199),u=o(93736),p=o(47630),v=o(29849),m=o(80184),f=["children","className","disableTypography","inset","primary","primaryTypographyProps","secondary","secondaryTypographyProps"],b=(0,p.ZP)("div",{name:"MuiListItemText",slot:"Root",overridesResolver:function(e,t){var o=e.ownerState;return[(0,r.Z)({},"& .".concat(v.Z.primary),t.primary),(0,r.Z)({},"& .".concat(v.Z.secondary),t.secondary),t.root,o.inset&&t.inset,o.primary&&o.secondary&&t.multiline,o.dense&&t.dense]}})((function(e){var t=e.ownerState;return(0,i.Z)({flex:"1 1 auto",minWidth:0,marginTop:4,marginBottom:4},t.primary&&t.secondary&&{marginTop:6,marginBottom:6},t.inset&&{paddingLeft:56})})),g=a.forwardRef((function(e,t){var o=(0,u.Z)({props:e,name:"MuiListItemText"}),r=o.children,p=o.className,g=o.disableTypography,Z=void 0!==g&&g,h=o.inset,y=void 0!==h&&h,x=o.primary,w=o.primaryTypographyProps,C=o.secondary,R=o.secondaryTypographyProps,S=(0,n.Z)(o,f),I=a.useContext(l.Z).dense,k=null!=x?x:r,P=C,F=(0,i.Z)({},o,{disableTypography:Z,inset:y,primary:!!k,secondary:!!P,dense:I}),M=function(e){var t=e.classes,o=e.inset,r=e.primary,n=e.secondary,i={root:["root",o&&"inset",e.dense&&"dense",r&&n&&"multiline"],primary:["primary"],secondary:["secondary"]};return(0,d.Z)(i,v.L,t)}(F);return null==k||k.type===c.Z||Z||(k=(0,m.jsx)(c.Z,(0,i.Z)({variant:I?"body2":"body1",className:M.primary,component:"span",display:"block"},w,{children:k}))),null==P||P.type===c.Z||Z||(P=(0,m.jsx)(c.Z,(0,i.Z)({variant:"body2",className:M.secondary,color:"text.secondary",display:"block"},R,{children:P}))),(0,m.jsxs)(b,(0,i.Z)({className:(0,s.Z)(M.root,p),ownerState:F,ref:t},S,{children:[k,P]}))}));t.Z=g},53767:function(e,t,o){"use strict";var r=o(4942),n=o(63366),i=o(87462),a=o(72791),s=o(51184),d=o(45682),c=o(78519),l=o(82466),u=o(47630),p=o(93736),v=o(80184),m=["component","direction","spacing","divider","children"];function f(e,t){var o=a.Children.toArray(e).filter(Boolean);return o.reduce((function(e,r,n){return e.push(r),n<o.length-1&&e.push(a.cloneElement(t,{key:"separator-".concat(n)})),e}),[])}var b=(0,u.ZP)("div",{name:"MuiStack",slot:"Root",overridesResolver:function(e,t){return[t.root]}})((function(e){var t=e.ownerState,o=e.theme,n=(0,i.Z)({display:"flex"},(0,s.k9)({theme:o},(0,s.P$)({values:t.direction,breakpoints:o.breakpoints.values}),(function(e){return{flexDirection:e}})));if(t.spacing){var a=(0,d.hB)(o),c=Object.keys(o.breakpoints.values).reduce((function(e,o){return null==t.spacing[o]&&null==t.direction[o]||(e[o]=!0),e}),{}),u=(0,s.P$)({values:t.direction,base:c}),p=(0,s.P$)({values:t.spacing,base:c});n=(0,l.Z)(n,(0,s.k9)({theme:o},p,(function(e,o){return{"& > :not(style) + :not(style)":(0,r.Z)({margin:0},"margin".concat((n=o?u[o]:t.direction,{row:"Left","row-reverse":"Right",column:"Top","column-reverse":"Bottom"}[n])),(0,d.NA)(a,e))};var n})))}return n})),g=a.forwardRef((function(e,t){var o=(0,p.Z)({props:e,name:"MuiStack"}),r=(0,c.Z)(o),a=r.component,s=void 0===a?"div":a,d=r.direction,l=void 0===d?"column":d,u=r.spacing,g=void 0===u?0:u,Z=r.divider,h=r.children,y=(0,n.Z)(r,m),x={direction:l,spacing:g};return(0,v.jsx)(b,(0,i.Z)({as:s,ownerState:x,ref:t},y,{children:Z?f(h,Z):h}))}));t.Z=g},31260:function(e,t,o){"use strict";var r=o(78949);t.Z=r.Z},28610:function(e,t,o){"use strict";o.r(t),o.d(t,{capitalize:function(){return r.Z},createChainedFunction:function(){return n.Z},createSvgIcon:function(){return i.Z},debounce:function(){return a.Z},deprecatedPropType:function(){return s},isMuiElement:function(){return d.Z},ownerDocument:function(){return c.Z},ownerWindow:function(){return l.Z},requirePropFactory:function(){return u},setRef:function(){return p},unstable_ClassNameGenerator:function(){return y.Z},unstable_useEnhancedEffect:function(){return v.Z},unstable_useId:function(){return m.Z},unsupportedProp:function(){return f},useControlled:function(){return b.Z},useEventCallback:function(){return g.Z},useForkRef:function(){return Z.Z},useIsFocusVisible:function(){return h.Z}});var r=o(14036),n=o(31260),i=o(76189),a=o(83199);var s=function(e,t){return function(){return null}},d=o(19103),c=o(98301),l=o(17602);o(87462);var u=function(e,t){return function(){return null}},p=o(62971).Z,v=o(40162),m=o(67384);var f=function(e,t,o,r,n){return null},b=o(98278),g=o(89683),Z=o(42071),h=o(68221),y=o(87125)},1829:function(e,t,o){var r=o(87757),n=o(48926).default;function i(){return new DOMException("The request is not allowed","NotAllowedError")}function a(e){return s.apply(this,arguments)}function s(){return(s=n(r.mark((function e(t){return r.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:if(navigator.clipboard){e.next=2;break}throw i();case 2:return e.abrupt("return",navigator.clipboard.writeText(t));case 3:case"end":return e.stop()}}),e)})))).apply(this,arguments)}function d(e){return c.apply(this,arguments)}function c(){return(c=n(r.mark((function e(t){var o,n,a,s;return r.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:(o=document.createElement("span")).textContent=t,o.style.whiteSpace="pre",o.style.webkitUserSelect="auto",o.style.userSelect="all",document.body.appendChild(o),n=window.getSelection(),a=window.document.createRange(),n.removeAllRanges(),a.selectNode(o),n.addRange(a),s=!1;try{s=window.document.execCommand("copy")}finally{n.removeAllRanges(),window.document.body.removeChild(o)}if(s){e.next=15;break}throw i();case 15:case"end":return e.stop()}}),e)})))).apply(this,arguments)}function l(){return(l=n(r.mark((function e(t){return r.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,a(t);case 3:case 10:e.next=15;break;case 5:return e.prev=5,e.t0=e.catch(0),e.prev=7,e.next=10,d(t);case 12:throw e.prev=12,e.t1=e.catch(7),e.t1||e.t0||i();case 15:case"end":return e.stop()}}),e,null,[[0,5],[7,12]])})))).apply(this,arguments)}e.exports=function(e){return l.apply(this,arguments)}}}]);
//# sourceMappingURL=986.f5c9d7cf.chunk.js.map