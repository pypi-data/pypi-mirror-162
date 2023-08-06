"use strict";(self.webpackChunkreact_frontend=self.webpackChunkreact_frontend||[]).push([[7853],{89833:(e,t,r)=>{r.d(t,{O:()=>h});var n=r(87480),i=r(86251),o=r(37500),s=r(59036),a=r(8636),c=r(51346),d=r(71260);const l={fromAttribute:e=>null!==e&&(""===e||e),toAttribute:e=>"boolean"==typeof e?e?"":null:e};class h extends i.P{constructor(){super(...arguments),this.rows=2,this.cols=20,this.charCounter=!1}render(){const e=this.charCounter&&-1!==this.maxLength,t=e&&"internal"===this.charCounter,r=e&&!t,n=!!this.helper||!!this.validationMessage||r,i={"mdc-text-field--disabled":this.disabled,"mdc-text-field--no-label":!this.label,"mdc-text-field--filled":!this.outlined,"mdc-text-field--outlined":this.outlined,"mdc-text-field--end-aligned":this.endAligned,"mdc-text-field--with-internal-counter":t};return o.dy`
      <label class="mdc-text-field mdc-text-field--textarea ${(0,a.$)(i)}">
        ${this.renderRipple()}
        ${this.outlined?this.renderOutline():this.renderLabel()}
        ${this.renderInput()}
        ${this.renderCharCounter(t)}
        ${this.renderLineRipple()}
      </label>
      ${this.renderHelperText(n,r)}
    `}renderInput(){const e=this.label?"label":void 0,t=-1===this.minLength?void 0:this.minLength,r=-1===this.maxLength?void 0:this.maxLength,n=this.autocapitalize?this.autocapitalize:void 0;return o.dy`
      <textarea
          aria-labelledby=${(0,c.o)(e)}
          class="mdc-text-field__input"
          .value="${(0,d.a)(this.value)}"
          rows="${this.rows}"
          cols="${this.cols}"
          ?disabled="${this.disabled}"
          placeholder="${this.placeholder}"
          ?required="${this.required}"
          ?readonly="${this.readOnly}"
          minlength="${(0,c.o)(t)}"
          maxlength="${(0,c.o)(r)}"
          name="${(0,c.o)(""===this.name?void 0:this.name)}"
          inputmode="${(0,c.o)(this.inputMode)}"
          autocapitalize="${(0,c.o)(n)}"
          @input="${this.handleInputChange}"
          @blur="${this.onInputBlur}">
      </textarea>`}}(0,n.__decorate)([(0,s.IO)("textarea")],h.prototype,"formElement",void 0),(0,n.__decorate)([(0,s.Cb)({type:Number})],h.prototype,"rows",void 0),(0,n.__decorate)([(0,s.Cb)({type:Number})],h.prototype,"cols",void 0),(0,n.__decorate)([(0,s.Cb)({converter:l})],h.prototype,"charCounter",void 0)},96791:(e,t,r)=>{r.d(t,{W:()=>n});const n=r(37500).iv`.mdc-text-field{height:100%}.mdc-text-field__input{resize:none}`},89194:(e,t,r)=>{r(48175),r(65660),r(70019);var n=r(67139),i=r(50856);(0,n.k)({_template:i.d`
    <style>
      :host {
        overflow: hidden; /* needed for text-overflow: ellipsis to work on ff */
        @apply --layout-vertical;
        @apply --layout-center-justified;
        @apply --layout-flex;
      }

      :host([two-line]) {
        min-height: var(--paper-item-body-two-line-min-height, 72px);
      }

      :host([three-line]) {
        min-height: var(--paper-item-body-three-line-min-height, 88px);
      }

      :host > ::slotted(*) {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      :host > ::slotted([secondary]) {
        @apply --paper-font-body1;

        color: var(--paper-item-body-secondary-color, var(--secondary-text-color));

        @apply --paper-item-body-secondary;
      }
    </style>

    <slot></slot>
`,is:"paper-item-body"})},3239:(e,t,r)=>{function n(e){if(!e||"object"!=typeof e)return e;if("[object Date]"==Object.prototype.toString.call(e))return new Date(e.getTime());if(Array.isArray(e))return e.map(n);var t={};return Object.keys(e).forEach((function(r){t[r]=n(e[r])})),t}r.d(t,{Z:()=>n})},1460:(e,t,r)=>{r.d(t,{l:()=>s});var n=r(15304),i=r(38941);const o={},s=(0,i.XM)(class extends i.Xe{constructor(){super(...arguments),this.nt=o}render(e,t){return t()}update(e,[t,r]){if(Array.isArray(t)){if(Array.isArray(this.nt)&&this.nt.length===t.length&&t.every(((e,t)=>e===this.nt[t])))return n.Jb}else if(this.nt===t)return n.Jb;return this.nt=Array.isArray(t)?Array.from(t):t,this.render(t,r)}})},69505:(e,t,r)=>{r.d(t,{DD:()=>n,G0:()=>k,IX:()=>v,O7:()=>m,Rx:()=>g,Ry:()=>w,Yj:()=>y,Z_:()=>A,f0:()=>f,hu:()=>l,i0:()=>b,is:()=>h,jt:()=>$,lF:()=>O});class n extends TypeError{constructor(e,t){let r;const{message:n,...i}=e,{path:o}=e;super(0===o.length?n:"At path: "+o.join(".")+" -- "+n),this.value=void 0,this.key=void 0,this.type=void 0,this.refinement=void 0,this.path=void 0,this.branch=void 0,this.failures=void 0,Object.assign(this,i),this.name=this.constructor.name,this.failures=()=>{var n;return null!=(n=r)?n:r=[e,...t()]}}}function i(e){return"object"==typeof e&&null!=e}function o(e){return"string"==typeof e?JSON.stringify(e):""+e}function s(e,t,r,n){if(!0===e)return;!1===e?e={}:"string"==typeof e&&(e={message:e});const{path:i,branch:s}=t,{type:a}=r,{refinement:c,message:d="Expected a value of type `"+a+"`"+(c?" with refinement `"+c+"`":"")+", but received: `"+o(n)+"`"}=e;return{value:n,type:a,refinement:c,key:i[i.length-1],path:i,branch:s,...e,message:d}}function*a(e,t,r,n){var o;i(o=e)&&"function"==typeof o[Symbol.iterator]||(e=[e]);for(const i of e){const e=s(i,t,r,n);e&&(yield e)}}function*c(e,t,r={}){const{path:n=[],branch:o=[e],coerce:s=!1,mask:a=!1}=r,d={path:n,branch:o};if(s&&(e=t.coercer(e,d),a&&"type"!==t.type&&i(t.schema)&&i(e)&&!Array.isArray(e)))for(const r in e)void 0===t.schema[r]&&delete e[r];let l=!0;for(const r of t.validator(e,d))l=!1,yield[r,void 0];for(let[r,h,u]of t.entries(e,d)){const t=c(h,u,{path:void 0===r?n:[...n,r],branch:void 0===r?o:[...o,h],coerce:s,mask:a});for(const n of t)n[0]?(l=!1,yield[n[0],void 0]):s&&(h=n[1],void 0===r?e=h:e instanceof Map?e.set(r,h):e instanceof Set?e.add(h):i(e)&&(e[r]=h))}if(l)for(const r of t.refiner(e,d))l=!1,yield[r,void 0];l&&(yield[void 0,e])}class d{constructor(e){this.TYPE=void 0,this.type=void 0,this.schema=void 0,this.coercer=void 0,this.validator=void 0,this.refiner=void 0,this.entries=void 0;const{type:t,schema:r,validator:n,refiner:i,coercer:o=(e=>e),entries:s=function*(){}}=e;this.type=t,this.schema=r,this.entries=s,this.coercer=o,this.validator=n?(e,t)=>a(n(e,t),t,this,e):()=>[],this.refiner=i?(e,t)=>a(i(e,t),t,this,e):()=>[]}assert(e){return l(e,this)}create(e){return function(e,t){const r=u(e,t,{coerce:!0});if(r[0])throw r[0];return r[1]}(e,this)}is(e){return h(e,this)}mask(e){return function(e,t){const r=u(e,t,{coerce:!0,mask:!0});if(r[0])throw r[0];return r[1]}(e,this)}validate(e,t={}){return u(e,this,t)}}function l(e,t){const r=u(e,t);if(r[0])throw r[0]}function h(e,t){return!u(e,t)[0]}function u(e,t,r={}){const i=c(e,t,r),o=function(e){const{done:t,value:r}=e.next();return t?void 0:r}(i);if(o[0]){return[new n(o[0],(function*(){for(const e of i)e[0]&&(yield e[0])})),void 0]}return[void 0,o[1]]}function f(...e){const t="type"===e[0].type,r=e.map((e=>e.schema)),n=Object.assign({},...r);return t?j(n):w(n)}function p(e,t){return new d({type:e,schema:null,validator:t})}function y(){return p("any",(()=>!0))}function v(e){return new d({type:"array",schema:e,*entries(t){if(e&&Array.isArray(t))for(const[r,n]of t.entries())yield[r,n,e]},coercer:e=>Array.isArray(e)?e.slice():e,validator:e=>Array.isArray(e)||"Expected an array value, but received: "+o(e)})}function m(){return p("boolean",(e=>"boolean"==typeof e))}function b(e){const t=o(e),r=typeof e;return new d({type:"literal",schema:"string"===r||"number"===r||"boolean"===r?e:null,validator:r=>r===e||"Expected the literal `"+t+"`, but received: "+o(r)})}function x(){return p("never",(()=>!1))}function g(){return p("number",(e=>"number"==typeof e&&!isNaN(e)||"Expected a number, but received: "+o(e)))}function w(e){const t=e?Object.keys(e):[],r=x();return new d({type:"object",schema:e||null,*entries(n){if(e&&i(n)){const i=new Set(Object.keys(n));for(const r of t)i.delete(r),yield[r,n[r],e[r]];for(const e of i)yield[e,n[e],r]}},validator:e=>i(e)||"Expected an object, but received: "+o(e),coercer:e=>i(e)?{...e}:e})}function $(e){return new d({...e,validator:(t,r)=>void 0===t||e.validator(t,r),refiner:(t,r)=>void 0===t||e.refiner(t,r)})}function A(){return p("string",(e=>"string"==typeof e||"Expected a string, but received: "+o(e)))}function j(e){const t=Object.keys(e);return new d({type:"type",schema:e,*entries(r){if(i(r))for(const n of t)yield[n,r[n],e[n]]},validator:e=>i(e)||"Expected an object, but received: "+o(e)})}function k(e){const t=e.map((e=>e.type)).join(" | ");return new d({type:"union",schema:null,coercer:(t,r)=>(e.find((e=>{const[r]=e.validate(t,{coerce:!0});return!r}))||_()).coercer(t,r),validator(r,n){const i=[];for(const t of e){const[...e]=c(r,t,n),[o]=e;if(!o[0])return[];for(const[t]of e)t&&i.push(t)}return["Expected the value to satisfy a union of `"+t+"`, but received: "+o(r),...i]}})}function _(){return p("unknown",(()=>!0))}function O(e,t,r){return new d({...e,*refiner(n,i){yield*e.refiner(n,i);const o=a(r(n,i),i,e,n);for(const e of o)yield{...e,refinement:t}}})}}}]);