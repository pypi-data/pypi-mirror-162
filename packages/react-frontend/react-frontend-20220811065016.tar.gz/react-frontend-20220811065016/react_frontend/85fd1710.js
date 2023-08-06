(self.webpackChunkreact_frontend=self.webpackChunkreact_frontend||[]).push([[6465],{91893:(e,t,i)=>{var r={"./entity-settings-helper-tab":[24205,1985,3266,1291,8250,4205],"./entity-settings-helper-tab.ts":[24205,1985,3266,1291,8250,4205]};function n(e){if(!i.o(r,e))return Promise.resolve().then((()=>{var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=r[e],n=t[0];return Promise.all(t.slice(1).map(i.e)).then((()=>i(n)))}n.keys=()=>Object.keys(r),n.id=91893,e.exports=n},17267:(e,t,i)=>{"use strict";i.d(t,{h:()=>o});var r=i(37500),n=i(57835);const o=(0,n.XM)(class extends n.Xe{constructor(e){var t,i,r;if(super(e),r=void 0,(i="_element")in(t=this)?Object.defineProperty(t,i,{value:r,enumerable:!0,configurable:!0,writable:!0}):t[i]=r,e.type!==n.pX.CHILD)throw new Error("dynamicElementDirective can only be used in content bindings")}update(e,[t,i]){return this._element&&this._element.localName===t?(i&&Object.entries(i).forEach((([e,t])=>{this._element[e]=t})),r.Jb):this.render(t,i)}render(e,t){return this._element=document.createElement(e),t&&Object.entries(t).forEach((([e,t])=>{this._element[e]=t})),this._element}})},23860:(e,t,i)=>{"use strict";var r=i(68546),n=i(37500),o=i(59036),s=i(8636),a=i(18394);i(32678),i(37662);function l(){l=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!h(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return m(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?m(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=f(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:u(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=u(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function d(e){var t,i=f(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function c(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function h(e){return e.decorators&&e.decorators.length}function p(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function u(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function f(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function m(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}const y={info:r.EaN,warning:r.O8k,error:r._gM,success:r.F9P};!function(e,t,i,r){var n=l();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(p(o.descriptor)||p(n.descriptor)){if(h(o)||h(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(h(o)){if(h(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}c(o,n)}else t.push(o)}return t}(s.d.map(d)),e);n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("ha-alert")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)()],key:"title",value:()=>""},{kind:"field",decorators:[(0,o.Cb)({attribute:"alert-type"})],key:"alertType",value:()=>"info"},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"dismissable",value:()=>!1},{kind:"field",decorators:[(0,o.Cb)({type:Boolean})],key:"rtl",value:()=>!1},{kind:"method",key:"render",value:function(){return n.dy`
      <div
        class="issue-type ${(0,s.$)({rtl:this.rtl,[this.alertType]:!0})}"
        role="alert"
      >
        <div class="icon ${this.title?"":"no-title"}">
          <slot name="icon">
            <ha-svg-icon .path=${y[this.alertType]}></ha-svg-icon>
          </slot>
        </div>
        <div class="content">
          <div class="main-content">
            ${this.title?n.dy`<div class="title">${this.title}</div>`:""}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${this.dismissable?n.dy`<ha-icon-button
                    @click=${this._dismiss_clicked}
                    label="Dismiss alert"
                    .path=${r.r5M}
                  ></ha-icon-button>`:""}
            </slot>
          </div>
        </div>
      </div>
    `}},{kind:"method",key:"_dismiss_clicked",value:function(){(0,a.B)(this,"alert-dismissed-clicked")}},{kind:"field",static:!0,key:"styles",value:()=>n.iv`
    .issue-type {
      position: relative;
      padding: 8px;
      display: flex;
      margin: 4px 0;
    }
    .issue-type.rtl {
      flex-direction: row-reverse;
    }
    .issue-type::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: 4px;
    }
    .icon {
      z-index: 1;
    }
    .icon.no-title {
      align-self: center;
    }
    .issue-type.rtl > .content {
      flex-direction: row-reverse;
      text-align: right;
    }
    .content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
    }
    .action {
      z-index: 1;
      width: min-content;
      --mdc-theme-primary: var(--primary-text-color);
    }
    .main-content {
      overflow-wrap: anywhere;
      word-break: break-word;
      margin-left: 8px;
      margin-right: 0;
    }
    .issue-type.rtl > .content > .main-content {
      margin-left: 0;
      margin-right: 8px;
    }
    .title {
      margin-top: 2px;
      font-weight: bold;
    }
    .action mwc-button,
    .action ha-icon-button {
      --mdc-theme-primary: var(--primary-text-color);
      --mdc-icon-button-size: 36px;
    }
    .issue-type.info > .icon {
      color: var(--info-color);
    }
    .issue-type.info::after {
      background-color: var(--info-color);
    }

    .issue-type.warning > .icon {
      color: var(--warning-color);
    }
    .issue-type.warning::after {
      background-color: var(--warning-color);
    }

    .issue-type.error > .icon {
      color: var(--error-color);
    }
    .issue-type.error::after {
      background-color: var(--error-color);
    }

    .issue-type.success > .icon {
      color: var(--success-color);
    }
    .issue-type.success::after {
      background-color: var(--success-color);
    }
  `}]}}),n.oi)},2638:(e,t,i)=>{"use strict";var r=i(37500),n=i(59036),o=i(18394),s=i(34614);i(16591),i(20297);function a(){a=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!c(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return f(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?f(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=u(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:p(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=p(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function l(e){var t,i=u(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function d(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function c(e){return e.decorators&&e.decorators.length}function h(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function p(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function u(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function f(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}let m=[];const y=e=>r.dy`<mwc-list-item
  graphic="avatar"
>
  <ha-icon .icon=${e.icon} slot="graphic"></ha-icon>
  ${e.icon}
</mwc-list-item>`;!function(e,t,i,r){var n=a();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,p.elements)}),i),p=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(h(o.descriptor)||h(n.descriptor)){if(c(o)||c(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(c(o)){if(c(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}d(o,n)}else t.push(o)}return t}(s.d.map(l)),e);n.initializeClassElements(s.F,p.elements),n.runClassFinishers(s.F,p.finishers)}([(0,n.Mo)("ha-icon-picker")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,n.Cb)()],key:"hass",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"value",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"label",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"helper",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"placeholder",value:void 0},{kind:"field",decorators:[(0,n.Cb)()],key:"fallbackPath",value:void 0},{kind:"field",decorators:[(0,n.Cb)({attribute:"error-message"})],key:"errorMessage",value:void 0},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"disabled",value:()=>!1},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"required",value:()=>!1},{kind:"field",decorators:[(0,n.Cb)({type:Boolean})],key:"invalid",value:()=>!1},{kind:"field",decorators:[(0,n.SB)()],key:"_opened",value:()=>!1},{kind:"field",decorators:[(0,n.IO)("ha-combo-box",!0)],key:"comboBox",value:void 0},{kind:"method",key:"render",value:function(){return r.dy`
      <ha-combo-box
        .hass=${this.hass}
        item-value-path="icon"
        item-label-path="icon"
        .value=${this._value}
        allow-custom-value
        .filteredItems=${m}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .placeholder=${this.placeholder}
        .errorMessage=${this.errorMessage}
        .invalid=${this.invalid}
        .renderer=${y}
        icon
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
        @filter-changed=${this._filterChanged}
      >
        ${this._value||this.placeholder?r.dy`
              <ha-icon .icon=${this._value||this.placeholder} slot="icon">
              </ha-icon>
            `:this.fallbackPath?r.dy`<ha-svg-icon
              .path=${this.fallbackPath}
              slot="icon"
            ></ha-svg-icon>`:""}
      </ha-combo-box>
    `}},{kind:"method",key:"_openedChanged",value:async function(e){if(this._opened=e.detail.value,this._opened&&!m.length){const e=await i.e(3893).then(i.t.bind(i,63893,19));m=e.default.map((e=>({icon:`mdi:${e.name}`,keywords:e.keywords}))),this.comboBox.filteredItems=m,Object.keys(s.g).forEach((e=>{this._loadCustomIconItems(e)}))}}},{kind:"method",key:"_loadCustomIconItems",value:async function(e){try{const t=s.g[e].getIconList;if("function"!=typeof t)return;const i=(await t()).map((t=>{var i;return{icon:`${e}:${t.name}`,keywords:null!==(i=t.keywords)&&void 0!==i?i:[]}}));m.push(...i),this.comboBox.filteredItems=m}catch(t){console.warn(`Unable to load icon list for ${e} iconset`)}}},{kind:"method",key:"_valueChanged",value:function(e){e.stopPropagation(),this._setValue(e.detail.value)}},{kind:"method",key:"_setValue",value:function(e){this.value=e,(0,o.B)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}},{kind:"method",key:"_filterChanged",value:function(e){const t=e.detail.value.toLowerCase();if(t.length>=2){const e=[],i=[];m.forEach((r=>{r.icon.includes(t)?e.push(r):r.keywords.some((e=>e.includes(t)))&&i.push(r)})),e.push(...i),e.length>0?this.comboBox.filteredItems=e:this.comboBox.filteredItems=[{icon:t,keywords:[]}]}else this.comboBox.filteredItems=m}},{kind:"get",key:"_value",value:function(){return this.value||""}},{kind:"get",static:!0,key:"styles",value:function(){return r.iv`
      ha-icon,
      ha-svg-icon {
        color: var(--primary-text-color);
        position: relative;
        bottom: 2px;
      }
      *[slot="prefix"] {
        margin-right: 8px;
      }
    `}}]}}),r.oi)},19096:(e,t,i)=>{"use strict";var r=i(83684),n=i(44973),o=i(37500);function s(){s=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!d(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return u(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?u(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=p(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:h(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=h(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function a(e){var t,i=p(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function l(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function d(e){return e.decorators&&e.decorators.length}function c(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function h(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function p(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function u(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}!function(e,t,i,r){var n=s();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var h=t((function(e){n.initializeInstanceElements(e,p.elements)}),i),p=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(c(o.descriptor)||c(n.descriptor)){if(d(o)||d(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(d(o)){if(d(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}l(o,n)}else t.push(o)}return t}(h.d.map(a)),e);n.initializeClassElements(h.F,p.elements),n.runClassFinishers(h.F,p.finishers)}([(0,i(59036).Mo)("ha-radio")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",static:!0,key:"styles",value:()=>[n.W,o.iv`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `]}]}}),r.J)},71133:(e,t,i)=>{"use strict";var r=i(45285),n=i(3762),o=i(37500),s=i(59036),a=i(72218),l=i(2537);function d(){d=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!p(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return y(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?y(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=m(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:f(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=f(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function c(e){var t,i=m(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function h(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function p(e){return e.decorators&&e.decorators.length}function u(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function f(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function m(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function y(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function v(){return v="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=b(e,t);if(r){var n=Object.getOwnPropertyDescriptor(r,t);return n.get?n.get.call(arguments.length<3?e:i):n.value}},v.apply(this,arguments)}function b(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=g(e)););return e}function g(e){return g=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},g(e)}!function(e,t,i,r){var n=d();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(u(o.descriptor)||u(n.descriptor)){if(p(o)||p(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(p(o)){if(p(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}h(o,n)}else t.push(o)}return t}(s.d.map(c)),e);n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,s.Mo)("ha-select")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"field",decorators:[(0,s.Cb)({type:Boolean})],key:"icon",value:void 0},{kind:"method",key:"renderLeadingIcon",value:function(){return this.icon?o.dy`<span class="mdc-select__icon"
      ><slot name="icon"></slot
    ></span>`:o.Ld}},{kind:"method",key:"connectedCallback",value:function(){v(g(i.prototype),"connectedCallback",this).call(this),window.addEventListener("translations-updated",this._translationsUpdated)}},{kind:"method",key:"disconnectedCallback",value:function(){v(g(i.prototype),"disconnectedCallback",this).call(this),window.removeEventListener("translations-updated",this._translationsUpdated)}},{kind:"field",key:"_translationsUpdated",value(){return(0,a.D)((async()=>{await(0,l.y)(),this.layoutOptions()}),500)}},{kind:"field",static:!0,key:"styles",value:()=>[n.W,o.iv`
      .mdc-select:not(.mdc-select--disabled) .mdc-select__icon {
        color: var(--secondary-text-color);
      }
      .mdc-select__anchor {
        width: var(--ha-select-min-width, 200px);
      }
      .mdc-floating-label {
        inset-inline-start: 16px !important;
        inset-inline-end: initial !important;
        direction: var(--direction);
      }
    `]}]}}),r.K)},60470:(e,t,i)=>{"use strict";i.d(t,{iJ:()=>n,pB:()=>r});const r=(e,t)=>{const i=new URLSearchParams;return t&&(t.type&&i.append("type",t.type),t.domain&&i.append("domain",t.domain)),e.callApi("GET",`config/config_entries/entry?${i.toString()}`)},n=(e,t)=>e.callApi("DELETE",`config/config_entries/entry/${t}`)},15858:(e,t,i)=>{"use strict";i.d(t,{D7:()=>a,Ky:()=>o,WW:()=>l,XO:()=>s});var r=i(64346);const n={"HA-Frontend-Base":`${location.protocol}//${location.host}`},o=(e,t)=>{var i;return e.callApi("POST","config/config_entries/flow",{handler:t,show_advanced_options:Boolean(null===(i=e.userData)||void 0===i?void 0:i.showAdvanced)},n)},s=(e,t,i)=>e.callApi("POST",`config/config_entries/flow/${t}`,i,n),a=e=>e.sendMessagePromise({type:"config_entries/flow/progress"}),l=(e,t)=>t.context.title_placeholders&&0!==Object.keys(t.context.title_placeholders).length?e(`component.${t.handler}.config.flow_title`,t.context.title_placeholders)||("name"in t.context.title_placeholders?t.context.title_placeholders.name:(0,r.Lh)(e,t.handler)):(0,r.Lh)(e,t.handler)},64346:(e,t,i)=>{"use strict";i.d(t,{Lh:()=>r,t4:()=>n});const r=(e,t,i)=>e(`component.${t}.title`)||(null==i?void 0:i.name)||t,n=(e,t)=>e.callWS({type:"manifest/get",integration:t})},76465:(e,t,i)=>{"use strict";i.r(t),i.d(t,{DialogEntityEditor:()=>me});i(27303),i(22001);var r=i(68546),n=i(37500),o=i(59036),s=i(40015),a=i(17267),l=i(18394),d=i(2733),c=(i(9828),i(95469),i(32678),i(87545)),h=i(60470),p=i(51134),u=i(67846),f=i(49389);i(84323);function m(){m=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!b(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return _(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?_(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=w(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:k(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=k(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function y(e){var t,i=w(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function v(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function b(e){return e.decorators&&e.decorators.length}function g(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function k(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function w(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function _(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function E(){return E="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=$(e,t);if(r){var n=Object.getOwnPropertyDescriptor(r,t);return n.get?n.get.call(arguments.length<3?e:i):n.value}},E.apply(this,arguments)}function $(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=C(e)););return e}function C(e){return C=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},C(e)}!function(e,t,i,r){var n=m();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(g(o.descriptor)||g(n.descriptor)){if(b(o)||b(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(b(o)){if(b(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}v(o,n)}else t.push(o)}return t}(s.d.map(y)),e);n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("ha-related-items")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)()],key:"itemType",value:void 0},{kind:"field",decorators:[(0,o.Cb)()],key:"itemId",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_entries",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_devices",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_areas",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_related",value:void 0},{kind:"method",key:"hassSubscribe",value:function(){return[(0,p.q4)(this.hass.connection,(e=>{this._devices=e})),(0,c.sG)(this.hass.connection,(e=>{this._areas=e}))]}},{kind:"method",key:"firstUpdated",value:function(e){E(C(i.prototype),"firstUpdated",this).call(this,e),(0,h.pB)(this.hass).then((e=>{this._entries=e})),this.hass.loadBackendTranslation("title")}},{kind:"method",key:"updated",value:function(e){E(C(i.prototype),"updated",this).call(this,e),(e.has("itemId")||e.has("itemType"))&&this.itemId&&this.itemType&&this._findRelated()}},{kind:"method",key:"render",value:function(){return this._related?0===Object.keys(this._related).length?n.dy`
        ${this.hass.localize("ui.components.related-items.no_related_found")}
      `:n.dy`
      ${this._related.config_entry&&this._entries?this._related.config_entry.map((e=>{const t=this._entries.find((t=>t.entry_id===e));return t?n.dy`
              <h3>
                ${this.hass.localize("ui.components.related-items.integration")}:
              </h3>
              <a
                href=${`/config/integrations#config_entry=${e}`}
                @click=${this._navigateAwayClose}
              >
                ${this.hass.localize(`component.${t.domain}.title`)}:
                ${t.title}
              </a>
            `:""})):""}
      ${this._related.device&&this._devices?this._related.device.map((e=>{const t=this._devices.find((t=>t.id===e));return t?n.dy`
              <h3>
                ${this.hass.localize("ui.components.related-items.device")}:
              </h3>
              <a
                href="/config/devices/device/${e}"
                @click=${this._navigateAwayClose}
              >
                ${t.name_by_user||t.name}
              </a>
            `:""})):""}
      ${this._related.area&&this._areas?this._related.area.map((e=>{const t=this._areas.find((t=>t.area_id===e));return t?n.dy`
              <h3>
                ${this.hass.localize("ui.components.related-items.area")}:
              </h3>
              <a
                href="/config/areas/area/${e}"
                @click=${this._navigateAwayClose}
              >
                ${t.name}
              </a>
            `:""})):""}
      ${this._related.entity?n.dy`
            <h3>
              ${this.hass.localize("ui.components.related-items.entity")}:
            </h3>
            <ul>
              ${this._related.entity.map((e=>{const t=this.hass.states[e];return t?n.dy`
                  <li>
                    <button
                      @click=${this._openMoreInfo}
                      .entityId=${e}
                      class="link"
                    >
                      ${t.attributes.friendly_name||e}
                    </button>
                  </li>
                `:""}))}
            </ul>
          `:""}
      ${this._related.group?n.dy`
            <h3>${this.hass.localize("ui.components.related-items.group")}:</h3>
            <ul>
              ${this._related.group.map((e=>{const t=this.hass.states[e];return t?n.dy`
                  <li>
                    <button
                      class="link"
                      @click=${this._openMoreInfo}
                      .entityId=${e}
                    >
                      ${t.attributes.friendly_name||t.entity_id}
                    </button>
                  </li>
                `:""}))}
            </ul>
          `:""}
      ${this._related.scene?n.dy`
            <h3>${this.hass.localize("ui.components.related-items.scene")}:</h3>
            <ul>
              ${this._related.scene.map((e=>{const t=this.hass.states[e];return t?n.dy`
                  <li>
                    <button
                      class="link"
                      @click=${this._openMoreInfo}
                      .entityId=${e}
                    >
                      ${t.attributes.friendly_name||t.entity_id}
                    </button>
                  </li>
                `:""}))}
            </ul>
          `:""}
      ${this._related.automation?n.dy`
            <h3>
              ${this.hass.localize("ui.components.related-items.automation")}:
            </h3>
            <ul>
              ${this._related.automation.map((e=>{const t=this.hass.states[e];return t?n.dy`
                  <li>
                    <button
                      class="link"
                      @click=${this._openMoreInfo}
                      .entityId=${e}
                    >
                      ${t.attributes.friendly_name||t.entity_id}
                    </button>
                  </li>
                `:""}))}
            </ul>
          `:""}
      ${this._related.script?n.dy`
            <h3>
              ${this.hass.localize("ui.components.related-items.script")}:
            </h3>
            <ul>
              ${this._related.script.map((e=>{const t=this.hass.states[e];return t?n.dy`
                  <li>
                    <button
                      class="link"
                      @click=${this._openMoreInfo}
                      .entityId=${e}
                    >
                      ${t.attributes.friendly_name||t.entity_id}
                    </button>
                  </li>
                `:""}))}
            </ul>
          `:""}
    `:n.dy``}},{kind:"method",key:"_navigateAwayClose",value:async function(){await new Promise((e=>setTimeout(e,0))),(0,l.B)(this,"close-dialog")}},{kind:"method",key:"_findRelated",value:async function(){this._related=await(0,u.K)(this.hass,this.itemType,this.itemId),await this.updateComplete,(0,l.B)(this,"iron-resize")}},{kind:"method",key:"_openMoreInfo",value:function(e){const t=e.target.entityId;(0,l.B)(this,"hass-more-info",{entityId:t})}},{kind:"get",static:!0,key:"styles",value:function(){return n.iv`
      a {
        color: var(--primary-color);
      }
      button.link {
        color: var(--primary-color);
        text-align: left;
        cursor: pointer;
        background: none;
        border-width: initial;
        border-style: none;
        border-color: initial;
        border-image: initial;
        padding: 0px;
        font: inherit;
        text-decoration: underline;
      }
      h3 {
        font-family: var(--paper-font-title_-_font-family);
        -webkit-font-smoothing: var(
          --paper-font-title_-_-webkit-font-smoothing
        );
        font-size: var(--paper-font-title_-_font-size);
        font-weight: var(--paper-font-headline-_font-weight);
        letter-spacing: var(--paper-font-title_-_letter-spacing);
        line-height: var(--paper-font-title_-_line-height);
        opacity: var(--dark-primary-opacity);
      }
    `}}]}}),(0,f.f)(n.oi));var P=i(26038),x=i(15815),D=i(29950),S=i(84728);const A={input_number:"entity-settings-helper-tab",input_select:"entity-settings-helper-tab",input_text:"entity-settings-helper-tab",input_boolean:"entity-settings-helper-tab",input_datetime:"entity-settings-helper-tab",counter:"entity-settings-helper-tab",timer:"entity-settings-helper-tab",input_button:"entity-settings-helper-tab"};i(51187),i(1819),i(44577);var z=i(14516),T=i(86089),O=i(36655),I=i(98228),B=i(28858),j=(i(23860),i(25718),i(31360),i(2638),i(19096),i(71133),i(51520),i(15858)),F=i(64346);const M=(e,t)=>{var i;return e.callApi("POST","config/config_entries/options/flow",{handler:t,show_advanced_options:Boolean(null===(i=e.userData)||void 0===i?void 0:i.showAdvanced)})},R=(e,t)=>e.callApi("GET",`config/config_entries/options/flow/${t}`),L=(e,t,i)=>e.callApi("POST",`config/config_entries/options/flow/${t}`,i),U=(e,t)=>e.callApi("DELETE",`config/config_entries/options/flow/${t}`),N=()=>Promise.all([i.e(1985),i.e(3266),i.e(1922),i.e(1291),i.e(8250),i.e(5938)]).then(i.bind(i,5938)),q=(e,t,i)=>((e,t,i)=>{(0,l.B)(e,"show-dialog",{dialogTag:"dialog-data-entry-flow",dialogImport:N,dialogParams:{...t,flowConfig:i}})})(e,{startFlowHandler:t.entry_id,domain:t.domain,manifest:i},{loadDevicesAndAreas:!1,createFlow:async(e,i)=>{const[r]=await Promise.all([M(e,i),e.loadBackendTranslation("options",t.domain)]);return r},fetchFlow:async(e,i)=>{const[r]=await Promise.all([R(e,i),e.loadBackendTranslation("options",t.domain)]);return r},handleFlowStep:L,deleteFlow:U,renderAbortDescription(e,i){const r=e.localize(`component.${t.domain}.options.abort.${i.reason}`,i.description_placeholders);return r?n.dy`
              <ha-markdown
                breaks
                allowsvg
                .content=${r}
              ></ha-markdown>
            `:""},renderShowFormStepHeader:(e,i)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.title`)||e.localize("ui.dialogs.options_flow.form.header"),renderShowFormStepDescription(e,i){const r=e.localize(`component.${t.domain}.options.step.${i.step_id}.description`,i.description_placeholders);return r?n.dy`
              <ha-markdown
                allowsvg
                breaks
                .content=${r}
              ></ha-markdown>
            `:""},renderShowFormStepFieldLabel:(e,i,r)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.data.${r.name}`),renderShowFormStepFieldHelper:(e,i,r)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.data_description.${r.name}`),renderShowFormStepFieldError:(e,i,r)=>e.localize(`component.${t.domain}.options.error.${r}`,i.description_placeholders),renderExternalStepHeader:(e,t)=>"",renderExternalStepDescription:(e,t)=>"",renderCreateEntryDescription:(e,t)=>n.dy`
          <p>${e.localize("ui.dialogs.options_flow.success.description")}</p>
        `,renderShowFormProgressHeader:(e,i)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.title`)||e.localize(`component.${t.domain}.title`),renderShowFormProgressDescription(e,i){const r=e.localize(`component.${t.domain}.options.progress.${i.progress_action}`,i.description_placeholders);return r?n.dy`
              <ha-markdown
                allowsvg
                breaks
                .content=${r}
              ></ha-markdown>
            `:""},renderMenuHeader:(e,i)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.title`)||e.localize(`component.${t.domain}.title`),renderMenuDescription(e,i){const r=e.localize(`component.${t.domain}.options.step.${i.step_id}.description`,i.description_placeholders);return r?n.dy`
              <ha-markdown
                allowsvg
                breaks
                .content=${r}
              ></ha-markdown>
            `:""},renderMenuOption:(e,i,r)=>e.localize(`component.${t.domain}.options.step.${i.step_id}.menu_options.${r}`,i.description_placeholders),renderLoadingDescription:(e,i)=>e.localize(`component.${t.domain}.options.loading`)||e.localize(`ui.dialogs.options_flow.loading.${i}`,{integration:(0,F.Lh)(e.localize,t.domain)})});var H=i(11285);const W=()=>i.e(5690).then(i.bind(i,55690));var K=i(28658);function X(){X=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!V(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return ee(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?ee(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=Q(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:Z(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=Z(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function J(e){var t,i=Q(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function G(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function V(e){return e.decorators&&e.decorators.length}function Y(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function Z(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function Q(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function ee(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function te(){return te="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=ie(e,t);if(r){var n=Object.getOwnPropertyDescriptor(r,t);return n.get?n.get.call(arguments.length<3?e:i):n.value}},te.apply(this,arguments)}function ie(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=re(e)););return e}function re(e){return re=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},re(e)}const ne={cover:[["awning","blind","curtain","damper","door","garage","gate","shade","shutter","window"]],binary_sensor:[["lock"],["window","door","garage_door","opening"],["battery","battery_charging"],["cold","gas","heat"],["running","motion","moving","occupancy","presence","vibration"],["power","plug","light"],["smoke","safety","sound","problem","tamper","carbon_monoxide","moisture"]]},oe={temperature:["°C","°F","K"],pressure:["hPa","Pa","kPa","bar","cbar","mbar","mmHg","inHg","psi"]},se=["cover","fan","light","lock","siren"];!function(e,t,i,r){var n=X();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(Y(o.descriptor)||Y(n.descriptor)){if(V(o)||V(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(V(o)){if(V(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}G(o,n)}else t.push(o)}return t}(s.d.map(J)),e);n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("entity-registry-settings")],(function(e,t){class i extends t{constructor(...t){super(...t),e(this)}}return{F:i,d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.Cb)()],key:"entry",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_name",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_icon",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_entityId",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_deviceClass",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_switchAs",value:()=>"switch"},{kind:"field",decorators:[(0,o.SB)()],key:"_areaId",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_disabledBy",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_hiddenBy",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_device",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_helperConfigEntry",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_unit_of_measurement",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_error",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_submitting",value:void 0},{kind:"field",key:"_origEntityId",value:void 0},{kind:"field",key:"_deviceLookup",value:void 0},{kind:"field",key:"_deviceClassOptions",value:void 0},{kind:"method",key:"hassSubscribe",value:function(){return[(0,p.q4)(this.hass.connection,(e=>{this._deviceLookup={};for(const t of e)this._deviceLookup[t.id]=t;this.entry.device_id&&(this._device=this._deviceLookup[this.entry.device_id])}))]}},{kind:"method",key:"firstUpdated",value:function(e){te(re(i.prototype),"firstUpdated",this).call(this,e),this.entry.config_entry_id&&(0,h.pB)(this.hass,{type:"helper",domain:this.entry.platform}).then((e=>{this._helperConfigEntry=e.find((e=>e.entry_id===this.entry.config_entry_id))}))}},{kind:"method",key:"willUpdate",value:function(e){if(te(re(i.prototype),"willUpdate",this).call(this,e),!e.has("entry"))return;this._error=void 0,this._name=this.entry.name||"",this._icon=this.entry.icon||"",this._deviceClass=this.entry.device_class||this.entry.original_device_class,this._origEntityId=this.entry.entity_id,this._areaId=this.entry.area_id,this._entityId=this.entry.entity_id,this._disabledBy=this.entry.disabled_by,this._hiddenBy=this.entry.hidden_by,this._device=this.entry.device_id&&this._deviceLookup?this._deviceLookup[this.entry.device_id]:void 0;const t=(0,O.M)(this.entry.entity_id);if("sensor"===t){var r;const e=this.hass.states[this.entry.entity_id];this._unit_of_measurement=null==e||null===(r=e.attributes)||void 0===r?void 0:r.unit_of_measurement}const n=ne[t];if(n){this._deviceClassOptions=[[],[]];for(const e of n)e.includes(this.entry.original_device_class)?this._deviceClassOptions[0]=e:this._deviceClassOptions[1].push(...e)}}},{kind:"method",key:"render",value:function(){var e,t,i,r,o,s;if(this.entry.entity_id!==this._origEntityId)return n.dy``;const a=this.hass.states[this.entry.entity_id],l=(0,O.M)(this.entry.entity_id),d=(0,O.M)(this._entityId.trim())!==l;return n.dy`
      ${a?"":n.dy`
            <div class="container warning">
              ${this.hass.localize("ui.dialogs.entity_registry.editor.unavailable")}
              ${null!==(e=this._device)&&void 0!==e&&e.disabled_by?n.dy`<br />${this.hass.localize("ui.dialogs.entity_registry.editor.device_disabled")}<br /><mwc-button @click=${this._openDeviceSettings}>
                      ${this.hass.localize("ui.dialogs.entity_registry.editor.open_device_settings")}
                    </mwc-button>`:""}
            </div>
          `}
      ${this._error?n.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:""}
      <div class="form container">
        <ha-textfield
          .value=${this._name}
          .label=${this.hass.localize("ui.dialogs.entity_registry.editor.name")}
          .invalid=${d}
          .disabled=${this._submitting}
          .placeholder=${this.entry.original_name}
          @input=${this._nameChanged}
        ></ha-textfield>
        <ha-icon-picker
          .value=${this._icon}
          @value-changed=${this._iconChanged}
          .label=${this.hass.localize("ui.dialogs.entity_registry.editor.icon")}
          .placeholder=${this.entry.original_icon||(null==a?void 0:a.attributes.icon)}
          .fallbackPath=${this._icon||null!=a&&a.attributes.icon||!a?void 0:(0,I.K)((0,O.M)(a.entity_id),a)}
          .disabled=${this._submitting}
        ></ha-icon-picker>
        ${this._deviceClassOptions?n.dy`
              <ha-select
                .label=${this.hass.localize("ui.dialogs.entity_registry.editor.device_class")}
                .value=${this._deviceClass}
                naturalMenuWidth
                fixedMenuPosition
                @selected=${this._deviceClassChanged}
                @closed=${T.U}
              >
                <mwc-list-item></mwc-list-item>
                ${this._deviceClassesSorted(l,this._deviceClassOptions[0],this.hass.localize).map((e=>n.dy`
                    <mwc-list-item .value=${e.deviceClass}>
                      ${e.label}
                    </mwc-list-item>
                  `))}
                ${this._deviceClassOptions[0].length&&this._deviceClassOptions[1].length?n.dy`<li divider role="separator"></li>`:""}
                ${this._deviceClassesSorted(l,this._deviceClassOptions[1],this.hass.localize).map((e=>n.dy`
                    <mwc-list-item .value=${e.deviceClass}>
                      ${e.label}
                    </mwc-list-item>
                  `))}
              </ha-select>
            `:""}
        ${this._deviceClass&&null!=a&&a.attributes.unit_of_measurement&&null!==(t=oe[this._deviceClass])&&void 0!==t&&t.includes(null==a?void 0:a.attributes.unit_of_measurement)?n.dy`
              <ha-select
                .label=${this.hass.localize("ui.dialogs.entity_registry.editor.unit_of_measurement")}
                .value=${a.attributes.unit_of_measurement}
                naturalMenuWidth
                fixedMenuPosition
                @selected=${this._unitChanged}
                @closed=${T.U}
              >
                ${oe[this._deviceClass].map((e=>n.dy`
                    <mwc-list-item .value=${e}>${e}</mwc-list-item>
                  `))}
              </ha-select>
            `:""}
        ${"switch"===l?n.dy`<ha-select
              .label=${this.hass.localize("ui.dialogs.entity_registry.editor.device_class")}
              naturalMenuWidth
              fixedMenuPosition
              @selected=${this._switchAsChanged}
              @closed=${T.U}
            >
              <mwc-list-item value="switch" selected>
                ${(0,F.Lh)(this.hass.localize,"switch")}</mwc-list-item
              >
              <li divider role="separator"></li>
              ${this._switchAsDomainsSorted(se,this.hass.localize).map((e=>n.dy`
                  <mwc-list-item .value=${e.domain}>
                    ${e.label}
                  </mwc-list-item>
                `))}
            </ha-select>`:""}
        ${this._helperConfigEntry?n.dy`
              <div class="row">
                <mwc-button
                  @click=${this._showOptionsFlow}
                  .disabled=${this._submitting}
                >
                  ${this.hass.localize("ui.dialogs.entity_registry.editor.configure_state","integration",(0,F.Lh)(this.hass.localize,this._helperConfigEntry.domain))}
                </mwc-button>
              </div>
            `:""}
        <ha-textfield
          error-message="Domain needs to stay the same"
          .value=${this._entityId}
          .label=${this.hass.localize("ui.dialogs.entity_registry.editor.entity_id")}
          .invalid=${d}
          .disabled=${this._submitting}
          @input=${this._entityIdChanged}
        ></ha-textfield>
        ${this.entry.device_id?"":n.dy`<ha-area-picker
              .hass=${this.hass}
              .value=${this._areaId}
              @value-changed=${this._areaPicked}
            ></ha-area-picker>`}

        <ha-expansion-panel
          .header=${this.hass.localize("ui.dialogs.entity_registry.editor.advanced")}
          outlined
        >
          <div class="label">
            ${this.hass.localize("ui.dialogs.entity_registry.editor.entity_status")}:
          </div>
          <div class="secondary">
            ${this._disabledBy&&"user"!==this._disabledBy&&"integration"!==this._disabledBy?this.hass.localize("ui.dialogs.entity_registry.editor.enabled_cause","cause",this.hass.localize(`config_entry.disabled_by.${this._disabledBy}`)):""}
          </div>
          <div class="row">
            <mwc-formfield
              .label=${this.hass.localize("ui.dialogs.entity_registry.editor.enabled_label")}
            >
              <ha-radio
                name="hiddendisabled"
                value="enabled"
                .checked=${!this._hiddenBy&&!this._disabledBy}
                .disabled=${this._hiddenBy&&"user"!==this._hiddenBy||(null===(i=this._device)||void 0===i?void 0:i.disabled_by)||this._disabledBy&&"user"!==this._disabledBy&&"integration"!==this._disabledBy}
                @change=${this._viewStatusChanged}
              ></ha-radio>
            </mwc-formfield>
            <mwc-formfield
              .label=${this.hass.localize("ui.dialogs.entity_registry.editor.hidden_label")}
            >
              <ha-radio
                name="hiddendisabled"
                value="hidden"
                .checked=${null!==this._hiddenBy}
                .disabled=${this._hiddenBy&&"user"!==this._hiddenBy||Boolean(null===(r=this._device)||void 0===r?void 0:r.disabled_by)||this._disabledBy&&"user"!==this._disabledBy&&"integration"!==this._disabledBy}
                @change=${this._viewStatusChanged}
              ></ha-radio>
            </mwc-formfield>
            <mwc-formfield
              .label=${this.hass.localize("ui.dialogs.entity_registry.editor.disabled_label")}
            >
              <ha-radio
                name="hiddendisabled"
                value="disabled"
                .checked=${null!==this._disabledBy}
                .disabled=${this._hiddenBy&&"user"!==this._hiddenBy||Boolean(null===(o=this._device)||void 0===o?void 0:o.disabled_by)||this._disabledBy&&"user"!==this._disabledBy&&"integration"!==this._disabledBy}
                @change=${this._viewStatusChanged}
              ></ha-radio>
            </mwc-formfield>
          </div>

          ${null!==this._disabledBy?n.dy`
                <div class="secondary">
                  ${this.hass.localize("ui.dialogs.entity_registry.editor.enabled_description")}
                </div>
              `:null!==this._hiddenBy?n.dy`
                <div class="secondary">
                  ${this.hass.localize("ui.dialogs.entity_registry.editor.hidden_description")}
                </div>
              `:""}
          ${this.entry.device_id?n.dy`
                <div class="label">
                  ${this.hass.localize("ui.dialogs.entity_registry.editor.change_area")}:
                </div>
                <ha-area-picker
                  .hass=${this.hass}
                  .value=${this._areaId}
                  .placeholder=${null===(s=this._device)||void 0===s?void 0:s.area_id}
                  .label=${this.hass.localize("ui.dialogs.entity_registry.editor.area")}
                  @value-changed=${this._areaPicked}
                ></ha-area-picker>
                <div class="secondary">
                  ${this.hass.localize("ui.dialogs.entity_registry.editor.area_note")}
                  ${this._device?n.dy`
                        <button class="link" @click=${this._openDeviceSettings}>
                          ${this.hass.localize("ui.dialogs.entity_registry.editor.change_device_area")}
                        </button>
                      `:""}
                </div>
              `:""}
        </ha-expansion-panel>
      </div>
      <div class="buttons">
        <mwc-button
          class="warning"
          @click=${this._confirmDeleteEntry}
          .disabled=${this._submitting||!this._helperConfigEntry&&!(null!=a&&a.attributes.restored)}
        >
          ${this.hass.localize("ui.dialogs.entity_registry.editor.delete")}
        </mwc-button>
        <mwc-button
          @click=${this._updateEntry}
          .disabled=${d||this._submitting}
        >
          ${this.hass.localize("ui.dialogs.entity_registry.editor.update")}
        </mwc-button>
      </div>
    `}},{kind:"method",key:"_nameChanged",value:function(e){this._error=void 0,this._name=e.target.value}},{kind:"method",key:"_iconChanged",value:function(e){this._error=void 0,this._icon=e.detail.value}},{kind:"method",key:"_entityIdChanged",value:function(e){this._error=void 0,this._entityId=e.target.value}},{kind:"method",key:"_deviceClassChanged",value:function(e){this._error=void 0,this._deviceClass=e.target.value}},{kind:"method",key:"_unitChanged",value:function(e){this._error=void 0,this._unit_of_measurement=e.target.value}},{kind:"method",key:"_switchAsChanged",value:function(e){""!==e.target.value&&(this._switchAs=e.target.value)}},{kind:"method",key:"_areaPicked",value:function(e){this._error=void 0,this._areaId=e.detail.value}},{kind:"method",key:"_viewStatusChanged",value:function(e){switch(e.target.value){case"enabled":this._disabledBy=null,this._hiddenBy=null;break;case"disabled":this._disabledBy="user",this._hiddenBy=null;break;case"hidden":this._hiddenBy="user",this._disabledBy=null}}},{kind:"method",key:"_openDeviceSettings",value:function(){var e,t;e=this,t={device:this._device,updateEntry:async e=>{await(0,p.t1)(this.hass,this._device.id,e)}},(0,l.B)(e,"show-dialog",{dialogTag:"dialog-device-registry-detail",dialogImport:W,dialogParams:t})}},{kind:"method",key:"_updateEntry",value:async function(){var e;this._submitting=!0;const t=this.getRootNode().host,i={name:this._name.trim()||null,icon:this._icon.trim()||null,area_id:this._areaId||null,device_class:this._deviceClass||null,new_entity_id:this._entityId.trim()},r=this.hass.states[this.entry.entity_id],n=(0,O.M)(this.entry.entity_id);this.entry.disabled_by===this._disabledBy||null!==this._disabledBy&&"user"!==this._disabledBy||(i.disabled_by=this._disabledBy),this.entry.hidden_by===this._hiddenBy||null!==this._hiddenBy&&"user"!==this._hiddenBy||(i.hidden_by=this._hiddenBy),"sensor"===n&&(null==r||null===(e=r.attributes)||void 0===e?void 0:e.unit_of_measurement)!==this._unit_of_measurement&&(i.options_domain="sensor",i.options={unit_of_measurement:this._unit_of_measurement});try{const e=await(0,P.Nv)(this.hass,this._origEntityId,i);e.require_restart&&(0,H.Ys)(this,{text:this.hass.localize("ui.dialogs.entity_registry.editor.enabled_restart_confirm")}),e.reload_delay&&(0,H.Ys)(this,{text:this.hass.localize("ui.dialogs.entity_registry.editor.enabled_delay_confirm","delay",e.reload_delay)}),(0,l.B)(this,"close-dialog")}catch(e){this._error=e.message||"Unknown error"}finally{this._submitting=!1}if("switch"!==this._switchAs){var o;if(!await(0,H.g7)(this,{text:this.hass.localize("ui.dialogs.entity_registry.editor.switch_as_x_confirm","domain",this._switchAs)}))return;const e=await(0,j.Ky)(this.hass,"switch_as_x"),i=await(0,j.XO)(this.hass,e.flow_id,{entity_id:this._entityId.trim(),target_domain:this._switchAs});if(null===(o=i.result)||void 0===o||!o.entry_id)return;const r=await this.hass.connection.subscribeEvents((()=>{r(),(0,P.hg)(this.hass.connection).then((e=>{const r=e.find((e=>e.config_entry_id===i.result.entry_id));r&&(0,K.R)(t,{entity_id:r.entity_id})}))}),"entity_registry_updated")}}},{kind:"method",key:"_confirmDeleteEntry",value:async function(){if(await(0,H.g7)(this,{text:this.hass.localize("ui.dialogs.entity_registry.editor.confirm_delete")})){this._submitting=!0;try{this._helperConfigEntry?await(0,h.iJ)(this.hass,this._helperConfigEntry.entry_id):await(0,P.z3)(this.hass,this._origEntityId),(0,l.B)(this,"close-dialog")}finally{this._submitting=!1}}}},{kind:"method",key:"_showOptionsFlow",value:async function(){q(this,this._helperConfigEntry,null)}},{kind:"field",key:"_switchAsDomainsSorted",value:()=>(0,z.Z)(((e,t)=>e.map((e=>({domain:e,label:(0,F.Lh)(t,e)}))).sort(((e,t)=>(0,B.$)(e.label,t.label)))))},{kind:"field",key:"_deviceClassesSorted",value:()=>(0,z.Z)(((e,t,i)=>t.map((t=>({deviceClass:t,label:i(`ui.dialogs.entity_registry.editor.device_classes.${e}.${t}`)}))).sort(((e,t)=>(0,B.$)(e.label,t.label)))))},{kind:"get",static:!0,key:"styles",value:function(){return[D.Qx,n.iv`
        :host {
          display: block;
        }
        .container {
          padding: 20px 24px;
        }
        .form {
          margin-bottom: 53px;
        }
        .buttons {
          position: absolute;
          bottom: 0;
          width: 100%;
          box-sizing: border-box;
          border-top: 1px solid
            var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
          display: flex;
          justify-content: space-between;
          padding: 8px;
          padding-bottom: max(env(safe-area-inset-bottom), 8px);
          background-color: var(--mdc-theme-surface, #fff);
        }
        ha-select {
          width: 100%;
          margin: 8px 0;
        }
        ha-switch {
          margin-right: 16px;
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
        ha-area-picker {
          margin: 8px 0;
          display: block;
        }
        .row {
          margin: 8px 0;
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
        }
        .label {
          margin-top: 16px;
        }
        .secondary {
          margin: 8px 0;
          width: 340px;
        }
        li[divider] {
          border-bottom-color: var(--divider-color);
        }
      `]}}]}}),(0,f.f)(n.oi));function ae(){ae=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var o="static"===n?e:i;this.defineClassElement(o,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!ce(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var o=this.decorateConstructor(i,t);return r.push.apply(r,o.finishers),o.finishers=r,o},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,o=n.length-1;o>=0;o--){var s=t[e.placement];s.splice(s.indexOf(e.key),1);var a=this.fromElementDescriptor(e),l=this.toElementFinisherExtras((0,n[o])(a)||a);e=l.element,this.addElementPlacement(e,t),l.finisher&&r.push(l.finisher);var d=l.extras;if(d){for(var c=0;c<d.length;c++)this.addElementPlacement(d[c],t);i.push.apply(i,d)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),o=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==o.finisher&&i.push(o.finisher),void 0!==o.elements){e=o.elements;for(var s=0;s<e.length-1;s++)for(var a=s+1;a<e.length;a++)if(e[s].key===e[a].key&&e[s].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[s].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return fe(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?fe(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=ue(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var o={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),o.initializer=e.initializer),o},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:pe(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=pe(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function le(e){var t,i=ue(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function de(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function ce(e){return e.decorators&&e.decorators.length}function he(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function pe(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function ue(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function fe(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}let me=function(e,t,i,r){var n=ae();if(r)for(var o=0;o<r.length;o++)n=r[o](n);var s=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===o.key&&e.placement===o.placement},r=0;r<e.length;r++){var n,o=e[r];if("method"===o.kind&&(n=t.find(i)))if(he(o.descriptor)||he(n.descriptor)){if(ce(o)||ce(n))throw new ReferenceError("Duplicated methods ("+o.key+") can't be decorated.");n.descriptor=o.descriptor}else{if(ce(o)){if(ce(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+o.key+").");n.decorators=o.decorators}de(o,n)}else t.push(o)}return t}(s.d.map(le)),e);return n.initializeClassElements(s.F,a.elements),n.runClassFinishers(s.F,a.finishers)}([(0,o.Mo)("dialog-entity-editor")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,o.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_params",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_entry",value:void 0},{kind:"field",decorators:[(0,o.SB)()],key:"_curTab",value:()=>"tab-settings"},{kind:"field",decorators:[(0,o.SB)()],key:"_extraTabs",value:()=>({})},{kind:"field",decorators:[(0,o.SB)()],key:"_settingsElementTag",value:void 0},{kind:"field",key:"_curTabIndex",value:()=>0},{kind:"method",key:"showDialog",value:function(e){this._params=e,this._entry=void 0,this._settingsElementTag=void 0,this._extraTabs={},this._getEntityReg()}},{kind:"method",key:"closeDialog",value:function(){this._params=void 0,(0,l.B)(this,"dialog-closed",{dialog:this.localName})}},{kind:"method",key:"render",value:function(){if(!this._params||void 0===this._entry)return n.dy``;const e=this._params.entity_id,t=this._entry,i=this.hass.states[e];return n.dy`
      <ha-dialog
        open
        .heading=${i?(0,d.C)(i):(null==t?void 0:t.name)||e}
        hideActions
        @closed=${this.closeDialog}
        @close-dialog=${this.closeDialog}
      >
        <div slot="heading">
          <ha-header-bar>
            <ha-icon-button
              slot="navigationIcon"
              .label=${this.hass.localize("ui.dialogs.entity_registry.dismiss")}
              .path=${r.r5M}
              dialogAction="cancel"
            ></ha-icon-button>
            <span slot="title">
              ${i?(0,d.C)(i):(null==t?void 0:t.name)||e}
            </span>
            ${i?n.dy`
                  <ha-icon-button
                    slot="actionItems"
                    .label=${this.hass.localize("ui.dialogs.entity_registry.control")}
                    .path=${r.S3d}
                    @click=${this._openMoreInfo}
                  ></ha-icon-button>
                `:""}
          </ha-header-bar>
          <mwc-tab-bar
            .activeIndex=${this._curTabIndex}
            @MDCTabBar:activated=${this._handleTabActivated}
            @MDCTab:interacted=${this._handleTabInteracted}
          >
            <mwc-tab
              id="tab-settings"
              .label=${this.hass.localize("ui.dialogs.entity_registry.settings")}
              dialogInitialFocus
            >
            </mwc-tab>
            ${Object.entries(this._extraTabs).map((([e,t])=>n.dy`
                <mwc-tab
                  id=${e}
                  .label=${this.hass.localize(t.translationKey)||e}
                >
                </mwc-tab>
              `))}
            <mwc-tab
              id="tab-related"
              .label=${this.hass.localize("ui.dialogs.entity_registry.related")}
            >
            </mwc-tab>
          </mwc-tab-bar>
        </div>
        <div class="wrapper">${(0,s.F)(this._renderTab())}</div>
      </ha-dialog>
    `}},{kind:"method",key:"_renderTab",value:function(){switch(this._curTab){case"tab-settings":return this._entry?this._settingsElementTag?n.dy`
              ${(0,a.h)(this._settingsElementTag,{hass:this.hass,entry:this._entry,entityId:this._params.entity_id})}
            `:n.dy``:n.dy`
          <div class="content">
            ${this.hass.localize("ui.dialogs.entity_registry.no_unique_id","entity_id",this._params.entity_id,"faq_link",n.dy`<a
                href=${(0,S.R)(this.hass,"/faq/unique_id")}
                target="_blank"
                rel="noreferrer"
                >${this.hass.localize("ui.dialogs.entity_registry.faq")}</a
              >`)}
          </div>
        `;case"tab-related":return n.dy`
          <ha-related-items
            class="content"
            .hass=${this.hass}
            .itemId=${this._params.entity_id}
            itemType="entity"
          ></ha-related-items>
        `;default:return n.dy``}}},{kind:"method",key:"_getEntityReg",value:async function(){try{this._entry=await(0,P.L3)(this.hass,this._params.entity_id),this._loadPlatformSettingTabs()}catch{this._entry=null}}},{kind:"method",key:"_handleTabActivated",value:function(e){this._curTabIndex=e.detail.index}},{kind:"method",key:"_handleTabInteracted",value:function(e){this._curTab=e.detail.tabId}},{kind:"method",key:"_loadPlatformSettingTabs",value:async function(){if(!this._entry)return;if(!Object.keys(A).includes(this._entry.platform))return void(this._settingsElementTag="entity-registry-settings");const e=A[this._entry.platform];await i(91893)(`./${e}`),this._settingsElementTag=e}},{kind:"method",key:"_openMoreInfo",value:function(){(0,x.ku)(this),(0,l.B)(this,"hass-more-info",{entityId:this._params.entity_id}),this.closeDialog()}},{kind:"get",static:!0,key:"styles",value:function(){return[D.yu,n.iv`
        ha-header-bar {
          --mdc-theme-on-primary: var(--primary-text-color);
          --mdc-theme-primary: var(--mdc-theme-surface);
          flex-shrink: 0;
        }

        mwc-tab-bar {
          border-bottom: 1px solid
            var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
        }

        ha-dialog {
          --dialog-content-position: static;
          --dialog-content-padding: 0;
          --dialog-z-index: 6;
        }

        @media all and (min-width: 451px) and (min-height: 501px) {
          .wrapper {
            min-width: 400px;
          }
        }

        .content {
          display: block;
          padding: 20px 24px;
        }

        /* overrule the ha-style-dialog max-height on small screens */
        @media all and (max-width: 450px), all and (max-height: 500px) {
          ha-header-bar {
            --mdc-theme-primary: var(--app-header-background-color);
            --mdc-theme-on-primary: var(--app-header-text-color, white);
          }
        }

        mwc-button.warning {
          --mdc-theme-primary: var(--error-color);
        }

        :host([rtl]) app-toolbar {
          direction: rtl;
          text-align: right;
        }
      `]}}]}}),n.oi)},84728:(e,t,i)=>{"use strict";i.d(t,{R:()=>r});const r=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`}}]);