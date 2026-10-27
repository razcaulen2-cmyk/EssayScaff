/* Real Body tutor, exact marks, shared trace and saved/unsaved context. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const [origin,artifacts,mode]=process.argv.slice(2),before=mode==='before';
const corpus=JSON.parse(fs.readFileSync(path.join(__dirname,'body_feedback_repair_cases.json'),'utf8'));
const password=process.env.ESSAYSCAFF_BODY_PASSWORD;
let browser,socket,sessionId,nextId=0;const pending=new Map(),errors=[],records={},contextChecks=[];
const delay=ms=>new Promise(r=>setTimeout(r,ms));
function send(method,params={},root=false){const id=++nextId;return new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error(method+' timeout')),35000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params,...(!root&&sessionId?{sessionId}:{})}));});}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true,userGesture:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function wait(expression,label){for(let i=0;i<240;i++){if(await evaluate(expression))return;await delay(100);}throw Error('wait: '+label);}
async function click(selector){await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);}
async function fill(selector,text){await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.value=${JSON.stringify(text)};e.dispatchEvent(new Event('input',{bubbles:true}));})()`);}
async function shot(name,selector='.feedback-card',margin=100){await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.style.scrollMarginTop='${margin}px';e.scrollIntoView({block:'start'});return new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));})()`);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(artifacts,mode+'-'+name+'.png'),Buffer.from(r.data,'base64'));}
async function login(role){const old=await evaluate('performance.timeOrigin');await send('Page.navigate',{url:origin+'/login'});await wait(`performance.timeOrigin!==${old}&&document.readyState==='complete'&&!!document.querySelector('#username')`,'login page');await fill('#username','body_'+role);await fill('#password',password);await click('form button[type="submit"]');await wait(role==='student'?`location.pathname==='/'&&typeof state!=='undefined'&&!state.restoring`:`location.pathname==='/teacher'&&typeof showTeacherView==='function'`,'login '+role);}
async function analyze(){await click('#analyze-button');await wait(`!!state.analyses.BODY&&state.analysisSnapshots.BODY===analysisSnapshot('BODY')`,'current Body');return evaluate('state.analyses.BODY');}
async function write(stage,text){await click(`[data-stage="${stage}"]`);await fill('#stage-text',text);}
async function save(){await click('#save-button');await wait(`!state.saving&&document.querySelector('#save-status').textContent==='Draft saved'`,'saved draft');}
async function reload(){const old=await evaluate('performance.timeOrigin');await send('Page.reload');await wait(`performance.timeOrigin!==${old}&&typeof state!=='undefined'&&!state.restoring`,'restored page');await click('[data-app-link="workspace"]');}
async function openAssignment(title){await click('[data-app-link="assignments"]');await wait(`Array.from(document.querySelectorAll('#available-assignment-list button')).some(b=>b.closest('li').textContent.includes(${JSON.stringify(title)}))`,'available task');await evaluate(`Array.from(document.querySelectorAll('#available-assignment-list button')).find(b=>b.closest('li').textContent.includes(${JSON.stringify(title)})).click()`);await click('#open-assignment-workspace');await wait(`!state.restoring&&state.assignmentId!==null`,'assignment restored');}
(async()=>{
 browser=spawn(process.env.CHROME_PATH||'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(artifacts,'chrome-profile'),'about:blank'],{stdio:['ignore','ignore','pipe']});
 const ws=await new Promise((resolve,reject)=>{let s='';browser.stderr.on('data',b=>{s+=b;const m=/DevTools listening on (ws:\/\/\S+)/.exec(s);if(m)resolve(m[1]);});browser.on('error',reject);});socket=new WebSocket(ws);await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});
 socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description));else if(m.method==='Page.javascriptDialogOpening')send('Page.handleJavaScriptDialog',{accept:true}).catch(err=>errors.push(String(err)));};
 const target=await send('Target.createTarget',{url:'about:blank'},true);sessionId=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true},true)).sessionId;await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
 await login('student');await click('[data-app-link="workspace"]');await fill('#assignment-topic',corpus.assignment_topic);await fill('#focus-terms',corpus.focus_terms.join(', '));
 await evaluate(`window.__analysisCalls=0;window.__persistenceCalls=0;const originalFetch=window.fetch;window.fetch=(...args)=>{if(String(args[0])==='/api/analyze-stage')window.__analysisCalls++;if(args[1]?.method==='POST'&&['/api/drafts','/api/revisions','/api/submissions'].includes(String(args[0])))window.__persistenceCalls++;return originalFetch(...args);};`);
 for(const [id,text] of Object.entries(corpus.cases)){
   await write('INTRODUCTION',id==='B08'?'':corpus.introduction);await write('BODY',text);const result=await analyze();
   const model=await evaluate('studentFeedbackPresentation(state.analyses.BODY)'),trace=result.research_trace.stages.BODY;
   const marks=await evaluate(`Array.from(document.querySelectorAll('#tutor-evidence mark'),e=>e.textContent)`);
   records[id]={text,analysis:result.analysis,feedback:result.feedback,decision:trace.feedback_decisions,presentation:model,marks,input_sections:trace.input_sections};
   if(!before){
     const metadata=trace.feedback_decisions.instructional_feedback;assert.ok(metadata,'Body instructional record '+id);assert.deepEqual(model.instructional_feedback,metadata);
     const item=metadata.items[0];assert.deepEqual(marks,(item?.highlight_spans||[]).map(s=>s.text),'exact actual tutor marks '+id);
     if(id==='B04'){assert.deepEqual(metadata.strengths,[]);assert.equal(await evaluate(`document.querySelector('#tutor-working-section').hidden`),true,'keyword list receives no lexical-match praise');}
     assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('#editor-mirror mark'),e=>e.textContent)`),marks,'editor/tutor marks '+id);
     if(metadata.selection_status==='NO_SUPPORTED_CONCERN_SELECTED'){
       assert.equal(model.writing_dimension,null);assert.equal(model.teaching_content_source,null);assert.equal(model.tutor_items.length,1);
       assert.equal(await evaluate(`document.querySelector('#tutor-task-section').hidden`),true,'neutral never forces a task');assert.equal(marks.length,0);
     }
     const calls=await evaluate('__analysisCalls'),original=JSON.stringify(result);const report=await evaluate('buildFullAnalysisReport(state.analyses.BODY)');assert.ok(report.includes('instructional_feedback'));assert.equal(await evaluate('__analysisCalls'),calls);assert.equal(await evaluate('JSON.stringify(state.analyses.BODY)'),original);
   }
   if(['B01','B02','B03','B04','B05','B07'].includes(id))await shot(id+'-desktop');
 }
 const analysisOnlyPersistenceCalls=await evaluate('__persistenceCalls');assert.equal(analysisOnlyPersistenceCalls,0,'analysis-only Body examples never persist writing');
 // Controlled saves: current unsaved Introduction is used, then a reload restores the saved one.
 await write('INTRODUCTION',corpus.keyword_introduction);await write('BODY',corpus.cases.B01);await save();
 let result=await analyze();assert.equal(result.research_trace.stages.BODY.input_sections.introduction,corpus.keyword_introduction);contextChecks.push('saved keyword-list Introduction compared exactly');
 await write('INTRODUCTION',corpus.introduction);await click('[data-stage="BODY"]');assert.equal(await evaluate('!!state.analyses.BODY'),false,'editing Introduction invalidates Body');
 result=await analyze();assert.equal(result.research_trace.stages.BODY.input_sections.introduction,corpus.introduction);contextChecks.push('unsaved Introduction edit compared exactly; old Body invalidated');
 await reload();await click('[data-stage="BODY"]');result=await analyze();assert.equal(result.research_trace.stages.BODY.input_sections.introduction,corpus.keyword_introduction);contextChecks.push('reload without saving restores the saved keyword-list Introduction');
 await write('INTRODUCTION',corpus.introduction);await save();await reload();await click('[data-stage="BODY"]');result=await analyze();assert.equal(result.research_trace.stages.BODY.input_sections.introduction,corpus.introduction);contextChecks.push('save then reload uses corrected Introduction');
 await openAssignment('Body context A');await click('[data-stage="BODY"]');result=await analyze();assert.equal(result.research_trace.stages.BODY.input_sections.introduction,corpus.introduction);
 await openAssignment('Body context B');await click('[data-stage="BODY"]');assert.equal(await evaluate('!!state.analyses.BODY'),false);result=await analyze();assert.equal(result.research_trace.stages.BODY.input_sections.introduction,'The second assignment has a different saved Introduction.');
 await openAssignment('Body context A');await click('[data-stage="BODY"]');result=await analyze();assert.equal(result.research_trace.stages.BODY.input_sections.introduction,corpus.introduction);contextChecks.push('A → B → A assignment switching uses each saved Introduction; no prior Body survives');
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth'));await shot('B01-mobile');
 if(!before){
   await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});await click('[data-process-id="feedback-decision"]');await click('[data-evidence-section="engine:overview"] > summary');await shot('student-body-trace','[data-six-trait-trace]',160);
   await click('form[action="/logout"] button');await wait(`location.pathname==='/login'`,'logout');await login('teacher');await click('a[href="/teacher/research-inspector"]');await wait(`document.querySelector('#run-research-analysis')?.disabled===false`,'inspector ready');
   for(const [id,text] of Object.entries(corpus.cases)){
     // A textarea normalizes CRLF to LF. Compare the SAME analyzed string;
     // direct-API Unicode/CRLF preservation has separate exact-offset tests.
     const payload={stage_id:'BODY',assignment_topic:corpus.assignment_topic,focus_terms:corpus.focus_terms,body_text:records[id].analysis.input_text,introduction_text:id==='B08'?'':corpus.introduction};
     const other=await evaluate(`(async()=>{const r=await fetch('/api/research-inspector/analyze',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':document.querySelector('meta[name="csrf-token"]').content},body:JSON.stringify(${JSON.stringify(payload)})});if(!r.ok)throw Error(r.status);return r.json();})()`);
     assert.deepEqual(other.research_trace.stages.BODY.feedback_decisions.instructional_feedback,records[id].decision.instructional_feedback,'student/professor same record '+id);
   }
   await evaluate(`document.querySelector('#research-stage').value='BODY';document.querySelector('#research-stage').dispatchEvent(new Event('change',{bubbles:true}));`);await fill('#research-topic',corpus.assignment_topic);await fill('#research-focus-terms',corpus.focus_terms.join(', '));await fill('#research-introduction',corpus.introduction);await fill('#research-body',corpus.cases.B01);await click('#run-research-analysis');await wait(`document.querySelector('#copy-research-json')?.disabled===false`,'professor neutral result');await click('.research-process-button[data-index="7"]');await shot('professor-neutral-trace','[data-six-trait-trace]');
   const neutralText=await evaluate(`document.querySelector('[data-six-trait-trace]').textContent`);assert.ok(neutralText.includes('NO_SUPPORTED_CONCERN_SELECTED')&&neutralText.includes(records.B01.presentation.displayed_strengths.split('\n')[0]));
   await fill('#research-body',corpus.cases.B03);await click('#run-research-analysis');await wait(`document.querySelector('#copy-research-json')?.disabled===false`,'professor selected result');await click('.research-process-button[data-index="7"]');
   const concernText=await evaluate(`document.querySelector('[data-six-trait-trace]').textContent`),actualTutor=records.B03.decision.instructional_feedback.items[0];
   assert.ok(concernText.includes(actualTutor.prepared_guidance.noticed)&&concernText.includes(actualTutor.prepared_guidance.task)&&concernText.includes(actualTutor.lesson_id),'professor shows actual prepared tutor wording as well as backend feedback');
   await shot('professor-concern-trace','[data-six-trait-trace]');
   await evaluate(`(()=>{const d=Array.from(document.querySelectorAll('[data-six-trait-trace] details')).find(d=>d.querySelector('summary').textContent.startsWith('Primary Feedback'));d.open=true;d.dataset.bodyHighlightEvidence='true';})()`);await shot('professor-highlight-provenance','[data-body-highlight-evidence]');
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(artifacts,mode+'-outputs.json'),JSON.stringify({records,contextChecks,analysisOnlyPersistenceCalls,javascriptErrors:errors},null,2));console.log(JSON.stringify({mode,cases:Object.keys(records).length,contextChecks,analysisOnlyPersistenceCalls,branches:Object.fromEntries(Object.entries(records).map(([k,r])=>[k,r.decision.fields['Primary Feedback'].selection_branch])),javascriptErrors:errors},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(socket?.readyState===WebSocket.OPEN){try{await send('Browser.close',{},true);}catch(_){}socket.close();}browser?.kill();});
