/*! For license information please see 73cea48e.js.LICENSE.txt */
"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[56918],{14166:(t,e,i)=>{i.d(e,{W:()=>s});var o=function(){return o=Object.assign||function(t){for(var e,i=1,o=arguments.length;i<o;i++)for(var s in e=arguments[i])Object.prototype.hasOwnProperty.call(e,s)&&(t[s]=e[s]);return t},o.apply(this,arguments)};function s(t,e,i){void 0===e&&(e=Date.now()),void 0===i&&(i={});var s=o(o({},n),i||{}),a=(+t-+e)/1e3;if(Math.abs(a)<s.second)return{value:Math.round(a),unit:"second"};var r=a/60;if(Math.abs(r)<s.minute)return{value:Math.round(r),unit:"minute"};var h=a/3600;if(Math.abs(h)<s.hour)return{value:Math.round(h),unit:"hour"};var l=a/86400;if(Math.abs(l)<s.day)return{value:Math.round(l),unit:"day"};var c=new Date(t),p=new Date(e),d=c.getFullYear()-p.getFullYear();if(Math.round(Math.abs(d))>0)return{value:Math.round(d),unit:"year"};var u=12*d+c.getMonth()-p.getMonth();if(Math.round(Math.abs(u))>0)return{value:Math.round(u),unit:"month"};var y=a/604800;return{value:Math.round(y),unit:"week"}}var n={second:45,minute:45,hour:22,day:5}},54040:(t,e,i)=>{var o=i(87480),s=i(33310),n=i(58417),a=i(39274);let r=class extends n.A{};r.styles=[a.W],r=(0,o.__decorate)([(0,s.Mo)("mwc-checkbox")],r)},56887:(t,e,i)=>{i.d(e,{F:()=>h});var o=i(87480),s=(i(54040),i(37500)),n=i(33310),a=i(8636),r=i(61092);class h extends r.K{constructor(){super(...arguments),this.left=!1,this.graphic="control"}render(){const t={"mdc-deprecated-list-item__graphic":this.left,"mdc-deprecated-list-item__meta":!this.left},e=this.renderText(),i=this.graphic&&"control"!==this.graphic&&!this.left?this.renderGraphic():s.dy``,o=this.hasMeta&&this.left?this.renderMeta():s.dy``,n=this.renderRipple();return s.dy`
      ${n}
      ${i}
      ${this.left?"":e}
      <span class=${(0,a.$)(t)}>
        <mwc-checkbox
            reducedTouchTarget
            tabindex=${this.tabindex}
            .checked=${this.selected}
            ?disabled=${this.disabled}
            @change=${this.onChange}>
        </mwc-checkbox>
      </span>
      ${this.left?e:""}
      ${o}`}async onChange(t){const e=t.target;this.selected===e.checked||(this._skipPropRequest=!0,this.selected=e.checked,await this.updateComplete,this._skipPropRequest=!1)}}(0,o.__decorate)([(0,n.IO)("slot")],h.prototype,"slotElement",void 0),(0,o.__decorate)([(0,n.IO)("mwc-checkbox")],h.prototype,"checkboxElement",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean})],h.prototype,"left",void 0),(0,o.__decorate)([(0,n.Cb)({type:String,reflect:!0})],h.prototype,"graphic",void 0)},21270:(t,e,i)=>{i.d(e,{W:()=>o});const o=i(37500).iv`:host(:not([twoline])){height:56px}:host(:not([left])) .mdc-deprecated-list-item__meta{height:40px;width:40px}`},63207:(t,e,i)=>{i(65660),i(15112);var o=i(9672),s=i(87156),n=i(50856),a=i(10994);(0,o.k)({_template:n.d`
    <style>
      :host {
        @apply --layout-inline;
        @apply --layout-center-center;
        position: relative;

        vertical-align: middle;

        fill: var(--iron-icon-fill-color, currentcolor);
        stroke: var(--iron-icon-stroke-color, none);

        width: var(--iron-icon-width, 24px);
        height: var(--iron-icon-height, 24px);
        @apply --iron-icon;
      }

      :host([hidden]) {
        display: none;
      }
    </style>
`,is:"iron-icon",properties:{icon:{type:String},theme:{type:String},src:{type:String},_meta:{value:a.XY.create("iron-meta",{type:"iconset"})}},observers:["_updateIcon(_meta, isAttached)","_updateIcon(theme, isAttached)","_srcChanged(src, isAttached)","_iconChanged(icon, isAttached)"],_DEFAULT_ICONSET:"icons",_iconChanged:function(t){var e=(t||"").split(":");this._iconName=e.pop(),this._iconsetName=e.pop()||this._DEFAULT_ICONSET,this._updateIcon()},_srcChanged:function(t){this._updateIcon()},_usesIconset:function(){return this.icon||!this.src},_updateIcon:function(){this._usesIconset()?(this._img&&this._img.parentNode&&(0,s.vz)(this.root).removeChild(this._img),""===this._iconName?this._iconset&&this._iconset.removeIcon(this):this._iconsetName&&this._meta&&(this._iconset=this._meta.byKey(this._iconsetName),this._iconset?(this._iconset.applyIcon(this,this._iconName,this.theme),this.unlisten(window,"iron-iconset-added","_updateIcon")):this.listen(window,"iron-iconset-added","_updateIcon"))):(this._iconset&&this._iconset.removeIcon(this),this._img||(this._img=document.createElement("img"),this._img.style.width="100%",this._img.style.height="100%",this._img.draggable=!1),this._img.src=this.src,(0,s.vz)(this.root).appendChild(this._img))}})},15112:(t,e,i)=>{i.d(e,{P:()=>s});i(10994);var o=i(9672);class s{constructor(t){s[" "](t),this.type=t&&t.type||"default",this.key=t&&t.key,t&&"value"in t&&(this.value=t.value)}get value(){var t=this.type,e=this.key;if(t&&e)return s.types[t]&&s.types[t][e]}set value(t){var e=this.type,i=this.key;e&&i&&(e=s.types[e]=s.types[e]||{},null==t?delete e[i]:e[i]=t)}get list(){if(this.type){var t=s.types[this.type];return t?Object.keys(t).map((function(t){return n[this.type][t]}),this):[]}}byKey(t){return this.key=t,this.value}}s[" "]=function(){},s.types={};var n=s.types;(0,o.k)({is:"iron-meta",properties:{type:{type:String,value:"default"},key:{type:String},value:{type:String,notify:!0},self:{type:Boolean,observer:"_selfChanged"},__meta:{type:Boolean,computed:"__computeMeta(type, key, value)"}},hostAttributes:{hidden:!0},__computeMeta:function(t,e,i){var o=new s({type:t,key:e});return void 0!==i&&i!==o.value?o.value=i:this.value!==o.value&&(this.value=o.value),o},get list(){return this.__meta&&this.__meta.list},_selfChanged:function(t){t&&(this.value=this)},byKey:function(t){return new s({type:this.type,key:t}).value}})},25782:(t,e,i)=>{i(10994),i(65660),i(70019),i(97968);var o=i(9672),s=i(50856),n=i(33760);(0,o.k)({_template:s.d`
    <style include="paper-item-shared-styles"></style>
    <style>
      :host {
        @apply --layout-horizontal;
        @apply --layout-center;
        @apply --paper-font-subhead;

        @apply --paper-item;
        @apply --paper-icon-item;
      }

      .content-icon {
        @apply --layout-horizontal;
        @apply --layout-center;

        width: var(--paper-item-icon-width, 56px);
        @apply --paper-item-icon;
      }
    </style>

    <div id="contentIcon" class="content-icon">
      <slot name="item-icon"></slot>
    </div>
    <slot></slot>
`,is:"paper-icon-item",behaviors:[n.U]})},89194:(t,e,i)=>{i(10994),i(65660),i(70019);var o=i(9672),s=i(50856);(0,o.k)({_template:s.d`
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
`,is:"paper-item-body"})}}]);
//# sourceMappingURL=73cea48e.js.map