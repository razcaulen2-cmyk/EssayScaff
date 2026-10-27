/* Actual Chrome snapshots and consistency checks; no installed test packages. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const [origin,artifacts,mode]=process.argv.slice(2),before=mode==='before';
const samples=JSON.parse(fs.readFileSync(path.join(__dirname,'introduction_ideas_cases.json'),'utf8'));
const password=process.env.ESSAYSCAFF_IDEAS_PASSWORD;
let browser,socket,sessionId,nextId=0;
const pending=new Map(),errors=[],records={};
const delay=ms=>new Promise(r=>setTimeout(r,ms));
function send(method,params={},root=false){const id=++nextId;return new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error(method+' timeout')),30000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params,...(!root&&sessionId?{sessionId}:{})}));});}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true,userGesture:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function wait(expression,label){for(let i=0;i<200;i++){if(await evaluate(expression))return;await delay(100);}throw Error('wait: '+label);}
async function click(selector){await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);}
async function fill(selector,text){await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.value=${JSON.stringify(text)};e.dispatchEvent(new Event('input',{bubbles:true}));})()`);}
async function screenshot(name){await evaluate(`new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))`);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(artifacts,name+'.png'),Buffer.from(r.data,'base64'));}
async function login(role){const old=await evaluate('performance.timeOrigin');await send('Page.navigate',{url:origin+'/login'});await wait(`performance.timeOrigin!==${old}&&document.readyState==='complete'&&!!document.querySelector('#username')`,'login page');await fill('#username','ideas_'+role);await fill('#password',password);await click('form button[type="submit"]');await wait(role==='student'?`location.pathname==='/'&&typeof state!=='undefined'&&!state.restoring`:`location.pathname==='/teacher'&&typeof showTeacherView==='function'`,'login '+role);}
(async()=>{
 browser=spawn(process.env.CHROME_PATH||'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(artifacts,'chrome-profile'),'about:blank'],{stdio:['ignore','ignore','pipe']});
 const ws=await new Promise((resolve,reject)=>{let s='';browser.stderr.on('data',b=>{s+=b;const m=/DevTools listening on (ws:\/\/\S+)/.exec(s);if(m)resolve(m[1]);});browser.on('error',reject);});socket=new WebSocket(ws);await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});
 socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description));else if(m.method==='Page.javascriptDialogOpening')send('Page.handleJavaScriptDialog',{accept:true}).catch(err=>errors.push(String(err)));};
 const target=await send('Target.createTarget',{url:'about:blank'},true);sessionId=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true},true)).sessionId;await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
 await login('student');await click('[data-app-link="workspace"]');await fill('#assignment-topic',samples.assignment_topic);await fill('#focus-terms',samples.focus_terms.join(', '));
 await evaluate(`window.__calls=0;const originalFetch=window.fetch;window.fetch=(...args)=>{if(String(args[0])==='/api/analyze-stage')window.__calls++;return originalFetch(...args);};`);
 for(const [id,text] of Object.entries(samples.cases)){
   await fill('#stage-text',text);await click('#analyze-button');await wait(`state.analysisSnapshots.INTRODUCTION===analysisSnapshot('INTRODUCTION')&&!!state.analyses.INTRODUCTION`,'analyze '+id);
   const result=await evaluate(`state.analyses.INTRODUCTION`),model=await evaluate(`studentFeedbackPresentation(state.analyses.INTRODUCTION)`);
   const decision=result.research_trace.stages.INTRODUCTION.feedback_decisions;
    records[id]={text,branch:decision.fields['Primary Feedback'].selection_branch,status:model.status,trait:model.writing_dimension,skill:model.writing_skill,lesson:model.teaching_content_source?.content_id??null,guidance:model.displayed_guidance,reason_status:result.analysis.reason_clause_evidence.status,central_count:result.analysis.observable_structure.central_direction_candidates.length,development_count:result.analysis.development_evidence.predicate_count,events:result.analysis.rule_evidence.map(e=>e.rule_id),instructional_feedback:decision.instructional_feedback||null,backend_feedback:Object.fromEntries(['Current Goal','Primary Feedback',"What's Working",'Needs Attention','Next Step'].map(field=>[field,result.feedback[field]])),displayed_strengths:model.displayed_strengths||'',displayed_highlights:await evaluate(`Array.from(document.querySelectorAll('#tutor-evidence mark'),e=>e.textContent)`)};
   if(!before){
     assert.ok(decision.instructional_feedback,'recorded backend mapping '+id);
      assert.equal(model.tutor_items[0].lesson_id,decision.instructional_feedback.items[0]?.lesson_id);
      assert.deepEqual(model.instructional_feedback,decision.instructional_feedback);
      const neutral=model.status==='NEUTRAL_OBSERVATION';
      assert.equal(neutral,['intro_ideas_point_and_reason','intro_ideas_review_details'].includes(records[id].branch),'recorded neutral branch '+id);
      if(neutral){
        assert.equal(model.writing_dimension,null,'neutral branch has no corrective trait '+id);
        assert.equal(model.writing_skill,null,'neutral branch has no corrective skill '+id);
        assert.equal(model.teaching_content_source,null,'neutral branch displays no teaching source '+id);
        assert.equal(model.tutor_items[0].neutral_result,true,'neutral result flag '+id);
        assert.deepEqual(Object.keys(model.displayed_guidance),['What I noticed',...(records[id].displayed_strengths?["What's working"]:[])],'neutral guidance only '+id);
        assert.deepEqual(records[id].displayed_highlights,[],'neutral tutor shows no error marks '+id);
        assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('#editor-mirror mark'),e=>e.textContent)`),[],'neutral editor shows no marks '+id);
        for(const section of ['tutor-evidence-section','tutor-why-section','tutor-task-section']) assert.equal(await evaluate(`document.getElementById(${JSON.stringify(section)}).hidden`),true,'neutral hides '+section+' '+id);
      }else{
        const marks=decision.instructional_feedback.items[0].highlight_spans.map(span=>span.text);
        assert.deepEqual(records[id].displayed_highlights,marks,'actual tutor marks '+id);
        assert.deepEqual(await evaluate(`Array.from(document.querySelectorAll('#editor-mirror mark'),e=>e.textContent)`),marks,'actual editor marks '+id);
        assert.equal(await evaluate(`document.getElementById('tutor-task-section').hidden`),!model.tutor_items[0].task_text,'corrective task reflects recorded task '+id);
      }
      assert.equal(records[id].displayed_strengths,decision.instructional_feedback.items[0].working_text,'actual strength '+id);
      const guided=await evaluate(`({state:document.querySelector('#guided-state-label').dataset.state,label:document.querySelector('#guided-state-label').textContent,reviewHidden:document.querySelector('#guided-review-suggestions').hidden,continueHidden:document.querySelector('#guided-continue-to-body').hidden,anywayHidden:document.querySelector('#guided-continue-anyway').hidden,title:document.querySelector('#stage-progress-title').textContent,badge:document.querySelector('#stage-progress-badge').dataset.state,progressReviewHidden:document.querySelector('#stage-progress-review').hidden})`);
      records[id].guided=guided;
      if(neutral){
        assert.equal(guided.state,'NEUTRAL','neutral current result does not claim a concern '+id);
        assert.equal(guided.label,'No Specific Issue Detected');
        assert.equal(guided.reviewHidden,true,'no unsupported Review Suggestions '+id);
        assert.equal(guided.continueHidden,false,'Continue to Body stays accessible '+id);
        assert.equal(guided.anywayHidden,true);
        assert.equal(guided.title,'No Specific Writing Issue Detected');
        assert.equal(guided.badge,'NO_ISSUE');
        assert.equal(guided.progressReviewHidden,true,'Stage Progress offers no Review Writing for neutral '+id);
      }else{
        assert.equal(guided.state,'REVIEW_SUGGESTED','genuine concern retains Review Suggested '+id);
        assert.equal(guided.reviewHidden,false);
        assert.equal(guided.continueHidden,true);
        assert.equal(guided.anywayHidden,false);
        assert.equal(guided.title,'Review Suggested');
        assert.equal(guided.badge,'REVIEW_SUGGESTED');
        assert.equal(guided.progressReviewHidden,false,'Review Writing stays available '+id);
      }
     const original=JSON.stringify(result),calls=await evaluate('__calls');
     const report=await evaluate(`buildFullAnalysisReport(state.analyses.INTRODUCTION)`);
     assert.ok(report.includes('instructional_feedback')&&report.includes(records[id].branch));
     assert.equal(await evaluate('__calls'),calls);assert.equal(await evaluate(`JSON.stringify(state.analyses.INTRODUCTION)`),original);
     if(['T01','T03','T04','T05','T12','T13'].includes(id))assert.notEqual(model.writing_skill,'Check Your Reason');
   }
   if(['T01','T03','T04','T05'].includes(id)){await evaluate(`document.querySelector('.feedback-card').scrollIntoView({block:'center'})`);await screenshot(mode+'-'+id+'-desktop');}
   if(['T01','T04'].includes(id)){await evaluate(`document.querySelector('#stage-progress').scrollIntoView({block:'center'})`);await screenshot(mode+'-'+id+'-stage-progress');}
 }
 await fill('#stage-text',samples.cases.T04);await click('#analyze-button');await wait(`state.analysisSnapshots.INTRODUCTION===analysisSnapshot('INTRODUCTION')`,'mobile current');await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await evaluate(`document.querySelector('.feedback-card').scrollIntoView({block:'center'})`);assert.ok(await evaluate(`document.documentElement.scrollWidth<=innerWidth`));await screenshot(mode+'-T04-mobile');
 if(!before){
   assert.equal(records.T04.branch,records.T05.branch);assert.equal(records.T04.skill,records.T05.skill);
   await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
    await click('[data-process-id="feedback-decision"]');await click('[data-evidence-section="engine:overview"] > summary');
   const traceCalls=await evaluate('__calls');
    await evaluate(`(()=>{const e=Array.from(document.querySelectorAll('[data-six-trait-trace]')).find(e=>e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0);if(!e)throw Error('visible 6+1 trace missing');const d=e.querySelector('details');if(d){d.open=true;d.dispatchEvent(new Event('toggle'));}e.style.scrollMarginTop='150px';e.scrollIntoView({block:'start'});})()`);
   assert.equal(await evaluate('__calls'),traceCalls,'opening recorded evidence never reruns analysis');await screenshot('after-student-framework-trace');
   await click('form[action="/logout"] button');await wait(`location.pathname==='/login'&&!!document.querySelector('#username')`,'student logout');
   await login('teacher');await click('a[href="/teacher/research-inspector"]');await wait(`document.querySelector('#run-research-analysis')?.disabled===false`,'inspector');
   for(const [id,text] of Object.entries(samples.cases)){
     const payload={stage_id:'INTRODUCTION',assignment_topic:samples.assignment_topic,focus_terms:samples.focus_terms,introduction_text:text};
     const other=await evaluate(`(async()=>{const r=await fetch('/api/research-inspector/analyze',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':document.querySelector('meta[name="csrf-token"]').content},body:JSON.stringify(${JSON.stringify(payload)})});if(!r.ok)throw Error(r.status);return r.json();})()`);
     assert.deepEqual(other.research_trace.stages.INTRODUCTION.feedback_decisions.instructional_feedback,records[id].instructional_feedback,'student/teacher mapping '+id);
   }
    await fill('#research-topic',samples.assignment_topic);await fill('#research-focus-terms',samples.focus_terms.join(', '));await fill('#research-introduction',samples.cases.T04);await click('#run-research-analysis');await wait(`document.querySelector('#copy-research-json')?.disabled===false`,'inspector result');await click('.research-process-button[data-index="7"]');await evaluate(`(()=>{const e=document.querySelector('[data-six-trait-trace]');e.style.scrollMarginTop='88px';e.scrollIntoView({block:'start'});})()`);await screenshot('after-professor-framework-trace');
    await evaluate(`(()=>{const d=document.querySelector('[data-six-trait-trace] details');d.open=true;d.style.scrollMarginTop='88px';d.scrollIntoView({block:'start'});})()`);await screenshot('after-professor-evidence-detail');
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(artifacts,mode+'-outputs.json'),JSON.stringify({records,javascriptErrors:errors},null,2));console.log(JSON.stringify({mode,cases:Object.keys(records).length,branches:Object.fromEntries(Object.entries(records).map(([k,r])=>[k,r.branch])),javascriptErrors:errors},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(socket?.readyState===WebSocket.OPEN){try{await send('Browser.close',{},true);}catch(_){}socket.close();}browser?.kill();});
