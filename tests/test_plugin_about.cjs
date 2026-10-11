// Validate plugin UI registration, ABOUT activation and normal native toggle.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync(require('path').join(__dirname,'..','plugin','quick_action.js'),'utf8');
const methods=[];const windows=[];
const plugin={guid:'asc.{TEST}',executeMethod:(name,args,cb)=>{methods.push({name,args});if(cb)cb(true);}};
const window={Asc:{plugin,PluginWindow:class { show(cfg){windows.push(cfg);} }},location:{href:'file:///plugins/index.html'}};
vm.runInNewContext(src,{window,URL,console});
plugin.init();plugin.init();
assert.equal(methods.length,1);assert.equal(methods[0].name,'AddToolbarMenuItem');
const items=methods[0].args[0].tabs[0].items;
assert.equal(items.length,2);assert(items[1].text.includes('licencek'));
plugin.event_onToolbarMenuClick('onlyoffice-native-overtype-about');
assert.equal(windows.length,1);assert(windows[0].url.endsWith('/about.html'));
plugin.event_onToolbarMenuClick('onlyoffice-native-overtype');
assert.equal(methods[1].name,'OOOvertypeToggle');
const html=fs.readFileSync(require('path').join(__dirname,'..','plugin','about.html'),'utf8');
assert(html.includes('Ascensio System SIA') && html.includes('github.com/ONLYOFFICE/sdkjs/blob/v9.4.0.129/LICENSE'));
console.log('Plugin ABOUT / toggle unit PASS');
