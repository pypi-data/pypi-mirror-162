"use strict";(self.webpackChunkreact_frontend=self.webpackChunkreact_frontend||[]).push([[8831],{98831:(e,t,i)=>{i.r(t);var r=i(15304),n=i(57835),o=i(19596);const s=new WeakMap;let a=0;const l=new Map,d=new WeakSet,c=()=>new Promise((e=>requestAnimationFrame(e))),h=(e,t)=>{const i=e-t;return 0===i?void 0:i},p=(e,t)=>{const i=e/t;return 1===i?void 0:i},u={left:(e,t)=>{const i=h(e,t);return{value:i,transform:i&&`translateX(${i}px)`}},top:(e,t)=>{const i=h(e,t);return{value:i,transform:i&&`translateY(${i}px)`}},width:(e,t)=>{const i=p(e,t);return{value:i,transform:i&&`scaleX(${i})`}},height:(e,t)=>{const i=p(e,t);return{value:i,transform:i&&`scaleY(${i})`}}},m={duration:333,easing:"ease-in-out"},f=["left","top","width","height","opacity","color","background"],v=new WeakMap;class y extends o.s{constructor(e){if(super(e),this.t=null,this.i=null,this.o=!0,this.shouldLog=!1,e.type===n.pX.CHILD)throw Error("The `animate` directive must be used in attribute position.");this.createFinished()}createFinished(){var e;null===(e=this.resolveFinished)||void 0===e||e.call(this),this.finished=new Promise((e=>{this.h=e}))}async resolveFinished(){var e;null===(e=this.h)||void 0===e||e.call(this),this.h=void 0}render(e){return r.Ld}getController(){return s.get(this.l)}isDisabled(){var e;return this.options.disabled||(null===(e=this.getController())||void 0===e?void 0:e.disabled)}update(e,[t]){var i;const r=void 0===this.l;return r&&(this.l=null===(i=e.options)||void 0===i?void 0:i.host,this.l.addController(this),this.element=e.element,v.set(this.element,this)),this.optionsOrCallback=t,(r||"function"!=typeof t)&&this.u(t),this.render(t)}u(e){var t,i;e=null!=e?e:{};const r=this.getController();void 0!==r&&((e={...r.defaultOptions,...e}).keyframeOptions={...r.defaultOptions.keyframeOptions,...e.keyframeOptions}),null!==(t=(i=e).properties)&&void 0!==t||(i.properties=f),this.options=e}v(){const e={},t=this.element.getBoundingClientRect(),i=getComputedStyle(this.element);return this.options.properties.forEach((r=>{var n;const o=null!==(n=t[r])&&void 0!==n?n:u[r]?void 0:i[r],s=Number(o);e[r]=isNaN(s)?o+"":s})),e}p(){let e,t=!0;return this.options.guard&&(e=this.options.guard(),t=((e,t)=>{if(Array.isArray(e)){if(Array.isArray(t)&&t.length===e.length&&e.every(((e,i)=>e===t[i])))return!1}else if(t===e)return!1;return!0})(e,this.m)),this.o=this.l.hasUpdated&&!this.isDisabled()&&!this.isAnimating()&&t&&this.element.isConnected,this.o&&(this.m=Array.isArray(e)?Array.from(e):e),this.o}hostUpdate(){var e;"function"==typeof this.optionsOrCallback&&this.u(this.optionsOrCallback()),this.p()&&(this.g=this.v(),this.t=null!==(e=this.t)&&void 0!==e?e:this.element.parentNode,this.i=this.element.nextSibling)}async hostUpdated(){if(!this.o||!this.element.isConnected||this.options.skipInitial&&!this.isHostRendered)return;let e;this.prepare(),await c;const t=this.A(),i=this._(this.options.keyframeOptions,t),r=this.v();if(void 0!==this.g){const{from:i,to:n}=this.j(this.g,r,t);this.log("measured",[this.g,r,i,n]),e=this.calculateKeyframes(i,n)}else{const i=l.get(this.options.inId);if(i){l.delete(this.options.inId);const{from:n,to:o}=this.j(i,r,t);e=this.calculateKeyframes(n,o),e=this.options.in?[{...this.options.in[0],...e[0]},...this.options.in.slice(1),e[1]]:e,a++,e.forEach((e=>e.zIndex=a))}else this.options.in&&(e=[...this.options.in,{}])}this.animate(e,i)}resetStyles(){var e;void 0!==this.S&&(this.element.setAttribute("style",null!==(e=this.S)&&void 0!==e?e:""),this.S=void 0)}commitStyles(){var e,t;this.S=this.element.getAttribute("style"),null===(e=this.webAnimation)||void 0===e||e.commitStyles(),null===(t=this.webAnimation)||void 0===t||t.cancel()}reconnected(){}async disconnected(){var e;if(!this.o)return;if(void 0!==this.options.id&&l.set(this.options.id,this.g),void 0===this.options.out)return;if(this.prepare(),await c(),null===(e=this.t)||void 0===e?void 0:e.isConnected){const e=this.i&&this.i.parentNode===this.t?this.i:null;if(this.t.insertBefore(this.element,e),this.options.stabilizeOut){const e=this.v();this.log("stabilizing out");const t=this.g.left-e.left,i=this.g.top-e.top;!("static"===getComputedStyle(this.element).position)||0===t&&0===i||(this.element.style.position="relative"),0!==t&&(this.element.style.left=t+"px"),0!==i&&(this.element.style.top=i+"px")}}const t=this._(this.options.keyframeOptions);await this.animate(this.options.out,t),this.element.remove()}prepare(){this.createFinished()}start(){var e,t;null===(t=(e=this.options).onStart)||void 0===t||t.call(e,this)}didFinish(e){var t,i;e&&(null===(i=(t=this.options).onComplete)||void 0===i||i.call(t,this)),this.g=void 0,this.animatingProperties=void 0,this.frames=void 0,this.resolveFinished()}A(){const e=[];for(let t=this.element.parentNode;t;t=null==t?void 0:t.parentNode){const i=v.get(t);i&&!i.isDisabled()&&i&&e.push(i)}return e}get isHostRendered(){const e=d.has(this.l);return e||this.l.updateComplete.then((()=>{d.add(this.l)})),e}_(e,t=this.A()){const i={...m};return t.forEach((e=>Object.assign(i,e.options.keyframeOptions))),Object.assign(i,e),i}j(e,t,i){e={...e},t={...t};const r=i.map((e=>e.animatingProperties)).filter((e=>void 0!==e));let n=1,o=1;return void 0!==r&&(r.forEach((e=>{e.width&&(n/=e.width),e.height&&(o/=e.height)})),void 0!==e.left&&void 0!==t.left&&(e.left=n*e.left,t.left=n*t.left),void 0!==e.top&&void 0!==t.top&&(e.top=o*e.top,t.top=o*t.top)),{from:e,to:t}}calculateKeyframes(e,t,i=!1){var r;const n={},o={};let s=!1;const a={};for(const i in t){const l=e[i],d=t[i];if(i in u){const e=u[i];if(void 0===l||void 0===d)continue;const t=e(l,d);void 0!==t.transform&&(a[i]=t.value,s=!0,n.transform=`${null!==(r=n.transform)&&void 0!==r?r:""} ${t.transform}`)}else l!==d&&void 0!==l&&void 0!==d&&(s=!0,n[i]=l,o[i]=d)}return n.transformOrigin=o.transformOrigin=i?"center center":"top left",this.animatingProperties=a,s?[n,o]:void 0}async animate(e,t=this.options.keyframeOptions){this.start(),this.frames=e;let i=!1;if(!this.isAnimating()&&!this.isDisabled()&&(this.options.onFrames&&(this.frames=e=this.options.onFrames(this),this.log("modified frames",e)),void 0!==e)){this.log("animate",[e,t]),i=!0,this.webAnimation=this.element.animate(e,t);const r=this.getController();null==r||r.add(this);try{await this.webAnimation.finished}catch(e){}null==r||r.remove(this)}return this.didFinish(i),i}isAnimating(){var e,t;return"running"===(null===(e=this.webAnimation)||void 0===e?void 0:e.playState)||(null===(t=this.webAnimation)||void 0===t?void 0:t.pending)}log(e,t){this.shouldLog&&!this.isDisabled()&&console.log(e,this.options.id,t)}}const g=(0,n.XM)(y),b=["top","right","bottom","left"];class k extends o.s{constructor(e){if(super(e),e.type!==n.pX.ELEMENT)throw Error("The `position` directive must be used in attribute position.")}render(e,t){return r.Ld}update(e,[t,i]){var r;return void 0===this.l&&(this.l=null===(r=e.options)||void 0===r?void 0:r.host,this.l.addController(this)),this.$=e.element,this.k=t,this.F=null!=i?i:["left","top","width","height"],this.render(t,i)}hostUpdated(){this.O()}O(){var e,t;const i="function"==typeof this.k?this.k():null===(e=this.k)||void 0===e?void 0:e.value,r=i.offsetParent;if(void 0===i||!r)return;const n=i.getBoundingClientRect(),o=r.getBoundingClientRect();null===(t=this.F)||void 0===t||t.forEach((e=>{const t=b.includes(e)?n[e]-o[e]:n[e];this.$.style[e]=t+"px"}))}}(0,n.XM)(k);i(24103),i(44577);var w=i(68546),_=i(37500),E=i(59036),C=i(86230),A=i(18394),x=i(51750),S=i(78889),D=i(23469),P=i(11285),$=i(29950);i(39098),i(9828),i(95469),i(37662),i(41911),i(82960),i(51187);function z(){z=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!T(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return B(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?B(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=M(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:j(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=j(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function I(e){var t,i=M(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function O(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function T(e){return e.decorators&&e.decorators.length}function F(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function j(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function M(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function B(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}!function(e,t,i,r){var n=z();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(F(o.descriptor)||F(n.descriptor)){if(T(o)||T(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(T(o)){if(T(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}O(o,n)}else t.push(o)}return t}(s.d.map(I)),e);n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,E.Mo)("ha-media-upload-button")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,E.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,E.Cb)()],key:"currentItem",value:void 0},{kind:"field",decorators:[(0,E.SB)()],key:"_uploading",value:()=>0},{kind:"method",key:"render",value:function(){return this.currentItem&&(0,D.aV)(this.currentItem.media_content_id||"")?_.dy`
      <mwc-button
        .label=${this._uploading>0?this.hass.localize("ui.components.media-browser.file_management.uploading",{count:this._uploading}):this.hass.localize("ui.components.media-browser.file_management.add_media")}
        .disabled=${this._uploading>0}
        @click=${this._startUpload}
      >
        ${this._uploading>0?_.dy`
              <ha-circular-progress
                size="tiny"
                active
                alt=""
                slot="icon"
              ></ha-circular-progress>
            `:_.dy` <ha-svg-icon .path=${w.xyB} slot="icon"></ha-svg-icon> `}
      </mwc-button>
    `:_.dy``}},{kind:"method",key:"_startUpload",value:async function(){if(this._uploading>0)return;const e=document.createElement("input");e.type="file",e.accept="audio/*,video/*,image/*",e.multiple=!0,e.addEventListener("change",(async()=>{(0,A.B)(this,"uploading");const t=e.files;document.body.removeChild(e);const i=this.currentItem.media_content_id;for(let e=0;e<t.length;e++){this._uploading=t.length-e;try{await(0,D.oE)(this.hass,i,t[e])}catch(e){(0,P.Ys)(this,{text:this.hass.localize("ui.components.media-browser.file_management.upload_failed",{reason:e.message||e})});break}}this._uploading=0,(0,A.B)(this,"media-refresh")}),{once:!0}),e.style.display="none",document.body.append(e),e.click()}},{kind:"field",static:!0,key:"styles",value:()=>_.iv`
    mwc-button {
      /* We use icon + text to show disabled state */
      --mdc-button-disabled-ink-color: --mdc-theme-primary;
    }

    ha-svg-icon[slot="icon"],
    ha-circular-progress[slot="icon"] {
      vertical-align: middle;
    }

    ha-svg-icon[slot="icon"] {
      margin-inline-start: 0px;
      margin-inline-end: 8px;
      direction: var(--direction);
    }
  `}]}}),_.oi);function U(){U=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!L(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return H(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?H(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=W(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:K(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=K(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function N(e){var t,i=W(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function R(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function L(e){return e.decorators&&e.decorators.length}function X(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function K(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function W(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function H(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}!function(e,t,i,r){var n=U();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(X(o.descriptor)||X(n.descriptor)){if(L(o)||L(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(L(o)){if(L(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}R(o,n)}else t.push(o)}return t}(s.d.map(N)),e);n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,E.Mo)("dialog-media-manage")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,E.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,E.SB)()],key:"_currentItem",value:void 0},{kind:"field",decorators:[(0,E.SB)()],key:"_params",value:void 0},{kind:"field",decorators:[(0,E.SB)()],key:"_uploading",value:()=>!1},{kind:"field",decorators:[(0,E.SB)()],key:"_deleting",value:()=>!1},{kind:"field",decorators:[(0,E.SB)()],key:"_selected",value:()=>new Set},{kind:"field",key:"_filesChanged",value:()=>!1},{kind:"method",key:"showDialog",value:function(e){this._params=e,this._refreshMedia()}},{kind:"method",key:"closeDialog",value:function(){this._filesChanged&&this._params.onClose&&this._params.onClose(),this._params=void 0,this._currentItem=void 0,this._uploading=!1,this._deleting=!1,this._filesChanged=!1,(0,A.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"method",key:"render",value:function(){var e,t,i,r;if(!this._params)return _.dy``;const n=(null===(e=this._currentItem)||void 0===e||null===(t=e.children)||void 0===t?void 0:t.filter((e=>!e.can_expand)))||[];let o=0;return _.dy`
      <ha-dialog
        open
        scrimClickAction
        escapeKeyAction
        hideActions
        flexContent
        .heading=${this._params.currentItem.title}
        @closed=${this.closeDialog}
      >
        <ha-header-bar slot="heading">
          ${0===this._selected.size?_.dy`
                <span slot="title">
                  ${this.hass.localize("ui.components.media-browser.file_management.title")}
                </span>

                <ha-media-upload-button
                  .disabled=${this._deleting}
                  .hass=${this.hass}
                  .currentItem=${this._params.currentItem}
                  @uploading=${this._startUploading}
                  @media-refresh=${this._doneUploading}
                  slot="actionItems"
                ></ha-media-upload-button>
                ${this._uploading?"":_.dy`
                      <ha-icon-button
                        .label=${this.hass.localize("ui.dialogs.generic.close")}
                        .path=${w.r5M}
                        dialogAction="close"
                        slot="actionItems"
                        class="header_button"
                        dir=${(0,x.Zu)(this.hass)}
                      ></ha-icon-button>
                    `}
              `:_.dy`
                <mwc-button
                  class="danger"
                  slot="title"
                  .disabled=${this._deleting}
                  .label=${this.hass.localize("ui.components.media-browser.file_management."+(this._deleting?"deleting":"delete"),{count:this._selected.size})}
                  @click=${this._handleDelete}
                >
                  <ha-svg-icon .path=${w.x9U} slot="icon"></ha-svg-icon>
                </mwc-button>

                ${this._deleting?"":_.dy`
                      <mwc-button
                        slot="actionItems"
                        .label=${"Deselect all"}
                        @click=${this._handleDeselectAll}
                      >
                        <ha-svg-icon
                          .path=${w.r5M}
                          slot="icon"
                        ></ha-svg-icon>
                      </mwc-button>
                    `}
              `}
        </ha-header-bar>
        ${this._currentItem?n.length?_.dy`
              <mwc-list multi @selected=${this._handleSelected}>
                ${(0,C.r)(n,(e=>e.media_content_id),(e=>{const t=_.dy`
                      <ha-svg-icon
                        slot="graphic"
                        .path=${S.Fn["directory"===e.media_class&&e.children_media_class||e.media_class].icon}
                      ></ha-svg-icon>
                    `;return _.dy`
                      <ha-check-list-item
                        ${g({id:e.media_content_id,skipInitial:!0})}
                        graphic="icon"
                        .disabled=${this._uploading||this._deleting}
                        .selected=${this._selected.has(o++)}
                        .item=${e}
                      >
                        ${t} ${e.title}
                      </ha-check-list-item>
                    `}))}
              </mwc-list>
            `:_.dy`<div class="no-items">
              <p>
                ${this.hass.localize("ui.components.media-browser.file_management.no_items")}
              </p>
              ${null!==(i=this._currentItem)&&void 0!==i&&null!==(r=i.children)&&void 0!==r&&r.length?_.dy`<span class="folders"
                    >${this.hass.localize("ui.components.media-browser.file_management.folders_not_supported")}</span
                  >`:""}
            </div>`:_.dy`
              <div class="refresh">
                <ha-circular-progress active></ha-circular-progress>
              </div>
            `}
      </ha-dialog>
    `}},{kind:"method",key:"_handleSelected",value:function(e){this._selected=e.detail.index}},{kind:"method",key:"_startUploading",value:function(){this._uploading=!0,this._filesChanged=!0}},{kind:"method",key:"_doneUploading",value:function(){this._uploading=!1,this._refreshMedia()}},{kind:"method",key:"_handleDeselectAll",value:function(){this._selected.size&&(this._selected=new Set)}},{kind:"method",key:"_handleDelete",value:async function(){if(!await(0,P.g7)(this,{text:this.hass.localize("ui.components.media-browser.file_management.confirm_delete",{count:this._selected.size}),warning:!0}))return;this._filesChanged=!0,this._deleting=!0;const e=[];let t=0;this._currentItem.children.forEach((i=>{i.can_expand||this._selected.has(t++)&&e.push(i)}));try{await Promise.all(e.map((async e=>{await(0,D.Qr)(this.hass,e.media_content_id),this._currentItem={...this._currentItem,children:this._currentItem.children.filter((t=>t!==e))}})))}finally{this._deleting=!1,this._selected=new Set}}},{kind:"method",key:"_refreshMedia",value:async function(){this._selected=new Set,this._currentItem=void 0,this._currentItem=await(0,D.b)(this.hass,this._params.currentItem.media_content_id)}},{kind:"get",static:!0,key:"styles",value:function(){return[$.yu,_.iv`
        ha-dialog {
          --dialog-z-index: 8;
          --dialog-content-padding: 0;
        }

        @media (min-width: 800px) {
          ha-dialog {
            --mdc-dialog-max-width: 800px;
            --dialog-surface-position: fixed;
            --dialog-surface-top: 40px;
            --mdc-dialog-max-height: calc(100vh - 72px);
          }
        }

        ha-header-bar {
          --mdc-theme-on-primary: var(--primary-text-color);
          --mdc-theme-primary: var(--mdc-theme-surface);
          flex-shrink: 0;
          border-bottom: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
        }

        ha-media-upload-button,
        mwc-button {
          --mdc-theme-primary: var(--mdc-theme-on-primary);
        }

        mwc-list {
          direction: ltr;
        }

        .danger {
          --mdc-theme-primary: var(--error-color);
        }

        ha-svg-icon[slot="icon"] {
          vertical-align: middle;
        }

        ha-svg-icon[slot="icon"] {
          margin-inline-start: 0px !important;
          margin-inline-end: 8px !important;
          direction: var(--direction);
        }

        .refresh {
          display: flex;
          height: 200px;
          justify-content: center;
          align-items: center;
        }

        .no-items {
          text-align: center;
          padding: 16px;
        }
        .folders {
          color: var(--secondary-text-color);
          font-style: italic;
        }
      `]}}]}}),_.oi)}}]);