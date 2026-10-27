"""Regression coverage for neutral Introduction feedback and Guided Progression."""

from tests.test_reason_highlighting import _make_stage_payload
from tests.test_workspace_frontend import _run_workspace_frontend
from services.essay_analysis_service import EssayAnalysisService

TOPIC = "Should schools turn part of their playgrounds into vegetable gardens?"
FOCUS = ["schools", "playgrounds", "vegetable gardens", "students", "learning"]
NEUTRAL_TEXT = (
    "Schools should turn part of their playgrounds into vegetable gardens because students can learn "
    "science through planting and develop responsibility by caring for plants. Students can observe how "
    "seeds grow, record changes, and connect these observations to their science lessons. Taking turns "
    "watering and maintaining the garden can also help students practice responsibility."
)
CONCERN_TEXT = "Because students can learn science through planting."
BODY_NEUTRAL_TEXT = (
    "Students learn science by planting seeds and they record changes in a journal "
    "while they care for the garden."
)
BODY_CONCERN_TEXT = "Students learn science by planting seeds.\n\nThey also practice responsibility."
CONCLUSION_NEUTRAL_TEXT = "Gardens help students learn science and responsibility."
CONCLUSION_CONCERN_TEXT = "Students should also sell the vegetables to buy new books."


def _analysis(service, **sections):
    return service.analyze(TOPIC, FOCUS, include_research_trace=True, **sections)


def _branch(result, stage):
    return result["research_trace"]["stages"][stage]["feedback_decisions"]["fields"]["Primary Feedback"]["selection_branch"]


def _responses():
    service = EssayAnalysisService()
    intro_neutral = _analysis(service, introduction_text=NEUTRAL_TEXT)
    intro_concern = _analysis(service, introduction_text=CONCERN_TEXT)
    body_neutral = _analysis(service, introduction_text=NEUTRAL_TEXT, body_text=BODY_NEUTRAL_TEXT)
    body_concern = _analysis(service, introduction_text=NEUTRAL_TEXT, body_text=BODY_CONCERN_TEXT)
    conclusion_neutral = _analysis(service, introduction_text=NEUTRAL_TEXT, body_text=BODY_NEUTRAL_TEXT,
                                   conclusion_text=CONCLUSION_NEUTRAL_TEXT)
    conclusion_concern = _analysis(service, introduction_text=NEUTRAL_TEXT, body_text=BODY_NEUTRAL_TEXT,
                                   conclusion_text=CONCLUSION_CONCERN_TEXT)
    assert _branch(intro_neutral, "INTRODUCTION") == "intro_ideas_point_and_reason"
    assert _branch(intro_concern, "INTRODUCTION") == "intro_sentence_fluency_complete_sentence"
    assert _branch(body_neutral, "BODY") == "body_neutral_observable"
    assert _branch(body_concern, "BODY") == "body_ideas_develop_point"
    assert _branch(conclusion_neutral, "CONCLUSION") == "conclusion_ideas_bring_together"
    assert _branch(conclusion_concern, "CONCLUSION") == "conclusion_ideas_new_words"
    return {
        "INTRO_NEUTRAL": _make_stage_payload(intro_neutral, "INTRODUCTION"),
        "INTRO_CONCERN": _make_stage_payload(intro_concern, "INTRODUCTION"),
        "BODY_NEUTRAL": _make_stage_payload(body_neutral, "BODY"),
        "BODY_CONCERN": _make_stage_payload(body_concern, "BODY"),
        "CONCLUSION_NEUTRAL": _make_stage_payload(conclusion_neutral, "CONCLUSION"),
        "CONCLUSION_CONCERN": _make_stage_payload(conclusion_concern, "CONCLUSION"),
    }


def test_neutral_feedback_guided_progression_and_shared_stage_regressions(tmp_path):
    scenario = r'''
(async () => {
  const allText = (node) => [node.textContent, ...node.children.map(allText)].join(" ");
  const neutral = actualStageResponses.INTRO_NEUTRAL;
  const concern = actualStageResponses.INTRO_CONCERN;
  const neutralText = neutral.analysis.linguistic_observations.text;
  const concernText = concern.analysis.linguistic_observations.text;
  const topic = neutral.analysis.assignment_topic;
  const focus = neutral.analysis.lexical_topic_evidence.focus_terms.join(", ");
  const revisionsBefore = revisions.length;
  const writesBefore = persistenceWrites.length;

  const page = await analyzeGuidedScenario({topic, focus, text: neutralText, response: neutral});
  const e = page.elements;
  const presentation = value(page, "studentFeedbackPresentation(state.analyses.INTRODUCTION)");
  const backend = neutral.research_trace.stages.INTRODUCTION.feedback_decisions.instructional_feedback;

  // Neutral result stays neutral: no trait, lesson, corrective headings or marks.
  assert.equal(presentation.status, "NEUTRAL_OBSERVATION");
  assert.equal(presentation.writing_dimension, null);
  assert.equal(presentation.writing_skill, null);
  assert.equal(presentation.tutor_items[0].neutral_result, true);
  assert.equal(presentation.tutor_items[0].label, "No specific writing issue detected");
  assert.equal(presentation.tutor_items[0].category, null);
  assert.equal(presentation.tutor_items[0].skill, null);
  assert.deepEqual(Object.keys(presentation.displayed_guidance), ["What I noticed", "What's working"]);
  assert.equal(e["tutor-evidence-section"].hidden, true, "no Look at your writing heading");
  assert.equal(e["tutor-why-section"].hidden, true, "no Why it matters heading");
  assert.equal(e["tutor-task-section"].hidden, true, "no How to improve heading");
  assert.equal(e["tutor-working-section"].hidden, false, "applicable positive observation remains");
  assert.equal(e["tutor-working"].textContent, backend.items[0].working_text);
  assert.equal(e["tutor-evidence"].children.length, 0);
  assert.equal(e["tutor-evidence"].querySelectorAll("mark").length, 0);
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length, 0);
  assert.equal(e["feedback-writing-focus"].textContent, "No specific writing issue detected");
  assert.equal(e["feedback-writing-focus"].attributes["aria-label"], "Neutral observation result, not a writing grade");

  // The recorded decision, trait mapping and span stay in the Transparency Inspector.
  assert.equal(JSON.stringify(presentation.instructional_feedback), JSON.stringify(backend));
  assert.equal(presentation.recorded_feedback_decision.selection_branch, "intro_ideas_point_and_reason");
  assert.equal(JSON.stringify(presentation.recorded_feedback_decision),
    JSON.stringify(neutral.research_trace.stages.INTRODUCTION.feedback_decisions.fields["Primary Feedback"]));
  assert.equal(backend.items[0].trait, "Ideas");
  assert.equal(backend.items[0].skill, "Review Your Explanation");
  const recordedSpan = backend.items[0].highlight_spans[0];
  assert.equal(recordedSpan.text, neutralText.slice(recordedSpan.start, recordedSpan.end));
  assert.ok(recordedSpan.text.startsWith("because students can learn science through planting"));
  const inspector = allText(e["nlp-transparency-content"]);
  assert.ok(inspector.includes("Recorded neutral review branch"));
  assert.ok(inspector.includes("Review Your Explanation"), "raw recorded mapping remains visible");
  page.context.currentResponse = neutral;
  page.context.expectedBackend = backend;
  assert.equal(value(page, `(() => {
    const records = [];
    buildFullAnalysisReport(currentResponse, records);
    const value = records.find((record) => record.path.endsWith(".feedback_decisions.instructional_feedback")).value;
    return JSON.stringify(value) === JSON.stringify(analysisReportValue(expectedBackend));
  })()`), true);

  // Guided Progression reuses the recorded neutral result instead of Review Suggested.
  assert.equal(e["guided-state-label"].dataset.state, "NEUTRAL");
  assert.equal(e["guided-state-label"].textContent, "No Specific Issue Detected");
  assert.match(e["guided-state-message"].textContent, /did not identify a specific writing concern/);
  assert.equal(e["guided-review-suggestions"].hidden, true, "no unsupported revision warning");
  assert.equal(e["guided-continue-to-body"].hidden, false, "Continue to Body stays accessible");
  assert.equal(e["guided-continue-anyway"].hidden, true);
  assert.equal(e["stage-progress-title"].textContent, "No Specific Writing Issue Detected");
  assert.equal(e["stage-progress-badge"].dataset.state, "NO_ISSUE");
  assert.equal(e["stage-progress-review"].hidden, true);

  // Editing after analysis withdraws the old neutral result instead of showing it as current.
  e["stage-text"].value = neutralText + " More.";
  await input(e["stage-text"]);
  assert.equal(e["guided-state-label"].dataset.state, "CHECKING");
  assert.equal(e["feedback-content"].hidden, true);
  assert.equal(e["stage-progress-title"].textContent, "Ready to Review Your Writing?");
  assert.equal(e["stage-progress-review"].hidden, true);
  e["stage-text"].value = neutralText;
  await input(e["stage-text"]);
  analysisResponseOverride = neutral;
  await runTimers(page, 6000);
  assert.equal(e["guided-state-label"].dataset.state, "NEUTRAL", "the fresh neutral analysis is current again");

  // Completing both self-checks still produces the completion state and a working Continue.
  e["guided-position-confirmed"].checked = true;
  await change(e["guided-position-confirmed"]);
  e["guided-direction-confirmed"].checked = true;
  await change(e["guided-direction-confirmed"]);
  assert.equal(e["guided-state-label"].dataset.state, "CHECKLIST_COMPLETE");
  assert.equal(e["guided-continue-to-body"].hidden, false);
  assert.equal(e["guided-review-suggestions"].hidden, true);
  await click(e["guided-continue-to-body"]);
  assert.equal(value(page, "state.currentStage"), "BODY");
  assert.equal(revisions.length, revisionsBefore, "viewing feedback and continuing create no revision");
  assert.equal(persistenceWrites.length, writesBefore, "viewing feedback and continuing save nothing");

  // Shared Body neutral path still hides corrective sections and marks no error.
  await click(page.tabs[1]);
  const bodyNeutral = actualStageResponses.BODY_NEUTRAL;
  e["stage-text"].value = bodyNeutral.research_trace.stages.BODY.linguistic_observations.text;
  await input(e["stage-text"]);
  analysisResponseOverride = bodyNeutral;
  await click(e["analyze-button"]);
  const bodyPresentation = value(page, "studentFeedbackPresentation(state.analyses.BODY)");
  assert.equal(bodyPresentation.status, "NO_SUPPORTED_CONCERN_SELECTED");
  assert.equal(e["tutor-evidence-section"].hidden, true);
  assert.equal(e["tutor-why-section"].hidden, true);
  assert.equal(e["tutor-task-section"].hidden, true);
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length, 0);
  assert.equal(e["stage-progress-title"].textContent, "No Specific Writing Issue Detected");
  assert.equal(e["stage-progress-review"].hidden, true);
  assert.equal(revisions.length, revisionsBefore);
  assert.equal(persistenceWrites.length, writesBefore);

  // Shared Conclusion concern path still renders the full corrective guidance.
  await click(page.tabs[2]);
  const conclusionConcern = actualStageResponses.CONCLUSION_CONCERN;
  e["stage-text"].value = conclusionConcern.research_trace.stages.CONCLUSION.linguistic_observations.text;
  await input(e["stage-text"]);
  analysisResponseOverride = conclusionConcern;
  await click(e["analyze-button"]);
  const conclusionPresentation = value(page, "studentFeedbackPresentation(state.analyses.CONCLUSION)");
  assert.equal(conclusionPresentation.status, "PREPARED_INLINE_GUIDANCE");
  assert.deepEqual(Object.keys(conclusionPresentation.displayed_guidance),
    ["What I noticed", "Look at your writing", "Why it matters", "How to improve"]);
  assert.equal(e["tutor-evidence-section"].hidden, false);
  assert.equal(e["tutor-why-section"].hidden, false);
  assert.equal(e["tutor-task-section"].hidden, false);
  assert.equal(e["stage-progress-title"].textContent, "Review Suggested");
  assert.equal(e["stage-progress-review"].hidden, false);
  assert.equal(revisions.length, revisionsBefore);
  assert.equal(persistenceWrites.length, writesBefore);

  // A genuine Introduction concern keeps Review Suggested, Review Writing and Continue.
  await click(page.tabs[0]);
  e["stage-text"].value = concernText;
  await input(e["stage-text"]);
  analysisResponseOverride = concern;
  await click(e["analyze-button"]);
  const concernPresentation = value(page, "studentFeedbackPresentation(state.analyses.INTRODUCTION)");
  assert.equal(concernPresentation.status, "PREPARED_INLINE_GUIDANCE");
  assert.equal(concernPresentation.writing_dimension, "Sentence Fluency");
  assert.equal(concernPresentation.writing_skill, "Complete Your Sentence");
  assert.deepEqual(Object.keys(concernPresentation.displayed_guidance),
    ["What I noticed", "Look at your writing", "Why it matters", "How to improve"]);
  assert.equal(e["tutor-evidence-section"].hidden, false);
  assert.equal(e["tutor-why-section"].hidden, false);
  assert.equal(e["tutor-task-section"].hidden, false);
  assert.ok(e["editor-mirror"].querySelectorAll("mark").length >= 1);
  assert.ok(e["tutor-evidence"].querySelectorAll("mark").length >= 1);
  assert.equal(e["guided-state-label"].dataset.state, "REVIEW_SUGGESTED");
  assert.equal(e["guided-review-suggestions"].hidden, false);
  assert.equal(e["guided-continue-anyway"].hidden, false);
  assert.equal(e["guided-continue-to-body"].hidden, true);
  assert.equal(e["stage-progress-title"].textContent, "Review Suggested");
  assert.equal(e["stage-progress-review"].hidden, false);
  await click(e["stage-progress-review"]);
  assert.equal(e["stage-text"].focused, true, "Review Writing stays functional");
  await click(e["stage-progress-continue"]);
  assert.equal(value(page, "state.currentStage"), "BODY");
  assert.equal(revisions.length, revisionsBefore);
  assert.equal(persistenceWrites.length, writesBefore);
  console.log("Feedback presentation scenarios completed.");
})().catch((error) => { console.error(error); process.exitCode = 1; });
'''
    _run_workspace_frontend(tmp_path, scenario, _responses())
