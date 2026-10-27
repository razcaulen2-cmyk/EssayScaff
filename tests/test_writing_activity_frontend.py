"""Exercise active-writing timing rules with a controlled JavaScript clock."""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest


NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(
    NODE is None, reason="Node.js is required for the writing activity test"
)


def test_active_writing_interval_rules_with_fake_clock():
    tracker_path = (
        Path(__file__).resolve().parents[1] / "static" / "writing_activity.js"
    )
    script = r'''
const assert = require("node:assert/strict");
const { createWritingActivityTracker } = require(process.env.TRACKER_PATH);

let tabCounter = 0;

function makeHarness({ storage = new Map(), clock = { value: 0 }, fetchState = { failNext: false, posted: [] } } = {}) {
  let hidden = false;
  let canTrack = true;
  const timers = new Map();
  let nextTimerId = 1;
  const storageApi = {
    getItem: (key) => storage.has(key) ? storage.get(key) : null,
    setItem: (key, value) => storage.set(key, String(value)),
    removeItem: (key) => storage.delete(key),
  };
  const tracker = createWritingActivityTracker({
    canTrack: () => canTrack,
    isHidden: () => hidden,
    now: () => clock.value,
    fetchImpl: async (url, options) => {
      assert.equal(url, "/api/writing-activity");
      assert.equal(options.headers["X-CSRF-Token"], "csrf-test");
      if (fetchState.failNext) {
        fetchState.failNext = false;
        throw new Error("controlled network failure");
      }
      fetchState.posted.push(JSON.parse(options.body));
      return { ok: true, status: 200 };
    },
    storage: storageApi,
    setIntervalImpl: (callback, delay) => {
      const id = nextTimerId++;
      timers.set(id, { callback, delay });
      return id;
    },
    clearIntervalImpl: (id) => timers.delete(id),
    csrfToken: "csrf-test",
    tabId: `tab-${++tabCounter}`,
  });
  tracker.configure({ enabled: true, assignmentId: 101, sessionId: "a".repeat(32) });
  return {
    tracker, timers, clock, storage, fetchState,
    setHidden(value) { hidden = value; },
    setCanTrack(value) { canTrack = value; },
    ticks(from, to) {
      for (let time = from; time <= to; time += 5_000) {
        clock.value = time;
        tracker.tick();
      }
    },
  };
}

function eventsOf(harness) {
  return harness.fetchState.posted.flatMap((payload) => payload.events);
}

function secondsFor(harness, stage) {
  return eventsOf(harness)
    .filter((event) => event.stage === stage)
    .reduce((total, event) => total + event.seconds, 0);
}

(async () => {
  // Continuous typing counts a five-second interval per tick.
  {
    const h = makeHarness();
    h.tracker.noteEdit("INTRODUCTION");
    h.ticks(5_000, 60_000);
    await h.tracker.flush();
    assert.equal(secondsFor(h, "INTRODUCTION"), 60);
    assert.equal(h.fetchState.posted[0].assignment_id, 101);
    assert.equal(h.fetchState.posted[0].session_id, "a".repeat(32));
    h.tracker.leaveWorkspace();
    await h.tracker.flush();
    assert.equal(h.timers.size, 0, "leaving stops the interval timer");
  }

  // A short pause below 60 seconds remains part of the active period.
  {
    const h = makeHarness();
    h.tracker.noteEdit("BODY");
    h.clock.value = 0;
    h.ticks(5_000, 30_000);
    await h.tracker.flush();
    assert.equal(secondsFor(h, "BODY"), 30);
  }

  // More than 60 seconds without editing ends the period; editing resumes it.
  {
    const h = makeHarness();
    h.tracker.noteEdit("INTRODUCTION");
    h.ticks(5_000, 65_000);
    await h.tracker.flush();
    assert.equal(secondsFor(h, "INTRODUCTION"), 60);
    h.ticks(70_000, 90_000);
    await h.tracker.flush();
    assert.equal(secondsFor(h, "INTRODUCTION"), 60, "idle ticks add no time");
    h.clock.value = 100_000;
    h.tracker.noteEdit("INTRODUCTION");
    h.ticks(105_000, 110_000);
    await h.tracker.flush();
    assert.equal(secondsFor(h, "INTRODUCTION"), 70);
  }

  // Hiding the tab stops and flushes; returning does not count until an edit.
  {
    const h = makeHarness();
    h.tracker.noteEdit("INTRODUCTION");
    h.ticks(5_000, 5_000);
    h.setHidden(true);
    h.clock.value = 10_000;
    h.tracker.tick();
    await h.tracker.flush();
    const afterHide = secondsFor(h, "INTRODUCTION");
    h.setHidden(false);
    h.ticks(15_000, 20_000);
    await h.tracker.flush();
    assert.equal(secondsFor(h, "INTRODUCTION"), afterHide, "visible return alone is inactive");
    h.clock.value = 25_000;
    h.tracker.noteEdit("INTRODUCTION");
    h.ticks(30_000, 30_000);
    await h.tracker.flush();
    assert.ok(secondsFor(h, "INTRODUCTION") > afterHide);
  }

  // Switching stage gives no time to the new stage until it is edited.
  {
    const h = makeHarness();
    h.tracker.noteEdit("INTRODUCTION");
    h.ticks(5_000, 10_000);
    h.tracker.stageChanged();
    h.ticks(15_000, 20_000);
    await h.tracker.flush();
    assert.equal(secondsFor(h, "INTRODUCTION"), 10);
    assert.equal(secondsFor(h, "BODY"), 0);
    h.clock.value = 25_000;
    h.tracker.noteEdit("BODY");
    h.ticks(30_000, 35_000);
    await h.tracker.flush();
    assert.equal(secondsFor(h, "BODY"), 10);
    assert.equal(secondsFor(h, "INTRODUCTION"), 10);
  }

  // A refresh flushes the old buffer; the new page starts a new buffer.
  {
    const shared = { storage: new Map(), clock: { value: 0 }, fetchState: { failNext: false, posted: [] } };
    const first = makeHarness(shared);
    first.tracker.noteEdit("INTRODUCTION");
    first.ticks(5_000, 5_000);
    first.tracker.leaveWorkspace();
    await first.tracker.flush();
    assert.equal(secondsFor(first, "INTRODUCTION"), 5);

    const refreshed = makeHarness(shared);
    refreshed.clock.value = 10_000;
    refreshed.tracker.noteEdit("INTRODUCTION");
    refreshed.ticks(15_000, 15_000);
    await refreshed.tracker.flush();
    const total = shared.fetchState.posted
      .flatMap((payload) => payload.events)
      .filter((event) => event.stage === "INTRODUCTION")
      .reduce((sum, event) => sum + event.seconds, 0);
    assert.equal(total, 10);
  }

  // Two tabs share one lease; only the most recently edited tab records.
  {
    const storage = new Map();
    const clock = { value: 0 };
    const first = makeHarness({ storage, clock });
    const second = makeHarness({ storage, clock });
    first.tracker.noteEdit("INTRODUCTION");
    first.clock.value = 5_000;
    first.tracker.tick();
    second.clock.value = 5_000;
    second.tracker.noteEdit("INTRODUCTION");
    first.clock.value = 10_000;
    first.tracker.tick();
    second.clock.value = 10_000;
    second.tracker.tick();
    first.ticks(15_000, 20_000);
    second.ticks(15_000, 20_000);
    await first.tracker.flush();
    await second.tracker.flush();

    assert.equal(secondsFor(first, "INTRODUCTION"), 5);
    assert.equal(secondsFor(second, "INTRODUCTION"), 15);
    const events = eventsOf(first).concat(eventsOf(second));
    const keys = new Set(events.map((event) => `${event.stage}:${event.bucket_start}`));
    assert.equal(keys.size, events.length, "the two tabs never report the same bucket");
  }

  // Repeated flushes are deduplicated, and failed reports retry without loss.
  {
    const h = makeHarness();
    h.tracker.noteEdit("CONCLUSION");
    h.ticks(5_000, 5_000);
    const firstFlush = h.tracker.flush();
    const secondFlush = h.tracker.flush();
    await Promise.all([firstFlush, secondFlush]);
    assert.equal(h.fetchState.posted.length, 1);
    assert.equal(secondsFor(h, "CONCLUSION"), 5);
    await h.tracker.flush();
    assert.equal(h.fetchState.posted.length, 1, "an empty buffer sends nothing");

    const retry = makeHarness();
    retry.tracker.noteEdit("BODY");
    retry.ticks(5_000, 5_000);
    retry.fetchState.failNext = true;
    await retry.tracker.flush();
    assert.equal(retry.fetchState.posted.length, 0);
    await retry.tracker.flush();
    assert.equal(secondsFor(retry, "BODY"), 5);
  }

  // Analyze/save/navigation are outside this module; only noteEdit starts a period.
  {
    const h = makeHarness();
    h.ticks(5_000, 30_000);
    await h.tracker.flush();
    assert.equal(eventsOf(h).length, 0, "page being open does not count");
  }

  console.log("writing activity timing checks passed");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
'''
    completed = subprocess.run(
        [NODE, "-e", script],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "TRACKER_PATH": str(tracker_path)},
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_activity_events_are_only_started_by_editor_input():
    app_js = (
        Path(__file__).resolve().parents[1] / "static" / "app.js"
    ).read_text(encoding="utf-8")
    template = (
        Path(__file__).resolve().parents[1] / "templates" / "index.html"
    ).read_text(encoding="utf-8")

    assert template.index("writing_activity.js") < template.index("app.js")
    assert app_js.count("writingActivity?.noteEdit(") == 1

    input_handler = re.search(
        r'writingInput\.addEventListener\("input", \(\) => \{(?P<body>.*?)\n\}\);',
        app_js,
        re.S,
    )
    assert input_handler is not None
    assert "noteEdit(state.currentStage)" in input_handler.group("body")

    for function_name in ("async function saveDraft()", "async function saveRevision()"):
        start = app_js.index(function_name)
        end = app_js.index("\n}", start)
        assert "noteEdit(" not in app_js[start:end]

    assert "writingActivity?.stageChanged();" in app_js
    assert "writingActivity?.leaveWorkspace();" in app_js
    assert 'document.visibilityState === "hidden"' in app_js
