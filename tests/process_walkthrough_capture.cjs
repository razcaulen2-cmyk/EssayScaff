/* Capture the real process walkthrough in isolated headless Chrome. */
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const [origin, artifacts] = process.argv.slice(2);
const chromePath = process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const topic = 'Should communities reduce their use of single-use plastics?';
const focusTerms = 'single-use plastics, communities, reduce, environment';
const intro = 'Single-use plastics are everywhere in our communities. Communities should reduce their use of these plastics because they can pollute rivers and harm animals.';
const body = 'Communities can reduce single-use plastics by carrying reusable bags. Reusable bags reduce waste in rivers.\n\nPlastic containers harm animals. Communities can protect animals by using reusable containers.';
const conclusion = 'In conclusion, communities should reduce single-use plastics. Reusable bags and containers can protect rivers and animals.';
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const errors = [], shots = [];
let browser, socket, sessionId, nextId = 0;
const pending = new Map();
function send(method, params = {}, browserLevel = false) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, 45000);
    pending.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params, ...(!browserLevel && sessionId ? { sessionId } : {}) }));
  });
}
async function evaluate(expression) {
  const result = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true, userGesture: true });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}
async function wait(expression, description) {
  for (let i = 0; i < 240; i++) {
    if (await evaluate(expression)) return;
    await delay(100);
  }
  throw new Error(`Browser wait failed: ${description}`);
}
async function fill(selector, text) {
  await evaluate(`(() => { const element=document.querySelector(${JSON.stringify(selector)}); element.value=${JSON.stringify(text)}; element.dispatchEvent(new Event('input',{bubbles:true})); })()`);
}
async function click(selector) {
  await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);
}
async function login(username) {
  await send('Page.navigate', { url: origin + '/login' });
  await wait(`location.pathname==='/login' && !!document.querySelector('#username')`, 'login form');
  await fill('#username', username);
  await fill('#password', 'walkthrough-password-1');
  await evaluate(`document.querySelector('form').requestSubmit()`);
  await wait(`location.pathname==='/' && typeof state!=='undefined' && !state.restoring`, 'workspace restore');
}
async function scrollTo(selector, offset = 100) {
  await evaluate(`(() => { const element=document.querySelector(${JSON.stringify(selector)}); if(!element)throw new Error('missing '+${JSON.stringify(selector)}); const top=element.getBoundingClientRect().top+scrollY-${offset}; window.scrollTo(0,Math.max(0,top)); return new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))); })()`);
  await delay(120);
}
async function screenshot(name, selector, offset = 100, note = '') {
  if (selector) await scrollTo(selector, offset);
  await evaluate(`new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))`);
  await delay(120);
  const image = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  fs.writeFileSync(path.join(artifacts, name + '.png'), Buffer.from(image.data, 'base64'));
  const state = await evaluate(`(() => { const id=transparencyTabsApi&&transparencyTabsApi.activeProcessId; const panel=id&&document.querySelector('[data-explorer-process="'+id+'"]'); return {stage:state.currentStage,process:id,title:panel?.querySelector('.explorer-process-heading h3')?.textContent||null,status:panel?.querySelector('[data-execution-status]')?.textContent?.trim()||null,overview:panel?.querySelector('[data-stage-section="A"]')?.innerText?.slice(0,700)||null,visual:panel?.querySelector('[data-stage-section="C"]')?.innerText?.slice(0,900)||null,evidence:panel?.querySelector('[data-stage-section="D"]')?.innerText?.slice(0,900)||null,scrollY:Math.round(window.scrollY)}; })()`);
  shots.push({ file: name + '.png', note, ...state });
}
async function selectProcess(id) {
  await click(`[data-process-id="${id}"]`);
  await wait(`transparencyTabsApi.activeProcessId===${JSON.stringify(id)}`, 'process ' + id);
  await delay(160);
}
async function processShot(name, id, section = 'C', note = '') {
  await selectProcess(id);
  const selector = section ? `[data-explorer-process="${id}"] [data-stage-section="${section}"]` : `[data-explorer-process="${id}"]`;
  await wait(`!!document.querySelector(${JSON.stringify(selector)})`, name);
  await screenshot(name, selector, 100, note);
}
async function analyzeStage(stage, text) {
  await click(`[data-stage="${stage}"]`);
  await fill('#stage-text', text);
  await evaluate(`clearTimeout(liveAnalysisTimer); liveAnalysisTimer=null;`);
  await click('#analyze-button');
  await wait(`document.querySelector('#nlp-transparency-content').dataset.status==='CURRENT' && state.analyses.${stage}?.stage_id==='${stage}'`, stage + ' analysis');
  await delay(250);
}
(async () => {
  browser = spawn(chromePath, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=0', `--user-data-dir=${path.join(artifacts, 'chrome-profile')}`, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  const wsUrl = await new Promise((resolve, reject) => {
    let stderr = '';
    const timer = setTimeout(() => reject(new Error('Chrome CDP startup timeout')), 20000);
    browser.stderr.on('data', chunk => { stderr += chunk; const match = /DevTools listening on (ws:\/\/[^\s]+)/.exec(stderr); if (match) { clearTimeout(timer); resolve(match[1]); } });
    browser.on('error', reject);
  });
  socket = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.id) {
      const item = pending.get(message.id);
      if (!item) return;
      pending.delete(message.id); clearTimeout(item.timer);
      message.error ? item.reject(new Error(JSON.stringify(message.error))) : item.resolve(message.result);
    } else if (message.method === 'Page.javascriptDialogOpening') {
      void send('Page.handleJavaScriptDialog', { accept: true });
    } else if (message.method === 'Runtime.exceptionThrown') errors.push(message.params.exceptionDetails);
    else if (message.method === 'Log.entryAdded' && message.params.entry.level === 'error' && !String(message.params.entry.url || '').endsWith('/favicon.ico')) errors.push(message.params.entry);
  };
  const target = await send('Target.createTarget', { url: 'about:blank' }, true);
  sessionId = (await send('Target.attachToTarget', { targetId: target.targetId, flatten: true }, true)).sessionId;
  await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
  await login('walkthrough_student');
  await click('[data-app-link="workspace"]');
  await wait(`state.activeAppView==='workspace' && !state.restoring`, 'workspace view');
  await evaluate(`window.__walkthroughCalls=[]; window.__walkthroughWrites=[]; const previousFetch=window.fetch; window.fetch=async (...args)=>{ const url=String(args[0]); if(url==='/api/analyze-stage') __walkthroughCalls.push(url); if(['/api/drafts','/api/revisions','/api/submissions'].includes(url)&&args[1]?.method==='POST') __walkthroughWrites.push(url); return previousFetch(...args); };`);
  await fill('#assignment-topic', topic);
  await fill('#focus-terms', focusTerms);
  await fill('#stage-text', intro);
  await evaluate(`clearTimeout(liveAnalysisTimer); liveAnalysisTimer=null;`);
  await screenshot('01-practice-setup', '#workspace-assignment-context', 100, 'Free Writing / Practice setup with the real assignment topic, focus terms and Introduction draft.');
  await screenshot('02-introduction-editor', '#work-area', 100, 'Introduction editor and the not-yet-analyzed Writing Tutor.');
  await analyzeStage('INTRODUCTION', intro);

  // Stage navigation and the source-verified full processing map.
  await screenshot('03-technical-inspector-overview', '#nlp-transparency', 100, 'Technical transparency section after the Introduction analysis.');
  await selectProcess('focus-preparation');
  await evaluate(`(() => { const details=document.querySelector('[data-evidence-section="backend:flow"]'); if(!details.open)details.querySelector('summary').click(); })()`);
  await wait(`document.querySelector('[data-evidence-section="backend:flow"]').open && document.querySelectorAll('.transparency-flow .transparency-flow-node').length>5`, 'pipeline map');
  await screenshot('04-pipeline-map', '.transparency-flow', 100, 'Source-verified processing map from the retained backend flow section.');

  // Stage 1 — Assignment Preparation.
  await click('[data-process-stage="preparation"]');
  await processShot('05-focus-preparation', 'focus-preparation', 'C', 'Prepared teacher focus terms, surface words and normalized lemma targets.');
  await processShot('06-focus-normalization', 'focus-normalization', 'D', 'Recorded focus-term normalization evidence.');

  // Stage 2 — Linguistic Processing.
  await click('[data-process-stage="linguistic"]');
  await processShot('07-tokenization', 'tokens', 'C', 'Recorded token strip from the one shared spaCy Doc.');
  await processShot('08-pos', 'pos', 'C', 'Part-of-speech and fine-tag annotations over the exact analyzed text.');
  await processShot('09-dependencies', 'dependencies', 'C', 'Recorded dependency tree drawn from token head links.');
  await processShot('10-lemmas', 'lemmas', 'C', 'Recorded word-form changes from token to lemma.');
  await processShot('11-sentences', 'sentences', 'C', 'Recorded sentence bounds; paragraph cards appear only for stages that split paragraphs.');
  await processShot('12-noun-phrases', 'noun-phrases', 'C', 'Recorded spaCy noun-chunk spans.');

  // Stage 3 — Topic Processing.
  await click('[data-process-stage="topic"]');
  await processShot('13-concepts', 'concepts', 'C', 'Grouped noun-based concept candidates with every recorded occurrence span.');
  await processShot('14-focus-matching', 'topic-matching', 'C', 'Direct and lemma-normalized focus-term matches with source spans.');
  await processShot('15-wordnet-skipped', 'wordnet', '', 'Direct WordNet state for the Introduction and any nested comparisons.');
  await processShot('16-related-words', 'related-concepts', 'C', 'Informational related-word evidence; not counted as a focus match.');
  await processShot('17-cross-stage-introduction', 'cross-stage', 'C', 'Introduction earlier-section comparison state.');

  // Stage 4 — Rule Evaluation.
  await click('[data-process-stage="rules"]');
  await processShot('18-stage-rule-checks', 'stage-patterns', 'C', 'Introduction structural rule checks and their recorded candidates.');
  await processShot('19-sentence-connection-review', 'sentence-connection', 'C', 'Introduction sentence topic-connection review.');
  await processShot('20-rule-events', 'rule-events', 'C', 'Emitted Rule Events with evidence, condition, outcome and feedback use.');

  // Stage 5 — Feedback Decisions.
  await click('[data-process-stage="feedback"]');
  await processShot('21-feedback-decision', 'feedback-decision', 'C', 'Recorded feedback branch trace.');
  await processShot('22-feedback-fields', 'feedback-fields', 'C', 'The five feedback fields exactly as returned.');
  await processShot('23-trait-mapping', 'trait-mapping', 'C', 'Recorded instructional mapping after branch selection.');
  await processShot('24-highlight-evidence', 'highlight-evidence', 'C', 'Verified source spans available to the tutor highlight.');

  // Stage 6 — Output & Technical Trace.
  await click('[data-process-stage="output"]');
  await processShot('25-api-rendering', 'api-rendering', 'C', 'Flask response, guarded browser cache and rendering handoff.');
  await processShot('26-technical-trace', 'technical-trace', 'C', 'Retained runtime metadata, processing steps and timing scope.');

  await screenshot('27-introduction-tutor', '.feedback-card', 100, 'Introduction Writing Tutor after analysis.');
  const introduction = await evaluate(`state.analyses.INTRODUCTION`);

  // Body.
  await analyzeStage('BODY', body);
  await screenshot('28-body-tutor', '.feedback-card', 100, 'Body Writing Tutor after analysis.');
  await selectProcess('topic-sentences');
  await screenshot('29-body-topic-sentences', '[data-explorer-process="topic-sentences"] [data-stage-section="C"]', 100, 'Body topic-sentence candidates per paragraph.');
  await selectProcess('cross-stage');
  await screenshot('30-body-cross-stage', '[data-explorer-process="cross-stage"] [data-stage-section="C"]', 100, 'Recorded Introduction–Body lexical comparisons.');
  const bodyResponse = await evaluate(`state.analyses.BODY`);

  // Conclusion.
  await analyzeStage('CONCLUSION', conclusion);
  await screenshot('31-conclusion-tutor', '.feedback-card', 100, 'Conclusion Writing Tutor after analysis.');
  await selectProcess('cross-stage');
  await screenshot('32-conclusion-cross-stage', '[data-explorer-process="cross-stage"] [data-stage-section="C"]', 100, 'Recorded earlier-section–Conclusion comparisons.');
  await selectProcess('new-material');
  await screenshot('33-conclusion-new-material', '[data-explorer-process="new-material"] [data-stage-section="C"]', 100, 'Conclusion unobserved-wording observations.');
  await selectProcess('highlight-evidence');
  await screenshot('34-conclusion-highlight', '[data-explorer-process="highlight-evidence"] [data-stage-section="C"]', 100, 'Conclusion highlight-evidence state.');
  const conclusionResponse = await evaluate(`state.analyses.CONCLUSION`);

  const calls = await evaluate(`__walkthroughCalls.length`), writes = await evaluate(`__walkthroughWrites.length`);
  assert.equal(calls, 3, 'one real analysis request per stage');
  assert.equal(writes, 0, 'capture never saves or submits');
  assert.deepEqual(errors, [], 'no browser errors');
  const meta = {
    capturedAt: new Date().toISOString(),
    viewport: { width: 1440, height: 1000 },
    assignment: { topic, focus_terms: focusTerms, introduction: intro, body, conclusion },
    calls, writes, screenshots: shots, javascriptErrors: errors,
  };
  fs.writeFileSync(path.join(artifacts, 'walkthrough-capture.json'), JSON.stringify(meta, null, 2));
  fs.writeFileSync(path.join(artifacts, 'INTRODUCTION-response.json'), JSON.stringify(introduction, null, 2));
  fs.writeFileSync(path.join(artifacts, 'BODY-response.json'), JSON.stringify(bodyResponse, null, 2));
  fs.writeFileSync(path.join(artifacts, 'CONCLUSION-response.json'), JSON.stringify(conclusionResponse, null, 2));
  console.log(JSON.stringify({ screenshots: shots.length, calls, writes, javascriptErrors: errors.length, artifacts }, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; }).finally(async () => {
  if (socket?.readyState === WebSocket.OPEN) { try { await send('Browser.close', {}, true); } catch (_) {} socket.close(); }
  browser?.kill();
});
