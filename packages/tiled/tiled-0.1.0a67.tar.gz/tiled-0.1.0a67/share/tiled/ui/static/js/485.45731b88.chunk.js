"use strict";(self.webpackChunktiled=self.webpackChunktiled||[]).push([[485],{46348:function(e,t,n){n.d(t,{yC:function(){return l},Pu:function(){return o},jZ:function(){return d},be:function(){return u}});var r=n(15861),a=n(87757),s=n.n(a),i=n(74569),c={NODE_ENV:"production",PUBLIC_URL:"/ui",WDS_SOCKET_HOST:void 0,WDS_SOCKET_PATH:void 0,WDS_SOCKET_PORT:void 0,FAST_REFRESH:!0}.REACT_APP_API_PREFIX||"../api",u=n.n(i)().create({baseURL:c}),l=function(){var e=(0,r.Z)(s().mark((function e(t,n){var r,a,i,c,l,o,d=arguments;return s().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return r=d.length>2&&void 0!==d[2]?d[2]:[],a=d.length>3&&void 0!==d[3]?d[3]:null,i=d.length>4&&void 0!==d[4]?d[4]:0,c=d.length>5&&void 0!==d[5]?d[5]:100,l="/node/search/".concat(t.join("/"),"?page[offset]=").concat(i,"&page[limit]=").concat(c,"&fields=").concat(r.join("&fields=")),null!==a&&(l=l.concat("&select_metadata=".concat(a))),e.next=8,u.get(l,{signal:n});case 8:return o=e.sent,e.abrupt("return",o.data);case 10:case"end":return e.stop()}}),e)})));return function(t,n){return e.apply(this,arguments)}}(),o=function(){var e=(0,r.Z)(s().mark((function e(t,n){var r,a,i=arguments;return s().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return r=i.length>2&&void 0!==i[2]?i[2]:[],e.next=3,u.get("/node/metadata/".concat(t.join("/"),"?fields=").concat(r.join("&fields=")),{signal:n});case 3:return a=e.sent,e.abrupt("return",a.data);case 5:case"end":return e.stop()}}),e)})));return function(t,n){return e.apply(this,arguments)}}(),d=function(){var e=(0,r.Z)(s().mark((function e(){var t;return s().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,u.get("/");case 2:return t=e.sent,e.abrupt("return",t.data);case 4:case"end":return e.stop()}}),e)})));return function(){return e.apply(this,arguments)}}()},32485:function(e,t,n){n.r(t),n.d(t,{default:function(){return B}});var r=n(15861),a=n(70885),s=n(1413),i=n(45987),c=n(87757),u=n.n(c),l=n(72791),o=n(64554),d=n(58974),m=n(93517),f=n(23060),x=n(43504),p=n(80184),h=function(e){return void 0!==e.segments?(0,p.jsx)(o.Z,{mt:3,mb:2,children:(0,p.jsxs)(m.Z,{"aria-label":"breadcrumb",children:[(0,p.jsx)(f.Z,{component:x.rU,to:"/browse/",children:"Top"},"breadcrumb-0"),e.segments.map((function(e,t,n){return(0,p.jsx)(f.Z,{component:x.rU,to:"/browse".concat(n.slice(0,1+t).map((function(e){return"/"+e})).join(""),"/"),children:e},"breadcrumb-{1 + i}"+e)}))]})}):(0,p.jsx)("div",{children:"..."})},v=n(10703),j=n(47047),b=n(43896),g=n(39124),Z=n(20890),y=n(46348),k=n(16871),w=["children","value","index"],_=(0,l.lazy)((function(){return n.e(741).then(n.bind(n,48741))})),P=(0,l.lazy)((function(){return Promise.all([n.e(494),n.e(446),n.e(197),n.e(214),n.e(393),n.e(356)]).then(n.bind(n,36356))})),S=(0,l.lazy)((function(){return Promise.all([n.e(494),n.e(446),n.e(197),n.e(705),n.e(276)]).then(n.bind(n,61276))})),C=(0,l.lazy)((function(){return Promise.all([n.e(494),n.e(446),n.e(197),n.e(705),n.e(214),n.e(986),n.e(113)]).then(n.bind(n,87113))})),E=(0,l.lazy)((function(){return n.e(128).then(n.bind(n,19128))})),T=(0,l.lazy)((function(){return Promise.all([n.e(773),n.e(69)]).then(n.bind(n,7069))})),z=(0,l.lazy)((function(){return Promise.all([n.e(705),n.e(773),n.e(921)]).then(n.bind(n,48921))})),U=(0,l.lazy)((function(){return Promise.all([n.e(494),n.e(446),n.e(197),n.e(705),n.e(214),n.e(393),n.e(837)]).then(n.bind(n,17837))}));function A(e){var t=e.children,n=e.value,r=e.index,a=(0,i.Z)(e,w);return(0,p.jsx)("div",(0,s.Z)((0,s.Z)({role:"tabpanel",hidden:n!==r,id:"simple-tabpanel-".concat(r),"aria-labelledby":"simple-tab-".concat(r)},a),{},{children:n===r&&(0,p.jsx)(o.Z,{sx:{p:3},children:t})}))}function O(e){return{id:"simple-tab-".concat(e),"aria-controls":"simple-tabpanel-".concat(e)}}var R=function(e){if(void 0!==e.item){var t=e.item.data.attributes,n=t.structure_family;switch(n){case"node":return(0,p.jsx)(E,{name:e.item.data.id,structureFamily:n,specs:t.specs,link:e.item.data.links.full});case"array":return(0,p.jsx)(S,{name:e.item.data.id,structureFamily:n,macrostructure:t.structure.macro,specs:t.specs,link:e.item.data.links.full});case"dataframe":return(0,p.jsx)(C,{name:e.item.data.id,structureFamily:n,macrostructure:t.structure.macro,specs:t.specs,full_link:e.item.data.links.full,partition_link:e.item.data.links.partition});default:return(0,p.jsxs)("div",{children:['Unknown structure family "',n,'"']})}}return(0,p.jsx)(j.Z,{variant:"rectangular"})},D=function(e){if(void 0!==e.item){var t=e.item.data.attributes.structure_family;switch(t){case"node":return(0,p.jsx)(U,{segments:e.segments,item:e.item});case"array":return(0,p.jsx)(_,{segments:e.segments,item:e.item,link:e.item.data.links.full,structure:e.item.data.attributes.structure});case"dataframe":return(0,p.jsx)(P,{segments:e.segments,item:e.item});default:return(0,p.jsxs)("div",{children:['Unknown structure family "',t,'"']})}}return(0,p.jsx)(j.Z,{variant:"rectangular"})};var F=function(e){var t=(0,l.useState)(0),n=(0,a.Z)(t,2),i=n[0],c=n[1],m=(0,l.useState)(),f=(0,a.Z)(m,2),x=f[0],h=f[1];(0,l.useEffect)((function(){c(0)}),[e.segments]),(0,l.useEffect)((function(){h(void 0);var t=new AbortController;function n(){return(n=(0,r.Z)(u().mark((function n(){var r;return u().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,(0,y.Pu)(e.segments,t.signal,["structure_family","structure.macro","structure.micro","specs"]);case 2:void 0!==(r=n.sent)&&h(r);case 4:case"end":return n.stop()}}),n)})))).apply(this,arguments)}return function(){n.apply(this,arguments)}(),function(){t.abort()}}),[e.segments]);var k=(0,l.useState)(),w=(0,a.Z)(k,2),_=w[0],P=w[1];return(0,l.useEffect)((function(){var t=new AbortController;function n(){return(n=(0,r.Z)(u().mark((function n(){var r;return u().wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return n.next=2,(0,y.Pu)(e.segments,t.signal,["structure_family","structure.macro","structure.micro","specs","metadata","sorting","count"]);case 2:void 0!==(r=n.sent)&&P(r);case 4:case"end":return n.stop()}}),n)})))).apply(this,arguments)}return function(){n.apply(this,arguments)}(),function(){t.abort()}}),[e.segments]),(0,p.jsxs)(o.Z,{sx:{width:"100%"},children:[(0,p.jsx)(o.Z,{sx:{borderBottom:1,borderColor:"divider"},children:(0,p.jsxs)(g.Z,{value:i,onChange:function(e,t){c(t)},"aria-label":"basic tabs example",children:[(0,p.jsx)(b.Z,(0,s.Z)({label:"View"},O(0))),(0,p.jsx)(b.Z,(0,s.Z)({label:"Download"},O(1))),(0,p.jsx)(b.Z,(0,s.Z)({label:"Metadata"},O(2))),(0,p.jsx)(b.Z,(0,s.Z)({label:"Detail"},O(3)))]})}),(0,p.jsxs)(A,{value:i,index:0,children:[(0,p.jsx)(Z.Z,{variant:"h4",component:"h1",gutterBottom:!0,children:e.segments.length>0?e.segments[e.segments.length-1]:""}),(0,p.jsx)(v.Z,{elevation:3,sx:{px:3,py:3},children:(0,p.jsx)(d.Z,{children:(0,p.jsx)(l.Suspense,{fallback:(0,p.jsx)(j.Z,{variant:"rectangular"}),children:(0,p.jsx)(D,{segments:e.segments,item:x})})})})]}),(0,p.jsx)(A,{value:i,index:1,children:(0,p.jsx)(d.Z,{children:(0,p.jsx)(l.Suspense,{fallback:(0,p.jsx)(j.Z,{variant:"rectangular"}),children:(0,p.jsx)(R,{segments:e.segments,item:x})})})}),(0,p.jsx)(A,{value:i,index:2,children:(0,p.jsx)(d.Z,{children:(0,p.jsx)(l.Suspense,{fallback:(0,p.jsx)(j.Z,{variant:"rectangular"}),children:(0,p.jsx)(z,{json:_})})})}),(0,p.jsx)(A,{value:i,index:3,children:(0,p.jsx)(d.Z,{children:(0,p.jsx)(l.Suspense,{fallback:(0,p.jsx)(j.Z,{variant:"rectangular"}),children:(0,p.jsx)(T,{json:_})})})})]})},B=function(){var e=((0,k.UO)()["*"]||"").split("/").filter((function(e){return e}));return void 0!==e?(0,p.jsxs)(o.Z,{sx:{width:"100%"},children:[(0,p.jsx)(h,{segments:e}),(0,p.jsx)(F,{segments:e})]}):(0,p.jsx)(j.Z,{variant:"text"})}}}]);
//# sourceMappingURL=485.45731b88.chunk.js.map