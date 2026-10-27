const topicInput = document.getElementById("assignment-topic");
const focusInput = document.getElementById("focus-terms");
const writingInput = document.getElementById("stage-text");
const analyzeButton = document.getElementById("analyze-button");
const saveButton = document.getElementById("save-button");
const saveRevisionButton = document.getElementById("save-revision-button");
const saveStatus = document.getElementById("save-status");
const revisionSaveStatus = document.getElementById("revision-save-status");
const revisionEmpty = document.getElementById("revision-empty");
const revisionList = document.getElementById("revision-list");
const revisionPreview = document.getElementById("revision-preview");
const revisionPreviewTitle = document.getElementById("revision-preview-title");
const errorMessage = document.getElementById("error-message");
const analysisStatus = document.getElementById("analysis-status");
const introductionTutoring = document.getElementById("introduction-tutoring");
const introductionLessonSuggestion = document.getElementById("introduction-lesson-suggestion");
const openIntroductionLessonButton = document.getElementById("open-introduction-lesson");
const introductionLessonPanel = document.getElementById("introduction-lesson-panel");
const introductionLessonTitle = document.getElementById("introduction-lesson-title");
const introductionLessonStepLabel = document.getElementById("introduction-lesson-step-label");
const introductionLessonProgress = document.getElementById("introduction-lesson-progress");
const introductionLessonContent = document.getElementById("introduction-lesson-content");
const introductionLessonFeedback = document.getElementById("introduction-lesson-feedback");
const introductionLessonReturnButton = document.getElementById("introduction-lesson-return");
const introductionLessonDefinitionElement = document.getElementById("introduction-lesson-definition");
const introductionLessonDefinition = introductionLessonDefinitionElement?.textContent
  ? JSON.parse(introductionLessonDefinitionElement.textContent)
  : null;
const feedbackContent = document.getElementById("feedback-content");
const feedbackPlaceholder = document.getElementById("feedback-placeholder");
const feedbackStatus = document.getElementById("feedback-status");
const feedbackWritingFocus = document.getElementById("feedback-writing-focus");
const tutorStateTitle = document.getElementById("tutor-state-title");
const tutorStateLead = document.getElementById("tutor-state-lead");
const tutorStateDetail = document.getElementById("tutor-state-detail");
const tutorTypingDots = document.getElementById("tutor-typing-dots");
const tutorTabs = document.getElementById("tutor-tabs");
const tutorNoticed = document.getElementById("tutor-noticed");
const tutorEvidence = document.getElementById("tutor-evidence");
const tutorWhy = document.getElementById("tutor-why");
const tutorTask = document.getElementById("tutor-task");
const tutorLimitation = document.getElementById("tutor-limitation");
const stageProgress = document.getElementById("stage-progress");
const stageProgressTitle = document.getElementById("stage-progress-title");
const stageProgressBadge = document.getElementById("stage-progress-badge");
const stageProgressLead = document.getElementById("stage-progress-lead");
const stageProgressDetail = document.getElementById("stage-progress-detail");
const stageProgressFocus = document.getElementById("stage-progress-focus");
const stageProgressNoticed = document.getElementById("stage-progress-noticed");
const stageProgressTask = document.getElementById("stage-progress-task");
const stageProgressContinue = document.getElementById("stage-progress-continue");
const stageProgressReview = document.getElementById("stage-progress-review");
const scaffoldingCatalogElement = document.getElementById("scaffolding-guidance-definition");
const scaffoldingCatalog = scaffoldingCatalogElement?.textContent
  ? JSON.parse(scaffoldingCatalogElement.textContent) : null;
const nlpTransparency = document.getElementById("nlp-transparency");
const nlpTransparencyContent = document.getElementById("nlp-transparency-content");
const transparencyFocusToggle = document.getElementById("transparency-focus-toggle");
const copyFullAnalysisButton = document.getElementById("copy-full-analysis");
const analysisCopyStatus = document.getElementById("analysis-copy-status");
const analysisCopyFallback = document.getElementById("analysis-copy-fallback");
const fullAnalysisReport = document.getElementById("full-analysis-report");
const stageHeading = document.getElementById("stage-heading");
const stageLabel = document.querySelector(".card-heading .step-label");
const writingLabel = document.querySelector('label[for="stage-text"]');
const stageTabs = [...document.querySelectorAll(".stage-tab")];
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";
const workArea = document.getElementById("work-area");
const revisionCard = document.getElementById("revision-card");
const essayReviewPanel = document.getElementById("essay-review-panel");
const reviewSubmissionBadge = document.getElementById("review-submission-badge");
const reviewToggleTechnical = document.getElementById("review-toggle-technical");
const reviewEditButtons = ["INTRODUCTION", "BODY", "CONCLUSION"].map(
  (stage) => document.getElementById(`review-edit-${stage.toLowerCase()}`)
);
const assignmentList = document.getElementById("available-assignment-list");
const assignmentsEmpty = document.getElementById("assignments-empty");
const dashboardAssignmentList = document.getElementById("dashboard-assignment-list");
const dashboardAssignmentsEmpty = document.getElementById("dashboard-assignments-empty");
const classroomsPageList = document.getElementById("classrooms-page-list");
const classroomsPageEmpty = document.getElementById("classrooms-page-empty");
const showAllAssignmentsButton = document.getElementById("show-all-assignments");
const assignmentDetailView = document.getElementById("assignment-detail-view");
const assignmentDetailTitle = document.getElementById("assignment-detail-title");
const assignmentDetailClassroom = document.getElementById("assignment-detail-classroom");
const assignmentDetailProgress = document.getElementById("assignment-detail-progress");
const assignmentDetailTopic = document.getElementById("assignment-detail-topic");
const assignmentDetailInstructions = document.getElementById("assignment-detail-instructions");
const assignmentDetailFocus = document.getElementById("assignment-detail-focus");
const openAssignmentWorkspaceButton = document.getElementById("open-assignment-workspace");
const practiceSetup = document.getElementById("practice-setup");
const studentHistory = document.getElementById("student-history");
const studentHistoryList = document.getElementById("student-history-list");
const assignmentMessage = document.getElementById("assignment-message");
const practiceModeButton = document.getElementById("practice-mode-button");
const classroomList = document.getElementById("my-classroom-list");
const classroomsEmpty = document.getElementById("my-classrooms-empty");
const joinClassroomForm = document.getElementById("join-classroom-form");
const enrollmentCodeInput = document.getElementById("enrollment-code");
const selectedClassroom = document.getElementById("selected-classroom");
const selectedClassroomName = document.getElementById("selected-classroom-name");
const selectedClassroomSubtitle = document.getElementById("selected-classroom-subtitle");
const selectedAssignmentDetails = document.getElementById("selected-assignment-details");
const selectedAssignmentTitle = document.getElementById("selected-assignment-title");
const selectedAssignmentInstructions = document.getElementById("selected-assignment-instructions");
const selectedAssignmentTopic = document.getElementById("selected-assignment-topic");
const selectedAssignmentFocusTerms = document.getElementById("selected-assignment-focus-terms");
const assignmentSubmittedStatus = document.getElementById("assignment-submitted-status");
const submissionControls = document.getElementById("submission-controls");
const submitEssayButton = document.getElementById("submit-essay-button");
const submissionStatus = document.getElementById("submission-status");
const submissionError = document.getElementById("submission-error");
const appViews = [...document.querySelectorAll("[data-app-view]")];
const appLinks = [...document.querySelectorAll("[data-app-link]")];

let activityStorage = null;
try {
  activityStorage = window.localStorage;
} catch (_error) {
  activityStorage = null;
}
const writingActivity = typeof window.createWritingActivityTracker === "function"
  ? window.createWritingActivityTracker({
      canTrack: () => (
        state.activeAppView === "workspace"
        && state.assignmentId !== null
        && state.currentView === state.currentStage
        && !state.submission
        && !state.deletedAssignment
        && !state.restoring
        && !state.submitting
      ),
      isHidden: () => document.visibilityState === "hidden",
      fetchImpl: (url, options) => fetch(url, options),
      storage: activityStorage,
      setIntervalImpl: window.setInterval?.bind(window),
      clearIntervalImpl: window.clearInterval?.bind(window),
      csrfToken,
    })
  : null;

const stageSettings = {
  INTRODUCTION: {
    title: "Write Your Introduction",
    button: "Analyze Now",
    placeholder: "Write your Introduction here…",
    limit: 12000,
  },
  BODY: {
    title: "Write Your Body",
    button: "Analyze Now",
    placeholder: "Write your Body paragraphs here. Leave a blank line between paragraphs…",
    limit: 30000,
  },
  CONCLUSION: {
    title: "Write Your Conclusion",
    button: "Analyze Now",
    placeholder: "Write your Conclusion here…",
    limit: 12000,
  },
};

const state = {
  currentStage: "INTRODUCTION",
  currentView: "INTRODUCTION",
  activeAppView: "dashboard",
  assignmentId: null,
  pendingAssignmentId: null,
  assignmentTitle: "",
  deletedAssignment: false,
  selectedClassroomId: null,
  classrooms: [],
  assignments: [],
  drafts: { INTRODUCTION: "", BODY: "", CONCLUSION: "" },
  analyses: {},
  analysisSnapshots: {},
  analysisFailures: {},
  introductionLesson: { open: false },
  sessionId: null,
  draftVersion: null,
  submission: null,
  submitting: false,
  savedSnapshot: null,
  saving: false,
  revisionSaving: false,
  restoring: false,
  saveFailed: false,
  saveErrorMessage: "",
  restoreIdWarning: false,
  restored: false,
  tutorAnalysisRunning: false,
  tutorError: false,
  tutorTyping: false,
  tutorAssignmentStale: false,
  tutorStaleStages: {},
  revisionCount: null,
  revisionHistoryStatus: "idle",
  writingActivityStatus: "idle",
  writingActivitySeconds: null,
  writingActivityNote: "",
  reviewTechnicalInspectorOpen: false,
};

const LIVE_ANALYSIS_DELAY_MS = 1000;
const TUTOR_TYPING_IDLE_MS = 350;
let liveAnalysisTimer = null;
let tutorTypingTimer = null;
let activeTutorItems = [];
let activeTutorItemIndex = 0;
let activeAnalysisController = null;
let activeAnalysisStage = null;
let analysisRequestId = 0;
let inFlightAnalysis = null;
let queuedStageAnalysis = null;
let analysisWorkPromise = null;
let analysisCopyGeneration = 0;
let analysisCopyInProgress = false;
let activitySummaryRequestId = 0;

const TUTOR_WELCOME = {
  INTRODUCTION: {
    title: "Ready to write your Introduction?",
    lead: "Start by introducing the topic and explaining what you think about it.",
    detail: "Your first draft doesn't have to be perfect. You can review and improve it when you're ready.",
  },
  BODY: {
    title: "Let's develop your ideas.",
    lead: "Choose one reason that supports your main point.",
    detail: "Explain that reason and include an example or supporting detail.",
  },
  CONCLUSION: {
    title: "Let's finish your essay.",
    lead: "Think about the important ideas you explained earlier.",
    detail: "Bring those ideas together and give your reader a clear ending.",
  },
};
const TUTOR_STATE_TEXT = {
  TYPING: { title: "You're writing…", lead: "Feedback will update after a short pause.", detail: "" },
  PAUSED: { title: "Checking your latest writing…", lead: "Your latest version is waiting for analysis.", detail: "" },
  RUNNING: { title: "Analyzing your writing…", lead: "This usually takes a few seconds.", detail: "" },
  STALE: { title: "Your writing has changed.", lead: "Analyze again to review this version.", detail: "" },
  ASSIGNMENT_STALE: { title: "Assignment details changed.", lead: "Analyze this stage again for current feedback.", detail: "" },
  ERROR: { title: "Writing analysis is temporarily unavailable. You can try Analyze Now.", lead: "Your writing is still in the editor.", detail: "" },
};
const TUTOR_NO_EXCERPT_TEXT = "I could not point to a verified part of your writing for this notice.";
const TUTOR_CATEGORY_LABELS = {
  "Ideas": "Ideas",
  "Organization": "Organization",
  "Sentence Fluency": "Sentence Fluency",
  "Word Choice": "Word Choice",
  "Conventions": "Conventions",
};
const TUTOR_TRAITS = Object.keys(TUTOR_CATEGORY_LABELS);

function resetAnalysisContext() {
  state.analyses = {};
  state.analysisSnapshots = {};
  state.analysisFailures = {};
  state.tutorStaleStages = {};
  state.tutorAssignmentStale = false;
  resetIntroductionLessonProgress();
}

function currentAssignmentDetails() {
  return JSON.stringify([state.assignmentId, topicInput.value, focusInput.value]);
}

function currentDraftData() {
  state.drafts[state.currentStage] = writingInput.value;
  return {
    assignment_topic: topicInput.value,
    focus_terms: focusInput.value,
    assignment_id: state.assignmentId,
    introduction_text: state.drafts.INTRODUCTION,
    body_text: state.drafts.BODY,
    conclusion_text: state.drafts.CONCLUSION,
  };
}

function draftSnapshot() {
  return JSON.stringify(currentDraftData());
}

function updateSaveStatus() {
  const current = draftSnapshot();
  if (state.saving || state.revisionSaving) {
    setSaveStatus(state.revisionSaving ? "Saving revision…" : "Saving…", "saving");
  } else if (state.saveFailed) {
    setSaveStatus(state.saveErrorMessage || "Save failed — try again", "failed");
  } else if (state.savedSnapshot !== null && current !== state.savedSnapshot) {
    setSaveStatus("Unsaved changes", "unsaved");
  } else if (state.restoreIdWarning) {
    setSaveStatus("Draft saved; browser restore ID could not be stored", "saved");
  } else if (state.sessionId && state.restored) {
    setSaveStatus("Draft restored", "saved");
  } else if (state.sessionId && state.savedSnapshot === current) {
    setSaveStatus("Draft saved", "saved");
  } else {
    setSaveStatus("Not saved", "unsaved");
  }
}

function setSaveStatus(message, status) {
  saveStatus.textContent = message;
  saveStatus.dataset.state = status;
}

function isDirty() {
  return state.savedSnapshot !== null && draftSnapshot() !== state.savedSnapshot;
}

function updateBeforeUnloadWarning(event) {
  if (isDirty() || state.saving || state.revisionSaving) {
    event.preventDefault();
    event.returnValue = "";
  }
}

function updateWordCount() {
  const count = countWords(writingInput.value);
  document.getElementById("word-count").textContent = `${count} ${count === 1 ? "word" : "words"}`;
}

function countWords(text) {
  return (text.trim().match(/\S+/g) || []).length;
}

let transparencyFocusActive = false;

function updateTransparencyFocusMetrics() {
  if (typeof getComputedStyle !== "function") return;
  const headerHeight = document.querySelector(".app-header")?.offsetHeight || 72;
  document.documentElement.style.setProperty("--app-header-h", `${headerHeight}px`);
  const layout = document.querySelector(".app-layout");
  const singleColumn = Boolean(layout) && getComputedStyle(layout).display === "block";
  const sidebarHeight = singleColumn ? (document.querySelector(".app-sidebar")?.offsetHeight || 0) : 0;
  document.documentElement.style.setProperty("--app-top-chrome-h", `${headerHeight + sidebarHeight}px`);
}

function setTransparencyFocus(active, revealTransparency = true) {
  active = Boolean(active) && state.activeAppView === "workspace";
  if (active === transparencyFocusActive) return;
  transparencyFocusActive = active;
  if (active) updateTransparencyFocusMetrics();
  document.body.classList.toggle("transparency-focus", active);
  if (transparencyFocusToggle) {
    transparencyFocusToggle.textContent = active ? "Exit full-screen" : "Full-screen explorer";
    transparencyFocusToggle.setAttribute("aria-pressed", String(active));
  }
  if (active) window.scrollTo(0, 0);
  else if (revealTransparency) nlpTransparency?.scrollIntoView?.({ block: "start" });
}

window.addEventListener("resize", () => {
  if (transparencyFocusActive) updateTransparencyFocusMetrics();
});

transparencyFocusToggle?.addEventListener("click", () => setTransparencyFocus(!transparencyFocusActive));

function navigateAppView(view, updateHistory = true) {
  if (!appViews.some((item) => item.dataset.appView === view)) view = "dashboard";
  if (view !== "workspace") {
    cancelAnalysisWork();
    setTransparencyFocus(false, false);
    writingActivity?.leaveWorkspace();
  }
  if (state.activeAppView !== view) assignmentMessage.textContent = "";
  for (const item of appViews) item.hidden = item.dataset.appView !== view;
  for (const link of appLinks) {
    const active = link.dataset.appLink === view;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  state.activeAppView = view;
  document.body.dataset.activeView = view;
  updateAnalysisExport();
  updateIntroductionTutoring();
  updateStageProgress();
  if (updateHistory && window.location && window.location.hash !== `#${view}`) {
    window.history.pushState({ studentView: view }, "", `#${view}`);
  }
  if (view === "dashboard") loadDashboardAssignments();
  if (view === "assignments" && state.selectedClassroomId === null) loadAllAssignments();
  if (view === "workspace" && !state.analyses[state.currentStage]) scheduleLiveAnalysis();
}

function restoreAppViewFromHash() {
  const requested = window.location?.hash?.slice(1);
  if (requested) navigateAppView(requested, false);
}

for (const link of appLinks) {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    if (link.dataset.appLink === "assignments") {
      state.selectedClassroomId = null;
      selectedClassroom.hidden = true;
    }
    navigateAppView(link.dataset.appLink);
  });
}
window.addEventListener("hashchange", restoreAppViewFromHash);
window.addEventListener("popstate", restoreAppViewFromHash);

function renderClassrooms(classrooms) {
  state.classrooms = classrooms;
  classroomList.replaceChildren();
  classroomsPageList.replaceChildren();
  for (const classroom of classrooms) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.className = "dashboard-classroom-button";
    button.type = "button";
    button.textContent = `${classroom.classroom_name} · ${classroom.section}`;
    button.addEventListener("click", () => selectClassroom(classroom.classroom_id));
    item.appendChild(button);
    classroomList.appendChild(item);

    const card = document.createElement("li");
    card.className = "classroom-grid-item";
    const heading = document.createElement("h2");
    heading.textContent = classroom.classroom_name;
    const details = document.createElement("p");
    details.textContent = `${classroom.subject} · ${classroom.section}`;
    const teacher = document.createElement("p");
    teacher.className = "classroom-teacher-name";
    teacher.textContent = classroom.teacher_username
      ? `Teacher ${classroom.teacher_username}`
      : "Teacher information not available";
    const assignmentCount = document.createElement("span");
    assignmentCount.className = "status-chip";
    assignmentCount.textContent = `${classroom.assignment_count || 0} assignments`;
    const open = document.createElement("button");
    open.type = "button";
    open.className = "button-secondary compact-button";
    open.textContent = "View assignments";
    open.addEventListener("click", () => selectClassroom(classroom.classroom_id));
    card.append(heading, details, teacher, assignmentCount, open);
    classroomsPageList.appendChild(card);
  }
  classroomsEmpty.hidden = classrooms.length > 0;
  classroomsPageEmpty.hidden = classrooms.length > 0;
}

async function loadMyClassrooms() {
  try {
    const response = await fetch("/api/classrooms");
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Classrooms could not be loaded.");
    renderClassrooms(result.classrooms || []);
  } catch (error) {
    classroomsEmpty.hidden = false;
    classroomsEmpty.textContent = error.message || "Classrooms could not be loaded.";
  }
}

async function loadStudentHistory() {
  try {
    const response = await fetch("/api/student-history");
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Student history could not be loaded.");
    studentHistoryList.replaceChildren();
    for (const assignment of result.assignments || []) {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.className = "history-record-button";
      button.type = "button";
      const status = document.createElement("span");
      status.className = `status-chip history-status status-${assignment.history_status.toLowerCase()}`;
      status.textContent = assignment.history_status;
      const title = document.createElement("span");
      title.className = "history-record-title";
      title.textContent = `${assignment.title} — ${assignment.classroom_name} · ${assignment.section}`;
      button.append(status, title);
      button.addEventListener("click", () => showAssignmentDetails(assignment));
      item.appendChild(button);
      studentHistoryList.appendChild(item);
    }
    studentHistory.hidden = (result.assignments || []).length === 0;
  } catch (error) {
    studentHistory.hidden = false;
    studentHistory.textContent = error.message || "Student history could not be loaded.";
  }
}

function assignmentCard(assignment, compact = false) {
  const item = document.createElement("li");
  item.className = compact ? "dashboard-assignment-item" : "assignment-grid-item";
  const card = document.createElement("article");
  card.className = "assignment-card-inner";
  const header = document.createElement("div");
  header.className = "assignment-card-header";
  const title = document.createElement(compact ? "h3" : "h2");
  title.textContent = assignment.title;
  const status = document.createElement("span");
  status.className = `status-chip status-${String(assignment.progress || "Not Started").toLowerCase().replaceAll(" ", "-")}`;
  status.textContent = assignment.progress || "Not Started";
  header.append(title, status);
  const topic = document.createElement("p");
  topic.className = "assignment-card-topic";
  topic.textContent = assignment.topic;
  const classroom = document.createElement("p");
  classroom.className = "assignment-card-classroom";
  classroom.textContent = `${assignment.classroom_name}${assignment.section ? ` · ${assignment.section}` : ""}`;
  const action = document.createElement("button");
  action.type = "button";
  action.className = "button-primary compact-button";
  action.textContent = compact
    ? assignment.progress === "In Progress" ? "Continue Writing" : assignment.progress === "Submitted" ? "Review Writing" : "Start Writing"
    : "View assignment details";
  action.addEventListener("click", () => compact
    ? selectAssignment(assignment.assignment_id)
    : showAssignmentDetails(assignment));
  card.append(header, topic, classroom, action);
  item.appendChild(card);
  return item;
}

function showAssignmentDetails(assignment) {
  state.pendingAssignmentId = assignment.assignment_id;
  assignmentDetailTitle.textContent = assignment.title;
  assignmentDetailClassroom.textContent = `${assignment.classroom_name}${assignment.section ? ` · ${assignment.section}` : ""}`;
  const progress = assignment.progress || assignment.history_status;
  assignmentDetailProgress.textContent = progress || (assignment.deleted_at ? "Read only" : "Not Started");
  assignmentDetailTopic.textContent = assignment.topic;
  assignmentDetailInstructions.textContent = assignment.instructions || "No additional instructions were provided.";
  assignmentDetailFocus.textContent = assignment.focus_terms
    ? `Focus terms: ${assignment.focus_terms}`
    : "No focus terms provided.";
  openAssignmentWorkspaceButton.textContent = assignment.deleted_at
    ? "Open saved work"
    : progress === "In Progress" ? "Continue Writing" : progress === "Submitted" ? "Review Writing" : "Start Writing";
  assignmentDetailView.hidden = false;
}

function renderAvailableAssignments(assignments) {
  assignmentList.replaceChildren();
  assignmentDetailView.hidden = true;
  state.assignments = assignments;
  for (const assignment of assignments) assignmentList.appendChild(assignmentCard(assignment));
  assignmentsEmpty.hidden = assignments.length > 0;
  assignmentList.hidden = assignments.length === 0;
}

async function loadDashboardAssignments() {
  try {
    const response = await fetch("/api/assignments");
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Assignments could not be loaded.");
    dashboardAssignmentList.replaceChildren();
    for (const assignment of (result.assignments || []).slice(0, 3)) {
      dashboardAssignmentList.appendChild(assignmentCard(assignment, true));
    }
    dashboardAssignmentsEmpty.hidden = (result.assignments || []).length > 0;
  } catch (error) {
    dashboardAssignmentsEmpty.hidden = false;
    dashboardAssignmentsEmpty.textContent = error.message || "Assignments could not be loaded.";
  }
}

async function loadAllAssignments() {
  try {
    const response = await fetch("/api/assignments");
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Assignments could not be loaded.");
    renderAvailableAssignments(result.assignments || []);
  } catch (error) {
    assignmentList.replaceChildren();
    assignmentList.hidden = true;
    assignmentsEmpty.hidden = false;
    assignmentsEmpty.textContent = error.message || "Assignments could not be loaded.";
  }
}

async function selectClassroom(classroomId, navigate = true) {
  try {
    const response = await fetch(`/api/classrooms/${encodeURIComponent(classroomId)}/assignments`);
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Classroom assignments could not be loaded.");
    const classroom = state.classrooms.find((item) => item.classroom_id === classroomId);
    state.selectedClassroomId = classroomId;
    selectedClassroomName.textContent = classroom ? classroom.classroom_name : "Classroom";
    selectedClassroomSubtitle.textContent = classroom
      ? `${classroom.subject} · ${classroom.section}`
      : "";
    selectedClassroom.hidden = false;
    renderAvailableAssignments(result.assignments || []);
    if (navigate) navigateAppView("assignments");
    if (navigate) navigateAppView("assignments");
  } catch (error) {
    state.selectedClassroomId = null;
    selectedClassroom.hidden = true;
    assignmentsEmpty.hidden = false;
    assignmentsEmpty.textContent = error.message || "Classroom assignments could not be loaded.";
  }
}

function setWorkspaceControlsDisabled(disabled) {
  for (const control of [
    topicInput, focusInput, writingInput, analyzeButton, saveButton, saveRevisionButton,
    practiceModeButton, enrollmentCodeInput, ...stageTabs,
  ]) {
    control.disabled = disabled;
  }
  for (const button of assignmentList.querySelectorAll("button")) button.disabled = disabled;
  for (const button of classroomList.querySelectorAll("button")) button.disabled = disabled;
  updateSubmissionUI();
  updateAnalysisExport();
}

function reviewControlsLocked() {
  return state.submission !== null || state.deletedAssignment || state.submitting
    || state.restoring || state.saving || state.revisionSaving;
}

function updateReviewEditButtons() {
  const locked = reviewControlsLocked();
  for (const button of reviewEditButtons) {
    if (!button) continue;
    button.disabled = locked;
    button.title = locked
      ? state.submission !== null
        ? "Submitted essays are read-only."
        : "Editing is temporarily unavailable."
      : "";
  }
}

function syncTechnicalInspectorVisibility() {
  const reviewing = state.currentView === "ESSAY_REVIEW";
  const expanded = reviewing && state.reviewTechnicalInspectorOpen;
  if (nlpTransparency) nlpTransparency.hidden = reviewing && !expanded;
  if (reviewToggleTechnical) {
    reviewToggleTechnical.setAttribute("aria-expanded", String(expanded));
    reviewToggleTechnical.textContent = expanded
      ? "Hide technical analysis (NLP Process Explorer)"
      : "Show technical analysis (NLP Process Explorer)";
  }
}

function updateSubmissionUI() {
  const assigned = state.assignmentId !== null;
  const submitted = state.submission !== null;
  const locked = submitted || state.deletedAssignment || state.submitting;
  submissionControls.hidden = !assigned || submitted || state.deletedAssignment;
  assignmentSubmittedStatus.hidden = !submitted && !state.deletedAssignment;
  assignmentSubmittedStatus.textContent = submitted
    ? `Submitted ${formatRevisionDate(state.submission.submitted_at)}. This assignment is read-only.`
    : state.deletedAssignment
      ? "This assignment was deleted by your teacher. Your saved work is available read-only."
      : "";
  writingInput.readOnly = locked;
  for (const control of [analyzeButton, saveButton, saveRevisionButton]) {
    control.disabled = locked || state.restoring || state.saving || state.revisionSaving;
  }
  submitEssayButton.disabled = locked || state.restoring || state.saving || state.revisionSaving;
  updateReviewEditButtons();
  updateIntroductionTutoring();
}

function applyAssignmentWorkspace(workspace) {
  cancelAnalysisWork();
  const assignment = workspace.assignment;
  const draft = workspace.draft;
  state.assignmentId = assignment.assignment_id;
  state.assignmentTitle = assignment.title;
  state.deletedAssignment = Boolean(assignment.deleted_at);
  state.selectedClassroomId = assignment.classroom_id;
  state.sessionId = draft.session_id;
  state.draftVersion = workspace.draft_version || null;
  state.submission = workspace.submission || null;
  state.drafts = {
    INTRODUCTION: draft.introduction_text,
    BODY: draft.body_text,
    CONCLUSION: draft.conclusion_text,
  };
  resetAnalysisContext();
  resetReviewSummaryState();
  state.restored = true;
  revisionPreview.hidden = true;
  revisionSaveStatus.textContent = "";
  topicInput.value = assignment.topic;
  focusInput.value = assignment.focus_terms;
  topicInput.readOnly = true;
  focusInput.readOnly = true;
  practiceSetup.hidden = true;
  selectedAssignmentTitle.textContent = assignment.title;
  selectedAssignmentTopic.textContent = assignment.topic;
  selectedAssignmentInstructions.textContent = assignment.instructions;
  selectedAssignmentFocusTerms.textContent = assignment.focus_terms
    ? `Focus terms: ${assignment.focus_terms}`
    : "No teacher focus terms provided.";
  selectedAssignmentDetails.hidden = false;
  writingInput.value = state.drafts[state.currentStage];
  state.savedSnapshot = draftSnapshot();
  let storageWarning = false;
  try {
    window.localStorage.setItem("essayScaffActiveAssignmentId", String(assignment.assignment_id));
  } catch (_error) {
    storageWarning = true;
  }
  assignmentMessage.textContent = storageWarning
    ? "Assignment opened. Browser storage is unavailable for remembering this selection."
    : "Assignment writing is saved separately for your student account.";
  feedbackStatus.textContent = "Not analyzed";
  displayFeedback(null);
  writingActivity?.configure({
    enabled: Boolean(workspace.activity_tracking_enabled),
    assignmentId: state.assignmentId,
    sessionId: state.sessionId,
  });
  selectStage(state.currentStage);
  submissionStatus.textContent = state.deletedAssignment
    ? "This assignment has been deleted and cannot accept new work."
    : state.submission
      ? "This essay has been submitted."
      : "Submit your saved essay when it is ready.";
  submissionError.hidden = true;
  updateSubmissionUI();
  updateSaveStatus();
}

function applyPracticeDraft(draft) {
  cancelAnalysisWork();
  state.assignmentId = null;
  state.assignmentTitle = "";
  state.deletedAssignment = false;
  state.selectedClassroomId = null;
  state.sessionId = draft ? draft.session_id : null;
  state.draftVersion = null;
  state.submission = null;
  state.drafts = draft
    ? {
        INTRODUCTION: draft.introduction_text,
        BODY: draft.body_text,
        CONCLUSION: draft.conclusion_text,
      }
    : { INTRODUCTION: "", BODY: "", CONCLUSION: "" };
  resetAnalysisContext();
  resetReviewSummaryState();
  state.restored = Boolean(draft);
  revisionPreview.hidden = true;
  revisionSaveStatus.textContent = "";
  topicInput.value = draft ? draft.assignment_topic : "";
  focusInput.value = draft ? draft.focus_terms : "";
  topicInput.readOnly = false;
  focusInput.readOnly = false;
  practiceSetup.hidden = false;
  selectedAssignmentDetails.hidden = true;
  selectedClassroom.hidden = true;
  assignmentList.replaceChildren();
  assignmentList.hidden = true;
  assignmentsEmpty.hidden = true;
  writingInput.value = state.drafts[state.currentStage];
  state.savedSnapshot = draftSnapshot();
  feedbackStatus.textContent = "Not analyzed";
  displayFeedback(null);
  writingActivity?.configure({
    enabled: false,
    assignmentId: null,
    sessionId: state.sessionId,
  });
  selectStage(state.currentStage);
  updateSubmissionUI();
  assignmentMessage.textContent = "Free Writing / Practice selected.";
}

async function selectAssignment(assignmentId) {
  if (state.restoring) return;
  if (state.saving || state.revisionSaving || state.submitting) {
    assignmentMessage.textContent = "Wait for the current save or submission before switching workspaces.";
    return;
  }
  if (isDirty()) {
    navigateAppView("workspace");
    assignmentMessage.textContent = "Save your current draft before switching workspaces.";
    return;
  }
  cancelAnalysisWork();
  navigateAppView("workspace");
  state.restoring = true;
  setWorkspaceControlsDisabled(true);
  assignmentMessage.textContent = "Opening assignment…";
  try {
    const response = await fetch(`/api/assignments/${encodeURIComponent(assignmentId)}/workspace`);
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Assignment could not be opened.");
    applyAssignmentWorkspace(result);
    await loadRevisionHistory();
    await selectClassroom(result.assignment.classroom_id, false);
  } catch (error) {
    assignmentMessage.textContent = error.message || "Assignment could not be opened.";
  } finally {
    state.restoring = false;
    setWorkspaceControlsDisabled(false);
    updateSaveStatus();
  }
}

async function selectPracticeMode() {
  if (state.restoring) return;
  if (state.saving || state.revisionSaving || state.submitting) {
    assignmentMessage.textContent = "Wait for the current save or submission before switching workspaces.";
    return;
  }
  if (state.assignmentId === null) return;
  if (isDirty()) {
    assignmentMessage.textContent = "Save your assignment draft before switching to Free Writing / Practice.";
    return;
  }
  cancelAnalysisWork();
  state.restoring = true;
  setWorkspaceControlsDisabled(true);
  assignmentMessage.textContent = "Opening Free Writing / Practice…";
  try {
    const sessionId = window.localStorage.getItem("essayScaffSessionId");
    let draft = null;
    if (sessionId) {
      const response = await fetch(`/api/drafts?session_id=${encodeURIComponent(sessionId)}`);
      if (response.ok) {
        draft = await response.json();
      } else if (response.status !== 404 && response.status !== 400) {
        const result = await response.json().catch(() => ({}));
        throw new Error(result.error || "Practice writing could not be restored.");
      } else {
        // The missing practice session is expected for a first-time practice workspace.
      }
    }
    state.assignmentId = null;
    state.assignmentTitle = "";
    state.deletedAssignment = false;
    state.selectedClassroomId = null;
    state.sessionId = draft ? draft.session_id : null;
    state.draftVersion = null;
    state.submission = null;
    state.drafts = draft
      ? {
          INTRODUCTION: draft.introduction_text,
          BODY: draft.body_text,
          CONCLUSION: draft.conclusion_text,
        }
      : { INTRODUCTION: "", BODY: "", CONCLUSION: "" };
    resetAnalysisContext();
    state.restored = Boolean(draft);
    topicInput.value = draft ? draft.assignment_topic : "";
    focusInput.value = draft ? draft.focus_terms : "";
    topicInput.readOnly = false;
    focusInput.readOnly = false;
    practiceSetup.hidden = false;
    selectedAssignmentDetails.hidden = true;
    selectedClassroom.hidden = true;
    assignmentList.replaceChildren();
    assignmentList.hidden = true;
    assignmentsEmpty.hidden = true;
    writingInput.value = state.drafts[state.currentStage];
    state.savedSnapshot = draftSnapshot();
    updateSubmissionUI();
    try {
      window.localStorage.removeItem("essayScaffActiveAssignmentId");
    } catch (_error) {
      // The active editor still works if browser storage is unavailable.
    }
    feedbackStatus.textContent = "Not analyzed";
    displayFeedback(null);
    writingActivity?.configure({
      enabled: false,
      assignmentId: null,
      sessionId: state.sessionId,
    });
    selectStage(state.currentStage);
    assignmentMessage.textContent = "Free Writing / Practice selected.";
    await loadRevisionHistory();
  } catch (error) {
    assignmentMessage.textContent = error.message || "Practice writing could not be opened.";
  } finally {
    state.restoring = false;
    setWorkspaceControlsDisabled(false);
    updateSaveStatus();
  }
}

function resetReviewSummaryState() {
  activitySummaryRequestId++;
  state.revisionCount = null;
  state.revisionHistoryStatus = "idle";
  state.writingActivityStatus = "idle";
  state.writingActivitySeconds = null;
  state.writingActivityNote = "";
  state.reviewTechnicalInspectorOpen = false;
  if (nlpTransparency) nlpTransparency.hidden = false;
}

function setReviewText(elementId, text) {
  const element = document.getElementById(elementId);
  if (element) element.textContent = text;
}

function formatWritingActivity(seconds) {
  if (!Number.isFinite(seconds) || seconds <= 0) return "Not recorded";
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  if (minutes === 0) return `${remainder} sec`;
  return remainder ? `${minutes} min ${remainder} sec` : `${minutes} min`;
}

function renderEssayReview() {
  setReviewText("review-assignment-topic", topicInput.value.trim() || "No assignment topic entered.");
  const sections = [
    ["INTRODUCTION", "review-introduction", "Introduction"],
    ["BODY", "review-body", "Body"],
    ["CONCLUSION", "review-conclusion", "Conclusion"],
  ];
  let total = 0;
  let writtenSections = 0;
  for (const [stage, elementId, label] of sections) {
    const text = state.drafts[stage] || "";
    const hasWriting = text.trim().length > 0;
    if (hasWriting) writtenSections += 1;
    document.getElementById(elementId).textContent = text || `${label} has not been written yet.`;
    const count = countWords(text);
    total += count;
    setReviewText(`review-progress-${stage.toLowerCase()}-words`, String(count));
    setReviewText(`review-progress-${stage.toLowerCase()}-status`, hasWriting ? "Drafted" : "Not started");
  }
  setReviewText("review-summary-total-words", String(total));
  setReviewText("review-summary-sections", `${writtenSections} of 3`);
  document.getElementById("review-unsaved-note").hidden = !isDirty();

  setReviewText("review-summary-revisions", state.revisionCount === null
    ? state.revisionHistoryStatus === "error" ? "Unavailable" : "Checking…"
    : String(state.revisionCount));
  setReviewText("review-revisions-note", state.revisionHistoryStatus === "error"
    ? "Revision records could not be loaded."
    : "Explicit snapshots saved with Save Revision.");

  setReviewText("review-summary-active-time", state.writingActivityStatus === "recorded"
    ? formatWritingActivity(state.writingActivitySeconds)
    : state.writingActivityStatus === "loading"
      ? "Checking…"
      : state.writingActivityStatus === "unavailable" ? "Unavailable" : "Not recorded");
  setReviewText("review-active-time-note", state.writingActivityNote
    || "No active writing time has been recorded yet.");
  setReviewText("review-summary-remaining-time", "Unavailable");
  setReviewText("review-remaining-note",
    "No word target is set for this assignment, so EssayScaff does not estimate remaining time.");

  const submitted = state.submission !== null;
  if (reviewSubmissionBadge) {
    reviewSubmissionBadge.textContent = submitted
      ? "Submitted"
      : state.deletedAssignment ? "Read-only" : "Not submitted";
    reviewSubmissionBadge.dataset.state = submitted
      ? "SUBMITTED"
      : state.deletedAssignment ? "READ_ONLY" : "DRAFT";
  }
  setReviewText("review-submission-note", submitted
    ? `Submitted ${formatRevisionDate(state.submission.submitted_at)}. This essay is read-only.`
    : state.deletedAssignment
      ? "This assignment was deleted by your teacher. The saved work is read-only."
      : state.assignmentId === null
        ? "Submission is available only for classroom assignments."
        : "Submitting sends your saved draft to your teacher. You will not be able to edit it afterward.");
  updateReviewEditButtons();
  syncTechnicalInspectorVisibility();
}

for (const stage of ["INTRODUCTION", "BODY", "CONCLUSION"]) {
  document.getElementById(`review-edit-${stage.toLowerCase()}`)?.addEventListener("click", () => {
    if (reviewControlsLocked()) return;
    selectStage(stage);
    writingInput.focus();
    writingInput.scrollIntoView?.({ behavior: "smooth", block: "center" });
  });
}

reviewToggleTechnical?.addEventListener("click", () => {
  state.reviewTechnicalInspectorOpen = !state.reviewTechnicalInspectorOpen;
  syncTechnicalInspectorVisibility();
  if (state.reviewTechnicalInspectorOpen) {
    nlpTransparency?.scrollIntoView?.({ behavior: "smooth", block: "start" });
  }
});

function transparencyValue(value) {
  return value === undefined || value === null || value === "" ? "Not available" : String(value);
}

function transparencySection(parent, title) {
  const section = document.createElement("section");
  section.className = "transparency-section";
  const heading = document.createElement("h3");
  heading.textContent = title;
  section.appendChild(heading);
  parent.appendChild(section);
  return section;
}

const STUDENT_TRANSPARENCY_SUBTABS = {
  processing: [["overview", "Overview"], ["pipeline", "spaCy Pipeline"], ["tokenization", "Tokenization"], ["lemmatization", "Lemmatization"], ["pos", "POS Tagging"], ["dependencies", "Dependency Parsing"], ["noun-chunks", "Noun Chunks"], ["concepts", "Concept Extraction"]],
  topic: [["overview", "Overview"], ["focus-terms", "Focus Terms"], ["normalization", "Normalization"], ["direct", "Direct Matches"], ["lemma", "Lemma Matches"], ["wordnet", "WordNet"], ["cross-stage", "Cross-stage Comparison"]],
  rules: [["overview", "Overview"], ["triggered", "Triggered Rules"], ["not-triggered", "Not Triggered"], ["conditions", "Rule Conditions"], ["evidence", "Evidence & Thresholds"], ["code", "Code & References"]],
  feedback: [["overview", "Overview"], ["goal", "Current Goal"], ["primary", "Primary Feedback"], ["working", "What's Working"], ["attention", "Needs Attention"], ["next", "Next Step"], ["provenance", "Provenance"]],
};

const HORIZONTAL_TRANSPARENCY_TABS = [
  ["student", "Student Text", [["overview", "Overview"], ["text", "Analyzed Text"], ["context", "Assignment & Context"]]],
  ["backend", "Flask Backend", [["overview", "Overview"], ["validation", "Validation"], ["response", "Response Handling"], ["flow", "Call & Data Flow"]]],
  ["nlp", "NLP Extraction", [["overview", "Overview"], ["sentences", "Sentences"], ["tokens", "Tokens"], ["lemmas", "Lemmas"], ["pos", "POS"], ["dependencies", "Dependencies"], ["chunks", "Noun Chunks"], ["pipeline", "Pipeline"]]],
  ["concept", "Concept Extraction", [["overview", "Overview"], ["concepts", "Extracted Concepts"], ["occurrences", "Occurrences & Sources"]]],
  ["topic", "Topic Matching", [["overview", "Overview"], ["focus-terms", "Focus Terms"], ["normalization", "Normalization"], ["direct", "Direct Matches"], ["lemma", "Lemma Matches"], ["related", "Related Topic Concepts"], ["wordnet", "WordNet"], ["cross-stage", "Cross-stage"]]],
  ["rules", "Rule Base", [["overview", "Overview"], ["stage", "Stage Observations"], ["triggered", "Triggered"], ["not-triggered", "Not Triggered"], ["evidence", "Evidence"], ["trace", "Evaluation Trace"], ["sources", "Sources & References"]]],
  ["engine", "Feedback Engine", [["overview", "Overview"], ["goal", "Goal"], ["primary", "Primary Feedback"], ["working", "What's Working"], ["attention", "Needs Attention"], ["next", "Next Step"], ["provenance", "Provenance"]]],
  ["final", "Final Feedback", [["overview", "Overview"], ["fields", "Five Fields"], ["response", "Response & Display"], ["complete", "Complete Evidence"], ["limitations", "Limitations"]]],
];

const TRANSPARENCY_OPERATION_VIEWS = {
  input: ["student", "text"], pipeline: ["nlp", "pipeline"], sentences: ["nlp", "sentences"],
  tokens: ["nlp", "tokens"], lemmas: ["nlp", "lemmas"], pos: ["nlp", "pos"],
  dependencies: ["nlp", "dependencies"], chunks: ["nlp", "chunks"], concepts: ["concept", "occurrences"],
  focus: ["topic", "overview"], related: ["topic", "related"], wordnet: ["topic", "wordnet"], stage: ["rules", "stage"],
  rules: ["rules", "trace"], feedback: ["engine", "overview"], response: ["final", "response"],
};

// Evidence-link adapter for the process explorer. Stable original section keys
// are retained for visualizer cross-links and the lossless full-analysis index.
let transparencyTabsApi = null;

function transparencyText(parent, text, className = "") {
  const paragraph = document.createElement("p");
  if (className) paragraph.className = className;
  paragraph.textContent = text;
  parent.appendChild(paragraph);
  return paragraph;
}

function transparencyTable(parent, headings, rows, emptyMessage = "Not available") {
  if (!Array.isArray(rows) || rows.length === 0) {
    transparencyText(parent, emptyMessage);
    return;
  }
  const wrapper = document.createElement("div");
  wrapper.className = "transparency-table-wrap";
  wrapper.tabIndex = 0;
  wrapper.setAttribute("role", "region");
  wrapper.setAttribute("aria-label", `${headings.join(", ")} evidence table; scroll for additional rows or columns`);
  const table = document.createElement("table");
  table.className = "transparency-table";
  const head = document.createElement("thead");
  const headerRow = document.createElement("tr");
  for (const heading of headings) {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = heading;
    headerRow.appendChild(cell);
  }
  head.appendChild(headerRow);
  table.appendChild(head);
  const body = document.createElement("tbody");
  for (const row of rows) {
    const tableRow = document.createElement("tr");
    for (const value of row) {
      const cell = document.createElement("td");
      cell.textContent = transparencyValue(value);
      tableRow.appendChild(cell);
    }
    body.appendChild(tableRow);
  }
  table.appendChild(body);
  wrapper.appendChild(table);
  parent.appendChild(wrapper);
}

function transparencyEvidence(parent, evidence) {
  if (evidence === undefined || evidence === null) {
    transparencyText(parent, "Not available");
    return;
  }
  if (Array.isArray(evidence) && evidence.length === 0) {
    transparencyText(parent, "No evidence items were recorded.");
    return;
  }
  renderTransparencyRecord(parent, evidence);
}

const STUDENT_TRANSPARENCY_PROCESS_INFO = {
  "processing:overview": { what: "This overview groups the linguistic observations returned for the current stage.", why: "The next checks use the same parsed stage document.", how: "NLPService.parse calls the loaded spaCy Language object; analyze_doc serializes its annotations.", source: "services/nlp_service.py: NLPService.parse, analyze_doc", references: [["spaCy pipeline guide", "https://spacy.io/usage/processing-pipelines"]], limitation: "Statistical labels can be wrong and do not validate meaning.", next: "Inspect the enabled pipeline, then each returned token attribute." },
  "processing:pipeline": { what: "The loaded spaCy components that process the current stage.", why: "Each component supplies annotations used by downstream observations.", how: "Tokenizer creates a Doc, then enabled named components run in nlp.pipe_names order. EssayScaff records the active pipeline from the same NLPService.", source: "services/nlp_service.py:NLPService.__init__, parse; services/research_inspector.py:runtime_metadata", references: [["spaCy pipeline guide", "https://spacy.io/usage/processing-pipelines"]], limitation: "Individual component timings are not measured; NER runs but its entities are not consumed by active Rule Bases.", next: "Tokenization and annotation fields come from this same Doc." },
  "processing:tokenization": { what: "The token sequence created from this stage's exact text.", why: "Token spans support phrase matching and map rule evidence back to the essay.", how: "spaCy tokenizes the string; EssayScaff excludes space tokens from its serialized token list but retains punctuation. Offsets are zero-based and end-exclusive.", source: "services/nlp_service.py:NLPService.parse, analyze_doc, _token_data", references: [["spaCy Token API", "https://spacy.io/api/token"]], limitation: "Token boundaries are model/tokenizer output, not words as defined by every writing convention.", next: "The same token records receive lemmas, POS/tags, and parser relations." },
  "processing:lemmatization": { what: "The actual token-to-lemma mapping for the analyzed essay.", why: "Lemma sequences support normalized focus matching and concept grouping.", how: "TopicService reads Token.lemma_ from the existing Doc and case-folds it for matching/grouping.", source: "services/nlp_service.py:_token_data; services/topic_service.py:_lemma, _extract_concepts", references: [["spaCy pipeline guide", "https://spacy.io/usage/processing-pipelines"]], limitation: "A lemma is a normalized linguistic form, not a synonym or meaning judgment.", next: "Lemmas feed concept extraction and normalized matches." },
  "processing:pos": { what: "Coarse POS and fine-grained tag labels assigned to each actual token.", why: "Rule Bases filter finite predicate candidates and content words by these labels.", how: "The spaCy tagger and attribute components annotate the Doc. EssayScaff reads token.pos and token.tag; see the glossary for labels.", source: "services/nlp_service.py:_token_data; services/introduction_rules.py:FINITE_TAGS", references: [["spaCy Token API", "https://spacy.io/api/token"]], limitation: "POS/tag predictions are statistical annotations and can be mistaken, especially for ambiguous wording.", next: "Dependency rules combine POS/tags with parser relations." },
  "processing:dependencies": { what: "The parser's token-to-head grammatical relation records.", why: "Subject-linked predicates support structural clause candidates.", how: "spaCy Parser supplies dep_, head, sentence boundaries, and head offsets; the view maps actual head_start values to source tokens.", source: "services/nlp_service.py:analyze_doc; services/stage_evidence.py:clause_candidates_from_sentences", references: [["spaCy Token API", "https://spacy.io/api/token"]], limitation: "A dependency tree does not prove that a proposition is meaningful, true, or coherent.", next: "Stage Rule Bases use selected subject, predicate, and dependency records." },
  "processing:noun-chunks": { what: "Noun phrase spans returned by spaCy's parser-backed Doc.noun_chunks.", why: "TopicService uses noun chunks as candidate multiword concepts.", how: "NLPService serializes phrase text and character spans from the same parsed Doc.", source: "services/nlp_service.py:analyze_doc; services/topic_service.py:_extract_concepts", references: [["spaCy pipeline guide", "https://spacy.io/usage/processing-pipelines"]], limitation: "A noun chunk is a parser phrase candidate; it is not guaranteed to be a salient idea.", next: "TopicService groups noun chunks and individual noun/proper-noun tokens into concepts." },
  "processing:concepts": { what: "Lemma-normalized noun phrase and noun/proper-noun candidates from the current stage.", why: "Body and Conclusion rules use concepts for recurrence and cross-stage lexical comparison.", how: "TopicService groups identical normalized forms and keeps each distinct source occurrence and extraction method.", source: "services/topic_service.py:TopicService._extract_concepts", references: [["spaCy Token API", "https://spacy.io/api/token"]], limitation: "There is no concept rank or confidence score; generic nouns can be included and non-nominal ideas can be missed.", next: "Body/Conclusion recurrence and cross-stage comparisons, and optional direct WordNet suggestions, consume concepts. Direct/lemma focus matching independently consumes Doc token windows; Introduction rules do not consume concepts." },
  "topic:overview": { what: "This overview shows the configured focus source, coverage, and actual lexical matches.", why: "It explains which teacher-provided terms or topic-derived candidates were compared.", how: "TopicService normalizes focus phrases, searches the current Doc, and summarizes observed/unobserved terms.", source: "services/topic_service.py:analyze, prepare_teacher_context", references: [], limitation: "Word overlap is not semantic relevance or topic understanding.", next: "Inspect terms, normalization, and separate WordNet candidates." },
  "topic:focus-terms": { what: "The actual teacher terms or automatic topic-derived candidates for this analysis.", why: "These are the lexical targets used by TopicService matching.", how: "Teacher phrases are deduplicated by normalized lemma form; absent/empty teacher terms lead to topic-derived noun concepts.", source: "services/topic_service.py:prepare_teacher_context, _unique_focus_terms", references: [], limitation: "Focus lists can omit paraphrases or include generic terms.", next: "Each term is normalized before direct/lemma matching." },
  "topic:normalization": { what: "The original focus phrase and its actual case-folded lemma sequence.", why: "Normalization lets inflected forms share a comparison form.", how: "Alphabetic phrase tokens are lemmatized and joined with spaces; duplicates with the same normalized form are grouped.", source: "services/topic_service.py:_unique_focus_terms, _lemma", references: [["spaCy Token API", "https://spacy.io/api/token"]], limitation: "Lemma normalization does not include broad semantic paraphrase expansion.", next: "Direct and lemma match tabs show the resulting spans." },
  "topic:direct": { what: "Case-insensitive surface-form focus matches returned for this essay.", why: "They show exact word/phrase overlap used in coverage and stage evidence.", how: "TopicService scans consecutive alphabetic-token windows and labels an equal case-folded surface sequence direct.", source: "services/topic_service.py:_find_matches", references: [], limitation: "A direct match can be irrelevant in context.", next: "Lemma Matches show normalized matches that are not direct surface matches." },
  "topic:lemma": { what: "Focus matches found by comparing the actual token lemma sequence with the normalized focus phrase.", why: "Inflected forms can match a teacher focus phrase without identical surface text.", how: "Each eligible token window is lemmatized; an equal normalized sequence is recorded as normalized.", source: "services/topic_service.py:_find_matches", references: [["spaCy pipeline guide", "https://spacy.io/usage/processing-pipelines"]], limitation: "A lemma match is still lexical overlap, not a semantic equivalence judgment.", next: "WordNet is a separate, optional candidate relation." },
  "topic:related": { what: "Some words relate to a topic without being the same word. A configured river → environment relationship is an association, not an exact synonym.", how: "TopicService passes existing token/lemma records and prepared teacher focus to RelatedTopicConceptService.match. A whole teacher focus phrase must equal a configured key. Alphabetic token lemmas, or explicitly configured singular/plural surface forms, match approved single-word concepts. spaCy supplies annotations; the small curated JSON resource supplies relationships and any fallback forms. Each record names its normalization method. No WordNet or extra NLP call is used.", why: "Students may discuss an assignment using vocabulary that does not exactly match the teacher's focus terms.", where: "Informational inspection and the copy report only. Possible future topic-feedback revisions require evaluation and review first; no current rule, eligibility check or FeedbackService branch consumes these records.", source: "services/topic_service.py: _with_related_concepts; services/related_topic_concept_service.py: RelatedTopicConceptService.match; content/topic_concept_relations.json: versioned developer-curated associations", references: [], limitation: "Lexical mentions do not establish a complete statement, topic understanding, environmental support or a valid argument. Negation, stance and word sense are not evaluated. Related concepts are separate from direct matches, lemma matches and WordNet candidates." },
  "topic:wordnet": { what: "WordNet is an English lexical database that groups word senses into synonym sets, called synsets. These records show separate direct and cross-stage lookups when present.", why: "The code can suggest a limited shared-synset relation beyond direct/lemma matches.", how: "Direct suggestions compare unmatched single-word focus targets with noun concepts; cross-stage checks compare different single-word concepts with equal mapped POS. Each path probes corpus availability and requires exactly one shared synset for a candidate. Direct suggestions run only for Conclusion text: the coordinator enables them only when stage == CONCLUSION (essay_analysis_service.py) and the Conclusion Rule Base passes include_wordnet=True for the Conclusion text while prior-section and Body analyses pass False; earlier-section comparisons run inside Body/Conclusion rules when context is supplied.", source: "services/topic_service.py:_wordnet_status, _wordnet_suggestions; services/stage_evidence.py:_wordnet_candidates", references: [["NLTK WordNet guide", "https://www.nltk.org/howto/wordnet.html"], ["Princeton WordNet", "https://wordnet.princeton.edu/"]], limitation: "Senses are not disambiguated in sentence context; a shared synset candidate is not verified semantic equivalence.", next: "Candidates stay separate from confirmed focus coverage; cross-stage candidates can emit WordNet-specific Rule Events and are retained in Conclusion new-material paraphrase observations. FeedbackService does not treat them as verified meaning." },
  "topic:cross-stage": { what: "The actual lexical comparison records between the current stage and supplied prior sections.", why: "Body and Conclusion compare extracted concepts across sections.", how: "The existing helper compares normalized forms and compatible POS for surface/lemma pairs; optional WordNet calls are recorded separately.", source: "services/stage_evidence.py:compare_stage_concepts; services/body_rules.py; services/conclusion_rules.py", references: [["Witte & Faigley (1981)", "https://doi.org/10.58680/ccc198115912"]], limitation: "Lexical continuity does not prove support, coherence, synthesis, or contradiction.", next: "The resulting observations can be consumed by stage rules." },
  "rules:overview": { what: "The actual stage Rule Events and recorded evaluation statuses.", why: "These are the existing deterministic conditions that feed feedback.", how: "The selected Rule Base consumes the stage analysis and returns events. Trace statuses are derived from returned fields/events, not a second rule run.", source: "services/introduction_rules.py; services/body_rules.py; services/conclusion_rules.py", references: [["UNC Writing Center: Paragraphs", "https://writingcenter.unc.edu/tips-and-tools/paragraphs/"]], limitation: "Rules are structural/lexical observations, not semantic validation.", next: "Inspect fired events, evaluated non-triggered conditions, thresholds, and code." },
  "rules:triggered": { what: "Rule Events emitted during this stage's actual Rule Base execution.", why: "Events record the condition, evidence type, spans, and interpretation limits.", how: "The Rule Base adds an event when its existing event branch emits one.", source: "Stage Rule Base _rule_events functions", references: [], limitation: "An emitted event means its configured observation fired, not that a rhetorical claim was verified.", next: "Not Triggered separates explicitly evaluated alternatives." },
  "rules:not-triggered": { what: "Conditions whose outcomes are recorded as EVALUATED_NOT_TRIGGERED.", why: "It prevents an absent event from being misrepresented as a tested negative.", how: "The trace maps returned intermediate fields to rule status; anything without evidence remains NOT_RECORDED or NOT_APPLICABLE.", source: "services/research_inspector.py:build_rule_evaluation_trace", references: [], limitation: "Only returned conditions can be classified; the trace does not run rules a second time.", next: "Evidence, conditions and configuration shows the exact condition and its recorded basis." },
  "rules:conditions": { what: "The current stage's Rule IDs, conditions, status, and decision basis.", why: "It makes conditional behavior inspectable without rerunning the analyzer.", how: "Each row joins existing Rule Events to status evidence from the returned stage fields.", source: "services/research_inspector.py:rule_inventory, _observed_rule_decisions", references: [], limitation: "NOT_RECORDED means no result proves that branch was evaluated. Registry condition/configuration summaries abbreviate some algorithms (notably Introduction subordinator and list checks); stage findings explain the verified helper behavior.", next: "Evidence & Thresholds exposes spans and configured thresholds." },
  "rules:evidence": { what: "The actual evidence objects used by emitted events and the observed threshold values.", why: "Evidence links each condition back to the essay's spans and returned features.", how: "Event evidence is displayed as returned; no extra parser or Rule Base run is used.", source: "Stage Rule Base _rule_events functions", references: [], limitation: "Character spans anchor text but do not validate meaning.", next: "Code & References shows implementation locations and supporting context." },
  "rules:code": { what: "Resolved Rule Base function locations and rule-to-reference context.", why: "It supports source-level thesis review and separates academic rationale from the local heuristic.", how: "The response exposes rule metadata and line locations resolved from current Python functions.", source: "services/research_inspector.py:rule_inventory; stage Rule Base files", references: [["Project feedback rule mapping", "/docs/feedback_rule_references.md"]], limitation: "Cited work does not validate EssayScaff-specific conditions or thresholds.", next: "Feedback provenance and recorded priority shows how selected rule IDs are associated with messages." },
  "feedback:overview": { what: "The five actual feedback fields returned for this analyzed stage.", why: "It summarizes the user-facing result without rerunning FeedbackService.", how: "The cached API response supplies the existing feedback object and provenance.", source: "services/feedback_service.py; services/essay_analysis_service.py", references: [["Hattie & Timperley (2007)", "https://doi.org/10.3102/003465430298487"], ["Knight et al. (2020)", "https://doi.org/10.17239/jowr-2020.12.01.06"]], limitation: "These references inform formative feedback design generally, not EssayScaff message efficacy.", next: "Select a field to inspect its message and provenance." },
  "feedback:goal": { what: "The Current Goal text returned by FeedbackService for this stage.", why: "It communicates the stage-specific revision focus.", how: "The value is selected by the existing stage feedback function.", source: "services/feedback_service.py:generate, generate_body, generate_conclusion", references: [["Hattie & Timperley (2007)", "https://doi.org/10.3102/003465430298487"]], limitation: "A goal is guidance, not a readiness decision.", next: "Primary Feedback reports the selected main observation." },
  "feedback:primary": { what: "The actual Primary Feedback message and available selection evidence.", why: "It is the main deterministic message selected by the stage feedback priority branches.", how: "The current response may include trace-mode selection branch and rule IDs; otherwise those fields are explicitly unavailable.", source: "services/feedback_service.py", references: [["Hattie & Timperley (2007)", "https://doi.org/10.3102/003465430298487"], ["Knight et al. (2020)", "https://doi.org/10.17239/jowr-2020.12.01.06"]], limitation: "The message cannot establish correctness, meaning, or quality.", next: "Its provenance links back to events and spans." },
  "feedback:working": { what: "The actual positive/working observations returned for this stage.", why: "It shows which recorded signals the existing feedback code surfaced.", how: "The stage feedback function appends list items when their existing evidence conditions are met.", source: "services/feedback_service.py", references: [["Hattie & Timperley (2007)", "https://doi.org/10.3102/003465430298487"]], limitation: "Positive lexical overlap does not prove relevance or support.", next: "Needs Attention shows cautions that were actually returned." },
  "feedback:attention": { what: "The actual Needs Attention items returned for this stage.", why: "It displays cautions from the existing stage-specific branch conditions.", how: "The feedback code appends each item according to its condition and associates any available rule IDs.", source: "services/feedback_service.py", references: [["Knight et al. (2020)", "https://doi.org/10.17239/jowr-2020.12.01.06"]], limitation: "A caution is a review prompt, not a finding of incorrect writing.", next: "Next Step shows the selected revision suggestion." },
  "feedback:next": { what: "The actual Next Step message returned for the current stage.", why: "It provides a concrete review action while leaving writing decisions to the writer.", how: "The existing prioritized stage branch supplies the message and any recorded rule provenance.", source: "services/feedback_service.py", references: [["UNC Writing Center: Paragraphs", "https://writingcenter.unc.edu/tips-and-tools/paragraphs/"]], limitation: "The text does not rewrite the essay or validate a claim.", next: "Provenance links feedback fields to recorded evidence." },
  "feedback:provenance": { what: "The actual feedback-field-to-rule-event relationships.", why: "It makes the source of a message inspectable.", how: "FeedbackService records the rule ID, triggering condition, evidence, evidence type, and limitation when a selected field references an event.", source: "services/feedback_service.py:Feedback Provenance construction", references: [["Hattie & Timperley (2007)", "https://doi.org/10.3102/003465430298487"]], limitation: "No provenance item is returned for an unlinked message; absence is shown as unavailable, not guessed.", next: "Read the evidence span in the other process tabs." },
};

const STUDENT_TRANSPARENCY_MAIN = {
  processing: "Text Processing explains how the current section became spaCy annotations and application concepts.",
  topic: "Topic Matching explains current teacher focus terms, normalized terms, exact/lemma spans, and optional semantic-resource paths.",
  rules: "Rule Evidence reports actual emitted events and only those non-triggered statuses that the returned trace records.",
  feedback: "Feedback Explanation links the current five feedback fields to their recorded provenance.",
};

function transparencyData(result) {
  const analysis = result?.analysis || {};
  const trace = result?.research_trace || null;
  const stage = trace?.selected_stage || result?.stage_id || analysis.stage || "Not available";
  const stageTrace = trace?.stages?.[stage] || null;
  const linguistic = analysis.linguistic_observations || analysis.linguistic_analysis || stageTrace?.linguistic_observations || null;
  const paragraphs = analysis.paragraphs || analysis.conclusion_paragraphs || [];
  const fallbackSentences = paragraphs.flatMap((paragraph) => paragraph.sentence_spans || []);
  const sentences = linguistic?.sentences || fallbackSentences;
  const tokens = linguistic?.tokens || sentences.flatMap((sentence) => sentence.tokens || []);
  const concepts = stageTrace?.topic_service?.steps?.find((step) => step.id === "concept_extraction")?.output;
  return { result, analysis, trace, stage, stageTrace, linguistic, paragraphs, sentences, tokens, concepts };
}

function transparencyCurrentText(data) {
  const key = String(data.stage).toLowerCase();
  return data.stageTrace?.input_sections?.[key]
    ?? data.analysis.input_text
    ?? data.linguistic?.text
    ?? (key === "body" && Array.isArray(data.analysis.paragraphs)
      ? data.paragraphs.map((paragraph) => paragraph.text).join("\n\n")
      : "Section text not included in this response.");
}

function transparencySourceText(data) {
  return transparencyCurrentText(data);
}

function transparencyTokenRows(tokens, mapper) {
  return tokens.map((token, index) => mapper(token, token.index ?? index));
}

function transparencyFeedbackField(feedback, key, parent) {
  const value = feedback?.[key];
  if (Array.isArray(value)) {
    if (!value.length) transparencyText(parent, "No item was returned for this field.");
    else value.forEach((item) => transparencyText(parent, item));
  } else transparencyText(parent, transparencyValue(value));
}

function resolveStudentFeedbackProvenance(item, result) {
  const events = Array.isArray(result.analysis?.rule_evidence) ? result.analysis.rule_evidence : [];
  const event = events.find((candidate) => candidate.rule_id === item.rule_id);
  return {
    ...item,
    triggering_condition: item.triggering_condition ?? event?.triggering_condition,
    evidence_type: item.evidence_type ?? event?.evidence_type,
    limitations: item.limitations ?? item.limitation ?? event?.limitations ?? event?.limitation,
    actual_evidence: item.actual_evidence ?? item.evidence ?? event?.actual_evidence ?? event?.evidence,
  };
}

function renderStudentRuleEvents(parent, events) {
  if (!Array.isArray(events)) {
    transparencyText(parent, "Not available — this response did not return a Rule Event list.");
    return;
  }
  if (!events.length) {
    transparencyText(parent, "No Rule Events were emitted for this stage.");
    return;
  }
  transparencyExpandableTable(
    parent,
    `Expand ${events.length} emitted Rule Events`,
    ["Rule ID", "Condition", "Evidence type", "Status"],
    events.map((event) => [
      event.rule_id,
      event.triggering_condition,
      event.evidence_type,
      event.triggered === false || event.fired === false ? "Not triggered" : "Triggered / emitted",
    ]),
  );
  events.forEach((event) => transparencyExpandable(parent, `${event.rule_id}: actual evidence and spans`, event.actual_evidence ?? event.evidence));
}

function transparencyExpandable(parent, label, evidence) {
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = label;
  details.appendChild(summary);
  transparencyEvidence(details, evidence);
  parent.appendChild(details);
  return details;
}

function transparencyExpandableTable(parent, label, headings, rows, emptyMessage = "Not available") {
  const details = document.createElement("details");
  details.className = "transparency-data-disclosure";
  details.open = false;
  const summary = document.createElement("summary");
  summary.textContent = label;
  details.appendChild(summary);
  const content = document.createElement("div");
  content.className = "transparency-table-disclosure";
  transparencyTable(content, headings, rows, emptyMessage);
  details.appendChild(content);
  parent.appendChild(details);
  return details;
}

function transparencyReferenceList(parent, references) {
  if (!Array.isArray(references) || references.length === 0) {
    transparencyText(parent, "No external reference is mapped to this exact implementation condition.");
    return;
  }
  const list = document.createElement("ul");
  for (const [label, href] of references) {
    const item = document.createElement("li");
    if (href.startsWith("http")) {
      const link = document.createElement("a");
      link.textContent = label;
      link.href = href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      item.appendChild(link);
    } else item.textContent = label;
    list.appendChild(item);
  }
  parent.appendChild(list);
}

function transparencyProcessSection(parent, title, content) {
  const section = transparencySection(parent, title);
  // Two arguments create a container that the caller will populate, not an empty result.
  if (arguments.length < 3) return section;
  if (typeof content === "string") transparencyText(section, content);
  else if (content !== undefined && content !== null) transparencyEvidence(section, content);
  else transparencyText(section, "Not available — no value was included in this response.");
  return section;
}

function transparencyProcessExplanation(panel, mainKey, subKey, result, data) {
  const info = STUDENT_TRANSPARENCY_PROCESS_INFO[`${mainKey}:${subKey}`];
  if (!info) {
    transparencyText(panel, "Process explanation is not available.");
    return;
  }
  const lexical = data.analysis.lexical_topic_evidence || {};
  const input = {
    stage: data.stage,
    section_text: transparencyCurrentText(data),
    assignment_topic: data.trace?.teacher_context?.assignment_topic || data.analysis.assignment_topic || "Not available",
    focus_source: lexical.focus_source || data.trace?.teacher_context?.focus_source || "Not available",
    focus_terms: lexical.focus_terms || data.trace?.teacher_context?.focus_terms?.map((term) => term.term) || "Not available",
    prior_sections: data.stageTrace?.input_sections
      ? Object.fromEntries(Object.entries(data.stageTrace.input_sections).filter(([key]) => key !== String(data.stage).toLowerCase()))
      : "Prior-section inputs not included in this response.",
  };
  const what = transparencyProcessSection(panel, "1. What is this process?");
  transparencyText(what, `Simple explanation: ${info.what}`);
  transparencyText(what, `Technical explanation: ${info.how}`);
  transparencyProcessSection(panel, "2. Why is it used?", info.why);
  transparencyProcessSection(panel, "3. How does the actual algorithm work?", info.how);
  transparencyExpandable(transparencyProcessSection(panel, "4. Retained essay context (not necessarily this component's direct input)"), "Show retained context; inspect the causal walkthrough for component inputs", input);
  const output = transparencyProcessSection(panel, "5. Actual output and intermediate evidence");
  transparencyRenderSubtabEvidence(output, mainKey, subKey, result, data);
  const decisions = transparencyProcessSection(panel, "6. Conditions and recorded decisions");
  transparencyRenderDecisionSummary(decisions, mainKey, subKey, result, data);
  transparencyProcessSection(panel, "7. Python file and function", info.source);
  const refs = transparencyProcessSection(panel, "8. Supporting technical or academic references");
  transparencyReferenceList(refs, info.references);
  transparencyText(refs, "These references support APIs or general concepts; they do not validate EssayScaff-specific heuristics.");
  transparencyProcessSection(panel, "9. Known limitations", info.limitation);
  transparencyProcessSection(panel, "10. Navigation / source-defined next consumer (not observed usage)", info.next);
}

const TRANSPARENCY_EVIDENCE_TYPES = {
  OBSERVED: "OBSERVED — returned directly by this analysis response.",
  DERIVED: "DERIVED — calculated in the browser from recorded values.",
  SOURCE_VERIFIED: "SOURCE-VERIFIED LOGIC — source conditions explained using retained inputs; not an observed execution log.",
  STATIC: "STATIC EXPLANATION — general description; not proof that an operation executed during this analysis.",
  SKIPPED: "SKIPPED — a recorded execution status says this operation did not run.",
  NOT_APPLICABLE: "NOT APPLICABLE — the operation does not apply to this stage or available context.",
  NOT_RECORDED: "NOT RECORDED — not present in the existing evidence.",
  REPORT_ONLY: "REPORT ONLY — available in Complete Evidence but not in this panel.",
};

function transparencyEvidenceTypeTag(kind) {
  return ({ SOURCE_VERIFIED: "SOURCE-VERIFIED LOGIC", STATIC: "STATIC EXPLANATION", NOT_APPLICABLE: "NOT APPLICABLE", NOT_RECORDED: "NOT RECORDED", REPORT_ONLY: "REPORT ONLY" })[kind] || (TRANSPARENCY_EVIDENCE_TYPES[kind] ? kind : "NOT RECORDED");
}

function transparencyEvidenceTypeLegend(parent) {
  const details = document.createElement("details");
  details.className = "transparency-evidence-legend";
  const summary = document.createElement("summary");
  summary.textContent = "Evidence types used in this panel";
  details.appendChild(summary);
  for (const [kind, description] of Object.entries(TRANSPARENCY_EVIDENCE_TYPES)) {
    transparencyText(details, `${kind} — ${description}`);
  }
  parent.appendChild(details);
}

function transparencyJourney(parent, rows, emptyMessage = "No recorded journey steps were returned for this view.") {
  if (!Array.isArray(rows) || !rows.length) {
    transparencyText(parent, emptyMessage);
    return;
  }
  transparencyTable(
    parent,
    ["Journey step", "Evidence type", "Actual recorded value", "Recorded source"],
    rows.map(([step, kind, value, source]) => [step, transparencyEvidenceTypeTag(kind), value, source || "This analysis response."]),
  );
}

// Which recorded field actually carries this stage's exact text. All agreeing
// sources are named; disagreement is reported instead of picking one silently.
function transparencyTextSources(data) {
  const key = String(data.stage).toLowerCase();
  const sources = [
    ["analysis.input_text", data.analysis.input_text],
    ["analysis.linguistic_observations.text", data.analysis.linguistic_observations?.text],
    ["analysis.linguistic_analysis.text", data.analysis.linguistic_analysis?.text],
    [`research_trace.stages.${data.stage}.linguistic_observations.text`, data.stageTrace?.linguistic_observations?.text],
    [`research_trace.stages.${data.stage}.input_sections.${key}`, data.stageTrace?.input_sections?.[key]],
    ["supplied_text", data.result?.supplied_text],
  ].filter(([, value]) => typeof value === "string");
  if (!sources.length) return { text: null, source: "Section text not included in this response." };
  const agrees = sources.every(([, value]) => value === sources[0][1]);
  return {
    text: agrees ? sources[0][1] : null,
    source: agrees ? sources.map(([path]) => path).join(" · all agree")
      : sources.map(([path]) => path).join("; ") + " — retained sources disagree; no single source claimed.",
  };
}

function transparencyAnalyzedEssay(parent, data, title = "Original analyzed writing for this stage") {
  const section = transparencySection(parent, title);
  const resolved = transparencyTextSources(data);
  if (resolved.text === null) {
    transparencyText(section, `Exact source: ${resolved.source}`);
    return section;
  }
  studentSourceViewer(section, resolved.text, `${data.stage}: exact analyzed text used by this process`);
  transparencyText(section, `Exact source: ${resolved.source}. Zero-based character offsets elsewhere in this panel refer to this text.`, "student-input-provenance");
  return section;
}

// Minimal shared handoff block (output -> next consumer). It renders only
// implementation-verified next steps plus any recorded consumer evidence, so a
// general description can never be mistaken for proof of consumption. Panels
// whose table rows are counted by verification tests receive plain text lines.
const TRANSPARENCY_HANDOFF_PLAIN = new Set(["rules:triggered", "rules:not-triggered", "rules:trace"]);

function transparencyHandoff(parent, mainKey, subKey, result, data) {
  const key = `${mainKey}:${subKey}`;
  const entry = TRANSPARENCY_HANDOFF[key];
  if (!entry) return null;
  const rows = entry(result, data);
  if (!Array.isArray(rows) || !rows.length) return null;
  const section = transparencySection(parent, "Output handoff — where this output goes next");
  if (TRANSPARENCY_HANDOFF_PLAIN.has(key)) {
    for (const [step, kind, value, source] of rows) {
      transparencyText(section, `${step} — [${transparencyEvidenceTypeTag(kind)}] ${value} Source: ${source || "This analysis response."}`);
    }
  } else transparencyJourney(section, rows);
  return section;
}

const TRANSPARENCY_HANDOFF = {
  "nlp:overview": () => [["Next process: spaCy Pipeline, then token/lemma/POS/dependency views of the same Doc", "STATIC", "These tabs are views of one parsed document; opening them does not parse again.", "static/app.js renderNlpTransparency; services/nlp_service.py analyze_doc"]],
  "nlp:pipeline": (result, data) => [
    ["Annotated Doc → NLPService.analyze_doc serialized token/sentence records", "OBSERVED", "Recorded counts and token records in the Sentences/Tokens tabs come from the same response.", "analysis.linguistic_observations / research_trace…topic_service.steps.spacy_document_processing"],
    ["Same Doc → TopicService._extract_concepts and _find_matches", "OBSERVED", `Concept extraction step recorded execution_status ${data.stageTrace?.topic_service?.steps?.find((step) => step.id === "concept_extraction")?.execution_status ?? "not recorded"} with candidate_count ${data.stageTrace?.topic_service?.steps?.find((step) => step.id === "concept_extraction")?.candidate_count ?? "not recorded"}.`, "research_trace…topic_service.steps.concept_extraction"],
    ["Prepared observations → stage Rule Base (no second parse)", "STATIC", "The Rule Base reads prepared TopicService output; see Rule Base for emitted events.", "services/introduction_rules.py analyze; services/body_rules.py analyze; services/conclusion_rules.py analyze"],
  ],
  "nlp:sentences": () => [["Sentence spans → clause/context/paragraph checks", "STATIC", "Stage findings name the sentence records they read; no consumer value is copied here.", "services/stage_evidence.py clause_candidates_from_sentences"]],
  "nlp:tokens": () => [["Token offsets → phrase matching, concept extraction and evidence spans", "STATIC", "Recorded match and concept spans reuse these offsets.", "services/topic_service.py _find_matches, _extract_concepts"]],
  "nlp:lemmas": () => [["Lemmas → normalized focus matching and concept grouping", "STATIC", "Normalized matches list their lemma sequence in Topic Matching.", "services/topic_service.py _lemma, _find_matches"]],
  "nlp:pos": () => [["POS/tags → clause filters, concept eligibility and WordNet POS mapping", "STATIC", "WordNet POS values are recorded per focus term in Topic Matching → Normalization.", "services/introduction_rules.py FINITE_TAGS; services/stage_evidence.py _wordnet_candidates"]],
  "nlp:dependencies": () => [["Subject/predicate edges → clause candidates", "STATIC", "Stage Observations records the accepted candidates, not every edge.", "services/stage_evidence.py clause_candidates_from_sentences"]],
  "nlp:chunks": () => [["Noun chunks → noun-phrase concepts", "STATIC", "Concept Extraction lists the concepts built from chunks and noun tokens.", "services/topic_service.py _extract_concepts"]],
  "concept:overview": (result, data) => [["Concepts → Body/Conclusion recurrence, cross-stage comparison, Conclusion new-material checks", "STATIC", data.stage === "INTRODUCTION" ? "This Introduction response records no consumer of concepts." : "Recorded comparison/paragraph structures that reuse concepts are listed in Concept Extraction.", "services/body_rules.py, services/conclusion_rules.py, services/stage_evidence.py"]],
  "concept:concepts": () => [["Concept groups → Occurrence records and downstream consumers", "STATIC", "Open Occurrences & Sources for per-occurrence spans and recorded use.", "services/topic_service.py _extract_concepts"]],
  "concept:occurrences": (result, data) => [["Occurrences → cross-stage comparison pairs (Body/Conclusion)", "STATIC", data.stage === "INTRODUCTION" ? "Introduction rules do not consume concepts." : "Compare the spans with Topic Matching → Cross-stage pairs.", "services/stage_evidence.py compare_stage_concepts"]],
  "topic:overview": (result, data) => [["Coverage → stage topic/context observations, Rule Events and feedback checks", "STATIC", "Rule Base → Triggered lists the emitted events; Feedback Engine lists field links.", "services/*_rules.py; services/feedback_service.py"]],
  "topic:focus-terms": () => [["Prepared targets → _find_matches windows and (when enabled) the direct WordNet input set", "STATIC", "WordNet tab shows whether the direct path ran for this stage.", "services/topic_service.py _find_matches, _wordnet_suggestions"]],
  "topic:normalization": () => [["Normalized forms → deduplicated targets and lemma-window comparison", "STATIC", "Lemma Matches shows the recorded normalized matches.", "services/topic_service.py _unique_focus_terms, _find_matches"]],
  "topic:direct": () => [["Direct match spans → lexical_topic_evidence.matches and coverage counts", "OBSERVED", "The recorded match list is displayed in this panel and reused in coverage counts.", "analysis.lexical_topic_evidence.matches"]],
  "topic:lemma": () => [["Normalized match spans → lexical_topic_evidence.matches with method preserved", "OBSERVED", "The recorded match list is displayed in this panel.", "analysis.lexical_topic_evidence.matches"]],
  "topic:related": () => [["Related-concept records → inspection and Copy Full Analysis only", "OBSERVED", "Recorded decision use: informational only; no rule or feedback field consumes them.", "related_topic_concept_evidence.informational_only, affects_rules_or_feedback"]],
  "topic:wordnet": (result, data) => {
    const events = (result.analysis?.rule_evidence || []).filter((event) => event.rule_id.includes("WORDNET"));
    return [
      ["Direct suggestions → analysis.lexical_topic_evidence.wordnet_relationship_candidates (Conclusion only)", "OBSERVED", `Recorded candidate items: ${Array.isArray(result.analysis?.lexical_topic_evidence?.wordnet_relationship_candidates) ? result.analysis.lexical_topic_evidence.wordnet_relationship_candidates.length : "not recorded for this stage"}.`, "analysis.lexical_topic_evidence.wordnet_relationship_candidates"],
      ["Cross-stage candidates → emitted WordNet Rule Events", events.length ? "OBSERVED" : "NOT_RECORDED", events.length ? events.map((event) => event.rule_id).join(", ") : "No WordNet Rule Event was emitted for this response.", "analysis.rule_evidence"],
      ["Cross-stage candidates → Conclusion new-material paraphrase observations", data.stage === "CONCLUSION" ? "OBSERVED" : "NOT_RECORDED", data.stage === "CONCLUSION" ? `candidate_paraphrase_relationships: ${result.analysis?.new_material_observations?.candidate_paraphrase_relationships?.length ?? 0} recorded item(s).` : "Not applicable for this stage.", "analysis.new_material_observations.candidate_paraphrase_relationships"],
      ["Any WordNet record → FeedbackService", "SOURCE_VERIFIED", events.length && (result.feedback?.["Feedback Provenance"] || []).some((item) => events.some((event) => event.rule_id === item.rule_id)) ? "At least one WordNet Rule Event appears in Feedback Provenance; inspect the source before attributing selection causality." : "No Feedback Provenance item in this response references a WordNet Rule Event. Source verification: FeedbackService does not read WordNet candidates; cross-stage events are informational, not feedback-selection conditions.", "feedback['Feedback Provenance']; services/feedback_service.py generate_body / generate_conclusion"],
    ];
  },
  "topic:cross-stage": (result, data) => {
    const keys = ["introduction_to_body_continuity", "introduction_to_conclusion_continuity", "body_to_conclusion_continuity"];
    const events = (result.analysis?.rule_evidence || []).filter((event) => keys.some((key) => event.rule_id.includes(key.split("_to_")[0].toUpperCase()) && event.rule_id.includes("CONTINUITY")));
    return [
      ["Comparison records → stage continuity observations and rule events", events.length ? "OBSERVED" : "NOT_RECORDED", events.length ? events.map((event) => event.rule_id).join(", ") : "No continuity Rule Event was emitted for this response.", "analysis.rule_evidence"],
      ["Comparison records → FeedbackService links", "OBSERVED", (result.feedback?.["Feedback Provenance"] || []).filter((item) => events.some((event) => event.rule_id === item.rule_id)).map((item) => `${item.feedback_field} ← ${item.rule_id}`).join("; ") || "No feedback field in this response links to a continuity comparison.", "feedback['Feedback Provenance']"],
      ["Earlier-section concepts → not returned", "NOT_RECORDED", "Only the selected stage trace is returned, so prior-stage concept lists cannot be re-listed here; recorded pair evidence names every compared occurrence.", "app.py analyze_payload research_trace.stages selection"],
    ];
  },
  "rules:overview": () => [["Reconstructed evaluation trace → inspection only", "SOURCE_VERIFIED", "FeedbackService reads stage observations for selection and emitted events for provenance. It never reads this later reconstructed trace.", "services/research_inspector.py build_rule_evaluation_trace; services/feedback_service.py"]],
  "rules:stage": () => [["Stage findings → _rule_events → analysis.rule_evidence", "STATIC", "Emitted events are listed under Triggered.", "services/*_rules.py _rule_events"]],
  "rules:triggered": (result, data) => [["Emitted events → Feedback Provenance field links", "OBSERVED", `Feedback Provenance items in this response: ${Array.isArray(result.feedback?.["Feedback Provenance"]) ? result.feedback["Feedback Provenance"].length : "not recorded"}.`, "feedback['Feedback Provenance']"]],
  "rules:not-triggered": () => [["Recorded non-triggered statuses → inspection only", "STATIC", "An absent event is never shown as a tested negative beyond the recorded decision basis.", "services/research_inspector.py _observed_rule_decisions"]],
  "rules:evidence": (result, data) => [["Recorded evidence and thresholds → Feedback Provenance resolution", "OBSERVED", "Provenance links are resolved against analysis.rule_evidence in Feedback Engine.", "analysis.rule_evidence; resolveStudentFeedbackProvenance"]],
  "rules:trace": () => [["Trace rows → inspection only (not an input to FeedbackService)", "SOURCE_VERIFIED", "Stage observations select feedback; emitted events supply provenance. This trace is constructed afterwards.", "services/essay_analysis_service.py build_rule_evaluation_trace call site"]],
  "rules:sources": () => [["Implementation metadata → thesis source review", "STATIC", "Line numbers identify current functions; they are not an execution log.", "services/research_inspector.py rule_inventory"]],
  "engine:overview": () => [["Selected branches and rule IDs → student Writing Feedback panel", "OBSERVED", "The five original backend fields are shown in Final Feedback → Five Fields.", "feedback fields + research_trace…feedback_decisions"]],
  "engine:goal": () => [["Current Goal → student Writing Feedback header", "OBSERVED", "Final Feedback shows the original value verbatim.", "feedback['Current Goal']"]],
  "engine:primary": () => [["Primary Feedback → Writing Tutor prepared guidance (where a mapping exists)", "OBSERVED", "The prepared lesson is shown with the selected message in this panel.", "static/app.js studentFeedbackPresentation"]],
  "engine:working": () => [["What's Working → student Writing Feedback panel", "OBSERVED", "Original list items are shown in Final Feedback.", "feedback[\"What's Working\"]"]],
  "engine:attention": () => [["Needs Attention → student Writing Feedback panel", "OBSERVED", "Original list items are shown in Final Feedback.", "feedback['Needs Attention']"]],
  "engine:next": () => [["Next Step → student Writing Feedback panel", "OBSERVED", "The original message is shown in Final Feedback.", "feedback['Next Step']"]],
  "engine:provenance": () => [["Provenance items → field-to-event links", "OBSERVED", "Each link resolves to an emitted event in analysis.rule_evidence.", "feedback['Feedback Provenance']"]],
  "final:overview": () => [["Cached response → Writing Feedback, transparency panels and Copy Full Analysis", "OBSERVED", "All three views read the same stored response.", "static/app.js displayFeedback, currentAnalysisForExport"]],
  "final:fields": () => [["Five original fields → student-visible presentation", "OBSERVED", "Writing Tutor presentation may add prepared guidance alongside these values.", "feedback fields"]],
  "final:response": () => [["Response → guarded browser cache (no save)", "STATIC", "Draft saving and submission are separate requests.", "static/app.js performStageAnalysis; app.py analyze_payload"]],
  "final:complete": () => [["Complete evidence → export index and Copy Full Analysis", "OBSERVED", "Each record keeps its source path.", "static/app.js buildFullAnalysisReport"]],
  "final:limitations": () => [["Recorded limits → interpretation of every panel", "OBSERVED", "These limits travel with the response.", "analysis.interpretation_limit, feedback.interpretation_limit, research_trace.limitations"]],
};

// Educational groupings below describe data dependencies, not separate NLP runs.
// See docs/transparency_process_map.md for the source-verified call map.
let transparencyLastContext = null;

function transparencyLabel(key) {
  return String(key).replace(/_/g, " ").replace(/\b\w/, (letter) => letter.toUpperCase());
}

function transparencyDisclosure(parent, title, render) {
  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = title;
  details.appendChild(summary);
  let rendered = false;
  const populate = () => {
    if (rendered) return;
    rendered = true;
    render(details);
  };
  details.addEventListener("toggle", () => { if (details.open) populate(); });
  // Also supports keyboard-activated summaries; the toggle remains authoritative.
  summary.addEventListener("click", populate);
  parent.appendChild(details);
  return details;
}

function renderTransparencyRecord(parent, value) {
  // Structured, lossless evidence inspection. No source code, JSON dumps, row
  // truncation, reparsing, or guessed values. Nested records are opened on demand.
  if (value === undefined || value === null || typeof value !== "object") {
    transparencyText(parent, value === undefined ? "Not available in the cached response." : value === null ? "Not recorded (null)." : String(value));
    return;
  }
  if (Array.isArray(value) && !value.length) {
    transparencyText(parent, "Recorded empty list — no items returned.");
    return;
  }
  const rows = Array.isArray(value) ? value.map((item, index) => [String(index), item]) : Object.entries(value);
  const scalarRows = rows.filter(([, item]) => item === null || typeof item !== "object");
  if (scalarRows.length) transparencyTable(parent, [Array.isArray(value) ? "Record index (zero-based)" : "Recorded field", "Actual value"], scalarRows.map(([key, item]) => [transparencyLabel(key), item === null ? "Not recorded (null)" : item === "" ? "Recorded empty text" : item]));
  for (const [key, item] of rows.filter(([, item]) => item !== null && typeof item === "object")) {
    const count = Array.isArray(item) ? `${item.length} records` : `${Object.keys(item).length} fields`;
    transparencyDisclosure(parent, `${Array.isArray(value) ? "Record " : ""}${transparencyLabel(key)} · ${count}`, (target) => renderTransparencyRecord(target, item));
  }
  if (!rows.length) transparencyText(parent, "Recorded empty object — no fields returned.");
}

function transparencyDraftIdentity(text, stage) {
  let hash = 2166136261;
  for (const character of text) hash = Math.imul(hash ^ character.codePointAt(0), 16777619) >>> 0;
  return `${stage} · ${Array.from(text).length} characters · ${hash.toString(16).padStart(8, "0")}`;
}

const TRANSPARENCY_EXTRA_INFO = {
  input: { what: "The exact writing and assignment supplied for this analysis.", how: "runStageAnalysis posts the selected stage and available earlier writing. Flask resolves an authorized assignment when an assignment ID is supplied, or uses practice topic/focus values, then checks stage, types, nonblank text and size limits.", why: "Rules need the correct draft and assignment targets before comparing any evidence.", where: "Validated arguments go to EssayAnalysisService.analyze, then shared teacher-context preparation and each supplied section's TopicService call.", source: "static/app.js: runStageAnalysis; app.py: analyze_stage, analyze_payload" },
  sentences: { what: "A sentence boundary marks where one sentence ends and another starts.", how: "The installed spaCy parser supplies Doc.sents. NLPService.analyze_doc takes each sentence's first and last nonspace tokens and records their original start/end positions and text.", why: "Subject and predicate observations must belong to an identified sentence; rules also compare adjacent sentence records.", where: "Introduction clause, context and subordinator checks; Body sentence/detail/unity checks; Conclusion clause, synthesis and final-sentence checks.", source: "services/nlp_service.py: analyze_doc; services/stage_evidence.py: sentence_segments_in_span, clause_candidates_from_sentences" },
  stage: { what: "The current stage's structural and lexical observations, before messages are selected.", how: "The Rule Base reuses prepared TopicService output. Introduction checks root clauses, focus/context, fragments, subordinators and supported clause counts. Body/Conclusion split blank-line paragraphs and filter existing spans; they compare clauses, repeated wording and supplied earlier concepts without reparsing.", why: "Each writing stage needs its own inspectable observations rather than one overall quality score.", where: "The stage's _rule_events and FeedbackService consume these findings. Cross-stage WordNet is nested inside applicable comparisons.", source: "services/introduction_rules.py: analyze; services/body_rules.py: analyze; services/conclusion_rules.py: analyze; services/stage_evidence.py" },
  response: { what: "The completed analysis travels back to the browser as JSON.", how: "Flask selects the requested stage, compacts repeated data and calls jsonify. JavaScript checks request/input/assignment/stage/view snapshots before caching. studentFeedbackPresentation uses verified branch/provenance and prepared content for concise guidance, preserving original backend messages separately.", why: "The evidence and teaching presentation must describe the draft that was actually analyzed.", where: "The same cached response and presentation model supply Writing Feedback, its technical trace and Copy Full Analysis. Draft saving, revisions and submission are separate requests.", source: "app.py: compact_student_transparency_trace, compact_student_feedback, analyze_payload; static/app.js: runStageAnalysis, displayFeedback, studentFeedbackPresentation, currentAnalysisForExport" },
};

function transparencyExplanation(parent, info) {
  const grid = document.createElement("div");
  grid.className = "transparency-explanation-grid";
  transparencyText(parent, "SOURCE-VERIFIED LOGIC / STATIC EXPLANATION — implementation context below is not a per-request execution log.", "field-help");
  for (const [label, text] of [["WHAT is it?", info.what], ["HOW does it work?", info.how], ["WHY do we need it?", info.why], ["WHERE is it used?", info.where || info.next]]) {
    const block = document.createElement("div");
    const heading = document.createElement("h4");
    heading.textContent = label;
    block.appendChild(heading);
    transparencyText(block, text);
    grid.appendChild(block);
  }
  parent.appendChild(grid);
  transparencyDisclosure(parent, "Source references — file, function and purpose", (target) => {
    transparencyTable(target, ["File / recorded reference", "Function", "Purpose"], String(info.source || "Not returned").split(";").map((reference) => {
      const separator = reference.indexOf(":");
      return separator < 0 ? [reference.trim(), "Function not named in this reference", info.why]
        : [reference.slice(0, separator).trim(), reference.slice(separator + 1).trim(), info.why];
    }));
  });
  if (info.limitation) transparencyText(parent, info.limitation, "field-help");
}

const TRANSPARENCY_LABELS = {
  NOUN: "noun: a person, place, thing or idea", PROPN: "proper noun: a name", VERB: "verb: an action or state", AUX: "auxiliary: a helping verb", ADJ: "adjective: describes a noun", ADV: "adverb: modifies an action or description", PRON: "pronoun: stands for a noun", DET: "determiner: marks a noun phrase", ADP: "adposition: a preposition-like link", CCONJ: "coordinating conjunction: joins items", SCONJ: "subordinating conjunction: introduces a dependent clause", PART: "particle: a small grammatical marker", PUNCT: "punctuation", NUM: "number", INTJ: "interjection", SYM: "symbol", X: "other word type",
  VB: "base-form verb", VBP: "present-tense verb, usually non-third-person singular", VBZ: "third-person singular present verb", VBD: "past-tense verb", VBG: "present participle or gerund", VBN: "past participle", MD: "modal auxiliary", NN: "singular/common noun", NNS: "plural common noun", NNP: "singular proper noun", NNPS: "plural proper noun", JJ: "adjective", JJR: "comparative adjective", JJS: "superlative adjective", RB: "adverb", RBR: "comparative adverb", RBS: "superlative adverb", IN: "preposition or subordinator", DT: "determiner", PRP: "personal pronoun", "PRP$": "possessive pronoun", TO: "to marker", CC: "coordinating conjunction", CD: "number", HYPH: "hyphen", ".": "sentence punctuation", ",": "comma", POS: "possessive ending", EX: "existential there", WDT: "wh-determiner", WP: "wh-pronoun", WRB: "wh-adverb",
  ROOT: "sentence's top-level grammatical head", nsubj: "nominal subject linked to its predicate", nsubjpass: "subject in a passive construction", csubj: "clause acting as a subject", csubjpass: "clausal subject in a passive construction", dobj: "direct object linked to a verb", obj: "object", iobj: "indirect object", pobj: "object of a preposition", advcl: "adverbial clause attached to another clause", ccomp: "clause used as a complement", xcomp: "open clause complement", relcl: "relative clause modifying a noun", conj: "coordinated word or clause", cc: "coordinating conjunction link", aux: "helping verb attached to a predicate", auxpass: "passive auxiliary", cop: "linking verb", det: "determiner attached to a noun", poss: "possessive modifier", case: "case/possessive marker", compound: "compound-word modifier", amod: "adjective modifier of a noun", advmod: "adverb modifier", neg: "negation marker", prep: "prepositional link", mark: "marker introducing a subordinate clause", punct: "punctuation attachment", attr: "attribute after a linking verb", acomp: "adjective complement", oprd: "object predicate", appos: "appositional noun phrase", nmod: "nominal modifier", npadvmod: "noun phrase used as an adverbial modifier", nummod: "numeric modifier", dative: "dative/indirect-object relation", agent: "agent of a passive construction", prt: "verb particle", quantmod: "quantity modifier", intj: "interjection attachment", dep: "unspecified dependency", expl: "expletive subject", preconj: "pre-coordination marker", predet: "predeterminer", acl: "clause modifying a noun", parataxis: "loosely connected clause",
};

function transparencyLabelExplanation(label) {
  return TRANSPARENCY_LABELS[label] || "No plain-English mapping retained for this model label; the recorded label is preserved.";
}

function buildDependencyTreeModel(sentence, fullText) {
  // Pure builder: recorded spaCy edges → layout model. No analysis is rerun;
  // node identity is the recorded character start (repeated words stay distinct).
  const issues = [];
  const edges = Array.isArray(sentence?.dependencies) ? sentence.dependencies : [];
  const tokens = Array.isArray(sentence?.tokens) ? sentence.tokens : [];
  const tokenByStart = new Map();
  for (const token of tokens) {
    if (Number.isInteger(token?.start)) tokenByStart.set(token.start, token);
  }
  const nodesByKey = new Map();
  const nodeList = [];
  for (const edge of edges) {
    if (!Number.isInteger(edge?.start)) {
      issues.push("A dependency record without a valid token start was skipped; no node was invented for it.");
      continue;
    }
    const key = String(edge.start);
    if (nodesByKey.has(key)) continue;
    const token = tokenByStart.get(edge.start) || null;
    const node = {
      key,
      text: typeof edge.text === "string" ? edge.text : (token?.text ?? ""),
      start: edge.start,
      end: Number.isInteger(edge.end) ? edge.end : (token?.end ?? null),
      pos: token?.pos ?? null,
      tag: token?.tag ?? null,
      dependency: typeof edge.dependency === "string" ? edge.dependency : null,
      headText: typeof edge.head === "string" ? edge.head : null,
      headStart: Number.isInteger(edge.head_start) ? edge.head_start : null,
      isRoot: edge.dependency === "ROOT",
      explanation: transparencyLabelExplanation(edge.dependency),
      posExplanation: token?.pos ? transparencyLabelExplanation(token.pos) : "POS was not returned for this token.",
      depth: 0,
      col: 0,
      resolved: true,
      headKey: null,
      unresolvedReason: null,
    };
    nodesByKey.set(key, node);
    nodeList.push(node);
  }
  const roots = nodeList.filter((node) => node.isRoot);
  let rootKey = null;
  if (roots.length === 1) {
    rootKey = roots[0].key;
  } else if (roots.length > 1) {
    rootKey = roots[0].key;
    issues.push(`Multiple ROOT records (${roots.length}) were recorded for this sentence; the first is used for layout and every ROOT node stays marked as ROOT.`);
  } else {
    const selfHeaded = nodeList.filter((node) => node.headStart === node.start);
    if (selfHeaded.length === 1) {
      rootKey = selfHeaded[0].key;
      issues.push("No ROOT dependency label was recorded; the token whose recorded head is itself is used as the layout root.");
    } else if (selfHeaded.length > 1) {
      rootKey = selfHeaded[0].key;
      issues.push(`No ROOT label was recorded; ${selfHeaded.length} tokens record themselves as head; the first is used for layout.`);
    } else if (nodeList.length) {
      issues.push("No ROOT label and no self-headed token were recorded for this sentence; nodes are shown in token order without a tree root.");
    }
  }
  const childrenByHead = new Map();
  for (const node of nodeList) {
    if (node.key === rootKey) {
      node.resolved = true;
      node.headKey = null;
      continue;
    }
    if (node.headStart === null) {
      node.resolved = false;
      node.unresolvedReason = "Head position was not recorded for this dependency; no connector was drawn.";
      issues.push(`Unresolved dependency for "${node.text}" [${node.start}, ${node.end}): head position was not recorded.`);
      continue;
    }
    if (!nodesByKey.has(String(node.headStart))) {
      node.resolved = false;
      node.unresolvedReason = `Recorded head position ${node.headStart} does not match any token in this sentence; no connector was drawn to an unverified head.`;
      issues.push(`Unresolved dependency for "${node.text}" [${node.start}, ${node.end}): head position ${node.headStart} is not a token of this sentence.`);
      continue;
    }
    node.headKey = String(node.headStart);
    if (!childrenByHead.has(node.headKey)) childrenByHead.set(node.headKey, []);
    childrenByHead.get(node.headKey).push(node);
  }
  for (const list of childrenByHead.values()) list.sort((a, b) => a.start - b.start);
  let nextLeafCol = 0;
  let maxDepth = 0;
  const assigned = new Set();
  const visit = (node, depth) => {
    node.depth = depth;
    if (depth > maxDepth) maxDepth = depth;
    assigned.add(node.key);
    const children = childrenByHead.get(node.key) || [];
    if (!children.length) {
      node.col = nextLeafCol;
      nextLeafCol += 1;
      return;
    }
    for (const child of children) visit(child, depth + 1);
    node.col = (children[0].col + children[children.length - 1].col) / 2;
  };
  if (rootKey) visit(nodesByKey.get(rootKey), 0);
  for (const node of nodeList) {
    if (assigned.has(node.key)) continue;
    node.depth = 0;
    node.col = nextLeafCol;
    nextLeafCol += 1;
    node.resolved = false;
    if (!node.unresolvedReason) node.unresolvedReason = "This token could not be reached from the recorded root; it is shown in token order without a connector.";
    if (!issues.some((issue) => issue.includes(`"${node.text}"`) && issue.includes(`[${node.start}`))) {
      issues.push(`Unreachable token "${node.text}" [${node.start}, ${node.end}): not reachable from the recorded root.`);
    }
  }
  const renderEdges = [];
  for (const [headKey, children] of childrenByHead) {
    for (const child of children) {
      if (!assigned.has(child.key)) continue;
      renderEdges.push({ fromKey: headKey, toKey: child.key, label: child.dependency ?? "?" });
    }
  }
  return {
    sentenceText: typeof sentence?.text === "string" ? sentence.text : "",
    nodes: nodeList,
    nodeMap: nodesByKey,
    edges: renderEdges,
    rootKey,
    issues,
    leafCount: nextLeafCol,
    maxDepth,
    fullText: typeof fullText === "string" ? fullText : null,
  };
}

function studentTextInputEvidence(result) {
  // Only retained response fields supply evidence. The live editor is never a
  // source for this model, and paragraph strings are not joined into fake input.
  const data = transparencyData(result);
  const stageValues = [result?.stage_id, data.trace?.selected_stage, data.analysis.stage]
    .filter((value) => ["INTRODUCTION", "BODY", "CONCLUSION"].includes(value));
  const stage = stageValues.length && stageValues.every((value) => value === stageValues[0]) ? stageValues[0] : null;
  const stagePath = `research_trace.stages.${data.stage}`;
  const sources = [
    ["analysis.input_text", data.analysis.input_text],
    ["analysis.linguistic_observations.text", data.analysis.linguistic_observations?.text],
    ["analysis.linguistic_analysis.text", data.analysis.linguistic_analysis?.text],
    [`${stagePath}.linguistic_observations.text`, data.stageTrace?.linguistic_observations?.text],
    [`${stagePath}.input_sections.${String(data.stage).toLowerCase()}`, data.stageTrace?.input_sections?.[String(data.stage).toLowerCase()]],
    ["supplied_text", result?.supplied_text],
  ].filter(([, value]) => typeof value === "string");
  const agrees = sources.length > 0 && sources.every(([, value]) => value === sources[0][1]);
  const text = agrees ? sources[0][1] : null;
  const lexical = data.analysis.lexical_topic_evidence || {};
  const teacher = data.trace?.teacher_context || {};
  const question = typeof teacher.assignment_topic === "string" ? teacher.assignment_topic
    : typeof data.analysis.assignment_topic === "string" ? data.analysis.assignment_topic : null;
  const focusSource = lexical.focus_source ?? teacher.focus_source ?? null;
  const terms = Array.isArray(lexical.focus_terms) && lexical.focus_terms.every((term) => typeof term === "string")
    ? lexical.focus_terms : Array.isArray(teacher.focus_terms) && teacher.focus_terms.every((term) => typeof term?.term === "string")
      ? teacher.focus_terms.map((term) => term.term) : null;
  const priorStages = stage === "BODY" ? ["INTRODUCTION"] : stage === "CONCLUSION" ? ["INTRODUCTION", "BODY"] : [];
  const earlier = priorStages.map((prior) => {
    const key = prior.toLowerCase();
    const value = data.stageTrace?.input_sections?.[key];
    const comparison = data.analysis[`${key}_to_${String(stage).toLowerCase()}_continuity`];
    return { stage: prior, text: typeof value === "string" ? value : null,
      source: `${stagePath}.input_sections.${key}`,
      status: typeof value === "string" ? "Recorded" : comparison?.status === `NOT_AVAILABLE_NO_${prior}_SUPPLIED`
        ? "Not supplied (recorded by the continuity result)." : "Not recorded." };
  });
  return {
    stage, stage_source: "stage_id / research_trace.selected_stage / analysis.stage",
    text, text_source: agrees ? sources[0][0] : null,
    text_status: agrees ? "Recorded" : sources.length ? "Not recorded. Retained text sources disagree; no exact source is selected." : "Not recorded.",
    agreeing_text_sources: agrees ? sources.map(([path]) => path) : [],
    conflicting_text_sources: agrees ? [] : sources.map(([path, value]) => ({ source: path, text: value })),
    assignment_question: question,
    assignment_question_source: typeof teacher.assignment_topic === "string" ? "research_trace.teacher_context.assignment_topic" : "analysis.assignment_topic",
    focus_source: focusSource, configured_focus_terms: terms,
    focus_terms_source: Array.isArray(lexical.focus_terms) ? "analysis.lexical_topic_evidence.focus_terms" : "research_trace.teacher_context.focus_terms[].term",
    teacher_focus_terms: focusSource === "teacher_provided" ? terms : null,
    earlier_sections: earlier,
    code_point_characters: text === null ? null : Array.from(text).length,
    whitespace_words: text === null ? null : countWords(text),
    browser_fingerprint: text === null || stage === null ? null : transparencyDraftIdentity(text, stage),
    line_endings: text === null ? null : { crlf_pairs: (text.match(/\r\n/g) || []).length,
      standalone_lf: (text.match(/(?<!\r)\n/g) || []).length, standalone_cr: (text.match(/\r(?!\n)/g) || []).length },
    transmitted_request_payload: null, saved_revision_id: null,
    forward_summary_provenance: "Reconstructed from retained analysis-response values; not an observed HTTP payload.",
  };
}

function studentInputFacts(parent, rows) {
  const list = document.createElement("dl");
  list.className = "student-input-facts";
  for (const [label, value, source] of rows) {
    const row = document.createElement("div");
    const term = document.createElement("dt");
    term.textContent = label;
    const description = document.createElement("dd");
    description.textContent = value === null || value === undefined ? "Not recorded." : String(value);
    if (source) transparencyText(description, source, "student-input-provenance");
    row.append(term, description);
    list.appendChild(row);
  }
  parent.appendChild(list);
}

function studentSourceViewer(parent, text, label) {
  const viewer = document.createElement("div");
  viewer.className = "student-source-text";
  viewer.tabIndex = 0;
  viewer.setAttribute("role", "textbox");
  viewer.setAttribute("aria-readonly", "true");
  viewer.setAttribute("aria-multiline", "true");
  viewer.setAttribute("aria-label", label);
  viewer.textContent = text === null ? "Not recorded." : text;
  if (text !== null) {
    viewer.dataset.sourceStart = "0";
    viewer.dataset.sourceEnd = String(Array.from(text).length);
    viewer.dataset.offsetUnit = "Unicode code points; zero-based start, exclusive end";
  }
  parent.appendChild(viewer);
  return viewer;
}

function renderStudentInputInspector(parent, result, { stale = false, mode = "overview" } = {}) {
  const model = studentTextInputEvidence(result);
  const termText = (terms) => terms === null ? null : terms.length ? terms.join(", ") : "Recorded empty list (0 terms).";
  parent.classList.toggle("student-input-inspector", true);
  parent.setAttribute("data-student-input-inspector", mode);
  const section = (key, title) => {
    const item = transparencySection(parent, title);
    item.setAttribute("data-input-section", key);
    return item;
  };
  const original = section("original", "A. ORIGINAL STUDENT ESSAY");
  const version = transparencyText(original, "", "student-input-version");
  const assignmentAtCapture = transparencyLastContext?.result === result ? transparencyLastContext.assignmentDetails : currentAssignmentDetails();
  const refreshVersion = () => {
    const differs = stale || state.currentStage !== model.stage || writingInput.value !== model.text
      || currentAssignmentDetails() !== assignmentAtCapture;
    version.textContent = `${model.stage || "Stage not recorded"} · ${differs ? "Previously analyzed version — the editor or assignment/context has changed." : "Retained analyzed snapshot — not a saved draft or revision."}`;
    version.setAttribute("data-snapshot-status", differs ? "PREVIOUS" : "CURRENT");
  };
  refreshVersion();
  studentSourceViewer(original, model.text, `${model.stage || "Selected stage"}: exact retained analyzed text`);
  transparencyText(original, model.text === null ? model.text_status : `Exact source: ${model.text_source}. Capitalization, punctuation and whitespace are preserved.`, "student-input-provenance");
  if (model.conflicting_text_sources.length) {
    const alternatives = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Inspect conflicting retained text values — no agreed input selected";
    alternatives.appendChild(summary);
    for (const entry of model.conflicting_text_sources) {
      transparencyText(alternatives, entry.source, "student-input-provenance");
      studentSourceViewer(alternatives, entry.text, `Recorded alternative: ${entry.source}`);
    }
    original.appendChild(alternatives);
  }

  const actual = section("received", "B. ACTUAL INPUT RECEIVED");
  transparencyText(actual, "Recorded response values are shown below. The exact transmitted HTTP request was not recorded; these values are not a network-payload log.");
  studentInputFacts(actual, [
    ["Writing stage", model.stage, model.stage_source],
    ["Exact captured analyzed text", model.text === null ? null : "Shown unchanged in section A.", model.text_source],
    ["Assignment question", model.assignment_question, model.assignment_question_source],
    ["Configured focus terms", termText(model.configured_focus_terms), model.focus_terms_source],
    ["Focus source", model.focus_source, "analysis.lexical_topic_evidence.focus_source / research_trace.teacher_context.focus_source"],
    ["Focus terms labeled teacher-provided", termText(model.teacher_focus_terms), "The recorded focus source says teacher_provided; this label alone does not establish who entered the terms."],
    ["Characters (Unicode code points)", model.code_point_characters, "Browser-derived from the exact retained text; spaces and line-ending characters are included."],
    ["Words (whitespace-separated)", model.whitespace_words, "Browser-derived: trim outer whitespace, then count nonempty whitespace-separated pieces."],
    ["Analyzed-text fingerprint", model.browser_fingerprint, "Browser-derived, non-cryptographic text fingerprint; not a database revision ID or proof of saving."],
    ["Saved revision ID", model.saved_revision_id, "The analysis response does not identify a saved revision."],
    ["Exact transmitted request payload", model.transmitted_request_payload, "Not retained in the cached response."],
  ]);
  if (model.stage === "INTRODUCTION") transparencyText(actual, "Earlier sections: not applicable for Introduction.");
  else if (!model.stage) transparencyText(actual, "Earlier sections: Not recorded.");
  for (const prior of model.earlier_sections) {
    studentInputFacts(actual, [[`${prior.stage} earlier-section context`, prior.status, prior.source]]);
    if (prior.text !== null) {
      const details = document.createElement("details");
      details.open = mode === "context";
      const summary = document.createElement("summary");
      summary.textContent = `Inspect exact earlier ${prior.stage.toLowerCase()} text`;
      details.appendChild(summary);
      studentSourceViewer(details, prior.text, `Retained earlier ${prior.stage.toLowerCase()} context`);
      actual.appendChild(details);
    }
  }

  const explanation = section("explanation", "C. WHAT HAPPENED IN THIS STEP?");
  const grid = document.createElement("div");
  grid.className = "transparency-explanation-grid";
  for (const [title, content] of [
    ["WHAT is it?", "The system captured the writing submitted for the selected stage. This view inspects that retained version."],
    ["WHY do we need it?", "Later evidence must refer to the correct text, assignment and earlier-section context."],
    ["HOW does it work?", "The workspace captures input, selects a stage and constructs an analysis request. A successful, matching response is cached. This inspector reads that cache without running analysis again."],
    ["WHERE is it used?", "The captured writing and available assignment/context values describe the inputs supplied to the Flask analysis pathway. POS tagging, grammar observations, concepts and matching belong to later processes, not Student Text."],
  ]) {
    const block = document.createElement("div");
    const heading = document.createElement("h4"); heading.textContent = title;
    block.appendChild(heading); transparencyText(block, content); grid.appendChild(block);
  }
  explanation.appendChild(grid);
  transparencyDisclosure(explanation, "Source references — file, function and purpose", (target) => studentInputFacts(target, [
    ["static/app.js — writingInput input listener", "Captures the textarea value into the selected stage's draft; the inspector does not substitute that live draft for recorded evidence."],
    ["static/app.js — selectStage", "Selects Introduction, Body or Conclusion and restores that stage's editor text."],
    ["static/app.js — runStageAnalysis / drainAnalysisQueue", "Queues the active snapshot and serializes analysis requests."],
    ["static/app.js — performStageAnalysis", "Constructs the payload and posts to /api/analyze-stage; accepts a response only after snapshot/context checks and caches it in state.analyses."],
    ["app.py — analyze_stage / analyze_payload", "Validates and resolves assignment/context, selects the requested stage's response, and returns JSON."],
    ["app.py — compact_student_transparency_trace", "Removes duplicate trace data; retained text may therefore be in linguistic observations instead of input_sections."],
    ["services/essay_analysis_service.py — _stage_result", "Retains supplied_text in the coordinator's stage result; the student route returns selected analysis/trace fields."],
    ["static/app.js — transparencyData / studentTextInputEvidence", "Reads retained response fields and labels browser-derived counts separately. No request-payload or revision ID is invented."],
  ]));

  const observed = section("observed", "D. ACTUAL OBSERVED RESULT");
  const recordedEarlier = model.earlier_sections.filter((prior) => prior.text !== null).map((prior) => prior.stage);
  studentInputFacts(observed, [["Writing stage", model.stage], ["Whitespace-based words", model.whitespace_words],
    ["Unicode code-point characters", model.code_point_characters],
    ["Configured focus-term count", model.configured_focus_terms?.length ?? null],
    ["Earlier sections with retained text", recordedEarlier.join(", ") || (!model.stage ? null : model.stage === "INTRODUCTION" ? "Not applicable." : model.earlier_sections.every((prior) => prior.status.startsWith("Not supplied")) ? "None supplied (recorded)." : null)],
    ["Retained line endings", model.line_endings ? `${model.line_endings.crlf_pairs} CRLF pairs; ${model.line_endings.standalone_lf} standalone LF; ${model.line_endings.standalone_cr} standalone CR.` : null,
      "Browser-derived from retained characters, not a claim about pre-browser paste bytes or normalization history."]]);

  const output = section("forward", "E. OUTPUT PASSED FORWARD");
  transparencyText(output, "The captured stage text, assignment information and available earlier sections are supplied to the Flask analysis pathway. The summary here is reconstructed from retained response fields, not the exact transmitted request.");
  studentInputFacts(output, [["Observed transmitted/request values", null, "No request payload log is included in this response."],
    ["Retained selected text", model.text === null ? null : `${model.stage || "Stage not recorded"}: exact text shown in section A.`, model.text_source],
    ["Retained assignment question", model.assignment_question, model.assignment_question_source],
    ["Configured focus-term values", termText(model.configured_focus_terms), model.focus_terms_source],
    ["Summary provenance", model.forward_summary_provenance]]);

  const limits = section("limitations", "F. LIMITATIONS");
  for (const message of ["Capturing writing does not evaluate its quality. Word counts do not determine essay readiness.",
    "A browser fingerprint is not a saved revision ID, a cryptographic proof, or evidence that Save Draft was used.",
    "The current editor may differ from this analyzed version. Later observations belong to this specific captured snapshot.",
    "No text is reconstructed by joining paragraphs. If exact retained text is missing or contradictory, it is marked Not recorded.",
    "Text is rendered literally with Unicode code-point positions. Retained CRLF/LF characters are preserved; the native textarea may already have normalized line endings before submission."]) transparencyText(limits, message);
  return refreshVersion;
}

function renderNlpTransparency(result) {
  if (!nlpTransparencyContent) return;
  nlpTransparency.hidden = state.currentView === "ESSAY_REVIEW" && !state.reviewTechnicalInspectorOpen;
  if (!result?.analysis || result.availability !== "ANALYZED") {
    setTransparencyFocus(false, false);
    if (transparencyFocusToggle) transparencyFocusToggle.hidden = true;
    nlpTransparencyContent.replaceChildren();
    transparencyTabsApi = null;
    const previous = transparencyLastContext?.stage === state.currentStage && transparencyLastContext?.assignmentId === state.assignmentId;
    transparencyText(nlpTransparencyContent, previous
      ? `STALE — previous analysis (${transparencyLastContext.identity}) no longer represents the current draft or context. Analyze again to see current evidence.`
      : "Analyze your current writing first to see how EssayScaff processed it. Analyzing does not save your draft.", "transparency-analysis-status");
     nlpTransparencyContent.dataset.status = previous ? "STALE" : "NOT_ANALYZED";
    if (previous && transparencyLastContext?.result) {
      const oldInput = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = "Previously analyzed input — not current writing";
      oldInput.appendChild(summary);
      nlpTransparencyContent.appendChild(oldInput);
      renderStudentInputInspector(oldInput, transparencyLastContext.result, { stale: true, mode: "previous" });
    }
    return;
  }
  // Avoid rebuilding open evidence tables for the same authoritative response.
  if (transparencyLastContext?.result === result && nlpTransparencyContent.dataset.status === "CURRENT") return;
  nlpTransparencyContent.replaceChildren();
  const data = transparencyData(result);
  const { analysis, stage, stageTrace, trace } = data;
  const text = transparencyCurrentText(data);
  const identity = studentTextInputEvidence(result).browser_fingerprint || "Not recorded.";
  transparencyLastContext = { result, stage, assignmentId: state.assignmentId, identity, assignmentDetails: currentAssignmentDetails() };
  nlpTransparencyContent.dataset.status = "CURRENT";
  if (transparencyFocusToggle) transparencyFocusToggle.hidden = false;
  const status = transparencyText(nlpTransparencyContent, "CURRENT · Analyzed snapshot. Edits require a new analysis.", "transparency-analysis-status");
  status.setAttribute("role", "status");
  const tabs = NlpProcessExplorer.create(nlpTransparencyContent, result, data);
  transparencyTabsApi = tabs;
  const hosts = {};
  const view = (main, sub, title, explanation) => {
    renderCausalPanel(tabs.subPanels[`${main}:${sub}`], `${main}:${sub}`, result, data, tabs);
    const section = transparencySection(tabs.subPanels[`${main}:${sub}`], title);
    section.className = "transparency-section transparency-operation";
    if (explanation) transparencyDisclosure(section, "Implementation explanation and academic references", target => {
      renderTransparencyRecord(target, explanation);
      transparencyReferenceList(target, explanation.references);
    });
    return section;
  };
  const step = (id, title, info) => {
    const [main, sub] = TRANSPARENCY_OPERATION_VIEWS[id];
    const section = view(main, sub, title, info);
    section.id = `transparency-step-${id}`;
    section.tabIndex = -1;
    section.dataset.operation = id;
    hosts[id] = section;
    return section;
  };
  const info = (key) => {
    const metadata = STUDENT_TRANSPARENCY_PROCESS_INFO[key];
    const where = {
      "processing:overview": "The same Doc supplies sentence/token serialization, concept extraction and focus-window matching; stage Rule Bases reuse those prepared observations.",
      "processing:pipeline": "Doc annotations go to NLPService.analyze_doc and TopicService's concept extraction and lexical matching; no new parse is needed for these views.",
      "processing:tokenization": "Token positions and text are reused by lexical windows, concept extraction, paragraph filtering and the stage Rule Bases.",
      "processing:lemmatization": "TopicService uses lemmas for target normalization and matching; noun concepts and content-word recurrence/comparison reuse qualifying lemmas.",
      "processing:pos": "Noun concepts use NOUN/PROPN; clause rules filter VERB/AUX and permitted fine tags; content comparisons and WordNet use their configured POS filters.",
      "processing:dependencies": "Introduction and shared Body/Conclusion clause helpers require subject-to-predicate head links. These candidates feed stage findings and Rule Events.",
      "processing:noun-chunks": "TopicService reads noun chunks directly from the shared Doc to build noun-phrase concepts. The serialized noun_phrases list is an inspection copy, not a separate input to that helper.",
      "processing:concepts": metadata.next,
      "topic:overview": "Confirmed lexical matches and coverage feed the stage Rule Base's topic/context observations, emitted events and related FeedbackService checks.",
      "topic:focus-terms": "Prepared targets are shared by TopicService._find_matches across supplied sections; eligible unmatched single-word targets can also enter direct WordNet suggestion checks.",
      "topic:normalization": "Surface and normalized target sequences are inputs to TopicService._find_matches; normalized forms also deduplicate teacher targets.",
      "topic:direct": "Recorded spans become stage lexical_topic_evidence, paragraph focus matches and Introduction context candidates where applicable; related events support feedback.",
      "topic:lemma": "Normalized match spans count toward lexical coverage and feed the same stage topic/context checks as direct matches, with their distinct method preserved.",
      "topic:related": metadata.where,
      "topic:wordnet": metadata.next,
      "topic:cross-stage": "Body/Conclusion continuity findings and applicable WordNet events retain these comparisons. FeedbackService reads the resulting stage observations; Conclusion also retains candidate rewording/paraphrase relationships.",
    }[key] || (key.startsWith("topic:") ? metadata.next
      : key.startsWith("rules:") ? "Stage findings and emitted Rule Events feed FeedbackService. The reconstructed evaluation trace, configuration and source-reference records are inspection outputs; FeedbackService does not consume that later trace."
        : key.startsWith("feedback:") ? "The returned fields appear in the student's Writing Feedback panel and Final Feedback tabs. Recorded provenance connects these fields to emitted events; the same response supplies Copy Full Analysis."
          : metadata.next);
    return { ...metadata, where };
  };
  const diagram = view("backend", "flow", "Source-verified processing map", { ...TRANSPARENCY_EXTRA_INFO.response, what: "The application's actual calls and shared data, including nested and conditional work." });
  diagram.className = "transparency-flow";
  transparencyText(diagram, "Arrows show calls or labeled data transfers. Boxes inside TopicService reuse one spaCy Doc per supplied section. The annotation buttons are educational views of that shared document, not six separate calls.");
  const node = (parent, target, label, stateLabel) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "transparency-flow-node button-secondary";
    button.textContent = `${label} · ${stateLabel}`;
    button.setAttribute("aria-controls", `transparency-step-${target}`);
    button.addEventListener("click", () => {
      const [main, sub] = TRANSPARENCY_OPERATION_VIEWS[target];
      tabs.activate(main, sub);
    });
    parent.appendChild(button);
  };
  const arrow = (parent, label) => transparencyText(parent, `↓ ${label}`, "transparency-flow-arrow");
  node(diagram, "input", "Browser runStageAnalysis → Flask analyze_payload", "request accepted");
  arrow(diagram, "calls EssayAnalysisService.analyze");
  const coordinator = document.createElement("div");
  coordinator.className = "transparency-flow-group";
  transparencyText(coordinator, "EssayAnalysisService — prepare all supplied sections, then run their Rule Bases and feedback functions", "transparency-flow-title");
  node(coordinator, "focus", "TopicService.prepare_teacher_context", trace?.teacher_context ? "prepared once / shared" : "trace not retained");
  arrow(coordinator, "prepared terms + each supplied section → TopicService.analyze");
  const topicGroup = document.createElement("div");
  topicGroup.className = "transparency-flow-group";
  transparencyText(topicGroup, "Inside TopicService.analyze (per supplied section)", "transparency-flow-title");
  node(topicGroup, "pipeline", "NLPService.parse → loaded spaCy Language → analyze_doc", stageTrace?.topic_service?.steps?.find((item) => item.id === "spacy_document_processing")?.execution_status || "execution trace not retained");
  const annotations = document.createElement("div");
  annotations.className = "transparency-flow-annotations";
  for (const [target, label] of [["sentences", "Sentences"], ["tokens", "Tokens"], ["lemmas", "Lemmas"], ["pos", "POS / tags"], ["dependencies", "Dependencies"], ["chunks", "Noun chunks"]]) node(annotations, target, label, "shared Doc view");
  topicGroup.appendChild(annotations);
  arrow(topicGroup, "same Doc → noun concepts and focus-window matching (separate consumers)");
  node(topicGroup, "concepts", "TopicService._extract_concepts", data.concepts ? "recorded output" : "output not retained");
  node(topicGroup, "focus", "TopicService._find_matches + prepared targets", "lexical spans");
  node(topicGroup, "related", "Informational side branch: existing tokens/lemmas + curated resource", result.related_topic_concept_evidence?.execution_status || "not retained");
  transparencyText(topicGroup, "Related-concept evidence is attached separately to the selected response. It is not consumed by Rule Bases or FeedbackService.", "field-help");
  const direct = stageTrace?.topic_service?.steps?.find((item) => item.id === "wordnet_direct_suggestions");
  node(topicGroup, "wordnet", "Direct WordNet suggestions (conditional)", transparencyWordNetStatus(direct).label);
  coordinator.appendChild(topicGroup);
  arrow(coordinator, "prepared linguistic + lexical observations → stage Rule Base (no section reparse)");
  node(coordinator, "stage", `${({ INTRODUCTION: "Introduction", BODY: "Body", CONCLUSION: "Conclusion" })[stage]}RuleBase.analyze`, "stage findings");
  if (stage !== "INTRODUCTION") {
    const cross = document.createElement("div");
    cross.className = "transparency-flow-group";
    transparencyText(cross, "Nested inside this Rule Base: supplied earlier concepts → compare_stage_concepts → conditional cross-stage WordNet (inspect each recorded path)");
    node(cross, "wordnet", "Cross-stage lexical / WordNet comparison", "per-path status below");
    coordinator.appendChild(cross);
  }
  arrow(coordinator, "findings → _rule_events → returned stage analysis");
  node(coordinator, "rules", "Stage _rule_events → analysis.rule_evidence", "emitted events");
  arrow(coordinator, "completed analysis + emitted events → stage feedback function");
  node(coordinator, "feedback", `FeedbackService.${({ INTRODUCTION: "generate", BODY: "generate_body", CONCLUSION: "generate_conclusion" })[stage]}`, "five selected fields");
  const inspection = document.createElement("div");
  inspection.className = "transparency-flow-group";
  transparencyText(inspection, "Later inspection branch — after all supplied stages' feedback is generated: rule inventory + returned fields/events → reconstructed evaluation trace. This trace is not an input to FeedbackService.");
  node(inspection, "rules", "build_rule_evaluation_trace → rule_inventory + _observed_rule_decisions", Array.isArray(analysis.rule_evaluation_trace) ? "retained / no rule rerun" : "not retained in response");
  coordinator.appendChild(inspection);
  diagram.appendChild(coordinator);
  arrow(diagram, "selected stage → Flask compacting + jsonify → guarded browser cache");
  node(diagram, "response", "Writing Feedback + dashboard + Copy Full Analysis", "same response / no rerun");

  const student = view("student", "overview", "01 · Student Text — input and evidence inspector");
  const input = step("input", "01 · Input and text reception");
  const assignment = view("student", "context", "Assignment and earlier-stage context");
  const studentViews = {
    overview: renderStudentInputInspector(student, result, { mode: "overview" }),
    text: renderStudentInputInspector(input, result, { mode: "text" }),
    context: renderStudentInputInspector(assignment, result, { mode: "context" }),
  };
  tabs.setOnActivateSubtab((main, sub) => { if (main === "student") studentViews[sub]?.(); });
  const backend = view("backend", "overview", "Request → validated coordinator inputs", TRANSPARENCY_EXTRA_INFO.input);
  transparencyTable(backend, ["Request boundary", "Source-verified behavior / response"], [["Receiver", "POST /api/analyze-stage → analyze_stage → analyze_payload"], ["Coordinator", "EssayAnalysisService.analyze prepares supplied sections, runs stage rules and selects feedback"], ["Selected stage", result.stage_id], ["Result availability", result.availability]]);
  const validation = view("backend", "validation", "Input validation and eligibility", TRANSPARENCY_EXTRA_INFO.input);
  transparencyTable(validation, ["Validation / eligibility", "Actual evidence or source-defined policy"], [
    ["Validation", "This successful response passed Flask's request validation. Individual validation booleans are not returned."],
    ["Limits (source-defined)", "Topic: 500 characters; Introduction/Conclusion: 12,000; Body: 30,000; up to 20 focus terms of 120 characters; request body: 256 KiB."],
    ["Assignment resolution", "Saved assignment IDs resolve through authorized assignment lookup; practice requests supply topic/focus. Resolution details are not separately recorded here."],
  ]);
  const packaging = view("backend", "response", "Flask response selection and compacting", TRANSPARENCY_EXTRA_INFO.response);
  transparencyTable(packaging, ["Operation", "Output / next consumer"], [["Select requested stage", `${result.stage_id} → analysis + feedback + optional selected-stage trace`], ["Compact student response", "Repeated input/linguistic/trace copies are removed; compact feedback links retain field and Rule ID, resolved against emitted events"], ["jsonify", "Browser checks request ID and input/assignment/stage/view snapshot before caching"], ["Persistence", "Analysis is separate from saving, revisions and submission"]]);

  const pipeline = step("pipeline", "02 · Shared spaCy document and installed pipeline", info("processing:pipeline"));
  transparencyRenderSubtabEvidence(pipeline, "processing", "pipeline", result, data);
  const nlpOverview = view("nlp", "overview", "One shared spaCy document", info("processing:overview"));
  transparencyRenderSubtabEvidence(nlpOverview, "processing", "overview", result, data);
  transparencyText(nlpOverview, `Editor words: ${countWords(text)} (browser-derived whitespace count). spaCy includes punctuation in token counts and counts alphabetic-only tokens separately. These tabs inspect annotations of the same document, not separate model calls.`);
  const sentences = step("sentences", "03 · Sentence segmentation", TRANSPARENCY_EXTRA_INFO.sentences);
  transparencyTable(sentences, ["Sentence number", "Actual text", "Start", "End"], data.sentences.map((sentence, index) => [index + 1, sentence.text, sentence.start, sentence.end]));
  transparencyText(sentences, "Positions are zero-based, end-exclusive Python character offsets into the analyzed text. An end position points just after the last character.");
  const tokens = step("tokens", "04 · Tokenization", info("processing:tokenization"));
  transparencyRenderSubtabEvidence(tokens, "processing", "tokenization", result, data);
  const lemmas = step("lemmas", "05 · Lemmatization", info("processing:lemmatization"));
  transparencyExpandableTable(lemmas, `All ${data.tokens.length} recorded token-to-lemma mappings`, ["Original token", "Lemma", "Processing source", "Later use"], data.tokens.map((token) => [token.text, token.lemma, "spaCy Token.lemma_ → NLPService._token_data", token.is_alpha ? "Eligible alphabetic tokens: focus-window lemma comparison; noun concepts/content recurrence where POS qualifies" : "Retained annotation; excluded from alphabetic lexical windows"]));
  const pos = step("pos", "06 · POS tagging and fine-grained tags", info("processing:pos"));
  transparencyExpandableTable(pos, `All ${data.tokens.length} actual POS/tag records`, ["Token", "POS", "POS meaning", "Tag", "Tag meaning", "Start", "End"], data.tokens.map((token) => [token.text, token.pos, transparencyLabelExplanation(token.pos), token.tag, transparencyLabelExplanation(token.tag), token.start, token.end]));
  const dependencies = step("dependencies", "07 · Dependency parsing and connected heads", info("processing:dependencies"));
  const dependencyRows = data.sentences.flatMap((sentence) => (sentence.dependencies || []).map((edge) => [edge.text, edge.dependency, edge.head ?? "Head text not returned", edge.head_start ?? "Head position not returned", data.tokens.find((token) => token.start === edge.start)?.pos, transparencyLabelExplanation(edge.dependency), `[${edge.start}, ${edge.end})`]));
  transparencyExpandableTable(dependencies, `All ${dependencyRows.length} actual dependency relationships`, ["Token", "Dependency", "Connected head", "Head start", "POS", "Explanation", "Token span"], dependencyRows);
  transparencyText(dependencies, "Rules compare subject edges' head_start with candidate predicate positions; VERB/AUX, permitted tags and dependency labels must also qualify. Displaying an edge does not mean it was accepted as a clause candidate.");
  renderDependencyTree(dependencies, data, text);
  const chunks = step("chunks", "08 · Noun chunks", info("processing:noun-chunks"));
  transparencyRenderSubtabEvidence(chunks, "processing", "noun-chunks", result, data);
  const concepts = step("concepts", "09 · Extracted lexical concepts", info("processing:concepts"));
  transparencyRenderSubtabEvidence(concepts, "processing", "concepts", result, data);
  renderConceptJourney(concepts, data);
  const conceptOverview = view("concept", "overview", "Noun-based lexical candidates", info("processing:concepts"));
  transparencyTable(conceptOverview, ["Extraction measure", "Actual recorded value"], [["Normalized concept groups", data.concepts?.length], ["Distinct source occurrences (sum across groups)", data.concepts?.reduce((count, concept) => count + (concept.occurrences?.length || 0), 0)], ["Current-stage use", stage === "INTRODUCTION" ? "Returned for inspection; Introduction Rule Base does not consume concepts" : "Paragraph recurrence and/or cross-stage lexical comparisons"]]);
  const conceptGroups = view("concept", "concepts", "Extracted concept groups", info("processing:concepts"));
  const conceptConsumer = stage === "INTRODUCTION" ? "Introduction Rule Base does not consume concepts (inspection only)."
    : stage === "BODY" ? "Paragraph focus/recurrence observations and Introduction→Body cross-stage comparison."
      : "Synthesis, new-material and cross-stage comparisons; optional Conclusion direct WordNet input set.";
  transparencyTable(conceptGroups, ["Extracted wording", "Normalized form", "Occurrences", "Extraction methods", "Next consumer (implementation)"], (data.concepts || []).map((concept) => [concept.text, concept.normalized_form, concept.occurrence_count, (concept.extraction_methods || []).join(", "), conceptConsumer]), "Full-stage concept output was not retained, or no concepts were extracted.");
  transparencyDisclosure(conceptGroups, "Complete concept records, including all source positions", (target) => renderTransparencyRecord(target, data.concepts));
  const focus = step("focus", "10 · Focus preparation, normalization and TopicService matching", info("topic:overview"));
  for (const key of ["focus-terms", "normalization", "direct", "lemma"]) {
    const section = view("topic", key, ({ "focus-terms": "Prepared focus terms", normalization: "Normalization", direct: "Direct matches and original positions", lemma: "Lemma matches and original positions" })[key], info(`topic:${key}`));
    transparencyRenderSubtabEvidence(section, "topic", key, result, data);
  }
  const lexical = analysis.lexical_topic_evidence || {};
  transparencyRenderSubtabEvidence(focus, "topic", "overview", result, data);
  transparencyTable(focus, ["Match measure", "Recorded / derived value"], [["Unique matched terms", lexical.observed_unique_focus_terms ?? lexical.observed_focus_terms?.length], ["Total match occurrences (returned match list length)", lexical.matches?.length], ["All unique targets", lexical.total_unique_focus_terms ?? lexical.focus_terms?.length]]);
  transparencyTable(focus, ["Unmatched focus term", "Meaning"], (lexical.unobserved_focus_terms || []).map((term) => [term, "No direct or lemma-normalized match was recorded; this does not establish that the draft is off topic."]), "No unmatched terms recorded (or unmatched list not returned).");
  transparencyText(focus, "Why one occurrence counts: one eligible consecutive alphabetic-token window equals a target's casefolded surface sequence (direct), otherwise its lemma sequence (normalized). A direct window is not counted again as normalized. Hyphens/apostrophes/whitespace are permitted between phrase tokens; punctuation and blank-line boundaries block a phrase. Several occurrences of one target still count as one unique matched term.");
  renderRelatedTopicConceptSummary(focus, result);
  const related = step("related", "Related Topic Concepts · informational evidence", info("topic:related"));
  renderRelatedTopicConcepts(related, result);

  const wordnet = step("wordnet", "11 · WordNet and cross-stage comparisons", info("topic:wordnet"));
  renderStudentWordNet(wordnet, result, data);
  const crossStage = view("topic", "cross-stage", "Cross-stage lexical comparisons", info("topic:cross-stage"));
  transparencyRenderSubtabEvidence(crossStage, "topic", "cross-stage", result, data);
  const findings = step("stage", "12 · Stage-specific observations before feedback", TRANSPARENCY_EXTRA_INFO.stage);
  renderTransparencyStageFindings(findings, data);
  const rules = step("rules", "13 · Rule Evaluation Trace and emitted Rule Events", info("rules:overview"));
  renderTransparencyRules(rules, result, data, "trace");
  for (const key of ["overview", "triggered", "not-triggered", "evidence", "sources"]) {
    const metadata = ({ overview: "overview", triggered: "triggered", "not-triggered": "not-triggered", evidence: "evidence", sources: "code" })[key];
    const target = view("rules", key, ({ overview: "Rule observations at a glance", triggered: "Emitted Rule Events", "not-triggered": "Evaluated but not triggered", evidence: "Evidence, conditions and configuration", sources: "Rule implementation and reference metadata" })[key], info(`rules:${metadata}`));
    renderTransparencyRules(target, result, data, key);
  }
  renderRuleDecisionExplorer(tabs, result, data);
  const feedback = step("feedback", "14 · FeedbackService: observations to selected advice", info("feedback:overview"));
  renderTransparencyFeedback(feedback, result, data, "overview");
  for (const key of ["goal", "primary", "working", "attention", "next", "provenance"]) {
    const target = view("engine", key, ({ goal: "Current Goal", primary: "Primary Feedback", working: "What's Working", attention: "Needs Attention", next: "Next Step", provenance: "Feedback provenance and recorded priority" })[key], info(`feedback:${key}`));
    renderTransparencyFeedback(target, result, data, key);
  }
  const feedbackFlow = renderFeedbackDecisionFlow(tabs, result, data);
  renderFeedbackFlowEntries(tabs, result, data, feedbackFlow);
  const finalOverview = view("final", "overview", "Original response and exact student-facing feedback", TRANSPARENCY_EXTRA_INFO.response);
  transparencyTable(finalOverview, ["Returned result", "Actual value"], [["Stage", result.stage_id], ["Availability", result.availability], ["Original Primary Feedback", result.feedback?.["Primary Feedback"]], ["Original Next Step", result.feedback?.["Next Step"]]]);
  const studentPresentation = studentFeedbackPresentation(result);
  transparencyText(finalOverview, `Writing focus: ${studentPresentation.displayed_dimension_label || "No instructional label"}. ${studentPresentation.dimension_role}`);
  transparencyTable(finalOverview, ["Student section", "Exact displayed text"], Object.entries(studentPresentation.displayed_guidance));
  const chainFields = ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"];
  const chainProvenance = Array.isArray(result.feedback?.["Feedback Provenance"]) ? result.feedback["Feedback Provenance"] : [];
  const chainEvents = Array.isArray(analysis.rule_evidence) ? analysis.rule_evidence : [];
  transparencySection(finalOverview, "Recorded provenance chain — branch → Rule ID → emitted event → provenance record (same cached response)");
  transparencyTable(finalOverview, ["Feedback field", "1. Recorded selection branch (FeedbackService)", "2. Linked Rule IDs (recorded)", "3. Emitted event evidence (Rule Base)", "4. Provenance record (FeedbackService)", "Evidence type"], chainFields.map((field) => {
    const decision = stageTrace?.feedback_decisions?.fields?.[field];
    const fieldProvenance = chainProvenance.filter((item) => item.feedback_field === field);
    const ruleIds = decision?.rule_ids || fieldProvenance.map((item) => item.rule_id);
    const eventStates = (ruleIds || []).map((ruleId) => {
      const event = chainEvents.find((candidate) => candidate.rule_id === ruleId);
      return event ? `${ruleId}: emitted (evidence type ${event.evidence_type})` : `${ruleId}: NOT RECORDED — no emitted event matches this Rule ID`;
    });
    const observed = decision?.selection_branch || fieldProvenance.length;
    return [field,
      decision?.selection_branch || "NOT RECORDED — branch selection was not retained for this field.",
      ruleIds?.length ? ruleIds.join(", ") : "No rule link recorded.",
      eventStates.length ? eventStates.join("; ") : "No rule IDs recorded for this field.",
      fieldProvenance.length ? `${fieldProvenance.length} record(s): ${fieldProvenance.map((item) => `${item.rule_id} (${resolveStudentFeedbackProvenance(item, result).triggering_condition || "condition not recorded"})`).join("; ")}` : "No provenance record for this field in this response.",
      observed ? "OBSERVED" : "NOT_RECORDED"];
  }));
  transparencyText(finalOverview, "Each step above is a field of this same cached response (research_trace…feedback_decisions, analysis.rule_evidence, feedback['Feedback Provenance']); no step was re-run and nothing is inferred between steps.", "field-help");
  const finalFields = view("final", "fields", "All five original backend feedback fields", info("feedback:overview"));
  for (const field of ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"]) {
    const section = transparencySection(finalFields, field);
    transparencyFeedbackField(result.feedback, field, section);
  }
  const response = step("response", "15 · Final response, display and complete retained evidence", TRANSPARENCY_EXTRA_INFO.response);
  transparencyTable(response, ["Response / display fact", "Actual value / source-verified behavior"], [["Returned availability", result.availability], ["Selected stage", result.stage_id], ["Stale-response protection", "Request ID + input/assignment snapshot + active stage/view checks before cache update"], ["Storage", "Analysis does not save writing. Draft saving, revision snapshots and submission are separate operations. This response does not establish whether the draft was separately saved."], ["Frontend fallbacks", "Writing Feedback substitutes display-only text for missing/empty fields. Below and in Copy Full Analysis, empty backend arrays and absent values remain explicit."], ["Interpretation limit", result.interpretation_limit]]);
  const complete = view("final", "complete", "Complete retained technical evidence", TRANSPARENCY_EXTRA_INFO.response);
  transparencyDisclosure(complete, "Complete retained evidence index — same records as Copy Full Analysis", (parent) => {
    const records = [];
    buildFullAnalysisReport(result, records);
    transparencyText(parent, "Every available technical report record is accessible here as structured fields. Source paths identify recorded response data; explanatory/status summaries are explicitly labeled. Identical retained copies are deduplicated in the report. Open only the records you need.");
    for (const record of records) {
      const details = transparencyDisclosure(parent, record.label, (target) => {
        transparencyText(target, `Source: ${record.path}`, "transparency-source");
        renderTransparencyRecord(target, record.value);
      });
      details.dataset.source = record.path;
    }
  });
  const limitations = view("final", "limitations", "What these observations cannot establish", { ...info("feedback:provenance"), what: "The recorded scope and limits of this stage's observations.", how: "The dashboard preserves the limits returned with analysis, feedback and trace records.", why: "A lexical or structural signal should not be mistaken for a semantic or quality judgment.", where: "Interpret all displayed evidence and selected feedback within these recorded limits." });
  renderTransparencyRecord(limitations, { interpretation_limit: result.interpretation_limit, feedback_limit: result.feedback?.interpretation_limit, uncertainty: analysis.uncertainty, prohibited_conclusions: analysis.prohibited_conclusions, trace_limitations: trace?.limitations });
  // Output handoff for every process sub-panel that has implementation-verified
  // next steps. Appended after each panel's own content, never before it.
  for (const [panelKey, panel] of Object.entries(tabs.subPanels)) {
    if (!panel || !panelKey.includes(":")) continue;
    const separator = panelKey.indexOf(":");
    transparencyHandoff(panel, panelKey.slice(0, separator), panelKey.slice(separator + 1), result, data);
  }
  tabs.finish();
}

// Read-only explanation models. These compare retained observations, never
// create events, rerun NLP, replace a backend decision, or mutate a response.
function causalValue(value) {
  return value === undefined || value === null ? "NOT RECORDED" : typeof value === "object" ? JSON.stringify(value) : String(value);
}

function causalSpan(text, item) {
  if (typeof text !== "string" || !Number.isInteger(item?.start) || !Number.isInteger(item?.end)) return "NOT RECORDED";
  const chars = Array.from(text);
  if (item.start < 0 || item.end < item.start || item.end > chars.length) return "INVALID — outside source";
  return chars.slice(item.start, item.end).join("") === (item.text ?? item.observed_text) ? "VERIFIED" : "MISMATCH — not a verified source span";
}

function causalFacts(parent, rows) {
  // Definition lists avoid turning explanatory rows into apparent event rows.
  studentInputFacts(parent, rows.map(([label, value, source]) => [label, causalValue(value), source]));
}

// Plain language for the existing source-verified comparisons. Requirements
// below are internal metadata from causalRuleModel, never parsed row.condition.
function ruleTreeComparison(model) {
  const c = model.checks[0];
  const path = c?.path || "NOT RECORDED";
  const labels = [
    [/alphabetic_word_count$/, "alphabetic tokens"],
    [/central_direction_candidates$/, "central-direction candidates (finite ROOT predicates with a linked subject)"],
    [/incomplete_subordinator_candidates$/, "possible incomplete-subordinator candidates"],
    [/introductory_context_candidates$/, "sentences with both a focus-term match and a subject–predicate candidate"],
    [/development_evidence.predicate_count$/, "supported clause-predicate candidates, after excluding flagged sentences"],
    [/clause_structure_candidates.length$/, "subject-linked clause candidates in this paragraph"],
    [/lexical_topic_evidence.matches$/, "direct or lemma focus-match occurrences"],
    [/focus_term_evidence$/, "focus-match occurrences in this paragraph"],
    [/topic_sentence_candidates$/, "topic-sentence candidates in this paragraph"],
    [/closure_candidates.candidates$/, "closing-structure candidates (a final ROOT clause or a closing expression)"],
    [/clause_candidates$/, "subject-linked finite clause candidates"],
    [/paragraph_pairs$/, "recorded adjacent-paragraph comparisons"],
    [/substantive_paragraph_count$/, "paragraphs containing alphabetic text"],
  ];
  const label = labels.find(([pattern]) => pattern.test(path))?.[1];
  const requirements = {
    "count > 0": "At least 1", "count == 0": "No",
    "count >= 2": "At least 2", "count < 2": "Fewer than 2",
    "count >= 2 after excluding flagged sentences": "At least 2",
    "count < 2 after excluding flagged sentences": "Fewer than 2",
  };
  const absence = Boolean(label && c?.required === "count == 0");
  const numeric = Boolean(label && requirements[c?.required]);
  const known = numeric && typeof c.value === "number" && c.satisfied !== null;
  let purpose = `This rule checks for ${model.row.name || model.id}.`;
  if (path.endsWith("central_direction_candidates")) purpose = absence
    ? "This rule checks whether the Introduction lacks a qualifying subject–predicate structure."
    : "This rule checks whether the Introduction contains a qualifying subject–predicate structure.";
  const required = numeric ? `${requirements[c.required]} ${label}.` : model.row.condition || "NOT RECORDED — the rule requirement is unavailable.";
  const observed = known ? `${c.value} ${label}.` : c && c.value !== undefined && c.value !== null
    ? `${causalValue(c.value)} — ${path}.` : `NOT RECORDED — the needed observation (${path}) is unavailable.`;
  let reason = "The exact comparison cannot be explained from a retained, supported value here. See the recorded condition and source-derived details; intermediate execution steps are NOT RECORDED.";
  if (known) {
    reason = absence && !c.satisfied
      ? "Qualifying evidence was found, so the absence condition was not satisfied."
      : `The recorded count ${c.satisfied ? "meets" : "does not meet"} the requirement (${required.toLowerCase().replace(/\.$/, "")}), so this count comparison was ${c.satisfied ? "satisfied" : "not satisfied"}.`;
  } else if (c?.required === "LEXICAL_COMPARISON_AVAILABLE" && typeof c.value === "string") {
    reason = c.satisfied ? "The earlier section was available for a lexical comparison. This says a comparison was available, not that the ideas connected successfully."
      : "The retained comparison status does not establish an available lexical comparison with the earlier section.";
  } else if (typeof c?.value === "boolean" && c.satisfied !== null) {
    reason = `The retained finding flag is ${c.value ? "true" : "false"}; the source-defined check of that flag was ${c.satisfied ? "satisfied" : "not satisfied"}. Individual detector steps are not recorded Boolean results.`;
  }
  if (model.checks.length > 1) reason += " This is one source-verified comparison, not a reconstructed execution log of all compound conditions; the additional comparisons are available below.";
  const statusMessage = model.status === "NOT_APPLICABLE" ? "This rule was not applicable to the available inputs; it is not an evaluated-false result."
    : model.status === "NOT_RECORDED" ? "The analysis does not record whether this rule was evaluated."
      : model.status === "FAILED" ? "The analysis records a failed evaluation; it does not establish a satisfied or unsatisfied writing condition."
        : model.status === "TRIGGERED" ? "The rule triggered."
          : model.status === "EVALUATED_NOT_TRIGGERED" ? "The rule did not trigger."
            : `The recorded status is ${model.status}; no Boolean meaning is inferred.`;
  const ordinary = ["TRIGGERED", "EVALUATED_NOT_TRIGGERED"].includes(model.status);
  if (!ordinary) reason = `${statusMessage} ${model.row.decision_basis || "The reason for this status is NOT RECORDED."} Any retained comparisons explain inputs only.`;
  // Do not explain a contradictory cached status away by inventing another condition.
  if (known && ordinary && model.checks.length === 1 && c.satisfied !== (model.status === "TRIGGERED")) reason = "The source-derived comparison and the retained status disagree. The analysis does not record an explanation for this discrepancy; neither value has been overwritten.";
  return { purpose, required, observed, reason, absence, path, known, statusMessage };
}

function ruleTreeFeedbackMessage(model, result, data) {
  if (model.emitted && model.links.length) return "This Rule Event supports the selected feedback.";
  if (!model.emitted && model.eventsKnown && !model.event && model.status === "EVALUATED_NOT_TRIGGERED") return "No Rule Event was produced because this rule did not trigger. There is therefore no emitted event to link to selected feedback.";
  const fields = data.stageTrace?.feedback_decisions?.fields;
  const completeDecisions = ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"].every(field => Array.isArray(fields?.[field]?.rule_ids));
  if (model.emitted && (Array.isArray(result.feedback?.["Feedback Provenance"]) || completeDecisions)) return "This observation was recorded, but the selected feedback does not cite this Rule Event.";
  return "The available analysis does not record a feedback connection for this finding.";
}

function ruleTreeMarkerReason(data) {
  const warning = data.analysis.observable_structure?.incomplete_subordinator_candidates?.[0];
  if (!warning) return "";
  const sentence = data.sentences?.find(s => s.start <= warning.start && s.end >= warning.end);
  const token = sentence?.tokens?.find(t => t.start === warning.start && t.end === warning.end && t.text === warning.text);
  const conditions = token ? causalSubordinatorConditions(sentence, token) : null;
  if (!conditions) return "The marker candidate is recorded, but the token/dependency records needed to explain its attachment are NOT RECORDED.";
  const head = sentence.dependencies?.find(e => e.start === token.start);
  const explanations = {
    "unattached marker (dependency ROOT)": "the marker itself is labeled as the sentence's main grammatical head rather than attached to a clause",
    "mark with no supported clause head": "the marker is attached without a supported clause predicate",
    "only-root alternative after safeguard": "the marker attaches to the only qualifying main-clause predicate, and the safeguard finds no separate subject-linked finite subordinate clause",
    "prep with neither direct nor nested pobj/obj": "the marker is labeled as a preposition without a recorded direct or nested object",
    "because/prep + nominal pobj other than of + no later predicate": "because is labeled as a preposition with only a nominal object and no later eligible predicate",
  };
  const reasons = conditions.rows.filter(r => r.value === true && explanations[r.condition]).map(r => explanations[r.condition]);
  return reasons.length ? `For “${token.text}”, the recorded labels are ${token.pos}/${token.dependency}${head?.head ? `, attached to “${head.head}”` : ""}. The retained parse supports a possible incomplete sentence because ${reasons.join("; or ")}. This explains a parser-based warning, not a confirmed writing mistake.`
    : "The retained marker candidate could not be explained by the source-derived attachment comparisons. The reason for this discrepancy is NOT RECORDED.";
}

function ruleTreeEvidenceRole(model) {
  if (!model.highlightSpans.length) return model.spans.length
    ? "General recorded context — no words are marked as proof of missing evidence. An absence condition does not identify a writing mistake at a particular word."
    : "No verified source span available for highlighting. Any writing shown is general recorded context, not a marked error.";
  if (model.scope || model.id.includes("WORDNET") || !["TRIGGERED", "EVALUATED_NOT_TRIGGERED"].includes(model.status)) return "Evidence retained for inspection only — these highlights show source correspondence, not a detected writing error or a claim that feedback used this evidence.";
  if (model.status === "EVALUATED_NOT_TRIGGERED" && model.comparison.absence && model.comparison.known) return model.id.includes("CLAUSE")
    ? "Evidence contradicting an absence condition — these highlighted words show the grammatical structures found in the essay. They are evidence against the rule's missing-structure condition. They are not detected writing mistakes."
    : "Evidence contradicting an absence condition — these highlights show the recorded evidence that the absence rule was looking for. Because evidence exists, the absence condition was not satisfied. They are not detected writing mistakes.";
  if (model.status === "TRIGGERED") return model.id.includes("POSSIBLE_INCOMPLETE_SUBORDINATOR")
    ? "Evidence supporting a triggered condition — these highlighted words contain the grammatical evidence used to flag a possible incomplete sentence. This is a review candidate, not proof of a mistake."
    : "Evidence supporting a triggered condition — these highlights show recorded input supporting this rule's finding. A highlight is not itself a writing error or a quality judgment.";
  return "General recorded context — these highlights show inputs inspected for this rule, not proof that its whole condition was satisfied. A non-trigger is not automatically a positive writing assessment.";
}

function ruleTreeConnectionMessage(model, from, to) {
  if (to === "feedback") return model.feedbackMessage;
  if (to === "event") return model.outputMessage;
  if (to === "decision") return "The recorded decision is shown below; the comparison explains the retained evidence.";
  if (to === "conditions") return model.checks.length ? "Compare what was found with what this rule requires." : "The intermediate evidence needed for this comparison was not recorded.";
  return model.edges.some(e => e.from === from && e.to === to) ? "The observations below come from this analyzed writing." : "The analysis does not retain enough information to connect this writing to the observation.";
}

// Process 06 only: an inspection graph, never an execution engine.
function buildRuleDecisionTree(row, result, data = transparencyData(result)) {
  const causal = causalRuleModel(row, result, data);
  if (!causal.checks.length) causal.related = { source: "NOT RECORDED — no source-verified input mapping", value: undefined };
  const id = row.rule_id, status = row.status || "NOT_RECORDED";
  const eventsKnown = Array.isArray(data.analysis.rule_evidence);
  const event = causal.event;
  const emitted = Boolean(event && event.triggered !== false && event.fired !== false);
  const links = [];
  const provenance = result.feedback?.["Feedback Provenance"];
  for (const item of Array.isArray(provenance) ? provenance : []) {
    if (item.rule_id === id) links.push({ field: item.feedback_field, source: "feedback['Feedback Provenance']", branch: null });
  }
  for (const [field, decision] of Object.entries(data.stageTrace?.feedback_decisions?.fields || {})) {
    if (Array.isArray(decision.rule_ids) && decision.rule_ids.includes(id)) {
      links.push({ field, branch: decision.selection_branch, source: `research_trace.stages.${data.stage}.feedback_decisions.fields.${field}.rule_ids` });
    }
  }
  const feedbackUse = emitted && links.length ? "Used by selected feedback" : emitted ? "Recorded as an observation" : "No event emitted / no recorded decision link";
  const resolved = transparencyTextSources(data);
  const paragraphNumber = /^BODY\.P(\d+)\./.exec(id)?.[1];
  const paragraph = data.analysis.paragraphs?.find(p => p.paragraph_index === Number(paragraphNumber));
  const crossStage = /CONTINUITY|SYNTHESIS|NEW_MATERIAL/.test(id);
  const contexts = [];
  if (resolved.text !== null) {
    const validParagraph = paragraph && causalSpan(resolved.text, paragraph) === "VERIFIED";
    contexts.push({ text: validParagraph ? paragraph.text : resolved.text, start: validParagraph ? paragraph.start : 0,
      end: validParagraph ? paragraph.end : Array.from(resolved.text).length, section: data.stage.toLowerCase(),
      label: validParagraph ? `Paragraph ${paragraphNumber}` : `Whole ${data.stage} context`, source: resolved.source });
  }
  if (crossStage) {
    const priorKeys = data.stage === "BODY" || id.includes("CONTINUITY.INTRODUCTION") ? ["introduction"]
      : id.includes("CONTINUITY.BODY") ? ["body"] : ["introduction", "body"];
    for (const key of priorKeys) {
      const text = data.stageTrace?.input_sections?.[key];
      if (typeof text === "string") contexts.push({ text, start: 0, end: Array.from(text).length, section: key,
        label: `${key} — supplied comparison context`, source: `research_trace.stages.${data.stage}.input_sections.${key}` });
    }
  }
  const spans = [];
  // Cross-stage records have mixed offset spaces. Never reinterpret them as
  // selected-stage spans; exact source-labeled records remain in the details.
  const collect = (value, path) => {
    if (!value || typeof value !== "object") return;
    if (Array.isArray(value)) { value.forEach((item, i) => collect(item, `${path}[${i}]`)); return; }
    if (value.source_section && value.source_section !== data.stage.toLowerCase()) return;
    if (causalSpan(resolved.text, value) === "VERIFIED" && value.end > value.start && !spans.some(s => s.start === value.start && s.end === value.end)) {
      spans.push({ start: value.start, end: value.end, text: value.text ?? value.observed_text, source: path });
    }
    for (const [key, child] of Object.entries(value)) collect(child, `${path}.${key}`);
  };
  if (!crossStage) collect(causal.related.value, causal.related.source);
  if (!crossStage && emitted) collect(event.actual_evidence ?? event.evidence, `analysis.rule_evidence[rule_id=${id}].${event.actual_evidence !== undefined ? "actual_evidence" : "evidence"}`);
  spans.sort((a, b) => a.start - b.start || b.end - a.end);
  if (id.startsWith("INTRO.CLAUSE.") && spans.length && Array.isArray(data.sentences)) {
    const sentences = data.sentences.filter(s => causalSpan(resolved.text, s) === "VERIFIED" && spans.some(span => span.start >= s.start && span.end <= s.end));
    if (sentences.length) contexts.splice(0, contexts.length, ...sentences.map(s => ({ text: s.text, start: s.start, end: s.end,
      section: data.stage.toLowerCase(), label: "Sentence containing verified rule evidence", source: resolved.source })));
  }
  const output = emitted ? `${id} — ${event.evidence_type || "evidence type NOT RECORDED"}`
    : event ? "Event record retained with an explicit false flag; not an emitted event."
      : !eventsKnown ? "NOT RECORDED — Rule Event collection is absent."
        : status === "EVALUATED_NOT_TRIGGERED" || status === "NOT_APPLICABLE" ? "No Rule Event was emitted for this evaluated condition."
          : "No matching event retained; emission cannot be established from the status alone.";
  const checks = causal.checks;
  const measured = checks.map(c => `${c.path}: observed ${causalValue(c.value)}; required ${c.required}; ${c.satisfied === null ? "NOT RECORDED" : c.satisfied ? "satisfied" : "not satisfied"}`).join(". ");
  const scope = /\.(LIMITATION|GOAL)\./.test(id);
  const nodes = [
    { key: "writing", title: "A · Original student evidence", kind: "evidence", summary: contexts.length ? contexts[0].label : "NOT RECORDED — exact source text unavailable", source: resolved.source },
    { key: "observations", title: "B · Input observations", kind: "evidence", summary: checks.length ? checks.map(c => `${c.path.split('.').pop()}: ${causalValue(c.value)}`).join("; ") : "NOT RECORDED — no verified intermediate mapping", source: causal.related.source },
    { key: "conditions", title: "C · Rule conditions", kind: "condition", summary: row.condition || "NOT RECORDED", source: `${row.implementation?.file || "NOT RECORDED"}: ${row.implementation?.function || "NOT RECORDED"}` },
    { key: "decision", title: "D · Actual decision", kind: "decision", summary: status, source: `analysis.rule_evaluation_trace[rule_id=${id}]` },
    { key: "event", title: "E · Rule output", kind: "output", summary: output, source: "analysis.rule_evidence" },
    { key: "feedback", title: "F · Feedback connection", kind: "feedback", summary: feedbackUse, source: "services/feedback_service.py: generate / generate_body / generate_conclusion" },
  ];
  const edges = [];
  const edge = (from, to, label, source) => edges.push({ from, to, label, source });
  if (contexts.length && causal.related.value !== undefined) edge("writing", "observations", "source context → retained observations", causal.related.source);
  if (checks.length) edge("observations", "conditions", "SOURCE-VERIFIED LOGIC · compares retained inputs", nodes[2].source);
  if (row.status) edge("conditions", "decision", "explains reconstructed status · not runtime order", "services/research_inspector.py: build_rule_evaluation_trace");
  if (emitted) edge("decision", "event", "same Rule ID · recorded event association", "analysis.rule_evidence.rule_id");
  if (emitted && links.length) edge("event", "feedback", "recorded field-level provenance · not execution order", links.map(link => link.source).join("; "));
  const model = { id, name: row.name || row.purpose || id, status, row, causal, nodes, edges, contexts, spans, crossStage, scope,
    emitted, event, eventsKnown, output, links, feedbackUse, measured, checks };
  model.comparison = ruleTreeComparison(model);
  if (id === "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR") model.comparison.reason += ` ${ruleTreeMarkerReason(data)}`;
  model.feedbackMessage = ruleTreeFeedbackMessage(model, result, data);
  model.outputMessage = emitted ? "The rule produced a Rule Event containing its recorded evidence."
    : !event && eventsKnown && status === "EVALUATED_NOT_TRIGGERED" ? "No Rule Event was produced because this rule did not trigger."
      : !event && eventsKnown && status === "NOT_APPLICABLE" ? "This rule was not applicable; no matching Rule Event is retained."
        : output;
  // Preserve every retained span in technical details. Emphasize only direct
  // subject/predicate evidence for the central-direction check, not complements.
  model.highlightSpans = /^INTRO\.CLAUSE\.(NO_)?SUBJECT_PREDICATE_CANDIDATE$/.test(id)
    ? spans.filter(s => /\.(subject_evidence|predicate_evidence)(\[|\.|$)/.test(s.source)) : spans;
  if (model.comparison.absence && status === "TRIGGERED") model.highlightSpans = [];
  model.evidenceRole = ruleTreeEvidenceRole(model);
  model.decisionSummary = `${model.comparison.purpose} Required for triggering: ${model.comparison.required} Actually recorded: ${model.comparison.observed} ${model.comparison.reason} ${model.comparison.statusMessage} ${model.outputMessage}`;
  nodes[1].summary = model.comparison.observed;
  nodes[2].summary = model.comparison.required;
  nodes[4].summary = model.outputMessage;
  nodes[5].summary = model.feedbackMessage;
  return model;
}

function renderRuleWriting(parent, model, expanded = false) {
  transparencyText(parent, model.evidenceRole, "rule-tree-evidence-role");
  if (!model.contexts.length) transparencyText(parent, "NOT RECORDED — exact analyzed text unavailable; no span is highlighted.");
  const contexts = expanded ? model.contexts : model.contexts.slice(0, 2);
  const highlights = expanded ? model.highlightSpans : model.highlightSpans.slice(0, 6);
  for (const context of contexts) {
    transparencyText(parent, `${context.label} · [${context.start}, ${context.end}) · ${context.source}`, "transparency-source");
    const source = document.createElement("div");
    source.className = "rule-tree-writing";
    const chars = Array.from(context.text);
    let cursor = context.start;
    const append = (text, marked) => { const el = document.createElement(marked ? "mark" : "span"); el.textContent = text; source.appendChild(el); };
    for (const span of highlights) {
      if (span.start < cursor || span.end > context.end || context.section !== model.contexts[0]?.section) continue;
      append(chars.slice(cursor - context.start, span.start - context.start).join(""), false);
      append(chars.slice(span.start - context.start, span.end - context.start).join(""), true);
      cursor = span.end;
    }
    append(chars.slice(cursor - context.start).join(""), false);
    parent.appendChild(source);
  }
  transparencyText(parent, model.crossStage ? "Cross-stage offsets belong to different sections. Contexts are shown without merged highlights; source-labeled evidence remains below. Missing prior text is NOT RECORDED."
    : `${model.highlightSpans.length} relevant verified span(s); ${model.spans.length} verified spans retained in technical details. Offsets use Unicode code points, zero-based and end-exclusive.`, "field-help");
  if (!expanded && (model.contexts.length > contexts.length || model.highlightSpans.length > highlights.length)) {
    transparencyText(parent, "Concise view: at most 2 contexts and 6 relevant highlights. Expand below to inspect the remaining verified evidence; nothing is removed from the analysis report.", "field-help");
    transparencyDisclosure(parent, "Show all relevant verified evidence", target => renderRuleWriting(target, model, true));
  }
}

function renderRuleNodeDetails(parent, model, key, result, data) {
  parent.replaceChildren();
  const node = model.nodes.find(n => n.key === key);
  transparencyText(parent, node.title, "rule-tree-detail-title");
  transparencyText(parent, model.row.purpose || model.row.name || "Purpose NOT RECORDED");
  transparencyText(parent, `Why: ${model.row.educational_rationale || "NOT RECORDED — no rationale supplied."}`, "field-help");
  transparencyText(parent, `Source: ${node.source}`, "transparency-source");
  if (key === "writing") renderRuleWriting(parent, model);
  if (key === "observations" || key === "conditions" || key === "decision") {
    transparencyText(parent, model.comparison.purpose);
    causalFacts(parent, [["Required for triggering", model.comparison.required, "SOURCE-VERIFIED LOGIC"],
      ["Actually recorded", model.comparison.observed, `OBSERVED — ${model.comparison.path}`],
      ["Result", model.status, "OBSERVED — evaluation record"], ["Reason", model.comparison.reason, "SOURCE-VERIFIED DERIVATION — not a Boolean execution log"]]);
    if (key === "conditions") transparencyText(parent, `SOURCE-VERIFIED LOGIC / returned condition metadata: ${model.row.condition || "NOT RECORDED"}`);
    transparencyText(parent, "SOURCE-VERIFIED DERIVATION — comparisons of retained findings, not individually recorded Boolean execution steps.", "field-help");
    for (const c of model.checks) causalFacts(parent, [[c.path, c.value, `Required: ${c.required}; comparison: ${c.satisfied === null ? "NOT RECORDED" : c.satisfied ? "satisfied" : "not satisfied"}`]]);
    if (!model.checks.length) transparencyText(parent, "NOT RECORDED — no faithful intermediate condition mapping is available.");
    if (key === "decision") {
      transparencyText(parent, `${model.status}: ${model.row.decision_basis || "Decision basis NOT RECORDED"}`);
      transparencyText(parent, ["TRIGGERED", "EVALUATED_NOT_TRIGGERED"].includes(model.status)
        ? "This is a recorded detector outcome, not a successful or unsuccessful writing assessment."
        : "This status is not an evaluated-false result; no Boolean decision is inferred.");
    }
    if (key === "conditions" && model.id.includes("KEYWORD_LIST")) transparencyText(parent, "SOURCE-VERIFIED LOGIC — text present AND no qualifying subject-linked finite clause AND (at least 3 nonclausal sentence spans OR at least 4 NOUN/PROPN tokens). The retained candidate flag combines these conditions; the noun count alone is insufficient.");
    if (key === "conditions" && model.id.includes("SUBORDINATOR")) transparencyDisclosure(parent, "Marker attachment and compound alternatives — source-derived, not a runtime log", target => renderCausalSubordinators(target, data));
  }
  if (key === "event") {
    transparencyText(parent, model.outputMessage);
    transparencyText(parent, `SOURCE-VERIFIED LOGIC — services/${data.stage.toLowerCase()}_rules.py: _rule_events emits the event. services/research_inspector.py: build_rule_evaluation_trace later associates it with an evaluation row.`, "field-help");
    if (model.event) causalFacts(parent, [["Recorded event flags", { triggered: model.event.triggered, fired: model.event.fired }, "No missing flag is displayed as an observed true value"], ["Event condition", model.event.triggering_condition], ["Evidence type", model.event.evidence_type]]);
  }
  if (key === "feedback") {
    transparencyText(parent, model.feedbackMessage);
    if (model.emitted && model.links.length) for (const link of model.links) {
      causalFacts(parent, [[link.field, link.branch || "Selection branch NOT RECORDED in this provenance record", link.source], ["Selected feedback", result.feedback?.[link.field]]]);
    }
    transparencyText(parent, "FeedbackService reads stage findings, then attaches event provenance. Field-level links do not establish list-item-level causality or that an event caused the Primary Feedback.", "field-help");
    if (model.id.includes("WORDNET")) transparencyText(parent, "SOURCE-VERIFIED LOGIC — WordNet candidate events are informational; FeedbackService does not read them to select messages.");
  }
  transparencyText(parent, `Limitation: ${causalValue(model.causal.limit)}`, "field-help");
  const index = model.nodes.findIndex(n => n.key === key);
  if (index < model.nodes.length - 1) transparencyText(parent, ruleTreeConnectionMessage(model, key, model.nodes[index + 1].key), "field-help");
  transparencyDisclosure(parent, "Detailed technical records — selected rule only", target => renderTransparencyRecord(target, {
    input_path: model.causal.related.source, input: model.causal.related.value, evaluation: model.row,
    event: model.event, verified_spans: model.spans, feedback_links: model.links, connection_sources: model.edges,
  }));
}

function renderRuleDecisionExplorer(tabs, result, data) {
  renderRuleLimitationPaths(tabs.subPanels["rules:stage"], data);
  const parent = tabs.subPanels["rules:overview"];
  const section = transparencySection(parent, "Explore a Rule — Visual Decision Tree");
  section.className += " rule-tree-explorer";
  section.dataset.ruleExplorer = "true";
  transparencyText(section, "Read-only explanation of this cached response. Evaluation rows were reconstructed after feedback selection; arrows describe supported evidence relationships, not a new execution or runtime order.", "field-help");
  const rows = Array.isArray(data.analysis.rule_evaluation_trace) ? data.analysis.rule_evaluation_trace : Array.isArray(data.stageTrace?.rule_evaluation_trace) ? data.stageTrace.rule_evaluation_trace : [];
  if (!rows.length) { transparencyText(section, "NOT RECORDED — no evaluation records were returned. No rule inventory or negative decisions are invented."); return; }
  const label = document.createElement("label");
  label.textContent = "Select an evaluated rule";
  const select = document.createElement("select");
  select.className = "rule-tree-selector";
  select.setAttribute("aria-label", "Select an evaluated rule");
  for (const row of rows) {
    const option = document.createElement("option"); option.value = row.rule_id;
    option.textContent = `${row.name || row.purpose || row.rule_id} — ${row.rule_id} — ${row.status || "NOT_RECORDED"}`;
    select.appendChild(option);
  }
  label.appendChild(select); section.appendChild(label);
  const identity = transparencyText(section, "", "rule-tree-identity");
  identity.setAttribute("aria-live", "polite");
  const layout = document.createElement("div"); layout.className = "rule-tree-layout";
  const graph = document.createElement("div"); graph.className = "rule-tree-graph";
  graph.setAttribute("aria-label", "Selected rule evidence relationships");
  const details = document.createElement("div"); details.className = "rule-tree-details";
  layout.append(graph, details); section.appendChild(layout);
  const explanation = transparencySection(section, "Why did this rule produce this result?");
  explanation.className += " rule-tree-decision-summary";
  const explanationText = transparencyText(explanation, "");
  transparencyText(explanation, "Recorded values and status: OBSERVED. Comparison explanation: SOURCE-VERIFIED DERIVATION, not an individually recorded Boolean execution trace.", "field-help");
  const choose = id => {
    const row = rows.find(r => r.rule_id === id); if (!row) return;
    const model = buildRuleDecisionTree(row, result, data);
    section.dataset.selectedRule = id; section.dataset.ruleStatus = model.status;
    select.value = id; identity.textContent = `${model.name} · ${id} · ${model.status}`;
    explanationText.textContent = model.decisionSummary;
    graph.replaceChildren();
    const buttons = [];
    const chooseNode = key => {
      buttons.forEach(b => { const active = b.dataset.ruleNode === key; b.className = `button-quiet rule-tree-node rule-tree-${b.dataset.kind}${active ? " rule-tree-selected" : ""}`; b.setAttribute("aria-pressed", String(active)); });
      renderRuleNodeDetails(details, model, key, result, data);
    };
    if (model.scope) transparencyText(graph, id.includes(".LIMITATION.") ? "Unconditional stage-scope warning — not an uncertainty detector." : "Unconditional stage-scope goal — not a quality decision.", "field-help");
    model.nodes.forEach((node, i) => {
      if (i) {
        const edge = model.edges.find(e => e.from === model.nodes[i - 1].key && e.to === node.key);
        const connector = transparencyText(graph, `${edge ? "↓ " : ""}${ruleTreeConnectionMessage(model, model.nodes[i - 1].key, node.key)}`, "rule-tree-connector");
        if (edge) { connector.dataset.ruleFrom = edge.from; connector.dataset.ruleTo = edge.to; connector.title = edge.source; }
      }
      const button = document.createElement("button"); button.type = "button";
      button.dataset.ruleNode = node.key; button.dataset.kind = node.kind;
      const title = document.createElement("strong"); title.textContent = node.title;
      const summary = document.createElement("span"); summary.textContent = node.summary;
      button.append(title, summary); button.addEventListener("click", () => chooseNode(node.key));
      graph.appendChild(button); buttons.push(button);
    });
    chooseNode("writing");
  };
  select.addEventListener("change", () => choose(select.value));
  choose(rows[0].rule_id);
  for (const key of ["triggered", "not-triggered", "trace"]) {
    const target = tabs.subPanels[`rules:${key}`];
    transparencyDisclosure(target, "Explore these rules in the Visual Decision Tree", host => {
      const subset = key === "triggered" ? rows.filter(r => r.status === "TRIGGERED") : key === "not-triggered" ? rows.filter(r => r.status === "EVALUATED_NOT_TRIGGERED") : rows;
      for (const row of subset) {
        const button = document.createElement("button"); button.type = "button"; button.className = "rule-tree-open button-quiet";
        button.dataset.openRule = row.rule_id; button.textContent = `${row.name || row.rule_id} · ${row.rule_id} · ${row.status || "NOT_RECORDED"}`;
        button.addEventListener("click", () => { choose(row.rule_id); tabs.activate("rules", "overview"); section.scrollIntoView({ block: "start" }); select.focus(); });
        host.appendChild(button);
      }
    });
  }
}

function renderRuleLimitationPaths(parent, data) {
  const section = transparencySection(parent, "Limitation Explanation Paths");
  transparencyText(section, "Static methodological limitations and unconditional stage-scope warnings are not conditional observations or actual feedback concerns. These arrays do not select feedback; event links are shown separately in the rule explorer.");
  for (const key of ["uncertainty", "prohibited_conclusions"]) {
    const values = data.analysis[key];
    if (!Array.isArray(values)) { transparencyText(section, `analysis.${key}: NOT RECORDED`); continue; }
    for (const wording of values) transparencyDisclosure(section, `${key}: ${wording}`, host => {
      const reason = CAUSAL_SCOPE_REASONS[wording];
      const nodes = [["Underlying method", reason?.[0]], ["What was observed", `Recorded scope statement: ${wording}`], ["What remains unknown", reason?.[2]], ["Why the stronger conclusion is unsupported", reason?.[1]]];
      const explanation = document.createElement("div"); explanation.className = "rule-tree-details";
      nodes.forEach(([title, value], i) => {
        if (i) transparencyText(host, "↓ explanation relationship · not detector execution", "rule-tree-connector");
        const button = document.createElement("button"); button.type = "button"; button.className = "button-quiet rule-tree-node";
        button.textContent = `${title}: ${value || "NOT RECORDED — source explanation unavailable"}`;
        button.addEventListener("click", () => { explanation.replaceChildren(); transparencyText(explanation, `${title}: ${value || "NOT RECORDED"}`); transparencyText(explanation, `STATIC EXPLANATION · analysis.${key}; services/${data.stage.toLowerCase()}_rules.py: analyze. No uncertainty-detection execution is claimed.`); });
        host.appendChild(button);
      });
      host.appendChild(explanation);
    });
  }
}

// ─── Process 07: read-only interactive Feedback Decision Flow ───────────────
// One feedback field at a time: recorded Rule Events → Feedback Conditions →
// Selected Branch → Feedback Output → Writing Tutor Display. Every node shows
// a recorded value or a source-verified relationship. Switching selections
// never triggers an analysis request, never rewrites feedback and never
// claims a per-branch runtime evaluation that the response did not retain.

const FEEDBACK_FLOW_FIELDS = ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"];

const FEEDBACK_FLOW_FIELD_PURPOSES = {
  "Current Goal": "The stage constant teaching goal. FeedbackService sets it from the selected stage alone; no writing observation participates.",
  "Primary Feedback": "The single prioritized review message. Primary Feedback and Next Step are chosen by a fixed if/elif order: the first satisfied branch supplies the message.",
  "What's Working": "Positive observations appended by their own independent checks; there is no single selected branch.",
  "Needs Attention": "Caution observations appended by their own independent checks, separate from the Primary Feedback priority chain.",
  "Next Step": "The single next-step message, chosen by its own fixed if/elif priority order.",
};

// Static per-branch purpose table read from services/feedback_service.py. It
// never asserts why a branch won, only what the branch condition means.
const FEEDBACK_FLOW_BRANCH_PURPOSES = {
  stage_constant: "The selected stage supplies this value; no writing condition participates.",
  intro_neutral_empty: "The recorded text-presence status is EMPTY: no alphabetic content reached any writing-evidence branch.",
  intro_neutral_whitespace: "The recorded text-presence status is WHITESPACE_ONLY: only whitespace was present.",
  intro_neutral_punctuation: "The recorded text-presence status is PUNCTUATION_ONLY: only punctuation was present.",
  intro_neutral_write_first: "The recorded text-presence status is EMPTY, WHITESPACE_ONLY or PUNCTUATION_ONLY, so the next step is to write one opening sentence.",
  intro_organization_topic_intro: "The recorded structure finding marked the section as a keyword list or writing fragment rather than complete sentences.",
  intro_sentence_fluency_complete_sentence: "A flagged starting sentence part was recorded and no main statement completed that thought.",
  intro_word_choice_specific_subject: "Only broad words matched the assignment; no specific focus term matched.",
  intro_ideas_topic_match: "No configured focus term matched the writing after higher-priority text, list, and sentence checks.",
  intro_ideas_main_point: "Limited central subject-linked root-pattern evidence after higher-priority checks; no absence of meaningful ideas is inferred.",
  intro_ideas_point_and_reason: "A possible main statement and a recorded because subtree support neutral explanation review, regardless of topic-word overlap within the subtree.",
  intro_ideas_develop_main_point: "A possible main statement without additional recorded patterns supports a development task, not a missing-point accusation.",
  intro_ideas_review_details: "A possible main statement and additional patterns support reviewing details already present, with no because requirement or logical-support certification.",
  intro_ideas_review_topic_connection: "A verified local sentence wording gap supports a topic-connection review after higher-priority sentence and whole-topic checks; no irrelevance is inferred.",
  intro_ideas_state_position: "An argumentativeness cue in the assignment wording plus recorded topic discussion without any modal or first-person stance cue supports asking for an explicit position; paraphrased positions are not detected.",
  body_neutral_empty: "No substantive paragraph was recorded.",
  body_organization_paragraph_shape: "The first substantive paragraph in paragraph order was recorded as a keyword-list candidate.",
  body_organization_paragraph_link: "An adjacent paragraph pair had no observed explicit link.",
  body_ideas_develop_point: "The first sentence-bearing substantive paragraph had no additional sentence-part development candidates.",
  body_sentence_fluency_sentence_beginnings: "A substantive paragraph recorded repeated sentence beginnings.",
   body_neutral_observable: "NO_SUPPORTED_CONCERN_SELECTED: no revision task, trait, skill or lesson is forced; supported structural observations are retained.",
  body_neutral_no_intro_context: "The recorded status shows the Introduction comparison was unavailable for this Body.",
  body_neutral_general: "Fallback: no earlier Body condition matched, so a general review message was used.",
  conclusion_neutral_empty: "The recorded alphabetic word count is zero, so no writing-evidence branch applies.",
  conclusion_neutral_review: "No complete closing sentence was recorded, so a neutral review of the ending applies.",
  conclusion_neutral_general: "Fallback: no earlier Conclusion condition matched, so a general review of the ending applies.",
  conclusion_organization_bring_together: "The recorded text marked the Conclusion as a keyword list, so the writer is asked to choose one main closing idea.",
  conclusion_ideas_new_words: "Earlier-section concepts were recorded as unobserved in this Conclusion.",
  conclusion_ideas_bring_together: "A sentence combining ideas from more than one earlier section was recorded.",
  conclusion_organization_clear_ending: "A closing-structure record was considered after earlier Conclusion branches did not apply.",
  conclusion_ideas_return_to_point: "Focus words matched, and no earlier Conclusion signal branch applied.",
  independent_evidence_checks: "Each list item is appended when its own evidence condition passes; no single branch selects the whole list.",
  independent_attention_checks: "Each caution is appended when its own check identifies the corresponding condition; no single branch selects the whole list.",
  paragraph_evidence_loop: "Each substantive paragraph contributes its own checked message to this list.",
  paragraph_and_cross_stage_checks: "Paragraph, adjacent-pair, Introduction comparison and limitation messages are appended when their recorded conditions match.",
};

function feedbackFlowFieldPurpose(field) {
  return FEEDBACK_FLOW_FIELD_PURPOSES[field] || "Feedback field recorded by FeedbackService for this stage.";
}

function feedbackFlowBranchPurpose(branch) {
  if (!branch) return "No branch name was recorded for this field, so no purpose is claimed for it.";
  return FEEDBACK_FLOW_BRANCH_PURPOSES[branch] || "This branch name is not in the source-derived purpose table; only the recorded name is shown.";
}

function feedbackFlowGenerateFunction(stage) {
  return stage === "INTRODUCTION" ? "generate" : stage === "BODY" ? "generate_body" : "generate_conclusion";
}

// Build the complete read-only model for one feedback field from the cached
// response. Citation states require actual retained links; nothing is assumed.
function buildFeedbackDecisionFlow(field, result, data = transparencyData(result)) {
  const feedback = result?.feedback || {};
  const decisions = data.stageTrace?.feedback_decisions;
  const decision = decisions?.fields?.[field] || null;
  const provenance = Array.isArray(feedback["Feedback Provenance"]) ? feedback["Feedback Provenance"] : null;
  const provenanceField = provenance ? provenance.filter(item => item.feedback_field === field) : null;
  const value = feedback[field];
  const isList = Array.isArray(value);
  const messages = isList ? [...value] : value === undefined || value === null ? [] : [value];
  const eventsKnown = Array.isArray(data.analysis.rule_evidence);
  const emitted = eventsKnown ? data.analysis.rule_evidence.filter(event => event.triggered !== false && event.fired !== false) : null;
  const decisionIds = decision && Array.isArray(decision.rule_ids) ? decision.rule_ids : null;
  const fieldRecordComplete = Boolean(decisionIds && provenanceField);
  const evaluationNames = new Map((data.analysis.rule_evaluation_trace || []).map(row => [row.rule_id, row.name]));
  const branch = decision?.selection_branch || null;
  const recordedCondition = decision?.selection_condition || null;

  const cited = [], uncited = [], unknown = [];
  if (emitted) for (const event of emitted) {
    const inDecision = decisionIds ? decisionIds.includes(event.rule_id) : null;
    const inProvenance = provenanceField ? provenanceField.some(item => item.rule_id === event.rule_id) : null;
    const state = inDecision === true || inProvenance === true ? "CITED" : fieldRecordComplete ? "NOT_CITED" : "UNKNOWN";
    let discrepancy = "";
    if (state === "CITED" && inDecision !== null && inProvenance !== null && inDecision !== inProvenance) {
      discrepancy = inDecision
        ? "The recorded decision lists this Rule ID, but this response contains no provenance record for it under this field."
        : "This response contains a provenance record for this field, but the recorded decision does not list this Rule ID.";
    }
    const otherFields = provenance
      ? [...new Set(provenance.filter(item => item.rule_id === event.rule_id && item.feedback_field !== field).map(item => item.feedback_field))]
      : [];
    (state === "CITED" ? cited : state === "NOT_CITED" ? uncited : unknown).push({
      rule_id: event.rule_id, name: evaluationNames.get(event.rule_id) || event.rule_id, event, state,
      inDecision, inProvenance, discrepancy, otherFields,
      condition: event.triggering_condition || "NOT RECORDED",
      evidenceType: event.evidence_type || "NOT RECORDED",
      limitation: event.limitation ?? event.limitations ?? null,
      evidence: event.actual_evidence ?? event.evidence,
    });
  }
  const eventsSummary = !emitted
    ? "NOT RECORDED — this response contains no Rule Event list, so no event relationship is claimed."
    : `${emitted.length} emitted event(s): ${cited.length} cited by this field, ${uncited.length} recorded but not cited by this field${unknown.length ? `, ${unknown.length} with unknown connection to this field` : ""}.`;

  const conditionKind = field === "Current Goal" ? "constant" : ["Primary Feedback", "Next Step"].includes(field) ? "priority" : "independent";
  const recordedBodyChecks = data.stage === "BODY" && Array.isArray(decisions?.selection_checks);
  const priorityRows = conditionKind === "constant" ? [] : conditionKind === "priority" ? causalFeedbackPriority(data, field) : causalIndependentFeedback(data, field);
  const selectedIndex = branch ? priorityRows.findIndex(row => row.branch === branch) : -1;
  const discrepancies = [];
  if (conditionKind === "priority" && branch) {
    priorityRows.forEach((row, index) => {
      if (row.branch === branch) row.selected = true;
      if (index < selectedIndex && row.passes === true && !/fallback/i.test(String(row.condition))) {
        discrepancies.push(`Branch "${row.branch}" appears before the recorded branch "${branch}" and its source-derived condition is satisfied, yet "${branch}" is the recorded selection. The response does not record an explanation for this discrepancy; neither value has been overwritten.`);
      }
    });
  }
  const comparisons = priorityRows.map(row => conditionKind === "priority" ? {
    name: row.branch, required: row.condition, observed: causalValue(row.value),
    result: row.passes === null ? "NOT RECORDED" : row.passes ? "Satisfied" : "Not satisfied",
    explanation: row.control || "SOURCE-VERIFIED LOGIC",
    selected: Boolean(branch) && row.branch === branch,
  } : {
    name: "Independent append check", required: row.condition, observed: causalValue(row.values),
    result: row.passes === null ? "NOT RECORDED" : row.passes ? "Satisfied" : "Not satisfied",
    explanation: "SOURCE-VERIFIED LOGIC — a satisfied check supports appending its own message; this is not a ranked selection among branches.",
    selected: null,
  });
  let precedence = "";
  if (conditionKind === "constant") precedence = "Stage constant — no branch precedence applies.";
  else if (conditionKind === "independent") precedence = "Independent append checks have no single precedence order; each satisfied check may append its own message.";
  else if (!branch) precedence = "NOT RECORDED — the response does not record which branch this field used.";
  else if (selectedIndex < 0) precedence = "The recorded branch was not found among the source-derived priority rows for this field, so its position in the order cannot be placed.";
  else if (selectedIndex === 0) precedence = "The recorded branch is the first branch in source order for this field.";
  else precedence = `${selectedIndex} branch(es) appear earlier in services/feedback_service.py for this field. SOURCE-VERIFIED LOGIC — their code is evaluated before the recorded branch in the if/elif order. The response retains no per-branch evaluation record.`;
  if (recordedBodyChecks && conditionKind === "priority") precedence = "The same response records Body candidate-check results in priority order. Matched lower-priority concerns are retained as MATCHED_NOT_SELECTED_HIGHER_PRIORITY; the neutral fallback is a selection status, not an NLP Rule Event.";

  // Item-level alignment for list fields: source-verified append order plus
  // matching recorded counts. Never a runtime per-item log.
  const selectedCount = decision && Number.isInteger(decision.selected_message_count) ? decision.selected_message_count : null;
  const itemAlignment = { available: false, reason: "", index: null, rule_id: null };
  if (!isList) itemAlignment.reason = "This field returns a single message, so there are no separate items to select.";
  else if (!messages.length) itemAlignment.reason = "This field returned an empty list, so there are no items to select.";
  else if (!provenanceField) itemAlignment.reason = "This response has no feedback provenance records for this field, so individual items cannot be matched to Rule Events.";
  else if (selectedCount !== null && selectedCount !== messages.length) itemAlignment.reason = `The recorded message count (${selectedCount}) does not match the returned item count (${messages.length}); item-level alignment is not retained.`;
  else if (provenanceField.length !== messages.length) itemAlignment.reason = `This field returned ${messages.length} item(s) but ${provenanceField.length} provenance record(s); the counts do not match, so individual items cannot be matched to Rule Events.`;
  else {
    const ids = provenanceField.map(item => item.rule_id);
    if (new Set(ids).size !== ids.length) itemAlignment.reason = "The provenance records for this field repeat a Rule ID, so item order cannot be trusted for alignment.";
    else if (decisionIds && (decisionIds.length !== ids.length || decisionIds.some((id, i) => id !== ids[i]))) itemAlignment.reason = "The recorded decision's Rule ID order and this field's provenance order disagree; item alignment is not asserted.";
    else {
      itemAlignment.available = true;
      itemAlignment.reason = `SOURCE-VERIFIED DERIVATION — services/feedback_service.py appends each list item together with its Rule ID in one pass, and the recorded counts match (${messages.length}); item i therefore aligns with provenance i. This is count-checked field-level provenance, not a runtime per-item log.`;
    }
  }

  // Writing Tutor display, read from the existing presentation model only.
  const presentation = studentFeedbackPresentation(result);
  const tutorItems = Array.isArray(presentation.tutor_items) ? presentation.tutor_items : [];
  const primaryTutor = tutorItems[0] || null;
  const secondaryTutors = tutorItems.slice(1);
  const citedIds = new Set(cited.map(row => row.rule_id));
  const tutor = { status: "NOT RECORDED", supported: false, note: "The Writing Tutor display for this field is unavailable because the cached response has no usable presentation input.", category: null, skill: null, lesson: null, sections: [], excerpt: null, limitation: null, secondary: [] };
  if (field === "Primary Feedback") {
    if (presentation.status === "PREPARED_INLINE_GUIDANCE" && primaryTutor?.role === "PREPARED") {
      Object.assign(tutor, {
        status: "PREPARED_LESSON", supported: true,
        note: "The recorded Primary Feedback branch has a verified prepared-lesson mapping; the Writing Tutor shows that lesson for this field.",
        category: presentation.displayed_dimension_label, skill: presentation.writing_skill, lesson: primaryTutor.lesson_id,
        sections: [["What I noticed", primaryTutor.noticed], ["Look at your writing", primaryTutor.evidence_text], ["Why it matters", primaryTutor.why], ["How to improve", primaryTutor.task_text]],
        excerpt: primaryTutor.excerpt, limitation: primaryTutor.limitation,
      });
    } else if (primaryTutor?.role === "NO_SUPPORTED_CONCERN_SELECTED") {
      Object.assign(tutor, { status: "NO_SUPPORTED_CONCERN_SELECTED", note: "The completed Body selection recorded no supported concern. Only the neutral notice, up to two evidence-backed observations and the short limitation are displayed; no trait, lesson, error mark or improvement task is assigned.",
        sections: [["What I noticed", primaryTutor.noticed], ...(primaryTutor.working_text ? [["What's working", primaryTutor.working_text]] : [])], limitation: primaryTutor.limitation });
    } else if (presentation.status === "NEUTRAL_OBSERVATION" && primaryTutor?.role === "PREPARED") {
      Object.assign(tutor, { status: "NEUTRAL_OBSERVATION", note: `The recorded ${data.stage === "CONCLUSION" ? "Conclusion" : "Introduction"} branch is a neutral review. Only the neutral notice, any recorded strength and the limitation are displayed; no corrective trait, lesson, evidence location or improvement task is assigned. The raw recorded mapping remains in transparency.`,
        sections: [["What I noticed", primaryTutor.noticed], ...(primaryTutor.working_text ? [["What's working", primaryTutor.working_text]] : [])], limitation: primaryTutor.limitation });
    } else if (primaryTutor?.role === "NEUTRAL_REVIEW") {
      Object.assign(tutor, { status: "NEUTRAL_REVIEW", note: "No prepared lesson mapping matches the recorded branch. The Writing Tutor shows a neutral paragraph review built from recorded paragraph and sentence counts; no development problem is inferred.", limitation: primaryTutor?.limitation || null });
    } else {
      Object.assign(tutor, { status: "GENERAL_REVIEW", note: "No prepared lesson mapping matches the recorded branch. The Writing Tutor shows the original feedback as a general review without an invented dimension or skill label.", limitation: primaryTutor?.limitation || null });
    }
  } else if (field === "Needs Attention") {
    const supported = secondaryTutors.filter(item => (item.rule_ids || []).some(id => citedIds.has(id)));
    if (supported.length) {
      Object.assign(tutor, {
        status: "SECONDARY_LESSONS", supported: true,
        note: `The Writing Tutor shows ${supported.length} additional prepared lesson tab(s) selected from independently supported Needs Attention items; matching message/provenance counts, emitted events and prepared bindings were required.`,
        lesson: supported.map(item => item.lesson_id).join(", "),
        sections: [["What I noticed", supported[0].noticed], ["Look at your writing", supported[0].evidence_text], ["Why it matters", supported[0].why], ["How to improve", supported[0].task_text]],
        excerpt: supported[0].excerpt, limitation: supported[0].limitation,
        secondary: supported.slice(1).map(item => ({ lesson: item.lesson_id, noticed: item.noticed })),
      });
    } else {
      Object.assign(tutor, { status: "NO_SECONDARY_LESSON", note: secondaryTutors.length ? "Additional prepared lesson items exist for other selections, but none is linked to this field's cited events." : "No additional prepared lesson was selected for this field's items in this response. The original list still appears in the Writing Feedback panel." });
    }
  } else if (field === "What's Working") {
    Object.assign(tutor, { status: "LIST_DISPLAY_ONLY", note: "Positive observations appear verbatim in the Writing Feedback panel's 'What's Working' list (inside 'Show more feedback'). The lesson mapping starts from the recorded Primary Feedback branch; this field has no Writing Tutor lesson of its own." });
    if (data.stage === "BODY" && presentation.displayed_strengths) Object.assign(tutor, { status: "RECORDED_OBSERVATIONS_DISPLAYED", note: "Up to two recorded structural/wording observations are also shown under What's working in the Body tutor. Their source events and paragraph/sentence positions are retained in instructional_feedback.strengths; they are not rhetorical-quality assessments.", sections: [["What's working", presentation.displayed_strengths]] });
    else if (presentation.status === "NEUTRAL_OBSERVATION" && presentation.displayed_strengths) Object.assign(tutor, { status: "RECORDED_OBSERVATIONS_DISPLAYED", note: `The recorded positive observation is shown under What's working in the ${data.stage === "CONCLUSION" ? "Conclusion" : "Introduction"} tutor. It is not a rhetorical-quality assessment and does not turn the neutral review into a corrective finding.`, sections: [["What's working", presentation.displayed_strengths]] });
  } else if (field === "Current Goal") {
    Object.assign(tutor, { status: "NOT_MAPPED", note: "Current Goal is not mapped to its own Writing Tutor lesson. It is shown verbatim in Transparency Mode → Final Feedback → Five Fields and in Copy Full Analysis." });
  } else {
    Object.assign(tutor, { status: "NEXT_STEP_DISPLAY", note: "Next Step is shown verbatim in Final Feedback → Five Fields. It also supplies the Writing Tutor's 'How to improve' text only when the selected tutor item has no prepared lesson text (general review)." });
    if (data.stage === "BODY" && presentation.status === "NO_SUPPORTED_CONCERN_SELECTED") Object.assign(tutor, { status: "NO_REVISION_TASK_SELECTED", note: "The recorded Next Step is empty: no supported concern was selected, so the Body tutor does not display How to improve." });
    else if (presentation.status === "NEUTRAL_OBSERVATION") Object.assign(tutor, { status: "NO_REVISION_TASK_SELECTED", note: `The recorded ${data.stage === "CONCLUSION" ? "Conclusion" : "Introduction"} branch is a neutral review, so the tutor does not display How to improve. The original Next Step remains available verbatim in Final Feedback → Five Fields.` });
  }

  const outputSummary = value === "" ? "Recorded empty text — no revision task was selected for this field." : !messages.length
    ? value === undefined ? "NOT RECORDED — this field is absent from the response."
      : value === null ? "NOT RECORDED — the field is present with a null value."
        : "Recorded empty list — no item returned for this field."
    : isList ? `${messages.length} item(s) recorded for this field.`
      : messages[0];
  const prioritySentence = recordedBodyChecks && conditionKind === "priority"
    ? "Actual Body selection checks and their matched/selected statuses were retained in this cached response; no candidate feedback message or semantic judgment is invented for an unselected branch."
    : conditionKind === "constant"
    ? "Current Goal is a stage constant: there is no branch evaluation to retain, and no writing condition participates."
    : branch
      ? "The selected feedback branch is recorded, but individual evaluations of other possible branches were not retained."
      : "No selection branch is recorded for this field, so neither a selection nor any evaluation of other branches is available. Nothing is inferred in its place.";
  const stage = data.stage;
  const nodes = [
    { key: "events", title: "A · Recorded Rule Events", kind: "evidence", summary: eventsSummary, source: "analysis.rule_evidence (emitted events); analysis.rule_evaluation_trace (rule names)" },
    { key: "conditions", title: "B · Feedback Conditions", kind: "condition", summary: conditionKind === "constant" ? "Stage constant — no writing condition participates" : !branch ? "NOT RECORDED — no recorded selection for this field" : `${comparisons.length} source-derived ${conditionKind === "priority" ? "priority row(s)" : "independent append check(s)"}${recordedCondition ? "" : " · condition text NOT RECORDED"}`, source: `services/feedback_service.py: ${feedbackFlowGenerateFunction(stage)}; research_trace…selection_condition` },
    { key: "branch", title: "C · Selected Feedback Branch", kind: "decision", summary: branch || "NOT RECORDED — the response does not record which branch this field used", source: `research_trace.stages.${stage}.feedback_decisions.fields[${JSON.stringify(field)}].selection_branch` },
    { key: "output", title: "D · Actual Feedback Output", kind: "output", summary: outputSummary, source: `feedback[${JSON.stringify(field)}] — OBSERVED from the same cached response` },
    { key: "tutor", title: "E · Writing Tutor Display", kind: "feedback", summary: `${tutor.status}${tutor.lesson ? ` · ${tutor.lesson}` : ""} — ${tutor.supported ? "recorded lesson mapping" : "verbatim or fallback display"}`, source: "static/app.js studentFeedbackPresentation / selectTutorItems / buildTutorItem; templates/index.html Writing Tutor sections" },
  ];
  const edges = [];
  const edge = (from, to, label, source) => edges.push({ from, to, label, source });
  if (conditionKind !== "constant" && (emitted || fieldRecordComplete || branch)) {
    edge("events", "conditions", "SOURCE-VERIFIED LOGIC · the recorded condition reads the same stage findings that Rule Events record", "services/feedback_service.py reads stage findings; analysis.rule_evidence records the fired checks");
  }
  if (branch) edge("conditions", "branch", "OBSERVED · recorded condition and recorded selection branch travel together in this response", `research_trace.stages.${stage}.feedback_decisions.fields`);
  if (branch && value !== undefined && value !== null) edge("branch", "output", "OBSERVED · the recorded branch and the exact returned message come from the same cached response", `feedback[${JSON.stringify(field)}]`);
  edge("output", "tutor", "OBSERVED · the student-facing panel displays this same cached value (prepared mapping or verbatim fallback)", "static/app.js displayFeedback / studentFeedbackPresentation");
  return {
    field, stage, isList, messages, value, decisions, decision, provenance, provenanceField,
    branch, recordedCondition, decisionIds, conditionKind, eventsKnown, emitted,
    cited, uncited, unknown, eventsSummary, priorityRows, comparisons, selectedIndex, discrepancies,
    precedence, prioritySentence, itemAlignment, selectedCount, purpose: feedbackFlowFieldPurpose(field),
    tutor, presentation, nodes, edges, outputSummary,
    limitations: { feedback: feedback.interpretation_limit || null, decision: decision?.limitation || null },
  };
}

function feedbackFlowConnection(model, from, to) {
  const edge = model.edges.find(candidate => candidate.from === from && candidate.to === to);
  if (edge) return `↓ ${edge.label}`;
  if (from === "events" && to === "conditions" && model.conditionKind === "constant") return "↓ NOT APPLICABLE — this field is a stage constant; no feedback condition for it reads writing findings.";
  if (from === "events" && to === "conditions") return "↓ NOT RECORDED — no Rule Event list and no field decision/provenance records are present, so no event-to-condition link can be shown.";
  if (from === "conditions" && to === "branch") return "↓ NOT RECORDED — the response does not record which branch this field used.";
  if (from === "branch" && to === "output") return "↓ NOT RECORDED — the recorded branch or the field value is missing from this response.";
  return "↓ Recorded relationship not available in this response.";
}

// Six beginner-first questions per node, always rendered as recorded facts.
function feedbackFlowExplanation(model, key) {
  const field = model.field;
  const source = `services/feedback_service.py: ${feedbackFlowGenerateFunction(model.stage)}`;
  const questions = {
    events: [
      ["What is this?", "Rule Events are the small records the stage Rule Base writes when one of its checks fired on this section. They show which findings existed when FeedbackService chose this field's message.", "STATIC EXPLANATION — services/*_rules.py: _rule_events"],
      ["Why does it matter?", "FeedbackService keeps only rule IDs whose event was actually emitted (services/feedback_service.py: _emitted_events, _emitted_rule_ids), so emitted events are the recorded link between findings and this field.", "SOURCE-VERIFIED LOGIC"],
      ["What did EssayScaff record?", model.eventsSummary, "OBSERVED — analysis.rule_evidence; feedback['Feedback Provenance']; research_trace…feedback_decisions.rule_ids"],
      ["How was it used?", model.cited.length ? `CITED — ${model.cited.map(row => row.rule_id).join(", ")} appear in this field's recorded decision and/or provenance record; their evidence is shown in technical details.` : "No emitted event is cited by this field in the retained records (CITED: 0). A citation is a field-level association, not proof that one sentence caused the message.", "OBSERVED citation state"],
      ["Where did it come from?", "analysis.rule_evidence (emitted events), analysis.rule_evaluation_trace (rule names), feedback['Feedback Provenance'] and research_trace…feedback_decisions for this field — all from this analysis response.", "This cached response"],
      ["What are its limitations?", "Events recorded but not cited by this field may still share the same underlying findings. A citation does not establish list-item causality, and no runtime log records events being read or ignored.", "Method limitation"],
    ],
    conditions: [
      ["What is this?", `The condition (rule) in ${source} that chooses the message for this field: one priority branch for single-message fields, or separate append checks for list fields.`, "SOURCE-VERIFIED LOGIC"],
      ["Why does it matter?", "It is the recorded explanation of which observation the message depends on.", "STATIC EXPLANATION"],
      ["What did EssayScaff record?", model.recordedCondition ? `Selection condition: ${model.recordedCondition}` : model.branch === "stage_constant" ? "No selection_condition text is recorded for this field; the recorded branch 'stage_constant' and the stage goal itself are the retained evidence." : model.branch ? "NOT RECORDED — the decision record for this field contains no selection_condition text." : "NOT RECORDED — no selection record exists for this field.", "OBSERVED — research_trace…selection_condition"],
      ["How was it used?", model.stage === "BODY" && model.decisions?.selection_checks && model.conditionKind === "priority" ? "The Body candidate checks were recorded by FeedbackService. The first supported concern in priority order supplies the message; lower-priority matches are retained, and no match selects the explicit neutral status." : model.conditionKind === "constant" ? "The stage determines this value; no writing observation is required." : model.conditionKind === "priority" ? "services/feedback_service.py uses an if/elif chain: the first branch whose condition matches supplies the message. The comparison rows are SOURCE-VERIFIED DERIVATION from retained values, not a recorded runtime evaluation of every branch." : "Each list item is appended by its own check; there is no single selected branch and no ranked order among items.", "SOURCE-VERIFIED LOGIC"],
      ["Where did it come from?", `${source}: ${feedbackFlowGenerateFunction(model.stage)}; retained findings in analysis.* of this response.`, "This cached response"],
      ["What are its limitations?", model.stage === "BODY" && model.decisions?.selection_checks ? "Body selection_checks retain candidate-check Booleans and precedence outcomes, not every Python subexpression or a semantic-quality assessment. The existing Rule Base evaluation trace remains separate." : "The response does not retain a Boolean result for each conditional expression. Where a derived comparison disagrees with the recorded branch, the discrepancy is shown rather than explained away.", "Method limitation"],
    ],
    branch: [
      ["What is this?", `The branch name FeedbackService recorded for this field: ${model.branch || "NOT RECORDED"}. It identifies the code path that produced the message.`, "OBSERVED — research_trace…selection_branch"],
      ["Why does it matter?", "It links the recorded findings (node A), the code condition (node B) and the exact message (node D).", "STATIC EXPLANATION"],
      ["What did EssayScaff record?", `Branch: ${model.branch || "NOT RECORDED"}.${model.branch ? ` ${feedbackFlowBranchPurpose(model.branch)}` : ""} Linked Rule IDs: ${model.decisionIds?.length ? model.decisionIds.join(", ") : model.provenanceField?.length ? model.provenanceField.map(item => item.rule_id).join(", ") : "none recorded"}${model.decision?.selected_message_count !== undefined ? `; selected_message_count ${model.decision.selected_message_count}` : ""}`, "OBSERVED — research_trace…selection_branch / rule_ids"],
      ["How was it used?", model.precedence, model.stage === "BODY" && model.decisions?.selection_checks ? "OBSERVED — recorded Body selection checks and selected branch" : "SOURCE-VERIFIED DERIVATION — if/elif source order; no per-branch runtime evaluations were recorded"],
      ["Where did it come from?", `research_trace.stages.${model.stage}.feedback_decisions.fields[${JSON.stringify(field)}]`, "This cached response"],
      ["What are its limitations?", `${model.decisions?.unselected_alternatives || "Unselected alternatives: NOT RECORDED — the response does not retain an alternatives statement."} ${model.stage === "BODY" && model.decisions?.selection_checks ? "Recorded Body check outcomes explain selection only; unselected messages and quality judgments are not generated." : "Unselected candidate messages and a per-branch evaluation log were never recorded, so no rejected-branch execution can be shown."}`, "OBSERVED statement / method limitation"],
    ],
    output: [
      ["What is this?", `The exact message (or list item) FeedbackService returned for this field.`, "OBSERVED — feedback value"],
      ["Why does it matter?", "This is the text the student actually receives in the Writing Feedback presentation.", "STATIC EXPLANATION"],
      ["What did EssayScaff record?", model.outputSummary, `OBSERVED — feedback[${JSON.stringify(field)}]`],
      ["How was it used?", "Copied verbatim from the cached response; this inspector never regenerates, reorders or rewrites it.", "OBSERVED"],
      ["Where did it come from?", `feedback[${JSON.stringify(field)}] from the same response that supplies every node in this flow.`, "This cached response"],
      ["What are its limitations?", `${model.limitations.feedback || "No interpretation limit text was recorded for this feedback response."} A feedback message is a review prompt, not a judgment that the writing is correct or incorrect.`, "Method limitation"],
    ],
    tutor: [
      ["What is this?", `How this field reaches the student-facing Writing Tutor. ${model.tutor.note}`, "STATIC EXPLANATION — static/app.js presentation model"],
      ["Why does it matter?", "It separates what the backend recorded from what the student panel actually displays for this field.", "STATIC EXPLANATION"],
      ["What did EssayScaff record?", `Display status for this field: ${model.tutor.status}${model.tutor.lesson ? `; lesson ${model.tutor.lesson}` : ""}${model.tutor.category ? `; focus ${model.tutor.category}${model.tutor.skill ? ` · ${model.tutor.skill}` : ""}` : ""}.`, "DERIVED — existing presentation model on the same cached response"],
      ["How was it used?", "selectScaffoldingGuidance reads the recorded Primary Feedback branch and prepared binding; selectTutorItems may add independently supported Needs Attention lessons; buildTutorItem fills the five sections from verified evidence; displayFeedback renders them.", "SOURCE-VERIFIED LOGIC — static/app.js"],
      ["Where did it come from?", "content/lessons/feedback_help.json (catalog and bindings); static/app.js presentation functions; templates/index.html Writing Tutor sections.", "Implementation source"],
      ["What are its limitations?", `${model.tutor.limitation || "No item-specific limitation recorded."} A lesson label is an instructional focus, not a validated classification; a missing highlight means no verified span was available, not that no concern exists.`, "Method limitation"],
    ],
  };
  return questions[key] || [];
}

function renderFeedbackFlowPriority(host, model) {
  host.replaceChildren();
  causalFacts(host, [
    ["Selected branch", model.branch || "NOT RECORDED — this response does not record a selection branch for this field.", "OBSERVED — research_trace…selection_branch"],
    ["Required condition (recorded)", model.recordedCondition || (model.branch === "stage_constant" ? "NOT RECORDED as text — the recorded branch 'stage_constant' states that the selected stage alone supplies this value." : "NOT RECORDED — no selection condition text was retained for this field."), "OBSERVED — research_trace…selection_condition"],
    ["Actually recorded supporting observations", model.cited.length ? model.cited.map(row => `${row.rule_id} (${row.evidenceType})`).join(", ") : model.emitted ? "No emitted event is cited by this field in the retained records." : "NOT RECORDED — no Rule Event list in this response.", "OBSERVED — analysis.rule_evidence + feedback provenance"],
    ["Source-defined precedence", model.precedence, model.stage === "BODY" && model.decisions?.selection_checks ? "OBSERVED — recorded Body selection checks and precedence outcomes" : "SOURCE-VERIFIED DERIVATION — services/feedback_service.py if/elif order; no per-branch runtime evaluations were recorded"],
    ["Recorded alternative branch outcomes", model.decisions?.unselected_alternatives || "NOT RECORDED — the response does not retain an alternatives statement.", "OBSERVED statement from the same response"],
    ["Why this field contains the selected message", `${model.purpose}${model.branch ? ` ${feedbackFlowBranchPurpose(model.branch)}` : ""} Exact output: ${model.outputSummary}`, "STATIC EXPLANATION — never a runtime claim"],
  ]);
  transparencyText(host, model.prioritySentence, "feedback-flow-priority-sentence");
  for (const note of model.discrepancies) transparencyText(host, note, "feedback-flow-discrepancy");
}

function renderFeedbackFlowEvents(parent, model) {
  transparencyText(parent, model.eventsSummary, "feedback-flow-state-summary");
  if (!model.emitted) { transparencyText(parent, "NOT RECORDED — Rule Events are absent from this response; no event is invented."); return; }
  if (model.cited.length) {
    transparencyTable(parent, ["Rule ID", "Rule name", "Evidence type", "Recorded condition", "Citation state"],
      model.cited.map(row => [row.rule_id, row.name, row.evidenceType, row.condition, "CITED"]));
  } else transparencyText(parent, "No emitted event is cited by this field in the retained records.");
  if (model.unknown.length) transparencyDisclosure(parent, `${model.unknown.length} event(s) with unknown connection to this field`, target => {
    transparencyText(target, "CONNECTION UNKNOWN — the response lacks the provenance and/or decision records needed to tell whether these events contributed to this field. Neither contribution nor exclusion is claimed.", "field-help");
    transparencyTable(target, ["Rule ID", "Rule name", "Evidence type"], model.unknown.map(row => [row.rule_id, row.name, row.evidenceType]));
  });
  if (model.uncited.length) transparencyDisclosure(parent, `${model.uncited.length} recorded event(s) not cited by this field`, target => {
    transparencyText(target, "NOT CITED — these events exist in the response, and the retained selection records for this field do not reference them. This does not mean the event was ignored during execution; the source-defined conditions for this field are shown in node B.", "field-help");
    transparencyTable(target, ["Rule ID", "Rule name", "Evidence type", "Cited by other fields"],
      model.uncited.map(row => [row.rule_id, row.name, row.evidenceType, row.otherFields.join(", ") || "No other field cites it"]));
  });
  for (const row of [...model.cited, ...model.uncited, ...model.unknown]) {
    if (row.discrepancy) transparencyText(parent, `${row.rule_id}: ${row.discrepancy}`, "feedback-flow-discrepancy");
  }
}

function renderFeedbackFlowConditions(parent, model) {
  if (model.conditionKind === "constant") {
    transparencyText(parent, "Stage constant — no writing condition and no priority comparison apply to this field.");
    return;
  }
  transparencyText(parent, model.conditionKind === "priority"
    ? model.stage === "BODY" && model.decisions?.selection_checks ? "Recorded Body priority checks below: required condition, actual paragraph positions, matched result and selection outcome. Matched lower-priority concerns were not selected as the main concern." : "Priority rows below: Required → Actually recorded → Result → Explanation. Rows after the recorded branch are marked SKIPPED; their derived values claim no outcome."
    : "Independent append checks below: each satisfied check supports appending its own message. There is no ranked selection among them.", "field-help");
  if (!model.comparisons.length) { transparencyText(parent, "NOT RECORDED — retained inputs are insufficient for source-derived comparisons for this field."); return; }
  transparencyTable(parent, ["Branch / check", "Required condition", "Actually recorded", "Result", "Source-defined explanation"],
    model.comparisons.map(row => [row.name, row.required, row.observed, row.result, row.explanation]));
}

function renderFeedbackFlowBranch(parent, model) {
  transparencyText(parent, model.branch ? `Recorded branch: ${model.branch}` : "NOT RECORDED — the response does not record a selection branch for this field.");
  if (model.branch) transparencyText(parent, feedbackFlowBranchPurpose(model.branch), "field-help");
  causalFacts(parent, [
    ["Recorded rule IDs", model.decisionIds?.length ? model.decisionIds.join(", ") : model.provenanceField?.length ? model.provenanceField.map(item => item.rule_id).join(", ") : "None recorded", "OBSERVED — research_trace…rule_ids / feedback provenance"],
    ["Recorded selection condition", model.recordedCondition || "NOT RECORDED for this field.", "OBSERVED — research_trace…selection_condition"],
    ["Source-defined precedence", model.precedence, "SOURCE-VERIFIED DERIVATION"],
    ["Recorded alternative branches", model.decisions?.unselected_alternatives || "NOT RECORDED", "OBSERVED statement"],
  ]);
  for (const note of model.discrepancies) transparencyText(parent, note, "feedback-flow-discrepancy");
}

function renderFeedbackFlowOutput(parent, model, itemIndex) {
  if (!model.messages.length) {
    transparencyText(parent, model.value === undefined
      ? "NOT RECORDED — this field is absent from the response."
      : model.value === null ? "NOT RECORDED — the field is present with a null value."
        : "Recorded empty list — no item returned for this field.");
    return;
  }
  const focused = model.itemAlignment.available && itemIndex > 0 && itemIndex <= model.messages.length ? itemIndex - 1 : null;
  if (model.isList && focused !== null) {
    const provenanceItem = model.provenanceField?.[focused];
    causalFacts(parent, [
      [`Selected item ${focused + 1}`, model.messages[focused], `OBSERVED — feedback[${JSON.stringify(model.field)}][${focused}]`],
      ["Aligned Rule ID", provenanceItem?.rule_id || "NOT RECORDED", model.itemAlignment.reason],
      ["Recorded condition", provenanceItem?.triggering_condition || "NOT RECORDED", "OBSERVED — feedback provenance"],
      ["Evidence type", provenanceItem?.evidence_type || "NOT RECORDED", "OBSERVED — feedback provenance"],
      ["Limitations", provenanceItem?.limitations || "NOT RECORDED", "OBSERVED — feedback provenance"],
    ]);
  } else if (model.isList) {
    transparencyText(parent, `${model.messages.length} item(s) recorded. Select an item above to inspect its aligned provenance record.`);
  }
  if (model.isList) {
    model.messages.forEach((message, index) => {
      transparencyText(parent, `Item ${index + 1}: ${message}`, `feedback-flow-output-item${focused === index ? " feedback-flow-item-selected" : ""}`);
    });
  } else transparencyText(parent, model.messages[0] || model.outputSummary, "feedback-flow-output-item feedback-flow-item-selected");
  transparencyText(parent, `OBSERVED — feedback[${JSON.stringify(model.field)}]; this inspector copies the value verbatim.`, "field-help");
  if (model.provenanceField?.length) {
    transparencyText(parent, `Field-level provenance: ${model.provenanceField.map(item => item.rule_id).join(", ")}. Field-level provenance does not establish item-by-item causality${model.itemAlignment.available ? " beyond the count-checked derivation stated above" : ""}.`, "field-help");
  }
}

function renderFeedbackFlowTutor(parent, model) {
  const tutor = model.tutor;
  transparencyText(parent, tutor.note, "feedback-flow-tutor-note");
  causalFacts(parent, [
    ["Display status for this field", tutor.status, "DERIVED — existing presentation model, same cached response"],
    ["Writing focus / skill", tutor.category ? `${tutor.category}${tutor.skill ? ` · ${tutor.skill}` : ""}` : "No instructional label for this field.", "content/lessons/feedback_help.json binding — instructional focus, not a validated classification"],
    ["Prepared lesson", tutor.lesson || "No prepared lesson is mapped to this field.", "content/lessons/feedback_help.json"],
    ["Limitation", tutor.limitation || "No item-specific limitation recorded.", "OBSERVED presentation limitation"],
  ]);
  if (tutor.sections.length) transparencyTable(parent, ["Writing Tutor section", "Exact displayed text"], tutor.sections);
  for (const extra of tutor.secondary) transparencyText(parent, `Additional tutor tab — lesson ${extra.lesson}: ${extra.noticed}`, "field-help");
  if (tutor.excerpt?.contexts?.length) {
    for (const context of tutor.excerpt.contexts) {
      const text = Array.from(tutor.excerpt.source).slice(context.start, context.end).join("");
      transparencyText(parent, `Highlighted source context [${context.start}, ${context.end}): ${text}`, "feedback-flow-tutor-highlight");
    }
  } else transparencyText(parent, "No highlight is shown for this field in the current editor. Absence of a highlight does not mean no concern exists.", "field-help");
}

function renderFeedbackFlowDetails(parent, model, key, result, data, itemIndex = 0) {
  parent.replaceChildren();
  const node = model.nodes.find(candidate => candidate.key === key);
  transparencyText(parent, node.title, "feedback-flow-detail-title");
  transparencyText(parent, node.summary, key === "branch" ? "feedback-flow-branch" : "");
  transparencyText(parent, `Source: ${node.source}`, "transparency-source");
  const rows = feedbackFlowExplanation(model, key);
  if (rows.length) causalFacts(parent, rows);
  if (key === "events") renderFeedbackFlowEvents(parent, model);
  if (key === "conditions") renderFeedbackFlowConditions(parent, model);
  if (key === "branch") renderFeedbackFlowBranch(parent, model);
  if (key === "output") renderFeedbackFlowOutput(parent, model, itemIndex);
  if (key === "tutor") renderFeedbackFlowTutor(parent, model);
  const index = model.nodes.findIndex(candidate => candidate.key === key);
  if (index < model.nodes.length - 1) transparencyText(parent, feedbackFlowConnection(model, key, model.nodes[index + 1].key), "field-help");
  transparencyDisclosure(parent, "Detailed technical records — this field only", target => renderTransparencyRecord(target, {
    decision: model.decision,
    provenance_for_field: model.provenanceField,
    emitted_events: model.emitted ? model.emitted.map(event => ({
      rule_id: event.rule_id, triggering_condition: event.triggering_condition,
      evidence_type: event.evidence_type, limitation: event.limitation ?? event.limitations,
    })) : "NOT RECORDED",
    item_alignment: model.itemAlignment,
    display_model: { status: model.tutor.status, supported: model.tutor.supported, lesson: model.tutor.lesson, note: model.tutor.note },
    connections: model.edges,
  }));
}

// Mount the flow into Process 07 → Overview. Returns a small controller so
// the existing field panels can link back to the same explorer.
function renderFeedbackDecisionFlow(tabs, result, data) {
  const parent = tabs.subPanels["engine:overview"];
  const section = transparencySection(parent, "Explore Feedback — Visual Decision Flow");
  section.className += " feedback-flow-explorer";
  section.dataset.feedbackFlow = "true";
  transparencyText(section, "Read-only explanation of one selected feedback field from this cached response. Nodes show recorded values and source-verified relationships; switching selections never triggers a new analysis or changes feedback.", "field-help");
  const label = document.createElement("label");
  label.textContent = "Select a feedback field";
  const select = document.createElement("select");
  select.className = "feedback-flow-selector";
  select.setAttribute("aria-label", "Select a feedback field");
  for (const field of FEEDBACK_FLOW_FIELDS) {
    const option = document.createElement("option");
    option.value = field;
    option.textContent = field;
    select.appendChild(option);
  }
  label.appendChild(select);
  section.appendChild(label);
  const itemLabel = document.createElement("label");
  itemLabel.textContent = "Select an item";
  const itemSelect = document.createElement("select");
  itemSelect.className = "feedback-flow-item-selector";
  itemSelect.setAttribute("aria-label", "Select a feedback item");
  itemLabel.appendChild(itemSelect);
  section.appendChild(itemLabel);
  const identity = transparencyText(section, "", "feedback-flow-identity");
  identity.setAttribute("aria-live", "polite");
  const itemNote = transparencyText(section, "", "feedback-flow-item-note");
  const layout = document.createElement("div");
  layout.className = "feedback-flow-layout";
  const graph = document.createElement("div");
  graph.className = "feedback-flow-graph";
  graph.setAttribute("aria-label", "Recorded feedback decision flow nodes");
  const details = document.createElement("div");
  details.className = "feedback-flow-details";
  layout.append(graph, details);
  section.appendChild(layout);
  const prioritySection = transparencySection(section, "Why was this feedback selected?");
  prioritySection.className += " feedback-flow-summary";
  const priorityHost = document.createElement("div");
  priorityHost.className = "feedback-flow-summary-body";
  prioritySection.appendChild(priorityHost);
  transparencyText(prioritySection, "Recorded branch, condition, values and counts: OBSERVED. Priority comparisons and source order: SOURCE-VERIFIED DERIVATION — no per-branch runtime evaluations were recorded.", "field-help");

  let currentField = "Primary Feedback";
  let currentItem = 0;
  const render = () => {
    const model = buildFeedbackDecisionFlow(currentField, result, data);
    section.dataset.feedbackField = currentField;
    section.dataset.feedbackBranch = model.branch || "NOT_RECORDED";
    section.dataset.itemAlignment = model.itemAlignment.available ? "available" : model.isList ? "unavailable" : "not-applicable";
    select.value = currentField;
    identity.textContent = `${currentField} · branch ${model.branch || "NOT RECORDED"} · ${model.cited.length} cited event(s) · ${model.messages.length} message item(s)`;
    itemNote.textContent = model.itemAlignment.available ? (currentItem > 0 ? `Item ${currentItem} of ${model.messages.length} selected.` : "") : model.itemAlignment.reason;
    if (currentItem > model.messages.length) currentItem = 0;
    renderFeedbackFlowPriority(priorityHost, model);
    graph.replaceChildren();
    const buttons = [];
    const chooseNode = key => {
      buttons.forEach(button => {
        const active = button.dataset.flowNode === key;
        button.className = `button-quiet feedback-flow-node feedback-flow-${button.dataset.kind}${active ? " feedback-flow-selected" : ""}`;
        button.setAttribute("aria-pressed", String(active));
      });
      renderFeedbackFlowDetails(details, model, key, result, data, currentItem);
    };
    model.nodes.forEach((node, index) => {
      if (index) {
        const edge = model.edges.find(candidate => candidate.from === model.nodes[index - 1].key && candidate.to === node.key);
        const connector = transparencyText(graph, feedbackFlowConnection(model, model.nodes[index - 1].key, node.key), "feedback-flow-connector");
        if (edge) { connector.dataset.flowFrom = edge.from; connector.dataset.flowTo = edge.to; connector.title = edge.label; }
      }
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.flowNode = node.key;
      button.dataset.kind = node.kind;
      const title = document.createElement("strong");
      title.textContent = node.title;
      const summary = document.createElement("span");
      summary.textContent = node.key === "output" && model.itemAlignment.available && currentItem > 0
        ? `Item ${currentItem}: ${model.messages[currentItem - 1]}`
        : node.summary;
      button.append(title, summary);
      button.addEventListener("click", () => chooseNode(node.key));
      graph.appendChild(button);
      buttons.push(button);
    });
    chooseNode("events");
  };
  const applyField = field => {
    currentField = FEEDBACK_FLOW_FIELDS.includes(field) ? field : FEEDBACK_FLOW_FIELDS[0];
    currentItem = 0;
    itemSelect.replaceChildren();
    const probe = buildFeedbackDecisionFlow(currentField, result, data);
    if (probe.itemAlignment.available) {
      const whole = document.createElement("option");
      whole.value = "0";
      whole.textContent = `Whole field — all ${probe.messages.length} items`;
      itemSelect.appendChild(whole);
      probe.messages.forEach((message, index) => {
        const option = document.createElement("option");
        option.value = String(index + 1);
        option.textContent = `Item ${index + 1}: ${message.slice(0, 60)}${message.length > 60 ? "…" : ""}`;
        itemSelect.appendChild(option);
      });
      itemLabel.hidden = false;
    } else itemLabel.hidden = true;
    render();
  };
  select.addEventListener("change", () => applyField(select.value));
  itemSelect.addEventListener("change", () => { currentItem = Number(itemSelect.value) || 0; render(); });
  applyField(currentField);
  return {
    section,
    choose: field => applyField(field),
    open: field => {
      tabs.activate("engine", "overview");
      applyField(field);
      section.scrollIntoView({ block: "start" });
      select.focus();
    },
  };
}

// Cross-links from the existing field panels into the same explorer. Each
// disclosure reuses the cached response; no analysis request is made.
function renderFeedbackFlowEntries(tabs, result, data, flow) {
  const fields = { goal: "Current Goal", primary: "Primary Feedback", working: "What's Working", attention: "Needs Attention", next: "Next Step" };
  const link = (panel, field) => {
    if (!panel) return;
    transparencyDisclosure(panel, "Explore this field in the Visual Decision Flow", host => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "feedback-flow-open button-quiet";
      button.dataset.openField = field;
      button.textContent = `${field} — open the visual decision flow`;
      button.addEventListener("click", () => flow.open(field));
      host.appendChild(button);
      transparencyText(host, "Opens Feedback Result → Overview with this field selected, switching to Technical View. The cached response is reused; no analysis request is made.", "field-help");
    });
  };
  for (const [sub, field] of Object.entries(fields)) link(tabs.subPanels[`engine:${sub}`], field);
  const provenancePanel = tabs.subPanels["engine:provenance"];
  if (provenancePanel) transparencyDisclosure(provenancePanel, "Explore each field in the Visual Decision Flow", host => {
    for (const field of FEEDBACK_FLOW_FIELDS) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "feedback-flow-open button-quiet";
      button.dataset.openField = field;
      button.textContent = `${field} — open the visual decision flow`;
      button.addEventListener("click", () => flow.open(field));
      host.appendChild(button);
    }
    transparencyText(host, "Each link opens Feedback Result → Overview with the matching field selected (switching to Technical View); the cached response is reused and no analysis request is made.", "field-help");
  });
}

function causalRuleModel(row, result, data) {
  const a = data.analysis, id = row.rule_id;
  const event = (a.rule_evidence || []).find(item => item.rule_id === id);
  const related = transparencyRuleInputs(row, data);
  const checks = [];
  const check = (path, value, required, satisfied) => checks.push({ path, value, required,
    satisfied: value === undefined || value === null ? null : satisfied });
  const list = (path, value, positive = true) => check(path, Array.isArray(value) ? value.length : undefined,
    positive ? "count > 0" : "count == 0", Array.isArray(value) ? positive ? value.length > 0 : value.length === 0 : null);
  const presence = a.text_presence || {}, structure = a.observable_structure || {};
  const pnum = /^BODY\.P(\d+)\./.exec(id)?.[1];
  const p = a.paragraphs?.find(item => item.paragraph_index === Number(pnum));
  const pp = `analysis.paragraphs[paragraph_index=${pnum}]`;
  if (/\.(GOAL|LIMITATION)\./.test(id)) check("analysis.stage / stage_id", data.stage, `stage == ${data.stage}; unconditional scope event`, true);
  else if (/^(INTRO|CONCLUSION)\.TEXT\.(PRESENT|EMPTY_OR_NONALPHABETIC)$/.test(id)) {
    const positive = id.endsWith(".PRESENT");
    check("analysis.text_presence.alphabetic_word_count", presence.alphabetic_word_count, positive ? "count > 0" : "count == 0", positive ? presence.alphabetic_word_count > 0 : presence.alphabetic_word_count === 0);
  } else if (id.startsWith("INTRO.CLAUSE.") && !id.includes("SUBORDINATOR")) list("analysis.observable_structure.central_direction_candidates", structure.central_direction_candidates, !id.includes(".NO_"));
  else if (id.includes("POSSIBLE_INCOMPLETE_SUBORDINATOR")) list("analysis.observable_structure.incomplete_subordinator_candidates", structure.incomplete_subordinator_candidates);
  else if (id.startsWith("INTRO.CONTEXT")) list("analysis.observable_structure.introductory_context_candidates", structure.introductory_context_candidates);
  else if (id.startsWith("INTRO.DEVELOPMENT")) {
    const n = a.development_evidence?.predicate_count;
    check("analysis.development_evidence.predicate_count", n, id.includes(".MULTIPLE_") ? "count >= 2 after excluding flagged sentences" : "count < 2 after excluding flagged sentences", id.includes(".MULTIPLE_") ? n >= 2 : n < 2);
  } else if (id === "INTRO.TEXT.FRAGMENT_CANDIDATE") {
    check("analysis.observable_structure.list_or_fragment_candidate.fragmentary_text_candidate", structure.list_or_fragment_candidate?.fragmentary_text_candidate, "true", structure.list_or_fragment_candidate?.fragmentary_text_candidate === true);
    check("analysis.observable_structure.list_or_fragment_candidate.keyword_list_candidate", structure.list_or_fragment_candidate?.keyword_list_candidate, "false: keyword-list branch takes precedence", structure.list_or_fragment_candidate?.keyword_list_candidate === false);
  } else if (id.includes("KEYWORD_LIST")) {
    const finding = p ? p.fragment_or_list_candidate : data.stage === "INTRODUCTION" ? structure.list_or_fragment_candidate : a.keyword_list_candidate;
    const value = finding?.keyword_list_candidate ?? finding?.candidate;
    check(p ? `${pp}.fragment_or_list_candidate.keyword_list_candidate` : data.stage === "INTRODUCTION" ? "analysis.observable_structure.list_or_fragment_candidate.keyword_list_candidate" : "analysis.keyword_list_candidate.candidate", value, "true: text/tokens present, no qualifying clause, and >=3 nonclausal sentence spans OR >=4 NOUN/PROPN tokens", value === true);
    check("list finding.noun_or_proper_noun_count", finding?.noun_or_proper_noun_count, "one side of the OR threshold is noun count >= 4; this alone is insufficient", (finding?.noun_or_proper_noun_count ?? -1) >= 4);
  } else if (id.startsWith("INTRO.POSITION")) {
    const pe = a.position_statement_evidence || {};
    // NO_RELEVANT_* ends with RELEVANT_*: match the more specific ID first.
    const notApplicable = id.endsWith("CHECK_NOT_APPLICABLE");
    check("analysis.position_statement_evidence.status", pe.status,
      notApplicable ? "status in {CHECK_NOT_APPLICABLE_INFORMATIONAL_ASSIGNMENT, INSUFFICIENT_TOPIC_EVIDENCE_FOR_POSITION_CHECK}"
        : id.endsWith("NO_RELEVANT_POSITION_OBSERVED") ? "status == NO_RELEVANT_POSITION_OBSERVED"
        : "status == RELEVANT_POSITION_OBSERVED",
      notApplicable ? ["CHECK_NOT_APPLICABLE_INFORMATIONAL_ASSIGNMENT", "INSUFFICIENT_TOPIC_EVIDENCE_FOR_POSITION_CHECK"].includes(pe.status)
        : id.endsWith("NO_RELEVANT_POSITION_OBSERVED") ? pe.status === "NO_RELEVANT_POSITION_OBSERVED"
        : pe.status === "RELEVANT_POSITION_OBSERVED");
    if (notApplicable) { /* status gate only */ }
    else if (id.endsWith("NO_RELEVANT_POSITION_OBSERVED")) {
      list("analysis.position_statement_evidence.position_statements", pe.position_statements, false);
      list("analysis.observable_structure.central_direction_candidates", structure.central_direction_candidates);
    } else list("analysis.position_statement_evidence.position_statements", pe.position_statements);
  } else if (p) {
    if (id.includes("SEGMENTED")) check(`${pp}.text`, p.text, "nonblank line group returned by split_paragraph_spans", Boolean(p.text?.trim()));
    else if (id.includes("FOCUS_TERMS")) list(`${pp}.focus_term_evidence`, p.focus_term_evidence, !id.includes("NOT_OBSERVED"));
    else if (id.includes("TOPIC_SENTENCE")) list(`${pp}.topic_sentence_candidates`, p.topic_sentence_candidates, !id.includes("NO_CANDIDATE"));
    else if (id.includes("SUPPORTING_DETAIL")) {
      const n = p.clause_structure_candidates?.length;
      check(`${pp}.clause_structure_candidates.length`, n, id.endsWith(".CANDIDATE") ? "count >= 2" : "count < 2", id.endsWith(".CANDIDATE") ? n >= 2 : n < 2);
      list(`${pp}.supporting_detail_candidates.candidates`, p.supporting_detail_candidates?.candidates, !id.endsWith(".NOT_OBSERVED"));
    } else if (id.includes("EXAMPLE")) list(`${pp}.example_or_explanation_markers`, p.example_or_explanation_markers);
    else if (id.includes("REPETITION")) list(`${pp}.repetition_observations.${id.split(".").pop().toLowerCase()}`, p.repetition_observations?.[id.split(".").pop().toLowerCase()]);
    else if (id.includes("UNITY")) {
      const pair = p.paragraph_unity_evidence?.sentence_pairs?.find(item => id.endsWith(`SENTENCE_PAIR_${item.sentence_pair.join("_")}`));
      check(`${pp}.paragraph_unity_evidence.sentence_pairs`, pair?.status, "pairwise comparison exists; event does not mean unity passed", pair !== undefined);
    }
  } else if (id === "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW") {
    list("analysis.sentence_topic_evidence.review_candidates", a.sentence_topic_evidence?.review_candidates);
  } else if (id.includes(".TOPIC.")) {
    const positive = id.endsWith("FOCUS_MATCHES") || id.endsWith("FOCUS_TERMS_OBSERVED");
    list("analysis.lexical_topic_evidence.matches", a.lexical_topic_evidence?.matches, positive);
    if (data.stage === "BODY") check("analysis.lexical_topic_evidence.total_unique_focus_terms", a.lexical_topic_evidence?.total_unique_focus_terms, "count > 0 (otherwise not applicable)", a.lexical_topic_evidence?.total_unique_focus_terms > 0);
  } else if (id === "BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH") check("analysis.substantive_paragraph_count", a.substantive_paragraph_count, "count == 0", a.substantive_paragraph_count === 0);
  else if (id === "BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON") list("analysis.cross_paragraph_continuity.paragraph_pairs", a.cross_paragraph_continuity?.paragraph_pairs);
  else if (id.includes("CONTINUITY")) {
    const key = data.stage === "BODY" ? "introduction_to_body_continuity" : id.includes("INTRODUCTION") ? "introduction_to_conclusion_continuity" : "body_to_conclusion_continuity";
    const comp = a[key];
    check(`analysis.${key}.status`, comp?.status, id.endsWith("UNAVAILABLE") ? "earlier section unavailable" : "LEXICAL_COMPARISON_AVAILABLE", id.endsWith("UNAVAILABLE") ? comp?.status?.startsWith("NOT_AVAILABLE") : comp?.status === "LEXICAL_COMPARISON_AVAILABLE");
    if (id.includes("WORDNET")) list(`analysis.${key}.wordnet_relationship_candidates.suggestions`, comp?.wordnet_relationship_candidates?.suggestions);
  } else if (id.startsWith("CONCLUSION.STRUCTURE")) list("analysis.clause_candidates", a.clause_candidates, !id.includes("NO_CLAUSE"));
  else if (id.startsWith("CONCLUSION.SYNTHESIS")) {
    const required = id.endsWith("UNAVAILABLE") ? "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED" : id.endsWith("NO_CANDIDATE") ? "NO_SYNTHESIS_STRUCTURE_CANDIDATE_OBSERVED" : "SYNTHESIS_STRUCTURE_CANDIDATE";
    check("analysis.synthesis_structure_candidates.status", a.synthesis_structure_candidates?.status, required, a.synthesis_structure_candidates?.status === required);
  } else if (id.startsWith("CONCLUSION.CLOSURE")) {
    if (id.includes("MODAL")) list("analysis.closure_candidates.final_sentence_modal_or_recommendation_cues", a.closure_candidates?.final_sentence_modal_or_recommendation_cues);
    else list("analysis.closure_candidates.candidates", a.closure_candidates?.candidates, !id.endsWith("NO_CANDIDATE"));
  } else if (id.startsWith("CONCLUSION.NEW_MATERIAL")) {
    const key = id.endsWith("UNOBSERVED_CONCEPTS") ? "unobserved_concept_candidates" : "phrase_combinations_of_observed_concepts";
    list(`analysis.new_material_observations.${key}`, a.new_material_observations?.[key]);
  } else if (id.startsWith("CONCLUSION.REPETITION")) list(`analysis.repetition_observations.${id.split(".").pop().toLowerCase()}`, a.repetition_observations?.[id.split(".").pop().toLowerCase()]);
  const links = (result.feedback?.["Feedback Provenance"] || []).filter(item => item.rule_id === id).map(item => item.feedback_field);
  const alternativePairs = [["TEXT.PRESENT", "TEXT.EMPTY_OR_NONALPHABETIC"], ["CLAUSE.SUBJECT_PREDICATE_CANDIDATE", "CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE"], ["TOPIC.FOCUS_TERMS_OBSERVED", "TOPIC.NO_FOCUS_MATCH_OBSERVED"], ["DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES", "DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE"], ["SUPPORTING_DETAIL.CANDIDATE", "SUPPORTING_DETAIL.NOT_OBSERVED"], ["TOPIC_SENTENCE.CANDIDATE", "TOPIC_SENTENCE.NO_CANDIDATE"], ["STRUCTURE.CLAUSE_CANDIDATE", "STRUCTURE.NO_CLAUSE_CANDIDATE"], ["TOPIC.FOCUS_MATCHES", "TOPIC.NO_FOCUS_MATCH"], ["POSITION.RELEVANT_POSITION_OBSERVED", "POSITION.NO_RELEVANT_POSITION_OBSERVED"]];
  const alternatives = alternativePairs.flatMap(pair => pair.filter(suffix => id.endsWith(suffix)).flatMap(suffix => pair.filter(other => other !== suffix).map(other => id.slice(0, -suffix.length) + other)))
    .filter(other => (a.rule_evidence || []).some(item => item.rule_id === other));
  const measures = checks.map(item => `${item.path}: observed ${causalValue(item.value)}; required ${item.required}; comparison ${item.satisfied === null ? "NOT RECORDED" : item.satisfied ? "satisfied" : "not satisfied"}`).join(". ");
  return { id, event, row, checks, related, alternatives, links,
    summary: `${id}: ${measures || "NOT RECORDED — no faithful measured comparison is available for this rule."}. Recorded status: ${row.status || "NOT RECORDED"}. ${event ? "The Rule Base emitted this event." : "No emitted event with this ID is retained."}`,
    usage: id.includes("WORDNET") ? "Informational Rule Event: the Rule Base retains the candidate; FeedbackService does not read WordNet candidates to select messages. Direct/lemma continuity is a different input."
      : links.length ? `Recorded provenance links: ${links.join(", ")}. FeedbackService reads the stage findings to select messages, then resolves emitted event IDs for provenance; the ID itself is not proof of an event-to-event dependency.`
        : "No feedback provenance link recorded. This does not by itself prove that the underlying observation was unread; inspect the field's source conditions. The reconstructed evaluation row is inspection-only.",
    limit: event?.limitation || event?.limitations || row.limitations || "The conditions examine parser/lexical evidence, not meaning, truth or writing quality." };
}

function renderCausalRule(parent, row, result, data) {
  const model = causalRuleModel(row, result, data);
  const section = document.createElement("div");
  section.dataset.causalRule = model.id;
  parent.appendChild(section);
  transparencyText(section, model.summary);
  transparencyDisclosure(section, `${model.id} — why, conditions, evidence and actual use`, target => {
    causalFacts(target, [
      ["Identity / purpose", row.purpose || row.name, row.educational_rationale || "Purpose metadata not recorded"],
      ["Input", model.related.source, "Returned observation, not raw text independently parsed by this rule"],
      ["Exact source condition", row.condition, `${row.implementation?.file || "NOT RECORDED"}: ${row.implementation?.function || "NOT RECORDED"}`],
      ["Measured comparison", model.summary, "SOURCE-VERIFIED LOGIC — reconstructed from retained values, not a new execution"],
      ["Alternative actually emitted", model.alternatives.length ? model.alternatives.join(", ") : "No mapped contrary event retained; no alternative inferred"],
      ["Status meaning", ["NOT_APPLICABLE", "NOT_RECORDED", "FAILED"].includes(row.status) ? `${row.status} is not an evaluated-false result.` : "A non-trigger is not automatically a writing success."],
      ["Downstream", model.usage, "services/feedback_service.py: generate / generate_body / generate_conclusion"],
      ["Limitation and cause", model.limit],
    ]);
    if (model.id === "INTRO.TEXT.PRESENT" || model.id === "INTRO.TEXT.EMPTY_OR_NONALPHABETIC") transparencyText(target, "SOURCE-VERIFIED LOGIC — NLPService.analyze_doc counts Token.is_alpha, not whitespace words. IntroductionRuleBase.analyze reads that count; _rule_events uses its truth value. Clause extraction already ran before event emission and does not depend on INTRO.TEXT.PRESENT. FeedbackService uses text_presence.status for the empty/whitespace/punctuation branches. If the count were zero, the complementary empty/nonalphabetic event would be emitted; text presence alone says nothing about completeness.");
    if (model.id.includes("KEYWORD_LIST")) transparencyText(target, "SOURCE-VERIFIED LOGIC — absence of any qualifying subject-linked clause is required. Absence of a ROOT clause alone is insufficient. The recorded list flag incorporates the conjunction and OR threshold; the noun-count comparison alone is not the rule result. Registry wording above is retained verbatim even where it abbreviates this distinction.");
    if (model.id.includes("SUBORDINATOR")) renderCausalSubordinators(target, data);
    transparencyDisclosure(target, "Complete retained input, emitted event, configuration and reconstructed registry row", detail => renderTransparencyRecord(detail, { input: model.related.value, emitted_event: model.event, registry: row }));
  });
}

function causalSubordinatorConditions(sentence, token) {
  // Source-verifiable Boolean comparisons only; not a second rule execution.
  // Values never feed analysis, events, feedback or lesson selection.
  const tokens = sentence.tokens, edges = sentence.dependencies;
  if (!Array.isArray(tokens) || !Array.isArray(edges) || !Number.isInteger(sentence.start) || typeof sentence.text !== "string") return null;
  const finite = ["VB", "VBD", "VBP", "VBZ"], subjects = ["nsubj", "nsubjpass", "csubj", "csubjpass"];
  const predicates = tokens.filter(t => ["VERB", "AUX"].includes(t.pos) && ["ROOT", "conj", "advcl", "ccomp", "xcomp", "relcl"].includes(t.dependency));
  const edge = edges.find(e => e.start === token.start);
  if (!edge || tokens.some(t => !edges.some(e => e.start === t.start))) return null;
  const headStart = edge.head_start, marker = token.text.toLowerCase();
  const roots = tokens.filter(t => ["VERB", "AUX"].includes(t.pos) && finite.includes(t.tag) && t.dependency === "ROOT");
  const ordinaryHead = predicates.some(t => t.start === headStart);
  const rows = [];
  const add = (condition, value, applicability = "Source comparison; per-request evaluation log NOT RECORDED") => rows.push({ condition, value, applicability });
  let clauseHead = ordinaryHead;
  add("SCONJ + configured marker eligibility", true);
  add("head_start belongs to predicate_starts (VERB/AUX + allowed dependency)", ordinaryHead);
  if (!ordinaryHead && marker === "before" && token.dependency === "mark") {
    const node = position => {
      const ts = tokens.filter(t => t.start === position), es = edges.filter(e => e.start === position);
      if (ts.length !== 1 || es.length !== 1) return null;
      const t = ts[0], e = es[0];
      if (!Number.isInteger(position) || !Number.isInteger(t.end) || position < sentence.start || t.end <= position || t.end > sentence.end || Array.from(sentence.text).slice(position - sentence.start, t.end - sentence.start).join("") !== t.text || ["text", "start", "end", "dependency", "head"].some(k => t[k] !== e[k])) return null;
      return { t, e };
    };
    const m = node(token.start), subordinate = m ? node(m.e.head_start) : null, main = subordinate ? node(subordinate.e.head_start) : null;
    const validLength = Number.isInteger(sentence.end) && sentence.end - sentence.start === Array.from(sentence.text).length;
    const subOK = Boolean(subordinate && subordinate.t.pos === "ADJ" && subordinate.t.tag === "JJ" && subordinate.t.dependency === "advcl");
    const mainOK = Boolean(main && ![token.start, subordinate.t.start].includes(main.t.start) && ["VERB", "AUX"].includes(main.t.pos) && finite.includes(main.t.tag) && main.t.dependency === "ROOT" && main.e.head_start === main.t.start && token.head === subordinate.t.text && subordinate.t.head === main.t.text);
    const independent = Boolean(main && !edges.some(e => e.head_start === main.t.start && e.dependency === "mark"));
    const hasSubject = predicate => Boolean(predicate && edges.some(e => subjects.includes(e.dependency) && e.head_start === predicate.start && node(e.start) && node(e.start).t.head === predicate.text && ![token.start, subordinate?.t.start, main?.t.start].includes(e.start)));
    const subSubject = hasSubject(subordinate?.t), mainSubject = hasSubject(main?.t);
    clauseHead = Boolean(validLength && m && subOK && mainOK && independent && subSubject && mainSubject);
    for (const [condition, value] of [["before safeguard: verified sentence length and marker node", Boolean(validLength && m)], ["before safeguard: verified ADJ/JJ advcl head", subOK], ["before safeguard: separate verified finite ROOT and consistent heads", mainOK], ["before safeguard: ROOT has no mark dependent", independent], ["before safeguard: verified subject for subordinate", subSubject], ["before safeguard: verified subject for main ROOT", mainSubject], ["before safeguard conjunction", clauseHead]]) add(condition, value, "SOURCE-VERIFIED LOGIC — retained-node comparison; helper execution/return log NOT RECORDED");
  } else add("narrow before safeguard", null, "NOT APPLICABLE under retained source conditions");
  const initialRoot = token.dependency === "mark" && clauseHead && roots.some(t => t.start === headStart) && !roots.some(t => t.start !== headStart);
  const separate = tokens.some(t => ["VERB", "AUX"].includes(t.pos) && finite.includes(t.tag) && ["advcl", "ccomp", "xcomp"].includes(t.dependency) && t.start !== headStart && edges.some(e => subjects.includes(e.dependency) && e.head_start === t.start));
  const rootWarning = initialRoot && !separate;
  const unattached = token.dependency === "ROOT", badMark = token.dependency === "mark" && !clauseHead;
  const directObject = edges.some(e => e.head_start === token.start && ["pobj", "obj"].includes(e.dependency));
  const nestedObject = edges.some(child => child.head_start === token.start && child.dependency === "prep" && edges.some(e => e.head_start === child.start && ["pobj", "obj"].includes(e.dependency)));
  const prep = token.dependency === "prep" && !directObject && !nestedObject;
  const because = marker === "because" && token.dependency === "prep" && edges.some(e => e.head_start === token.start && e.dependency === "pobj" && e.text.toLowerCase() !== "of") && !predicates.some(t => t.start > token.end);
  add("only finite ROOT before separate-clause safeguard", initialRoot);
  add("separate finite advcl/ccomp/xcomp with its own subject", separate, initialRoot ? "Source suppresses only-root alternative when true" : "Not reached by this source guard; structural fact only");
  add("unattached marker (dependency ROOT)", unattached);
  add("mark with no supported clause head", badMark);
  add("only-root alternative after safeguard", rootWarning);
  add("prep with neither direct nor nested pobj/obj", prep);
  add("because/prep + nominal pobj other than of + no later predicate", because);
  return { rows, supportedWarning: unattached || badMark || rootWarning || prep || because };
}

function renderCausalSubordinators(parent, data) {
  const finite = ["VB", "VBD", "VBP", "VBZ"], deps = ["ROOT", "conj", "advcl", "ccomp", "xcomp", "relcl"], subjects = ["nsubj", "nsubjpass", "csubj", "csubjpass"];
  const markers = ["although", "as", "because", "before", "if", "once", "since", "though", "unless", "until", "when", "whereas", "while"];
  const text = transparencyTextSources(data).text;
  transparencyText(parent, "SOURCE-VERIFIED LOGIC — services/introduction_rules.py: _incomplete_subordinator_evidence. Only a token labeled SCONJ whose casefolded word is configured enters the detector. Retained annotations support the comparisons below. Short-circuit execution flags and the narrow before safeguard return value are NOT RECORDED; no separate uncertainty detector ran.");
  let count = 0;
  for (const sentence of data.sentences) for (const token of sentence.tokens || []) {
    if (token.pos !== "SCONJ" || !markers.includes(token.text.toLowerCase())) continue;
    count += 1;
    const edges = sentence.dependencies || [], tokens = sentence.tokens || [];
    const edge = edges.find(item => item.start === token.start);
    const head = tokens.find(item => item.start === edge?.head_start);
    const predicates = tokens.filter(item => ["VERB", "AUX"].includes(item.pos) && deps.includes(item.dependency));
    const roots = predicates.filter(item => finite.includes(item.tag) && item.dependency === "ROOT");
    const separate = tokens.filter(item => ["VERB", "AUX"].includes(item.pos) && finite.includes(item.tag) && ["advcl", "ccomp", "xcomp"].includes(item.dependency) && item.start !== edge?.head_start && edges.some(link => subjects.includes(link.dependency) && link.head_start === item.start));
    const warning = (data.analysis.observable_structure?.incomplete_subordinator_candidates || []).find(item => item.start === token.start && item.end === token.end);
    const conditions = causalSubordinatorConditions(sentence, token);
    if (conditions) {
      transparencyDisclosure(parent, `${token.text}@${token.start}: all source conditions and safeguards`, target => {
        for (const row of conditions.rows) causalFacts(target, [[row.condition, row.value, row.applicability]]);
        causalFacts(target, [["Source-derived OR result", conditions.supportedWarning, "SOURCE-VERIFIED LOGIC — not an observed Boolean log"], ["Recorded candidate exists", Boolean(warning), "OBSERVED — incomplete_subordinator_candidates"], ["Agreement", conditions.supportedWarning === Boolean(warning), "A mismatch must be investigated, never used to overwrite the retained result"]]);
      });
    } else transparencyText(parent, "NOT RECORDED — incomplete token/dependency evidence prevents faithful source-condition reconstruction.");
    const onlyRoot = token.dependency === "mark" && roots.some(item => item.start === edge?.head_start) && roots.length === 1;
    causalFacts(parent, [
      ["Original sentence", sentence.text, `[${sentence.start}, ${sentence.end}) — ${causalSpan(text, sentence)}`],
      ["Marker / annotations", `${token.text}: ${token.pos} / ${token.tag} / ${token.dependency}; head ${edge?.head} at ${edge?.head_start}`, `[${token.start}, ${token.end}) — ${causalSpan(text, token)}`],
      ["Eligible predicate positions", predicates.map(item => `${item.text}@${item.start}`).join(", ") || "none", "VERB/AUX and configured dependency; this predicate set has no finite-tag filter"],
      ["Finite ROOT positions", roots.map(item => `${item.text}@${item.start}`).join(", ") || "none"],
      ["Marker is ROOT", token.dependency === "ROOT", "Unattached-marker alternative"],
      ["Ordinary clause head", predicates.some(item => item.start === edge?.head_start), "A mark without a clause head is an alternative; before may use the narrow safeguard"],
      ["Only finite ROOT before safeguard", onlyRoot],
      ["Separate subject-linked finite subordinate predicates", separate.map(item => `${item.text}@${item.start}`).join(", ") || "none", "If the only-root test is reached and this list is nonempty, the source suppresses that alternative"],
      ["Before safeguard", token.text.toLowerCase() === "before" ? `Head ${head?.text}: ${head?.pos}/${head?.tag}/${head?.dependency}. _before_adjective_clause_supported requires verified ADJ/JJ advcl → independent finite ROOT and subjects for both.` : "NOT APPLICABLE — marker is not before", "Actual helper return/reached flag: NOT RECORDED"],
      ["Other alternatives", "prep with no pobj/obj (including nested prep complement); because/prep with nominal pobj other than 'of' and no later predicate", "Exact edges below; intermediate branch log NOT RECORDED"],
      ["Recorded detector result", warning ? "Warning candidate retained" : "No warning candidate retained — not proof of grammatical correctness"],
      ["Development dependency", "_development_finding excludes clauses in sentences with a recorded warning", "This is an actual finding-to-finding dependency, unlike an event-ID prerequisite"],
      ["Why limited", "Parser attachment can be wrong. These grammatical patterns cannot establish thesis meaning or completeness with certainty."],
    ]);
    transparencyDisclosure(parent, `${token.text}@${token.start}: actual tokens, heads, subjects and detector output`, target => renderTransparencyRecord(target, { sentence, warning }));
  }
  if (!count) transparencyText(parent, "No configured SCONJ marker appears in the retained sentence tokens. If tokens were omitted, eligibility is NOT RECORDED.");
}

// Each configured safeguard is matched by exact returned wording. Unknown or
// future wording is preserved with an honest missing-source explanation.
const CAUSAL_SCOPE_REASONS = {
  "These rules use linguistic structure and lexical overlap only.": ["POS/dependency and exact/lemma matches", "The implementation has no semantic validity test; grammatical/lexical evidence is the scope of the method.", "Meaning and argument evaluation with independent reference evidence"],
  "A grammatical clause can be semantically anomalous or contradictory.": ["central_direction_candidates", "A subject-to-predicate edge can exist even in a contradictory proposition.", "Contextual semantic and contradiction evaluation"],
  "No semantic intelligibility, logical coherence, or factual correctness judgment is made.": ["All Introduction findings", "The code tests syntax and word overlap, not truth or logical relations.", "Semantic, logic and factual verification"],
  "A central-direction candidate is not a validated thesis or a readiness decision.": ["central_direction_candidates", "A finite ROOT and linked subject establish a parser pattern, not an argumentative claim answering the assignment.", "Assignment-aware thesis assessment and validated readiness criteria"],
  "A recorded position cue is not a verified argument, and paraphrased positions may not be detected.": ["position_statement_evidence", "A modal or first-person stance cue matched with an assignment word is fixed wording evidence, not a verified argument; paraphrased positions are not detected.", "Argument-quality and paraphrased-position assessment"],
  "Linguistic and lexical structure does not establish semantic intelligibility or logical coherence.": ["Body clauses and continuity comparisons", "Shared word forms and clause counts do not test relations between propositions.", "Contextual meaning and reasoning assessment"],
  "A topic-sentence or supporting-detail candidate is not a confirmed rhetorical role or valid argument.": ["topic_sentence_candidates / supporting_detail_candidates", "Focus overlap or recurrence with a clause, and a two-clause threshold, cannot verify rhetorical function or support.", "Rhetorical-role and argument-support evaluation"],
  "Low lexical overlap may reflect paraphrase or focus terms that do not cover the student's wording.": ["focus_term_evidence / continuity", "Finite teacher vocabulary and exact/lemma comparisons can miss rewordings; WordNet does not disambiguate contextual sense.", "Context-sensitive relevance assessment"],
  "No factual correctness, academic quality, or Body readiness judgment is made.": ["All Body findings", "No fact checker, quality rubric scoring or readiness classifier is called.", "Evidence-based fact checking and validated rubric/readiness assessment"],
  "These rules describe lexical, sentence, and dependency evidence only.": ["All Conclusion findings", "The implementation retains linguistic observations, not a semantic model judgment.", "Independent semantic evaluation"],
  "A final sentence or closing expression is not proof of effective rhetorical closure.": ["closure_candidates", "A final ROOT or listed expression detects a structural cue, not its rhetorical effect.", "Whole-essay rhetorical assessment"],
  "Lexical overlap does not prove that the Conclusion restates, synthesizes, or supports earlier claims.": ["continuity / synthesis_structure_candidates", "Shared normalized concepts do not establish relations among claims or successful synthesis.", "Contextual claim and synthesis assessment"],
  "No factual correctness, semantic intelligibility, essay quality, or readiness decision is made.": ["All Conclusion findings", "The predicates inspect syntax and vocabulary rather than those broader constructs.", "Independent fact, meaning and rubric-based evaluation"],
  "meaningful or nonsensical": ["Parser-labeled clauses", "Grammatical structure can describe nonsensical or contradictory content.", "Context-sensitive semantic evidence"],
  "academically good or poor": ["Clause counts and lexical matches", "No academic-quality rubric is evaluated by these rules.", "Validated rubric assessment"],
  "ready or not ready": ["Presence, structure and development candidates", "These observations are not a validated readiness decision.", "Explicit validated readiness criteria"],
  "stage unlocked": ["Stage goal and positive structural events", "Analysis emits guidance, not a workflow authorization decision.", "Separate workflow policy and applicable user action"],
  "BODY_READY": ["Body paragraph and detail candidates", "Candidate counts are not a validated Body-readiness measure.", "Validated readiness criteria"],
  "proven topic support": ["Focus matches and supporting_detail_candidates", "Word overlap and two clauses do not test whether evidence supports a claim.", "Argument-support evaluation"],
  "logically coherent": ["Adjacent lexical continuity", "Repeated content lemmas or transitions do not test logical inference.", "Proposition-level reasoning assessment"],
};

function renderCausalLimits(parent, data) {
  for (const [key, label] of [["uncertainty", "Uncertainty — methodological scope"], ["prohibited_conclusions", "Prohibited conclusions — unsupported claims"]]) {
    const values = data.analysis[key];
    transparencyText(parent, `${label}. These are methodological safeguards, not automatically detected writing errors.`);
    if (!Array.isArray(values)) {
      transparencyText(parent, `NOT RECORDED — analysis.${key} is absent. ${data.stage === "CONCLUSION" && key === "prohibited_conclusions" ? "ConclusionRuleBase.analyze does not configure this array; no catalog has been invented." : "No missing record is treated as an empty list."}`);
      continue;
    }
    for (const wording of values) {
      const explanation = CAUSAL_SCOPE_REASONS[wording];
      transparencyDisclosure(parent, `${label}: ${wording}`, target => causalFacts(target, [
        ["Actual configured record", wording, `OBSERVED — analysis.${key}`],
        ["Producer / emission", `services/${data.stage.toLowerCase()}_rules.py: ${data.stage === "INTRODUCTION" ? "Introduction" : data.stage === "BODY" ? "Body" : "Conclusion"}RuleBase.analyze return object`, explanation ? "SOURCE-VERIFIED LOGIC — unconditional stage-scope statement; not a conditional error detector" : "NOT RECORDED — origin of this wording has not been verified"],
        ["Evidence it qualifies / tempting inference", explanation?.[0]],
        ["Why it applies / unsupported interpretation", explanation?.[1]],
        ["Evidence needed to support the broader claim", explanation?.[2], "STATIC EXPLANATION — capability requirement, not a promised feature"],
        ["Decision effect", "FeedbackService does not read these arrays. A separate unconditional *.LIMITATION.NO_SEMANTIC_VALIDATION event is emitted; Body/Conclusion link that event to their scope caution in Needs Attention. The arrays themselves do not select a warning or change a rule result.", "services/feedback_service.py: generate / generate_body / generate_conclusion"],
      ]));
    }
  }
}

function causalFeedbackInputs(data) {
  const a = data.analysis;
  if (data.stage === "INTRODUCTION") return { text_presence: a.text_presence, lexical_topic_evidence: a.lexical_topic_evidence,
    observable_structure: a.observable_structure, development_evidence: a.development_evidence, sentence_topic_evidence: a.sentence_topic_evidence, sentence_count: data.linguistic?.counts?.sentence_count };
  if (data.stage === "BODY") return { paragraphs: a.paragraphs, cross_paragraph_continuity: a.cross_paragraph_continuity, introduction_to_body_continuity: a.introduction_to_body_continuity };
  return { text_presence: a.text_presence, clause_candidates: a.clause_candidates, lexical_topic_evidence: a.lexical_topic_evidence,
    introduction_to_conclusion_continuity: a.introduction_to_conclusion_continuity, body_to_conclusion_continuity: a.body_to_conclusion_continuity,
    synthesis_structure_candidates: a.synthesis_structure_candidates, closure_candidates: a.closure_candidates, new_material_observations: a.new_material_observations };
}

function causalFeedbackPriority(data, field) {
  const a = data.analysis, s = a.observable_structure || {}, presence = a.text_presence || {}, lex = a.lexical_topic_evidence || {};
  const n = value => Array.isArray(value) ? value.length : null;
  const rows = [];
  const add = (branch, condition, value, passes) => rows.push({ branch, condition, value, passes: value === undefined || value === null ? null : passes });
  const primary = field === "Primary Feedback", next = field === "Next Step";
  if (data.stage === "INTRODUCTION") {
    const focus = lex.observed_focus_terms;
    const broad = Array.isArray(focus) ? focus.filter(term => ["student", "students", "use", "uses", "used", "using"].includes(term.trim().toLowerCase())) : null;
    const specific = Array.isArray(focus) ? focus.filter(term => !broad.includes(term)) : null;
    if (primary) for (const [branch, status] of [["intro_neutral_empty", "EMPTY"], ["intro_neutral_whitespace", "WHITESPACE_ONLY"], ["intro_neutral_punctuation", "PUNCTUATION_ONLY"]]) add(branch, `text_presence.status == ${status}`, presence.status, presence.status === status);
    else add("intro_neutral_write_first", "text_presence.status in EMPTY, WHITESPACE_ONLY, PUNCTUATION_ONLY", presence.status, ["EMPTY", "WHITESPACE_ONLY", "PUNCTUATION_ONLY"].includes(presence.status));
    add("intro_organization_topic_intro", "list_or_fragment_candidate.keyword_list_candidate == true", s.list_or_fragment_candidate?.keyword_list_candidate, s.list_or_fragment_candidate?.keyword_list_candidate === true);
    add("intro_sentence_fluency_complete_sentence", "incomplete_subordinator_candidates count > 0", n(s.incomplete_subordinator_candidates), n(s.incomplete_subordinator_candidates) > 0);
    add("intro_word_choice_specific_subject", "broad focus count > 0 AND specific focus count == 0", specific && { broad: broad.length, specific: specific.length }, broad?.length > 0 && specific?.length === 0);
    add("intro_ideas_topic_match", "observed_focus_terms count == 0", n(focus), n(focus) === 0);
    add("intro_ideas_review_topic_connection", "review_candidates nonempty AND recorded sentence-connection event emitted", a.sentence_topic_evidence?.review_candidates,
      Boolean(a.sentence_topic_evidence?.review_candidates?.length && a.rule_evidence?.some(e => e.rule_id === "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW" && e.triggered !== false && e.fired !== false)));
    add("intro_ideas_state_position", "recorded missing-position event: argumentative assignment cue AND topic discussion AND no modal or first-person stance cue", a.position_statement_evidence?.status,
      Boolean(a.rule_evidence?.some(e => e.rule_id === "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED" && e.triggered !== false && e.fired !== false)));
    const central = n(s.central_direction_candidates), developed = a.development_evidence?.status;
    const reasons = n(a.reason_clause_evidence?.clauses);
    const values = central === null ? null : { central, developed, reason_clause_count: reasons };
    add("intro_ideas_point_and_reason", "central count > 0 AND recorded reason-clause count > 0; lexical overlap does not change neutral review", values, central > 0 && reasons > 0);
    add("intro_ideas_review_details", "central count > 0 AND no recorded because-clause AND structural elaboration", values, central > 0 && reasons === 0 && developed === "STRUCTURAL_ELABORATION_CANDIDATE");
    add("intro_ideas_develop_main_point", "central count > 0 AND no recorded because-clause AND development is not structural elaboration", values, central > 0 && reasons === 0 && developed !== "STRUCTURAL_ELABORATION_CANDIDATE");
    add("intro_ideas_main_point", "no central candidate after earlier checks; limited pattern evidence only", central, central === 0);
  } else if (data.stage === "BODY") {
    const recorded = data.stageTrace?.feedback_decisions?.selection_checks;
    if (Array.isArray(recorded)) {
      for (const check of recorded) {
        add(check.branch, check.condition, check.paragraph_indices, check.condition_matched);
        rows[rows.length - 1].control = `${check.status === "SELECTED" ? "Selected branch (recorded); " : ""}RECORDED FeedbackService selection check: ${check.status}`;
      }
      add("body_neutral_observable", "no supported concern selected; no correction is required by these checks", data.stageTrace.feedback_decisions.selection_status,
        data.stageTrace.feedback_decisions.selection_status === "NO_SUPPORTED_CONCERN_SELECTED");
      rows[rows.length - 1].control = data.stageTrace.feedback_decisions.selection_status === "NO_SUPPORTED_CONCERN_SELECTED"
        ? "Selected branch (recorded); NO_SUPPORTED_CONCERN_SELECTED; no forced lesson" : "Neutral fallback not selected; a supported concern was recorded";
      return rows;
    }
    const paragraphs = a.paragraphs?.filter(p => p.substantive);
    const lists = paragraphs?.filter(p => p.fragment_or_list_candidate?.keyword_list_candidate);
    const shifts = a.cross_paragraph_continuity?.paragraph_pairs?.filter(p => p.status === "NO_EXPLICIT_LEXICAL_LINK_OBSERVED");
    const limited = paragraphs?.filter(p => p.supporting_detail_candidates?.candidates?.length === 0 && p.counts?.sentence_count > 0 && p.clause_structure_candidates?.length && !p.fragment_or_list_candidate?.keyword_list_candidate);
    const repeated = paragraphs?.filter(p => p.repetition_observations?.repeated_sentence_openings?.length);
    add("body_neutral_empty", "substantive paragraph count == 0", n(paragraphs), n(paragraphs) === 0);
    for (const [branch, condition, values] of [["body_organization_paragraph_shape", "first supported list-like paragraph", lists], ["body_ideas_develop_point", "first paragraph with a recorded statement and no additional qualifying development pattern", limited], ["body_sentence_fluency_sentence_beginnings", "first substantive paragraph with recorded repeated sentence beginnings", repeated], ["body_organization_paragraph_link", "first adjacent paragraph pair with a recorded wording-link absence", shifts]]) add(branch, condition, values?.map(p => p.paragraph_index ?? p.paragraph_pair), values?.length > 0);
    add("body_neutral_observable", "fallback only if all preceding supported concern checks fail", "source fallback", true);
  } else {
    add("conclusion_neutral_empty", "alphabetic_word_count == 0", presence.alphabetic_word_count, presence.alphabetic_word_count === 0);
    add("conclusion_organization_bring_together", "text_presence.keyword_list_candidate == true", presence.keyword_list_candidate, presence.keyword_list_candidate === true);
    if (primary) add("conclusion_neutral_review", "clause_candidates count == 0", n(a.clause_candidates), n(a.clause_candidates) === 0);
    add("conclusion_ideas_new_words", "unobserved_concept_candidates count > 0", n(a.new_material_observations?.unobserved_concept_candidates), n(a.new_material_observations?.unobserved_concept_candidates) > 0);
    add("conclusion_ideas_bring_together", "synthesis_structure_candidates.candidates count > 0", n(a.synthesis_structure_candidates?.candidates), n(a.synthesis_structure_candidates?.candidates) > 0);
    if (primary) {
      add("conclusion_organization_clear_ending", "closure_candidates.candidates count > 0", n(a.closure_candidates?.candidates), n(a.closure_candidates?.candidates) > 0);
      add("conclusion_ideas_return_to_point", "observed_focus_terms count > 0", n(lex.observed_focus_terms), n(lex.observed_focus_terms) > 0);
      add("conclusion_neutral_general", "fallback after preceding conditions", "source fallback", true);
    } else {
      add("conclusion_organization_clear_ending", "closure record present or absent after earlier branches do not apply", "source fallback", true);
    }
  }
  const selected = data.stageTrace?.feedback_decisions?.fields?.[field]?.selection_branch;
  const index = rows.findIndex(row => row.branch === selected);
  return rows.map((row, i) => ({ ...row, control: index < 0 ? "NOT RECORDED — selected branch missing/unrecognized" : i > index ? "SKIPPED by source priority after the selected branch; no candidate message claimed" : i === index ? "Selected branch (recorded); condition explanation SOURCE-VERIFIED LOGIC" : "Earlier priority test — SOURCE-VERIFIED LOGIC, not an instrumented Boolean log" }));
}

function causalIndependentFeedback(data, field) {
  const a = data.analysis, rows = [], working = field === "What's Working";
  const add = (condition, values, passes) => rows.push({ condition, values, passes });
  const focus = a.lexical_topic_evidence?.observed_focus_terms;
  if (data.stage === "INTRODUCTION") {
    const s = a.observable_structure || {}, primary = data.stageTrace?.feedback_decisions?.fields?.["Primary Feedback"]?.rule_ids;
    if (!Array.isArray(focus) || !Array.isArray(primary) || !Array.isArray(s.central_direction_candidates) || !Array.isArray(s.incomplete_subordinator_candidates) || !Array.isArray(s.introductory_context_candidates)) return [];
    const broad = focus.filter(term => ["student", "students", "use", "uses", "used", "using"].includes(term.trim().toLowerCase()));
    const specific = focus.filter(term => !broad.includes(term));
    const central = s.central_direction_candidates.length, incomplete = s.incomplete_subordinator_candidates.length;
    if (working) {
      add("specific focus terms exist", { specific }, specific.length > 0);
      const contexts = s.introductory_context_candidates.filter(c => c.topic_match_evidence?.some(m => specific.includes(m.focus_term)));
      add("a context candidate has a specific-focus match", { qualifying_contexts: contexts.length, sentences: contexts.map(c => c.sentence_text) }, contexts.length > 0);
      add("central candidate exists AND no specific focus matched", { central, specific: specific.length }, central > 0 && specific.length === 0);
    } else {
      add("recorded sentence-topic review event exists AND not used in Primary Feedback", a.sentence_topic_evidence,
        Boolean(a.sentence_topic_evidence?.review_candidates?.length && a.rule_evidence?.some(e => e.rule_id === "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW" && e.triggered !== false && e.fired !== false) && !primary.includes("INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW")));
      add("incomplete candidate exists AND incomplete-subordinator ID not used in Primary Feedback", { incomplete, primary_rule_ids: primary }, incomplete > 0 && !primary.includes("INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"));
      add("no focus matched AND no-focus ID not used in Primary Feedback", { observed_focus_count: focus.length, primary_rule_ids: primary }, focus.length === 0 && !primary.includes("INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED"));
      add("otherwise broad-only focus AND focus-observed ID not used in Primary Feedback", { broad, specific, primary_rule_ids: primary }, broad.length > 0 && specific.length === 0 && !primary.includes("INTRO.TOPIC.FOCUS_TERMS_OBSERVED"));
      add("recorded missing-position event AND missing-position ID not used in Primary Feedback", a.position_statement_evidence,
        Boolean(a.rule_evidence?.some(e => e.rule_id === "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED" && e.triggered !== false && e.fired !== false) && !primary.includes("INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED")));
    }
  } else if (data.stage === "BODY") {
    if (!Array.isArray(a.paragraphs)) return [];
    for (const p of a.paragraphs.filter(p => p.substantive)) {
      const id = `Paragraph ${p.paragraph_index}`;
      if (working) {
        if (p.fragment_or_list_candidate?.keyword_list_candidate) {
          add(`${id}: list-like structure — wording matches are retained as observations, not promoted as strengths`, p.fragment_or_list_candidate, false);
          continue;
        }
        add(`${id}: observed focus terms nonempty`, p.observed_focus_terms, p.observed_focus_terms.length > 0);
        add(`${id}: topic_sentence_candidates nonempty`, { candidates: p.topic_sentence_candidates.length }, p.topic_sentence_candidates.length > 0);
        add(`${id}: supporting_detail_candidates.candidates nonempty`, { clauses: p.clause_structure_candidates.length, details: p.supporting_detail_candidates.candidates.length }, p.supporting_detail_candidates.candidates.length > 0);
        const repeated = p.repetition_observations.repeated_surface_content_words;
        add(`${id}: repeated surface terms nonempty (only first term supplies this message)`, repeated[0] || [], repeated.length > 0);
      } else {
        add(`${id}: keyword_list_candidate true`, p.fragment_or_list_candidate, p.fragment_or_list_candidate.keyword_list_candidate === true);
        add(`${id}: recorded clause and no additional candidate, excluding list-like structures`, { clauses: p.clause_structure_candidates.length, details: p.supporting_detail_candidates.candidates.length }, p.clause_structure_candidates.length > 0 && p.supporting_detail_candidates.candidates.length === 0 && !p.fragment_or_list_candidate.keyword_list_candidate);
        add(`${id}: recorded repeated sentence openings`, p.repetition_observations.repeated_sentence_openings, p.repetition_observations.repeated_sentence_openings.length > 0);
      }
    }
    const comparison = a.introduction_to_body_continuity;
    if (!comparison) return rows;
    const available = comparison.status === "LEXICAL_COMPARISON_AVAILABLE";
    const shared = Boolean(comparison.direct_lexical_continuity?.length || comparison.lemma_normalized_continuity?.length);
    if (working) add("Introduction comparison available AND direct/lemma evidence nonempty AND a substantive non-list paragraph exists", { status: comparison.status, direct: comparison.direct_lexical_continuity?.length, lemma: comparison.lemma_normalized_continuity?.length }, available && shared && a.paragraphs.some(p => p.substantive && !p.fragment_or_list_candidate?.keyword_list_candidate));
    else {
      const cross = a.cross_paragraph_continuity;
      add("PAIRWISE_OBSERVATIONS AND any unlinked adjacent paragraph pair", { status: cross?.status, unlinked_pairs: cross?.paragraph_pairs?.filter(p => p.status === "NO_EXPLICIT_LEXICAL_LINK_OBSERVED").map(p => p.paragraph_pair) }, cross?.status === "PAIRWISE_OBSERVATIONS" && cross.paragraph_pairs.some(p => p.status === "NO_EXPLICIT_LEXICAL_LINK_OBSERVED"));
    }
  } else {
    const intro = a.introduction_to_conclusion_continuity, body = a.body_to_conclusion_continuity, synthesis = a.synthesis_structure_candidates, closure = a.closure_candidates, novel = a.new_material_observations;
    if (!Array.isArray(focus) || !intro || !body || !synthesis || !closure || !novel) return [];
    add(working ? "focus terms observed" : "no focus terms observed", focus, working ? focus.length > 0 : focus.length === 0);
    if (!working) {
      add("keyword_list_candidate true", a.text_presence?.keyword_list_candidate, a.text_presence?.keyword_list_candidate === true);
      add("clause_candidates empty", { clauses: a.clause_candidates?.length }, a.clause_candidates?.length === 0);
    }
    for (const [name, comp] of [["Introduction", intro], ["Body", body]]) {
      const shared = Boolean(comp.direct_lexical_continuity?.length || comp.lemma_normalized_continuity?.length);
      add(`${name} comparison available AND ${working ? "some" : "no"} direct/lemma continuity`, { status: comp.status, direct: comp.direct_lexical_continuity?.length, lemma: comp.lemma_normalized_continuity?.length }, comp.status === "LEXICAL_COMPARISON_AVAILABLE" && (working ? shared : !shared));
    }
    if (working) {
      add("synthesis candidates nonempty", { candidates: synthesis.candidates.length }, synthesis.candidates.length > 0);
      add("closure candidates nonempty", { candidates: closure.candidates.length }, closure.candidates.length > 0);
      add("known concept combinations nonempty", novel.phrase_combinations_of_observed_concepts, novel.phrase_combinations_of_observed_concepts.length > 0);
    } else {
      add("unobserved_concept_candidates nonempty", novel.unobserved_concept_candidates, novel.unobserved_concept_candidates.length > 0);
      add("NO_SYNTHESIS_STRUCTURE_CANDIDATE_OBSERVED AND at least one prior comparison available", { synthesis: synthesis.status, introduction: intro.status, body: body.status }, synthesis.status === "NO_SYNTHESIS_STRUCTURE_CANDIDATE_OBSERVED" && [intro.status, body.status].includes("LEXICAL_COMPARISON_AVAILABLE"));
      add("NO_CLOSURE_CANDIDATE_OBSERVED", closure.status, closure.status === "NO_CLOSURE_CANDIDATE_OBSERVED");
      add("unconditional Conclusion method-scope caution (not a writing diagnosis)", "CONCLUSION.LIMITATION.NO_SEMANTIC_VALIDATION", true);
    }
  }
  return rows;
}

function renderCausalFeedback(parent, result, data, field) {
  if (data.stage === "INTRODUCTION" && field === "Primary Feedback" && data.analysis.sentence_topic_evidence) {
    transparencyDisclosure(parent, "Sentence topic-connection observations — wording evidence, not relevance judgments", target => {
      transparencyText(target, "Each sentence reuses the existing spaCy boundaries, focus matches and normalized content words. A neighboring focus match is required; shared wording or a reference cue defers to contextual review. No semantic judgment or new spaCy call is made.");
      renderTransparencyRecord(target, data.analysis.sentence_topic_evidence);
    });
  }
  const d = data.stageTrace?.feedback_decisions?.fields?.[field];
  const links = (result.feedback?.["Feedback Provenance"] || []).filter(item => item.feedback_field === field);
  transparencyText(parent, `${field}: recorded branch ${d?.selection_branch || "NOT RECORDED"}. ${d?.selection_condition || (field === "Current Goal" ? "The selected stage determines a constant teaching goal, independent of writing quality." : "The branch condition was not retained.")}`);
  if (["Primary Feedback", "Next Step"].includes(field)) {
    for (const row of causalFeedbackPriority(data, field)) {
      transparencyText(parent, `${row.branch}: required ${row.condition}; retained value ${causalValue(row.value)}. ${row.control}. ${row.control.startsWith("SKIPPED") ? "No condition outcome asserted for this later branch." : `Source comparison: ${row.passes === null ? "NOT RECORDED" : row.passes ? "satisfied" : "not satisfied"}.`}`);
    }
  } else if (field !== "Current Goal") {
    transparencyText(parent, "SOURCE-VERIFIED LOGIC — this list uses independent append checks, not the Primary Feedback priority chain. Introduction suppresses some duplicate cautions already used by Primary Feedback; Body/Conclusion may repeat a concern. Field-level provenance does not establish item-by-item alignment or a hidden ranking.");
    const checks = causalIndependentFeedback(data, field);
    if (!checks.length) transparencyText(parent, "NOT RECORDED — retained inputs are insufficient for independent append-check reconstruction.");
    for (const check of checks) causalFacts(parent, [["Required condition", check.condition], ["Retained values", check.values], ["Source-derived append condition", check.passes ? "satisfied — this condition supports adding its message" : "not satisfied — this condition adds no message", "SOURCE-VERIFIED LOGIC — not a recorded item-by-item execution log"]]);
  }
  causalFacts(parent, [["Exact backend output", result.feedback?.[field], `OBSERVED — feedback[${JSON.stringify(field)}]`], ["Supporting emitted IDs", links.map(item => item.rule_id).join(", ") || "No link recorded"], ["Alternatives", data.stageTrace?.feedback_decisions?.unselected_alternatives || "NOT RECORDED — unselected message texts and a hidden ranking were not retained"]]);
  for (const item of links) {
    const row = (data.analysis.rule_evaluation_trace || []).find(row => row.rule_id === item.rule_id);
    if (row) transparencyText(parent, causalRuleModel(row, result, data).summary);
  }
  transparencyDisclosure(parent, `${field}: actual consumed findings and emitted-event provenance`, target => renderTransparencyRecord(target, { findings: causalFeedbackInputs(data), decision: d, provenance: links.map(item => resolveStudentFeedbackProvenance(item, result)) }));
}

function renderCausalTutor(parent, result, data) {
  const model = studentFeedbackPresentation(result), text = transparencyTextSources(data).text;
  transparencyText(parent, data.stage === "BODY" && model.instructional_feedback
    ? `The existing presentation model returned ${model.tutor_items.length} tutor item(s) from the completed Body instructional record. Status: ${model.instructional_feedback.selection_status}. Prepared concerns require their recorded binding, fired events and field provenance; a neutral result has no trait, lesson, improvement task or error mark. This inspector only reads the cached response.`
    : `DERIVED — the existing presentation model returned ${model.tutor_items.length} tutor section(s). selectTutorItems selects the recorded primary branch first, then at most two independently supported Needs Attention lessons. It requires matching message/provenance counts, emitted events and prepared bindings; limitation events and duplicate lessons are excluded. No new lesson decision is made by this inspector.`);
  for (const item of model.tutor_items) {
    const excerpt = item.excerpt;
    causalFacts(parent, [["Selected tutor section", item.label || item.role], ["Prepared lesson", item.lesson_id || "No verified lesson mapping; original/fallback presentation", "content/lessons/feedback_help.json; static/app.js: selectScaffoldingGuidance / selectTutorItems / buildTutorItem"], ["Supporting Rule Events", item.rule_ids], ["Actual tutor observation", item.noticed], ["Source highlight", excerpt?.contexts?.length ? excerpt.contexts : "Omitted — no supported excerpt; neutral review, section-wide absence, missing evidence or changed editor must not become an invented highlight"], ["Limitation", item.limitation]]);
    for (const context of excerpt?.contexts || []) {
      transparencyText(parent, `DERIVED — tutor context [${context.start}, ${context.end}): ${Array.from(excerpt.source).slice(context.start, context.end).join("")}. Source agrees with retained essay: ${excerpt.source === text}. The existing tutor validates integer Unicode-code-point bounds and exact evidence text equality before retaining a context. Missing/mismatched positions are omitted.`);
      transparencyText(parent, `Actual mark bounds: ${causalValue(context.marks)}. renderEditorHighlight uses this verified context for the editor's highlighted sentence/paragraph; the evidence view can mark the narrower evidence within it.`);
    }
  }
  transparencyDisclosure(parent, "Actual teaching mapping, sections and source-highlight records", target => renderTransparencyRecord(target, model));
}

function causalPanelModel(key, result, data) {
  const [main, sub] = key.split(":"), a = data.analysis, lex = a.lexical_topic_evidence || {};
  const fields = { goal: "Current Goal", primary: "Primary Feedback", working: "What's Working", attention: "Needs Attention", next: "Next Step" };
  const nlpKeys = { overview: "overview", sentences: "overview", tokens: "tokenization", lemmas: "lemmatization", pos: "pos", dependencies: "dependencies", chunks: "noun-chunks", pipeline: "pipeline" };
  const metadata = STUDENT_TRANSPARENCY_PROCESS_INFO[main === "nlp" ? `processing:${nlpKeys[sub]}` : main === "concept" ? "processing:concepts" : main === "engine" ? `feedback:${sub}` : main === "rules" ? `rules:${sub === "sources" ? "code" : ["stage", "trace"].includes(sub) ? "overview" : sub}` : key] || {};
  const model = { input: undefined, inputPath: "NOT RECORDED", purpose: metadata.why, method: metadata.how, source: metadata.source,
    result: "NOT RECORDED", usage: "NOT RECORDED — no per-item consumer record is retained.", limitation: metadata.limitation || "The method observes linguistic/lexical patterns rather than verifying meaning.", field: fields[sub] };
  if (main === "student") {
    const input = studentTextInputEvidence(result);
    Object.assign(model, { input, inputPath: input.text_source, purpose: "Bind every observation to the exact analyzed version, rather than a later edit.", method: "Read agreeing retained text sources; derive code-point/whitespace counts separately. The existing snapshot viewer below preserves the exact text.", source: "static/app.js: studentTextInputEvidence / renderStudentInputInspector", result: `${input.code_point_characters ?? "NOT RECORDED"} Unicode code points; ${input.whitespace_words ?? "NOT RECORDED"} whitespace words. Stage ${input.stage}; exact HTTP payload NOT RECORDED.`, usage: "SOURCE-VERIFIED LOGIC — performStageAnalysis submits stage/context; accepted response is cached only after snapshot checks. Opening these tabs reads the cache.", limitation: "Retained input proves what was analyzed, not saving, readiness or quality. Browser textarea normalization before capture is not logged." });
  } else if (main === "backend") Object.assign(model, { input: { stage_id: result.stage_id, availability: result.availability, assignment_topic: a.assignment_topic, teacher_context: data.trace?.teacher_context, input_sections: data.stageTrace?.input_sections }, inputPath: "stage_id; analysis.assignment_topic; research_trace.teacher_context; research_trace.stages.*.input_sections", purpose: "Associate analysis with the permitted assignment and stage so another user's assignment or an invalid field cannot become analysis context.", method: "SOURCE-VERIFIED LOGIC — require_account / require_csrf_token precede analyze_payload; saved assignments use authorized lookup, practice uses submitted topic/focus. Allowed stage, field types and lengths are checked before EssayAnalysisService.analyze. Individual outcomes and exact HTTP payload are NOT RECORDED.", source: "app.py: require_account / require_csrf_token / analyze_payload / compact_student_transparency_trace", result: `OBSERVED — stage_id=${result.stage_id}, availability=${result.availability}. Accepted retained values shown in technical evidence; authorization-check details are NOT RECORDED.`, usage: "SOURCE-VERIFIED LOGIC — accepted text/context goes to EssayAnalysisService.analyze; selected stage analysis and feedback return to displayFeedback. Failed validation returns an error rather than this analyzed response.", limitation: "A successful response supports acceptance, not a per-check audit log. Request-handler timing and database-resolution steps were not serialized." });
  else if (main === "nlp") {
    const outputs = { sentences: data.sentences, tokens: data.tokens, lemmas: data.tokens, pos: data.tokens, dependencies: data.sentences.map(item => item.dependencies), chunks: data.linguistic?.noun_phrases, pipeline: data.trace?.runtime?.pipeline, overview: data.linguistic?.counts };
    const methods = {
      sentences: "NLPService.analyze_doc iterates Doc.sents, removes space tokens, and sets bounds from first/last nonspace token. Sentence text is the original source slice; paragraph helpers later intersect these spans.",
      tokens: "spaCy's tokenizer creates Doc tokens; _token_data serializes nonspace tokens with Token.i, idx and idx+len(token). Punctuation remains, so token count differs from alphabetic count.",
      lemmas: "The loaded pipeline assigns Token.lemma_; _token_data preserves the prediction. TopicService._lemma uses lemma or original text, then Python casefold for normalization. The inspector displays the recorded forms rather than performing another lemmatization.",
      pos: "The configured tagger/attribute pipeline assigns broad POS and fine tags. Clause filters require VERB/AUX, VB/VBD/VBP/VBZ and a permitted dependency with a linked subject; concepts require alphabetic NOUN/PROPN or qualifying noun chunks.",
      dependencies: "The parser assigns dependency/head. analyze_doc serializes head_start separately from tokens. Clause candidates require a subject edge whose head_start equals the predicate start, plus POS/tag/dependency eligibility.",
      chunks: "Doc.noun_chunks supplies parser-derived phrase spans. _extract_concepts reads those chunks from the same Doc, filters alphabetic tokens and requires at least one NOUN/PROPN. The serialized noun_phrases list is an inspection copy, not its input.",
      pipeline: "NLPService.parse calls the loaded Language once for each supplied section. Enabled components annotate the shared Doc; metadata identifies disabled components. Per-component timing and model-internal decision scores are NOT RECORDED.",
      overview: "NLPService.parse creates one Doc; analyze_doc counts alphabetic tokens and serializes nonspace tokens, sentence spans and noun chunks. TopicService and stage rules reuse these annotations.",
    };
    Object.assign(model, { input: outputs[sub], inputPath: `linguistic_observations.${sub === "chunks" ? "noun_phrases" : sub === "pipeline" ? "(runtime.pipeline and topic_service.steps)" : sub === "overview" ? "counts" : ["lemmas", "pos"].includes(sub) ? "tokens" : sub}`,
      purpose: metadata.why || "Provide source-linked sentence boundaries for later clause and paragraph checks.", method: methods[sub], source: "services/nlp_service.py: parse / analyze_doc / _token_data; services/topic_service.py: analyze / _extract_concepts / _find_matches",
      result: `Retained ${data.tokens.length} token records and ${data.sentences.length} sentence records; recorded alphabetic count ${data.linguistic?.counts?.alphabetic_word_count ?? a.text_presence?.alphabetic_word_count ?? "NOT RECORDED"}. ${Array.isArray(outputs[sub]) ? `${outputs[sub].length} ${sub} records are available.` : `Selected output: ${causalValue(outputs[sub])}.`}`,
      usage: "SOURCE-VERIFIED LOGIC — sentence tokens/heads feed clause heuristics; lemmas/POS feed lexical matching and concept extraction. NER annotations are not consumed by active Rule Bases. Actual accepted clauses/concepts/matches are linked in technical evidence; annotation presence alone is not acceptance.",
      limitation: "Final annotations and spans are retained, but why the trained model chose a particular POS, lemma, head or sentence boundary is NOT RECORDED. These are predictions, not grammatical ground truth." });
  } else if (main === "concept") Object.assign(model, { input: data.concepts, inputPath: "research_trace.stages.*.topic_service / student_concepts; linguistic_observations.tokens and noun_phrases are retained Doc annotations", purpose: "Supply noun-based lexical candidates for paragraph recurrence and earlier-section comparison.", method: "Read alphabetic noun-chunk tokens containing NOUN/PROPN, plus individual alphabetic NOUN/PROPN tokens. Normalize each via casefolded lemma-or-text, group equal forms, deduplicate equal spans, count retained occurrences.", source: "services/topic_service.py: _extract_concepts / _lemma", result: Array.isArray(data.concepts) ? `${data.concepts.length} normalized groups, ${data.concepts.reduce((n, c) => n + c.occurrences.length, 0)} retained occurrences. Each original span and extraction criterion is explained below.` : "NOT RECORDED — full-stage concepts were not retained.", usage: data.stage === "INTRODUCTION" ? "SOURCE-VERIFIED LOGIC — IntroductionRuleBase does not consume its concept list. In a request with later sections, prepared Introduction concepts can be comparison inputs; that future use is not implied by this selected response." : "SOURCE-VERIFIED LOGIC — Body filters occurrences into paragraph spans for recurrence; Conclusion compares normalized concepts with earlier sections for synthesis/new-material. Actual containing records are shown, not an assumption that each concept selected feedback.", limitation: "Noun-based selection misses non-nominal ideas; shared forms and occurrence counts do not measure importance or meaning. Rejected candidate logs are NOT RECORDED." });
  else if (main === "topic") {
    const source = sub === "related" ? result.related_topic_concept_evidence : sub === "wordnet" ? data.stageTrace?.topic_service?.steps?.find(step => step.id === "wordnet_direct_suggestions") : sub === "cross-stage" ? Object.fromEntries(Object.entries(a).filter(([k]) => k.endsWith("_continuity"))) : { teacher_context: data.trace?.teacher_context, lexical_topic_evidence: lex };
    Object.assign(model, { input: source, inputPath: sub === "related" ? "related_topic_concept_evidence" : sub === "cross-stage" ? "analysis.*_continuity; research_trace.stages.*.input_sections" : "research_trace.teacher_context; analysis.lexical_topic_evidence; topic_service.steps",
      result: sub === "related" ? `Recorded informational status: ${result.related_topic_concept_evidence?.execution_status || "NOT RECORDED"}. This branch does not alter lexical coverage or feedback.` : sub === "wordnet" ? "Each path's recorded status, synset intersection and candidate_emitted flag are inspected separately below. An executed lookup is not a feedback decision." : sub === "cross-stage" ? `Recorded comparison statuses: ${Object.entries(a).filter(([k]) => k.endsWith("_continuity")).map(([k, v]) => `${k}=${v.status}`).join("; ") || "NOT APPLICABLE — Introduction has no earlier-section comparison"}.` : `Recorded observed terms: ${(lex.observed_focus_terms || []).join(", ") || "none"}; unobserved terms: ${(lex.unobserved_focus_terms || []).join(", ") || "none"}; ${lex.matches?.length ?? "NOT RECORDED"} matched occurrences.`,
      usage: ["related", "wordnet"].includes(sub) ? "SOURCE-VERIFIED LOGIC — related concepts are informational only. Direct WordNet candidates are retained suggestions. Cross-stage WordNet candidates may emit informational Rule Events and be copied into Conclusion paraphrase observations; FeedbackService reads direct/lemma continuity and unobserved-concept findings, not WordNet candidates." : "SOURCE-VERIFIED LOGIC — matches contribute unique focus coverage, paragraph-local focus and clause/context findings. FeedbackService consumes these observations; per-occurrence causal attribution is not separately recorded.",
      limitation: "No accepted candidate means the implementation emitted none, not that words are unrelated. Exact/lemma overlap and one shared synset cannot establish contextual relevance; no word-sense disambiguation is performed." });
  } else if (main === "rules") Object.assign(model, { input: { linguistic: data.linguistic, lexical: lex, earlier_sections: data.stageTrace?.input_sections }, inputPath: "prepared TopicService linguistic_analysis / confirmed_lexical_observations / focus_coverage and supplied earlier concepts", purpose: "Turn specific structural and lexical observations into inspectable stage findings and Rule Events.", method: "Stage helpers calculate findings; _rule_events tests the resulting fields. Research Inspector later reconstructs the registry statuses from retained findings/events. Detailed measured comparisons are available for every retained row.", source: `services/${data.stage.toLowerCase()}_rules.py: analyze / _rule_events; services/research_inspector.py: _observed_rule_decisions / build_rule_evaluation_trace`, result: `${a.rule_evidence?.length ?? "NOT RECORDED"} emitted events; ${a.rule_evaluation_trace?.length ?? "NOT RECORDED"} reconstructed evaluation records. These are different records, not two executions.`, usage: "SOURCE-VERIFIED LOGIC — FeedbackService selects messages using stage observations, then attaches event provenance. The later evaluation trace cannot cause the already-selected message. Actual links and source comparisons appear per rule.", limitation: "A failed heuristic is not a quality judgment; skipped/unavailable is not false. Source-derived comparisons are not a recorded short-circuit log. Uncertainty and prohibited conclusions are methodological scope, not detected errors." });
  else if (main === "engine") Object.assign(model, { input: causalFeedbackInputs(data), inputPath: "analysis stage findings + analysis.rule_evidence (emitted flags accepted by _emitted_events)", purpose: "Select one prioritized revision message, a separate next step, independent observation/caution lists and a constant stage goal.", method: "The stage FeedbackService function uses explicit if/elif priority for Primary Feedback and Next Step. Positive/caution lists use separate tests. Source-derived comparisons below stop claiming outcomes after the selected priority branch; no hidden ranking is invented.", source: `services/feedback_service.py: ${data.stage === "INTRODUCTION" ? "generate" : data.stage === "BODY" ? "generate_body" : "generate_conclusion"} / _emitted_rule_ids`, result: model.field ? `${model.field}: ${causalValue(result.feedback?.[model.field])}; branch ${data.stageTrace?.feedback_decisions?.fields?.[model.field]?.selection_branch || "NOT RECORDED"}.` : `Primary branch ${data.stageTrace?.feedback_decisions?.fields?.["Primary Feedback"]?.selection_branch || "NOT RECORDED"}; ${result.feedback?.["Feedback Provenance"]?.length ?? "NOT RECORDED"} field-level event links.`, usage: "OBSERVED / DERIVED — the retained backend fields feed studentFeedbackPresentation. Prepared lessons are selected by the existing branch mapping; independently supported concerns may appear separately. Informational events are not automatically lesson causes.", limitation: "Unselected candidate messages and item-level append logs are not retained. A field-level provenance link is not a hidden score or proof of a particular list-item alignment." });
  else if (main === "final") Object.assign(model, { input: { feedback: result.feedback, availability: result.availability, decision: data.stageTrace?.feedback_decisions }, inputPath: "retained response.feedback; feedback_decisions; existing studentFeedbackPresentation model", purpose: "Show the actual teaching presentation and its source without changing feedback or writing.", method: "selectScaffoldingGuidance checks the recorded Primary Feedback branch and prepared binding. selectTutorItems may add supported secondary lessons. tutorVerifiedSpan validates exact code-point source equality before highlighting. Complete Evidence and Copy Full Analysis read the same cached response.", source: "static/app.js: selectScaffoldingGuidance / selectTutorItems / buildTutorItem / tutorVerifiedSpan / studentFeedbackPresentation / buildFullAnalysisReport", result: `Selected stage ${result.stage_id}; backend Primary Feedback: ${causalValue(result.feedback?.["Primary Feedback"])}. Technical evidence shows the real prepared tutor sections and highlights.`, usage: "DERIVED — presentation is rendered to the Writing Tutor and available in export. It does not rerun analysis or save writing. A display fallback is frontend-prepared, not a backend finding.", limitation: "A lesson label is an instructional review focus, not a validated classification. Highlights localize verified retained evidence; omission of a highlight does not mean no concern exists." });
  return model;
}

function causalMissingEvidence(main, sub, data) {
  // Rows must describe records the source truly never retains; never a fabricated gap.
  const rows = [["Exact HTTP request payload as serialized by the browser", "static/app.js performStageAnalysis builds the body from stage text and context; only retained fields are echoed back"]];
  if (main === "student") rows.push(["Save/readiness state at analysis time", "The accepted response records analyzed text and context, not a save or readiness audit"]);
  if (main === "backend") rows.push(["Per-field validation and authorization decision outcomes", "app.py checks run before analysis; only acceptance is observable in a successful response"], ["Request-handler timing and database-resolution steps", "Not serialized into the compact response"]);
  if (main === "nlp") rows.push(["Model-internal decision scores for POS, lemma, head and sentence boundaries", "spaCy annotations retain final values only"], ["Per-component runtime timings", "services/nlp_service.py records enabled/disabled components, not timings"]);
  if (main === "concept") rows.push(["Candidate concepts rejected during extraction", "services/topic_service.py returns grouped occurrences, not a rejection log"]);
  if (main === "topic") {
    rows.push(["Rejected lexical windows and unreturned consultations", "services/topic_service.py retains matches and step statuses, not rejected windows"]);
    if (sub === "wordnet") rows.push(["Word-sense disambiguation of any candidate", "Not implemented — direct lookup records synset intersection only"]);
    if (["cross-stage", "related"].includes(sub)) rows.push(["Full earlier-stage concept sets beyond the compact retained comparison findings", "research_trace.stages.*.input_sections retains availability/text context; comparison output is compact"]);
  }
  if (main === "rules") rows.push(["Per-request short-circuit/evaluation log", "rule_evaluation_trace is reconstructed after feedback from retained findings and events (services/research_inspector.py)"], ["Boolean safeguard flags for subordinator helpers", "Only final candidate lists and retained sentence/token records are serialized"], ["Full earlier-stage concept sets beyond compact comparison findings", "Input sections retain text availability; concept comparison output is compact"]);
  if (main === "engine") rows.push(["Unselected candidate messages", "services/feedback_service.py returns only chosen field values"], ["Item-by-item append/provenance log", "Field-level Feedback Provenance links only"], ["Hidden score or alternative ranking", "Selection is a fixed if/elif order; no score is computed"]);
  if (main === "final") rows.push(["Reasons a paragraph or phrase was not highlighted", "Highlighting marks verified retained evidence; absence of a highlight is not an evaluation"], ["Item-level mapping from each list row to a provenance event", "Field-level provenance only"]);
  return rows;
}

function renderCausalPanel(parent, key, result, data, tabs) {
  const [main, sub] = key.split(":"), model = causalPanelModel(key, result, data);
  // Keep the technical heading in Advanced Inspector; details open on demand.
  const host = document.createElement("section");
  host.className = "transparency-section transparency-operation student-input-inspector causal-explanation";
  host.dataset.causalPanel = key;
  if (main === "backend") {
    const heading = document.createElement("h3");
    heading.textContent = "Why this analysis produced this result";
    host.appendChild(heading);
  }
  parent.appendChild(host);
  const source = studentTextInputEvidence(result);
  if (main !== "student") {
    const button = document.createElement("button"); button.type = "button"; button.className = "button-secondary";
    button.textContent = "Inspect exact analyzed essay and earlier-stage context";
    button.addEventListener("click", () => tabs.activate("student", "context")); host.appendChild(button);
  }
  transparencyDisclosure(host, "Technical causal walkthrough — actual values, conditions, sources and alternatives", target => {
    target.dataset.causalDetails = key;
    if (main !== "student" && !["wordnet", "cross-stage"].includes(sub)) transparencyDisclosure(target, "Exact analyzed snapshot (preserved whitespace and Unicode offsets)", essay => {
      studentSourceViewer(essay, source.text, `${data.stage}: exact analyzed snapshot`);
      for (const prior of source.earlier_sections) { transparencyText(essay, `${prior.stage}: ${prior.status}; ${prior.source}`); if (prior.text !== null) studentSourceViewer(essay, prior.text, `Earlier ${prior.stage} context`); }
    });
    if (main === "rules") {
      if (sub === "stage") {
        renderCausalLimits(target, data);
        if (data.stage === "INTRODUCTION") renderCausalSubordinators(target, data);
        if (data.stage === "BODY") renderCausalParagraphs(target, data);
        renderCausalStageObservations(target, data);
      }
      let rows = data.analysis.rule_evaluation_trace || [];
      if (sub === "triggered") rows = rows.filter(row => (data.analysis.rule_evidence || []).some(event => event.rule_id === row.rule_id));
      if (sub === "not-triggered") rows = rows.filter(row => row.status !== "TRIGGERED");
      for (const row of rows) renderCausalRule(target, row, result, data);
      if (!rows.length) transparencyText(target, "NOT RECORDED — no applicable evaluation rows retained; no negative result inferred.");
    } else if (main === "engine" || main === "final" && ["overview", "fields"].includes(sub)) {
      for (const field of model.field ? [model.field] : ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"]) renderCausalFeedback(target, result, data, field);
      if (main === "final" || sub === "primary") renderCausalTutor(target, result, data);
    } else if (main === "final") {
      if (sub === "limitations") renderCausalLimits(target, data);
      else renderCausalTutor(target, result, data);
    } else if (main === "nlp") renderCausalAnnotations(target, data, sub);
    else if (main === "concept") renderCausalConcepts(target, data);
    else if (main === "topic") renderCausalTopic(target, result, data, sub);
    transparencyDisclosure(target, "Complete relevant retained input / output fields", detail => renderTransparencyRecord(detail, model.input));
    const missing = causalMissingEvidence(main, sub, data);
    if (missing.length) {
      transparencyText(target, "Evidence the implementation never retains for this operation — each row is NOT RECORDED with its origin, so this walkthrough cannot be mistaken for a request or execution log:");
      for (const [item, origin] of missing) causalFacts(target, [[item, "NOT RECORDED", origin]]);
    }
  });
}

function renderCausalParagraphs(parent, data) {
  transparencyText(parent, "SOURCE-VERIFIED LOGIC — BodyRuleBase._paragraph_spans → stage_evidence.split_paragraph_spans splits on blank lines, trims outer whitespace and keeps internal newlines. _analyze_paragraph filters full-text tokens/concepts/matches to each span; sentence_segments_in_span intersects sentence boundaries without reparsing.");
  for (const p of data.analysis.paragraphs || []) {
    const clauses = p.clause_structure_candidates?.length;
    causalFacts(parent, [[`Paragraph ${p.paragraph_index} original`, p.text, `[${p.start}, ${p.end}) — ${causalSpan(transparencyTextSources(data).text, p)}`], ["Input counts", p.counts], ["Substantive", p.substantive, "any span-contained token.is_alpha; controls FeedbackService substantive paragraph loop"], ["Why detail result occurred", `${clauses ?? "NOT RECORDED"} subject-linked clauses; required >= 2; recorded detail candidates ${p.supporting_detail_candidates?.candidates?.length ?? "NOT RECORDED"}`, "_supporting_detail_candidates; sentence count is not the threshold"], ["Why topic-sentence candidates occurred", `${p.topic_sentence_candidates?.length ?? "NOT RECORDED"} retained; each needs a clause AND a same-sentence focus match OR a concept recurring in at least two paragraph sentences`, "_topic_sentence_candidates; exact per-candidate reason below"], ["Informational observations", "prominent_concept_candidates is not directly read by FeedbackService; example markers alone do not satisfy supporting details. UNITY and normalized-repetition events do not automatically select a message."], ["Limit", "Clause count does not validate the quality of support; shared lemmas do not establish unity of meaning."]]);
    transparencyDisclosure(parent, `Paragraph ${p.paragraph_index}: exact reasons, predicates, matches, recurrence and consumer inputs`, target => renderTransparencyRecord(target, p));
  }
}

function renderCausalStageObservations(parent, data) {
  const a = data.analysis;
  const definitions = data.stage === "INTRODUCTION" ? [
    ["text_presence", "analyze", "Read linguistic.counts.alphabetic_word_count; zero selects EMPTY/WHITESPACE_ONLY/PUNCTUATION_ONLY by exact text. Otherwise clauses, warning candidates and root candidates determine the structural statuses.", "FeedbackService.generate uses status for initial empty-input branches; _rule_events uses the alphabetic count."],
    ["observable_structure", "_clause_candidates / _context_candidates / _list_or_fragment_finding / _incomplete_subordinator_evidence", "Qualifying predicates need VERB/AUX, a permitted finite tag and dependency, plus a subject linked by head_start. ROOT subset gives central-direction candidates. Same-sentence focus matches plus central candidates give context candidates. List, fragment and warning findings are independent tests.", "_rule_events emits based on these lists/flags; FeedbackService reads them in its priority chain and independent checks."],
    ["development_evidence", "_development_finding", "Exclude all clauses in any sentence with an incomplete-subordinator candidate; count remaining predicates. >=2 selects STRUCTURAL_ELABORATION_CANDIDATE, otherwise NO_ADDITIONAL_CLAUSE_ELABORATION_OBSERVED.", "_rule_events and FeedbackService central-clause primary/next-step branches read the status."],
  ] : data.stage === "BODY" ? [
    ["cross_paragraph_continuity", "_cross_paragraph_continuity", "Compare neighboring substantive paragraphs' alphabetic content-token surfaces and lemmas. A shared lemma or a listed transition in the right paragraph produces a lexical/transition candidate; otherwise retain NO_EXPLICIT_LEXICAL_LINK_OBSERVED.", "generate_body prioritizes supported list, development and repetition concerns before optional adjacent-wording review; missing shared words do not establish semantic disconnection."],
    ["introduction_to_body_continuity", "_introduction_continuity / stage_evidence.compare_stage_concepts", "No Introduction means unavailable. Otherwise compare exact surface occurrences within common normalized concept forms; preserve direct and lemma matches separately, then optional WordNet candidates.", "generate_body uses availability and direct/lemma lists; WordNet events are informational."],
  ] : [
    ["text_presence", "_text_presence", "Count alphabetic tokens, sentences and paragraphs from the shared linguistic observations. No alphabetic tokens selects empty/nonalphabetic status; clause availability determines structural status.", "generate_conclusion first tests alphabetic count, then keyword-list flag."],
    ["conclusion_paragraphs", "_paragraphs", "Blank-line segmentation and span-filtered tokens/sentence segments reuse the existing Doc.", "Retained paragraph observations and text_presence counts; not a separate rhetorical-closure verdict."],
    ["clause_candidates", "stage_evidence.clause_candidates_from_sentences", "Finite VERB/AUX with permitted dependency and exact subject-to-predicate head link.", "No-clause Primary Feedback branch; synthesis requires a clause; final ROOT candidates feed closure."],
    ["keyword_list_candidate", "_keyword_list_finding", "Alphabetic text and no qualifying clause, plus at least three sentences or four NOUN/PROPN tokens.", "Rule Event emission; FeedbackService reads the corresponding text_presence.keyword_list_candidate."],
    ["synthesis_structure_candidates", "_synthesis_candidates", "Require prior context. For each clause-bearing sentence, retain concepts whose normalized form and occurrence were also present earlier. At least two distinct matched concepts in that sentence produce a candidate.", "Primary branch after new-material; independent working/attention and Next Step checks."],
    ["closure_candidates", "_closing_candidates", "A ROOT clause in the last sentence or any configured closing-expression span supplies a candidate. Modal/recommendation words in the last sentence are retained separately.", "Primary/Next Step and working/attention read candidates/status; modal-cue events are informational."],
    ["new_material_observations", "_new_material_observations / _occurrence_is_nested_in_larger_phrase", "Skip previously observed normalized forms, closing-expression spans and component occurrences inside larger concept phrases. Compare content-POS lemmas of remaining concepts to earlier concept words. Unseen words produce unobserved candidates; otherwise nonempty content words produce known-word combinations. WordNet paraphrases are copied separately and do not remove unobserved candidates.", "generate_conclusion prioritizes nonempty unobserved_concept_candidates after text/list/no-clause checks; phrase combinations can add What's Working. Paraphrase candidates do not select a branch."],
    ["repetition_observations", "stage_evidence.repetition_observations", "Group alphabetic content-token surfaces/lemmas with count >1 and identical first two alphabetic sentence words.", "Repetition events retained; generate_conclusion does not read repetition_observations for message selection."],
  ];
  for (const [key, producer, how, use] of definitions) {
    transparencyDisclosure(parent, `${key}: producer → criteria → observed result → consumer`, target => {
      causalFacts(target, [["Producer", `services/${data.stage.toLowerCase()}_rules.py: ${producer}`, "Shared helpers explicitly named stage_evidence are in services/stage_evidence.py"], ["Purpose / actual criteria", how, "SOURCE-VERIFIED LOGIC — explains the retained result; intermediate rejection logs may be absent"], ["Actual output", a[key]], ["Actual consumer condition", use]]);
      if (key === "synthesis_structure_candidates") for (const c of a[key]?.candidates || []) causalFacts(target, [["Sentence", c.sentence_text, causalValue(c.sentence_span)], ["Measured requirement", `${c.earlier_concept_matches.length} earlier concept matches >= 2; ${c.clause_candidates.length} qualifying clause(s) > 0`], ["Exact earlier concepts", c.earlier_concept_matches.map(m => m.normalized_form)]]);
      if (key === "new_material_observations") for (const c of a[key]?.unobserved_concept_candidates || []) causalFacts(target, [["Why marked unobserved", `${c.normalized_form}: retained unseen content lemmas ${c.unobserved_content_lemmas.join(", ")}`], ["Original occurrences", c.conclusion_occurrences], ["Limits", "Earlier concept word set and every rejected occurrence are NOT RECORDED in the compact response. Lexically unseen does not prove a genuinely new argument."]]);
      if (key === "development_evidence") causalFacts(target, [["Measured supported predicate count", a[key]?.predicate_count], ["Excluded sentence indices", (a.observable_structure?.incomplete_subordinator_candidates || []).map(c => c.sentence_index)], ["Retained predicate evidence", a[key]?.evidence]]);
    });
  }
  transparencyDisclosure(parent, "Missing observable elements — origin and dependent events", target => {
    transparencyText(target, `SOURCE-VERIFIED LOGIC — services/${data.stage.toLowerCase()}_rules.py:_missing_elements (Body also _paragraph_missing_elements) packages absent heuristic findings and their Rule IDs. These records document missing observations, not a quality score. FeedbackService reads the underlying stage findings rather than this list.`);
    for (const item of a.missing_observable_elements || []) causalFacts(target, [["Actual missing observation", item], ["Event retained", (a.rule_evidence || []).find(e => e.rule_id === item.rule_id) || "No corresponding event retained"]]);
  });
}

function renderCausalAnnotations(parent, data, sub) {
  const text = transparencyTextSources(data).text;
  if (sub === "sentences" || sub === "overview") for (const s of data.sentences) causalFacts(parent, [["Sentence output", s.text, `[${s.start}, ${s.end}) — ${causalSpan(text, s)}`], ["Why these bounds", "First and last nonspace tokens inside recorded Doc.sents span; model-internal boundary reasoning NOT RECORDED", "NLPService.analyze_doc"], ["Later use", "Sentence index/span bounds clause candidates and same-sentence focus evidence; paragraph segmentation may clip it"]]);
  if (["tokens", "lemmas", "pos", "dependencies"].includes(sub)) for (const token of data.tokens) {
    const sentence = data.sentences.find(s => s.start <= token.start && token.end <= s.end);
    const edge = sentence?.dependencies?.find(e => e.start === token.start);
    const subjectLinks = sentence?.dependencies?.filter(e => ["nsubj", "nsubjpass", "csubj", "csubjpass"].includes(e.dependency) && e.head_start === token.start) || [];
    const eligible = ["VERB", "AUX"].includes(token.pos) && ["VB", "VBD", "VBP", "VBZ"].includes(token.tag) && ["ROOT", "conj", "advcl", "ccomp", "xcomp", "relcl"].includes(token.dependency);
    causalFacts(parent, [[`Token ${token.index}: ${token.text}`, `lemma=${token.lemma}; POS=${token.pos}; tag=${token.tag}; dependency=${token.dependency}; head=${edge?.head ?? token.head}; head_start=${edge?.head_start ?? "NOT RECORDED"}`, `[${token.start}, ${token.end}) — ${causalSpan(text, token)}`], ["Alphabetic filter", token.is_alpha, "OBSERVED — NLPService uses this for alphabetic count; TopicService uses it for lexical windows"], ["Clause eligibility comparison", `${eligible ? "POS/tag/dependency pass" : "POS/tag/dependency do not all pass"}; ${subjectLinks.length} linked subject(s)`, "SOURCE-VERIFIED LOGIC — eligible predicate plus at least one exact subject head link; Introduction central candidates additionally require ROOT"], ["Actual lexical/concept occurrence links", { matches: (data.analysis.lexical_topic_evidence?.matches || []).filter(m => m.source_token_indices?.includes(token.index)).map(m => ({ focus_term: m.focus_term, method: m.match_method })), concepts: (data.concepts || []).filter(c => c.occurrences?.some(o => o.source_token_indices?.includes(token.index))).map(c => c.normalized_form) }, "DERIVED links by retained token index; no claim that every annotation selected feedback"]]);
  }
  if (sub === "chunks") for (const chunk of data.linguistic?.noun_phrases || []) causalFacts(parent, [["Recorded noun chunk", chunk.text, `[${chunk.start}, ${chunk.end}) — ${causalSpan(text, chunk)}`], ["Input annotations within chunk", data.tokens.filter(t => chunk.start <= t.start && t.end <= chunk.end)], ["Extraction requirement", "Keep alphabetic tokens and require any NOUN/PROPN; use first/last retained token positions", "SOURCE-VERIFIED LOGIC — TopicService._extract_concepts"]]);
  if (sub === "pipeline") transparencyText(parent, "SOURCE-VERIFIED LOGIC — the enabled pipeline list describes configuration, not component-level timings. tok2vec vectors, attribute_ruler internals and NER entities have no direct active Rule Base consumer. Missing component decision traces cannot explain why a model predicted this label.");
  transparencyDisclosure(parent, "Actual accepted stage clause records", target => renderTransparencyRecord(target, data.stage === "INTRODUCTION" ? data.analysis.observable_structure : data.stage === "BODY" ? data.analysis.paragraphs?.map(p => ({ paragraph_index: p.paragraph_index, clauses: p.clause_structure_candidates })) : data.analysis.clause_candidates));
}

function renderCausalConcepts(parent, data) {
  for (const concept of data.concepts || []) for (const occurrence of concept.occurrences || []) {
    const annotations = data.tokens.filter(token => occurrence.source_token_indices?.includes(token.index));
    const destinations = data.stage === "BODY" ? (data.analysis.paragraphs || []).filter(p => p.paragraph_focus_candidates?.some(c => c.normalized_form === concept.normalized_form)).map(p => `Paragraph ${p.paragraph_index} paragraph_focus_candidates`) : [];
    causalFacts(parent, [["Original → grouped concept", `${occurrence.text} → ${concept.normalized_form}`, `[${occurrence.start}, ${occurrence.end}) — ${causalSpan(transparencyTextSources(data).text, occurrence)}`], ["Extraction method / criterion", occurrence.extraction_method === "noun_phrase" ? "noun_phrase: alphabetic chunk tokens, at least one NOUN/PROPN" : "noun_or_proper_noun: alphabetic token with POS NOUN/PROPN", "TopicService._extract_concepts"], ["Actual annotations", annotations.map(t => ({ index: t.index, text: t.text, lemma: t.lemma, pos: t.pos, is_alpha: t.is_alpha }))], ["Normalization / grouping", `Retained normalized form ${concept.normalized_form}; occurrence_count=${concept.occurrence_count}; occurrence list length=${concept.occurrences.length}`, "SOURCE-VERIFIED LOGIC — casefold lemma-or-text and join; equal forms grouped and identical spans deduplicated"], ["Actual containing paragraph records", destinations.join("; ") || "No paragraph-local link identified in this retained response"], ["Why limited", "Noun/phrase eligibility does not establish an important idea. Extraction rejection history is NOT RECORDED."]]);
  }
  if (!Array.isArray(data.concepts)) transparencyText(parent, "NOT RECORDED — concept output omitted; it is not reconstructed from noun chunks.");
}

function renderCausalTopic(parent, result, data, sub) {
  const lex = data.analysis.lexical_topic_evidence || {}, specs = data.trace?.teacher_context?.focus_terms;
  if (["wordnet", "cross-stage"].includes(sub)) {
    transparencyText(parent, "SOURCE-VERIFIED LOGIC — TopicService._wordnet_suggestions handles eligible unmatched single-word targets; stage_evidence._wordnet_candidates handles cross-stage single-word concept pairs. Retained lookup_pairs name synsets, selection_condition and candidate_emitted. Pre-lookup rejected eligibility candidates are NOT RECORDED. Inspect the per-path tables below, including unsuccessful pairs.");
    const paths = [["Direct", data.stageTrace?.topic_service?.steps?.find(s => s.id === "wordnet_direct_suggestions")], ...Object.entries(data.analysis).filter(([key]) => key.endsWith("_continuity")).map(([key, value]) => [key, value.wordnet_relationship_candidates])];
    for (const [name, record] of paths) {
      transparencyText(parent, `${name}: execution/status ${record?.execution_status || record?.status || "NOT RECORDED"}; ${record?.lookup_pairs?.length ?? "NOT RECORDED"} retained lookup pairs.`);
      for (const pair of record?.lookup_pairs || []) transparencyText(parent, `${pair.teacher_lemma || pair.source_lemma} ↔ ${pair.student_lemma || pair.target_lemma}: shared synsets ${causalValue(pair.shared_synset_ids)}; required exactly one shared synset after eligibility filters; recorded candidate_emitted=${pair.candidate_emitted}. ${pair.candidate_emitted ? "A candidate was emitted, not a verified paraphrase." : "The implementation emitted no candidate; this does not prove unrelated meanings."}`);
    }
    return;
  }
  if (sub === "related") {
    transparencyText(parent, "SOURCE-VERIFIED LOGIC — RelatedTopicConceptService.match uses its curated resource and existing token/lemma annotations. Its match records include configured terms and observed spans. This separate informational result is not consumed by stage rules or FeedbackService and cannot turn an unmatched focus term into confirmed coverage.");
    renderTransparencyRecord(parent, result.related_topic_concept_evidence); return;
  }
  transparencyText(parent, `OBSERVED — focus_source=${lex.focus_source || "NOT RECORDED"}. SOURCE-VERIFIED LOGIC — prepare_teacher_context uses a nonempty supplied focus list, otherwise derives noun candidates from the assignment topic. _unique_focus_terms removes nonalphabetic tokens, normalizes via casefolded lemma-or-text, and keeps the first equal normalized target. Requested originals: ${causalValue(data.trace?.teacher_context?.requested_focus_terms)}.`);
  for (const term of lex.focus_terms || []) {
    const spec = specs?.find(item => item.term === term), matches = lex.matches?.filter(item => item.focus_term === term);
    causalFacts(parent, [["Configured target", term], ["Prepared surface / normalized words", spec ? { surface: spec.surface_words, lemmas: spec.normalized_words, normalized_form: spec.normalized_form } : undefined], ["Why coverage occurred", matches ? `${matches.length} accepted occurrence(s); unique coverage counts this term once if any accepted direct/normalized occurrence exists.` : "NOT RECORDED — matches omitted"], ["If no match", "The implementation retained no matching window, not an off-topic verdict. Rejected-window outcomes are NOT RECORDED."]]);
    for (const match of matches || []) {
      if (sub === "direct" && match.match_method !== "direct" || sub === "lemma" && match.match_method !== "normalized") continue;
      const tokens = data.tokens.filter(t => match.source_token_indices?.includes(t.index));
      causalFacts(parent, [["Student occurrence", match.observed_text, `[${match.start}, ${match.end}) — ${causalSpan(transparencyTextSources(data).text, match)}`], ["Actual token forms and lemmas", tokens.map(t => ({ text: t.text, lemma: t.lemma, is_alpha: t.is_alpha, index: t.index }))], ["Why this method", match.match_method === "direct" ? "SOURCE-VERIFIED LOGIC — accepted alphabetic window's casefolded surfaces equal the prepared surface_words; direct takes precedence." : "SOURCE-VERIFIED LOGIC — direct equality failed and casefolded lemma-or-text sequence equaled normalized_words; it is not counted again as direct."], ["Boundary condition", "Only whitespace, configured apostrophes/hyphens/dashes between alphabetic tokens; blank-line boundaries block matching", "TopicService._find_matches; full rejected-window log NOT RECORDED"], ["Recorded output", match], ["Downstream scope", "Counts toward direct/lemma lexical coverage; stage findings and feedback read coverage/observations rather than each occurrence independently."]]);
    }
  }
}

function renderConceptJourney(parent, data) {
  const steps = Array.isArray(data.stageTrace?.topic_service?.steps) ? data.stageTrace.topic_service.steps : [];
  const spacyStep = steps.find((step) => step.id === "spacy_document_processing");
  const conceptStep = steps.find((step) => step.id === "concept_extraction");
  const concepts = Array.isArray(data.concepts) ? data.concepts : [];
  const occurrenceCount = concepts.reduce((count, concept) => count + (concept.occurrences?.length || 0), 0);
  const paragraphs = Array.isArray(data.analysis.paragraphs) ? data.analysis.paragraphs : [];
  const paragraphReuse = paragraphs.filter((paragraph) => (paragraph.paragraph_focus_candidates || []).length || (paragraph.prominent_concept_candidates || []).length);
  const synthesis = data.analysis.synthesis_structure_candidates;
  const newMaterial = data.analysis.new_material_observations;
  const downstreamRow = data.stage === "INTRODUCTION"
    ? ["STATIC", "Introduction Rule Base does not consume these concept groups — recorded Introduction rules read clause, context, development and focus observations instead, and no Introduction Rule Event references concepts.", "services/introduction_rules.py: analyze (no concept-group consumer)"]
    : data.stage === "BODY"
      ? ["OBSERVED", `${paragraphReuse.length} of ${paragraphs.length} recorded paragraphs carry paragraph_focus_candidates / prominent_concept_candidates built from these occurrences; Introduction→Body comparison also reads them.`, "analysis.paragraphs[].paragraph_focus_candidates, prominent_concept_candidates; services/stage_evidence.py: compare_stage_concepts"]
      : ["OBSERVED", `synthesis_structure_candidates: ${Array.isArray(synthesis?.candidates) ? `${synthesis.candidates.length} candidate(s)` : synthesis?.candidates ? `${synthesis.candidates.length} candidate(s)` : "NOT RECORDED"}; new_material_observations.unobserved_concept_candidates: ${Array.isArray(newMaterial?.unobserved_concept_candidates) ? `${newMaterial.unobserved_concept_candidates.length} record(s)` : "NOT RECORDED"} — both compare these occurrences with supplied earlier-section concepts.`, "analysis.synthesis_structure_candidates, analysis.new_material_observations"];
  transparencyJourney(parent, [
    ["1. Parsed spaCy Doc (input to extraction)", spacyStep ? "OBSERVED" : "NOT_RECORDED", spacyStep ? `${spacyStep.execution_status} — model ${spacyStep.model_name} ${spacyStep.model_version}; parse_ms ${spacyStep.parse_ms ?? "not recorded"}.` : "spacy_document_processing step not retained in this response.", `research_trace.stages.${data.stage}.topic_service.steps[spacy_document_processing]`],
    ["2. TopicService._extract_concepts executed", conceptStep ? "OBSERVED" : "NOT_RECORDED", conceptStep ? `${conceptStep.execution_status} — candidate_count ${conceptStep.candidate_count}, duration_ms ${conceptStep.duration_ms}. ${conceptStep.implementation}` : "concept_extraction step not retained in this response.", `research_trace.stages.${data.stage}.topic_service.steps[concept_extraction]`],
    ["3. Extracted concept groups (recorded output)", concepts.length ? "OBSERVED" : (conceptStep ? "SKIPPED" : "NOT_RECORDED"), concepts.length ? `${concepts.length} group(s), ${occurrenceCount} source occurrence(s) in total.` : "Recorded empty output — no concept groups were extracted.", `research_trace.stages.${data.stage}.topic_service.steps[concept_extraction].output`],
    ["4. Recorded downstream consumption for this stage", downstreamRow[0], downstreamRow[1], downstreamRow[2]],
    ["5. Cross-stage reuse of the same occurrences", data.stage === "INTRODUCTION" ? "SKIPPED" : "STATIC", data.stage === "INTRODUCTION" ? "Not applicable — Introduction has no earlier section to compare with." : "compare_stage_concepts reads each supplied earlier section's concept occurrences; those earlier-stage concept lists are not in this response (selected-stage trace only), so only the recorded pair evidence can be shown.", "services/stage_evidence.py: compare_stage_concepts; app.py: analyze_payload stage-trace selection"],
  ]);
}

function renderDependencyTreeFigure(model) {
  const colW = 122;
  const rowH = 96;
  const padX = 32;
  const padTop = 34;
  const width = padX * 2 + Math.max(1, model.leafCount) * colW;
  const height = padTop * 2 + (model.maxDepth + 1) * rowH;
  const figure = document.createElement("div");
  figure.className = "dependency-tree-figure";
  figure.style.position = "relative";
  figure.style.width = `${width}px`;
  figure.style.height = `${height}px`;
  figure.setAttribute("data-dependency-tree-figure", "true");
  const pos = (node) => ({ x: padX + node.col * colW + colW / 2, y: padTop + node.depth * rowH + rowH / 2 });
  const hasSvg = typeof document.createElementNS === "function";
  const svgNS = "http://www.w3.org/2000/svg";
  let svg = null;
  if (hasSvg) {
    svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("class", "dependency-tree-lines");
    svg.setAttribute("width", String(width));
    svg.setAttribute("height", String(height));
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("aria-hidden", "true");
    figure.appendChild(svg);
  }
  for (const edge of model.edges) {
    const from = model.nodeMap.get(edge.fromKey);
    const to = model.nodeMap.get(edge.toKey);
    if (!from || !to) continue;
    const p1 = pos(from);
    const p2 = pos(to);
    const y1 = p1.y + 20;
    const y2 = p2.y - 20;
    if (svg) {
      const line = document.createElementNS(svgNS, "line");
      line.setAttribute("x1", String(Math.round(p1.x)));
      line.setAttribute("y1", String(Math.round(y1)));
      line.setAttribute("x2", String(Math.round(p2.x)));
      line.setAttribute("y2", String(Math.round(y2)));
      line.setAttribute("class", "dependency-tree-edge");
      line.setAttribute("data-from", edge.fromKey);
      line.setAttribute("data-to", edge.toKey);
      line.setAttribute("data-label", edge.label);
      svg.appendChild(line);
      const label = document.createElementNS(svgNS, "text");
      label.setAttribute("x", String(Math.round((p1.x + p2.x) / 2)));
      label.setAttribute("y", String(Math.round((y1 + y2) / 2) - 5));
      label.setAttribute("class", "dependency-tree-edge-label");
      label.setAttribute("text-anchor", "middle");
      label.textContent = edge.label;
      svg.appendChild(label);
    } else {
      const line = document.createElement("div");
      line.className = "dependency-tree-edge";
      line.setAttribute("data-from", edge.fromKey);
      line.setAttribute("data-to", edge.toKey);
      line.setAttribute("data-label", edge.label);
      figure.appendChild(line);
    }
  }
  for (const node of model.nodes) {
    const p = pos(node);
    const button = document.createElement("button");
    button.type = "button";
    const classes = ["dependency-tree-node"];
    if (node.isRoot) classes.push("dependency-tree-node-root");
    if (!node.resolved) classes.push("dependency-tree-node-unresolved");
    button.className = classes.join(" ");
    button.style.position = "absolute";
    button.style.left = `${Math.round(p.x)}px`;
    button.style.top = `${Math.round(p.y)}px`;
    button.setAttribute("data-tree-node", node.key);
    button.setAttribute("data-dependency", node.dependency ?? "");
    button.setAttribute("data-pos", node.pos ?? "");
    button.setAttribute("data-resolved", String(Boolean(node.resolved)));
    button.setAttribute("aria-label", `${node.text}, ${node.dependency ?? "dependency not recorded"}${node.isRoot ? ", root" : ""}${node.resolved ? "" : ", unresolved"}`);
    const word = document.createElement("span");
    word.className = "dependency-tree-node-text";
    word.textContent = node.text;
    button.appendChild(word);
    const badge = document.createElement("span");
    badge.className = "dependency-tree-node-badge";
    badge.textContent = node.isRoot ? "ROOT" : (node.dependency ?? "?");
    button.appendChild(badge);
    button._treeNode = node;
    figure.appendChild(button);
  }
  return figure;
}

function renderDependencyTreeDetails(host, model, node) {
  host.replaceChildren();
  if (!node) {
    host.textContent = "Select a word node above to see its recorded annotation and verified source span.";
    return;
  }
  const title = document.createElement("strong");
  title.className = "dependency-tree-details-title";
  title.textContent = node.text;
  host.appendChild(title);
  const rows = [
    ["POS", node.pos ?? "NOT RECORDED", node.posExplanation],
    ["Dependency", node.dependency ?? "NOT RECORDED", node.explanation],
    ["Connected head", node.isRoot ? `${node.headText ?? node.text} (this token is its own head — ROOT)` : (node.headText ?? "NOT RECORDED"), node.headStart === null ? "Head position not recorded." : `Recorded head start: ${node.headStart}`],
    ["Token span", node.end === null ? `[${node.start}, end not recorded)` : `[${node.start}, ${node.end})`, null],
  ];
  if (model.fullText !== null && node.end !== null) {
    const verified = Array.from(model.fullText).slice(node.start, node.end).join("");
    rows.push(["Verified source span", verified === node.text ? `Exact match: "${verified}"` : `Recorded token text "${node.text}"; source slice at these offsets is "${verified}".`, "Character offsets are zero-based, end-exclusive Python indices recorded by spaCy; the slice is taken by Unicode code point."]);
  }
  for (const [label, value, note] of rows) {
    const line = document.createElement("div");
    line.className = "dependency-tree-details-row";
    const key = document.createElement("span");
    key.className = "dependency-tree-details-key";
    key.textContent = `${label}:`;
    const val = document.createElement("span");
    val.className = "dependency-tree-details-value";
    val.textContent = value;
    line.appendChild(key);
    line.appendChild(val);
    if (note) {
      const help = document.createElement("span");
      help.className = "field-help";
      help.textContent = note;
      line.appendChild(help);
    }
    host.appendChild(line);
  }
  if (!node.resolved && node.unresolvedReason) {
    const warning = document.createElement("p");
    warning.className = "dependency-tree-details-warning";
    warning.textContent = `Unresolved record: ${node.unresolvedReason}`;
    host.appendChild(warning);
  }
}

function renderDependencyTree(parent, data, fullText) {
  const sentences = Array.isArray(data?.sentences) ? data.sentences : [];
  const usable = sentences.filter((sentence) => Array.isArray(sentence?.dependencies) && sentence.dependencies.length > 0);
  if (!usable.length) {
    transparencyText(parent, "No recorded dependency relationships were returned for this stage's sentences; the visual tree is not shown.");
    return;
  }
  const section = transparencySection(parent, "Visual Dependency Tree — How the Words Connect");
  section.setAttribute("data-dependency-tree-section", "true");
  transparencyText(section, "Each tree is built only from the recorded spaCy dependency edges of one sentence — no new analysis runs when you switch sentences or select a word. Node identity uses the recorded character start, so repeated words remain distinct.", "transparency-lead");
  const selector = document.createElement("div");
  selector.className = "dependency-tree-selector";
  selector.setAttribute("role", "group");
  selector.setAttribute("aria-label", "Select a sentence to visualize");
  const context = transparencyText(section, "", "dependency-tree-sentence-context");
  const figureHost = document.createElement("div");
  figureHost.className = "dependency-tree-host";
  const detailsHost = document.createElement("div");
  detailsHost.className = "dependency-tree-details";
  detailsHost.setAttribute("aria-live", "polite");
  section.appendChild(selector);
  section.appendChild(context);
  section.appendChild(figureHost);
  section.appendChild(detailsHost);
  const sentenceButtons = [];
  const sentenceModels = sentences.map((sentence) => buildDependencyTreeModel(sentence, fullText));
  for (let i = 0; i < sentences.length; i += 1) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "dependency-tree-sentence-button";
    button.textContent = `Sentence ${i + 1}`;
    button.setAttribute("data-sentence-index", String(i));
    button.addEventListener("click", () => showSentence(i));
    sentenceButtons.push(button);
    selector.appendChild(button);
  }
  let selectedIndex = -1;
  const showSentence = (index) => {
    if (index < 0 || index >= sentences.length) return;
    selectedIndex = index;
    const model = sentenceModels[index];
    sentenceButtons.forEach((button, buttonIndex) => {
      const active = buttonIndex === index;
      button.className = active ? "dependency-tree-sentence-button dependency-tree-sentence-active" : "dependency-tree-sentence-button";
      button.setAttribute("aria-pressed", String(active));
    });
    context.textContent = `Sentence ${index + 1} of ${sentences.length}: “${model.sentenceText}”`;
    figureHost.replaceChildren();
    const figure = renderDependencyTreeFigure(model);
    figureHost.appendChild(figure);
    for (const button of figure.querySelectorAll("button")) {
      button.addEventListener("click", () => renderDependencyTreeDetails(detailsHost, model, button._treeNode || null));
    }
    renderDependencyTreeDetails(detailsHost, model, null);
    if (model.issues.length) {
      const issueNote = transparencyText(figureHost, "", "dependency-tree-issues");
      issueNote.textContent = `Recorded-data notes for this sentence: ${model.issues.join(" ")}`;
    }
  };
  showSentence(0);
  transparencyText(section, "This diagram shows how spaCy connected the words in this sentence. The main grammatical head appears at the top. The connected words show subjects, objects, modifiers and other grammatical relationships.", "field-help");
  const distinction = document.createElement("div");
  distinction.className = "dependency-tree-distinction";
  transparencyText(distinction, "Dependency result: the linguistic relationships predicted by spaCy for each recorded token.", "field-help");
  transparencyText(distinction, "Rule Base result: which of those relationships satisfy EssayScaff's configured clause-detection conditions. Not every dependency edge becomes an accepted clause candidate or a writing problem — the Stage Rule Bases perform those separate evaluations.", "field-help");
  section.appendChild(distinction);
}

function renderRelatedTopicConceptSummary(parent, result) {
  const lexical = result.analysis?.lexical_topic_evidence;
  const related = result.related_topic_concept_evidence;
  transparencyTable(parent, ["Separate evidence channel", "Current recorded result"], [
    ["Direct/lemma focus terms observed", Array.isArray(lexical?.observed_focus_terms) ? lexical.observed_focus_terms.join(", ") || "None observed" : "Not returned"],
    ["Teacher focus terms with related-concept evidence (not exact coverage)", Array.isArray(related?.summary?.teacher_focus_terms_with_related_evidence) ? related.summary.teacher_focus_terms_with_related_evidence.join(", ") || "No recorded evidence" : "Not returned"],
    ["Unique related concepts observed", related?.summary?.unique_related_concepts_observed ?? "Not returned"],
    ["Related-concept occurrences (distinct source spans)", related?.summary?.total_related_concept_occurrences ?? "Not returned"],
    ["Related-concept execution status", related?.execution_status || "NOT_RECORDED"],
  ]);
}

function renderRelatedTopicConcepts(parent, result) {
  const related = result.related_topic_concept_evidence;
  if (!related) {
    transparencyText(parent, "NOT_RECORDED — this cached response does not supply related-concept evidence. No relationship or zero count is inferred.");
    return;
  }
  transparencyTable(parent, ["Execution / provenance", "Recorded value"], [
    ["Execution status", related.execution_status], ["Recorded reason", related.reason],
    ["Resource status", related.resource?.status], ["Relationship source", related.resource?.source],
    ["Configuration version", related.resource?.configuration_version], ["Provenance", related.resource?.provenance],
    ["Current decision use", related.informational_only === true && related.affects_rules_or_feedback === false ? "Inspection only — does not change direct/lemma counts, rules, feedback or stage eligibility" : "Use not established by this response"],
  ]);
  renderRelatedTopicConceptSummary(parent, result);
  const evidence = document.createElement("div");
  evidence.className = "related-topic-evidence";
  parent.appendChild(evidence);
  transparencyTable(evidence, ["Student Word", "Base Form", "Teacher Focus", "Relationship", "Source", "Position"], (related.evidence || []).map((item) => [
    item.student_word, item.normalized_student_word, item.teacher_focus_term === item.normalized_focus_concept ? item.teacher_focus_term : `${item.teacher_focus_term} (${item.normalized_focus_concept})`,
    `${item.relationship_label} (${item.relationship_type})`,
    `${item.relationship_source} · ${item.relationship_id} · v${item.configuration_version}`,
    `[${item.start}, ${item.end}) · sentence index ${item.sentence_index ?? "not returned"}`,
  ]), related.execution_status === "EXECUTED" ? "Executed — no approved related vocabulary was observed." : "No relationship records; inspect the execution/resource status above. This is not a successful no-match result.");
  transparencyText(parent, "Positions are zero-based, end-exclusive Python character offsets into this stage's analyzed text. Sentence indices are zero-based. Direct/lemma focus coverage and WordNet statuses remain in their separate views.");
  transparencyDisclosure(parent, "Approved relationships activated by this teacher context", (target) => {
    transparencyTable(target, ["Complete focus concept", "Approved student lemma", "Approved surface forms", "Relationship", "Relationship ID"], (related.approved_relationships || []).map((item) => [item.focus_concept, item.related_concept, (item.surface_forms || [item.related_concept]).join(", "), item.relationship_label, item.id]), "No approved relationships activated.");
    renderTransparencyRecord(target, { active_focus_concepts: related.active_focus_concepts, resource: related.resource });
  });
  transparencyDisclosure(parent, "Complete related-concept records and normalization provenance", (target) => renderTransparencyRecord(target, related));
  transparencyText(parent, related.limitation || "Limitations not returned.", "field-help");
  if (related.future_integration) transparencyText(parent, related.future_integration, "field-help");
}

function renderTransparencyStageFindings(parent, data) {
  const groups = data.stage === "INTRODUCTION" ? [
    ["text_presence", "Text eligibility and counts", "Alphabetic presence and clause availability summarize the parsed input."],
    ["observable_structure", "Root clauses, context, fragments and subordinator checks", "Finite VERB/AUX predicates need permitted dependencies and linked subjects. Root clauses are central-direction candidates; focus matches in the same sentence give context candidates. Fragment/list checks require no qualifying clause; list thresholds are three nonclausal sentence spans or four NOUN/PROPN tokens. SCONJ checks inspect attachment, root-only subordinate clauses and complement availability; they are heuristics."],
    ["development_evidence", "Supported clause-predicate count", "Clauses in sentences flagged for incomplete subordinators are excluded. At least two remaining clauses produce a structural-elaboration candidate."],
  ] : data.stage === "BODY" ? [
    ["paragraphs", "All Body paragraph observations", "Blank-line segmentation → span-filtered sentences/tokens/concepts. Clause plus focus match or concept recurrence across at least two sentences → topic-sentence candidate. At least two subject-linked clauses → detail candidates. Adjacent content-word intersections, repeated surfaces/lemmas/two-word openings and listed example expressions remain separate observations."],
    ["cross_paragraph_continuity", "Adjacent-paragraph links and transitions", "Adjacent substantive paragraphs compare content surfaces/lemmas; a shared lemma or listed transition in the right paragraph yields a lexical/transition candidate."],
  ] : [
    ["conclusion_paragraphs", "Conclusion paragraphs and source spans", "Blank-line groups reuse the existing sentence/token observations; no paragraph-level NLP rerun."],
    ["clause_candidates", "Conclusion subject-linked clauses", "Finite VERB/AUX with permitted dependency and subject attached by exact head position."],
    ["keyword_list_candidate", "Conclusion list candidate", "No qualifying clause plus at least three sentences or four NOUN/PROPN tokens."],
    ["synthesis_structure_candidates", "Synthesis-structure candidates", "A sentence with a clause candidate must contain at least two normalized concepts previously observed in supplied earlier sections. This is lexical structure, not validated synthesis."],
    ["closure_candidates", "Final clauses, closing expressions and recommendation cues", "A final ROOT clause or a listed closing expression supplies a closure candidate. Modal/recommendation-associated words in the final sentence are recorded separately."],
    ["new_material_observations", "Unobserved concepts, known combinations and rewordings", "Compare conclusion concept forms/content lemmas with supplied earlier concepts; exclude closing-expression spans and component occurrences nested in larger phrases. Separate unseen content lemmas from new combinations of known words; preserve lemma rewordings and WordNet candidates."],
    ["repetition_observations", "Repeated wording", "Content POS surfaces and lemmas occurring more than once, plus repeated first two alphabetic sentence words, are reported with spans."],
  ];
  for (const [key, title, how] of groups) {
    transparencyDisclosure(parent, `${title} · recorded observations`, (target) => {
      const helper = ({ text_presence: "_text_presence / analyze", observable_structure: "_clause_candidates, _list_or_fragment_finding, _incomplete_subordinator_evidence, _context_candidates", development_evidence: "_development_finding", paragraphs: "_analyze_paragraph", cross_paragraph_continuity: "_cross_paragraph_continuity", conclusion_paragraphs: "_paragraphs", clause_candidates: "clause_candidates_from_sentences (shared stage_evidence.py helper)", keyword_list_candidate: "_keyword_list_finding", synthesis_structure_candidates: "_synthesis_candidates", closure_candidates: "_closing_candidates", new_material_observations: "_new_material_observations", repetition_observations: "repetition_observations (shared stage_evidence.py helper)" })[key];
      transparencyExplanation(target, { what: title, how, why: "Provide a specific, inspectable structural or lexical revision signal.", where: "The current stage's _rule_events and FeedbackService inspect these returned findings; the complete record preserves input spans, conditions and limitations where supplied.", source: `services/${data.stage.toLowerCase()}_rules.py: ${helper}; analysis.${key}` });
      if (data.stage === "BODY" && key === "paragraphs" && Array.isArray(data.analysis.paragraphs)) renderTransparencyBodyParagraphs(target, data.analysis.paragraphs);
      else renderTransparencyRecord(target, data.analysis[key]);
    });
  }
  transparencyDisclosure(parent, "Missing observable elements and stage limitations", (target) => renderTransparencyRecord(target, { missing_observable_elements: data.analysis.missing_observable_elements, uncertainty: data.analysis.uncertainty, prohibited_conclusions: data.analysis.prohibited_conclusions }));
}

function renderTransparencyBodyParagraphs(parent, paragraphs) {
  const operations = [
    ["clause_structure_candidates", "Subject-linked clause candidates", "Filter VERB/AUX tokens by VB/VBD/VBP/VBZ and ROOT/conj/advcl/ccomp/xcomp/relcl, then require an nsubj/nsubjpass/csubj/csubjpass edge whose head_start equals the predicate start.", "Find inspectable sentence structure for topic/detail checks.", "_topic_sentence_candidates and _supporting_detail_candidates", "_paragraph_clause_candidates"],
    ["fragment_or_list_candidate", "Fragment or keyword-list flags", "A token-bearing paragraph with no qualifying clause is fragmentary. The list flag additionally requires at least three sentence segments or four NOUN/PROPN tokens.", "Offer a review signal when noun-heavy wording lacks the expected clause pattern.", "_rule_events; FeedbackService.generate_body list branches", "_analyze_paragraph"],
    ["paragraph_focus_candidates", "Paragraph lexical concepts", "Filter the already extracted full-section concept occurrences to those wholly inside this paragraph; retain lemmas, methods and source positions.", "Provide paragraph-local lexical evidence without another parse.", "Concept recurrence; prominent_concept_candidates; _topic_sentence_candidates", "_concepts_in_span"],
    ["prominent_concept_candidates", "Prominent concept candidates", "Keep paragraph concepts occurring more than once or whose normalized form equals a focus match's normalized form. There is no ranking or confidence score.", "Expose recurrence/focus-related concept candidates.", "Returned paragraph observation; no direct FeedbackService read of this list", "_analyze_paragraph"],
    ["focus_term_evidence", "Paragraph focus matches", "Filter full-section direct/normalized matches to spans wholly inside this paragraph; preserve each recorded match method.", "Tie assignment-word overlap to a specific paragraph.", "observed_focus_terms, sentence focus grouping, topic-sentence candidates, events and feedback", "_analyze_paragraph"],
    ["topic_sentence_candidates", "Topic-sentence candidates", "For a sentence containing a clause candidate, require a focus match in that sentence or a normalized concept present across at least two different paragraph sentences. Collect qualifying sentences with their reasons and predicate evidence.", "Offer a lexical/structural signal to review a paragraph's focus.", "Topic-sentence events and FeedbackService.generate_body working observations", "_topic_sentence_candidates"],
    ["supporting_detail_candidates", "Additional-clause/detail candidates", "When the paragraph has at least two qualifying subject-linked clauses, return all of them as structural detail candidates. An example marker alone never satisfies this check.", "Expose possible development without claiming valid support.", "Supporting-detail events; primary/next-step and working/attention feedback checks", "_supporting_detail_candidates"],
    ["paragraph_unity_evidence", "Adjacent-sentence lexical comparison", "Take alphabetic NOUN/PROPN/VERB/ADJ/ADV tokens for each neighboring sentence pair; intersect casefolded surfaces and lemmas, retaining both sets of positions. A shared lemma yields a lexical-continuity candidate, not a semantic unity score.", "Show exactly which wording links adjacent sentences.", "Per-pair UNITY Rule Events; returned observations (no overall score)", "_sentence_unity"],
    ["repetition_observations", "Repeated words, lemmas and openings", "Group alphabetic content-token surfaces/lemmas with counts greater than one; separately group casefolded first two alphabetic words of each sentence. Retain every occurrence span.", "Make repeated wording visible while recognizing it can help continuity.", "Repetition Rule Events; first repeated opening primary branch and repeated surface working observation", "_repetition_observations → stage_evidence.repetition_observations"],
    ["example_or_explanation_markers", "Example/explanation expression spans", "Case-insensitive word-boundary scans for 'for example', 'for instance', 'such as', and 'including' return actual expression spans.", "Record explicit discourse cues separately from structural detail.", "EXAMPLE_OR_EXPLANATION_MARKER Rule Events; the marker alone does not select a detail message", "_example_marker_evidence"],
  ];
  for (const paragraph of paragraphs) {
    const section = transparencySection(parent, `Paragraph ${paragraph.paragraph_index} · [${paragraph.start}, ${paragraph.end})`);
    transparencyTable(section, ["Paragraph input", "Actual value"], [["Text", paragraph.text], ["Substantive (alphabetic token observed)", paragraph.substantive], ...Object.entries(paragraph.counts || {}).map(([key, value]) => [transparencyLabel(key), value])]);
    for (const [key, title, how, why, where, source] of operations) transparencyDisclosure(section, title, (target) => {
      transparencyExplanation(target, { what: title, how, why, where, source: `services/body_rules.py: ${source}; paragraphs[${paragraph.paragraph_index - 1}].${key}` });
      renderTransparencyRecord(target, paragraph[key]);
    });
    transparencyDisclosure(section, "All remaining paragraph fields, including sentence spans and missing elements", (target) => renderTransparencyRecord(target, Object.fromEntries(Object.entries(paragraph).filter(([key]) => !["text", "start", "end", "paragraph_index", "substantive", "counts", ...operations.map(([key]) => key)].includes(key)))));
  }
}

function transparencyRuleInputs(row, data) {
  const id = row.rule_id || "";
  if (id === "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW") return { source: "analysis.sentence_topic_evidence", value: data.analysis.sentence_topic_evidence };
  const paragraphIndex = /^BODY\.P(\d+)\./.exec(id)?.[1];
  if (paragraphIndex) {
    const paragraph = data.analysis.paragraphs?.find((item) => item.paragraph_index === Number(paragraphIndex));
    const key = id.includes("KEYWORD_LIST") ? "fragment_or_list_candidate" : id.includes("FOCUS_TERMS") ? "focus_term_evidence" : id.includes("TOPIC_SENTENCE") ? "topic_sentence_candidates" : id.includes("SUPPORTING_DETAIL") ? "supporting_detail_candidates" : id.includes("EXAMPLE") ? "example_or_explanation_markers" : id.includes("UNITY") ? "paragraph_unity_evidence" : id.includes("REPETITION") ? "repetition_observations" : null;
    return { source: `analysis.paragraphs (paragraph_index=${paragraphIndex})${key ? `.${key}` : ""}`, value: key ? paragraph?.[key] : paragraph };
  }
  const key = id.includes(".GOAL.") || id.includes(".LIMITATION.") ? "stage"
    : id.startsWith("INTRO.CONTEXT") || id.startsWith("INTRO.CLAUSE") || id.startsWith("INTRO.TEXT.KEYWORD") || id.startsWith("INTRO.TEXT.FRAGMENT") ? "observable_structure"
      : id.startsWith("INTRO.DEVELOPMENT") ? "development_evidence"
        : id.includes(".TOPIC.") ? "lexical_topic_evidence"
          : id.startsWith("BODY.INTRO_CONTINUITY") ? "introduction_to_body_continuity"
            : id.startsWith("BODY.CONTINUITY") ? "cross_paragraph_continuity"
              : id.startsWith("CONCLUSION.CONTINUITY.INTRODUCTION") ? "introduction_to_conclusion_continuity"
                : id.startsWith("CONCLUSION.CONTINUITY.BODY") ? "body_to_conclusion_continuity"
                  : id.startsWith("CONCLUSION.SYNTHESIS") ? "synthesis_structure_candidates"
                    : id.startsWith("CONCLUSION.CLOSURE") ? "closure_candidates"
                      : id.startsWith("CONCLUSION.NEW_MATERIAL") ? "new_material_observations"
                        : id.startsWith("CONCLUSION.REPETITION") ? "repetition_observations"
                          : id.startsWith("CONCLUSION.STRUCTURE") ? "clause_candidates"
                            : id === "BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH" ? "substantive_paragraph_count" : "text_presence";
  if (key === "observable_structure") {
    const field = id.startsWith("INTRO.CONTEXT") ? "introductory_context_candidates"
      : id === "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR" ? "incomplete_subordinator_candidates"
        : id.startsWith("INTRO.CLAUSE") ? "central_direction_candidates" : "list_or_fragment_candidate";
    return { source: `analysis.${key}.${field}`, value: data.analysis[key]?.[field] };
  }
  return { source: `analysis.${key}`, value: data.analysis[key] };
}

function renderTransparencyRules(parent, result, data, view = "trace") {
  const events = data.analysis.rule_evidence;
  const rows = data.analysis.rule_evaluation_trace;
  if (view === "overview") {
    transparencyTable(parent, ["Distinct structure", "Actual count"], [["Emitted Rule Events (analysis.rule_evidence)", events?.length], ["Evaluation records (analysis.rule_evaluation_trace)", rows?.length], ...["TRIGGERED", "EVALUATED_NOT_TRIGGERED", "NOT_APPLICABLE", "NOT_RECORDED", "FAILED"].map((status) => [status, Array.isArray(rows) ? rows.filter((row) => row.status === status).length : "Not returned"])]);
    transparencyText(parent, "Rule Events are emitted by stage rules. The evaluation trace is reconstructed later from the inventory, emitted events and returned fields. Its rows are not separate events. Non-triggered reasons are limited to recorded decision bases.");
    return;
  }
  if (view === "not-triggered" || view === "evidence") {
    transparencyRenderSubtabEvidence(parent, "rules", view, result, data);
    return;
  }
  if (view === "sources") {
    transparencyTable(parent, ["Rule ID", "File", "Function", "Purpose", "Reference IDs"], (rows || []).map((row) => [row.rule_id, row.implementation?.file, row.implementation?.function, row.purpose || row.name, (row.reference_ids || []).join(", ") || "No reference mapping recorded"]), "Rule source metadata was not returned.");
    transparencyReferenceList(parent, STUDENT_TRANSPARENCY_PROCESS_INFO["rules:code"].references);
    transparencyText(parent, "Source references identify implementation and general writing context; they do not validate the local heuristic. Exact recorded metadata remains in Evaluation Trace details and Complete Evidence.");
    return;
  }
  const affected = (id) => (result.feedback?.["Feedback Provenance"] || []).filter((item) => item.rule_id === id).map((item) => item.feedback_field);
  const evidenceSummary = (row) => {
    const event = events?.find((item) => item.rule_id === row.rule_id);
    const evidence = event?.actual_evidence ?? event?.evidence;
    const observed = transparencyRuleInputs(row, data);
    const value = observed.value;
    const summary = Array.isArray(value) ? `${value.length} returned records`
      : value && typeof value === "object" ? `${Object.keys(value).length} returned observation fields`
        : value === undefined ? "Input observation not returned" : String(value);
    return event ? `${Array.isArray(evidence) ? evidence.length : "Recorded"} event evidence item(s). Full record: Triggered sub-tab.`
      : `No emitted event; related input: ${summary}. Exact values: per-rule detail.`;
  };
  if (view === "trace") {
    transparencyTable(parent, ["Rule ID", "What it checks", "Actual evidence", "Condition", "Decision", "Explanation / feedback relationship"], (rows || []).map((row) => [row.rule_id, row.name, evidenceSummary(row), row.condition, row.status, `${row.decision_basis || "Reason not recorded."} Feedback links: ${affected(row.rule_id).join(", ") || "No field link recorded"}`]), "Rule Evaluation Trace was not included in this response.");
    transparencyDisclosure(parent, "Per-rule WHAT / HOW / WHY / WHERE, configuration and source references", (target) => {
      for (const row of rows || []) transparencyDisclosure(target, `${row.rule_id} · ${row.status}`, (detail) => {
        transparencyExplanation(detail, { what: row.name || row.purpose, how: row.condition || "Condition not recorded.", why: row.educational_rationale || "Purpose not recorded.", where: affected(row.rule_id).length ? `Recorded links to: ${affected(row.rule_id).join(", ")}.` : "No feedback-field relationship is recorded for this rule.", source: `${row.implementation?.file || "Source not returned"}: ${row.implementation?.function || ""}` });
        transparencyText(detail, "This is existing registry metadata reconstructed from returned observations. Its configuration/condition text is a summary, not a source-code listing or an independently captured execution log. See stage findings for verified algorithm details; no extra cause for a non-trigger is inferred.");
        renderTransparencyRecord(detail, row);
        const observed = transparencyRuleInputs(row, data);
        transparencyText(detail, `Related recorded input observations: ${observed.source}. This association displays returned data; it does not rerun or infer a rule decision.`);
        renderTransparencyRecord(detail, observed.value);
      });
    });
    return;
  }
  const eventSection = transparencySection(parent, "Emitted Rule Events — exact evidence and downstream links");
  transparencyTable(eventSection, ["Rule ID", "Condition", "Evidence type", "Status"], (events || []).map((event) => [event.rule_id, event.triggering_condition, event.evidence_type, event.triggered === false || event.fired === false ? "Recorded false" : "TRIGGERED / emitted"]), "No emitted Rule Events were returned.");
  if (!Array.isArray(events)) transparencyText(eventSection, "Rule Events were not returned.");
  for (const event of events || []) transparencyDisclosure(eventSection, `${event.rule_id} · ${event.triggered === false || event.fired === false ? "Recorded false" : "TRIGGERED / emitted"}`, (target) => {
    transparencyText(target, `Description / exact triggering condition: ${event.triggering_condition || "Not recorded"}`);
    transparencyText(target, `Feedback fields linked to this event: ${affected(event.rule_id).join(", ") || "No link recorded"}. Links are field-level; list-item-level causality is not returned.`);
    renderTransparencyRecord(target, event);
  });
}

function renderTransparencyFeedback(parent, result, data, view = "overview") {
  const decisions = data.stageTrace?.feedback_decisions;
  const provenance = result.feedback?.["Feedback Provenance"];
  const fieldNames = { goal: "Current Goal", primary: "Primary Feedback", working: "What's Working", attention: "Needs Attention", next: "Next Step" };
  const fields = view === "overview" ? Object.values(fieldNames) : fieldNames[view] ? [fieldNames[view]] : [];
  if (view === "overview") transparencyText(parent, "The first satisfied Primary Feedback / Next Step priority branch wins; positive and caution lists use separate checks. Select a field to inspect its exact supporting events.");
  if (view === "overview") transparencyTable(parent, ["Field", "Selection branch", "Recorded selection condition (why this branch)", "Linked Rule IDs"], fields.map((field) => {
    const decision = decisions?.fields?.[field];
    return [field, decision?.selection_branch || "Branch not returned", decision?.selection_condition || "No selection condition was recorded for this field.", (decision?.rule_ids || (provenance || []).filter((item) => item.feedback_field === field).map((item) => item.rule_id)).join(", ") || "No rule link recorded"];
  }));
  if (view === "overview") transparencyDisclosure(parent, "Recorded selection rules: priority order, source and unselected alternatives", (target) => {
    if (!decisions) transparencyText(target, "Detailed trace not included in this response — feedback branch selection was not recorded.");
    else renderTransparencyRecord(target, { priority_order: decisions.priority_order, selection_source: decisions.selection_source, unselected_alternatives: decisions.unselected_alternatives });
  });
  else if (fields.length) {
    transparencyTable(parent, ["Field", "Selected backend message", "Selection branch", "Supporting evidence / selection condition", "Rule IDs"], fields.map((field) => {
      const message = result.feedback?.[field];
      const decision = decisions?.fields?.[field];
      const ids = decision?.rule_ids ?? (provenance || []).filter((item) => item.feedback_field === field).map((item) => item.rule_id);
      return [field, Array.isArray(message) ? message.length ? message.join("\n\n") : "Recorded empty list — the feedback panel may show frontend fallback text." : message ?? "Backend value not returned", decision?.selection_branch || "Branch not returned", decision?.selection_condition || "No selection condition returned; inspect linked event evidence.", ids?.join(", ") || "No Rule ID link recorded"];
    }));
    for (const field of fields) transparencyDisclosure(parent, `${field} · recorded provenance and supporting event evidence`, (target) => {
      const items = Array.isArray(provenance) ? provenance.filter((item) => item.feedback_field === field).map((item) => resolveStudentFeedbackProvenance(item, result)) : undefined;
      renderTransparencyRecord(target, { selection: decisions?.fields?.[field], supporting_events: items });
    });
  }
  if (view === "provenance") {
    const resolved = Array.isArray(provenance) ? provenance.map((item) => resolveStudentFeedbackProvenance(item, result)) : [];
    transparencyTable(parent, ["Feedback field", "Rule ID", "Recorded condition", "Evidence type", "Limitations"], resolved.map((item) => [item.feedback_field, item.rule_id, item.triggering_condition, item.evidence_type, item.limitations]), "No feedback provenance records were returned.");
    resolved.forEach((item) => transparencyDisclosure(parent, `${item.feedback_field}: ${item.rule_id} · exact supporting evidence`, (target) => renderTransparencyRecord(target, item)));
    transparencyDisclosure(parent, "Recorded priority order and alternative-branch availability", (target) => renderTransparencyRecord(target, { priority_order: decisions?.priority_order, unselected_alternatives: decisions?.unselected_alternatives, selection_source: decisions?.selection_source }));
  }
  if (view === "overview") renderSixTraitTrace(parent, result);
  if (view === "primary") renderScaffoldingTrace(parent, result);
  transparencyText(parent, "These are original backend fields. Supported branches have a separate prepared student-facing presentation in the Primary Feedback trace. Empty unmapped fields may receive frontend-only fallback text. Neither presentation establishes meaning, truth, argument quality or readiness.");
}

function transparencyRenderSubtabEvidence(parent, mainKey, subKey, result, data) {
  const analysis = data.analysis;
  const lexical = analysis.lexical_topic_evidence || {};
  const matches = Array.isArray(lexical.matches) ? lexical.matches : null;
  const events = Array.isArray(analysis.rule_evidence) ? analysis.rule_evidence : null;

  if (mainKey === "processing") {
    const tokensRecorded = Array.isArray(data.linguistic?.tokens) || data.sentences.some((sentence) => Array.isArray(sentence.tokens));
    if (subKey === "overview") {
      const paragraphCount = analysis.paragraph_count ?? analysis.text_presence?.paragraph_count
        ?? (Array.isArray(analysis.paragraphs) ? analysis.paragraphs.length
          : Array.isArray(analysis.conclusion_paragraphs) ? analysis.conclusion_paragraphs.length
            : data.stage === "INTRODUCTION" ? "Not collected for this stage." : "Metric not included in this response.");
      transparencyTable(parent, ["Observed metric", "Current value"], [
        ["Alphabetic words", data.linguistic?.counts?.alphabetic_word_count ?? analysis.text_presence?.alphabetic_word_count ?? "Metric not included in this response."],
        ["Tokens", data.linguistic?.counts?.token_count ?? analysis.text_presence?.token_count ?? "Metric not included in this response."],
        ["Sentences", data.linguistic?.counts?.sentence_count ?? analysis.text_presence?.sentence_count ?? "Metric not included in this response."],
        ["Paragraphs", paragraphCount],
      ]);
    } else if (subKey === "pipeline") {
      const runtime = data.trace?.runtime;
      const pipeline = runtime?.pipeline;
      if (!pipeline) transparencyText(parent, "Detailed trace not included in this response — runtime component metadata was not retained.");
      else {
        transparencyTable(parent, ["Component", "Execution status", "EssayScaff output use"], [
          ["tokenizer", pipeline.tokenizer?.execution_status, "Creates the Doc; not listed in nlp.pipe_names."],
          ...(pipeline.enabled_components || []).map((component) => [component, "Enabled; executes during nlp(text)", pipeline.active_component_output_use?.[component] || "Component runs; EssayScaff use not separately recorded."]),
          ...(pipeline.disabled_components || []).map((component) => [component, "Disabled", "Not run for this pipeline call."]),
        ]);
        transparencyEvidence(parent, { python: runtime.python_version, spacy: runtime.spacy_version, nltk: runtime.nltk_version, flask: runtime.flask_version, sqlite: runtime.sqlite_runtime_version, model: runtime.model, service_initialization: runtime.analysis_service_initialization, component_timings: pipeline.component_timings });
      }
      const stageTrace = data.stageTrace;
      const timings = stageTrace?.timings_ms || {};
      const steps = Array.isArray(stageTrace?.topic_service?.steps) ? stageTrace.topic_service.steps : [];
      const spacyStep = steps.find((step) => step.id === "spacy_document_processing");
      const timingRows = [
        ["TopicService (whole call)", timings.topic_service_ms, `research_trace.stages.${data.stage}.timings_ms.topic_service_ms`],
        ["Stage Rule Base", timings.rule_base_ms, `research_trace.stages.${data.stage}.timings_ms.rule_base_ms`],
        ["FeedbackService", timings.feedback_ms, `research_trace.stages.${data.stage}.timings_ms.feedback_ms`],
        ["TopicService.total_ms", stageTrace?.topic_service?.total_ms, `research_trace.stages.${data.stage}.topic_service.total_ms`],
        ["spaCy parse (spacy_document_processing.parse_ms)", spacyStep?.parse_ms, `research_trace.stages.${data.stage}.topic_service.steps[spacy_document_processing].parse_ms`],
        ["Observation serialization (observation_serialization_ms)", spacyStep?.observation_serialization_ms, `research_trace.stages.${data.stage}.topic_service.steps[spacy_document_processing].observation_serialization_ms`],
        ...steps.filter((step) => typeof step.duration_ms === "number").map((step) => [`${step.id}.duration_ms`, step.duration_ms, `research_trace.stages.${data.stage}.topic_service.steps[${step.id}].duration_ms`]),
      ].filter(([, value]) => value !== undefined && value !== null);
      transparencyTable(parent, ["Recorded timing field", "Milliseconds", "Evidence type", "Recorded source"], timingRows.map(([label, value, source]) => [label, value, "OBSERVED", source]));
      if (!timingRows.length) transparencyText(parent, "NOT RECORDED — no timing fields were retained for this stage.");
      transparencyText(parent, "NOT RECORDED — the response contains no end-to-end request or Flask handling duration, and spaCy component-level timings are not measured (only the values above were recorded).", "field-help");
    } else if (subKey === "tokenization") {
      transparencyExpandableTable(parent, tokensRecorded ? `Expand all ${data.tokens.length} tokens` : "Token records", ["Token index", "Token", "Start", "End", "Alphabetic"], data.tokens.map((token, index) => [token.index ?? index, token.text, token.start, token.end, token.is_alpha]), tokensRecorded ? "No token records were returned." : "Token observations were not included in this response.");
    } else if (subKey === "lemmatization") {
      transparencyExpandableTable(parent, tokensRecorded ? `Expand ${data.tokens.length} actual token-to-lemma transformations` : "Token-to-lemma records", ["Token index", "Original token", "Lemma", "Original span"], data.tokens.map((token, index) => [token.index ?? index, token.text, token.lemma, `[${token.start}, ${token.end})`]), tokensRecorded ? "No token/lemma records were returned." : "Token/lemma observations were not included in this response.");
    } else if (subKey === "pos") {
      transparencyExpandableTable(parent, tokensRecorded ? `Expand POS and tag labels for ${data.tokens.length} tokens` : "POS and tag records", ["Token", "Coarse POS", "Fine tag", "Span"], data.tokens.map((token) => [token.text, token.pos, token.tag, `[${token.start}, ${token.end})`]), tokensRecorded ? "No POS/tag records were returned." : "POS/tag observations were not included in this response.");
    } else if (subKey === "dependencies") {
      const dependencyRows = data.sentences.flatMap((sentence) => (sentence.dependencies || []).map((item) => [item.text, item.dependency, item.head, item.head_start, `[${item.start}, ${item.end})`]));
      const dependenciesRecorded = Array.isArray(data.linguistic?.sentences) || data.sentences.some((sentence) => Array.isArray(sentence.dependencies));
      transparencyExpandableTable(parent, dependenciesRecorded ? `Expand ${dependencyRows.length} dependency edges` : "Dependency records", ["Dependent", "Relation", "Head", "Head character offset", "Dependent span"], dependencyRows, dependenciesRecorded ? "No dependency records were returned." : "Dependency observations were not included in this response.");
      transparencyTable(parent, ["Sentence", "Subjects", "Objects/complements"], data.sentences.map((sentence) => [sentence.text, (sentence.subjects || []).map((item) => `${item.text} (${item.dependency})`).join(", "), (sentence.objects_or_complements || []).map((item) => `${item.text} (${item.dependency})`).join(", ")]), "Subject/object observations not available.");
    } else if (subKey === "noun-chunks") {
      const phrases = data.linguistic?.noun_phrases;
      transparencyExpandableTable(parent, Array.isArray(phrases) ? `Expand ${phrases.length} noun chunks` : "Noun chunk records", ["Noun chunk", "Start", "End", "Slice verified"], (phrases || []).map((phrase) => [phrase.text, phrase.start, phrase.end, Array.from(transparencyCurrentText(data)).slice(phrase.start, phrase.end).join("") === phrase.text]), Array.isArray(phrases) ? "No noun chunks were returned." : "Noun chunk observations were not included in this response.");
    } else if (subKey === "concepts") {
      const concepts = data.concepts;
      const conceptRows = Array.isArray(concepts) ? concepts.flatMap((concept) => (concept.occurrences || []).map((occurrence) => [occurrence.text, concept.normalized_form, occurrence.extraction_method, (occurrence.pos || []).join(", "), `[${occurrence.start}, ${occurrence.end})`, (occurrence.source_token_indices || []).join(", "), concept.occurrence_count])) : null;
      transparencyExpandableTable(parent, conceptRows ? `Expand ${conceptRows.length} actual concept occurrences` : "Concept occurrence records", ["Original phrase", "Normalized form", "Extraction method", "POS", "Span", "Token indices", "Occurrences"], conceptRows, Array.isArray(concepts) ? "No concept candidates were extracted." : "Detailed trace not included in this response — concept extraction output was not retained.");
    }
    return;
  }

  if (mainKey === "topic") {
    const focusSpecs = data.trace?.teacher_context?.focus_terms || [];
    const focusTerms = Array.isArray(lexical.focus_terms) ? lexical.focus_terms : focusSpecs.map((item) => item.term);
    if (subKey === "overview") {
      transparencyTable(parent, ["Coverage item", "Actual result"], [
        ["Focus source", lexical.focus_source || data.trace?.teacher_context?.focus_source],
        ["Observed focus terms", Array.isArray(lexical.observed_focus_terms) ? lexical.observed_focus_terms.join(", ") || "No focus-term matches were recorded." : "Focus coverage not included in this response."],
        ["Unobserved focus terms", Array.isArray(lexical.unobserved_focus_terms) ? lexical.unobserved_focus_terms.join(", ") || "No unobserved focus terms were recorded." : "Focus coverage not included in this response."],
        ["Observed unique count", lexical.observed_unique_focus_terms ?? lexical.observed_focus_terms?.length],
        ["Total unique count", lexical.total_unique_focus_terms ?? lexical.focus_terms?.length],
      ]);
      if (lexical.limitation) transparencyText(parent, lexical.limitation);
    } else if (subKey === "focus-terms") {
      transparencyTable(parent, ["Original term", "Normalized form", "Observed?", "Match records"], focusTerms.map((term) => [term, focusSpecs.find((item) => item.term === term)?.normalized_form || "Not recorded", (lexical.observed_focus_terms || []).includes(term) ? "Yes" : (lexical.unobserved_focus_terms || []).includes(term) ? "No lexical match" : "Status not recorded.", matches ? matches.filter((item) => item.focus_term === term).length : "Match records not included."]), Array.isArray(lexical.focus_terms) || Array.isArray(data.trace?.teacher_context?.focus_terms) ? "No focus terms were configured/derived." : "Focus terms not included in this response.");
    } else if (subKey === "normalization") {
      transparencyTable(parent, ["Term", "Surface words", "Normalized form", "Normalized words", "WordNet POS"], focusSpecs.map((item) => [item.term, (item.surface_words || []).join(" "), item.normalized_form, (item.normalized_words || []).join(" "), (item.wordnet_pos || []).join(", ") || "No mapped POS recorded"]), Array.isArray(data.trace?.teacher_context?.focus_terms) ? "No normalized focus terms were recorded." : "Detailed trace not included in this response — normalized focus specs were not retained.");
    } else if (subKey === "direct" || subKey === "lemma") {
      const method = subKey === "direct" ? "direct" : "normalized";
      const exactText = transparencyTextSources(data).text;
      const verifyMatch = (match) => exactText === null
        ? "NOT RECORDED — exact text source not resolved."
        : Array.from(exactText).slice(match.start, match.end).join("") === match.observed_text
          ? "Yes — slice matches the recorded text." : "No — slice differs from the recorded text.";
      const destination = "lexical_topic_evidence.matches → coverage counts, paragraph focus evidence, stage topic/context Rule Events and FeedbackService topic checks.";
      const methodRows = (matches || []).filter((match) => match.match_method === method).map((match) => [match.focus_term, match.observed_text, match.match_method, match.normalized_form, (match.pos || []).join(", "), match.start, match.end, verifyMatch(match), destination]);
      transparencyExpandableTable(parent, matches ? `Expand ${methodRows.length} recorded ${method} match(es)` : `${method} match records`, ["Focus term", "Matched surface", "Method", "Normalized form", "POS", "Start", "End", "Slice verified (derived)", "Next recorded destination"], methodRows, matches ? `No ${method} matches were recorded for this check.` : "Match records were not included in this response.");
    } else if (subKey === "wordnet") {
      renderStudentWordNet(parent, result, data);
    } else if (subKey === "cross-stage") {
      renderStudentCrossStage(parent, result, data);
    }
    return;
  }

  if (mainKey === "rules") {
    const decisions = Array.isArray(analysis.rule_evaluation_trace) ? analysis.rule_evaluation_trace : null;
    if (subKey === "overview") {
      transparencyTable(parent, ["Rule evidence", "Current value"], [["Emitted Rule Events", events?.length], ["Evaluation records", decisions?.length], ["Evaluation trace", decisions ? "Available" : "Not available"]], "Rule data not available.");
    } else if (subKey === "triggered") {
      transparencyExpandableTable(parent, events ? `Expand ${events.length} emitted Rule Events` : "Rule Event records", ["Rule ID", "Condition", "Evidence type", "Status"], (events || []).map((event) => [event.rule_id, event.triggering_condition, event.evidence_type, event.triggered === false || event.fired === false ? "Not triggered" : "Triggered / emitted"]), events ? "No Rule Events were emitted." : "Rule Event list not included in this response.");
      (events || []).forEach((event) => transparencyExpandable(parent, `${event.rule_id}: actual evidence and spans`, event.actual_evidence ?? event.evidence));
    } else if (subKey === "not-triggered") {
      if (!decisions) transparencyText(parent, "Not available — this analysis response did not include rule evaluation statuses.");
      else {
        const rows = decisions.filter((item) => item.status === "EVALUATED_NOT_TRIGGERED");
        transparencyTable(parent, ["Rule ID", "Condition", "Status", "Decision basis"], rows.map((item) => [item.rule_id, item.condition, item.status, item.decision_basis]), "No evaluated-but-not-triggered condition was recorded.");
        const otherStatuses = decisions.filter((item) => item.status !== "EVALUATED_NOT_TRIGGERED");
        transparencyExpandableTable(parent, `Expand ${otherStatuses.length} other rule statuses (not interpreted as negative)`, ["Other status", "Rule ID", "Decision basis"], otherStatuses.map((item) => [item.status, item.rule_id, item.decision_basis]), "No other rule statuses were recorded.");
      }
    } else if (subKey === "conditions") {
      if (!decisions) transparencyText(parent, "Not available — rule condition records were not returned.");
      else transparencyExpandableTable(parent, `Expand ${decisions.length} recorded rule conditions`, ["Rule ID", "Name", "Exact condition", "Status", "Decision basis"], decisions.map((item) => [item.rule_id, item.name, item.condition, item.status, item.decision_basis]));
    } else if (subKey === "evidence") {
      if (!decisions) transparencyText(parent, "Threshold/configuration trace not available.");
      else {
        transparencyExpandableTable(parent, `Expand ${decisions.length} configuration/threshold entries`, ["Rule ID", "Configuration/threshold", "Status"], decisions.map((item) => [item.rule_id, item.configuration, item.status]));
        const provenanceLinks = Array.isArray(result.feedback?.["Feedback Provenance"]) ? result.feedback["Feedback Provenance"] : [];
        transparencyTable(parent, ["Rule ID", "Recorded input evidence (source path — value)", "Emitted event evidence type (recorded)", "Recorded next consumer"], decisions.map((row) => {
          const event = events?.find((item) => item.rule_id === row.rule_id);
          const observed = transparencyRuleInputs(row, data);
          const value = observed.value;
          const summary = Array.isArray(value) ? `${value.length} returned record(s)`
            : value && typeof value === "object" ? `${Object.keys(value).length} recorded field(s)`
              : value === undefined ? "input observation not returned" : String(value);
          const links = provenanceLinks.filter((item) => item.rule_id === row.rule_id).map((item) => item.feedback_field);
          return [row.rule_id, `${observed.source} — ${summary}`, event?.evidence_type || "Not applicable — no emitted event for this rule in this response.", links.length ? `Feedback fields: ${links.join(", ")}` : event ? "Emitted event recorded; no feedback field links to it in this response." : "No emitted event; recorded for inspection only."];
        }), "Rule evaluation records were not returned for this response.");
      }
      (events || []).forEach((event) => transparencyExpandable(parent, `${event.rule_id}: emitted evidence`, event.actual_evidence ?? event.evidence));
    } else if (subKey === "code") {
      if (!decisions) transparencyText(parent, "Not available — source references are included with trace-mode rule records.");
      else transparencyExpandableTable(parent, `Expand ${decisions.length} rule implementation references`, ["Rule ID", "Implementation", "Lines", "Reference IDs"], decisions.map((item) => [item.rule_id, `${item.implementation?.file || "Not available"} ${item.implementation?.class || ""}.${item.implementation?.function || ""}`, item.implementation?.start_line ? `${item.implementation.start_line}–${item.implementation.end_line}` : item.implementation?.line_status, (item.reference_ids || []).join(", ") || "No direct source mapping"]));
    }
    return;
  }

  if (mainKey === "feedback") {
    const fieldName = ({ goal: "Current Goal", primary: "Primary Feedback", working: "What's Working", attention: "Needs Attention", next: "Next Step" })[subKey];
    const provenance = result.feedback?.["Feedback Provenance"];
    if (subKey === "overview") {
      for (const name of ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"]) {
        const section = transparencySection(parent, name);
        transparencyFeedbackField(result.feedback, name, section);
      }
    } else if (fieldName) {
      const section = transparencySection(parent, fieldName);
      transparencyFeedbackField(result.feedback, fieldName, section);
      if (Array.isArray(provenance)) {
        const selected = provenance
          .filter((item) => item.feedback_field === fieldName)
          .map((item) => resolveStudentFeedbackProvenance(item, result));
        transparencyTable(section, ["Rule ID", "Condition", "Evidence type", "Limitation"], selected.map((item) => [item.rule_id, item.triggering_condition, item.evidence_type, item.limitations ?? item.limitation]), "No provenance record was returned for this field.");
        selected.forEach((item) => transparencyExpandable(section, `${item.rule_id}: source evidence`, item.actual_evidence ?? item.evidence));
      } else transparencyText(section, "Not available — feedback provenance was not returned.");
    } else if (subKey === "provenance") {
      if (!Array.isArray(provenance)) transparencyText(parent, "Not available — provenance array missing.");
      else {
        const resolved = provenance.map((item) => resolveStudentFeedbackProvenance(item, result));
        transparencyTable(parent, ["Feedback field", "Rule ID", "Condition", "Evidence type", "Limitation"], resolved.map((item) => [item.feedback_field, item.rule_id, item.triggering_condition, item.evidence_type, item.limitations]), "No feedback provenance items were returned.");
        resolved.forEach((item) => transparencyExpandable(parent, `${item.feedback_field}: ${item.rule_id} evidence`, item.actual_evidence));
      }
      transparencyExpandable(parent, "Recorded FeedbackService branch trace", data.stageTrace?.feedback_decisions || "Not available — feedback branch selection was not recorded.");
    }
  }
}

function transparencyWordNetStatus(record, comparison) {
  const execution = String(record?.execution_status || "").toUpperCase();
  const status = String(record?.status || "").toUpperCase();
  if (["NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED", "NOT_AVAILABLE_NO_BODY_SUPPLIED"].includes(comparison?.status)) {
    return { label: "Not applicable — no earlier section was supplied.", executed: false, empty: "Not applicable" };
  }
  if (status === "DISABLED" || execution === "DISABLED") {
    return { label: "Not executed for this stage — disabled.", executed: false, empty: "Not executed" };
  }
  if (status === "NOT_APPLICABLE" || execution === "NOT_APPLICABLE") {
    return { label: "Not applicable for this stage.", executed: false, empty: "Not applicable" };
  }
  if ([execution, status].some((value) => ["SKIPPED", "NOT_EVALUATED", "NOT_EXECUTED"].includes(value))) {
    return { label: `Not executed for this stage — ${execution === "SKIPPED" || status === "SKIPPED" ? "skipped" : "not evaluated"}.`, executed: false, empty: "Not executed" };
  }
  if (status === "RESOURCE_MISSING" || execution === "RESOURCE_MISSING") {
    return { label: "Resource unavailable — WordNet corpus is missing; candidate lookup could not run.", executed: false, empty: "Resource unavailable" };
  }
  if ([execution, status].some((value) => ["FAILED", "ERROR"].includes(value))) {
    return { label: "Error — WordNet processing reported a failure.", executed: false, empty: "Error" };
  }
  // AVAILABLE is the completed cross-stage check's documented return status;
  // an empty suggestions array or POS labels alone never establish execution.
  if (execution === "EXECUTED" || (!execution && comparison && status === "AVAILABLE")) {
    return { label: "Executed — WordNet candidate check completed.", executed: true, empty: "Not recorded" };
  }
  return { label: "Status not recorded.", executed: false, empty: "Status not recorded" };
}

function renderStudentWordNet(parent, result, data) {
  const lexical = data.analysis.lexical_topic_evidence || {};
  const direct = data.stageTrace?.topic_service?.steps?.find((step) => step.id === "wordnet_direct_suggestions");
  const topicInput = data.stageTrace?.topic_service?.input;
  const focusSpecs = data.trace?.teacher_context?.focus_terms || [];
  const paths = [["TopicService direct suggestions", direct, null, direct?.output ?? data.analysis.lexical_topic_evidence?.wordnet_relationship_candidates]];
  for (const [key, name] of [
    ["introduction_to_body_continuity", "Introduction–Body"],
    ["introduction_to_conclusion_continuity", "Introduction–Conclusion"],
    ["body_to_conclusion_continuity", "Body–Conclusion"],
  ]) {
    const comparison = data.analysis[key];
    if (comparison) paths.push([name, comparison.wordnet_relationship_candidates, comparison, comparison.wordnet_relationship_candidates?.suggestions]);
  }

  // A. Original writing this lookup ran against.
  transparencyAnalyzedEssay(parent, data);

  // B. Which pathway executed, and the recorded enablement that explains it.
  const statusSection = transparencySection(parent, "B. Which WordNet pathway ran for this analysis");
  const statusRows = paths.map(([name, record, comparison, suggestions]) => {
    const status = transparencyWordNetStatus(record, comparison);
    const count = (items) => Array.isArray(items)
      ? status.executed ? items.length : items.length ? `${items.length} recorded; execution not established` : status.empty
      : status.empty;
    return [name, status.label, record?.wordnet_version || record?.status || "Status not recorded.", count(record?.lookup_pairs), count(suggestions)];
  });
  transparencyTable(statusSection, ["Path", "Execution status", "Corpus version/status", "Recorded lookup pairs", "Recorded candidates"], statusRows);
  if (!direct) transparencyText(statusSection, "Detailed trace not included in this response — the direct WordNet path record was not retained.");
  transparencyTable(statusSection, ["Pathway", "Where this lookup runs (implementation)", "Recorded enablement for this run"], [
    ["TopicService direct suggestions", "services/topic_service.py: _wordnet_status, _wordnet_suggestions (inside TopicService.analyze)", topicInput
      ? `research_trace.stages.${data.stage}.topic_service.input.include_wordnet = ${String(topicInput.include_wordnet)} — direct path ${topicInput.include_wordnet ? "was enabled for this stage" : "was disabled for this stage"}.`
      : "NOT RECORDED — topic_service.input.include_wordnet is absent from this response; it is still reported under Final Feedback → Complete Evidence."],
    ["Cross-stage comparisons (the three paths above)", "Stage Rule Base → services/stage_evidence.py: compare_stage_concepts → _wordnet_candidates", "No enable flag exists for these paths; they run whenever earlier-section concept pairs qualify, earlier text is supplied and WordNet is available."],
  ]);

  // C. Input words for each pathway.
  const inputSection = transparencySection(parent, "C. Input words for each pathway");
  const singleWordConcepts = (Array.isArray(data.concepts) ? data.concepts : [])
    .filter((concept) => !/\s/.test(String(concept.normalized_form || "")));
  const directPairs = Array.isArray(direct?.lookup_pairs) ? direct.lookup_pairs : [];
  transparencyTable(inputSection, ["Input group", "Recorded values", "Evidence type", "Recorded source"], [
    ["Teacher focus targets supplied to TopicService", Array.isArray(topicInput?.focus_terms) ? topicInput.focus_terms.join(", ") : "NOT RECORDED", Array.isArray(topicInput?.focus_terms) ? "OBSERVED" : "NOT_RECORDED", `research_trace.stages.${data.stage}.topic_service.input.focus_terms`],
    ["Unobserved focus terms (recorded direct-path eligible set)", Array.isArray(lexical.unobserved_focus_terms) ? lexical.unobserved_focus_terms.join(", ") || "Recorded empty list — every focus term already matched directly or by lemma." : "NOT RECORDED", Array.isArray(lexical.unobserved_focus_terms) ? "OBSERVED" : "NOT_RECORDED", "analysis.lexical_topic_evidence.unobserved_focus_terms"],
    ["Student single-word concepts compared with those targets", singleWordConcepts.length ? singleWordConcepts.map((concept) => concept.normalized_form).join(", ") : "No single-word concept was recorded for this stage.", "DERIVED", "Filtered from the recorded concept groups by the documented single-word rule; no new lookup was run in the browser."],
    ["Student terms actually compared (named by recorded pairs)", directPairs.length ? [...new Set(directPairs.map((pair) => pair.observed_student_term))].join(", ") : "No direct lookup pair was recorded for this stage.", directPairs.length ? "OBSERVED" : "SKIPPED", "research_trace…topic_service.steps[wordnet_direct_suggestions].lookup_pairs"],
    ["Concept lists and pair-selection inputs for the cross-stage paths", "NOT RECORDED", "NOT_RECORDED", "The coordinator returns only the selected stage trace (app.py analyze_payload), and compact_student_transparency_trace removes cross_stage_comparison_inputs. The recorded lookup pairs in section E name every lemma and POS that was actually compared."],
  ]);

  // D. Word preparation before any synset query.
  const prepSection = transparencySection(parent, "D. Word preparation before lookup");
  transparencyTable(prepSection, ["Term", "Surface words", "Normalized form", "Normalized words", "WordNet POS (recorded per focus term)"], focusSpecs.map((item) => [item.term, (item.surface_words || []).join(" "), item.normalized_form, (item.normalized_words || []).join(" "), (item.wordnet_pos || []).join(", ") || "No mapped POS recorded"]), Array.isArray(data.trace?.teacher_context?.focus_terms) ? "No normalized focus terms were recorded." : "Detailed trace not included in this response — normalized focus specs were not retained.");
  transparencyText(prepSection, "STATIC EXPLANATION — direct path: focus terms are lemmatized and case-folded by TopicService._unique_focus_terms / _lemma; cross-stage path: concepts are already normalized forms and spaCy NOUN/PROPN map to n, VERB to v, ADJ to a, ADV to r. No synset was queried from this table alone.");

  // E. The actual synset lookups, pair by pair.
  const lookupSection = transparencySection(parent, "E. Actual WordNet lookups (recorded pair by pair)");
  for (const [name, record, comparison] of paths) {
    const status = transparencyWordNetStatus(record, comparison);
    const pairs = Array.isArray(record?.lookup_pairs) ? record.lookup_pairs : null;
    if (pairs && pairs.length) {
      const directPair = !comparison;
      transparencyExpandableTable(lookupSection, `${name}: ${pairs.length} recorded lookup pair(s)`, directPair
        ? ["Teacher term", "Teacher lemma", "Teacher POS", "Teacher synsets", "Student lemma", "Student POS", "Student synsets", "Shared synsets", "Candidate emitted", "Student span"]
        : ["Source lemma", "Source POS", "Source synsets", "Target lemma", "Target POS", "Target synsets", "Shared synsets", "Candidate emitted"],
        pairs.map((pair) => directPair
          ? [pair.teacher_term, pair.teacher_lemma, (pair.teacher_pos || []).join(", "), (pair.teacher_synset_ids || []).join(", ") || "None", pair.student_lemma, pair.student_pos, (pair.student_synset_ids || []).join(", ") || "None", (pair.shared_synset_ids || []).join(", ") || "None", pair.candidate_emitted ? "Yes" : "No", Array.isArray(pair.source_span) ? `[${pair.source_span[0]}, ${pair.source_span[1]})` : "NOT RECORDED"]
          : [pair.source_lemma, pair.source_pos, (pair.source_synset_ids || []).join(", ") || "None", pair.target_lemma, pair.target_pos, (pair.target_synset_ids || []).join(", ") || "None", (pair.shared_synset_ids || []).join(", ") || "None", pair.candidate_emitted ? "Yes" : "No"]));
      if (pairs[0]?.selection_condition) transparencyText(lookupSection, `${name}: recorded selection condition — ${pairs[0].selection_condition}`);
    } else if (status.executed) {
      transparencyText(lookupSection, `${name}: executed, but no lookup pair records were retained for this path.`);
    } else {
      transparencyText(lookupSection, `${name}: NOT RECORDED — this path did not run for this analysis, so no pair or synset list exists for it.`);
    }
  }

  // F. Recorded results.
  const resultSection = transparencySection(parent, "F. Recorded results and candidates");
  transparencyTable(resultSection, ["Pathway", "Recorded candidates", "Synset ID(s) of recorded candidates", "Rejected lookup pairs"], paths.map(([name, record, comparison, suggestions]) => {
    const status = transparencyWordNetStatus(record, comparison);
    const items = Array.isArray(suggestions) ? suggestions : [];
    const pairs = Array.isArray(record?.lookup_pairs) ? record.lookup_pairs : [];
    const rejected = pairs.filter((pair) => pair.candidate_emitted === false).length;
    return [name, status.executed ? items.length : status.empty,
      items.length ? [...new Set(items.map((item) => item.synset_id || "Synset ID not recorded"))].join(", ") : "None recorded",
      pairs.length ? `${rejected} of ${pairs.length} recorded pairs were not emitted` : "No pair records for this path"];
  }));
  for (const [name, record, comparison, suggestions] of paths) {
    const status = transparencyWordNetStatus(record, comparison);
    if (status.executed && Array.isArray(suggestions) && suggestions.length === 0) {
      transparencyText(resultSection, `${name}: No WordNet relationship candidates were recorded for this check.`);
    }
    (Array.isArray(suggestions) ? suggestions : []).forEach((candidate, index) => {
      transparencyExpandable(resultSection, `${name}: candidate ${index + 1} — ${candidate?.synset_id || "synset not recorded"}`, candidate);
    });
    if (record) transparencyExpandable(resultSection, `${name}: actual inputs, status and lookup results`, {
      ...(comparison ? {} : { input: data.trace?.teacher_context }),
      ...record,
    });
    else if (Array.isArray(suggestions)) transparencyExpandable(resultSection, `${name}: retained candidates (execution status not recorded)`, suggestions);
  }

  // G. Recorded downstream use (or absence of use) of these candidates.
  const downstreamSection = transparencySection(parent, "G. Where each recorded candidate goes next");
  const events = (Array.isArray(data.analysis.rule_evidence) ? data.analysis.rule_evidence : []).filter((event) => event.rule_id.includes("WORDNET"));
  const provenance = Array.isArray(result.feedback?.["Feedback Provenance"]) ? result.feedback["Feedback Provenance"] : [];
  const wordnetProvenance = provenance.filter((item) => events.some((event) => event.rule_id === item.rule_id));
  const paraphrases = data.analysis.new_material_observations?.candidate_paraphrase_relationships;
  const directCandidates = Array.isArray(lexical.wordnet_relationship_candidates) ? lexical.wordnet_relationship_candidates : null;
  transparencyTable(downstreamSection, ["Pathway / step", "Recorded downstream use in this response", "Evidence type"], [
    ["TopicService direct suggestions → analysis.lexical_topic_evidence", directCandidates
      ? `${directCandidates.length} candidate item(s) recorded. No emitted WordNet Rule Event and no Feedback Provenance item references these direct suggestions in this response (checked against analysis.rule_evidence and feedback['Feedback Provenance']).`
      : "Not present for this stage — direct suggestions only run when topic_service.input.include_wordnet is true (Conclusion in this coordinator path).", directCandidates ? "OBSERVED" : "SKIPPED"],
    ["Cross-stage candidates → Rule Events", events.length ? `Emitted: ${events.map((event) => event.rule_id).join(", ")}.` : "No WordNet Rule Event was emitted in this response.", events.length ? "OBSERVED" : "NOT_RECORDED"],
    ["Cross-stage candidates → Conclusion new-material observations", data.stage === "CONCLUSION"
      ? `analysis.new_material_observations.candidate_paraphrase_relationships holds ${Array.isArray(paraphrases) ? paraphrases.length : 0} recorded item(s).`
      : "Not applicable for this stage.", data.stage === "CONCLUSION" ? "OBSERVED" : "SKIPPED"],
    ["WordNet candidates → FeedbackService", wordnetProvenance.length
      ? `Linked in Feedback Provenance: ${wordnetProvenance.map((item) => `${item.feedback_field} ← ${item.rule_id}`).join("; ")}.`
      : "No Feedback Provenance item in this response references a WordNet Rule Event. SOURCE-VERIFIED LOGIC — FeedbackService does not read WordNet candidates. Cross-stage WordNet events record informational candidates; they do not select feedback.", "SOURCE-VERIFIED LOGIC"],
    ["Any candidate → semantic validation", "None. No WordNet candidate is treated as verified meaning anywhere in this response.", "STATIC EXPLANATION — services/feedback_service.py contains no reference to WordNet candidates; recorded limitations state senses are not disambiguated."],
  ]);

  // H. Limitations.
  const limitsSection = transparencySection(parent, "H. Limitations of these records");
  for (const [name, record, comparison] of paths) {
    const limitation = record?.limitation || comparison?.limitation;
    if (limitation) transparencyText(limitsSection, `${name}: ${limitation}`, "field-help");
    else if (record) transparencyText(limitsSection, `${name}: no limitation string was recorded on this record.`, "field-help");
  }
  transparencyText(limitsSection, "WordNet candidates remain separate from direct/lemma coverage and do not disambiguate the sense used in this sentence.", "field-help");
  transparencyText(limitsSection, `Recorded interpretation limit: ${data.analysis.interpretation_limit || result.interpretation_limit || "Not recorded."}`, "field-help");
}

// Cross-stage comparison inspection: original writing of every participating
// stage, recorded concept lists and pairs, verified spans, unmatched concepts,
// limitations, the Rule Base that consumed each record and any recorded
// feedback link. Earlier-stage concept lists are honestly NOT RECORDED because
// the response keeps only the selected stage trace.
function renderStudentCrossStage(parent, result, data) {
  const analysis = data.analysis;
  const stageKey = String(data.stage).toLowerCase();
  const comparisons = [];
  if (analysis.introduction_to_body_continuity) comparisons.push(["Introduction → Body", "introduction_to_body_continuity", ["introduction", "body"], "services/body_rules.py: analyze (nested introduction_to_body_continuity)", "BODY.INTRO_CONTINUITY"]);
  if (analysis.introduction_to_conclusion_continuity) comparisons.push(["Introduction → Conclusion", "introduction_to_conclusion_continuity", ["introduction", "conclusion"], "services/conclusion_rules.py: analyze (nested introduction_to_conclusion_continuity)", "CONCLUSION.CONTINUITY.INTRODUCTION"]);
  if (analysis.body_to_conclusion_continuity) comparisons.push(["Body → Conclusion", "body_to_conclusion_continuity", ["body", "conclusion"], "services/conclusion_rules.py: analyze (nested body_to_conclusion_continuity)", "CONCLUSION.CONTINUITY.BODY"]);
  if (!comparisons.length) {
    transparencyText(parent, data.stage === "INTRODUCTION" ? "Not applicable — cross-stage comparison is not performed for Introduction." : "Comparison data not included in this response.");
    return;
  }

  const sectionText = (key) => key === stageKey ? transparencyTextSources(data).text : data.stageTrace?.input_sections?.[key] ?? null;
  const verify = (key, start, end, text) => {
    const source = sectionText(key);
    if (source === null) return "NOT RECORDED — this section's exact text is not in the response.";
    return Array.from(source).slice(start, end).join("") === text ? "Yes — slice matches the recorded text." : "No — slice differs from the recorded text.";
  };

  // 0. Summary of each recorded comparison.
  transparencyTable(parent, ["Comparison", "Status", "Direct matches", "Lemma matches", "Unmatched source concepts"], comparisons.map(([name, key]) => {
    const item = analysis[key];
    const notApplicable = ["NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED", "NOT_AVAILABLE_NO_BODY_SUPPLIED"].includes(item.status);
    const executed = item.status === "LEXICAL_COMPARISON_AVAILABLE";
    const missing = notApplicable ? "Not applicable" : "Status not recorded.";
    return [name, notApplicable ? "Not applicable — no earlier section was supplied." : item.status || "Status not recorded.", executed ? item.direct_lexical_continuity?.length : missing, executed ? item.lemma_normalized_continuity?.length : missing, executed ? item.unobserved_introduction_concepts || item.unmatched_source_concepts : missing];
  }), "Comparison data not included in this response.");

  // 1. Original analyzed writing from each participating stage.
  const originalSection = transparencySection(parent, "1. Original analyzed writing from each participating stage");
  const currentSource = transparencyTextSources(data);
  const currentBlock = transparencySection(originalSection, `${data.stage} — current stage`);
  if (currentSource.text !== null) {
    studentSourceViewer(currentBlock, currentSource.text, `${data.stage}: exact analyzed text used for this comparison`);
    transparencyText(currentBlock, `Exact source: ${currentSource.source}. Offsets below that name this stage refer to this text.`, "student-input-provenance");
  } else transparencyText(currentBlock, `NOT RECORDED — exact text source not resolved (${currentSource.source}).`);
  const priorKeys = [...new Set(comparisons.flatMap(([, , keys]) => keys.filter((key) => key !== stageKey)))];
  for (const key of priorKeys) {
    const block = transparencySection(originalSection, `${key.toUpperCase()} — earlier section`);
    const text = data.stageTrace?.input_sections?.[key];
    if (typeof text === "string") {
      studentSourceViewer(block, text, `${key}: exact earlier-section text used for this comparison`);
      transparencyText(block, `Exact source: research_trace.stages.${data.stage}.input_sections.${key}.`, "student-input-provenance");
    } else transparencyText(block, "NOT RECORDED — this earlier section's text was not supplied; the continuity status in the summary above reports the same absence.", "student-input-provenance");
  }

  // 2. Concept lists that entered the comparison.
  const conceptSection = transparencySection(parent, "2. Concept lists used as comparison material");
  const concepts = Array.isArray(data.concepts) ? data.concepts : [];
  transparencyTable(conceptSection, ["Section", "Concept groups (normalized forms)", "Evidence type", "Recorded source"], [
    [data.stage, concepts.length ? concepts.map((concept) => concept.normalized_form).join(", ") : "Recorded empty list — no concepts were extracted for this stage.", concepts.length ? "OBSERVED" : "SKIPPED", `research_trace.stages.${data.stage}.topic_service.steps[concept_extraction].output`],
    ["Earlier sections (each prior stage's concept list)", "NOT RECORDED", "NOT_RECORDED", "The response keeps only the selected stage trace (app.py analyze_payload), and compact_student_transparency_trace removes cross_stage_comparison_inputs. The recorded pair evidence in sections 3–5 names every concept occurrence that was actually compared."],
  ]);

  // 3–5. Recorded pairs with slice verification.
  const pairSection = transparencySection(parent, "3–5. Recorded concept-pair comparisons, verified against the original text");
  const eventIds = (Array.isArray(analysis.rule_evidence) ? analysis.rule_evidence : []).map((event) => event.rule_id);
  for (const [name, key, sideKeys] of comparisons) {
    const item = analysis[key];
    const notApplicable = ["NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED", "NOT_AVAILABLE_NO_BODY_SUPPLIED"].includes(item.status);
    const executed = item.status === "LEXICAL_COMPARISON_AVAILABLE";
    transparencySection(pairSection, `${name}`);
    if (!executed) {
      transparencyText(pairSection, notApplicable ? "Not applicable — no earlier section was supplied." : `Status not recorded — ${item.status || "no status was returned"}; pair rows are NOT RECORDED for this path.`);
      continue;
    }
    const pairRows = (list) => (Array.isArray(list) ? list : []).flatMap((entry) => (Array.isArray(entry.matching_occurrences) ? entry.matching_occurrences : []).flatMap((occurrencePair) => {
      const cells = [name, entry.normalized_form, entry.evidence_type];
      for (const sideKey of sideKeys) {
        const occurrence = occurrencePair[sideKey];
        if (!occurrence) {
          cells.push("NOT RECORDED", "", "NOT RECORDED");
        } else {
          cells.push(`"${occurrence.text}" (${sideKey})`, `[${occurrence.start}, ${occurrence.end})`, verify(sideKey, occurrence.start, occurrence.end, occurrence.text));
        }
      }
      return [cells];
    }));
    const directRows = pairRows(item.direct_lexical_continuity);
    transparencyExpandableTable(pairSection, `Direct correspondence — ${directRows.length} recorded occurrence pair(s)`, ["Comparison", "Normalized form", "Evidence type", `${sideKeys[0]} occurrence`, `${sideKeys[0]} span`, `${sideKeys[0]} slice verified`, `${sideKeys[1]} occurrence`, `${sideKeys[1]} span`, `${sideKeys[1]} slice verified`], directRows, "No direct correspondence records were returned for this comparison.");
    const lemmaRows = pairRows(item.lemma_normalized_continuity);
    transparencyExpandableTable(pairSection, `Lemma correspondence — ${lemmaRows.length} recorded occurrence pair(s)`, ["Comparison", "Normalized form", "Evidence type", `${sideKeys[0]} occurrence`, `${sideKeys[0]} span`, `${sideKeys[0]} slice verified`, `${sideKeys[1]} occurrence`, `${sideKeys[1]} span`, `${sideKeys[1]} slice verified`], lemmaRows, "No lemma correspondence records were returned for this comparison.");
    if (!directRows.length && !lemmaRows.length) transparencyText(pairSection, `${name}: No direct or lemma matches were recorded for this check.`);

    const wordnet = item.wordnet_relationship_candidates;
    const suggestions = Array.isArray(wordnet?.suggestions) ? wordnet.suggestions : [];
    const suggestionRows = suggestions.flatMap((suggestion) => sideKeys.flatMap((sideKey) => {
      const side = suggestion[sideKey];
      if (!side) return [];
      const otherSide = sideKeys.find((other) => other !== sideKey);
      return (Array.isArray(side.occurrences) ? side.occurrences : []).map((occurrence) => [
        name, suggestion.synset_id || "Synset ID not recorded", side.term, `"${occurrence.text}"`, `[${occurrence.start}, ${occurrence.end})`,
        verify(sideKey, occurrence.start, occurrence.end, occurrence.text),
        suggestion[otherSide] ? `${suggestion[otherSide].term} (${(suggestion[otherSide].occurrences || []).length} occurrence(s))` : "Other side not recorded",
        suggestion.limitation || wordnet?.limitation || "Limitation not recorded",
      ]);
    }));
    const wnStatus = wordnet?.status ? (wordnet.status === "AVAILABLE" ? "Executed — WordNet candidate check completed." : wordnet.status) : "Status not recorded.";
    transparencyExpandableTable(pairSection, `WordNet correspondence — ${suggestions.length} recorded candidate(s) · ${wnStatus}`, ["Comparison", "Synset ID", "Term", "Occurrence", "Span", "Slice verified", "Other side", "Recorded limitation"], suggestionRows, suggestions.length ? "Candidate occurrences were not expanded for this record." : "No WordNet correspondence record for this comparison.");
    if (wordnet && Array.isArray(wordnet.lookup_pairs)) transparencyText(pairSection, `WordNet lookups for this comparison: ${wordnet.lookup_pairs.length} recorded pair(s) — full pair detail is in Topic Matching → WordNet.`);
  }

  // 6. Unmatched source concepts across all recorded comparisons.
  const unmatchedSection = transparencySection(parent, "6. Unmatched source concepts");
  transparencyTable(unmatchedSection, ["Comparison", "Recorded unmatched source concepts", "Evidence type", "Meaning"], comparisons.map(([name, key]) => {
    const unmatched = analysis[key].unobserved_introduction_concepts || analysis[key].unmatched_source_concepts;
    if (Array.isArray(unmatched)) return [name, unmatched.length ? unmatched.join(", ") : "Recorded empty list — every source concept found a recorded correspondence.", "OBSERVED", unmatched.length ? "Source concepts with no recorded direct or lemma correspondence in the target section." : "Absence of an unmatched list does not establish complete correspondence; only recorded pairs are shown."];
    return [name, "NOT RECORDED", "NOT_RECORDED", "No unmatched-concept list was returned for this comparison."];
  }));

  // 7. Outcomes and limitations.
  const outcomeSection = transparencySection(parent, "7. Comparison outcomes and recorded limitations");
  transparencyTable(outcomeSection, ["Comparison", "Status", "Recorded limitation"], comparisons.map(([name, key]) => {
    const item = analysis[key];
    const limitation = item.limitation || item.wordnet_relationship_candidates?.limitation;
    return [name, item.status || "Status not recorded.", limitation || "No separate limitation string was recorded on this comparison record; see Final Feedback → Limitations for the interpretation limit."];
  }));

  // 8. Which Rule Base read these records.
  const consumerSection = transparencySection(parent, "8. Which Rule Base used each comparison");
  transparencyTable(consumerSection, ["Comparison", "Rule Base (implementation)", "Emitted Rule Events from this comparison in this response", "Evidence type"], comparisons.map(([name, , , source, eventPrefix]) => {
    const emitted = eventIds.filter((id) => id.startsWith(eventPrefix));
    return [name, source, emitted.length ? emitted.join(", ") : "No event from this comparison was emitted in this response.", emitted.length ? "OBSERVED" : "STATIC"];
  }));

  // 9. Recorded feedback impact (presence or absence).
  const feedbackSection = transparencySection(parent, "9. Whether these records affected feedback in this run");
  const provenance = Array.isArray(result.feedback?.["Feedback Provenance"]) ? result.feedback["Feedback Provenance"] : [];
  transparencyTable(feedbackSection, ["Comparison", "Recorded feedback links", "Evidence type"], comparisons.map(([name, , , , eventPrefix]) => {
    const emitted = eventIds.filter((id) => id.startsWith(eventPrefix));
    const linked = provenance.filter((item) => emitted.includes(item.rule_id));
    return [name, linked.length ? linked.map((item) => `${item.feedback_field} ← ${item.rule_id}`).join("; ") : "No Feedback Provenance item in this response references this comparison; in this run it did not change a feedback field.", "OBSERVED"];
  }));

  transparencyExpandable(parent, "Actual cross-stage comparison records (complete returned data)", comparisons.map(([, key]) => [key, analysis[key]]));
}

function transparencyRenderDecisionSummary(parent, mainKey, subKey, result, data) {
  if (mainKey === "rules") {
    const decisions = data.analysis.rule_evaluation_trace;
    if (!Array.isArray(decisions)) transparencyText(parent, "Detailed trace not included in this response — rule evaluation statuses were not retained.");
    else {
      const rows = subKey === "not-triggered" ? decisions.filter((item) => item.status === "EVALUATED_NOT_TRIGGERED") : decisions;
      transparencyTable(parent, ["Rule ID", "Status", "Decision basis"], rows.map((item) => [item.rule_id, item.status, item.decision_basis]), "No recorded decision for this subtab.");
    }
  } else if (mainKey === "feedback") {
    const decisions = data.stageTrace?.feedback_decisions;
    if (decisions) transparencyEvidence(parent, decisions);
    else transparencyText(parent, "Detailed trace not included in this response — feedback branch selection was not retained.");
  } else if (mainKey === "topic") {
    transparencyEvidence(parent, { observed_focus_terms: data.analysis.lexical_topic_evidence?.observed_focus_terms, unobserved_focus_terms: data.analysis.lexical_topic_evidence?.unobserved_focus_terms, limitation: data.analysis.lexical_topic_evidence?.limitation });
  } else {
    transparencyText(parent, "No semantic or quality decision is made by these linguistic observations.");
  }
  void result;
}

// Export only selected-stage technical data, never account/session/workspace state.
const ANALYSIS_REPORT_PRIVATE_KEYS = new Set([
  "password", "passwordhash", "secret", "secretkey", "credentials", "authorization",
  "cookie", "cookies", "headers", "csrf", "csrftoken", "accesstoken", "refreshtoken",
  "session", "sessions", "sessionid", "sessiontoken", "account", "accounts", "accountid",
  "userid", "studentid", "teacherid", "ownerid", "classroomid", "assignmentid",
  "username", "email", "users", "students", "unrelatedrecords", "unrelatedstudentrecords",
  "studentrecords", "otherstudents", "otherstudentrecords", "accountrecords",
]);

function analysisReportValue(value) {
  if (Array.isArray(value)) return value.map(analysisReportValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort()
      .filter((key) => !ANALYSIS_REPORT_PRIVATE_KEYS.has(key.replace(/[^a-z0-9]/gi, "").toLowerCase()))
      .map((key) => [key, analysisReportValue(value[key])]));
  }
  return value;
}

function buildFullAnalysisReport(result, retainedRecords = null) {
  const data = transparencyData(result);
  const { analysis, stage, stageTrace, trace } = data;
  const stagePath = `research_trace.stages.${stage}`;
  const missing = "Not available in the cached response.";
  const lines = ["ESSAYSCAFF V2 — FULL ANALYSIS", "Source: cached selected-stage analysis response; no analysis was rerun.", "Source paths below refer to that response. Recorded values are preserved; absent values are not inferred."];
  const heading = (title) => lines.push("", title, "=".repeat(title.length));
  const record = (label, path, value) => {
    if (retainedRecords) retainedRecords.push({ label, path, value: analysisReportValue(value) });
    lines.push("", `${label} [source: ${path}]`);
    lines.push(value === undefined ? missing : typeof value === "string" ? value : JSON.stringify(analysisReportValue(value), null, 2));
  };
  const topicService = stageTrace?.topic_service;
  const steps = Array.isArray(topicService?.steps) ? topicService.steps : [];
  const linguisticSources = [
    ["analysis.linguistic_observations", analysis.linguistic_observations],
    ["analysis.linguistic_analysis", analysis.linguistic_analysis],
    [`${stagePath}.linguistic_observations`, stageTrace?.linguistic_observations],
  ];
  const uniqueRecords = (label, sources) => {
    const seen = new Map();
    let supplied = false;
    for (const [path, value] of sources) {
      if (value === undefined || value === null) continue;
      supplied = true;
      const encoded = JSON.stringify(analysisReportValue(value));
      if (seen.has(encoded)) lines.push(`${path}: identical retained copy; see ${seen.get(encoded)} above.`);
      else { record(label, path, value); seen.set(encoded, path); }
    }
    if (!supplied) record(label, sources.map(([path]) => path).join(" or "), undefined);
  };

  heading("1. Report Context");
  record("Writing stage", "stage_id / analysis.stage", stage);
  record("Analysis availability", "availability", result?.availability);
  const inputEvidence = studentTextInputEvidence(result);
  record("Analyzed draft identification", "Browser-derived text fingerprint from retained analyzed text (not a saved revision ID)", inputEvidence.browser_fingerprint ?? "Not recorded.");
  record("Editor words", "Browser-derived whitespace-separated count of retained analyzed text", inputEvidence.whitespace_words ?? "Not recorded.");
  record("Assignment topic/question", "research_trace.teacher_context.assignment_topic / analysis.assignment_topic", trace?.teacher_context?.assignment_topic ?? analysis.assignment_topic);
  record("Focus term source", "analysis.lexical_topic_evidence.focus_source / research_trace.teacher_context.focus_source", analysis.lexical_topic_evidence?.focus_source ?? trace?.teacher_context?.focus_source);
  record("Focus terms", "analysis.lexical_topic_evidence.focus_terms / research_trace.teacher_context.focus_terms", analysis.lexical_topic_evidence?.focus_terms ?? trace?.teacher_context?.focus_terms);
  record("Current analyzed writing text", "analysis.input_text / linguistic observations.text / selected-stage input_sections / supplied_text", inputEvidence.text ?? undefined);
  record("Process 01 captured-input evidence", "frontend.studentTextInputEvidence (retained response fields + explicitly browser-derived values)", inputEvidence);
  if (stage === "INTRODUCTION") lines.push("", "Prior-section context: Not applicable — Introduction does not compare earlier sections.");
  else {
    for (const prior of stage === "BODY" ? ["introduction"] : ["introduction", "body"]) {
      const comparison = analysis[`${prior}_to_${String(stage).toLowerCase()}_continuity`];
      record(`Recorded ${prior} input for cross-stage analysis`, `${stagePath}.input_sections.${prior}`,
        stageTrace?.input_sections?.[prior] ?? (comparison?.status === `NOT_AVAILABLE_NO_${prior.toUpperCase()}_SUPPLIED` ? "Not applicable — no earlier section was supplied." : undefined));
    }
  }
  record("Analysis interpretation limit", "interpretation_limit", result?.interpretation_limit);

  heading("2. Text Processing");
  const counts = data.linguistic?.counts || analysis.text_presence || {};
  for (const [label, key] of [["Tokens", "token_count"], ["Alphabetic words", "alphabetic_word_count"], ["Sentences", "sentence_count"]]) {
    record(label, `linguistic observations.counts.${key} / analysis.text_presence.${key}`, counts[key]);
  }
  const paragraphCount = analysis.paragraph_count ?? analysis.text_presence?.paragraph_count
    ?? (Array.isArray(analysis.paragraphs) ? analysis.paragraphs.length
      : Array.isArray(analysis.conclusion_paragraphs) ? analysis.conclusion_paragraphs.length
        : stage === "INTRODUCTION" ? "Not collected for this stage." : undefined);
  record("Paragraphs", "analysis.paragraph_count / analysis.text_presence.paragraph_count / returned paragraph array length", paragraphCount);
  uniqueRecords("Complete linguistic observations: tokens, lemmas, POS, fine tags, sentences, dependencies, noun chunks and spans", linguisticSources);
  for (const [index, step] of steps.entries()) {
    if (["spacy_document_processing", "concept_extraction"].includes(step.id)) record(`Processing step: ${step.id}`, `${stagePath}.topic_service.steps[${index}]`, step);
  }
  if (!steps.some((step) => step.id === "concept_extraction")) lines.push("", "Full-stage extracted-concept trace: Not available in the cached response. Any retained paragraph concepts appear in section 4.");

  heading("3. Topic Matching");
  record("Configured focus context and normalized forms", "research_trace.teacher_context", trace?.teacher_context);
  record("Complete lexical evidence: matched/unmatched terms, direct/lemma matches and original spans", "analysis.lexical_topic_evidence", analysis.lexical_topic_evidence);
  record("Related Topic Concepts — separate informational evidence, not direct/lemma coverage or WordNet", "related_topic_concept_evidence", result?.related_topic_concept_evidence);
  record("TopicService execution/context metadata", `${stagePath}.topic_service (excluding steps shown separately)`, topicService ? Object.fromEntries(Object.entries(topicService).filter(([key]) => key !== "steps")) : undefined);
  for (const [index, step] of steps.entries()) {
    if (!["spacy_document_processing", "concept_extraction"].includes(step.id)) record(`Topic step: ${step.id}`, `${stagePath}.topic_service.steps[${index}]`, step);
  }
  const wordnet = (label, path, value, comparison, candidates) => {
    const status = transparencyWordNetStatus(value, comparison);
    lines.push("", `${label} [source: ${path}]`, status.label);
    if (status.executed && Array.isArray(candidates) && candidates.length === 0) lines.push("No WordNet relationship candidates were recorded for this check.");
    if (!value) lines.push("Detailed execution metadata: Not available in the cached response. Retained candidates, if any, are in the lexical evidence above.");
  };
  const directIndex = steps.findIndex((step) => step.id === "wordnet_direct_suggestions");
  const direct = steps[directIndex];
  wordnet("WordNet — direct focus suggestions", `${stagePath}.topic_service.steps (wordnet_direct_suggestions)`, direct, null, direct?.output ?? analysis.lexical_topic_evidence?.wordnet_relationship_candidates);
  const comparisonKeys = ["introduction_to_body_continuity", "introduction_to_conclusion_continuity", "body_to_conclusion_continuity"];
  let comparisons = 0;
  for (const key of comparisonKeys) {
    const comparison = analysis[key];
    if (!comparison) continue;
    comparisons++;
    record(`Complete cross-stage comparison: ${key}`, `analysis.${key}`, comparison);
    if (["NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED", "NOT_AVAILABLE_NO_BODY_SUPPLIED"].includes(comparison.status)) lines.push("Not applicable — no earlier section was supplied.");
    else if (comparison.status === "LEXICAL_COMPARISON_AVAILABLE" && comparison.direct_lexical_continuity?.length === 0 && comparison.lemma_normalized_continuity?.length === 0) lines.push("No direct or lemma matches were recorded for this check.");
    wordnet(`WordNet — ${key}`, `analysis.${key}.wordnet_relationship_candidates`, comparison.wordnet_relationship_candidates, comparison, comparison.wordnet_relationship_candidates?.suggestions);
  }
  if (!comparisons) lines.push("", stage === "INTRODUCTION" ? "Cross-stage comparison: Not applicable for Introduction." : `Cross-stage comparison: ${missing}`);

  heading("4. Rule Evaluation");
  uniqueRecords("Complete rule evaluation records: Rule IDs, status, decision basis, configuration and source references", [
    ["analysis.rule_evaluation_trace", analysis.rule_evaluation_trace],
    [`${stagePath}.rule_evaluation_trace`, stageTrace?.rule_evaluation_trace],
  ]);
  record("Every emitted Rule Event and its complete evidence, original spans and limitations", "analysis.rule_evidence", analysis.rule_evidence);
  const covered = new Set(["stage", "assignment_topic", "input_text", "linguistic_observations", "linguistic_analysis", "lexical_topic_evidence", "rule_evaluation_trace", "rule_evidence", "uncertainty", "interpretation_limit", "prohibited_conclusions", ...comparisonKeys]);
  for (const key of Object.keys(analysis).sort()) {
    if (!covered.has(key) && !ANALYSIS_REPORT_PRIVATE_KEYS.has(key.replace(/[^a-z0-9]/gi, "").toLowerCase())) record(`Stage-specific evidence: ${key}`, `analysis.${key}`, analysis[key]);
  }
  for (const key of Object.keys(stageTrace || {}).sort()) {
    if (!["linguistic_observations", "topic_service", "rule_evaluation_trace", "feedback_decisions", "input_sections"].includes(key)
      && !ANALYSIS_REPORT_PRIVATE_KEYS.has(key.replace(/[^a-z0-9]/gi, "").toLowerCase())) record(`Selected-stage trace: ${key}`, `${stagePath}.${key}`, stageTrace[key]);
  }

  heading("5. Writing Feedback");
  for (const field of ["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"]) {
    const value = result?.feedback?.[field];
    if (retainedRecords) retainedRecords.push({ label: field, path: `feedback[${JSON.stringify(field)}]`, value: analysisReportValue(value) });
    lines.push("", `${field} [source: feedback[${JSON.stringify(field)}]]`);
    if (Array.isArray(value)) {
      if (!value.length) lines.push("No items returned (recorded empty list).");
      else value.forEach((message, index) => lines.push(`${index + 1}. ${message}`));
    } else lines.push(value === undefined || value === null ? missing : String(value));
  }
  const provenance = result?.feedback?.["Feedback Provenance"];
  const exportedProvenance = Array.isArray(provenance) ? provenance.map((item) => {
    const eventIndex = analysis.rule_evidence?.findIndex((event) => event.rule_id === item.rule_id) ?? -1;
    const event = analysis.rule_evidence?.[eventIndex];
    const evidenceKey = event?.actual_evidence != null ? "actual_evidence" : "evidence";
    return Object.fromEntries(Object.entries(item).map(([key, value]) => [key,
      ["actual_evidence", "evidence"].includes(key) && event?.[evidenceKey] !== undefined
        && JSON.stringify(analysisReportValue(value)) === JSON.stringify(analysisReportValue(event[evidenceKey]))
        ? { $ref: `analysis.rule_evidence[${eventIndex}].${evidenceKey}` } : value,
    ]));
  }) : provenance;
  record("Complete feedback provenance", 'feedback["Feedback Provenance"]', exportedProvenance);
  lines.push("Rule IDs refer to the complete events in section 4. A $ref replaces only an identical event-evidence copy; any different provenance evidence is retained in full.");
  record("Recorded FeedbackService branches, selection conditions, priority order and decision trace", `${stagePath}.feedback_decisions`, stageTrace?.feedback_decisions);
  if (stageTrace?.feedback_decisions?.instructional_feedback) record("6+1 instructional mapping, observed evidence, coverage and verified highlight provenance", `${stagePath}.feedback_decisions.instructional_feedback`, stageTrace.feedback_decisions.instructional_feedback);
  record("Exact student-facing scaffolding presentation (teaching interpretation, not a new NLP decision)", "frontend.studentFeedbackPresentation (prepared catalog + selected-stage response)", studentFeedbackPresentation(result));
  for (const key of Object.keys(result?.feedback || {}).sort()) {
    if (!["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step", "Feedback Provenance"].includes(key)
      && !ANALYSIS_REPORT_PRIVATE_KEYS.has(key.replace(/[^a-z0-9]/gi, "").toLowerCase())) record(`Additional feedback metadata: ${key}`, `feedback.${key}`, result.feedback[key]);
  }

  heading("6. Algorithm Explanations and Limitations");
  lines.push("spaCy supplies linguistic predictions; EssayScaff compares lexical forms, evaluates custom deterministic rules, records evidence, and selects predefined feedback.", "Grammatical and lexical observations do not establish semantic understanding, thesis validity, reasoning quality, factual correctness, or overall essay quality.", "The implementation descriptions below explain applicable operations; execution is established only by the cached records above, not by these descriptions.");
  const explanations = ["processing:pipeline", "processing:tokenization", "processing:lemmatization", "processing:pos", "processing:dependencies", "processing:noun-chunks", "processing:concepts", "topic:overview", "topic:normalization", "topic:direct", "topic:lemma", "topic:related", "topic:wordnet", ...(stage === "INTRODUCTION" ? [] : ["topic:cross-stage"]), "rules:overview", "rules:triggered", "rules:evidence", "feedback:overview", "feedback:provenance"];
  for (const key of explanations) {
    const info = STUDENT_TRANSPARENCY_PROCESS_INFO[key];
    record(`Implementation explanation: ${key}`, `STUDENT_TRANSPARENCY_PROCESS_INFO[${JSON.stringify(key)}] (existing frontend metadata)`, { what: info.what, how: info.how, why: info.why, where: info.where || info.next, implementation: info.source, limitation: info.limitation, references: info.references });
  }
  for (const [key, explanation] of Object.entries(TRANSPARENCY_EXTRA_INFO)) record(`Implementation explanation: ${key}`, "Source-verified frontend explanation (docs/transparency_process_map.md)", explanation);
  for (const key of ["uncertainty", "interpretation_limit", "prohibited_conclusions"]) {
    if (analysis[key] !== undefined) record(`Recorded stage limits: ${key}`, `analysis.${key}`, analysis[key]);
  }
  record("Recorded trace limitations", "research_trace.limitations", trace?.limitations);
  const runtimeKeys = ["trace_version", "runtime", "teacher_context_preparation_ms", "teacher_context_call_frequency", "request_validation_and_assignment_resolution_ms", "analysis_service_lookup_ms", "analysis_service_total_ms", "api_authentication_and_csrf_timing", "json_response_serialization_timing"];
  record("Available runtime and request instrumentation", "research_trace (listed technical metadata only)", trace ? Object.fromEntries(runtimeKeys.filter((key) => trace[key] !== undefined).map((key) => [key, trace[key]])) : undefined);
  lines.push("", "END OF FULL ANALYSIS");
  return lines.join("\n");
}

function currentAnalysisForExport() {
  const stage = state.currentStage;
  const result = state.analyses[stage];
  return state.activeAppView === "workspace" && state.currentView === stage && !state.restoring
    && result?.stage_id === stage && result.availability === "ANALYZED" && result.analysis && result.feedback
    && writingInput.value === state.drafts[stage]
    && state.analysisSnapshots[stage] === analysisSnapshot(stage) ? result : null;
}

function updateAnalysisExport() {
  analysisCopyGeneration++;
  analysisCopyFallback.hidden = true;
  fullAnalysisReport.value = "";
  const current = currentAnalysisForExport();
  copyFullAnalysisButton.disabled = !current || analysisCopyInProgress;
  analysisCopyStatus.textContent = analysisCopyInProgress
    ? "The draft or context changed during copying. Any copy already started describes the earlier analysis."
    : current ? "Current analysis ready to copy." : "Analyze the current draft first to copy its full analysis.";
}

function selectScaffoldingGuidance(result) {
  // A lookup of the selected, recorded feedback branch — never a new detector or
  // a reconstruction of FeedbackService's priorities from writing observations.
  if (![5, 6].includes(scaffoldingCatalog?.version) || scaffoldingCatalog.availability === "UNAVAILABLE"
    || result?.availability !== "ANALYZED" || !result.analysis || !result.feedback) return null;
  const stage = result.stage_id;
  const field = "Primary Feedback";
  if (result.research_trace?.selected_stage !== stage) return null;
  const decision = result.research_trace?.stages?.[stage]?.feedback_decisions?.fields?.[field];
  if (!decision?.selection_branch || typeof result.feedback[field] !== "string" || !result.feedback[field]
    || decision.selected_message !== result.feedback[field] || !Array.isArray(decision.rule_ids) || !decision.rule_ids.length) return null;
  const binding = scaffoldingCatalog.bindings?.find((item) => item.stage_id === stage
    && item.feedback_field === field && item.selection_branch === decision.selection_branch);
  const content = binding && scaffoldingCatalog.lessons?.find((item) => item.lesson_id === binding.lesson_id);
  if (!content?.inline_guidance || !TUTOR_TRAITS.includes(binding.dimension) || !binding.skill || !binding.mapping_basis) return null;
  const events = result.analysis.rule_evidence;
  const provenance = result.feedback["Feedback Provenance"];
  if (!Array.isArray(events) || !Array.isArray(provenance)) return null;
  const ruleIds = [...new Set(decision.rule_ids)];
  if (binding.required_rule_ids && (!Array.isArray(binding.required_rule_ids)
    || !binding.required_rule_ids.every((id) => ruleIds.includes(id)))) return null;
  if (binding.required_any_rule_ids && !binding.required_any_rule_ids.some(id => ruleIds.includes(id))) return null;
  if (!ruleIds.every((id) => events.some((event) => event.rule_id === id && event.triggered !== false && event.fired !== false)
    && provenance.some((item) => item.feedback_field === field && item.rule_id === id))) return null;
  const instructional = stage === "BODY" ? bodyInstructionalItem(result, field, ruleIds, content.lesson_id) : introductionInstructionalItem(result, field, ruleIds, content.lesson_id);
  if (stage === "INTRODUCTION" && result.research_trace?.stages?.INTRODUCTION?.feedback_decisions?.instructional_feedback && !instructional) return null;
  if (stage === "BODY" && result.research_trace?.stages?.BODY?.feedback_decisions?.instructional_feedback && !instructional) return null;
  if (stage === "INTRODUCTION" && instructional && !content.tutor.marker_notes && ["noticed", "why", "task"].some(key => instructional.prepared_guidance?.[key] !== content.tutor[key])) return null;
  return { result, stage, field, branch: decision.selection_branch, ruleIds, binding, content, instructional };
}

function introductionInstructionalItem(result, field, ruleIds, lessonId) {
  if (result?.stage_id !== "INTRODUCTION" || result.research_trace?.selected_stage !== "INTRODUCTION") return null;
  const trace = result.research_trace.stages?.INTRODUCTION?.feedback_decisions;
  const record = trace?.instructional_feedback?.items?.find(item => item.feedback_field === field
    && item.lesson_id === lessonId && JSON.stringify(item.rule_ids) === JSON.stringify(ruleIds));
  const decision = trace?.fields?.[field];
  if (!record || record.selection_branch !== decision?.selection_branch || record.catalog_reference?.version !== scaffoldingCatalog.version) return null;
  if (!ruleIds.every(id => decision.rule_ids?.includes(id)
    && result.analysis?.rule_evidence?.some(e => e.rule_id === id && e.triggered !== false && e.fired !== false)
    && result.feedback?.["Feedback Provenance"]?.some(p => p.feedback_field === field && p.rule_id === id))) return null;
  const binding = field === "Primary Feedback" ? scaffoldingCatalog.bindings?.find(b => b.selection_branch === record.selection_branch && b.stage_id === "INTRODUCTION")
    : scaffoldingCatalog.secondary_bindings?.find(b => b.stage_id === "INTRODUCTION" && b.lesson_id === lessonId && ruleIds.some(id => new RegExp(b.rule_id_pattern).test(id)));
  if (!binding || binding.dimension !== record.trait || binding.skill !== record.skill || binding.lesson_id !== record.lesson_id) return null;
  return record;
}

function bodyInstructionalItem(result, field, ruleIds, lessonId) {
  if (result?.stage_id !== "BODY" || result.research_trace?.selected_stage !== "BODY") return null;
  const trace = result.research_trace.stages?.BODY?.feedback_decisions;
  const record = trace?.instructional_feedback?.items?.find(item => item.feedback_field === field
    && item.lesson_id === lessonId && JSON.stringify(item.rule_ids) === JSON.stringify(ruleIds));
  if (!record || record.selection_branch !== trace.fields?.[field]?.selection_branch
    || record.catalog_reference?.version !== scaffoldingCatalog.version || !Array.isArray(record.paragraph_indices)
    || !ruleIds.every(id => result.analysis.rule_evidence?.some(e => e.rule_id === id && e.triggered !== false && e.fired !== false)
      && result.feedback?.["Feedback Provenance"]?.some(p => p.feedback_field === field && p.rule_id === id))) return null;
  const binding = field === "Primary Feedback" ? scaffoldingCatalog.bindings?.find(b => b.stage_id === "BODY" && b.selection_branch === record.selection_branch)
    : scaffoldingCatalog.secondary_bindings?.find(b => b.stage_id === "BODY" && b.lesson_id === lessonId && ruleIds.some(id => new RegExp(b.rule_id_pattern).test(id)));
  if (!binding || record.trait !== binding.dimension || record.skill !== binding.skill || record.lesson_id !== binding.lesson_id
    || (field === "Primary Feedback" && record.selected_message !== result.feedback["Primary Feedback"])) return null;
  return record;
}

function bodyRecordedStrengthText(result, record) {
  const source = tutorSourceText(result)?.source;
  if (!Array.isArray(record?.strengths) || record.strengths.length > 2) return "";
  return record.strengths.filter(strength => typeof strength.text === "string" && strength.rule_ids?.length
    && strength.rule_ids.every(id => result.feedback?.["Feedback Provenance"]?.some(p => p.feedback_field === "What's Working" && p.rule_id === id)
      && result.analysis.rule_evidence?.some(e => e.rule_id === id && e.triggered !== false && e.fired !== false))
    && strength.source_positions?.length === strength.rule_ids.length
    && strength.source_positions.every(entry => entry.positions?.length && entry.positions.every(position => {
      const event = result.analysis.rule_evidence.find(e => e.rule_id === entry.rule_id);
      const raw = (event?.actual_evidence ?? event?.evidence)?.[position.evidence_index];
      const bounds = raw?.sentence_span;
      return tutorVerifiedSpan(source, position) && (Array.isArray(bounds)
        ? bounds[0] === position.start && bounds[1] === position.end && raw.sentence_text === position.text
        : raw?.start === position.start && raw?.end === position.end && (raw.text ?? raw.observed_text) === position.text);
    }))).map(strength => strength.text).join("\n");
}

function selectBodyRecordedTutorItems(result) {
  const trace = result?.research_trace?.stages?.BODY?.feedback_decisions;
  const record = trace?.instructional_feedback;
  if (result?.stage_id !== "BODY" || result.research_trace?.selected_stage !== "BODY" || record?.stage !== "BODY") return null;
  const decision = trace.fields?.["Primary Feedback"];
  if (record.selection_status !== trace.selection_status || record.selection_branch !== decision?.selection_branch
    || record.student_message !== result.feedback?.["Primary Feedback"] || decision.selected_message !== record.student_message) return null;
  const working = bodyRecordedStrengthText(result, record);
  if (record.selection_status === "NO_SUPPORTED_CONCERN_SELECTED" && record.neutral_result && !record.items.length
    && !record.selection_checks.some(check => check.status === "SELECTED")) {
    return [{ role: "NO_SUPPORTED_CONCERN_SELECTED", category: null, label: record.neutral_result.label, skill: null, lesson_id: null,
      rule_ids: decision.rule_ids, noticed: record.student_message, working_text: working, feedback_purpose: "NO_SUPPORTED_CONCERN_SELECTED",
      highlight_provenance: [], evidence_text: "", why: "", task_text: "", limitation: record.neutral_result.limitation, excerpt: null }];
  }
  const items = [];
  for (const entry of record.items || []) {
    const instructional = bodyInstructionalItem(result, entry.feedback_field, entry.rule_ids, entry.lesson_id);
    const binding = entry.feedback_field === "Primary Feedback" ? scaffoldingCatalog.bindings?.find(b => b.stage_id === "BODY" && b.selection_branch === entry.selection_branch)
      : scaffoldingCatalog.secondary_bindings?.find(b => b.stage_id === "BODY" && b.lesson_id === entry.lesson_id && entry.rule_ids.some(id => new RegExp(b.rule_id_pattern).test(id)));
    const content = scaffoldingCatalog.lessons?.find(lesson => lesson.lesson_id === entry.lesson_id);
    if (instructional && binding && content) {
      const item = buildTutorItem({ result, binding, content, ruleIds: entry.rule_ids, instructional });
      item.working_text = working;
      items.push(item);
    }
  }
  if (items.length && record.items[0]?.feedback_field === "Primary Feedback" && items[0].lesson_id === record.items[0].lesson_id) return items;
  // Unavailable/corrupt mappings do not manufacture a new lesson or error span.
  return [{ role: "RECORDED_BODY_FEEDBACK", category: null, label: "Recorded Body feedback", skill: null, lesson_id: null,
    rule_ids: decision.rule_ids || [], noticed: record.student_message, working_text: working, feedback_purpose: null,
    highlight_provenance: [], evidence_text: "", why: "", task_text: "", limitation: record.limitations?.[0] || "", excerpt: null }];
}

function tutorInstructionalExcerpt(result, record, source, linguistic) {
  // Verify a backend-selected localization plan against its SAME raw event and
  // original source. This validates provenance; it does not select a branch.
  if (!Array.isArray(record?.highlight_spans) || !record.highlight_spans.length) return null;
  const contexts = [];
  for (const plan of record.highlight_spans) {
    if (!record.rule_ids.includes(plan.rule_id)) return null;
    const events = result.analysis.rule_evidence?.filter(e => e.rule_id === plan.rule_id && e.triggered !== false && e.fired !== false);
    const evidence = events?.length === 1 ? events[0].actual_evidence ?? events[0].evidence : null;
    let anchor = Number.isInteger(plan.evidence_index) && Array.isArray(evidence) ? evidence[plan.evidence_index] : null;
    for (const key of plan.anchor_path || []) anchor = anchor?.[key];
    if (!anchor || anchor[plan.anchor_start_field] !== plan.anchor?.start || anchor[plan.anchor_end_field] !== plan.anchor?.end) return null;
    const anchorText = anchor.text ?? anchor.observed_text;
    if (typeof anchorText === "string" && anchorText !== plan.anchor.text) return null;
    const verifiedAnchor = tutorVerifiedSpan(source, plan.anchor), mark = tutorVerifiedSpan(source, plan);
    const context = tutorVerifiedSpan(source, plan.context);
    const bodyParagraph = result.stage_id === "BODY" && plan.context_kind === "paragraph"
      ? result.analysis.paragraphs?.find(p => p.paragraph_index === plan.context?.paragraph_index && record.paragraph_indices?.includes(p.paragraph_index)) : null;
    const sentence = bodyParagraph ? tutorVerifiedSpan(source, bodyParagraph)
      : Number.isInteger(plan.context?.sentence_index) ? tutorVerifiedSpan(source, linguistic?.sentences?.[plan.context.sentence_index]) : null;
    if (!verifiedAnchor || !mark || !context || !sentence || context.start !== sentence.start || context.end !== sentence.end
      || context.start > mark.start || mark.end > context.end || context.start > verifiedAnchor.start || verifiedAnchor.end > context.end) return null;
    const item = evidence[plan.evidence_index];
    if (item.sentence_start !== undefined && (item.sentence_start !== sentence.start || item.sentence_end !== sentence.end || item.sentence_text !== sentence.text)) return null;
    if (plan.kind === "main_statement" && (!Array.isArray(item.subject_evidence) || !item.subject_evidence.length
      || !item.subject_evidence.every(s => tutorVerifiedSpan(source, s) && s.start >= sentence.start && s.end <= sentence.end))) return null;
    if (plan.kind === "body_statement_to_develop") {
      const statement = bodyParagraph?.clause_structure_candidates?.[0];
      if (!statement || statement.sentence_span?.[0] !== mark.start || statement.sentence_span?.[1] !== mark.end
        || statement.sentence_text !== mark.text || !statement.subject_evidence?.length
        || !tutorVerifiedSpan(source, statement.predicate_evidence) || !statement.subject_evidence.every(s => tutorVerifiedSpan(source, s))) return null;
    }
    if (plan.rule_id === "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW" && !result.analysis.sentence_topic_evidence?.review_candidates?.some(r => r.review_signal && r.start === mark.start && r.end === mark.end && r.text === mark.text)) return null;
    const existing = contexts.find(c => c.start === context.start && c.end === context.end);
    if (existing) existing.marks.push([mark.start, mark.end]);
    else contexts.push({ start: context.start, end: context.end, marks: [[mark.start, mark.end]] });
  }
  return { source, contexts };
}

function verifiedScaffoldingSubordinator(result) {
  // Python offsets count Unicode code points, not JavaScript UTF-16 units.
  // Name a marker only when one emitted evidence item agrees with the source,
  // recorded token, sentence span and stage finding. Never choose among markers.
  const ruleId = "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR";
  const analysis = result?.analysis;
  const linguistic = analysis?.linguistic_observations;
  // The student API removes duplicate input_text; linguistic.text is the
  // exact analyzed input retained in that response.
  const source = linguistic?.text;
  if (typeof source !== "string" || (analysis.input_text !== undefined && analysis.input_text !== source)
    || !Array.isArray(linguistic.tokens) || !Array.isArray(linguistic.sentences)) return null;
  const events = analysis.rule_evidence?.filter((event) => event.rule_id === ruleId && event.triggered !== false && event.fired !== false);
  if (events?.length !== 1) return null;
  const evidence = events[0].actual_evidence ?? events[0].evidence;
  const findings = analysis.observable_structure?.incomplete_subordinator_candidates;
  if (!Array.isArray(evidence) || evidence.length !== 1 || !Array.isArray(findings) || findings.length !== 1) return null;
  const item = evidence[0];
  const characters = Array.from(source);
  if (!item || typeof item.text !== "string" || !item.text || item.pos !== "SCONJ"
    || !Number.isInteger(item.start) || !Number.isInteger(item.end) || item.start < 0 || item.end <= item.start || item.end > characters.length
    || characters.slice(item.start, item.end).join("") !== item.text) return null;
  const sentence = Number.isInteger(item.sentence_index) && linguistic.sentences?.[item.sentence_index];
  const token = linguistic.tokens?.find((token) => token.start === item.start && token.end === item.end);
  const finding = findings[0];
  if (!sentence || item.start < sentence.start || item.end > sentence.end
    || !token || token.text !== item.text || token.pos !== "SCONJ" || token.dependency !== item.dependency
    || !finding || finding.text !== item.text || finding.start !== item.start || finding.end !== item.end
    || finding.sentence_index !== item.sentence_index || finding.pos !== item.pos || finding.dependency !== item.dependency) return null;
  return { rule_id: ruleId, text: item.text, start: item.start, end: item.end, sentence_index: item.sentence_index };
}

function tutorSourceText(result) {
  // The analyzed section text, taken only from recorded analysis fields that
  // agree with each other. Python offsets count Unicode code points.
  const analysis = result?.analysis || {};
  const stage = result?.stage_id;
  const stageTrace = result?.research_trace?.stages?.[stage] || null;
  const linguistic = analysis.linguistic_observations || stageTrace?.linguistic_observations || null;
  const candidates = [linguistic?.text, analysis.input_text].filter((value) => typeof value === "string");
  if (!candidates.length) return null;
  if (candidates.some((value) => value !== candidates[0])) return null;
  return { source: candidates[0], linguistic };
}

function tutorVerifiedSpan(source, span) {
  if (typeof source !== "string" || !span || typeof span !== "object"
    || !Number.isInteger(span.start) || !Number.isInteger(span.end)
    || span.start < 0 || span.end <= span.start) return null;
  const characters = Array.from(source);
  if (span.end > characters.length) return null;
  const text = characters.slice(span.start, span.end).join("");
  if (typeof span.text === "string" && span.text !== text) return null;
  return { start: span.start, end: span.end, text };
}

function tutorSentenceForSpan(source, linguistic, span) {
  if (!Array.isArray(linguistic?.sentences)) return null;
  for (const candidate of linguistic.sentences) {
    const verified = tutorVerifiedSpan(source, candidate);
    if (verified && verified.start <= span.start && span.end <= verified.end) return verified;
  }
  return null;
}

function tutorEvidenceExcerpt(result, ruleIds, source, linguistic) {
  // Build highlighted contexts only from recorded, verified offsets. Any
  // invalid span fails closed and returns no highlight at all.
  const analysis = result?.analysis || {};
  const events = (Array.isArray(analysis.rule_evidence) ? analysis.rule_evidence : [])
    .filter((event) => ruleIds.includes(event.rule_id) && event.triggered !== false && event.fired !== false);
  if (result?.stage_id === "INTRODUCTION" && ruleIds.includes("INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW")) {
    // Highlight one recorded sentence, never every zero-match sentence or the section.
    const records = events.filter(e => e.rule_id === "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW");
    const evidence = records.length === 1 ? records[0].actual_evidence ?? records[0].evidence : null;
    const target = Array.isArray(evidence) ? evidence[0] : null;
    const sentence = tutorVerifiedSpan(source, target);
    const recorded = Number.isInteger(target?.sentence_index)
      ? tutorVerifiedSpan(source, linguistic?.sentences?.[target.sentence_index]) : null;
    const finding = analysis.sentence_topic_evidence?.review_candidates?.find(r => r.sentence_index === target?.sentence_index);
    if (!sentence || !recorded || !finding?.review_signal || finding.status !== "POSSIBLE_CONNECTION_GAP"
      || sentence.start !== recorded.start || sentence.end !== recorded.end
      || sentence.start !== finding.start || sentence.end !== finding.end || sentence.text !== finding.text) return null;
    return { source, contexts: [{ start: sentence.start, end: sentence.end, marks: [[sentence.start, sentence.end]] }] };
  }
  // These Introduction branches cite both an observed clause and a development
  // record (present or absent). Only the observed clause supplies a source
  // location; the development rule is structural and has no span of its own.
  const clauseRule = "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE";
  const clauseSupportedDevRules = [
    "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE",
    "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES",
    "INTRO.REASON.NO_CLAUSE_TOPIC_OVERLAP",
    "INTRO.REASON.CLAUSE_TOPIC_OVERLAP",
  ];
  const reasonOverlapRule = "INTRO.REASON.CLAUSE_TOPIC_OVERLAP";
  const reasonNoOverlapRule = "INTRO.REASON.NO_CLAUSE_TOPIC_OVERLAP";
  if (result?.stage_id === "INTRODUCTION" && (ruleIds.includes(reasonOverlapRule) || ruleIds.includes(reasonNoOverlapRule))) {
    const reasonEvent = events.find((event) => event.rule_id === reasonOverlapRule || event.rule_id === reasonNoOverlapRule);
    const clauses = reasonEvent ? (reasonEvent.actual_evidence ?? reasonEvent.evidence) : null;
    if (!Array.isArray(clauses) || !clauses.length) return null;
    const target = clauses[0];
    const sentence = tutorVerifiedSpan(source, {
      start: target?.sentence_start, end: target?.sentence_end, text: target?.sentence_text,
    });
    const recorded = Number.isInteger(target?.sentence_index)
      ? tutorVerifiedSpan(source, linguistic?.sentences?.[target.sentence_index]) : null;
    if (!sentence || !recorded || sentence.start !== recorded.start || sentence.end !== recorded.end) return null;
    let marks = [];
    if (Number.isInteger(target?.clause_start) && Number.isInteger(target?.clause_end)
      && target.clause_start >= sentence.start && target.clause_end <= sentence.end && target.clause_start < target.clause_end) {
      const clauseSpan = tutorVerifiedSpan(source, { start: target.clause_start, end: target.clause_end });
      if (clauseSpan) marks.push([clauseSpan.start, clauseSpan.end]);
    }
    if (!marks.length) {
      marks.push([sentence.start, sentence.end]);
    }
    return { source, contexts: [{ start: sentence.start, end: sentence.end, marks }] };
  }
  if (result?.stage_id === "INTRODUCTION" && ruleIds.includes(clauseRule)
    && ruleIds.every((id) => [clauseRule, ...clauseSupportedDevRules].includes(id))) {
    const clauseEvents = events.filter((event) => event.rule_id === clauseRule);
    if (clauseEvents.length !== 1) return null;
    const candidates = clauseEvents[0].actual_evidence ?? clauseEvents[0].evidence;
    if (!Array.isArray(candidates) || !candidates.length) return null;
    const contexts = [];
    for (const candidate of candidates) {
      const sentence = tutorVerifiedSpan(source, {
        start: candidate?.sentence_start, end: candidate?.sentence_end, text: candidate?.sentence_text,
      });
      const recorded = Number.isInteger(candidate?.sentence_index)
        ? tutorVerifiedSpan(source, linguistic?.sentences?.[candidate.sentence_index]) : null;
      const predicate = tutorVerifiedSpan(source, candidate?.predicate_evidence);
      const subjects = candidate?.subject_evidence;
      if (!sentence || typeof candidate.sentence_text !== "string" || !recorded
        || sentence.start !== recorded.start || sentence.end !== recorded.end
        || !predicate || predicate.start < sentence.start || predicate.end > sentence.end
        || !Array.isArray(subjects) || !subjects.length
        || !subjects.every((subject) => tutorVerifiedSpan(source, subject)
          && subject.start >= sentence.start && subject.end <= sentence.end)) return null;
      if (!contexts.some((entry) => entry.start === sentence.start && entry.end === sentence.end)) {
        contexts.push({ start: sentence.start, end: sentence.end, marks: [[sentence.start, sentence.end]] });
      }
    }
    return { source, contexts: contexts.sort((a, b) => a.start - b.start) };
  }
  if (events.length !== 1) return null;
  const evidence = events[0].actual_evidence ?? events[0].evidence;
  if (!Array.isArray(evidence) || !evidence.length) return null;
  const contexts = [];
  for (const item of evidence) {
    if (!item || typeof item !== "object") return null;
    if (Array.isArray(item.paragraph_pair)) {
      const paragraphs = Array.isArray(analysis.paragraphs) ? analysis.paragraphs : [];
      for (const index of item.paragraph_pair) {
        const paragraph = paragraphs.find((entry) => entry?.paragraph_index === index);
        const verified = tutorVerifiedSpan(source, paragraph);
        if (!verified) return null;
        contexts.push({ start: verified.start, end: verified.end, marks: [] });
      }
      continue;
    }
    let span = null;
    if (Array.isArray(item.occurrences)) {
      if (!item.occurrences.length) return null;
      for (const occurrence of item.occurrences) {
        const verified = tutorVerifiedSpan(source, occurrence);
        if (!verified) return null;
        const sentence = tutorSentenceForSpan(source, linguistic, verified);
        const context = sentence || verified;
        const existing = contexts.find((entry) => entry.start === context.start && entry.end === context.end);
        if (existing) existing.marks.push([verified.start, verified.end]);
        else contexts.push({ start: context.start, end: context.end, marks: [[verified.start, verified.end]] });
      }
      continue;
    }
    if (Number.isInteger(item.sentence_index) && Number.isInteger(item.start) && Number.isInteger(item.end)) {
      // Token-level evidence with a recorded sentence: highlight the verified
      // sentence span only when it contains the verified token.
      const token = tutorVerifiedSpan(source, item);
      const sentenceRecord = Array.isArray(linguistic?.sentences) ? linguistic.sentences[item.sentence_index] : null;
      const sentence = tutorVerifiedSpan(source, sentenceRecord);
      if (!token || !sentence || sentence.start > token.start || token.end > sentence.end) return null;
      contexts.push({ start: sentence.start, end: sentence.end, marks: [[token.start, token.end]] });
      continue;
    }
    if (Number.isInteger(item.start) && Number.isInteger(item.end)) {
      span = tutorVerifiedSpan(source, item);
      if (!span) return null;
      const sentence = tutorSentenceForSpan(source, linguistic, span);
      const context = sentence || span;
      const existing = contexts.find((entry) => entry.start === context.start && entry.end === context.end);
      if (existing) existing.marks.push([span.start, span.end]);
      else contexts.push({ start: context.start, end: context.end, marks: [[span.start, span.end]] });
      continue;
    }
    return null;
  }
  if (!contexts.length) return null;
  contexts.sort((a, b) => a.start - b.start);
  return { source, contexts };
}

function fillTutorTemplate(template, slots) {
  let text = template;
  for (const [key, value] of Object.entries(slots)) {
    text = text.split(`{${key}}`).join(value ?? "");
  }
  return text;
}

function tutorIntroductionVocabularySummary(result, ruleIds) {
  if (result?.stage_id !== "INTRODUCTION" || !ruleIds?.includes("INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED")) return null;
  const events = result.analysis?.rule_evidence;
  if (!Array.isArray(events) || events.filter((event) => event.rule_id === "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED"
    && event.triggered !== false && event.fired !== false).length !== 1) return null;
  const lexical = result.analysis?.lexical_topic_evidence;
  const terms = lexical?.focus_terms;
  const observed = lexical?.observed_focus_terms;
  const missing = lexical?.unobserved_focus_terms;
  // Display returned measurements, never re-match words in the student's text.
  if (!Array.isArray(terms) || !terms.length || !terms.every((term) => typeof term === "string" && term.trim())
    || new Set(terms).size !== terms.length || !Array.isArray(observed) || observed.length
    || !Array.isArray(missing) || missing.length !== terms.length
    || !terms.every((term) => missing.includes(term))
    || lexical.observed_unique_focus_terms !== 0 || lexical.total_unique_focus_terms !== terms.length
    || !Array.isArray(lexical.matches) || lexical.matches.length) {
    return "Whole-Introduction vocabulary check: no direct or lemma match was reported. Detailed focus-term counts are unavailable or inconsistent in this analysis. Compare your opening with the assignment question; this absence finding has no source passage to highlight.";
  }
  return `Whole Introduction: ${lexical.observed_unique_focus_terms} of ${lexical.total_unique_focus_terms} configured focus terms observed (direct or lemma matches).\nTerms not observed: ${missing.join(", ")}.\nThis is a wording summary, not a judgment of relevance. No individual passage is highlighted for a whole-section absence.`;
}

function tutorBodyParagraphForRule(result, ruleIds, source) {
  if (result?.stage_id !== "BODY" || !Array.isArray(ruleIds) || ruleIds.length !== 1) return null;
  const match = /^BODY\.P(\d+)\.SUPPORTING_DETAIL\.NOT_OBSERVED$/.exec(ruleIds[0]);
  if (!match) return null;
  const paragraph = result.analysis?.paragraphs?.find((item) => item.paragraph_index === Number(match[1]));
  const events = result.analysis?.rule_evidence?.filter((event) => event.rule_id === ruleIds[0] && event.triggered !== false);
  const evidence = events?.length === 1 ? events[0].actual_evidence ?? events[0].evidence : null;
  if (!tutorVerifiedSpan(source, paragraph) || !Number.isInteger(paragraph.counts?.sentence_count)
    || paragraph.counts.sentence_count < 1 || !Array.isArray(evidence) || evidence.length !== 1
    || !tutorVerifiedSpan(source, evidence[0]) || evidence[0].start !== paragraph.start || evidence[0].end !== paragraph.end) return null;
  return paragraph;
}

function tutorBodyOverview(result, ruleIds, source) {
  const decision = result?.research_trace?.stages?.BODY?.feedback_decisions?.fields?.["Primary Feedback"];
  if (result?.stage_id !== "BODY" || decision?.selection_branch !== "body_neutral_observable"
    || decision.selected_message !== result.feedback?.["Primary Feedback"]) return null;
  const paragraphs = result.analysis?.paragraphs;
  if (!Array.isArray(paragraphs) || !paragraphs.length) return null;
  const events = result.analysis?.rule_evidence || [];
  const summaries = [];
  for (const paragraph of paragraphs) {
    const id = `BODY.P${paragraph.paragraph_index}.PARAGRAPH.SEGMENTED`;
    const event = events.filter((item) => item.rule_id === id && item.triggered !== false);
    const evidence = event.length === 1 ? event[0].actual_evidence ?? event[0].evidence : null;
    const count = paragraph.counts?.sentence_count;
    if (!ruleIds.includes(id) || !tutorVerifiedSpan(source, paragraph) || !Number.isInteger(count) || count < 0
      || !Array.isArray(evidence) || evidence.length !== 1 || !tutorVerifiedSpan(source, evidence[0])
      || evidence[0].start !== paragraph.start || evidence[0].end !== paragraph.end) return null;
    summaries.push(`Paragraph ${paragraph.paragraph_index}: ${count} recorded ${count === 1 ? "sentence" : "sentences"}.`);
  }
  const contextAvailable = result.analysis.introduction_to_body_continuity?.status === "LEXICAL_COMPARISON_AVAILABLE";
  return {
    noticed: "The available checks did not identify a specific structural concern in this Body section.",
    evidence: summaries.join("\n") + (contextAvailable ? "\nIntroduction context was compared with the Body." : "\nNo Introduction context was available for comparison."),
  };
}

// Recorded branches whose own backend wording is a neutral review, not a
// specific concern. Guidance must not turn these into revision warnings.
const STAGE_PROGRESS_NEUTRAL_BRANCHES = {
  INTRODUCTION: ["intro_ideas_point_and_reason", "intro_ideas_review_details"],
  BODY: ["body_neutral_observable"],
  CONCLUSION: ["conclusion_ideas_bring_together", "conclusion_organization_clear_ending", "conclusion_neutral_general"],
};

function recordedPrimaryFeedbackBranch(result) {
  const decision = result?.research_trace?.stages?.[result?.stage_id]?.feedback_decisions;
  return decision?.fields?.["Primary Feedback"]?.selection_branch
    || (Array.isArray(decision?.instructional_feedback?.items) ? decision.instructional_feedback.items[0]?.selection_branch : null);
}

function recordedNeutralSelection(result, selection) {
  // Reuse the validated prepared-guidance lookup so a damaged or contradictory
  // record falls back to the original feedback instead of inventing a neutral result.
  const chosen = arguments.length > 1 ? selection : selectScaffoldingGuidance(result);
  const branches = STAGE_PROGRESS_NEUTRAL_BRANCHES[result?.stage_id] || [];
  return Boolean(chosen?.branch && branches.includes(chosen.branch));
}

function recordedWorkingObservation(result, ruleIds) {
  // Surface only a recorded positive tied to the same fired rule. The feedback
  // list and provenance are index-aligned; refuse records that do not match.
  const messages = result?.feedback?.["What's Working"];
  const provenance = result?.feedback?.["Feedback Provenance"];
  if (!Array.isArray(messages) || !Array.isArray(provenance)) return "";
  const working = provenance.filter((item) => item?.feedback_field === "What's Working");
  if (working.length !== messages.length) return "";
  const ids = new Set(Array.isArray(ruleIds) ? ruleIds : []);
  const index = working.findIndex((item) => ids.has(item?.rule_id));
  return index >= 0 && typeof messages[index] === "string" ? messages[index] : "";
}

function buildTutorItem({ result, binding, content, ruleIds, message, marker, clause, observedMessage, instructional = null }) {
  // One prepared lesson rendered through the existing tutoring sections. Slots are
  // filled only from verified evidence; otherwise the recorded observation text
  // is used instead of an invented detail.
  const tutor = content?.tutor || null;
  const feedback = result?.feedback || {};
  const sourceData = tutorSourceText(result);
  const source = sourceData?.source || null;
  const linguistic = sourceData?.linguistic || null;
  const editorMatches = typeof source === "string" && writingInput.value === source;
  const recordedIntro = result?.stage_id === "INTRODUCTION" && result.research_trace?.stages?.INTRODUCTION?.feedback_decisions?.instructional_feedback;
  const recordedBody = result?.stage_id === "BODY" && result.research_trace?.stages?.BODY?.feedback_decisions?.instructional_feedback;
  const recordedPlan = recordedIntro || recordedBody;
  let excerpt = null;
  if (editorMatches && source && Array.isArray(ruleIds) && ruleIds.length) {
    if (recordedPlan) excerpt = binding && instructional ? tutorInstructionalExcerpt(result, instructional, source, linguistic) : null;
    else if (marker && Number.isInteger(marker.sentence_index) && Array.isArray(linguistic?.sentences)) {
      const sentenceRecord = linguistic.sentences[marker.sentence_index];
      const sentence = tutorVerifiedSpan(source, sentenceRecord);
      const token = tutorVerifiedSpan(source, marker);
      if (sentence && token && sentence.start <= token.start && token.end <= sentence.end) {
        excerpt = { source, contexts: [{ start: sentence.start, end: sentence.end, marks: [[sentence.start, sentence.end]] }] };
      }
    }
    if (!recordedPlan && !excerpt) excerpt = tutorEvidenceExcerpt(result, ruleIds, source, linguistic);
  }
  const slots = {
    marker: marker?.text || "",
    clause: clause || "",
    opening: "",
    observed: typeof observedMessage === "string" ? observedMessage : "",
    sentence_observation: linguistic?.counts?.sentence_count === 1 ? "Your Introduction contains one recorded sentence. " : "",
  };
  if (!slots.opening) {
    const events = (result?.analysis?.rule_evidence || [])
      .filter((event) => Array.isArray(ruleIds) && ruleIds.includes(event.rule_id) && event.triggered !== false && event.fired !== false);
    const evidence = events.length === 1 && Array.isArray(events[0].actual_evidence ?? events[0].evidence)
      ? (events[0].actual_evidence ?? events[0].evidence) : [];
    const openingEvent = evidence.find((entry) => typeof entry?.opening === "string" && entry.opening
      && Array.isArray(entry.occurrences) && entry.occurrences.length
      && entry.occurrences.every((occurrence) => tutorVerifiedSpan(source, occurrence)));
    if (openingEvent) slots.opening = openingEvent.opening;
  }
  const needsUnverifiedSlot = tutor && /\{(marker|clause|opening)\}/.test(`${tutor.noticed}${tutor.why}${tutor.task}`)
    && ((tutor.noticed.includes("{marker}") && !slots.marker)
      || (tutor.noticed.includes("{opening}") && !slots.opening)
      || (tutor.task.includes("{clause}") && !slots.clause));
  const fallbackNotice = binding?.noticed || feedback["Primary Feedback"] || "No observation reported.";
  let noticed = tutor ? fillTutorTemplate(tutor.noticed, slots) : fallbackNotice;
  if (needsUnverifiedSlot) noticed = fallbackNotice;
  let why = tutor
    ? (marker && tutor.marker_notes?.[marker.text.toLowerCase()]
      ? tutor.marker_notes[marker.text.toLowerCase()]
      : fillTutorTemplate(tutor.why, slots))
    : "Read the recorded feedback alongside the assignment question. These checks do not assess the meaning or quality of your answer.";
  let taskText;
  if (tutor?.task?.includes("{clause}")) {
    taskText = slots.clause ? fillTutorTemplate(tutor.task, slots) : (tutor.task_fallback || fillTutorTemplate(tutor.task, slots));
  } else if (tutor) {
    // A task that refers to a highlighted passage is valid only when a verified
    // excerpt exists; otherwise use the lesson's prepared general guidance.
    const highlightDependent = /\bhighlighted\b/i.test(tutor.task) && !excerpt;
    taskText = highlightDependent && tutor.task_fallback ? tutor.task_fallback : fillTutorTemplate(tutor.task, slots);
  } else {
    taskText = feedback["Next Step"] || "Reread this section and revise it in your own words if needed.";
  }
  const bodyParagraph = !recordedBody && content?.lesson_id === "HELP-BODY-DEVELOP-POINT" ? tutorBodyParagraphForRule(result, ruleIds, source) : null;
  if (bodyParagraph) {
    noticed = bodyParagraph.counts.sentence_count === 1
      ? `Paragraph ${bodyParagraph.paragraph_index} contains one recorded sentence. The checks did not identify an additional sentence part developing this paragraph.`
      : `In Paragraph ${bodyParagraph.paragraph_index}, the checks did not identify an additional sentence-part pattern for development. Other kinds of support may still be present.`;
  }
  const overview = !binding ? tutorBodyOverview(result, ruleIds, source) : null;
  let limitation = tutor ? tutor.limitation : (feedback.interpretation_limit ? `Limits of these checks: ${feedback.interpretation_limit}` : "");
  if (overview) {
    noticed = overview.noticed;
    excerpt = null; // Segmentation is neutral evidence, not a diagnosed problem.
    why = "";
    taskText = "";
    limitation = "These checks cannot determine whether the supporting ideas are logically correct or sufficient.";
  }
  if (recordedBody && instructional) {
    noticed = instructional.prepared_guidance.noticed;
    why = instructional.prepared_guidance.why;
    taskText = instructional.prepared_guidance.task;
    if (!excerpt && tutor?.task_fallback && /\bhighlighted\b/i.test(taskText)) taskText = tutor.task_fallback;
    limitation = instructional.prepared_guidance.limitation;
  }
  const vocabularySummary = tutorIntroductionVocabularySummary(result, ruleIds);
  if (vocabularySummary) excerpt = null; // Absence is section-wide, never a word-location finding.
  const evidenceText = overview?.evidence || vocabularySummary || (excerpt
    ? excerpt.contexts.map((context) => Array.from(source).slice(context.start, context.end).join("")).join("\n")
    : tutor?.evidence_fallback || TUTOR_NO_EXCERPT_TEXT);
  return {
    role: binding ? "PREPARED" : overview ? "NO_SUPPORTED_CONCERN_SELECTED" : "GENERAL_REVIEW",
    category: binding?.dimension && TUTOR_CATEGORY_LABELS[binding.dimension] ? binding.dimension : null,
    label: binding ? `${binding.dimension} · ${binding.skill}` : overview ? "No specific writing issue detected" : "General review",
    skill: binding?.skill || null,
    lesson_id: content?.lesson_id || null,
    rule_ids: Array.isArray(ruleIds) ? [...new Set(ruleIds)] : [],
    noticed,
    working_text: binding && instructional ? instructional.working_text || "" : "",
    feedback_purpose: instructional?.feedback_purpose || null,
    highlight_provenance: excerpt && instructional ? instructional.highlight_spans : [],
    evidence_text: evidenceText,
    why,
    task_text: taskText,
    limitation,
    excerpt,
  };
}

function selectTutorItems(result) {
  // Up to three items: the recorded primary branch first, then independently
  // supported Needs Attention findings with prepared secondary bindings.
  const bodyItems = selectBodyRecordedTutorItems(result);
  if (bodyItems) return bodyItems;
  const selected = selectScaffoldingGuidance(result);
  const maxItems = result?.stage_id === "INTRODUCTION" ? 2 : 3;
  const feedback = result?.feedback || {};
  const decision = result?.research_trace?.stages?.[result?.stage_id]?.feedback_decisions?.fields?.["Primary Feedback"];
  const primaryRuleIds = new Set(selected?.ruleIds || (Array.isArray(decision?.rule_ids) ? decision.rule_ids : []));
  const marker = selected?.branch === "intro_sentence_fluency_complete_sentence" ? verifiedScaffoldingSubordinator(result) : null;
  let clause = null;
  if (marker) {
    const sourceData = tutorSourceText(result);
    const sentence = sourceData ? tutorSentenceForSpan(sourceData.source, sourceData.linguistic, marker) : null;
    if (sentence) clause = sentence.text.replace(/[.!?]+$/u, "");
  }
  const observedMessage = typeof feedback["Primary Feedback"] === "string" ? feedback["Primary Feedback"] : "";
  const items = [buildTutorItem({
    result,
    binding: selected?.binding || null,
    content: selected?.content || null,
    ruleIds: selected?.ruleIds || (Array.isArray(decision?.rule_ids) ? decision.rule_ids : []),
    observedMessage,
    marker,
    clause,
    instructional: selected?.instructional || null,
  })];
  if (recordedNeutralSelection(result, selected)) {
    // The recorded branch is a neutral review. Keep the raw decision, lesson
    // and span in transparency, but do not present a trait/lesson concern.
    items[0].neutral_result = true;
    items[0].label = "No specific writing issue detected";
    items[0].category = null;
    items[0].skill = null;
    if (!items[0].working_text) items[0].working_text = recordedWorkingObservation(result, items[0].rule_ids);
  }
  const recorded = result?.stage_id === "INTRODUCTION" ? result.research_trace?.stages?.INTRODUCTION?.feedback_decisions?.instructional_feedback : null;
  if (recorded) {
    for (const entry of recorded.items || []) {
      if (items.length >= maxItems) break;
      if (entry.feedback_field !== "Needs Attention") continue;
      const instructional = introductionInstructionalItem(result, entry.feedback_field, entry.rule_ids, entry.lesson_id);
      const binding = scaffoldingCatalog.secondary_bindings?.find(b => b.stage_id === "INTRODUCTION" && b.lesson_id === entry.lesson_id && entry.rule_ids.some(id => new RegExp(b.rule_id_pattern).test(id)));
      const content = scaffoldingCatalog.lessons?.find(l => l.lesson_id === entry.lesson_id);
      if (!instructional || !binding || !content || items.some(i => i.lesson_id === content.lesson_id)) continue;
      const item = buildTutorItem({ result, binding, content, ruleIds: entry.rule_ids, instructional });
      if (entry.rule_ids.includes("INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW") && !item.excerpt) continue;
      items.push(item);
    }
    items.forEach((item, index) => { item.feedback_heading = index ? "Also Check" : "Main Feedback"; });
    return items;
  }
  if (scaffoldingCatalog?.availability === "AVAILABLE" && items.length < maxItems) {
    const messages = feedback["Needs Attention"];
    const provenance = (Array.isArray(feedback["Feedback Provenance"]) ? feedback["Feedback Provenance"] : [])
      .filter((item) => item?.feedback_field === "Needs Attention");
    if (Array.isArray(messages) && messages.length && messages.length === provenance.length) {
      const usedLessons = new Set(items.map((item) => item.lesson_id).filter(Boolean));
      const events = Array.isArray(result?.analysis?.rule_evidence) ? result.analysis.rule_evidence : [];
      for (let index = 0; index < messages.length && items.length < maxItems; index += 1) {
        const ruleId = provenance[index]?.rule_id;
        if (typeof ruleId !== "string" || !ruleId || primaryRuleIds.has(ruleId) || ruleId.includes(".LIMITATION.")) continue;
        if (!events.some((event) => event.rule_id === ruleId && event.triggered !== false && event.fired !== false)) continue;
        const binding = (scaffoldingCatalog.secondary_bindings || []).find((item) => item.stage_id === result?.stage_id
          && new RegExp(item.rule_id_pattern).test(ruleId));
        if (!binding || usedLessons.has(binding.lesson_id)) continue;
        const content = (scaffoldingCatalog.lessons || []).find((lesson) => lesson.lesson_id === binding.lesson_id);
        if (!content?.tutor) continue;
        usedLessons.add(binding.lesson_id);
        const item = buildTutorItem({
          result,
          binding,
          content,
          ruleIds: [ruleId],
          observedMessage: messages[index],
        });
        // A sentence-specific secondary concern needs verified source evidence.
        if (ruleId === "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW" && !item.excerpt) continue;
        items.push(item);
      }
    }
  }
  if (result?.stage_id === "INTRODUCTION") items.forEach((item, index) => {
    item.feedback_heading = index === 0 ? "Main Feedback" : "Also Check";
  });
  return items;
}

function studentFeedbackPresentation(result) {
  // The same read-only model supplies student text, transparency and export.
  // Original backend messages and protected analysis records are never changed.
  const selected = selectScaffoldingGuidance(result);
  const feedback = result?.feedback || {};
  const decision = result?.research_trace?.stages?.[result?.stage_id]?.feedback_decisions?.fields?.["Primary Feedback"];
  const ruleIds = selected?.ruleIds || (Array.isArray(decision?.rule_ids) ? decision.rule_ids : []);
  const items = selectTutorItems(result);
  const primary = items[0] || null;
  const marker = selected?.branch === "intro_sentence_fluency_complete_sentence" ? verifiedScaffoldingSubordinator(result) : null;
  const backendLimit = feedback.interpretation_limit || result?.interpretation_limit;
  const guidance = selected?.content.inline_guidance;
  const neutralBody = result?.stage_id === "BODY" && primary?.role === "NO_SUPPORTED_CONCERN_SELECTED";
  const neutralRecordedBranch = primary?.neutral_result === true
    && ["INTRODUCTION", "CONCLUSION"].includes(result?.stage_id);
  const neutral = neutralBody || neutralRecordedBranch;
  return {
    status: neutralBody ? "NO_SUPPORTED_CONCERN_SELECTED" : neutralRecordedBranch ? "NEUTRAL_OBSERVATION" : selected ? "PREPARED_INLINE_GUIDANCE" : "ORIGINAL_FEEDBACK",
    stage_id: result?.stage_id ?? null,
    writing_dimension: selected && primary?.category ? primary.category : null,
    writing_skill: selected && primary?.skill ? primary.skill : null,
    dimension_role: "Instructional review focus only; not a validated NLP classification, score or grade.",
    selection_branch: decision?.selection_branch ?? null,
    selection_priority: decision?.priority ?? null,
    rule_ids: ruleIds,
    verified_subordinator: marker,
    displayed_dimension_label: selected && primary?.category ? primary.label : null,
    recorded_feedback_decision: decision || null,
    instructional_feedback: ["INTRODUCTION", "BODY"].includes(result?.stage_id) && result?.research_trace?.selected_stage === result.stage_id ? result.research_trace.stages?.[result.stage_id]?.feedback_decisions?.instructional_feedback || null : null,
    displayed_strengths: primary?.working_text || "",
    supporting_rule_events: (result?.analysis?.rule_evidence || []).filter((event) => ruleIds.includes(event.rule_id)),
    nlp_evidence_location: "Supporting Rule Events retain actual evidence/actual_evidence, evidence types, conditions, spans and limitations where recorded. No additional observations are inferred.",
    original_feedback: Object.fromEntries(["Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"].filter((field) => feedback[field] !== undefined).map((field) => [field, feedback[field]])),
    displayed_guidance: neutral ? { "What I noticed": primary.noticed, ...(primary.working_text ? { "What's working": primary.working_text } : {}) } : {
      "What I noticed": primary?.noticed || "No observation reported.",
      "Look at your writing": primary?.evidence_text || TUTOR_NO_EXCERPT_TEXT,
      "Why it matters": primary?.why || "",
      "How to improve": primary?.task_text || "",
    },
    tutor_items: items.map((item) => ({
      role: item.role,
      neutral_result: item.neutral_result === true,
      feedback_heading: item.feedback_heading || null,
      category: item.category,
      label: item.label,
      skill: item.skill,
      lesson_id: item.lesson_id,
      rule_ids: item.rule_ids,
      noticed: item.noticed,
      working_text: item.working_text,
      feedback_purpose: item.feedback_purpose,
      highlight_provenance: item.highlight_provenance,
      evidence_text: item.evidence_text,
      why: item.why,
      task_text: item.task_text,
      limitation: item.limitation,
      excerpt: item.excerpt,
    })),
    displayed_limitation: neutral ? primary.limitation : guidance ? `Writing focus, not a score. ${guidance.limitation}` : backendLimit ? `Limits of these checks: ${backendLimit}` : "",
    teaching_content_source: neutralRecordedBranch ? null : selected ? {
      file: "content/lessons/feedback_help.json", catalog_version: scaffoldingCatalog.version,
      content_id: selected.content.lesson_id,
      binding: { stage_id: selected.stage, feedback_field: selected.field, selection_branch: selected.branch },
      mapping_basis: selected.binding.mapping_basis,
      recorded_observation_explanation: selected.binding.noticed,
    } : null,
    limitations: neutralRecordedBranch ? [primary.limitation, backendLimit].filter(Boolean) : selected ? [selected.content.limitation, selected.binding.mapping_basis, backendLimit].filter(Boolean) : [backendLimit].filter(Boolean),
    presentation_scope: neutralBody ? "Recorded Body outcome NO_SUPPORTED_CONCERN_SELECTED: neutral notice, supported observations and limitation only; no trait, lesson, improvement task, error location or passing grade."
      : neutralRecordedBranch
      ? `Recorded ${result.stage_id === "CONCLUSION" ? "Conclusion" : "Introduction"} branch is a neutral review: neutral notice, any recorded strength and limitation only; no corrective trait, lesson, improvement task or error location is displayed. The recorded decision, lesson mapping and spans remain in transparency.`
      : selected
      ? "Prepared content follows the completed backend choices; this renderer does not change branch selection, any of the five backend fields, or the student's writing."
      : "No verified prepared mapping is available. Original feedback and existing frontend fallbacks are retained without an invented dimension or skill label.",
  };
}

function renderScaffoldingTrace(parent, result) {
  const presentation = studentFeedbackPresentation(result);
  const neutralPresentation = presentation.status === "NO_SUPPORTED_CONCERN_SELECTED" || presentation.status === "NEUTRAL_OBSERVATION";
  const section = transparencySection(parent, "Exact student-facing guidance and teaching interpretation");
  transparencyText(section, presentation.dimension_role);
  transparencyTable(section, ["Presentation record", "Value"], [
    ["Status", presentation.status], ["Writing dimension", presentation.writing_dimension || "No instructional label"],
    ["Writing skill", presentation.writing_skill || "No instructional label"], ["Recorded Primary Feedback branch", presentation.selection_branch],
    ["Rule provenance", presentation.rule_ids.join(", ") || "No IDs recorded"],
    ["Teaching source", presentation.teaching_content_source ? `${presentation.teaching_content_source.file} · v${presentation.teaching_content_source.catalog_version} · ${presentation.teaching_content_source.content_id}` : presentation.status === "NO_SUPPORTED_CONCERN_SELECTED" ? "No trait or lesson assigned — neutral observation result" : presentation.status === "NEUTRAL_OBSERVATION" ? "No corrective trait or lesson displayed — recorded neutral review; raw mapping retained below" : "No verified prepared mapping"],
  ]);
  transparencyTable(section, ["Tutor section", "Original backend message", "Exact displayed guidance"], neutralPresentation ? [
    ["What I noticed", result.feedback?.["Primary Feedback"], presentation.displayed_guidance["What I noticed"]],
    ...(presentation.displayed_strengths ? [["What's working", result.feedback?.["What's Working"], presentation.displayed_strengths]] : []),
  ] : [
    ["What I noticed", result.feedback?.["Primary Feedback"], presentation.displayed_guidance["What I noticed"]],
    ["Look at your writing", "Verified analysis evidence", presentation.displayed_guidance["Look at your writing"]],
    ["Why it matters", "Teaching content / recorded rationale", presentation.displayed_guidance["Why it matters"]],
    ["How to improve", "Teaching content / recorded Next Step", presentation.displayed_guidance["How to improve"]],
  ]);
  transparencyText(section, `Exact displayed limitation: ${presentation.displayed_limitation || "No text displayed"}`);
  if (presentation.displayed_strengths) transparencyText(section, `What's working (recorded observation): ${presentation.displayed_strengths}`);
  transparencyDisclosure(section, "Recorded NLP evidence, emitted events, mapping rationale and limitations", (target) => renderTransparencyRecord(target, presentation));
}

function renderSixTraitTrace(parent, result) {
  const trace = ["INTRODUCTION", "BODY"].includes(result?.stage_id) ? result.research_trace?.stages?.[result.stage_id]?.feedback_decisions?.instructional_feedback : null;
  if (!trace) return;
  const section = transparencySection(parent, "6+1 instructional feedback — actual selected mapping");
  section.dataset.sixTraitTrace = "true";
  transparencyText(section, `Framework: ${trace.framework}. These are instructional categories and limited observations, not seven completed trait assessments. Marks identify evidence, not automatically errors.`);
  if (recordedNeutralSelection(result)) transparencyText(section, "Recorded neutral review branch: the student tutor does not display a corrective trait, lesson, evidence location or improvement task. The recorded mapping below is retained for transparency.");
  if (result.stage_id === "BODY") {
    transparencyText(section, `Actual Body selection status: ${trace.selection_status}. ${trace.neutral_result ? "No instructional trait, skill or lesson is assigned and no improvement task is displayed." : "Only the recorded supported concern is mapped to prepared instruction."}`);
    transparencyText(section, `Recorded backend Primary Feedback: ${trace.student_message}`);
    const prepared = trace.neutral_result || trace.items?.[0]?.prepared_guidance;
    if (prepared) transparencyTable(section, ["Student tutor section", "Actual recorded tutor wording"], [
      ["What I noticed", prepared.noticed],
      ...(prepared.working ? [["What's working", prepared.working]] : []),
      ...(trace.neutral_result ? [] : [["Why it matters", prepared.why], ["How to improve", prepared.task]]),
    ]);
    transparencyDisclosure(section, "Body selection checks, structural strengths, paragraph/sentence observations and exact Introduction context", host => {
      renderTransparencyRecord(host, { selection_checks: trace.selection_checks, strengths: trace.strengths,
        observed_paragraphs: trace.observed_paragraphs, introduction_context: trace.introduction_context, neutral_result: trace.neutral_result });
    });
  }
  transparencyTable(section, ["Feedback item", "Trait / skill", "Actual lesson / catalog", "FeedbackService branch", "Purpose"], trace.items.map(item => [
    item.feedback_field, `${item.trait || "No trait"} · ${item.skill || "No skill"}`,
    item.catalog_reference ? `${item.catalog_reference.file} · v${item.catalog_reference.version} · ${item.lesson_id}` : "No prepared mapping",
    item.selection_branch, item.feedback_purpose,
  ]), result.stage_id === "BODY" && trace.neutral_result ? "No trait, skill or lesson is assigned — NO_SUPPORTED_CONCERN_SELECTED." : undefined);
  if (result.stage_id !== "BODY" || trace.items.length) transparencyDisclosure(section, "Why selected, observed numeric fields, supporting events and exact highlights", host => {
    for (const item of trace.items) {
      transparencyText(host, `${item.feedback_field}: ${item.selection_condition || "No condition recorded"}`);
      transparencyText(host, `Mapping basis: ${item.mapping_basis}. Triggered supporting IDs: ${item.triggered_rule_ids.join(", ") || "none"}.`);
      transparencyTable(host, ["Original start", "Original end", "Highlighted text", "Supporting Rule Event", "Why this location"], item.highlight_spans.map(span => [span.start, span.end, span.text, span.rule_id, span.selection_reason]), "No verified source span was recorded; no highlight should be invented.");
      renderTransparencyRecord(host, { observed_fields: item.observed_fields, rule_conditions: item.rule_conditions,
        prepared_guidance: item.prepared_guidance, highlight_provenance: item.highlight_spans,
        supporting_events: result.analysis.rule_evidence.filter(e => item.rule_ids.includes(e.rule_id)) });
    }
  });
  transparencyDisclosure(section, "6+1 coverage — what ran, what is only a category, and what was not evaluated", host => {
    transparencyTable(host, ["Framework trait", "Recorded scope", "Status", "Selected category", "Quality assessment"], trace.coverage.map(row => [row.trait, row.scope, row.status, row.instructional_category_selected, row.trait_quality_assessment]));
  });
  for (const limitation of trace.limitations) transparencyText(section, limitation, "field-help");
}

copyFullAnalysisButton.addEventListener("click", async () => {
  if (analysisCopyInProgress) return;
  const result = currentAnalysisForExport();
  if (!result) { updateAnalysisExport(); return; }
  const generation = analysisCopyGeneration;
  const report = buildFullAnalysisReport(result);
  analysisCopyInProgress = true;
  copyFullAnalysisButton.disabled = true;
  analysisCopyFallback.hidden = true;
  fullAnalysisReport.value = "";
  analysisCopyStatus.textContent = "Copying full analysis…";
  try {
    if (!globalThis.navigator?.clipboard?.writeText) throw new Error("Clipboard API unavailable");
    await navigator.clipboard.writeText(report);
    if (generation === analysisCopyGeneration && currentAnalysisForExport() === result) analysisCopyStatus.textContent = "Full analysis copied.";
  } catch (_error) {
    if (generation === analysisCopyGeneration && currentAnalysisForExport() === result) {
      fullAnalysisReport.value = report;
      analysisCopyFallback.hidden = false;
      analysisCopyStatus.textContent = "Automatic copying was unavailable or blocked. Copy the complete report from the text field below.";
      fullAnalysisReport.focus();
      fullAnalysisReport.select();
    }
  } finally {
    analysisCopyInProgress = false;
    copyFullAnalysisButton.disabled = !currentAnalysisForExport();
    if (generation !== analysisCopyGeneration || currentAnalysisForExport() !== result) analysisCopyStatus.textContent = currentAnalysisForExport()
      ? "Current analysis ready to copy. A copy started before the change describes the earlier analysis."
      : "Analyze the current draft first. A copy started before the change describes the earlier analysis.";
  }
});

function markTutorTyping() {
  state.tutorTyping = true;
  if (tutorTypingTimer !== null) window.clearTimeout(tutorTypingTimer);
  tutorTypingTimer = window.setTimeout(() => {
    tutorTypingTimer = null;
    state.tutorTyping = false;
    updateTutorPlaceholder();
  }, TUTOR_TYPING_IDLE_MS);
  updateTutorPlaceholder();
}

function clearTutorTypingWork() {
  state.tutorTyping = false;
  if (tutorTypingTimer !== null) {
    window.clearTimeout(tutorTypingTimer);
    tutorTypingTimer = null;
  }
  updateTutorPlaceholder();
}

function setTutorStateMessage({ title, lead, detail = "", showTypingDots = false }) {
  tutorStateTitle.textContent = title;
  tutorStateLead.textContent = lead;
  tutorStateDetail.textContent = detail;
  tutorStateDetail.hidden = !detail;
  tutorTypingDots.hidden = !showTypingDots;
}

function updateTutorPlaceholder() {
  const stage = state.currentStage;
  if (!writingInput.value.trim()) {
    setTutorStateMessage({ title: "Start writing your essay. I'll help you review it as you write.", lead: (TUTOR_WELCOME[stage] || TUTOR_WELCOME.BODY).lead });
    return;
  }
  if (state.tutorAnalysisRunning) {
    setTutorStateMessage({ ...TUTOR_STATE_TEXT.RUNNING, showTypingDots: true });
    return;
  }
  if (state.tutorError) {
    setTutorStateMessage(TUTOR_STATE_TEXT.ERROR);
    return;
  }
  if (state.tutorTyping) {
    setTutorStateMessage({ ...TUTOR_STATE_TEXT.TYPING, showTypingDots: true });
    return;
  }
  if (liveAnalysisTimer !== null || queuedStageAnalysis) {
    setTutorStateMessage(TUTOR_STATE_TEXT.PAUSED);
    return;
  }
  if (state.tutorStaleStages[stage]) {
    setTutorStateMessage(TUTOR_STATE_TEXT.STALE);
    return;
  }
  if (state.tutorAssignmentStale) {
    setTutorStateMessage(TUTOR_STATE_TEXT.ASSIGNMENT_STALE);
    return;
  }
  const welcome = TUTOR_WELCOME[stage] || TUTOR_WELCOME.BODY;
  if (state.drafts[stage] && state.drafts[stage].trim()) {
    setTutorStateMessage({
      title: welcome.title,
      lead: "You already have writing in this section.",
      detail: "When you're ready, select Analyze Now to review this version.",
    });
    return;
  }
  setTutorStateMessage(welcome);
}

function renderTutorEvidence(parent, item) {
  parent.replaceChildren();
  parent.setAttribute("data-lesson", item.lesson_id || "");
  if (!item.excerpt || !Array.isArray(item.excerpt.contexts) || !item.excerpt.contexts.length
    || typeof item.excerpt.source !== "string") {
    const empty = document.createElement("p");
    empty.className = "tutor-excerpt";
    empty.textContent = item.evidence_text || TUTOR_NO_EXCERPT_TEXT;
    parent.appendChild(empty);
    return;
  }
  const characters = Array.from(item.excerpt.source);
  for (const context of item.excerpt.contexts) {
    const paragraph = document.createElement("p");
    paragraph.className = "tutor-excerpt";
    if (item.category) paragraph.setAttribute("data-category", item.category);
    const boundaries = new Set([context.start, context.end]);
    for (const [markStart, markEnd] of context.marks) {
      boundaries.add(markStart);
      boundaries.add(markEnd);
    }
    const points = [...boundaries]
      .filter((value) => value >= context.start && value <= context.end)
      .sort((a, b) => a - b);
    for (let index = 0; index < points.length - 1; index += 1) {
      const from = points[index];
      const to = points[index + 1];
      const text = characters.slice(from, to).join("");
      if (!text) continue;
      if (context.marks.some(([markStart, markEnd]) => markStart <= from && to <= markEnd)) {
        const mark = document.createElement("mark");
        mark.textContent = text;
        paragraph.appendChild(mark);
      } else {
        const span = document.createElement("span");
        span.textContent = text;
        paragraph.appendChild(span);
      }
    }
    parent.appendChild(paragraph);
  }
}

function renderTutorTabs(items, activeIndex) {
  tutorTabs.replaceChildren();
  if (items.length <= 1) {
    tutorTabs.hidden = true;
    return;
  }
  tutorTabs.hidden = false;
  items.forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "tutor-tab";
    button.textContent = item.feedback_heading ? `${item.feedback_heading}: ${item.label}` : item.label;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-selected", String(index === activeIndex));
    if (item.category) button.setAttribute("data-category", item.category);
    if (index === activeIndex) button.classList.toggle("active", true);
    button.addEventListener("click", () => selectTutorItem(index));
    tutorTabs.appendChild(button);
  });
}

function selectTutorItem(index) {
  const items = activeTutorItems;
  const item = items[index];
  if (!item) return;
  activeTutorItemIndex = index;
  const buttons = tutorTabs.querySelectorAll("button");
  buttons.forEach((button, buttonIndex) => {
    button.setAttribute("aria-selected", String(buttonIndex === index));
    button.classList.toggle("active", buttonIndex === index);
  });
  renderTutorItem(item);
  revealEditorEvidence();
}

function syncEditorHighlight() {
  const mirror = document.getElementById("editor-mirror");
  if (!mirror) return;
  if (typeof getComputedStyle === "function") {
    const style = getComputedStyle(writingInput);
    for (const property of ["font", "padding", "letterSpacing", "wordSpacing", "lineHeight", "tabSize", "wordBreak", "overflowWrap", "textIndent", "textAlign", "direction"]) {
      mirror.style[property] = style[property];
    }
  }
  mirror.style.width = `${writingInput.clientWidth}px`;
  mirror.style.transform = `translate(${-writingInput.scrollLeft || 0}px, ${-writingInput.scrollTop || 0}px)`;
}

function renderEditorHighlight(item = null) {
  const mirror = document.getElementById("editor-mirror");
  if (!mirror) return;
  mirror.replaceChildren();
  mirror.removeAttribute("data-category");
  const excerpt = item?.excerpt;
  const source = excerpt?.source;
  if (!item?.category || typeof source !== "string" || source !== writingInput.value
    || !Array.isArray(excerpt.contexts) || !excerpt.contexts.length) return;
  const characters = Array.from(source);
  const sentenceConcern = item.rule_ids.includes("INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR");
  const ranges = [];
  for (const context of excerpt.contexts) {
    if (!tutorVerifiedSpan(source, context)) return;
    const marks = sentenceConcern || !context.marks.length
      ? [[context.start, context.end]] : context.marks;
    for (const [start, end] of marks) {
      if (!tutorVerifiedSpan(source, { start, end }) || start < context.start || end > context.end) return;
      ranges.push([start, end]);
    }
  }
  // Merge overlapping recorded ranges; never search for a matching word.
  const merged = [];
  for (const range of ranges.sort((a, b) => a[0] - b[0])) {
    const last = merged[merged.length - 1];
    if (last && range[0] <= last[1]) last[1] = Math.max(last[1], range[1]);
    else merged.push([...range]);
  }
  let cursor = 0;
  for (const [start, end] of merged) {
    const before = document.createElement("span");
    before.textContent = characters.slice(cursor, start).join("");
    mirror.appendChild(before);
    const mark = document.createElement("mark");
    mark.textContent = characters.slice(start, end).join("");
    mirror.appendChild(mark);
    cursor = end;
  }
  const tail = document.createElement("span");
  tail.textContent = characters.slice(cursor).join("") + "\n";
  mirror.appendChild(tail);
  mirror.setAttribute("data-category", item.category);
  syncEditorHighlight();
}

function revealEditorEvidence() {
  const mirror = document.getElementById("editor-mirror");
  const mark = mirror?.querySelector("mark");
  if (!mark?.getBoundingClientRect || !writingInput.getBoundingClientRect) return;
  const editorBox = writingInput.getBoundingClientRect();
  const markBox = mark.getBoundingClientRect();
  if (markBox.top < editorBox.top || markBox.bottom > editorBox.bottom) {
    writingInput.scrollTop += markBox.top - editorBox.top - writingInput.clientHeight / 3;
    syncEditorHighlight();
  }
}

writingInput.addEventListener("scroll", syncEditorHighlight);
if (typeof ResizeObserver !== "undefined") new ResizeObserver(syncEditorHighlight).observe(writingInput);

function renderTutorItem(item) {
  const neutral = item.role === "NO_SUPPORTED_CONCERN_SELECTED" || item.neutral_result === true;
  for (const [id, visible] of [["tutor-evidence-section", !neutral && Boolean(item.evidence_text)], ["tutor-why-section", !neutral && Boolean(item.why)], ["tutor-task-section", !neutral && Boolean(item.task_text)]]) {
    const section = document.getElementById(id);
    if (section) section.hidden = !visible;
  }
  tutorNoticed.textContent = item.noticed;
  const working = document.getElementById("tutor-working"), workingSection = document.getElementById("tutor-working-section");
  if (working && workingSection) { working.textContent = item.working_text || ""; workingSection.hidden = !item.working_text; }
  if (neutral) {
    // A neutral result has no error location: clear the evidence node instead of
    // rendering the raw span that remains available in transparency.
    tutorEvidence.replaceChildren();
    tutorEvidence.setAttribute("data-lesson", item.lesson_id || "");
  } else {
    renderTutorEvidence(tutorEvidence, item);
  }
  tutorWhy.textContent = item.why;
  tutorTask.textContent = item.task_text;
  tutorLimitation.textContent = item.limitation || "";
  tutorLimitation.hidden = !item.limitation;
  if (feedbackWritingFocus) {
    feedbackWritingFocus.textContent = item.category || neutral ? item.label : "";
    feedbackWritingFocus.hidden = (!item.category && !neutral) || activeTutorItems.length > 1;
    feedbackWritingFocus.setAttribute("aria-label", neutral ? "Neutral observation result, not a writing grade" : "Instructional writing focus, not an assessed score");
    feedbackWritingFocus.setAttribute("data-category", item.category || "");
  }
  if (neutral) renderEditorHighlight();
  else renderEditorHighlight(item);
}

function displayFeedback(result) {
  renderEditorHighlight();
  renderNlpTransparency(result);
  if (!result) {
    updateAnalysisExport();
    activeTutorItems = [];
    activeTutorItemIndex = 0;
    feedbackContent.hidden = true;
    feedbackPlaceholder.hidden = false;
    if (feedbackWritingFocus) { feedbackWritingFocus.textContent = ""; feedbackWritingFocus.hidden = true; }
    updateTutorPlaceholder();
    updateStageProgress();
    return;
  }

  updateAnalysisExport();
  const feedback = result.feedback;
  const presentation = studentFeedbackPresentation(result);
  if (feedbackWritingFocus) {
    feedbackWritingFocus.textContent = presentation.displayed_dimension_label || "";
    feedbackWritingFocus.hidden = !presentation.displayed_dimension_label;
  }
  activeTutorItems = presentation.tutor_items || [];
  activeTutorItemIndex = 0;
  renderTutorTabs(activeTutorItems, 0);
  if (activeTutorItems.length) renderTutorItem(activeTutorItems[0]);
  revealEditorEvidence();
  document.getElementById("interpretation-limit").textContent = presentation.displayed_limitation;
  displayList("whats-working", feedback["What's Working"]);
  displayList("needs-attention", feedback["Needs Attention"]);
  feedbackPlaceholder.hidden = true;
  feedbackContent.hidden = false;
  updateStageProgress();
}

function displayList(id, values) {
  const list = document.getElementById(id);
  list.replaceChildren();
  const items = Array.isArray(values) ? [...values] : values ? [values] : [];
  if (!items.length) {
    items.push(id === "needs-attention"
      ? "No additional issue was flagged by the available checks."
      : "No positive observation was recorded by these checks.");
  }
  for (const value of items) {
    const item = document.createElement("li");
    item.textContent = value;
    list.appendChild(item);
  }
}

function resetIntroductionLessonProgress() {
  state.introductionLesson = { open: false };
  updateIntroductionTutoring();
}

function introductionLessonHasCurrentTeacherFocusMismatch() {
  if (state.assignmentId === null || state.deletedAssignment || state.submission) return false;
  const result = state.analyses.INTRODUCTION;
  const currentSnapshot = analysisSnapshot("INTRODUCTION");
  if (!result?.analysis || state.analysisSnapshots.INTRODUCTION !== currentSnapshot) return false;

  const lexical = result.analysis.lexical_topic_evidence || {};
  if (
    lexical.focus_source !== "teacher_provided"
    || !Array.isArray(lexical.focus_terms)
    || lexical.focus_terms.length === 0
    || (lexical.observed_focus_terms || []).length > 0
  ) return false;

  return (result.analysis.rule_evidence || []).some((event) =>
    event.rule_id === "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED"
    && event.triggered === true
  );
}

function lessonElement(tagName, className = "", text = null) {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  if (text !== null) element.textContent = text;
  return element;
}

function appendLessonParagraph(parent, text, className = "") {
  parent.appendChild(lessonElement("p", className, text));
}

function appendLessonExampleRow(parent, label, text, explanation = "") {
  const row = lessonElement("div", "introduction-lesson-example-row");
  const heading = lessonElement("strong", "", `${label}: `);
  const value = lessonElement("span", "", text);
  row.append(heading, value);
  if (explanation) appendLessonParagraph(row, explanation);
  parent.appendChild(row);
}

function renderIntroductionLessonModel() {
  const model = introductionLessonDefinition.model;
  introductionLessonContent.appendChild(lessonElement("h3", "", model.heading));
  for (const instruction of model.instruction) appendLessonParagraph(introductionLessonContent, instruction);

  const example = lessonElement("section", "introduction-lesson-example");
  example.setAttribute("aria-label", "Teacher-style example");
  appendLessonParagraph(example, `Assignment: ${model.teacher_authored_example.assignment}`);
  appendLessonExampleRow(example, "Topic", model.teacher_authored_example.topic, model.teacher_authored_example.topic_explanation);
  appendLessonExampleRow(example, "Topic description", model.teacher_authored_example.description_sentence, model.teacher_authored_example.description_explanation);
  appendLessonExampleRow(example, "Position with a reason", model.teacher_authored_example.position_sentence, model.teacher_authored_example.position_explanation);
  appendLessonParagraph(example, model.teacher_authored_example.direction_explanation);
  introductionLessonContent.appendChild(example);

  const sourceDetails = lessonElement("details", "introduction-lesson-sources");
  sourceDetails.appendChild(lessonElement("summary", "", "About this lesson’s teaching approach"));
  for (const source of introductionLessonDefinition.source_framework) {
    const sourceBlock = lessonElement("div", "introduction-lesson-source");
    appendLessonParagraph(sourceBlock, source.name);
    appendLessonParagraph(sourceBlock, source.recommendation || source.citation);
    appendLessonParagraph(sourceBlock, source.use_in_this_lesson || source.principles_used.join(" "));
    const link = lessonElement("a", "", source.url);
    link.href = source.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    sourceBlock.appendChild(link);
    sourceDetails.appendChild(sourceBlock);
  }
  introductionLessonContent.appendChild(sourceDetails);
  appendLessonParagraph(introductionLessonContent, introductionLessonDefinition.authorship_and_provenance.instructional_content, "introduction-lesson-provenance");
}

function renderIntroductionLesson() {
  if (!introductionLessonDefinition) return;
  introductionLessonTitle.textContent = introductionLessonDefinition.title;
  introductionLessonStepLabel.textContent = "WRITING GUIDE";
  introductionLessonProgress.textContent = "Read and revise independently";
  introductionLessonContent.replaceChildren();
  introductionLessonFeedback.textContent = "";
  introductionLessonFeedback.dataset.correct = "";

  renderIntroductionLessonModel();
}

function updateIntroductionTutoring() {
  if (!introductionTutoring) return;
  const inIntroduction = state.currentStage === "INTRODUCTION" && state.currentView !== "ESSAY_REVIEW";
  introductionTutoring.hidden = !inIntroduction;
  introductionLessonPanel.hidden = !inIntroduction || !state.introductionLesson.open;
  const suggestionAvailable = inIntroduction && introductionLessonHasCurrentTeacherFocusMismatch();
  introductionLessonSuggestion.hidden = !suggestionAvailable;
  introductionLessonSuggestion.textContent = suggestionAvailable
    ? "Your Introduction may use different words from the assignment focus. If you want help checking the prompt and choosing a position, this optional lesson is available."
    : "";
  openIntroductionLessonButton.disabled = !introductionLessonDefinition;
  if (state.introductionLesson.open && inIntroduction) renderIntroductionLesson();
}

function openIntroductionLesson() {
  if (!introductionLessonDefinition || state.currentStage !== "INTRODUCTION") return;
  state.introductionLesson.open = true;
  updateIntroductionTutoring();
  introductionLessonContent.focus();
}

function closeIntroductionLessonAndReturnToWriting() {
  state.introductionLesson.open = false;
  updateIntroductionTutoring();
  writingInput.scrollIntoView?.({ behavior: "smooth", block: "center" });
  writingInput.focus();
}

openIntroductionLessonButton.addEventListener("click", openIntroductionLesson);
introductionLessonReturnButton.addEventListener("click", closeIntroductionLessonAndReturnToWriting);

function currentIntroductionText() {
  if (state.currentStage === "INTRODUCTION") {
    state.drafts.INTRODUCTION = writingInput.value;
  }
  return state.drafts.INTRODUCTION || "";
}
const STAGE_PROGRESS_NEXT = {
  INTRODUCTION: { stage: "BODY", label: "Continue to Body", badge: "Before Body" },
  BODY: { stage: "CONCLUSION", label: "Continue to Conclusion", badge: "Before Conclusion" },
  CONCLUSION: { stage: "ESSAY_REVIEW", label: "Continue to Essay Review", badge: "Before Essay Review" },
};
function stageProgressCurrentResult(stage) {
  const result = state.analyses[stage];
  const stale = Boolean(state.tutorStaleStages[stage] || state.tutorAssignmentStale
    || (result && state.analysisSnapshots[stage] !== analysisSnapshot(stage))
    || (result && writingInput.value !== state.drafts[stage]));
  if (!result || result.stage_id !== stage || result.availability !== "ANALYZED"
    || !result.analysis || !result.feedback
    || state.analysisSnapshots[stage] !== analysisSnapshot(stage)
    || writingInput.value !== state.drafts[stage]) {
    return { result: null, stale };
  }
  return { result, stale: false };
}

function stageProgressNeedsAttention(result) {
  const messages = Array.isArray(result?.feedback?.["Needs Attention"]) ? result.feedback["Needs Attention"] : [];
  return messages.filter((message) => typeof message === "string" && message
    && !/^(These checks record structure and wording only|These checks highlight|This deterministic feedback|These checks cannot)\b/.test(message));
}

function stageProgressConcern(result) {
  if (!result) return null;
  const items = activeTutorItems.length ? activeTutorItems : selectTutorItems(result);
  const primary = items[0];
  if (!primary) return null;
  const decision = result.research_trace?.stages?.[result.stage_id]?.feedback_decisions;
  const record = decision?.instructional_feedback;
  const branch = decision?.fields?.["Primary Feedback"]?.selection_branch
    || (Array.isArray(record?.items) ? record.items[0]?.selection_branch : null);
  const neutralBranches = STAGE_PROGRESS_NEUTRAL_BRANCHES[result.stage_id] || [];
  const neutralSelected = primary.role === "NO_SUPPORTED_CONCERN_SELECTED"
    || (result.stage_id === "BODY" && decision?.selection_status === "NO_SUPPORTED_CONCERN_SELECTED")
    || (branch && neutralBranches.includes(branch));
  const supported = primary.role === "PREPARED" || primary.role === "RECORDED_BODY_FEEDBACK";
  if (neutralSelected || (!supported && !stageProgressNeedsAttention(result).length)) return null;

  const primaryRecord = Array.isArray(record?.items)
    ? record.items.find((entry) => entry.feedback_field === "Primary Feedback") || record.items[0]
    : null;
  const selectedCheck = Array.isArray(record?.selection_checks)
    ? record.selection_checks.find((check) => check.status === "SELECTED")
    : null;
  const indices = primaryRecord?.paragraph_indices || selectedCheck?.paragraph_indices || [];
  const paragraphNumber = Number.isInteger(indices[0]) ? indices[0] : null;
  const noticed = String(primary.noticed || result.feedback?.["Primary Feedback"] || "").trim();
  const namesParagraph = paragraphNumber !== null
    && new RegExp(`^Paragraph\\s+${paragraphNumber}\\b`, "i").test(noticed);
  return {
    paragraph: paragraphNumber === null || namesParagraph ? "" : `Paragraph ${paragraphNumber}:`,
    noticed,
    task: String(primary.task_text || "").trim(),
  };
}

function updateStageProgress() {
  if (!stageProgress) return;
  const stage = state.currentStage;
  const next = STAGE_PROGRESS_NEXT[stage];
  const visible = Boolean(next) && state.activeAppView === "workspace"
    && state.currentView === stage && !state.restoring;
  stageProgress.hidden = !visible;
  if (!visible) return;

  stageProgressBadge.textContent = next.badge;
  stageProgressContinue.textContent = next.label;
  stageProgressContinue.disabled = state.restoring;
  const current = stageProgressCurrentResult(stage);
  const concern = stageProgressConcern(current.result);
  const stateName = concern ? "REVIEW_SUGGESTED" : current.result ? "NO_ISSUE" : "NOT_ANALYZED";
  stageProgress.dataset.state = stateName;
  stageProgressBadge.dataset.state = stateName;
  stageProgressTitle.textContent = concern ? "Review Suggested"
    : current.result ? "No Specific Writing Issue Detected"
      : "Ready to Review Your Writing?";
  stageProgressLead.textContent = concern ? "EssayScaff found something you may want to review."
    : current.result ? "The available checks did not identify a specific structural concern."
      : "Click Analyze Now to receive feedback, or continue when you are ready.";

  if (concern) {
    stageProgressFocus.textContent = concern.paragraph;
    stageProgressFocus.hidden = !concern.paragraph;
    stageProgressNoticed.textContent = concern.noticed;
    stageProgressDetail.hidden = !concern.paragraph && !concern.noticed;
    stageProgressTask.textContent = concern.task;
    stageProgressTask.hidden = !concern.task;
  } else if (current.result) {
    stageProgressFocus.textContent = "";
    stageProgressFocus.hidden = true;
    stageProgressNoticed.textContent = "Review your ideas before continuing.";
    stageProgressDetail.hidden = false;
    stageProgressTask.textContent = "";
    stageProgressTask.hidden = true;
  } else {
    stageProgressFocus.textContent = "";
    stageProgressFocus.hidden = true;
    stageProgressNoticed.textContent = "";
    stageProgressDetail.hidden = true;
    stageProgressTask.textContent = current.stale
      ? "Your writing has changed since the last analysis. Analyze again to update this guidance."
      : "";
    stageProgressTask.hidden = !current.stale;
  }
  stageProgressReview.hidden = !concern;
}

stageProgressContinue.addEventListener("click", () => {
  const next = STAGE_PROGRESS_NEXT[state.currentStage];
  if (next) selectStage(next.stage);
});
stageProgressReview.addEventListener("click", () => {
  writingInput.focus();
  writingInput.scrollIntoView?.({ behavior: "smooth", block: "center" });
});

function selectStage(stage) {
  cancelAnalysisWork();
  clearTutorTypingWork();
  writingActivity?.stageChanged();
  state.drafts[state.currentStage] = writingInput.value;
  if (stage === "ESSAY_REVIEW") {
    state.currentView = "ESSAY_REVIEW";
    state.reviewTechnicalInspectorOpen = false;
    updateAnalysisExport();
    workArea.hidden = true;
    revisionCard.hidden = true;
    essayReviewPanel.hidden = false;
    for (const tab of stageTabs) {
      const selected = tab.dataset.stage === "ESSAY_REVIEW";
      tab.classList.toggle("active", selected);
      tab.setAttribute("aria-pressed", String(selected));
    }
    renderEssayReview();
    void loadRevisionHistory();
    void loadWritingActivitySummary();
    updateIntroductionTutoring();
    updateStageProgress();
    errorMessage.hidden = true;
    return;
  }

  state.currentView = stage;
  state.currentStage = stage;
  state.reviewTechnicalInspectorOpen = false;
  workArea.hidden = false;
  revisionCard.hidden = false;
  essayReviewPanel.hidden = true;
  syncTechnicalInspectorVisibility();
  const settings = stageSettings[stage];
  writingInput.value = state.drafts[stage];
  writingInput.maxLength = settings.limit;
  writingInput.placeholder = settings.placeholder;
  stageHeading.textContent = settings.title;
  stageLabel.textContent = `STEP ${Object.keys(stageSettings).indexOf(stage) + 1}`;
  writingLabel.textContent = settings.title;
  analyzeButton.textContent = settings.button;
  analysisStatus.textContent = state.analyses[stage]
    ? "Feedback is current for the last analysis. Edit to update it."
    : "Feedback updates after a short pause. Analyze Now checks immediately. Analysis does not save your draft.";
  for (const tab of stageTabs) {
    const selected = tab.dataset.stage === state.currentView;
    tab.classList.toggle("active", selected);
    tab.setAttribute("aria-pressed", String(selected));
  }
  feedbackStatus.textContent = state.analyses[stage] ? "Analysis complete" : "Not analyzed";
  displayFeedback(state.analyses[stage]);
  updateIntroductionTutoring();
  updateStageProgress();
  updateWordCount();
  updateSaveStatus();
  errorMessage.hidden = true;
  if (!state.analyses[stage]) scheduleLiveAnalysis();
}

function invalidateAnalysesFor(stage, statusText) {
  cancelAnalysisWork();
  const affectedStages = {
    INTRODUCTION: ["INTRODUCTION", "BODY", "CONCLUSION"],
    BODY: ["BODY", "CONCLUSION"],
    CONCLUSION: ["CONCLUSION"],
  }[stage];
  for (const affected of affectedStages) {
    if (state.analyses[affected]) state.tutorStaleStages[affected] = true;
    delete state.analyses[affected];
    delete state.analysisSnapshots[affected];
    delete state.analysisFailures[affected];
  }
  if (affectedStages.includes(state.currentStage)) {
    feedbackStatus.textContent = statusText;
    displayFeedback(null);
  }
  if (affectedStages.includes("INTRODUCTION")) updateIntroductionTutoring();
}

function invalidateAllAnalyses() {
  cancelAnalysisWork();
  clearTutorTypingWork();
  resetAnalysisContext();
  state.tutorAssignmentStale = true;
  state.tutorError = false;
  feedbackStatus.textContent = "Assignment changed — analyze again";
  displayFeedback(null);
  updateIntroductionTutoring();
  state.saveFailed = false;
  updateSaveStatus();
  if (state.currentView === "ESSAY_REVIEW") renderEssayReview();
}

stageTabs.forEach((tab) => {
  tab.addEventListener("click", () => selectStage(tab.dataset.stage));
});

function cancelAnalysisWork() {
  if (liveAnalysisTimer !== null) {
    window.clearTimeout(liveAnalysisTimer);
    liveAnalysisTimer = null;
  }
  state.tutorAnalysisRunning = false;
  analysisRequestId += 1;
  queuedStageAnalysis = null;
  // Invalidate immediately, but let the existing HTTP request settle before
  // starting another. Aborting fetch cannot cancel server-side spaCy execution.
  activeAnalysisStage = null;
}

function recordStageAnalysisFailure(stage, snapshot, reason) {
  state.analysisFailures[stage] = { snapshot, reason };
  if (stage === "INTRODUCTION") updateIntroductionTutoring();
}

function scheduleLiveAnalysis() {
  if (liveAnalysisTimer !== null) window.clearTimeout(liveAnalysisTimer);
  liveAnalysisTimer = null;
  errorMessage.hidden = true;
  errorMessage.textContent = "";
  if (
    state.activeAppView !== "workspace"
    || state.currentView !== state.currentStage
    || state.restoring
    || state.deletedAssignment
    || state.submission
    || state.submitting
  ) {
    analysisStatus.textContent = "";
    return;
  }
  if (!topicInput.value.trim() || !writingInput.value.trim()) {
    if (state.currentStage === "INTRODUCTION" && /\p{L}/u.test(writingInput.value) && !topicInput.value.trim()) {
      recordStageAnalysisFailure(
        "INTRODUCTION",
        analysisSnapshot("INTRODUCTION"),
        "Enter an assignment topic before analyzing.",
      );
      analysisStatus.textContent = "Add a topic before checking your Introduction.";
    } else {
      analysisStatus.textContent = "Add a topic and write in this section to get feedback.";
      updateIntroductionTutoring();
    }
    return;
  }

  if (state.analyses[state.currentStage] && state.analysisSnapshots[state.currentStage] === analysisSnapshot(state.currentStage)) return;
  analysisStatus.textContent = "Checking your latest writing…";
  liveAnalysisTimer = window.setTimeout(() => {
    liveAnalysisTimer = null;
    void runStageAnalysis({ automatic: true });
  }, LIVE_ANALYSIS_DELAY_MS);
  updateTutorPlaceholder();
  updateIntroductionTutoring();
}

joinClassroomForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (state.restoring) return;
  assignmentMessage.textContent = "";
  const enrollmentCode = enrollmentCodeInput.value.trim();
  if (!enrollmentCode) {
    assignmentMessage.textContent = "Enter the classroom enrollment code.";
    return;
  }
  try {
    const response = await fetch("/api/classroom-enrollments", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify({ enrollment_code: enrollmentCode }),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Could not join the classroom.");
    enrollmentCodeInput.value = "";
    await loadMyClassrooms();
    await loadStudentHistory();
    await selectClassroom(result.classroom.classroom_id);
    assignmentMessage.textContent = `Joined ${result.classroom.classroom_name}.`;
  } catch (error) {
    assignmentMessage.textContent = error.message || "Could not join the classroom.";
  }
});

showAllAssignmentsButton.addEventListener("click", () => {
  state.selectedClassroomId = null;
  selectedClassroom.hidden = true;
  navigateAppView("assignments");
});
openAssignmentWorkspaceButton.addEventListener("click", () => {
  if (state.pendingAssignmentId !== null && state.pendingAssignmentId !== undefined) {
    selectAssignment(state.pendingAssignmentId);
  }
});

writingInput.addEventListener("input", () => {
  state.drafts[state.currentStage] = writingInput.value;
  writingActivity?.noteEdit(state.currentStage);
  state.tutorError = false;
  state.tutorAssignmentStale = false;
  invalidateAnalysesFor(state.currentStage, "Draft edited — analyze again");
  markTutorTyping();
  state.saveFailed = false;
  state.saveErrorMessage = "";
  state.restoreIdWarning = false;
  updateWordCount();
  updateSaveStatus();
  scheduleLiveAnalysis();
});

topicInput.addEventListener("input", invalidateAllAnalyses);
focusInput.addEventListener("input", invalidateAllAnalyses);
for (const input of [topicInput, focusInput]) {
  input.addEventListener("input", () => {
    state.saveFailed = false;
    state.saveErrorMessage = "";
    state.restoreIdWarning = false;
    updateSaveStatus();
    scheduleLiveAnalysis();
  });
}
for (const stage of Object.keys(stageSettings)) state.drafts[stage] = "";
state.savedSnapshot = draftSnapshot();
updateWordCount();
updateSaveStatus();

window.addEventListener("beforeunload", updateBeforeUnloadWarning);
document.addEventListener?.("visibilitychange", () => {
  if (document.visibilityState === "hidden") writingActivity?.leaveWorkspace();
});
window.addEventListener("pagehide", () => writingActivity?.leaveWorkspace());

async function restoreDraft() {
  let practiceSessionId;
  let activeAssignmentId;
  try {
    practiceSessionId = window.localStorage.getItem("essayScaffSessionId");
    activeAssignmentId = window.localStorage.getItem("essayScaffActiveAssignmentId");
  } catch (_error) {
    setSaveStatus("Browser storage is unavailable", "failed");
    await loadMyClassrooms();
    await loadStudentHistory();
    return;
  }

  state.restoring = true;
  setWorkspaceControlsDisabled(true);
  setSaveStatus("Restoring workspace…", "saving");
  try {
    await loadMyClassrooms();
    await loadStudentHistory();
    if (activeAssignmentId) {
      const response = await fetch(
        `/api/assignments/${encodeURIComponent(activeAssignmentId)}/workspace`
      );
      const result = await response.json().catch(() => ({}));
      if (response.ok) {
        applyAssignmentWorkspace(result);
        await selectClassroom(result.assignment.classroom_id, false);
        await loadRevisionHistory();
        return;
      }
      if (response.status === 404 || response.status === 400 || response.status === 410) {
        window.localStorage.removeItem("essayScaffActiveAssignmentId");
      } else {
        throw new Error(result.error || "Assignment workspace could not be restored.");
      }
    }

    if (!practiceSessionId) {
      applyPracticeDraft(null);
      assignmentMessage.textContent = "";
      await loadRevisionHistory();
      return;
    }
    const response = await fetch(`/api/drafts?session_id=${encodeURIComponent(practiceSessionId)}`);
    const draft = await response.json().catch(() => ({}));
    if (response.ok && draft.assignment_id == null) {
      applyPracticeDraft(draft);
      await loadRevisionHistory();
      return;
    }
    if (response.status === 404 || response.status === 400 || (response.ok && draft.assignment_id != null)) {
      applyPracticeDraft(null);
      assignmentMessage.textContent = "";
      await loadRevisionHistory();
      return;
    }
    throw new Error(draft.error || "Practice draft could not be restored.");
  } catch (error) {
    setSaveStatus(error.message || "Workspace could not be restored", "failed");
  } finally {
    state.restoring = false;
    setWorkspaceControlsDisabled(false);
    updateSaveStatus();
  }
}

async function saveDraft() {
  if (state.restoring || state.saving || state.revisionSaving || state.submission || state.deletedAssignment) return false;
  const draft = currentDraftData();
  const snapshot = JSON.stringify(draft);
  const payload = { ...draft };
  if (state.sessionId) payload.session_id = state.sessionId;

  state.saving = true;
  state.saveFailed = false;
  state.saveErrorMessage = "";
  state.restoreIdWarning = false;
  saveButton.disabled = true;
  saveRevisionButton.disabled = true;
  setSaveStatus("Saving…", "saving");
  updateSubmissionUI();
  try {
    const response = await fetch("/api/drafts", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || `Draft could not be saved (HTTP ${response.status}).`);

    state.sessionId = result.session_id;
    state.draftVersion = result.draft_version;
    try {
      if (state.assignmentId !== null) {
        window.localStorage.setItem("essayScaffActiveAssignmentId", String(state.assignmentId));
      } else {
        window.localStorage.setItem("essayScaffSessionId", state.sessionId);
      }
    } catch (_error) {
      state.savedSnapshot = snapshot;
      state.restored = false;
      state.restoreIdWarning = true;
      return true;
    }
    state.savedSnapshot = snapshot;
    state.restored = false;
    updateSaveStatus();
    await loadRevisionHistory();
    return true;
  } catch (error) {
    state.saveFailed = true;
    state.saveErrorMessage = error.message || "Draft could not be saved. Please try again.";
    return false;
  } finally {
    state.saving = false;
    saveButton.disabled = false;
    saveRevisionButton.disabled = false;
    updateSaveStatus();
    updateSubmissionUI();
  }
}

saveButton.addEventListener("click", saveDraft);
practiceModeButton.addEventListener("click", selectPracticeMode);
submitEssayButton.addEventListener("click", async () => {
  submissionError.hidden = true;
  submissionError.textContent = "";
  if (state.assignmentId === null || state.submission || state.deletedAssignment || state.submitting || state.saving || state.revisionSaving) return;
  const missingSection = Object.entries(state.drafts).find(([, text]) => !text.trim());
  if (missingSection) {
    const label = missingSection[0].toLowerCase();
    submissionError.textContent = `Write your ${label} before submitting.`;
    submissionError.hidden = false;
    return;
  }
  if (!window.confirm("Submit this saved essay as your final submission? You will not be able to edit it afterward.")) {
    return;
  }

  state.submitting = true;
  cancelAnalysisWork();
  updateSubmissionUI();
  submissionStatus.textContent = "Saving your latest draft…";
  try {
    if (isDirty() || !state.draftVersion) {
      const saved = await saveDraft();
      if (!saved) throw new Error(state.saveErrorMessage || "Save your latest draft before submitting.");
    }
    await writingActivity?.flush();
    const response = await fetch("/api/submissions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify({
        assignment_id: state.assignmentId,
        session_id: state.sessionId,
        draft_version: state.draftVersion,
      }),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Essay could not be submitted.");
    state.submission = result;
    writingActivity?.leaveWorkspace();
    submissionStatus.textContent = "Essay submitted successfully.";
    updateSubmissionUI();
    if (state.currentView === "ESSAY_REVIEW") {
      renderEssayReview();
      void loadWritingActivitySummary();
    }
  } catch (error) {
    submissionError.textContent = error.message || "Essay could not be submitted. Please try again.";
    submissionError.hidden = false;
  } finally {
    state.submitting = false;
    updateSubmissionUI();
  }
});
const initialAppView = window.location?.hash?.slice(1) || document.body.dataset.initialView || "dashboard";
navigateAppView(initialAppView, false);
restoreDraft();

async function saveRevision() {
  if (state.restoring || state.saving || state.revisionSaving || state.submission || state.deletedAssignment) return;
  const draft = currentDraftData();
  const snapshot = JSON.stringify(draft);
  const payload = { ...draft };
  if (state.sessionId) payload.session_id = state.sessionId;

  state.revisionSaving = true;
  state.saveFailed = false;
  state.saveErrorMessage = "";
  state.restoreIdWarning = false;
  saveButton.disabled = true;
  saveRevisionButton.disabled = true;
  revisionSaveStatus.textContent = "Saving revision…";
  updateSubmissionUI();
  try {
    const response = await fetch("/api/revisions", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || `Revision could not be saved (HTTP ${response.status}).`);

    state.sessionId = result.session_id;
    state.draftVersion = result.draft_version;
    try {
      if (state.assignmentId !== null) {
        window.localStorage.setItem("essayScaffActiveAssignmentId", String(state.assignmentId));
      } else {
        window.localStorage.setItem("essayScaffSessionId", state.sessionId);
      }
    } catch (_error) {
      state.restoreIdWarning = true;
    }
    state.savedSnapshot = snapshot;
    state.restored = false;
    revisionSaveStatus.textContent = result.created
      ? `Revision ${result.revision_number} saved.`
      : `No new revision created; this matches Revision ${result.revision_number}.`;
    await loadRevisionHistory();
  } catch (error) {
    revisionSaveStatus.textContent = error.message || "Revision could not be saved. Please try again.";
  } finally {
    state.revisionSaving = false;
    saveButton.disabled = false;
    saveRevisionButton.disabled = false;
    updateSaveStatus();
    updateSubmissionUI();
  }
}

async function loadRevisionHistory() {
  const sessionId = state.sessionId;
  if (!state.sessionId) {
    state.revisionCount = 0;
    state.revisionHistoryStatus = "loaded";
    revisionList.replaceChildren();
    revisionList.hidden = true;
    revisionEmpty.hidden = false;
    revisionEmpty.textContent = "Save a revision to begin your history.";
    if (state.currentView === "ESSAY_REVIEW") renderEssayReview();
    return;
  }
  if (state.revisionCount === null) state.revisionHistoryStatus = "loading";
  try {
    const response = await fetch(`/api/revisions?session_id=${encodeURIComponent(sessionId)}`);
    const result = await response.json().catch(() => ({}));
    if (state.sessionId !== sessionId) return;
    if (!response.ok) throw new Error(result.error || "Revision history could not be loaded.");
    state.revisionCount = result.revisions.length;
    state.revisionHistoryStatus = "loaded";
    revisionList.replaceChildren();
    for (const revision of result.revisions) {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `Revision ${revision.revision_number} — ${formatRevisionDate(revision.created_at)}`;
      button.addEventListener("click", () => viewRevision(revision.revision_id));
      item.appendChild(button);
      revisionList.appendChild(item);
    }
    revisionList.hidden = result.revisions.length === 0;
    revisionEmpty.hidden = result.revisions.length > 0;
    revisionEmpty.textContent = result.revisions.length
      ? ""
      : "No revisions saved yet. Select Save Revision to save a snapshot.";
    if (state.currentView === "ESSAY_REVIEW") renderEssayReview();
  } catch (error) {
    if (state.sessionId !== sessionId) return;
    state.revisionCount = null;
    state.revisionHistoryStatus = "error";
    revisionList.replaceChildren();
    revisionList.hidden = true;
    revisionEmpty.hidden = false;
    revisionEmpty.textContent = error.message || "Revision history could not be loaded.";
    if (state.currentView === "ESSAY_REVIEW") renderEssayReview();
  }
}

async function loadWritingActivitySummary() {
  const assignmentId = state.assignmentId;
  const requestId = ++activitySummaryRequestId;
  if (assignmentId === null) {
    state.writingActivityStatus = "not-recorded";
    state.writingActivitySeconds = null;
    state.writingActivityNote = "Active writing time is recorded only for classroom assignments when tracking is enabled.";
    if (state.currentView === "ESSAY_REVIEW") renderEssayReview();
    return;
  }
  state.writingActivityStatus = "loading";
  state.writingActivityNote = "";
  if (state.currentView === "ESSAY_REVIEW") renderEssayReview();
  try {
    await writingActivity?.flush();
    if (requestId !== activitySummaryRequestId || state.assignmentId !== assignmentId) return;
    const response = await fetch(
      `/api/writing-activity?assignment_id=${encodeURIComponent(assignmentId)}`
    );
    const result = await response.json().catch(() => ({}));
    if (requestId !== activitySummaryRequestId || state.assignmentId !== assignmentId) return;
    if (!response.ok) throw new Error(result.error || "Recorded writing time could not be loaded.");
    const seconds = Number(result.recorded_seconds);
    if (Number.isFinite(seconds) && seconds > 0) {
      state.writingActivityStatus = "recorded";
      state.writingActivitySeconds = Math.round(seconds);
      state.writingActivityNote = "Recorded only while this assignment was open and actively edited. Idle periods are excluded.";
    } else {
      state.writingActivityStatus = "not-recorded";
      state.writingActivitySeconds = null;
      state.writingActivityNote = result.tracking_enabled
        ? "No active writing time has been recorded for this assignment yet."
        : "Writing-time tracking is not enabled for this workspace.";
    }
  } catch (_error) {
    if (requestId !== activitySummaryRequestId || state.assignmentId !== assignmentId) return;
    state.writingActivityStatus = "unavailable";
    state.writingActivitySeconds = null;
    state.writingActivityNote = "Recorded writing time is unavailable right now.";
  }
  if (state.currentView === "ESSAY_REVIEW") renderEssayReview();
}

async function viewRevision(revisionId) {
  if (!state.sessionId) return;
  const sessionId = state.sessionId;
  try {
    const response = await fetch(
      `/api/revisions/${encodeURIComponent(revisionId)}?session_id=${encodeURIComponent(sessionId)}`
    );
    const result = await response.json().catch(() => ({}));
    if (state.sessionId !== sessionId || state.restoring) return;
    if (!response.ok) throw new Error(result.error || "Revision could not be opened.");
    const revision = result;
    revisionPreviewTitle.textContent = `Viewing Revision ${revision.revision_number} — ${formatRevisionDate(revision.created_at)} (read-only)`;
    document.getElementById("preview-introduction").textContent = revision.introduction_text || "(No writing in this stage.)";
    document.getElementById("preview-body").textContent = revision.body_text || "(No writing in this stage.)";
    document.getElementById("preview-conclusion").textContent = revision.conclusion_text || "(No writing in this stage.)";
    revisionPreview.hidden = false;
  } catch (error) {
    if (state.sessionId !== sessionId || state.restoring) return;
    revisionSaveStatus.textContent = error.message || "Revision could not be opened.";
  }
}

function formatRevisionDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

saveRevisionButton.addEventListener("click", saveRevision);

function analysisJobIsCurrent(job) {
  return job.generation === analysisRequestId && state.activeAppView === "workspace"
    && state.currentStage === job.stage && state.currentView === job.stage
    && analysisSnapshot(job.stage) === job.snapshot && currentAssignmentDetails() === job.assignmentDetails
    && writingInput.value === state.drafts[job.stage] && !state.restoring && !state.deletedAssignment
    && !state.submission && !state.submitting;
}

function runStageAnalysis({ automatic = false } = {}) {
  if (liveAnalysisTimer !== null) {
    window.clearTimeout(liveAnalysisTimer);
    liveAnalysisTimer = null;
  }
  if (state.activeAppView !== "workspace" || state.currentView !== state.currentStage
    || state.submission || state.deletedAssignment || state.submitting || state.restoring) return Promise.resolve();
  state.drafts[state.currentStage] = writingInput.value;
  const job = { stage: state.currentStage, snapshot: analysisSnapshot(state.currentStage),
    assignmentDetails: currentAssignmentDetails(), generation: analysisRequestId, automatic };
  if (inFlightAnalysis && inFlightAnalysis.stage === job.stage && inFlightAnalysis.snapshot === job.snapshot
    && inFlightAnalysis.assignmentDetails === job.assignmentDetails) {
    // Identical pending snapshots share one request, including an edit reverted
    // to that exact text/context before the pending response has arrived.
    inFlightAnalysis.generation = job.generation;
    activeAnalysisStage = job.stage;
    queuedStageAnalysis = null;
    clearTutorTypingWork();
    state.tutorAnalysisRunning = true;
    updateTutorPlaceholder();
    return analysisWorkPromise;
  }
  if (state.analyses[job.stage] && state.analysisSnapshots[job.stage] === job.snapshot) {
    displayFeedback(state.analyses[job.stage]);
    return Promise.resolve();
  }
  queuedStageAnalysis = job;
  clearTutorTypingWork();
  if (!analysisWorkPromise) analysisWorkPromise = drainAnalysisQueue();
  else updateTutorPlaceholder();
  return analysisWorkPromise;
}

async function drainAnalysisQueue() {
  try {
    while (queuedStageAnalysis) {
      const job = queuedStageAnalysis;
      queuedStageAnalysis = null;
      if (!analysisJobIsCurrent(job)) continue;
      inFlightAnalysis = job;
      await performStageAnalysis(job);
      inFlightAnalysis = null;
      activeAnalysisController = null;
      activeAnalysisStage = null;
    }
  } finally {
    analysisWorkPromise = null;
  }
}

async function performStageAnalysis(job) {
  const { automatic } = job;
  clearTutorTypingWork();
  errorMessage.hidden = true;
  errorMessage.textContent = "";
  const assignmentTopic = topicInput.value.trim();
  const stage = state.currentStage;
  const stageText = writingInput.value;
  const assignmentDetails = currentAssignmentDetails();
  state.drafts[stage] = stageText;
  const analysisInputsSnapshot = analysisSnapshot(stage);
  if (state.submission || state.deletedAssignment || state.submitting || state.restoring) return;
  if (!assignmentTopic) {
    if (automatic) {
      analysisStatus.textContent = "Add a writing topic before checking this section.";
      if (stage === "INTRODUCTION" && /\p{L}/u.test(stageText)) {
        recordStageAnalysisFailure(stage, analysisInputsSnapshot, "Enter an assignment topic before analyzing.");
      }
      return;
    }
    if (stage === "INTRODUCTION" && /\p{L}/u.test(stageText)) {
      recordStageAnalysisFailure(stage, analysisInputsSnapshot, "Enter an assignment topic before analyzing.");
    }
    errorMessage.textContent = "Enter an assignment topic before analyzing.";
    errorMessage.hidden = false;
    topicInput.focus();
    return;
  }
  if (!stageText.trim()) {
    if (automatic) {
      analysisStatus.textContent = "Write in this section before checking it.";
      return;
    }
    errorMessage.textContent = `Write your ${stageSettings[stage].title.replace("Write Your ", "")} before analyzing it.`;
    errorMessage.hidden = false;
    writingInput.focus();
    return;
  }

  const payload = {
    stage_id: stage,
    assignment_topic: assignmentTopic,
    focus_terms: focusInput.value,
    include_transparency_trace: true,
    [stage === "INTRODUCTION" ? "introduction_text" : stage === "BODY" ? "body_text" : "conclusion_text"]: stageText,
  };
  if (state.assignmentId !== null) payload.assignment_id = state.assignmentId;
  if (stage === "BODY" || stage === "CONCLUSION") payload.introduction_text = state.drafts.INTRODUCTION;
  if (stage === "CONCLUSION") payload.body_text = state.drafts.BODY;

  const controller = typeof AbortController === "function" ? new AbortController() : null;
  activeAnalysisController = controller;
  activeAnalysisStage = stage;
  delete state.analysisFailures[stage];
  state.tutorAnalysisRunning = true;
  state.tutorError = false;
  updateTutorPlaceholder();
  analysisStatus.textContent = "Analyzing your writing…";
  updateIntroductionTutoring();
  try {
    const response = await fetch("/api/analyze-stage", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify(payload),
      ...(controller ? { signal: controller.signal } : {}),
    });
    const result = await response.json().catch(() => ({}));
    if (!analysisJobIsCurrent(job)) return;
    if (!response.ok) throw new Error(result.error || `Analysis could not be completed (HTTP ${response.status}).`);
    if (!result.feedback || !result.analysis || result.stage_id !== stage) {
      throw new Error("The server returned an incomplete analysis. Please try again.");
    }
    const returnedText = tutorSourceText(result)?.source;
    const stageTrace = result.research_trace?.stages?.[stage];
    const hasRecordedText = result.analysis.input_text !== undefined || result.analysis.linguistic_observations?.text !== undefined
      || stageTrace?.linguistic_observations?.text !== undefined;
    if (hasRecordedText && returnedText !== stageText) {
      throw new Error("The returned analysis does not match this draft. Please try again.");
    }
    for (const [section, field] of [["introduction", "introduction_text"], ["body", "body_text"]]) {
      const retainedContext = stageTrace?.input_sections?.[section];
      const isEarlierSection = stage === "CONCLUSION" || (stage === "BODY" && section === "introduction");
      if (isEarlierSection && typeof retainedContext === "string" && retainedContext !== (payload[field] || "")) {
        throw new Error("The returned analysis does not match the earlier-section context. Please try again.");
      }
    }

    if (
      analysisSnapshot(stage) !== analysisInputsSnapshot
      || currentAssignmentDetails() !== assignmentDetails
      || state.currentStage !== stage
      || state.currentView !== stage
      || state.activeAppView !== "workspace"
    ) return;

    state.analyses[stage] = result;
    state.analysisSnapshots[stage] = analysisInputsSnapshot;
    delete state.analysisFailures[stage];
    delete state.tutorStaleStages[stage];
    state.tutorAssignmentStale = false;
    state.tutorError = false;
    feedbackStatus.textContent = "Analysis complete";
    analysisStatus.textContent = "Feedback updated. Your draft was not saved.";
    displayFeedback(result);
    if (stage === "INTRODUCTION") updateIntroductionTutoring();
  } catch (error) {
    if (!analysisJobIsCurrent(job) || error.name === "AbortError") return;
    state.tutorError = true;
    if (stage === "INTRODUCTION") {
      recordStageAnalysisFailure(stage, analysisInputsSnapshot, error.message || "Analysis could not be completed.");
    }
    if (!state.analyses[stage]) displayFeedback(null);
    if (automatic) {
      analysisStatus.textContent = TUTOR_STATE_TEXT.ERROR.title;
      return;
    }
    errorMessage.textContent = error instanceof TypeError
      ? "The server could not be reached. Check that EssayScaff V2 is running and try again."
      : error.message;
    errorMessage.hidden = false;
    analysisStatus.textContent = TUTOR_STATE_TEXT.ERROR.title;
  } finally {
    if (analysisJobIsCurrent(job)) {
      state.tutorAnalysisRunning = false;
      if (activeAnalysisController === controller) activeAnalysisController = null;
      if (activeAnalysisStage === stage) activeAnalysisStage = null;
      analyzeButton.textContent = stageSettings[state.currentStage].button;
      if (state.analyses[state.currentStage]) {
        feedbackPlaceholder.hidden = true;
        feedbackContent.hidden = false;
      } else {
        feedbackContent.hidden = true;
        feedbackPlaceholder.hidden = false;
        updateTutorPlaceholder();
      }
      if (stage === "INTRODUCTION") updateIntroductionTutoring();
    }
  }
}

analyzeButton.addEventListener("click", async () => {
  await runStageAnalysis();
});

function analysisSnapshot(stage) {
  const values = [state.assignmentId, topicInput.value, focusInput.value];
  if (stage !== "INTRODUCTION") values.push(state.drafts.INTRODUCTION);
  if (stage === "CONCLUSION") values.push(state.drafts.BODY);
  values.push(state.drafts[stage]);
  return JSON.stringify(values);
}
