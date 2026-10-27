"""Exercise the lightweight teacher view router without a browser dependency."""

import shutil
import subprocess
from pathlib import Path

import pytest


NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is required for the navigation state test")


def test_teacher_navigation_shows_one_view_and_opens_requested_form():
    script_path = Path(__file__).resolve().parents[1] / "static" / "teacher.js"
    script = r'''
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

class Element {
  constructor(id, data = {}) {
    this.id = id;
    this.dataset = data;
    this.hidden = false;
    this.open = false;
    this.listeners = {};
    this.attributes = {};
    this.classList = { toggle: () => {} };
  }
  addEventListener(name, listener) {
    (this.listeners[name] ||= []).push(listener);
  }
  setAttribute(name, value) { this.attributes[name] = value; }
  removeAttribute(name) { delete this.attributes[name]; }
  querySelector() { return { focus() {} }; }
  hasAttribute(name) { return Object.hasOwn(this.attributes, name); }
}

const names = ["dashboard", "classrooms", "assignments", "progress"];
const views = names.map((view) => new Element(`view-${view}`, { teacherView: view }));
const links = names.map((view) => new Element(`link-${view}`, { teacherLink: view }));
const classroomAction = new Element("create-classroom", { openView: "classrooms", openForm: "create-classroom-panel" });
const assignmentAction = new Element("create-assignment", { openForm: "create-assignment-panel" });
const panels = {
  "create-classroom-panel": new Element("create-classroom-panel"),
  "create-assignment-panel": new Element("create-assignment-panel"),
};
const listeners = {};
const window = {
  location: { hash: "" },
  history: { pushState: (_state, _title, hash) => { window.location.hash = hash; } },
  addEventListener: (name, listener) => { listeners[name] = listener; },
};
const document = {
  body: { dataset: { initialView: "dashboard" } },
  querySelectorAll: (selector) => selector === "[data-teacher-view]" ? views
    : selector === "[data-teacher-link]" ? links
      : selector === "[data-open-view]" ? [classroomAction]
        : selector === "[data-open-form]" ? [classroomAction, assignmentAction] : [],
  getElementById: (id) => panels[id],
};
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), { document, window });
const click = async (element) => {
  for (const listener of element.listeners.click || []) await listener({ preventDefault() {} });
};

(async () => {
  assert.equal(views.find((view) => view.dataset.teacherView === "dashboard").hidden, false);
  assert.equal(views.filter((view) => !view.hidden).length, 1);
  await click(links.find((link) => link.dataset.teacherLink === "assignments"));
  assert.equal(window.location.hash, "#assignments");
  assert.equal(views.filter((view) => !view.hidden).length, 1);
  assert.equal(views.find((view) => view.dataset.teacherView === "assignments").hidden, false);
  await click(assignmentAction);
  assert.equal(panels["create-assignment-panel"].open, true);
  await click(classroomAction);
  assert.equal(window.location.hash, "#classrooms");
  assert.equal(panels["create-classroom-panel"].open, true);
  window.location.hash = "#progress";
  listeners.popstate();
  assert.equal(views.filter((view) => !view.hidden).length, 1);
  assert.equal(views.find((view) => view.dataset.teacherView === "progress").hidden, false);
})().catch((error) => { console.error(error); process.exitCode = 1; });
'''
    completed = subprocess.run(
        [NODE, "-e", script, str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
