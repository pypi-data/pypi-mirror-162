"use strict";(self.webpackChunkreact_frontend=self.webpackChunkreact_frontend||[]).push([[2299],{32299:(e,t,i)=>{i.r(t);i(51187);var r=i(68546),s=i(37500),n=i(59036),a=i(18394),o=(i(23860),i(39098),i(9828)),c=(i(48950),i(44577),i(86089));i(85878),i(51520);function l(){l=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var s=t.placement;if(t.kind===r&&("static"===s||"prototype"===s)){var n="static"===s?e:i;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],s={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,s)}),this),e.forEach((function(e){if(!h(e))return i.push(e);var t=this.decorateElement(e,s);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var n=this.decorateConstructor(i,t);return r.push.apply(r,n.finishers),n.finishers=r,n},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],s=e.decorators,n=s.length-1;n>=0;n--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var o=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,s[n])(o)||o);e=c.element,this.addElementPlacement(e,t),c.finisher&&r.push(c.finisher);var l=c.extras;if(l){for(var d=0;d<l.length;d++)this.addElementPlacement(l[d],t);i.push.apply(i,l)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var s=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[r])(s)||s);if(void 0!==n.finisher&&i.push(n.finisher),void 0!==n.elements){e=n.elements;for(var a=0;a<e.length-1;a++)for(var o=a+1;o<e.length;o++)if(e[a].key===e[o].key&&e[a].placement===e[o].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return y(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?y(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=v(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var s=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:i,placement:r,descriptor:Object.assign({},s)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(s,"get","The property descriptor of a field descriptor"),this.disallowProperty(s,"set","The property descriptor of a field descriptor"),this.disallowProperty(s,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:f(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=f(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function d(e){var t,i=v(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function u(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function h(e){return e.decorators&&e.decorators.length}function p(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function f(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function v(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function y(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function m(){return m="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=_(e,t);if(r){var s=Object.getOwnPropertyDescriptor(r,t);return s.get?s.get.call(arguments.length<3?e:i):s.value}},m.apply(this,arguments)}function _(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=g(e)););return e}function g(e){return g=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},g(e)}!function(e,t,i,r){var s=l();if(r)for(var n=0;n<r.length;n++)s=r[n](s);var a=t((function(e){s.initializeInstanceElements(e,o.elements)}),i),o=s.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},r=0;r<e.length;r++){var s,n=e[r];if("method"===n.kind&&(s=t.find(i)))if(p(n.descriptor)||p(s.descriptor)){if(h(n)||h(s))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");s.descriptor=n.descriptor}else{if(h(n)){if(h(s))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");s.decorators=n.decorators}u(n,s)}else t.push(n)}return t}(a.d.map(d)),e);s.initializeClassElements(a.F,o.elements),s.runClassFinishers(a.F,o.finishers)}([(0,n.Mo)("ha-qr-scanner")],(function(e,t){class o extends t{constructor(...t){super(...t),e(this)}}return{F:o,d:[{kind:"field",decorators:[(0,n.Cb)()],key:"localize",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_cameras",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_error",value:void 0},{kind:"field",key:"_qrScanner",value:void 0},{kind:"field",key:"_qrNotFoundCount",value:()=>0},{kind:"field",decorators:[(0,n.IO)("video",!0)],key:"_video",value:void 0},{kind:"field",decorators:[(0,n.IO)("#canvas-container",!0)],key:"_canvasContainer",value:void 0},{kind:"field",decorators:[(0,n.IO)("ha-textfield")],key:"_manualInput",value:void 0},{kind:"method",key:"disconnectedCallback",value:function(){for(m(g(o.prototype),"disconnectedCallback",this).call(this),this._qrNotFoundCount=0,this._qrScanner&&(this._qrScanner.stop(),this._qrScanner.destroy(),this._qrScanner=void 0);this._canvasContainer.lastChild;)this._canvasContainer.removeChild(this._canvasContainer.lastChild)}},{kind:"method",key:"connectedCallback",value:function(){m(g(o.prototype),"connectedCallback",this).call(this),this.hasUpdated&&navigator.mediaDevices&&this._loadQrScanner()}},{kind:"method",key:"firstUpdated",value:function(){navigator.mediaDevices&&this._loadQrScanner()}},{kind:"method",key:"updated",value:function(e){e.has("_error")&&this._error&&(0,a.B)(this,"qr-code-error",{message:this._error})}},{kind:"method",key:"render",value:function(){return s.dy`${this._error?s.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
    ${navigator.mediaDevices?s.dy`<video></video>
          <div id="canvas-container">
            ${this._cameras&&this._cameras.length>1?s.dy`<ha-button-menu
                  corner="BOTTOM_START"
                  fixed
                  @closed=${c.U}
                >
                  <ha-icon-button
                    slot="trigger"
                    .label=${this.localize("ui.components.qr-scanner.select_camera")}
                    .path=${r.pJw}
                  ></ha-icon-button>
                  ${this._cameras.map((e=>s.dy`
                      <mwc-list-item
                        .value=${e.id}
                        @click=${this._cameraChanged}
                        >${e.label}</mwc-list-item
                      >
                    `))}
                </ha-button-menu>`:""}
          </div>`:s.dy`<ha-alert alert-type="warning">
            ${window.isSecureContext?this.localize("ui.components.qr-scanner.not_supported"):this.localize("ui.components.qr-scanner.only_https_supported")}
          </ha-alert>
          <p>${this.localize("ui.components.qr-scanner.manual_input")}</p>
          <div class="row">
            <ha-textfield
              .label=${this.localize("ui.components.qr-scanner.enter_qr_code")}
              @keyup=${this._manualKeyup}
              @paste=${this._manualPaste}
            ></ha-textfield>
            <mwc-button @click=${this._manualSubmit}
              >${this.localize("ui.common.submit")}</mwc-button
            >
          </div>`}`}},{kind:"method",key:"_loadQrScanner",value:async function(){const e=(await i.e(1858).then(i.bind(i,31858))).default;if(!await e.hasCamera())return void(this._error="No camera found");e.WORKER_PATH="/static/js/qr-scanner-worker.min.js",this._listCameras(e),this._qrScanner=new e(this._video,this._qrCodeScanned,this._qrCodeError);const t=this._qrScanner.$canvas;this._canvasContainer.appendChild(t),t.style.display="block";try{await this._qrScanner.start()}catch(e){this._error=e}}},{kind:"method",key:"_listCameras",value:async function(e){this._cameras=await e.listCameras(!0)}},{kind:"field",key:"_qrCodeError",value(){return e=>{if("No QR code found"===e)return this._qrNotFoundCount++,void(250===this._qrNotFoundCount&&(this._error=e));this._error=e.message||e,console.log(e)}}},{kind:"field",key:"_qrCodeScanned",value(){return async e=>{this._qrNotFoundCount=0,(0,a.B)(this,"qr-code-scanned",{value:e})}}},{kind:"method",key:"_manualKeyup",value:function(e){"Enter"===e.key&&this._qrCodeScanned(e.target.value)}},{kind:"method",key:"_manualPaste",value:function(e){this._qrCodeScanned((e.clipboardData||window.clipboardData).getData("text"))}},{kind:"method",key:"_manualSubmit",value:function(){this._qrCodeScanned(this._manualInput.value)}},{kind:"method",key:"_cameraChanged",value:function(e){var t;null===(t=this._qrScanner)||void 0===t||t.setCamera(e.target.value)}},{kind:"field",static:!0,key:"styles",value:()=>s.iv`
    canvas {
      width: 100%;
    }
    #canvas-container {
      position: relative;
    }
    ha-button-menu {
      position: absolute;
      bottom: 8px;
      right: 8px;
      background: #727272b2;
      color: white;
      border-radius: 50%;
    }
    .row {
      display: flex;
      align-items: center;
    }
    ha-textfield {
      flex: 1;
      margin-right: 8px;
    }
  `}]}}),s.oi);i(19096),i(84323);let k,b,w,S;var C,$;!function(e){e[e.Idle=0]="Idle",e[e.Including=1]="Including",e[e.Excluding=2]="Excluding",e[e.Busy=3]="Busy",e[e.SmartStart=4]="SmartStart"}(k||(k={})),function(e){e[e.Default=0]="Default",e[e.SmartStart=1]="SmartStart",e[e.Insecure=2]="Insecure",e[e.Security_S0=3]="Security_S0",e[e.Security_S2=4]="Security_S2"}(b||(b={})),function(e){e[e.Temporary=-2]="Temporary",e[e.None=-1]="None",e[e.S2_Unauthenticated=0]="S2_Unauthenticated",e[e.S2_Authenticated=1]="S2_Authenticated",e[e.S2_AccessControl=2]="S2_AccessControl",e[e.S0_Legacy=7]="S0_Legacy"}(w||(w={})),function(e){e[e.SmartStart=0]="SmartStart"}(S||(S={})),function(e){e[e.S2=0]="S2",e[e.SmartStart=1]="SmartStart"}(C||(C={})),function(e){e[e.ZWave=0]="ZWave",e[e.ZWaveLongRange=1]="ZWaveLongRange"}($||($={}));let E;!function(e){e[e.Unknown=0]="Unknown",e[e.Asleep=1]="Asleep",e[e.Awake=2]="Awake",e[e.Dead=3]="Dead",e[e.Alive=4]="Alive"}(E||(E={}));const x=(e,t,i,r)=>e.callWS({type:"zwave_js/grant_security_classes",entry_id:t,security_classes:i,client_side_auth:r});var z=i(29950);function P(){P=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var s=t.placement;if(t.kind===r&&("static"===s||"prototype"===s)){var n="static"===s?e:i;this.defineClassElement(n,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],s={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,s)}),this),e.forEach((function(e){if(!A(e))return i.push(e);var t=this.decorateElement(e,s);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var n=this.decorateConstructor(i,t);return r.push.apply(r,n.finishers),n.finishers=r,n},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],s=e.decorators,n=s.length-1;n>=0;n--){var a=t[e.placement];a.splice(a.indexOf(e.key),1);var o=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,s[n])(o)||o);e=c.element,this.addElementPlacement(e,t),c.finisher&&r.push(c.finisher);var l=c.extras;if(l){for(var d=0;d<l.length;d++)this.addElementPlacement(l[d],t);i.push.apply(i,l)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var s=this.fromClassDescriptor(e),n=this.toClassDescriptor((0,t[r])(s)||s);if(void 0!==n.finisher&&i.push(n.finisher),void 0!==n.elements){e=n.elements;for(var a=0;a<e.length-1;a++)for(var o=a+1;o<e.length;o++)if(e[a].key===e[o].key&&e[a].placement===e[o].placement)throw new TypeError("Duplicated element ("+e[a].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return I(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?I(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=O(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var s=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var n={kind:t,key:i,placement:r,descriptor:Object.assign({},s)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(s,"get","The property descriptor of a field descriptor"),this.disallowProperty(s,"set","The property descriptor of a field descriptor"),this.disallowProperty(s,"value","The property descriptor of a field descriptor"),n.initializer=e.initializer),n},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:T(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=T(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function D(e){var t,i=O(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function q(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function A(e){return e.decorators&&e.decorators.length}function j(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function T(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function O(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function I(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function F(){return F="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=N(e,t);if(r){var s=Object.getOwnPropertyDescriptor(r,t);return s.get?s.get.call(arguments.length<3?e:i):s.value}},F.apply(this,arguments)}function N(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=R(e)););return e}function R(e){return R=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},R(e)}!function(e,t,i,r){var s=P();if(r)for(var n=0;n<r.length;n++)s=r[n](s);var a=t((function(e){s.initializeInstanceElements(e,o.elements)}),i),o=s.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===n.key&&e.placement===n.placement},r=0;r<e.length;r++){var s,n=e[r];if("method"===n.kind&&(s=t.find(i)))if(j(n.descriptor)||j(s.descriptor)){if(A(n)||A(s))throw new ReferenceError("Duplicated methods ("+n.key+") can't be decorated.");s.descriptor=n.descriptor}else{if(A(n)){if(A(s))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+n.key+").");s.decorators=n.decorators}q(n,s)}else t.push(n)}return t}(a.d.map(D)),e);s.initializeClassElements(a.F,o.elements),s.runClassFinishers(a.F,o.finishers)}([(0,n.Mo)("dialog-zwave_js-add-node")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"field",decorators:[(0,n.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_params",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_entryId",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_status",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_device",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_stages",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_inclusionStrategy",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_dsk",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_requestedGrant",value:void 0},{kind:"field",decorators:[(0,n.SB)()],key:"_securityClasses",value:()=>[]},{kind:"field",decorators:[(0,n.SB)()],key:"_lowSecurity",value:()=>!1},{kind:"field",decorators:[(0,n.SB)()],key:"_supportsSmartStart",value:void 0},{kind:"field",key:"_addNodeTimeoutHandle",value:void 0},{kind:"field",key:"_subscribed",value:void 0},{kind:"field",key:"_qrProcessing",value:()=>!1},{kind:"method",key:"disconnectedCallback",value:function(){F(R(i.prototype),"disconnectedCallback",this).call(this),this._unsubscribe()}},{kind:"method",key:"showDialog",value:async function(e){this._params=e,this._entryId=e.entry_id,this._status="loading",this._checkSmartStartSupport(),this._startInclusion()}},{kind:"field",decorators:[(0,n.IO)("#pin-input")],key:"_pinInput",value:void 0},{kind:"method",key:"render",value:function(){var e;return this._entryId?s.dy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        .heading=${(0,o.i)(this.hass,this.hass.localize("ui.panel.config.zwave_js.add_node.title"))}
      >
        ${"loading"===this._status?s.dy`<div style="display: flex; justify-content: center;">
              <ha-circular-progress size="large" active></ha-circular-progress>
            </div>`:"choose_strategy"===this._status?s.dy`<h3>Choose strategy</h3>
              <div class="flex-column">
                <ha-formfield
                  .label=${s.dy`<b>Secure if possible</b>
                    <div class="secondary">
                      Requires user interaction during inclusion. Fast and
                      secure with S2 when supported. Fallback to legacy S0 or no
                      encryption when necessary.
                    </div>`}
                >
                  <ha-radio
                    name="strategy"
                    @change=${this._handleStrategyChange}
                    .value=${b.Default}
                    .checked=${this._inclusionStrategy===b.Default||void 0===this._inclusionStrategy}
                  >
                  </ha-radio>
                </ha-formfield>
                <ha-formfield
                  .label=${s.dy`<b>Legacy Secure</b>
                    <div class="secondary">
                      Uses the older S0 security that is secure, but slow due to
                      a lot of overhead. Allows securely including S2 capable
                      devices which fail to be included with S2.
                    </div>`}
                >
                  <ha-radio
                    name="strategy"
                    @change=${this._handleStrategyChange}
                    .value=${b.Security_S0}
                    .checked=${this._inclusionStrategy===b.Security_S0}
                  >
                  </ha-radio>
                </ha-formfield>
                <ha-formfield
                  .label=${s.dy`<b>Insecure</b>
                    <div class="secondary">Do not use encryption.</div>`}
                >
                  <ha-radio
                    name="strategy"
                    @change=${this._handleStrategyChange}
                    .value=${b.Insecure}
                    .checked=${this._inclusionStrategy===b.Insecure}
                  >
                  </ha-radio>
                </ha-formfield>
              </div>
              <mwc-button
                slot="primaryAction"
                @click=${this._startManualInclusion}
              >
                Search device
              </mwc-button>`:"qr_scan"===this._status?s.dy`${this._error?s.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
              <ha-qr-scanner
                .localize=${this.hass.localize}
                @qr-code-scanned=${this._qrCodeScanned}
              ></ha-qr-scanner>
              <mwc-button slot="secondaryAction" @click=${this._startOver}>
                ${this.hass.localize("ui.panel.config.zwave_js.common.back")}
              </mwc-button>`:"validate_dsk_enter_pin"===this._status?s.dy`
                <p>
                  Please enter the 5-digit PIN for your device and verify that
                  the rest of the device-specific key matches the one that can
                  be found on your device or the manual.
                </p>
                ${this._error?s.dy`<ha-alert alert-type="error">
                        ${this._error}
                      </ha-alert>`:""}
                <div class="flex-container">
                <ha-textfield
                  label="PIN"
                  id="pin-input"
                  @keyup=${this._handlePinKeyUp}
                ></ha-textfield>
                ${this._dsk}
                </div>
                <mwc-button
                  slot="primaryAction"
                  @click=${this._validateDskAndEnterPin}
                >
                  Submit
                </mwc-button>
              </div>
            `:"grant_security_classes"===this._status?s.dy`
              <h3>The device has requested the following security classes:</h3>
              ${this._error?s.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
              <div class="flex-column">
                ${null===(e=this._requestedGrant)||void 0===e?void 0:e.securityClasses.sort().reverse().map((e=>s.dy`<ha-formfield
                      .label=${s.dy`<b
                          >${this.hass.localize(`ui.panel.config.zwave_js.security_classes.${w[e]}.title`)}</b
                        >
                        <div class="secondary">
                          ${this.hass.localize(`ui.panel.config.zwave_js.security_classes.${w[e]}.description`)}
                        </div>`}
                    >
                      <ha-checkbox
                        @change=${this._handleSecurityClassChange}
                        .value=${e}
                        .checked=${this._securityClasses.includes(e)}
                      >
                      </ha-checkbox>
                    </ha-formfield>`))}
              </div>
              <mwc-button
                slot="primaryAction"
                .disabled=${!this._securityClasses.length}
                @click=${this._grantSecurityClasses}
              >
                Submit
              </mwc-button>
            `:"timed_out"===this._status?s.dy`
              <h3>Timed out!</h3>
              <p>
                We have not found any device in inclusion mode. Make sure the
                device is active and in inclusion mode.
              </p>
              <mwc-button slot="primaryAction" @click=${this._startOver}>
                Retry
              </mwc-button>
            `:"started_specific"===this._status?s.dy`<h3>
                ${this.hass.localize("ui.panel.config.zwave_js.add_node.searching_device")}
              </h3>
              <ha-circular-progress active></ha-circular-progress>
              <p>
                ${this.hass.localize("ui.panel.config.zwave_js.add_node.follow_device_instructions")}
              </p>`:"started"===this._status?s.dy`
              <div class="select-inclusion">
                <div class="outline">
                  <h2>
                    ${this.hass.localize("ui.panel.config.zwave_js.add_node.searching_device")}
                  </h2>
                  <ha-circular-progress active></ha-circular-progress>
                  <p>
                    ${this.hass.localize("ui.panel.config.zwave_js.add_node.follow_device_instructions")}
                  </p>
                  <p>
                    <button
                      class="link"
                      @click=${this._chooseInclusionStrategy}
                    >
                      ${this.hass.localize("ui.panel.config.zwave_js.add_node.choose_inclusion_strategy")}
                    </button>
                  </p>
                </div>
                ${this._supportsSmartStart?s.dy` <div class="outline">
                      <h2>
                        ${this.hass.localize("ui.panel.config.zwave_js.add_node.qr_code")}
                      </h2>
                      <ha-svg-icon .path=${r.R54}></ha-svg-icon>
                      <p>
                        ${this.hass.localize("ui.panel.config.zwave_js.add_node.qr_code_paragraph")}
                      </p>
                      <p>
                        <mwc-button @click=${this._scanQRCode}>
                          ${this.hass.localize("ui.panel.config.zwave_js.add_node.scan_qr_code")}
                        </mwc-button>
                      </p>
                    </div>`:""}
              </div>
              <mwc-button slot="primaryAction" @click=${this.closeDialog}>
                ${this.hass.localize("ui.common.cancel")}
              </mwc-button>
            `:"interviewing"===this._status?s.dy`
              <div class="flex-container">
                <ha-circular-progress active></ha-circular-progress>
                <div class="status">
                  <p>
                    <b
                      >${this.hass.localize("ui.panel.config.zwave_js.add_node.interview_started")}</b
                    >
                  </p>
                  ${this._stages?s.dy` <div class="stages">
                        ${this._stages.map((e=>s.dy`
                            <span class="stage">
                              <ha-svg-icon
                                .path=${r.OE9}
                                class="success"
                              ></ha-svg-icon>
                              ${e}
                            </span>
                          `))}
                      </div>`:""}
                </div>
              </div>
              <mwc-button slot="primaryAction" @click=${this.closeDialog}>
                ${this.hass.localize("ui.common.close")}
              </mwc-button>
            `:"failed"===this._status?s.dy`
              <div class="flex-container">
                <div class="status">
                  <ha-alert
                    alert-type="error"
                    .title=${this.hass.localize("ui.panel.config.zwave_js.add_node.inclusion_failed")}
                  >
                    ${this._error||this.hass.localize("ui.panel.config.zwave_js.add_node.check_logs")}
                  </ha-alert>
                  ${this._stages?s.dy` <div class="stages">
                        ${this._stages.map((e=>s.dy`
                            <span class="stage">
                              <ha-svg-icon
                                .path=${r.OE9}
                                class="success"
                              ></ha-svg-icon>
                              ${e}
                            </span>
                          `))}
                      </div>`:""}
                </div>
              </div>
              <mwc-button slot="primaryAction" @click=${this.closeDialog}>
                ${this.hass.localize("ui.panel.config.zwave_js.common.close")}
              </mwc-button>
            `:"finished"===this._status?s.dy`
              <div class="flex-container">
                <ha-svg-icon
                  .path=${this._lowSecurity?r.fr4:r.OE9}
                  class=${this._lowSecurity?"warning":"success"}
                ></ha-svg-icon>
                <div class="status">
                  <p>
                    ${this.hass.localize("ui.panel.config.zwave_js.add_node.inclusion_finished")}
                  </p>
                  ${this._lowSecurity?s.dy`<ha-alert
                        alert-type="warning"
                        title="The device was added insecurely"
                      >
                        There was an error during secure inclusion. You can try
                        again by excluding the device and adding it again.
                      </ha-alert>`:""}
                  <a href=${`/config/devices/device/${this._device.id}`}>
                    <mwc-button>
                      ${this.hass.localize("ui.panel.config.zwave_js.add_node.view_device")}
                    </mwc-button>
                  </a>
                  ${this._stages?s.dy` <div class="stages">
                        ${this._stages.map((e=>s.dy`
                            <span class="stage">
                              <ha-svg-icon
                                .path=${r.OE9}
                                class="success"
                              ></ha-svg-icon>
                              ${e}
                            </span>
                          `))}
                      </div>`:""}
                </div>
              </div>
              <mwc-button slot="primaryAction" @click=${this.closeDialog}>
                ${this.hass.localize("ui.panel.config.zwave_js.common.close")}
              </mwc-button>
            `:"provisioned"===this._status?s.dy` <div class="flex-container">
                <ha-svg-icon
                  .path=${r.OE9}
                  class="success"
                ></ha-svg-icon>
                <div class="status">
                  <p>
                    ${this.hass.localize("ui.panel.config.zwave_js.add_node.provisioning_finished")}
                  </p>
                </div>
              </div>
              <mwc-button slot="primaryAction" @click=${this.closeDialog}>
                ${this.hass.localize("ui.panel.config.zwave_js.common.close")}
              </mwc-button>`:""}
      </ha-dialog>
    `:s.dy``}},{kind:"method",key:"_chooseInclusionStrategy",value:function(){this._unsubscribe(),this._status="choose_strategy"}},{kind:"method",key:"_handleStrategyChange",value:function(e){this._inclusionStrategy=e.target.value}},{kind:"method",key:"_handleSecurityClassChange",value:function(e){const t=e.currentTarget,i=Number(t.value);t.checked&&!this._securityClasses.includes(i)?this._securityClasses=[...this._securityClasses,i]:t.checked||(this._securityClasses=this._securityClasses.filter((e=>e!==i)))}},{kind:"method",key:"_scanQRCode",value:async function(){this._unsubscribe(),this._status="qr_scan"}},{kind:"method",key:"_qrCodeScanned",value:function(e){this._qrProcessing||this._handleQrCodeScanned(e.detail.value)}},{kind:"method",key:"_handleQrCodeScanned",value:async function(e){if(this._error=void 0,"qr_scan"!==this._status||this._qrProcessing)return;if(this._qrProcessing=!0,e.length<52||!e.startsWith("90"))return this._qrProcessing=!1,void(this._error=`Invalid QR code (${e})`);let t;try{t=await(i=this.hass,r=this._entryId,s=e,i.callWS({type:"zwave_js/parse_qr_code_string",entry_id:r,qr_code_string:s}))}catch(e){return this._qrProcessing=!1,void(this._error=e.message)}var i,r,s;if(this._status="loading",this.updateComplete.then((()=>{this._qrProcessing=!1})),1===t.version)try{var n;await((e,t,i,r,s)=>e.callWS({type:"zwave_js/provision_smart_start_node",entry_id:t,qr_code_string:r,qr_provisioning_information:i,planned_provisioning_entry:s}))(this.hass,this._entryId,t),this._status="provisioned",null!==(n=this._params)&&void 0!==n&&n.addedCallback&&this._params.addedCallback()}catch(e){this._error=e.message,this._status="failed"}else 0===t.version?(this._inclusionStrategy=b.Security_S2,this._startInclusion(t)):(this._error="This QR code is not supported",this._status="failed")}},{kind:"method",key:"_handlePinKeyUp",value:function(e){"Enter"===e.key&&this._validateDskAndEnterPin()}},{kind:"method",key:"_validateDskAndEnterPin",value:async function(){this._status="loading",this._error=void 0;try{await(e=this.hass,t=this._entryId,i=this._pinInput.value,e.callWS({type:"zwave_js/validate_dsk_and_enter_pin",entry_id:t,pin:i}))}catch(e){this._error=e.message,this._status="validate_dsk_enter_pin"}var e,t,i}},{kind:"method",key:"_grantSecurityClasses",value:async function(){this._status="loading",this._error=void 0;try{await x(this.hass,this._entryId,this._securityClasses)}catch(e){this._error=e.message,this._status="grant_security_classes"}}},{kind:"method",key:"_startManualInclusion",value:function(){this._inclusionStrategy||(this._inclusionStrategy=b.Default),this._startInclusion()}},{kind:"method",key:"_checkSmartStartSupport",value:async function(){var e,t,i;this._supportsSmartStart=(await(e=this.hass,t=this._entryId,i=S.SmartStart,e.callWS({type:"zwave_js/supports_feature",entry_id:t,feature:i}))).supported}},{kind:"method",key:"_startOver",value:function(e){this._startInclusion()}},{kind:"method",key:"_startInclusion",value:function(e,t,i){if(!this.hass)return;this._lowSecurity=!1;const r=e||t||i;this._subscribed=((e,t,i,r=b.Default,s,n,a)=>e.connection.subscribeMessage((e=>i(e)),{type:"zwave_js/add_node",entry_id:t,inclusion_strategy:r,qr_code_string:n,qr_provisioning_information:s,planned_provisioning_entry:a}))(this.hass,this._entryId,(e=>{if("inclusion started"===e.event&&(this._status=r?"started_specific":"started"),"inclusion failed"===e.event&&(this._unsubscribe(),this._status="failed"),"inclusion stopped"===e.event&&(this._addNodeTimeoutHandle&&clearTimeout(this._addNodeTimeoutHandle),this._addNodeTimeoutHandle=void 0),"validate dsk and enter pin"===e.event&&(this._status="validate_dsk_enter_pin",this._dsk=e.dsk),"grant security classes"===e.event){if(void 0===this._inclusionStrategy)return void x(this.hass,this._entryId,e.requested_grant.securityClasses,e.requested_grant.clientSideAuth);this._requestedGrant=e.requested_grant,this._securityClasses=e.requested_grant.securityClasses,this._status="grant_security_classes"}var t;("device registered"===e.event&&(this._device=e.device),"node added"===e.event&&(this._status="interviewing",this._lowSecurity=e.node.low_security),"interview completed"===e.event)&&(this._unsubscribe(),this._status="finished",null!==(t=this._params)&&void 0!==t&&t.addedCallback&&this._params.addedCallback());"interview stage completed"===e.event&&(void 0===this._stages?this._stages=[e.stage]:this._stages=[...this._stages,e.stage])}),this._inclusionStrategy,e,t,i),this._addNodeTimeoutHandle=window.setTimeout((()=>{this._unsubscribe(),this._status="timed_out"}),9e4)}},{kind:"method",key:"_unsubscribe",value:function(){var e,t;this._subscribed&&(this._subscribed.then((e=>e())),this._subscribed=void 0),this._entryId&&(e=this.hass,t=this._entryId,e.callWS({type:"zwave_js/stop_inclusion",entry_id:t})),this._requestedGrant=void 0,this._dsk=void 0,this._securityClasses=[],this._status=void 0,this._addNodeTimeoutHandle&&clearTimeout(this._addNodeTimeoutHandle),this._addNodeTimeoutHandle=void 0}},{kind:"method",key:"closeDialog",value:function(){this._unsubscribe(),this._inclusionStrategy=void 0,this._entryId=void 0,this._status=void 0,this._device=void 0,this._stages=void 0,this._error=void 0,(0,a.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"get",static:!0,key:"styles",value:function(){return[z.yu,z.Qx,s.iv`
        h3 {
          margin-top: 0;
        }

        .success {
          color: var(--success-color);
        }

        .warning {
          color: var(--warning-color);
        }

        .stages {
          margin-top: 16px;
          display: grid;
        }

        .flex-container .stage ha-svg-icon {
          width: 16px;
          height: 16px;
          margin-right: 0px;
        }
        .stage {
          padding: 8px;
        }

        .flex-container {
          display: flex;
          align-items: center;
        }

        .flex-column {
          display: flex;
          flex-direction: column;
        }

        .flex-column ha-formfield {
          padding: 8px 0;
        }

        .select-inclusion {
          display: flex;
          align-items: center;
        }

        .select-inclusion .outline:nth-child(2) {
          margin-left: 16px;
        }

        .select-inclusion .outline {
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          padding: 16px;
          min-height: 250px;
          text-align: center;
          flex: 1;
        }

        @media all and (max-width: 500px) {
          .select-inclusion {
            flex-direction: column;
          }

          .select-inclusion .outline:nth-child(2) {
            margin-left: 0;
            margin-top: 16px;
          }
        }

        ha-svg-icon {
          width: 68px;
          height: 48px;
        }
        ha-textfield {
          display: block;
        }
        .secondary {
          color: var(--secondary-text-color);
        }

        .flex-container ha-circular-progress,
        .flex-container ha-svg-icon {
          margin-right: 20px;
        }
      `]}}]}}),s.oi)}}]);