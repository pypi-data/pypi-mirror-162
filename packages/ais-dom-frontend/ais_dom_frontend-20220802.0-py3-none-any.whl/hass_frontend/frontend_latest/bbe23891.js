"use strict";(self.webpackChunkhome_assistant_frontend=self.webpackChunkhome_assistant_frontend||[]).push([[97740],{42141:(e,t,i)=>{function r(e){return void 0===e||Array.isArray(e)?e:[e]}i.d(t,{r:()=>r})},43793:(e,t,i)=>{i.d(t,{x:()=>r});const r=(e,t)=>e.substring(0,t.length)===t},8330:(e,t,i)=>{i.d(t,{P:()=>r});const r=(e,t,i=!0,r=!0)=>{let n,s=0;const o=(...o)=>{const a=()=>{s=!1===i?0:Date.now(),n=void 0,e(...o)},c=Date.now();s||!1!==i||(s=c);const l=t-(c-s);l<=0||l>t?(n&&(clearTimeout(n),n=void 0),s=c,e(...o)):n||!1===r||(n=window.setTimeout(a,l))};return o.cancel=()=>{clearTimeout(n),n=void 0,s=0},o}},55422:(e,t,i)=>{i.a(e,(async e=>{i.d(t,{jV:()=>d,sS:()=>p,Yc:()=>m,tf:()=>y,o1:()=>v,hb:()=>_,ri:()=>g,MY:()=>b});var r=i(49706),n=i(58831),s=i(29171),o=i(22311),a=i(56007),c=e([s]);s=(c.then?await c:c)[0];const l="ui.components.logbook.messages",d=["counter","proximity","sensor"],u={"numeric state of":"triggered_by_numeric_state_of","state of":"triggered_by_state_of",event:"triggered_by_event",time:"triggered_by_time","time pattern":"triggered_by_time_pattern","Home Assistant stopping":"triggered_by_homeassistant_stopping","Home Assistant starting":"triggered_by_homeassistant_starting"},h={},p=async(e,t,i)=>(await e.loadBackendTranslation("device_class"),f(e,t,void 0,void 0,i)),f=(e,t,i,r,n,s)=>{if((r||s)&&(!r||0===r.length)&&(!s||0===s.length))return Promise.resolve([]);const o={type:"logbook/get_events",start_time:t};return i&&(o.end_time=i),null!=r&&r.length&&(o.entity_ids=r),null!=s&&s.length&&(o.device_ids=s),n&&(o.context_id=n),e.callWS(o)},m=(e,t,i,r,n,s)=>{if((n||s)&&(!n||0===n.length)&&(!s||0===s.length))return Promise.reject("No entities or devices");const o={type:"logbook/event_stream",start_time:i,end_time:r};return null!=n&&n.length&&(o.entity_ids=n),null!=s&&s.length&&(o.device_ids=s),e.connection.subscribeMessage((e=>t(e)),o)},y=(e,t)=>{h[`${e}${t}`]={}},v=(e,t)=>({entity_id:e.entity_id,state:t,attributes:{device_class:null==e?void 0:e.attributes.device_class,source_type:null==e?void 0:e.attributes.source_type,has_date:null==e?void 0:e.attributes.has_date,has_time:null==e?void 0:e.attributes.has_time,entity_picture_local:r.iY.has((0,n.M)(e.entity_id))||null==e?void 0:e.attributes.entity_picture_local,entity_picture:r.iY.has((0,n.M)(e.entity_id))||null==e?void 0:e.attributes.entity_picture}}),_=(e,t)=>{for(const i in u)if(t.startsWith(i))return t.replace(i,`${e(`ui.components.logbook.${u[i]}`)}`);return t},g=(e,t,i,n,o)=>{switch(o){case"device_tracker":case"person":return"not_home"===i?t(`${l}.was_away`):"home"===i?t(`${l}.was_at_home`):t(`${l}.was_at_state`,"state",i);case"sun":return t("above_horizon"===i?`${l}.rose`:`${l}.set`);case"binary_sensor":{const e=i===r.uo,s=i===r.lC,o=n.attributes.device_class;switch(o){case"battery":if(e)return t(`${l}.was_low`);if(s)return t(`${l}.was_normal`);break;case"connectivity":if(e)return t(`${l}.was_connected`);if(s)return t(`${l}.was_disconnected`);break;case"door":case"garage_door":case"opening":case"window":if(e)return t(`${l}.was_opened`);if(s)return t(`${l}.was_closed`);break;case"lock":if(e)return t(`${l}.was_unlocked`);if(s)return t(`${l}.was_locked`);break;case"plug":if(e)return t(`${l}.was_plugged_in`);if(s)return t(`${l}.was_unplugged`);break;case"presence":if(e)return t(`${l}.was_at_home`);if(s)return t(`${l}.was_away`);break;case"safety":if(e)return t(`${l}.was_unsafe`);if(s)return t(`${l}.was_safe`);break;case"cold":case"gas":case"heat":case"moisture":case"motion":case"occupancy":case"power":case"problem":case"smoke":case"sound":case"vibration":if(e)return t(`${l}.detected_device_class`,{device_class:t(`component.binary_sensor.device_class.${o}`)});if(s)return t(`${l}.cleared_device_class`,{device_class:t(`component.binary_sensor.device_class.${o}`)});break;case"tamper":if(e)return t(`${l}.detected_tampering`);if(s)return t(`${l}.cleared_tampering`)}break}case"cover":switch(i){case"open":return t(`${l}.was_opened`);case"opening":return t(`${l}.is_opening`);case"closing":return t(`${l}.is_closing`);case"closed":return t(`${l}.was_closed`)}break;case"lock":if("unlocked"===i)return t(`${l}.was_unlocked`);if("locked"===i)return t(`${l}.was_locked`)}return i===r.uo?t(`${l}.turned_on`):i===r.lC?t(`${l}.turned_off`):a.V_.includes(i)?t(`${l}.became_unavailable`):e.localize(`${l}.changed_to_state`,"state",n?(0,s.D)(t,n,e.locale,i):i)},b=e=>"sensor"!==(0,o.N)(e)||void 0===e.attributes.unit_of_measurement&&void 0===e.attributes.state_class}))},97389:(e,t,i)=>{if(i.d(t,{mA:()=>n,lj:()=>s,U_:()=>o,nV:()=>a,Zm:()=>c}),32143==i.j)var r=i(43793);const n=(e,t,i,r)=>e.callWS({type:"trace/get",domain:t,item_id:i,run_id:r}),s=(e,t,i)=>e.callWS({type:"trace/list",domain:t,item_id:i}),o=(e,t,i)=>e.callWS({type:"trace/contexts",domain:t,item_id:i}),a=(e,t)=>{const i=t.split("/").reverse();let r=e;for(;i.length;){const e=i.pop(),t=Number(e);if(isNaN(t)){const t=r[e];if(!t&&"sequence"===e)continue;r=t}else if(Array.isArray(r))r=r[t];else if(0!==t)throw new Error("If config is not an array, can only return index 0")}return r},c=e=>"trigger"===e||(0,r.x)(e,"trigger/")},65253:(e,t,i)=>{i.d(t,{Pb:()=>r,CE:()=>n,uh:()=>s,r4:()=>o,Nq:()=>a,h8:()=>c,fm:()=>l,FH:()=>d});const r="system-admin",n="system-users",s=async e=>e.callWS({type:"config/auth/list"}),o=async(e,t,i,r)=>e.callWS({type:"config/auth/create",name:t,group_ids:i,local_only:r}),a=async(e,t,i)=>e.callWS({...i,type:"config/auth/update",user_id:t}),c=async(e,t)=>e.callWS({type:"config/auth/delete",user_id:t}),l=e=>e?e.trim().split(" ").slice(0,3).map((e=>e.substring(0,1))).join(""):"?",d=(e,t,i)=>{const r=[],n=t=>e.localize(`ui.panel.config.users.${t}`);return t.is_owner&&r.push(["M12 2C6.47 2 2 6.5 2 12C2 17.5 6.5 22 12 22S22 17.5 22 12 17.5 2 12 2M12 20C7.58 20 4 16.42 4 12C4 7.58 7.58 4 12 4S20 7.58 20 12C20 16.42 16.42 20 12 20M8 14L7 8L10 10L12 7L14 10L17 8L16 14H8M8.56 16C8.22 16 8 15.78 8 15.44V15H16V15.44C16 15.78 15.78 16 15.44 16H8.56Z",n("is_owner")]),i&&t.system_generated&&r.push(["M11,7H15V9H11V11H13A2,2 0 0,1 15,13V15A2,2 0 0,1 13,17H9V15H13V13H11A2,2 0 0,1 9,11V9A2,2 0 0,1 11,7M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4Z",n("is_system")]),t.local_only&&r.push(["M12 20C7.6 20 4 16.4 4 12S7.6 4 12 4 20 7.6 20 12 16.4 20 12 20M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M11 14H13V17H16V12H18L12 7L6 12H8V17H11V14",n("is_local")]),t.is_active||r.push(["M12 2C17.5 2 22 6.5 22 12S17.5 22 12 22 2 17.5 2 12 6.5 2 12 2M12 4C10.1 4 8.4 4.6 7.1 5.7L18.3 16.9C19.3 15.5 20 13.8 20 12C20 7.6 16.4 4 12 4M16.9 18.3L5.7 7.1C4.6 8.4 4 10.1 4 12C4 16.4 7.6 20 12 20C13.9 20 15.6 19.4 16.9 18.3Z",n("is_not_active")]),r}},44198:(e,t,i)=>{i.a(e,(async e=>{i(9874);var t=i(37500),r=i(33310),n=i(8636),s=i(12198),o=i(49684),a=i(25516),c=i(47181),l=i(58831),d=i(7323),u=(i(3143),i(31206),i(42952)),h=i(55422),p=i(11654),f=i(11254),m=e([h,o,s,u]);function y(){y=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var s="static"===n?e:i;this.defineClassElement(s,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!g(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var s=this.decorateConstructor(i,t);return r.push.apply(r,s.finishers),s.finishers=r,s},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,s=n.length-1;s>=0;s--){var o=t[e.placement];o.splice(o.indexOf(e.key),1);var a=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,n[s])(a)||a);e=c.element,this.addElementPlacement(e,t),c.finisher&&r.push(c.finisher);var l=c.extras;if(l){for(var d=0;d<l.length;d++)this.addElementPlacement(l[d],t);i.push.apply(i,l)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),s=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==s.finisher&&i.push(s.finisher),void 0!==s.elements){e=s.elements;for(var o=0;o<e.length-1;o++)for(var a=o+1;a<e.length;a++)if(e[o].key===e[a].key&&e[o].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[o].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return E(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?E(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=w(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var s={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),s.initializer=e.initializer),s},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:k(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=k(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function v(e){var t,i=w(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function _(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function g(e){return e.decorators&&e.decorators.length}function b(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function k(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function w(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function E(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}[h,o,s,u]=m.then?await m:m;const x=["script","automation"];!function(e,t,i,r){var n=y();if(r)for(var s=0;s<r.length;s++)n=r[s](n);var o=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===s.key&&e.placement===s.placement},r=0;r<e.length;r++){var n,s=e[r];if("method"===s.kind&&(n=t.find(i)))if(b(s.descriptor)||b(n.descriptor)){if(g(s)||g(n))throw new ReferenceError("Duplicated methods ("+s.key+") can't be decorated.");n.descriptor=s.descriptor}else{if(g(s)){if(g(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+s.key+").");n.decorators=s.decorators}_(s,n)}else t.push(s)}return t}(o.d.map(v)),e);n.initializeClassElements(o.F,a.elements),n.runClassFinishers(o.F,a.finishers)}([(0,r.Mo)("ha-logbook-renderer")],(function(e,i){return{F:class extends i{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[(0,r.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,r.Cb)({attribute:!1})],key:"userIdToName",value:()=>({})},{kind:"field",decorators:[(0,r.Cb)({attribute:!1})],key:"traceContexts",value:()=>({})},{kind:"field",decorators:[(0,r.Cb)({attribute:!1})],key:"entries",value:()=>[]},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"narrow"})],key:"narrow",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"virtualize",reflect:!0})],key:"virtualize",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"no-icon"})],key:"noIcon",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"no-name"})],key:"noName",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"relative-time"})],key:"relativeTime",value:()=>!1},{kind:"field",decorators:[(0,a.i)(".container")],key:"_savedScrollPos",value:void 0},{kind:"method",key:"shouldUpdate",value:function(e){const t=e.get("hass"),i=void 0===t||t.locale!==this.hass.locale;return e.has("entries")||e.has("traceContexts")||i}},{kind:"method",key:"render",value:function(){var e;return null!==(e=this.entries)&&void 0!==e&&e.length?t.dy`
      <div
        class="container ha-scrollbar ${(0,n.$)({narrow:this.narrow,"no-name":this.noName,"no-icon":this.noIcon})}"
        @scroll=${this._saveScrollPos}
      >
        ${this.virtualize?t.dy`<lit-virtualizer
              @visibilityChanged=${this._visibilityChanged}
              scroller
              class="ha-scrollbar"
              .items=${this.entries}
              .renderItem=${this._renderLogbookItem}
            >
            </lit-virtualizer>`:this.entries.map(((e,t)=>this._renderLogbookItem(e,t)))}
      </div>
    `:t.dy`
        <div class="container no-entries">
          ${this.hass.localize("ui.components.logbook.entries_not_found")}
        </div>
      `}},{kind:"field",key:"_renderLogbookItem",value(){return(e,i)=>{var r;if(!e||void 0===i)return t.dy``;const a=this.entries[i-1],c=[],u=e.entity_id?this.hass.states[e.entity_id]:void 0,p=u?(0,h.o1)(u,e.state):void 0,m=e.entity_id?(0,l.M)(e.entity_id):e.domain,y=p||e.icon||e.state||!m||!(0,d.p)(this.hass,m)?void 0:(0,f.X1)({domain:m,type:"icon",useFallback:!0,darkOptimized:null===(r=this.hass.themes)||void 0===r?void 0:r.darkMode});return t.dy`
      <div class="entry-container">
        ${0===i||null!=e&&e.when&&null!=a&&a.when&&new Date(1e3*e.when).toDateString()!==new Date(1e3*a.when).toDateString()?t.dy`
              <h4 class="date">
                ${(0,s.p6)(new Date(1e3*e.when),this.hass.locale)}
              </h4>
            `:t.dy``}

        <div class="entry ${(0,n.$)({"no-entity":!e.entity_id})}">
          <div class="icon-message">
            ${this.noIcon?"":t.dy`
                  <state-badge
                    .hass=${this.hass}
                    .overrideIcon=${e.icon}
                    .overrideImage=${y}
                    .stateObj=${e.icon?void 0:p}
                    .stateColor=${!1}
                  ></state-badge>
                `}
            <div class="message-relative_time">
              <div class="message">
                ${this.noName?"":this._renderEntity(e.entity_id,e.name)}
                ${this._renderMessage(e,c,m,p)}
                ${this._renderContextMessage(e,c)}
              </div>
              <div class="secondary">
                <span
                  >${(0,o.Vu)(new Date(1e3*e.when),this.hass.locale)}</span
                >
                -
                <ha-relative-time
                  .hass=${this.hass}
                  .datetime=${1e3*e.when}
                  capitalize
                ></ha-relative-time>
                ${e.context_user_id?t.dy`${this._renderUser(e)}`:""}
                ${x.includes(e.domain)&&e.context_id in this.traceContexts?t.dy`
                      -
                      <a
                        href=${`/config/${this.traceContexts[e.context_id].domain}/trace/${"script"===this.traceContexts[e.context_id].domain?`script.${this.traceContexts[e.context_id].item_id}`:this.traceContexts[e.context_id].item_id}?run_id=${this.traceContexts[e.context_id].run_id}`}
                        @click=${this._close}
                        >${this.hass.localize("ui.components.logbook.show_trace")}</a
                      >
                    `:""}
              </div>
            </div>
          </div>
        </div>
      </div>
    `}}},{kind:"method",decorators:[(0,r.hO)({passive:!0})],key:"_saveScrollPos",value:function(e){this._savedScrollPos=e.target.scrollTop}},{kind:"method",decorators:[(0,r.hO)({passive:!0})],key:"_visibilityChanged",value:function(e){(0,c.B)(this,"hass-logbook-live",{enable:0===e.first})}},{kind:"method",key:"_renderMessage",value:function(e,t,i,r){if(e.entity_id&&e.state)return r?(0,h.ri)(this.hass,this.hass.localize,e.state,r,i):e.state;const n=(e=>e.context_event_type||e.context_state||e.context_message)(e);let s=e.message;if(x.includes(i)&&e.source){if(n)return"";s=(0,h.hb)(this.hass.localize,e.source)}return s?this._formatMessageWithPossibleEntity(n?((e,t)=>t?e.replace(t," "):e)(s,e.context_entity_id):s,t,void 0):""}},{kind:"method",key:"_renderUser",value:function(e){const t=e.context_user_id&&this.userIdToName[e.context_user_id];return t?`- ${t}`:""}},{kind:"method",key:"_renderUnseenContextSourceEntity",value:function(e,i){return!e.context_entity_id||i.includes(e.context_entity_id)?"":t.dy` (${this._renderEntity(e.context_entity_id,e.context_entity_id_name)})`}},{kind:"method",key:"_renderContextMessage",value:function(e,i){if(e.context_state){const i=e.context_entity_id&&e.context_entity_id in this.hass.states?(0,h.o1)(this.hass.states[e.context_entity_id],e.context_state):void 0;return t.dy`${this.hass.localize("ui.components.logbook.triggered_by_state_of")}
      ${this._renderEntity(e.context_entity_id,e.context_entity_id_name)}
      ${i?(0,h.ri)(this.hass,this.hass.localize,e.context_state,i,(0,l.M)(e.context_entity_id)):e.context_state}`}if("call_service"===e.context_event_type)return t.dy`${this.hass.localize("ui.components.logbook.triggered_by_service")}
      ${e.context_domain}.${e.context_service}`;if(!e.context_message||i.includes(e.context_entity_id))return"";if("automation_triggered"===e.context_event_type||"script_started"===e.context_event_type){const r=e.context_source?e.context_source:e.context_message.replace("triggered by ",""),n=(0,h.hb)(this.hass.localize,r);return t.dy`${this.hass.localize("automation_triggered"===e.context_event_type?"ui.components.logbook.triggered_by_automation":"ui.components.logbook.triggered_by_script")}
      ${this._renderEntity(e.context_entity_id,e.context_entity_id_name)}
      ${e.context_message?this._formatMessageWithPossibleEntity(n,i):""}`}return t.dy` ${this.hass.localize("ui.components.logbook.triggered_by")}
    ${e.context_name}
    ${this._formatMessageWithPossibleEntity(e.context_message,i,e.context_entity_id)}
    ${this._renderUnseenContextSourceEntity(e,i)}`}},{kind:"method",key:"_renderEntity",value:function(e,i){const r=e&&e in this.hass.states,n=i||r&&this.hass.states[e].attributes.friendly_name||e;return r?t.dy`<button
      class="link"
      @click=${this._entityClicked}
      .entityId=${e}
    >
      ${n}
    </button>`:n}},{kind:"method",key:"_formatMessageWithPossibleEntity",value:function(e,i,r){if(-1!==e.indexOf(".")){const r=e.split(" ");for(let e=0,n=r.length;e<n;e++)if(r[e]in this.hass.states){const n=r[e];if(i.includes(n))return"";i.push(n);const s=r.splice(e);return s.shift(),t.dy`${r.join(" ")}
          ${this._renderEntity(n,this.hass.states[n].attributes.friendly_name)}
          ${s.join(" ")}`}}if(r&&r in this.hass.states){const n=this.hass.states[r].attributes.friendly_name;if(n&&e.endsWith(n))return i.includes(r)?"":(i.push(r),e=e.substring(0,e.length-n.length),t.dy`${e}
        ${this._renderEntity(r,n)}`)}return e}},{kind:"method",key:"_entityClicked",value:function(e){const t=e.currentTarget.entityId;t&&(e.preventDefault(),e.stopPropagation(),(0,c.B)(this,"hass-more-info",{entityId:t}))}},{kind:"method",key:"_close",value:function(){setTimeout((()=>(0,c.B)(this,"closed")),500)}},{kind:"get",static:!0,key:"styles",value:function(){return[p.Qx,p.$c,p.k1,t.iv`
        :host([virtualize]) {
          display: block;
          height: 100%;
        }

        .entry-container {
          width: 100%;
        }

        .entry {
          display: flex;
          width: 100%;
          line-height: 2em;
          padding: 8px 16px;
          box-sizing: border-box;
          border-top: 1px solid var(--divider-color);
        }

        .entry.no-entity,
        .no-name .entry {
          cursor: default;
        }

        .entry:hover {
          background-color: rgba(var(--rgb-primary-text-color), 0.04);
        }

        .narrow:not(.no-icon) .time {
          margin-left: 32px;
          margin-inline-start: 32px;
          margin-inline-end: initial;
          direction: var(--direction);
        }

        .message-relative_time {
          display: flex;
          flex-direction: column;
        }

        .secondary {
          font-size: 12px;
          line-height: 1.7;
        }

        .secondary a {
          color: var(--secondary-text-color);
        }

        .date {
          margin: 8px 0;
          padding: 0 16px;
        }

        .icon-message {
          display: flex;
          align-items: center;
        }

        .no-entries {
          text-align: center;
          color: var(--secondary-text-color);
        }

        state-badge {
          margin-right: 16px;
          margin-inline-start: initial;
          flex-shrink: 0;
          color: var(--state-icon-color);
          margin-inline-end: 16px;
          direction: var(--direction);
        }

        .message {
          color: var(--primary-text-color);
        }

        .no-name .message:first-letter {
          text-transform: capitalize;
        }

        a {
          color: var(--primary-color);
          text-decoration: none;
        }

        button.link {
          color: var(--paper-item-icon-color);
          text-decoration: none;
        }

        .container {
          max-height: var(--logbook-max-height);
        }

        .container,
        lit-virtualizer {
          height: 100%;
        }

        lit-virtualizer {
          contain: size layout !important;
        }

        .narrow .entry {
          line-height: 1.5;
        }

        .narrow .icon-message state-badge {
          margin-left: 0;
          margin-inline-start: 0;
          margin-inline-end: initial;
          direction: var(--direction);
        }
      `]}}]}}),t.oi)}))},97740:(e,t,i)=>{i.a(e,(async e=>{var t=i(37500),r=i(33310),n=i(7323),s=i(42141),o=i(22311),a=i(8330),c=(i(31206),i(55422)),l=i(97389),d=i(65253),u=i(44198),h=e([c,u]);function p(){p=function(){return e};var e={elementsDefinitionOrder:[["method"],["field"]],initializeInstanceElements:function(e,t){["method","field"].forEach((function(i){t.forEach((function(t){t.kind===i&&"own"===t.placement&&this.defineClassElement(e,t)}),this)}),this)},initializeClassElements:function(e,t){var i=e.prototype;["method","field"].forEach((function(r){t.forEach((function(t){var n=t.placement;if(t.kind===r&&("static"===n||"prototype"===n)){var s="static"===n?e:i;this.defineClassElement(s,t)}}),this)}),this)},defineClassElement:function(e,t){var i=t.descriptor;if("field"===t.kind){var r=t.initializer;i={enumerable:i.enumerable,writable:i.writable,configurable:i.configurable,value:void 0===r?void 0:r.call(e)}}Object.defineProperty(e,t.key,i)},decorateClass:function(e,t){var i=[],r=[],n={static:[],prototype:[],own:[]};if(e.forEach((function(e){this.addElementPlacement(e,n)}),this),e.forEach((function(e){if(!y(e))return i.push(e);var t=this.decorateElement(e,n);i.push(t.element),i.push.apply(i,t.extras),r.push.apply(r,t.finishers)}),this),!t)return{elements:i,finishers:r};var s=this.decorateConstructor(i,t);return r.push.apply(r,s.finishers),s.finishers=r,s},addElementPlacement:function(e,t,i){var r=t[e.placement];if(!i&&-1!==r.indexOf(e.key))throw new TypeError("Duplicated element ("+e.key+")");r.push(e.key)},decorateElement:function(e,t){for(var i=[],r=[],n=e.decorators,s=n.length-1;s>=0;s--){var o=t[e.placement];o.splice(o.indexOf(e.key),1);var a=this.fromElementDescriptor(e),c=this.toElementFinisherExtras((0,n[s])(a)||a);e=c.element,this.addElementPlacement(e,t),c.finisher&&r.push(c.finisher);var l=c.extras;if(l){for(var d=0;d<l.length;d++)this.addElementPlacement(l[d],t);i.push.apply(i,l)}}return{element:e,finishers:r,extras:i}},decorateConstructor:function(e,t){for(var i=[],r=t.length-1;r>=0;r--){var n=this.fromClassDescriptor(e),s=this.toClassDescriptor((0,t[r])(n)||n);if(void 0!==s.finisher&&i.push(s.finisher),void 0!==s.elements){e=s.elements;for(var o=0;o<e.length-1;o++)for(var a=o+1;a<e.length;a++)if(e[o].key===e[a].key&&e[o].placement===e[a].placement)throw new TypeError("Duplicated element ("+e[o].key+")")}}return{elements:e,finishers:i}},fromElementDescriptor:function(e){var t={kind:e.kind,key:e.key,placement:e.placement,descriptor:e.descriptor};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),"field"===e.kind&&(t.initializer=e.initializer),t},toElementDescriptors:function(e){var t;if(void 0!==e)return(t=e,function(e){if(Array.isArray(e))return e}(t)||function(e){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}(t)||function(e,t){if(e){if("string"==typeof e)return b(e,t);var i=Object.prototype.toString.call(e).slice(8,-1);return"Object"===i&&e.constructor&&(i=e.constructor.name),"Map"===i||"Set"===i?Array.from(e):"Arguments"===i||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(i)?b(e,t):void 0}}(t)||function(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()).map((function(e){var t=this.toElementDescriptor(e);return this.disallowProperty(e,"finisher","An element descriptor"),this.disallowProperty(e,"extras","An element descriptor"),t}),this)},toElementDescriptor:function(e){var t=String(e.kind);if("method"!==t&&"field"!==t)throw new TypeError('An element descriptor\'s .kind property must be either "method" or "field", but a decorator created an element descriptor with .kind "'+t+'"');var i=g(e.key),r=String(e.placement);if("static"!==r&&"prototype"!==r&&"own"!==r)throw new TypeError('An element descriptor\'s .placement property must be one of "static", "prototype" or "own", but a decorator created an element descriptor with .placement "'+r+'"');var n=e.descriptor;this.disallowProperty(e,"elements","An element descriptor");var s={kind:t,key:i,placement:r,descriptor:Object.assign({},n)};return"field"!==t?this.disallowProperty(e,"initializer","A method descriptor"):(this.disallowProperty(n,"get","The property descriptor of a field descriptor"),this.disallowProperty(n,"set","The property descriptor of a field descriptor"),this.disallowProperty(n,"value","The property descriptor of a field descriptor"),s.initializer=e.initializer),s},toElementFinisherExtras:function(e){return{element:this.toElementDescriptor(e),finisher:_(e,"finisher"),extras:this.toElementDescriptors(e.extras)}},fromClassDescriptor:function(e){var t={kind:"class",elements:e.map(this.fromElementDescriptor,this)};return Object.defineProperty(t,Symbol.toStringTag,{value:"Descriptor",configurable:!0}),t},toClassDescriptor:function(e){var t=String(e.kind);if("class"!==t)throw new TypeError('A class descriptor\'s .kind property must be "class", but a decorator created a class descriptor with .kind "'+t+'"');this.disallowProperty(e,"key","A class descriptor"),this.disallowProperty(e,"placement","A class descriptor"),this.disallowProperty(e,"descriptor","A class descriptor"),this.disallowProperty(e,"initializer","A class descriptor"),this.disallowProperty(e,"extras","A class descriptor");var i=_(e,"finisher");return{elements:this.toElementDescriptors(e.elements),finisher:i}},runClassFinishers:function(e,t){for(var i=0;i<t.length;i++){var r=(0,t[i])(e);if(void 0!==r){if("function"!=typeof r)throw new TypeError("Finishers must return a constructor.");e=r}}return e},disallowProperty:function(e,t,i){if(void 0!==e[t])throw new TypeError(i+" can't have a ."+t+" property.")}};return e}function f(e){var t,i=g(e.key);"method"===e.kind?t={value:e.value,writable:!0,configurable:!0,enumerable:!1}:"get"===e.kind?t={get:e.value,configurable:!0,enumerable:!1}:"set"===e.kind?t={set:e.value,configurable:!0,enumerable:!1}:"field"===e.kind&&(t={configurable:!0,writable:!0,enumerable:!0});var r={kind:"field"===e.kind?"field":"method",key:i,placement:e.static?"static":"field"===e.kind?"own":"prototype",descriptor:t};return e.decorators&&(r.decorators=e.decorators),"field"===e.kind&&(r.initializer=e.value),r}function m(e,t){void 0!==e.descriptor.get?t.descriptor.get=e.descriptor.get:t.descriptor.set=e.descriptor.set}function y(e){return e.decorators&&e.decorators.length}function v(e){return void 0!==e&&!(void 0===e.value&&void 0===e.writable)}function _(e,t){var i=e[t];if(void 0!==i&&"function"!=typeof i)throw new TypeError("Expected '"+t+"' to be a function");return i}function g(e){var t=function(e,t){if("object"!=typeof e||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t||"default");if("object"!=typeof r)return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return("string"===t?String:Number)(e)}(e,"string");return"symbol"==typeof t?t:String(t)}function b(e,t){(null==t||t>e.length)&&(t=e.length);for(var i=0,r=new Array(t);i<t;i++)r[i]=e[i];return r}function k(e,t,i){return k="undefined"!=typeof Reflect&&Reflect.get?Reflect.get:function(e,t,i){var r=function(e,t){for(;!Object.prototype.hasOwnProperty.call(e,t)&&null!==(e=w(e)););return e}(e,t);if(r){var n=Object.getOwnPropertyDescriptor(r,t);return n.get?n.get.call(i):n.value}},k(e,t,i||e)}function w(e){return w=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},w(e)}[c,u]=h.then?await h:h;const E=(e,t)=>new Date(e.getTime()-1e3*t).getTime()/1e3,x=(e,t)=>(void 0!==e||void 0!==t)&&(!e||!t||e.length!==t.length||!e.every((e=>t.includes(e))));!function(e,t,i,r){var n=p();if(r)for(var s=0;s<r.length;s++)n=r[s](n);var o=t((function(e){n.initializeInstanceElements(e,a.elements)}),i),a=n.decorateClass(function(e){for(var t=[],i=function(e){return"method"===e.kind&&e.key===s.key&&e.placement===s.placement},r=0;r<e.length;r++){var n,s=e[r];if("method"===s.kind&&(n=t.find(i)))if(v(s.descriptor)||v(n.descriptor)){if(y(s)||y(n))throw new ReferenceError("Duplicated methods ("+s.key+") can't be decorated.");n.descriptor=s.descriptor}else{if(y(s)){if(y(n))throw new ReferenceError("Decorators can't be placed on different accessors with for the same property ("+s.key+").");n.decorators=s.decorators}m(s,n)}else t.push(s)}return t}(o.d.map(f)),e);n.initializeClassElements(o.F,a.elements),n.runClassFinishers(o.F,a.finishers)}([(0,r.Mo)("ha-logbook")],(function(e,i){class u extends i{constructor(...t){super(...t),e(this)}}return{F:u,d:[{kind:"field",decorators:[(0,r.Cb)({attribute:!1})],key:"hass",value:void 0},{kind:"field",decorators:[(0,r.Cb)()],key:"time",value:void 0},{kind:"field",decorators:[(0,r.Cb)()],key:"entityIds",value:void 0},{kind:"field",decorators:[(0,r.Cb)()],key:"deviceIds",value:void 0},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"narrow"})],key:"narrow",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"virtualize",reflect:!0})],key:"virtualize",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"no-icon"})],key:"noIcon",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"no-name"})],key:"noName",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean,attribute:"relative-time"})],key:"relativeTime",value:()=>!1},{kind:"field",decorators:[(0,r.Cb)({type:Boolean})],key:"showMoreLink",value:()=>!0},{kind:"field",decorators:[(0,r.SB)()],key:"_logbookEntries",value:void 0},{kind:"field",decorators:[(0,r.SB)()],key:"_traceContexts",value:()=>({})},{kind:"field",decorators:[(0,r.SB)()],key:"_userIdToName",value:()=>({})},{kind:"field",decorators:[(0,r.SB)()],key:"_error",value:void 0},{kind:"field",key:"_subscribed",value:void 0},{kind:"field",key:"_liveUpdatesEnabled",value:()=>!0},{kind:"field",key:"_pendingStreamMessages",value:()=>[]},{kind:"field",key:"_throttleGetLogbookEntries",value(){return(0,a.P)((()=>this._getLogBookData()),1e3)}},{kind:"method",key:"render",value:function(){return(0,n.p)(this.hass,"logbook")?this._error?t.dy`<div class="no-entries">
        ${`${this.hass.localize("ui.components.logbook.retrieval_error")}: ${this._error}`}
      </div>`:void 0===this._logbookEntries?t.dy`
        <div class="progress-wrapper">
          <ha-circular-progress
            active
            alt=${this.hass.localize("ui.common.loading")}
          ></ha-circular-progress>
        </div>
      `:0===this._logbookEntries.length?t.dy`<div class="no-entries">
        ${this.hass.localize("ui.components.logbook.entries_not_found")}
      </div>`:t.dy`
      <ha-logbook-renderer
        .hass=${this.hass}
        .narrow=${this.narrow}
        .virtualize=${this.virtualize}
        .noIcon=${this.noIcon}
        .noName=${this.noName}
        .relativeTime=${this.relativeTime}
        .entries=${this._logbookEntries}
        .traceContexts=${this._traceContexts}
        .userIdToName=${this._userIdToName}
        @hass-logbook-live=${this._handleLogbookLive}
      ></ha-logbook-renderer>
    `:t.dy``}},{kind:"method",key:"refresh",value:async function(e=!1){(e||!this._subscribed&&void 0!==this._logbookEntries)&&(this._unsubscribeSetLoading(),this._throttleGetLogbookEntries.cancel(),this._updateTraceContexts.cancel(),this._updateUsers.cancel(),"range"in this.time&&(0,c.tf)(this.time.range[0].toISOString(),this.time.range[1].toISOString()),this._throttleGetLogbookEntries())}},{kind:"method",key:"firstUpdated",value:function(e){k(w(u.prototype),"firstUpdated",this).call(this,e)}},{kind:"method",key:"shouldUpdate",value:function(e){if(1!==e.size||!e.has("hass"))return!0;const t=e.get("hass");return!t||t.localize!==this.hass.localize}},{kind:"method",key:"updated",value:function(e){let t=e.has("time");for(const i of["entityIds","deviceIds"]){if(!e.has(i))continue;const r=e.get(i),n=this[i];if(x(r,n)){t=!0;break}}t&&this.refresh(!0)}},{kind:"method",key:"_handleLogbookLive",value:function(e){e.detail.enable&&!this._liveUpdatesEnabled&&(this._pendingStreamMessages.forEach((e=>this._processStreamMessage(e))),this._pendingStreamMessages=[]),this._liveUpdatesEnabled=e.detail.enable}},{kind:"get",key:"_filterAlwaysEmptyResults",value:function(){const e=(0,s.r)(this.entityIds),t=(0,s.r)(this.deviceIds);return(e||t)&&(!e||0===e.length)&&(!t||0===t.length)}},{kind:"method",key:"_unsubscribe",value:function(){this._subscribed&&(this._subscribed.then((e=>e?e().catch((()=>{})):void 0)),this._subscribed=void 0)}},{kind:"method",key:"connectedCallback",value:function(){k(w(u.prototype),"connectedCallback",this).call(this),this.hasUpdated&&this._subscribeLogbookPeriod(this._calculateLogbookPeriod())}},{kind:"method",key:"disconnectedCallback",value:function(){k(w(u.prototype),"disconnectedCallback",this).call(this),this._unsubscribeSetLoading()}},{kind:"method",key:"_unsubscribeSetLoading",value:function(){this._logbookEntries=void 0,this._unsubscribe()}},{kind:"method",key:"_unsubscribeNoResults",value:function(){this._logbookEntries=[],this._unsubscribe()}},{kind:"method",key:"_calculateLogbookPeriod",value:function(){const e=new Date;if("range"in this.time)return{now:e,startTime:this.time.range[0],endTime:this.time.range[1],purgeBeforePythonTime:void 0};if("recent"in this.time){const t=E(e,this.time.recent);return{now:e,startTime:new Date(1e3*t),endTime:new Date(e.getTime()+31536e6),purgeBeforePythonTime:E(e,this.time.recent)}}throw new Error("Unexpected time specified")}},{kind:"method",key:"_subscribeLogbookPeriod",value:function(e){return this._subscribed||(this._subscribed=(0,c.Yc)(this.hass,(e=>{this._subscribed&&this._processOrQueueStreamMessage(e)}),e.startTime.toISOString(),e.endTime.toISOString(),(0,s.r)(this.entityIds),(0,s.r)(this.deviceIds)).catch((e=>{this._subscribed=void 0,this._error=e}))),!0}},{kind:"method",key:"_getLogBookData",value:async function(){var e;if(this._error=void 0,this._filterAlwaysEmptyResults)return void this._unsubscribeNoResults();const t=this._calculateLogbookPeriod();t.startTime>t.now?this._unsubscribeNoResults():(this._updateUsers(),null!==(e=this.hass.user)&&void 0!==e&&e.is_admin&&this._updateTraceContexts(),this._subscribeLogbookPeriod(t))}},{kind:"field",key:"_nonExpiredRecords",value(){return e=>this._logbookEntries?e?this._logbookEntries.filter((t=>t.when>e)):this._logbookEntries:[]}},{kind:"field",key:"_processOrQueueStreamMessage",value(){return e=>{this._liveUpdatesEnabled?this._processStreamMessage(e):this._pendingStreamMessages.push(e)}}},{kind:"field",key:"_processStreamMessage",value(){return e=>{const t="recent"in this.time?E(new Date,this.time.recent):void 0,i=[...e.events].reverse();if(!this._logbookEntries||!this._logbookEntries.length)return void(this._logbookEntries=i);if(!i.length)return;const r=this._nonExpiredRecords(t);this._logbookEntries=r.length?i[0].when>=r[0].when?i.concat(r):r.concat(i):i}}},{kind:"field",key:"_updateTraceContexts",value(){return(0,a.P)((async()=>{this._traceContexts=await(0,l.U_)(this.hass)}),6e4)}},{kind:"field",key:"_updateUsers",value(){return(0,a.P)((async()=>{var e;const t={},i=(null===(e=this.hass.user)||void 0===e?void 0:e.is_admin)&&(0,d.uh)(this.hass);for(const e of Object.values(this.hass.states))e.attributes.user_id&&"person"===(0,o.N)(e)&&(t[e.attributes.user_id]=e.attributes.friendly_name);if(i){const e=await i;for(const i of e)i.id in t||(t[i.id]=i.name)}this._userIdToName=t}),6e4)}},{kind:"get",static:!0,key:"styles",value:function(){return[t.iv`
        :host {
          display: block;
        }

        :host([virtualize]) {
          height: 100%;
        }

        .no-entries {
          text-align: center;
          padding: 16px;
          color: var(--secondary-text-color);
        }

        .progress-wrapper {
          display: flex;
          justify-content: center;
          height: 100%;
          align-items: center;
        }
      `]}}]}}),t.oi)}))},11254:(e,t,i)=>{i.d(t,{X1:()=>r,RU:()=>n,u4:()=>s,zC:()=>o});const r=e=>e.domain.startsWith("ais_")?`https://ai-speaker.com/images/brands/${e.domain}/${e.type}.png`:`https://brands.home-assistant.io/${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,n=e=>`https://brands.home-assistant.io/hardware/${e.category}/${e.darkOptimized?"dark_":""}${e.manufacturer}${e.model?`_${e.model}`:""}.png`,s=e=>e.split("/")[4],o=e=>e.startsWith("https://brands.home-assistant.io/")}}]);
//# sourceMappingURL=bbe23891.js.map