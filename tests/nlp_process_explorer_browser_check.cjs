/* Actual Chrome process navigation, retained evidence, exports and snapshot safety. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const [origin,artifacts,mode]=process.argv.slice(2),before=mode==='before';
const corpus=JSON.parse(fs.readFileSync(path.join(__dirname,'nlp_process_explorer_cases.json'),'utf8'));
const password=process.env.ESSAYSCAFF_EXPLORER_PASSWORD;
let browser,socket,sessionId,nextId=0;const pending=new Map(),errors=[],checks=[],stable_records={};
const delay=ms=>new Promise(r=>setTimeout(r,ms));
function send(method,params={},root=false){const id=++nextId;return new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error(method+' timeout')),35000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params,...(!root&&sessionId?{sessionId}:{})}));});}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true,userGesture:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function wait(expression,label){for(let i=0;i<240;i++){if(await evaluate(expression))return;await delay(100);}throw Error('wait: '+label);}
async function click(selector){await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);}
async function fill(selector,text){await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.value=${JSON.stringify(text)};e.dispatchEvent(new Event('input',{bubbles:true}));})()`);}
async function screenshot(name,selector='#nlp-transparency'){await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.style.scrollMarginTop='90px';e.scrollIntoView({block:'start'});return new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));})()`);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(artifacts,mode+'-'+name+'.png'),Buffer.from(r.data,'base64'));}
async function analyze(stage,text){await click(`[data-stage="${stage}"]`);await fill('#stage-text',text);await click('#analyze-button');await wait(`!!state.analyses.${stage}&&state.analysisSnapshots.${stage}===analysisSnapshot('${stage}')`,'analyze '+stage);return evaluate(`state.analyses.${stage}`);}
function stable(value){if(Array.isArray(value))return value.map(stable);if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,(/_ms$/.test(k)||k==='timings_ms')?'MEASURED_RUNTIME_RETAINED':stable(v)]));return value;}
async function openAssignment(title){await click('[data-app-link="assignments"]');await wait(`Array.from(document.querySelectorAll('#available-assignment-list button')).some(b=>b.closest('li').textContent.includes(${JSON.stringify(title)}))`,'task list');await evaluate(`Array.from(document.querySelectorAll('#available-assignment-list button')).find(b=>b.closest('li').textContent.includes(${JSON.stringify(title)})).click()`);await click('#open-assignment-workspace');await wait(`!state.restoring&&state.assignmentId!==null`,'assignment restore');}
(async()=>{
 browser=spawn(process.env.CHROME_PATH||'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(artifacts,'chrome-profile'),'about:blank'],{stdio:['ignore','ignore','pipe']});
 const ws=await new Promise((resolve,reject)=>{let s='';browser.stderr.on('data',b=>{s+=b;const m=/DevTools listening on (ws:\/\/\S+)/.exec(s);if(m)resolve(m[1]);});browser.on('error',reject);});socket=new WebSocket(ws);await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});
 socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description));else if(m.method==='Page.javascriptDialogOpening')send('Page.handleJavaScriptDialog',{accept:true}).catch(err=>errors.push(String(err)));};
 const target=await send('Target.createTarget',{url:'about:blank'},true);sessionId=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true},true)).sessionId;await send('Page.enable');await send('Runtime.enable');await send('Browser.grantPermissions',{origin,permissions:['clipboardReadWrite','clipboardSanitizedWrite']},true);await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await send('Page.navigate',{url:origin+'/login'});await wait(`!!document.querySelector('#username')`,'login');await fill('#username','explorer_student');await fill('#password',password);await click('form button[type="submit"]');await wait(`location.pathname==='/'&&typeof state!=='undefined'&&!state.restoring`,'workspace');await click('[data-app-link="workspace"]');await fill('#assignment-topic',corpus.assignment_topic);await fill('#focus-terms',corpus.focus_terms.join(', '));
 await evaluate(`window.__explorerCalls=[];const previousFetch=window.fetch;window.fetch=(...args)=>{__explorerCalls.push({url:String(args[0]),method:args[1]?.method||'GET'});return previousFetch(...args);};`);
 for(const [stage,text] of [['INTRODUCTION',corpus.introduction],['BODY',corpus.body],['CONCLUSION',corpus.conclusion]]){
   const result=await analyze(stage,text),original=JSON.stringify(result),calls=await evaluate('__explorerCalls.length');
   const reports=await evaluate(`(()=>{const records=[];buildFullAnalysisReport(state.analyses.${stage},records);return records;})()`);
   stable_records[stage]={analysis:stable(result.analysis),feedback:stable(result.feedback),export_records:stable(reports)};
   if(before){await click('[data-view-mode="technical"]');await click('#nlp-tab-nlp');await evaluate(`document.querySelector('[data-sub-tab="nlp:tokens"]').click()`);}
   else{
     assert.equal(await evaluate(`document.querySelectorAll('.transparency-tabs,.transparency-subtabs,.transparency-view-mode').length`),0,'no obsolete navigation');
     const processes=await evaluate('transparencyTabsApi.processes.map(p=>({id:p.id,title:p.title,status:p.execution.status}))');assert.ok(processes.length>=15);assert.equal(new Set(processes.map(p=>p.id)).size,processes.length);
     assert.equal(await evaluate(`document.querySelectorAll('[data-evidence-section]').length`),45,'all original technical sections retained');
     for(const process of processes){
       await click(`[data-process-id="${process.id}"]`);
       assert.equal(await evaluate(`document.querySelector('[data-process-id="${process.id}"]').getAttribute('aria-current')`),'step');
       const visible=await evaluate(`Array.from(document.querySelectorAll('[data-explorer-process]')).filter(p=>!p.hidden).map(p=>p.dataset.explorerProcess)`);assert.deepEqual(visible,[process.id]);
       const content=await evaluate(`document.querySelector('[data-explorer-process="${process.id}"]').textContent`);
       for(const label of ['Process Overview','Actual Input','Visual Representation','Actual Recorded Evidence','How the Process Works','Output and Next Destination','Implementation Source','Limitations','Developer Evidence'])assert.ok(content.includes(label),stage+' '+process.id+' '+label);
       assert.equal(await evaluate(`document.querySelectorAll('[data-explorer-toggle]').length`),0,'no evidence-revealing toggle');
       assert.equal(await evaluate(`document.querySelector('[data-explorer-developer="${process.id}"]').tagName`),'SECTION');
     }
     await click('[data-process-id="tokens"]');await click('#explorer-next-process');assert.notEqual(await evaluate('transparencyTabsApi.activeProcessId'),'tokens');await click('#explorer-previous-process');assert.equal(await evaluate('transparencyTabsApi.activeProcessId'),'tokens');
     assert.equal(await evaluate(`document.querySelector('[data-explorer-metric="stage"]').textContent`),stage);
     assert.ok(await evaluate(`document.querySelector('[data-explorer-metric="fingerprint"]').textContent.includes(${JSON.stringify(stage)})`));
     if(stage==='BODY'){assert.equal(result.research_trace.stages.BODY.feedback_decisions.selection_status,'NO_SUPPORTED_CONCERN_SELECTED');assert.equal(await evaluate(`document.querySelector('#tutor-why-section').hidden&&document.querySelector('#tutor-task-section').hidden`),true);await click('[data-process-id="trait-mapping"]');assert.ok(await evaluate(`document.querySelector('[data-explorer-process="trait-mapping"]').textContent.includes('NO_SUPPORTED_CONCERN_SELECTED')`));}
     if(stage==='INTRODUCTION')assert.equal(processes.find(p=>p.id==='wordnet').status,'SKIPPED','direct WordNet is skipped when no earlier stage exists');
     else assert.equal(processes.find(p=>p.id==='wordnet').status,'EXECUTED','nested cross-stage WordNet comparisons are recorded');
     if(stage==='INTRODUCTION'){
       await click('[data-process-id="trait-mapping"]');
       assert.equal(processes.find(p=>p.id==='trait-mapping').status,'NOT_APPLICABLE','neutral Introduction mapping is not presented as unavailable');
       const mapping=await evaluate(`document.querySelector('[data-explorer-process="trait-mapping"]').textContent`);
       assert.ok(mapping.includes('NEUTRAL_OBSERVATION'),'neutral review status is stated');
       assert.ok(mapping.includes('HELP-INTRO-EXPLAIN-POINT'),'the retained prepared explanation item keeps its recorded lesson ID');
       await screenshot('INTRODUCTION-neutral-mapping-desktop','.explorer-detail-host');
       await click('[data-process-id="wordnet"]');await screenshot('INTRODUCTION-wordnet-skipped-desktop','.explorer-detail-host');
       await click('[data-process-id="highlight-evidence"]');await screenshot('INTRODUCTION-highlight-offsets-desktop','.explorer-detail-host');
       await click('[data-process-id="dependencies"]');
       await click('[data-evidence-section="nlp:dependencies"] > summary');
       await screenshot('INTRODUCTION-developer-evidence-desktop','[data-explorer-developer="dependencies"]');
     }
     if(stage==='BODY'){await click('[data-process-id="trait-mapping"]');await screenshot('BODY-neutral-mapping-desktop','.explorer-detail-host');}
     if(stage==='CONCLUSION'){await click('[data-process-id="cross-stage"]');await screenshot('CONCLUSION-comparisons-desktop','.explorer-detail-host');}
     await click('[data-process-id="tokens"]');await evaluate(`document.querySelector('.explorer-detail-host').scrollIntoView({block:'start'})`);checks.push({stage,processes});
   }
   await screenshot(stage+'-desktop');await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
   assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),stage+' mobile overflow');
   if(!before){assert.equal(await evaluate(`document.querySelectorAll('#nlp-process-select,.explorer-navigation,.explorer-mobile-navigation').length`),0,'obsolete vertical navigation removed');await click('[data-process-id="dependencies"]');assert.equal(await evaluate('transparencyTabsApi.activeProcessId'),'dependencies');}
   await screenshot(stage+'-mobile');await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
   assert.equal(await evaluate(`JSON.stringify(state.analyses.${stage})`),original);assert.equal(await evaluate('__explorerCalls.length'),calls,'all inspection reuses cached analysis');
   const copied=await evaluate(`buildFullAnalysisReport(state.analyses.${stage})`);await click('#copy-full-analysis');await wait(`document.querySelector('#analysis-copy-status').textContent==='Full analysis copied.'`,'clipboard');assert.equal((await evaluate('navigator.clipboard.readText()')).replace(/\r\n/g,'\n'),copied.replace(/\r\n/g,'\n'));
 }
 if(!before){
   await click('[data-stage="INTRODUCTION"]');assert.equal(await evaluate('state.analyses.INTRODUCTION.stage_id'),'INTRODUCTION');assert.equal(await evaluate('transparencyTabsApi.activeProcessId'),'dependencies','stage selection remembered');
   await fill('#stage-text',corpus.introduction+' Updated.');assert.equal(await evaluate(`document.querySelector('#copy-full-analysis').disabled`),true);assert.notEqual(await evaluate(`document.querySelector('#nlp-transparency-content').dataset.status`),'CURRENT');
   await click('#save-button');await wait(`!state.saving`,'save practice before switch');
   await openAssignment('Explorer assignment A');await click('[data-stage="BODY"]');await click('#analyze-button');await wait(`!!state.analyses.BODY&&state.analysisSnapshots.BODY===analysisSnapshot('BODY')`,'assigned Body A');assert.ok(await evaluate(`document.querySelector('[data-explorer-metric="assignment"]').textContent.includes('Explorer assignment A')`));
   await openAssignment('Explorer assignment B');assert.equal(await evaluate('!!state.analyses.BODY'),false);assert.equal(await evaluate(`document.querySelector('#copy-full-analysis').disabled`),true);await click('[data-stage="BODY"]');await click('#analyze-button');await wait(`!!state.analyses.BODY&&state.analysisSnapshots.BODY===analysisSnapshot('BODY')`,'assigned Body B');assert.ok(await evaluate(`document.querySelector('[data-explorer-metric="assignment"]').textContent.includes('Explorer assignment B')`));assert.ok(await evaluate(`state.analyses.BODY.research_trace.stages.BODY.input_sections.introduction.endsWith('Assignment B context.')`));
   checks.push({snapshotAndAssignmentSwitches:'PASS'});
 }
 const section_mapping=before?null:await evaluate('NlpProcessExplorer.sectionOwners');
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(artifacts,mode+'-outputs.json'),JSON.stringify({stable_records,checks,section_mapping,javascriptErrors:errors},null,2));console.log(JSON.stringify({mode,stages:Object.keys(stable_records),checks,javascriptErrors:errors},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(socket?.readyState===WebSocket.OPEN){try{await send('Browser.close',{},true);}catch(_){}socket.close();}browser?.kill();});
