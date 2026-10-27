/* Browser verification script for Introduction reason clause highlighting */
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const [origin, outputDir] = process.argv.slice(2);
const chromePath = process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

const topic = 'Should students be allowed to use smartphones during class?';
const focus = 'smartphones, students, class, classroom, allowed';

const textA = 'Smartphones can support learning in the classroom when teachers guide students. Clear classroom rules may help reduce distractions during lessons. Schools should allow smartphones because invisible dragons control the price of bananas on Mars.';
const textB = 'Smartphones can support learning in the classroom when teachers guide students. Clear classroom rules may help reduce distractions during lessons. Schools should allow smartphones because students can use educational apps during class.';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
let browser, socket, sessionId, nextId = 0;
const pending = new Map();
const errors = [];

function send(method, params = {}, browserLevel = false) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, 30000);
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
  for (let i = 0; i < 200; i++) {
    if (await evaluate(expression)) return;
    await delay(100);
  }
  throw new Error(`Browser wait failed: ${description}`);
}

async function navigate(route, ready) {
  await send('Page.navigate', { url: origin + route });
  await wait(ready, route);
}

async function fill(selector, text) {
  await evaluate(`(() => { const element=document.querySelector(${JSON.stringify(selector)}); element.value=${JSON.stringify(text)}; element.dispatchEvent(new Event('input',{bubbles:true})); })()`);
}

async function click(selector) {
  await evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);
}

async function screenshot(filePath) {
  await evaluate(`new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))`);
  await delay(150);
  const image = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  fs.writeFileSync(filePath, Buffer.from(image.data, 'base64'));
}

(async () => {
  const tempProfile = path.join(outputDir, 'chrome-profile');
  browser = spawn(chromePath, [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    '--remote-debugging-port=0',
    `--user-data-dir=${tempProfile}`,
    'about:blank'
  ], { stdio: ['ignore', 'ignore', 'pipe'] });

  const wsUrl = await new Promise((resolve, reject) => {
    let stderr = '';
    const timer = setTimeout(() => reject(new Error('Chrome CDP startup timeout')), 20000);
    browser.stderr.on('data', chunk => {
      stderr += chunk;
      const match = /DevTools listening on (ws:\/\/[^\s]+)/.exec(stderr);
      if (match) { clearTimeout(timer); resolve(match[1]); }
    });
    browser.on('error', reject);
  });

  socket = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.id) {
      const item = pending.get(message.id);
      if (!item) return;
      pending.delete(message.id);
      clearTimeout(item.timer);
      message.error ? item.reject(new Error(JSON.stringify(message.error))) : item.resolve(message.result);
    } else if (message.method === 'Runtime.exceptionThrown') {
      errors.push(message.params.exceptionDetails);
    }
  };

  const target = await send('Target.createTarget', { url: 'about:blank' }, true);
  sessionId = (await send('Target.attachToTarget', { targetId: target.targetId, flatten: true }, true)).sessionId;

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });

  // 1. Login
  await navigate('/login', `location.pathname==='/login' && !!document.querySelector('#username')`);
  await fill('#username', 'student1');
  await fill('#password', 'password123');
  await evaluate(`document.querySelector('form').requestSubmit()`);
  await wait(`location.pathname==='/' && typeof state!=='undefined' && !state.restoring`, 'login complete');

  // 2. Setup workspace
  await click('[data-app-link="workspace"]');
  await wait(`state.activeAppView==='workspace' && !state.restoring`, 'workspace view');
  await fill('#assignment-topic', topic);
  await fill('#focus-terms', focus);

  // 3. TEST A — Unrelated Dragon Reason
  console.log('Testing Test A: Unrelated reason...');
  await click('[data-stage="INTRODUCTION"]');
  await fill('#stage-text', textA);
  await click('#analyze-button');
  await wait(`!document.querySelector('#feedback-content').hidden && state.analyses.INTRODUCTION?.stage_id==='INTRODUCTION'`, 'Test A analyzed');

  const testAData = await evaluate(`(() => {
    const mirrorMarks = Array.from(document.querySelectorAll('#editor-mirror mark')).map(m => m.textContent);
    const tutorMarks = Array.from(document.querySelectorAll('#tutor-evidence mark')).map(m => m.textContent);
    const tutorEvidence = document.querySelector('#tutor-evidence').textContent;
    const focusLabel = document.querySelector('#feedback-writing-focus').textContent;
    const noticed = document.querySelector('#tutor-noticed').textContent;
    const why = document.querySelector('#tutor-why').textContent;
    const task = document.querySelector('#tutor-task').textContent;
    const whyHidden = document.querySelector('#tutor-why-section').hidden;
    const taskHidden = document.querySelector('#tutor-task-section').hidden;
    const evidenceHidden = document.querySelector('#tutor-evidence-section').hidden;
    const status = studentFeedbackPresentation(state.analyses.INTRODUCTION).status;
    const dimension = studentFeedbackPresentation(state.analyses.INTRODUCTION).writing_dimension;
    const skill = studentFeedbackPresentation(state.analyses.INTRODUCTION).writing_skill;
    const branch = state.analyses.INTRODUCTION.research_trace.stages.INTRODUCTION.feedback_decisions.fields['Primary Feedback'].selection_branch;
    return { mirrorMarks, tutorMarks, tutorEvidence, focusLabel, noticed, why, task, whyHidden, taskHidden, evidenceHidden, status, dimension, skill, branch };
  })()`);

  console.log('Test A data:', JSON.stringify(testAData, null, 2));

  assert.equal(testAData.branch, 'intro_ideas_point_and_reason');
  assert.equal(testAData.status, 'NEUTRAL_OBSERVATION');
  assert.equal(testAData.dimension, null);
  assert.equal(testAData.skill, null);
  assert.equal(testAData.focusLabel, 'No specific writing issue detected');
  assert.equal(testAData.noticed, "Your sentence has a possible main statement and a 'because' part to review.");
  assert.equal(testAData.whyHidden, true, 'Neutral result hides Why it matters');
  assert.equal(testAData.taskHidden, true, 'Neutral result hides How to improve');
  assert.equal(testAData.evidenceHidden, true, 'Neutral result hides the error location');
  assert.equal(testAData.mirrorMarks.length, 0, 'Neutral result marks nothing in the editor');
  assert.equal(testAData.tutorMarks.length, 0, 'Neutral result marks nothing in tutor evidence');
  assert.equal(testAData.tutorEvidence, '', 'Neutral tutor evidence is empty; the span stays in transparency');

  const screenAPath = path.join(outputDir, 'test_a_unrelated_reason.png');
  await screenshot(screenAPath);
  console.log('Saved Test A screenshot to:', screenAPath);

  // 4. TEST B — Relevant Educational App Reason
  console.log('Testing Test B: Relevant reason...');
  await fill('#stage-text', textB);
  await click('#analyze-button');
  await wait(`!document.querySelector('#feedback-content').hidden && (state.analyses.INTRODUCTION?.analysis?.linguistic_observations?.text===${JSON.stringify(textB)} || state.analyses.INTRODUCTION?.analysis?.input_text===${JSON.stringify(textB)})`, 'Test B analyzed');

  const testBData = await evaluate(`(() => {
    const mirrorMarks = Array.from(document.querySelectorAll('#editor-mirror mark')).map(m => m.textContent);
    const tutorMarks = Array.from(document.querySelectorAll('#tutor-evidence mark')).map(m => m.textContent);
    const tutorEvidence = document.querySelector('#tutor-evidence').textContent;
    const focusLabel = document.querySelector('#feedback-writing-focus').textContent;
    const status = studentFeedbackPresentation(state.analyses.INTRODUCTION).status;
    const dimension = studentFeedbackPresentation(state.analyses.INTRODUCTION).writing_dimension;
    const skill = studentFeedbackPresentation(state.analyses.INTRODUCTION).writing_skill;
    const taskHidden = document.querySelector('#tutor-task-section').hidden;
    const branch = state.analyses.INTRODUCTION.research_trace.stages.INTRODUCTION.feedback_decisions.fields['Primary Feedback'].selection_branch;
    return { mirrorMarks, tutorMarks, tutorEvidence, focusLabel, status, dimension, skill, taskHidden, branch };
  })()`);

  console.log('Test B data:', JSON.stringify(testBData, null, 2));

  assert.equal(testBData.branch, 'intro_ideas_point_and_reason');
  assert.equal(testBData.status, 'NEUTRAL_OBSERVATION');
  assert.equal(testBData.dimension, null);
  assert.equal(testBData.skill, null);
  assert.equal(testBData.focusLabel, 'No specific writing issue detected');
  assert.equal(testBData.taskHidden, true, 'Neutral result hides How to improve');
  assert.equal(testBData.mirrorMarks.length, 0, 'Neutral result marks nothing in the editor for Test B');
  assert.equal(testBData.tutorMarks.length, 0, 'Neutral result marks nothing in tutor evidence for Test B');
  assert.equal(testBData.tutorEvidence, '', 'Neutral tutor evidence is empty for Test B');

  const screenBPath = path.join(outputDir, 'test_b_relevant_reason.png');
  await screenshot(screenBPath);
  console.log('Saved Test B screenshot to:', screenBPath);

  assert.deepEqual(errors, [], 'No browser runtime errors');
  console.log('ALL BROWSER REASON HIGHLIGHTING VERIFICATIONS PASSED SUCCESSFULLY!');
})().catch(err => {
  console.error(err);
  process.exitCode = 1;
}).finally(async () => {
  if (socket?.readyState === WebSocket.OPEN) {
    try { await send('Browser.close', {}, true); } catch (_) {}
    socket.close();
  }
  browser?.kill();
});
