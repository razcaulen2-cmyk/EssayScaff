/* Actual Chrome verification for the Conclusion feedback correction; no installed test packages. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const [origin,artifacts]=process.argv.slice(2);
const password=process.env.ESSAYSCAFF_CONCLUSION_PASSWORD;
let browser,socket,sessionId,nextId=0;
const pending=new Map(),errors=[],records={};
const delay=ms=>new Promise(r=>setTimeout(r,ms));
function send(method,params={},root=false){const id=++nextId;return new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error(method+' timeout')),30000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params,...(!root&&sessionId?{sessionId}:{})}));});}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true,userGesture:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function wait(expression,label){for(let i=0;i<300;i++){if(await evaluate(expression))return;await delay(100);}throw Error('wait: '+label);}
async function click(selector){await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);}
async function fill(selector,text){await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.value=${JSON.stringify(text)};e.dispatchEvent(new Event('input',{bubbles:true}));})()`);}
async function screenshot(name){await evaluate(`new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))`);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(artifacts,name+'.png'),Buffer.from(r.data,'base64'));}
async function login(){await send('Page.navigate',{url:origin+'/login'});await wait(`document.readyState==='complete'&&!!document.querySelector('#username')`,'login page');await fill('#username','conclusion_student');await fill('#password',password);await click('form button[type="submit"]');await wait(`location.pathname==='/'&&typeof state!=='undefined'&&!state.restoring`,'student shell');}
const CASES={
 EXACT:{
  introduction:"Schools should turn a small part of their playgrounds into vegetable gardens because it can help students learn about science and develop responsibility. Through gardening activities, students can observe how plants grow and understand the importance of taking care of the environment. These experiences can make learning more practical while allowing students to enjoy both gardening and playing at school.",
  body:"A vegetable garden can help students learn about science. Students can observe how seeds grow and record changes in the plants. These activities give students a chance to practice what they learn in class.\n\nA school garden can also teach responsibility. For example, students can take turns watering the vegetables, removing weeds, and checking whether the plants are healthy. By completing these tasks regularly, students can learn to be responsible and understand the importance of caring for something.",
  conclusion:"In conclusion, schools should turn a small part of their playgrounds into vegetable gardens. These gardens can help students learn about science by observing how plants grow. Students can also develop responsibility by taking turns watering vegetables and caring for the plants.",
  expect:{branch:'conclusion_ideas_bring_together',neutral:true,primary:'HELP-CONCLUSION-BRING-TOGETHER'},
 },
 KEYWORD:{
  introduction:"Schools should turn a small part of their playgrounds into vegetable gardens because it can help students learn about science and develop responsibility. Through gardening activities, students can observe how plants grow and understand the importance of taking care of the environment. These experiences can make learning more practical while allowing students to enjoy both gardening and playing at school.",
  body:"A vegetable garden can help students learn about science. Students can observe how seeds grow and record changes in the plants. These activities give students a chance to practice what they learn in class.\n\nA school garden can also teach responsibility. For example, students can take turns watering the vegetables, removing weeds, and checking whether the plants are healthy. By completing these tasks regularly, students can learn to be responsible and understand the importance of caring for something.",
  conclusion:"schools, playgrounds, vegetable gardens, students, learning",
  expect:{branch:'conclusion_organization_bring_together',neutral:false,marks:true,primary:'HELP-CONCLUSION-LIST-ENDING'},
 },
 NEW_WORDS:{
  introduction:"Schools should turn a small part of their playgrounds into vegetable gardens because it can help students learn about science and develop responsibility. Through gardening activities, students can observe how plants grow and understand the importance of taking care of the environment. These experiences can make learning more practical while allowing students to enjoy both gardening and playing at school.",
  body:"A vegetable garden can help students learn about science. Students can observe how seeds grow and record changes in the plants. These activities give students a chance to practice what they learn in class.\n\nA school garden can also teach responsibility. For example, students can take turns watering the vegetables, removing weeds, and checking whether the plants are healthy. By completing these tasks regularly, students can learn to be responsible and understand the importance of caring for something.",
  conclusion:"Students should also sell the vegetables to buy new books.",
  expect:{branch:'conclusion_ideas_new_words',neutral:false,marks:false,primary:'HELP-CONCLUSION-EXPLAIN-NEW-WORDS'},
 },
 SECONDARY:{
  introduction:"Recess is important for young children.",
  body:"Students grow vegetables and learn responsibility.",
  conclusion:"Students should also sell the vegetables to buy new books.",
  expect:{branch:'conclusion_ideas_new_words',neutral:false,marks:false,primary:'HELP-CONCLUSION-EXPLAIN-NEW-WORDS',lesson:'HELP-CONCLUSION-BRING-TOGETHER'},
 },
};
const TOPIC='The School Garden Debate',FOCUS='schools, playgrounds, vegetable gardens, students, learning';
async function openAll(rootSelector){
 await evaluate(`(async()=>{const root=document.querySelector(${JSON.stringify(rootSelector)});if(!root)return;const walk=n=>[n,...Array.from(n.children).flatMap(walk)];for(let pass=0;pass<10;pass+=1){const closed=walk(root).filter(n=>n.tagName==='DETAILS'&&!n.open);if(!closed.length)break;for(const d of closed){d.open=true;d.dispatchEvent(new Event('toggle',{bubbles:true}));}}})()`);
 await delay(150);
}
(async()=>{
 browser=spawn(process.env.CHROME_PATH||'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(artifacts,'chrome-profile'),'about:blank'],{stdio:['ignore','ignore','pipe']});
 const ws=await new Promise((resolve,reject)=>{let s='';browser.stderr.on('data',b=>{s+=b;const m=/DevTools listening on (ws:\/\/\S+)/.exec(s);if(m)resolve(m[1]);});browser.on('error',reject);});
 socket=new WebSocket(ws);await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});
 socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description));else if(m.method==='Page.javascriptDialogOpening')send('Page.handleJavaScriptDialog',{accept:true}).catch(err=>errors.push(String(err)));};
 const target=await send('Target.createTarget',{url:'about:blank'},true);sessionId=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true},true)).sessionId;await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
 await login();await click('[data-app-link="workspace"]');
 await wait(`typeof state!=='undefined'&&!state.restoring&&!!document.querySelector('#stage-text')`,'workspace ready');
 await fill('#assignment-topic',TOPIC);await fill('#focus-terms',FOCUS);
 for(const [id,sample] of Object.entries(CASES)){
   await click('[data-stage="INTRODUCTION"]');await wait(`state.currentStage==='INTRODUCTION'`,'intro tab');
   await fill('#stage-text',sample.introduction);
   await click('[data-stage="BODY"]');await wait(`state.currentStage==='BODY'`,'body tab');
   await fill('#stage-text',sample.body);
   await click('[data-stage="CONCLUSION"]');await wait(`state.currentStage==='CONCLUSION'`,'conclusion tab');
   await fill('#stage-text',sample.conclusion);
   await evaluate(`window.__calls=0;if(!window.__counted){window.__counted=true;const originalFetch=window.fetch;window.fetch=(...args)=>{if(String(args[0])==='/api/analyze-stage')window.__calls++;return originalFetch(...args);};}`);
   await click('#analyze-button');
   await wait(`!!state.analyses.CONCLUSION&&state.analysisSnapshots.CONCLUSION===analysisSnapshot('CONCLUSION')&&!state.tutorAnalysisRunning`,'analyze '+id);
   const result=JSON.parse(await evaluate(`JSON.stringify(state.analyses.CONCLUSION)`));
   const decision=result.research_trace.stages.CONCLUSION.feedback_decisions.fields['Primary Feedback'];
   assert.equal(decision.selection_branch,sample.expect.branch,'recorded branch '+id);
   const model=JSON.parse(await evaluate(`JSON.stringify(studentFeedbackPresentation(state.analyses.CONCLUSION))`));
   const dom=JSON.parse(await evaluate(`JSON.stringify({
     tutorFocus:document.querySelector('#feedback-writing-focus').textContent,
     tutorFocusHidden:document.querySelector('#feedback-writing-focus').hidden,
     evidenceHidden:document.querySelector('#tutor-evidence-section').hidden,
     whyHidden:document.querySelector('#tutor-why-section').hidden,
     taskHidden:document.querySelector('#tutor-task-section').hidden,
     workingHidden:document.querySelector('#tutor-working-section').hidden,
     workingText:document.querySelector('#tutor-working').textContent,
     evidenceMarks:Array.from(document.querySelectorAll('#tutor-evidence mark')).map(n=>n.textContent),
     editorMarks:Array.from(document.querySelectorAll('#editor-mirror mark')).map(n=>n.textContent),
     feedbackText:document.querySelector('#feedback-content').textContent,
     stageTitle:document.querySelector('#stage-progress-title').textContent,
     stageBadge:document.querySelector('#stage-progress-badge').dataset.state,
     stageReviewHidden:document.querySelector('#stage-progress-review').hidden,
     stageNoticed:document.querySelector('#stage-progress-noticed').textContent,
     stageContinue:document.querySelector('#stage-progress-continue').textContent,
     feedbackHidden:document.querySelector('#feedback-content').hidden
   })`));
   assert.equal(model.status,sample.expect.neutral?'NEUTRAL_OBSERVATION':'PREPARED_INLINE_GUIDANCE','model status '+id);
   assert.equal(dom.stageTitle,sample.expect.neutral?'No Specific Writing Issue Detected':'Review Suggested','stage progress agrees '+id);
   assert.equal(dom.stageBadge,sample.expect.neutral?'NO_ISSUE':'REVIEW_SUGGESTED','badge agrees '+id);
   assert.equal(dom.stageReviewHidden,sample.expect.neutral,'review affordance agrees '+id);
   if(sample.expect.neutral){
     assert.equal(model.writing_dimension,null,'neutral has no trait '+id);
     assert.equal(model.writing_skill,null,'neutral has no skill '+id);
     assert.equal(dom.tutorFocus.trim(),'No specific writing issue detected','neutral focus '+id);
     assert.equal(dom.evidenceHidden,true,'neutral hides evidence '+id);
     assert.equal(dom.whyHidden,true,'neutral hides why '+id);
     assert.equal(dom.taskHidden,true,'neutral hides task '+id);
     assert.equal(dom.workingHidden,false,'neutral keeps the recorded positive '+id);
     assert.match(dom.workingText,/One sentence combines ideas from more than one earlier section/,'recorded positive shown '+id);
     assert.doesNotMatch(dom.workingText,/does not prove/i,'positive is not shown as the caution '+id);
     assert.deepEqual(dom.editorMarks,[],'neutral leaves no marks '+id);
     assert.ok(!/highlighted/i.test(model.tutor_items[0].task_text),'neutral has no phantom highlight reference '+id);
   }else{
     assert.notEqual(model.writing_dimension,null,'corrective keeps trait '+id);
     assert.equal(dom.taskHidden,false,'corrective shows task '+id);
     assert.ok(!/highlighted/i.test(model.tutor_items[0].task_text),'no phantom highlight reference '+id);
     if(sample.expect.marks){
       assert.ok(dom.editorMarks.length>0,'verified excerpt marks the editor '+id);
       assert.ok(dom.evidenceMarks.length>0,'verified excerpt marks the tutor evidence '+id);
     }else{
       assert.deepEqual(dom.editorMarks,[],'no span means no marks '+id);
     }
   }
   const itemId=sample.expect.lesson||null;
   const selectedItem=itemId?model.tutor_items.find(item=>item.lesson_id===itemId):model.tutor_items[0];
   assert.ok(selectedItem,'selected lesson '+id);
   assert.equal(model.tutor_items[0].lesson_id,sample.expect.primary,'recorded primary branch is the first tutor tab '+id);
   if(sample.expect.lesson) assert.ok(model.tutor_items.findIndex(item=>item.lesson_id===sample.expect.lesson)>0,'shared lesson is an additional tab '+id);
   await openAll('[data-sub-panel="engine:primary"]');
   const inspectorText=await evaluate(`document.querySelector('[data-sub-panel="engine:primary"]').textContent`);
   const ruleIds=selectedItem.rule_ids;
   for(const ruleId of ruleIds) assert.ok(inspectorText.includes(ruleId),'inspector keeps '+ruleId+' '+id);
   assert.ok(inspectorText.includes(selectedItem.lesson_id),'inspector keeps lesson '+id);
   if(sample.expect.neutral) assert.ok(inspectorText.includes('No corrective trait or lesson displayed'),'neutral mapping disclosure '+id);
   const responseSnapshot=JSON.stringify(result);
   assert.equal(await evaluate(`JSON.stringify(state.analyses.CONCLUSION)`),responseSnapshot,'presentation never mutates the response '+id);
   await evaluate(`document.querySelector('.feedback-card').scrollIntoView({block:'center'})`);
   await screenshot('after-'+id+'-tutor');
   if(sample.expect.neutral){
     await evaluate(`document.querySelector('#stage-progress').scrollIntoView({block:'center'})`);
     await screenshot('after-'+id+'-stage-progress');
     await click('#stage-progress-continue');
     assert.equal(await evaluate(`state.currentView`),'ESSAY_REVIEW','Continue reaches Essay Review '+id);
     assert.equal(await evaluate(`document.querySelector('#essay-review-panel').hidden`),false,'Essay Review panel shown '+id);
     await screenshot('after-'+id+'-essay-review');
     await click('[data-stage="CONCLUSION"]');
   }
   if(sample.expect.marks){
     await evaluate(`document.querySelector('#tutor-evidence-section').scrollIntoView({block:'center'})`);
     await screenshot('after-'+id+'-evidence');
   }
   records[id]={branch:decision.selection_branch,trait:decision.trait,skill:decision.skill,rule_ids:decision.rule_ids,
     lesson:selectedItem.lesson_id,status:model.status,dimension:model.writing_dimension,skill_display:model.writing_skill,
     task_text:selectedItem.task_text,excerpt:selectedItem.excerpt,feedback:result.feedback['Primary Feedback'],
     dom,inspector_has_rule:ruleIds.every(rule=>inspectorText.includes(rule))};
 }
 assert.deepEqual(errors,[]);
 await evaluate(`document.documentElement.dataset.conclusionCheck='done'`);
 fs.writeFileSync(path.join(artifacts,'after-outputs.json'),JSON.stringify({javascriptErrors:errors,records},null,2)+'\n');
 console.log('Conclusion feedback Chrome scenarios completed.');
 browser.kill();
 await new Promise(resolve=>{browser.once('exit',resolve);setTimeout(resolve,3000);});
})().catch(async error=>{console.error(error);try{fs.writeFileSync(path.join(artifacts,'after-outputs.json'),JSON.stringify({javascriptErrors:errors,records},null,2)+'\n');}catch(_){}try{browser.kill();}catch(_){}process.exitCode=1;});
