'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../src/rc5_runtime.js'),'utf8');
const old='pending.at - a.lastTime > 1800', next='pending.at - a.lastTime > 10000';
assert.equal(src.split(old).length-1,1);
let clock=1000;
const FakeDate={now:()=>clock};
function CDocument(h){this.History=h;this._ooOvertypeUndoEpoch=1;this.started=false;}
CDocument.prototype.IsActionStarted=function(){return this.started};
const AscDFH={historydescription_Document_AddLetter:167,historydescription_Document_AddLetterUnion:301,historyitem_TableId_Description:555};
vm.runInNewContext(src.replace(old,next),{CDocument,AscDFH,Date:FakeDate});
function history(){return {Points:[],Index:-1,RecIndex:-1,SavedIndex:null,UserSavedIndex:null,UndoRedoInProgress:false,Is_On:()=>true}}
function enter(d,time){clock=time;const h=d.History;if(h.Index>=0)h.Points[h.Index].Additional={};
  h.Points.push({State:{},Time:time,Description:167,Additional:{},Items:[{Data:{Type:7}},{Data:{Type:9}}]});
  h.Index=h.Points.length-1;h.RecIndex=h.Index;d.started=true;d._ooMarkOvertypeUndoPoint();d.started=false;d._ooFinishOvertypeUndoRC3();}
function test(label,stamps,adjust,expected){const h=history(),d=new CDocument(h);stamps.forEach((t,i)=>{if(adjust)adjust(h,d,i);enter(d,t)});assert.equal(h.Points.length,expected,label);console.log('PASS',label)}
test('manual pace 2.5s between characters groups as one Undo point',[1000,3500,6000],null,1);
test('pause of 10.001 seconds prevents merge',[1000,11001],null,2);
test('navigation epoch keeps separate Undo point',[1000,3500],(_,d,i)=>{if(i===1)d._ooOvertypeUndoEpoch++},2);
test('save boundary keeps separate Undo point',[1000,3500],(h,_,i)=>{if(i===1)h.SavedIndex=0},2);
test('fast typing unaffected',[1000,1100,1200],null,1);
