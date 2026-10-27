/* Actual Chrome reproduction of the pre-correction Conclusion behavior. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawn}=require('node:child_process');
const [origin,artifacts]=process.argv.slice(2);
const password=process.env.ESSAYSCAFF_CONCLUSION_PASSWORD;
let browser,socket,sessionId,nextId=0;
const pending=new Map(),errors=[];
const delay=ms=>new Promise(r=>setTimeout(r,ms));
function send(method,params={},root=false){const id=++nextId;return new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error(method+' timeout')),30000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params,...(!root&&sessionId?{sessionId}:{})}));});}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true,userGesture:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function wait(expression,label){for(let i=0;i<300;i++){if(await evaluate(expression))return;await delay(100);}throw Error('wait: '+label);}
async function click(selector){await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);}
async function fill(selector,text){await evaluate(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.value=${JSON.stringify(text)};e.dispatchEvent(new Event('input',{bubbles:true}));})()`);}
async function screenshot(name){await evaluate(`new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))`);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(artifacts,name+'.png'),Buffer.from(r.data,'base64'));}
const intro="Schools should turn a small part of their playgrounds into vegetable gardens because it can help students learn about science and develop responsibility. Through gardening activities, students can observe how plants grow and understand the importance of taking care of the environment. These experiences can make learning more practical while allowing students to enjoy both gardening and playing at school.";
const body="A vegetable garden can help students learn about science. Students can observe how seeds grow and record changes in the plants. These activities give students a chance to practice what they learn in class.\n\nA school garden can also teach responsibility. For example, students can take turns watering the vegetables, removing weeds, and checking whether the plants are healthy. By completing these tasks regularly, students can learn to be responsible and understand the importance of caring for something.";
const conclusion="In conclusion, schools should turn a small part of their playgrounds into vegetable gardens. These gardens can help students learn about science by observing how plants grow. Students can also develop responsibility by taking turns watering vegetables and caring for the plants.";
(async()=>{
 browser=spawn(process.env.CHROME_PATH||'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(artifacts,'chrome-profile-before'),'about:blank'],{stdio:['ignore','ignore','pipe']});
 const ws=await new Promise((resolve,reject)=>{let s='';browser.stderr.on('data',b=>{s+=b;const m=/DevTools listening on (ws:\/\/\S+)/.exec(s);if(m)resolve(m[1]);});browser.on('error',reject);});
 socket=new WebSocket(ws);await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});
 socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails);else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description));else if(m.method==='Page.javascriptDialogOpening')send('Page.handleJavaScriptDialog',{accept:true}).catch(err=>errors.push(String(err)));};
 const target=await send('Target.createTarget',{url:'about:blank'},true);sessionId=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true},true)).sessionId;await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
 await send('Page.navigate',{url:origin+'/login'});await wait(`document.readyState==='complete'&&!!document.querySelector('#username')`,'login');
 await fill('#username','conclusion_student');await fill('#password',password);await click('form button[type="submit"]');
 await wait(`location.pathname==='/'&&typeof state!=='undefined'&&!state.restoring`,'shell');
 await click('[data-app-link="workspace"]');await wait(`typeof state!=='undefined'&&!state.restoring&&!!document.querySelector('#stage-text')`,'workspace');
 await fill('#assignment-topic','The School Garden Debate');await fill('#focus-terms','schools, playgrounds, vegetable gardens, students, learning');
 await click('[data-stage="INTRODUCTION"]');await wait(`state.currentStage==='INTRODUCTION'`,'intro');await fill('#stage-text',intro);
 await click('[data-stage="BODY"]');await wait(`state.currentStage==='BODY'`,'body');await fill('#stage-text',body);
 await click('[data-stage="CONCLUSION"]');await wait(`state.currentStage==='CONCLUSION'`,'conclusion');await fill('#stage-text',conclusion);
 await click('#analyze-button');
 await wait(`!!state.analyses.CONCLUSION&&state.analysisSnapshots.CONCLUSION===analysisSnapshot('CONCLUSION')&&!state.tutorAnalysisRunning`,'analysis');
 const result=JSON.parse(await evaluate(`JSON.stringify(state.analyses.CONCLUSION)`));
 const decision=result.research_trace.stages.CONCLUSION.feedback_decisions.fields['Primary Feedback'];
 assert.equal(decision.selection_branch,'conclusion_ideas_bring_together');
 const model=JSON.parse(await evaluate(`JSON.stringify(studentFeedbackPresentation(state.analyses.CONCLUSION))`));
 const dom=JSON.parse(await evaluate(`JSON.stringify({
   focus:document.querySelector('#feedback-writing-focus').textContent,
   evidenceHidden:document.querySelector('#tutor-evidence-section').hidden,
   evidenceText:document.querySelector('#tutor-evidence').textContent,
   whyHidden:document.querySelector('#tutor-why-section').hidden,
   taskHidden:document.querySelector('#tutor-task-section').hidden,
   taskText:document.querySelector('#tutor-task').textContent,
   workingHidden:document.querySelector('#tutor-working-section').hidden,
   editorMarks:Array.from(document.querySelectorAll('#editor-mirror mark')).map(n=>n.textContent),
   tutorMarks:Array.from(document.querySelectorAll('#tutor-evidence mark')).map(n=>n.textContent),
   stageTitle:document.querySelector('#stage-progress-title').textContent,
   stageBadge:document.querySelector('#stage-progress-badge').dataset.state,
   stageReviewHidden:document.querySelector('#stage-progress-review').hidden,
   feedbackText:document.querySelector('#feedback-content').textContent
 })`));
 await evaluate(`document.querySelector('.feedback-card').scrollIntoView({block:'center'})`);await screenshot('before-EXACT-tutor');
 await evaluate(`document.querySelector('#stage-progress').scrollIntoView({block:'center'})`);await screenshot('before-EXACT-stage-progress');
 fs.writeFileSync(path.join(artifacts,'before-outputs.json'),JSON.stringify({javascriptErrors:errors,branch:decision.selection_branch,ruleIds:decision.rule_ids,status:model.status,dimension:model.writing_dimension,skill:model.writing_skill,lesson:model.teaching_content_source?.content_id||null,tutorItems:model.tutor_items.map(item=>({label:item.label,lesson:item.lesson_id,task:item.task_text,excerpt:item.excerpt})),dom},null,2)+'\n');
 console.log('Conclusion pre-correction Chrome reproduction completed.');
 browser.kill();await new Promise(resolve=>{browser.once('exit',resolve);setTimeout(resolve,3000);});
})().catch(async error=>{console.error(error);try{fs.writeFileSync(path.join(artifacts,'before-outputs.json'),JSON.stringify({javascriptErrors:errors,error:String(error)},null,2)+'\n');}catch(_){}try{browser.kill();}catch(_){}process.exitCode=1;});
