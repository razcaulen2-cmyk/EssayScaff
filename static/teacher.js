const teacherViews = [...document.querySelectorAll("[data-teacher-view]")];
const teacherLinks = [...document.querySelectorAll("[data-teacher-link]")];

function showTeacherView(view, updateHistory = true) {
  if (!teacherViews.some((item) => item.dataset.teacherView === view)) view = "dashboard";
  for (const item of teacherViews) item.hidden = item.dataset.teacherView !== view;
  for (const link of teacherLinks) {
    const active = link.dataset.teacherLink === view;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  document.body.dataset.activeView = view;
  if (updateHistory && window.location && window.location.hash !== `#${view}`) {
    window.history.pushState({ teacherView: view }, "", `#${view}`);
  }
}

for (const link of teacherLinks) {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    showTeacherView(link.dataset.teacherLink);
  });
}

for (const trigger of document.querySelectorAll("[data-open-view]")) {
  trigger.addEventListener("click", () => {
    showTeacherView(trigger.dataset.openView);
    const panel = document.getElementById(trigger.dataset.openForm);
    if (panel) {
      panel.open = true;
      panel.querySelector("summary")?.focus();
    }
  });
}

for (const trigger of document.querySelectorAll("[data-open-form]")) {
  if (trigger.hasAttribute("data-open-view")) continue;
  trigger.addEventListener("click", () => {
    const panel = document.getElementById(trigger.dataset.openForm);
    if (panel) {
      panel.open = true;
      panel.querySelector("summary")?.focus();
    }
  });
}

function restoreTeacherViewFromHash() {
  const requested = window.location?.hash?.slice(1);
  if (requested) showTeacherView(requested, false);
}

const initialTeacherView = window.location?.hash?.slice(1) || document.body.dataset.initialView || "dashboard";
showTeacherView(initialTeacherView, false);
if (initialTeacherView === "classrooms" && document.body.dataset.hasError === "true") {
  const panel = document.getElementById("create-classroom-panel");
  if (panel) panel.open = true;
}
if (initialTeacherView === "assignments" && document.body.dataset.hasError === "true") {
  const panel = document.getElementById("create-assignment-panel");
  if (panel) panel.open = true;
}
window.addEventListener("hashchange", restoreTeacherViewFromHash);
window.addEventListener("popstate", restoreTeacherViewFromHash);
