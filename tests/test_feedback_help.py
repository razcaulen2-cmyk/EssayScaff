"""S5.1 uses recorded feedback and existing local tutoring content, not new NLP."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from app import create_app
from services.essay_analysis_service import EssayAnalysisService
from services.introduction_rules import CLAUSE_SUBORDINATORS
from services.tutoring_lessons import load_feedback_help
from tests.auth_helpers import register_student
from tests.test_nlp_transparency import (
    PLASTICS_TOPIC, PLASTICS_FOCUS, PLASTICS_INTRODUCTION, PLASTICS_BODY, PLASTICS_CONCLUSION,
)
from tests.test_workspace_frontend import NODE, _run_workspace_frontend


PLASTICS_REASON_INTRO = (
    "Single-use plastics are everywhere in our communities. Communities should reduce their use "
    "of these plastics because plastic waste harms our environment."
)


@pytest.fixture(scope="module")
def help_responses(tmp_path_factory):
    app = create_app(EssayAnalysisService(), secret_key="s51-isolated-help")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path_factory.mktemp("feedback-help") / "help.sqlite3"))
    client = app.test_client()
    assert register_student(client, "s51_student").status_code == 302
    cases = [
        ("point", "INTRODUCTION", {"introduction_text": "Communities should reduce single-use plastics."}),
        ("one_sentence", "INTRODUCTION", {"introduction_text": "Communities."}),
        ("no_root", "INTRODUCTION", {"introduction_text": "Communities. Plastics."}),
        ("reason", "INTRODUCTION", {"introduction_text": PLASTICS_REASON_INTRO}),
        ("subordinator", "INTRODUCTION", {"introduction_text": "Throwing away plastic waste on communities is very harmful in the environment. Because it can effect rivers, animals, plants ect."}),
        ("subordinator_clean", "INTRODUCTION", {"introduction_text": "Communities should reduce plastic waste because it can affect rivers and animals."}),
        ("because_fragment", "INTRODUCTION", {"introduction_text": "Because plastic waste harms rivers."}),
        ("although_fragment", "INTRODUCTION", {"introduction_text": "Although communities reduce single-use plastics."}),
        ("if_fragment", "INTRODUCTION", {"introduction_text": "If communities reduce plastic waste."}),
        ("because_complete", "INTRODUCTION", {"introduction_text": "Communities should reduce plastic waste because it harms rivers."}),
        ("although_complete", "INTRODUCTION", {"introduction_text": "Although plastic is convenient, communities should reduce its use."}),
        ("parser_false_positive", "INTRODUCTION", {"introduction_text": "Because plastic waste harms rivers, communities should reduce their use of it."}),
        ("multiple_markers", "INTRODUCTION", {"introduction_text": "Because plastic waste harms rivers. Although communities reduce single-use plastics."}),
        ("unicode_marker", "INTRODUCTION", {"introduction_text": "🌍 Communities reduce waste. Although communities reduce single-use plastics."}),
        ("detail", "BODY", {"introduction_text": PLASTICS_INTRODUCTION, "body_text": "Communities reduce single-use plastics."}),
        ("connection", "BODY", {"introduction_text": PLASTICS_INTRODUCTION, "body_text": "Communities reduce plastics. Residents reuse bags.\n\nOrchestras perform symphonies. Musicians practice instruments."}),
        ("closure", "CONCLUSION", {"conclusion_text": "Overall, communities should reduce single-use plastics."}),
        ("synthesis", "CONCLUSION", {"introduction_text": PLASTICS_INTRODUCTION, "body_text": PLASTICS_BODY, "conclusion_text": PLASTICS_CONCLUSION}),
        ("unsupported", "INTRODUCTION", {"introduction_text": "Public buses carry commuters."}),
        ("uncertain", "INTRODUCTION", {"introduction_text": "!!!"}),
        ("no_trace", "INTRODUCTION", {"introduction_text": PLASTICS_INTRODUCTION, "include_transparency_trace": False}),
        ("body_unmapped", "BODY", {"introduction_text": PLASTICS_INTRODUCTION, "body_text": "Communities reduce plastics. Reusable bags reduce waste."}),
        ("conclusion_unmapped", "CONCLUSION", {"introduction_text": PLASTICS_INTRODUCTION, "body_text": PLASTICS_BODY, "conclusion_text": PLASTICS_CONCLUSION + " Satellites explore distant galaxies."}),
    ]
    cases.extend(
        (f"marker_{marker}", "INTRODUCTION", {"introduction_text": f"{marker.capitalize()} communities reduce plastic waste."})
        for marker in sorted(CLAUSE_SUBORDINATORS)
    )
    results = {}
    for name, stage, fields in cases:
        response = client.post("/api/analyze-stage", json={
            "stage_id": stage, "assignment_topic": PLASTICS_TOPIC, "focus_terms": PLASTICS_FOCUS,
            "include_transparency_trace": True, **fields,
        })
        assert response.status_code == 200
        results[name] = response.get_json()
    return results


def test_prepared_catalog_retains_content_and_adds_concise_instructional_guidance():
    catalog = load_feedback_help()
    assert catalog["availability"] == "AVAILABLE"
    assert catalog["version"] == 6
    assert len(catalog["lessons"]) == 19
    assert len(catalog["bindings"]) == 19
    assert len(catalog["secondary_bindings"]) == 10
    assert {item["feedback_field"] for item in catalog["bindings"]} == {"Primary Feedback"}
    assert "Shute (2008)" in " ".join(catalog["educational_basis"])
    assert "Education Northwest" in " ".join(catalog["educational_basis"])
    for lesson in catalog["lessons"]:
        assert not {"questions", "definitions", "why", "revision_task", "practice", "answers",
                    "quiz", "score", "mastery", "replacement_text", "example_paragraph"} & lesson.keys()
        assert lesson["title"] and lesson["limitation"]
        guidance = lesson["inline_guidance"]
        words = " ".join(guidance[key] for key in ("goal", "question", "explanation", "next_step"))
        assert 40 <= len(words.split()) <= 70
        assert guidance["limitation"]
        assert all(term not in words.lower() for term in ("sentence-part patterns", "lexical", "root subject", "semantic inconsistency"))
        assert set(lesson["tutor"]) >= {"noticed", "why", "task", "limitation"}
        assert not {"try", "check", "try_fallback"} & lesson["tutor"].keys()
    assert {binding["dimension"] for binding in catalog["bindings"]} == {
        "Ideas", "Organization", "Sentence Fluency", "Word Choice"}
    assert all(binding["dimension"] in {"Ideas", "Organization", "Sentence Fluency", "Word Choice", "Conventions"}
               for binding in catalog["secondary_bindings"])
    assert all(lesson["tutor"].get("evidence_fallback") for lesson in catalog["lessons"])


@pytest.mark.parametrize("case, lesson_id", [
    ("point", "HELP-INTRO-DEVELOP-POINT"), ("one_sentence", "HELP-INTRO-MAIN-POINT"), ("no_root", "HELP-INTRO-MAIN-POINT"),
    ("reason", "HELP-INTRO-EXPLAIN-POINT"), ("detail", "HELP-BODY-DEVELOP-POINT"),
    ("connection", "HELP-BODY-PARAGRAPH-LINK"), ("closure", "HELP-CONCLUSION-CLEAR-ENDING"),
    ("synthesis", "HELP-CONCLUSION-BRING-TOGETHER"), ("subordinator", "HELP-INTRO-COMPLETE-SENTENCE"),
    ("unsupported", "HELP-TOPIC-MATCH"),
])
def test_each_mapping_is_exercised_by_real_feedback_and_emitted_provenance(help_responses, case, lesson_id):
    result = help_responses[case]
    stage = result["stage_id"]
    decision = result["research_trace"]["stages"][stage]["feedback_decisions"]["fields"]["Primary Feedback"]
    binding = next(item for item in load_feedback_help()["bindings"] if item["stage_id"] == stage and item["selection_branch"] == decision["selection_branch"])
    assert binding["lesson_id"] == lesson_id
    expected_dimensions = {
        "point": ("Ideas", "Develop Your Main Point"), "one_sentence": ("Ideas", "State Your Main Point"),
        "no_root": ("Ideas", "State Your Main Point"), "reason": ("Ideas", "Review Your Explanation"),
        "detail": ("Ideas", "Develop Your Supporting Details"), "connection": ("Organization", "Review Paragraph Connections"),
        "closure": ("Organization", "Clear Ending"), "synthesis": ("Ideas", "Bring Ideas Together"),
        "subordinator": ("Sentence Fluency", "Complete Your Sentence"), "unsupported": ("Ideas", "Match Your Topic"),
    }
    assert (binding["dimension"], binding["skill"]) == expected_dimensions[case]
    assert binding["mapping_basis"]
    assert decision["selected_message"] == result["feedback"]["Primary Feedback"]
    events = {item["rule_id"] for item in result["analysis"]["rule_evidence"] if item.get("triggered", True) and item.get("fired", True)}
    links = {item["rule_id"] for item in result["feedback"]["Feedback Provenance"] if item["feedback_field"] == "Primary Feedback"}
    assert decision["rule_ids"] and set(decision["rule_ids"]) <= events & links
    # The API's analysis and five messages contain no educational replacement.
    assert "learning_help" not in result["analysis"] and "lesson" not in result["feedback"]


@pytest.mark.parametrize("case, branch", [
    ("body_unmapped", "body_neutral_observable"),
    ("uncertain", "intro_neutral_punctuation"),
])
def test_real_unmapped_branches_are_not_categorized_from_stage_alone(help_responses, case, branch):
    result = help_responses[case]
    stage = result["stage_id"]
    assert result["research_trace"]["stages"][stage]["feedback_decisions"]["fields"]["Primary Feedback"]["selection_branch"] == branch
    assert not any(item["stage_id"] == stage and item["selection_branch"] == branch for item in load_feedback_help()["bindings"])


def test_new_word_branch_selects_the_new_words_lesson(help_responses):
    result = help_responses["conclusion_unmapped"]
    decision = result["research_trace"]["stages"]["CONCLUSION"]["feedback_decisions"]["fields"]["Primary Feedback"]
    assert decision["selection_branch"] == "conclusion_ideas_new_words"
    binding = next(item for item in load_feedback_help()["bindings"] if item["stage_id"] == "CONCLUSION" and item["selection_branch"] == decision["selection_branch"])
    assert (binding["lesson_id"], binding["dimension"], binding["skill"]) == ("HELP-CONCLUSION-EXPLAIN-NEW-WORDS", "Ideas", "Explain New Words")


def test_incomplete_subordinator_guidance_is_grammatically_precise(help_responses):
    """The Because-sentence may hold a complete reason clause that still needs a main clause."""
    result = help_responses["subordinator"]
    stage = result["stage_id"]
    decision = result["research_trace"]["stages"][stage]["feedback_decisions"]["fields"]["Primary Feedback"]
    assert decision["selection_branch"] == "intro_sentence_fluency_complete_sentence"
    binding = next(item for item in load_feedback_help()["bindings"] if item["selection_branch"] == "intro_sentence_fluency_complete_sentence")
    lesson = next(item for item in load_feedback_help()["lessons"] if item["lesson_id"] == binding["lesson_id"])
    guidance = lesson["inline_guidance"]
    assert (binding["dimension"], binding["skill"]) == ("Sentence Fluency", "Complete Your Sentence")
    assert guidance["question"] == "Check whether this sentence needs a complete main statement."
    assert guidance["explanation"] == "A sentence part that starts a thought needs the main part of the sentence to finish it."
    assert guidance["next_step"] == "Read the words after the starting word and finish the thought in your own words."
    # Original backend wording is preserved separately and never replaced in the API.
    assert result["feedback"]["Primary Feedback"] == decision["selected_message"]
    assert "Because" in decision["selected_message"]
    # The rule evidence records the actual attachments that justified the branch.
    event = next(item for item in result["analysis"]["rule_evidence"] if item["rule_id"] == "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR")
    assert event["triggered"] is True
    evidence = event["evidence"][0]
    assert evidence["text"] == "Because" and evidence["pos"] == "SCONJ" and evidence["dependency"] == "mark"


def test_clean_reason_sentences_do_not_trigger_the_subordinator_branch(help_responses):
    """A complete main clause before or after the reason keeps the branch unselected."""
    clean = help_responses["subordinator_clean"]
    stage = clean["stage_id"]
    decision = clean["research_trace"]["stages"][stage]["feedback_decisions"]["fields"]["Primary Feedback"]
    assert decision["selection_branch"] != "intro_sentence_fluency_complete_sentence"
    assert not any(
        item["rule_id"] == "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR" and item.get("triggered", True)
        for item in clean["analysis"]["rule_evidence"]
    )


@pytest.fixture(scope="module")
def manual_introduction_responses(tmp_path_factory):
    samples = json.loads(Path(__file__).with_name("introduction_tutor_cases.json").read_text(encoding="utf-8"))
    app = create_app(EssayAnalysisService(), secret_key="manual-introduction-tutor")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path_factory.mktemp("intro-tutor") / "isolated.sqlite3"))
    client = app.test_client()
    assert register_student(client, "manual_tutor_student").status_code == 302
    results = {}
    for name, text in samples["cases"].items():
        response = client.post("/api/analyze-stage", json={
            "stage_id": "INTRODUCTION", "assignment_topic": samples["assignment_topic"],
            "focus_terms": samples["focus_terms"], "introduction_text": text, "include_transparency_trace": True,
        })
        assert response.status_code == 200
        results[name] = response.get_json()
    return results


@pytest.mark.parametrize("case, branch, rule, lesson", [
    ("long_although", "intro_sentence_fluency_complete_sentence", "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR", "HELP-INTRO-COMPLETE-SENTENCE"),
    ("cafeteria_although", "intro_sentence_fluency_complete_sentence", "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR", "HELP-INTRO-COMPLETE-SENTENCE"),
    ("keyword_list", "intro_organization_topic_intro", "INTRO.TEXT.KEYWORD_LIST_CANDIDATE", "HELP-INTRO-TOPIC-INTRO"),
    # Argumentative assignment with no recorded position cue now selects the
    # neutral State Your Position review before the development task.
    ("main_point", "intro_ideas_state_position", "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED", "HELP-INTRO-STATE-POSITION"),
    ("cafeteria_complete", "intro_ideas_topic_match", "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED", "HELP-TOPIC-MATCH"),
])
def test_manual_introduction_cases_use_actual_branches_and_rule_evidence(manual_introduction_responses, case, branch, rule, lesson):
    result = manual_introduction_responses[case]
    decision = result["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]["fields"]["Primary Feedback"]
    assert decision["selection_branch"] == branch
    assert decision["selected_message"] == result["feedback"]["Primary Feedback"]
    assert rule in decision["rule_ids"]
    event = next(event for event in result["analysis"]["rule_evidence"] if event["rule_id"] == rule)
    assert event["triggered"] is True
    binding = next(binding for binding in load_feedback_help()["bindings"] if binding["selection_branch"] == branch)
    assert binding["lesson_id"] == lesson
    if case.startswith("cafeteria"):
        lexical = result["analysis"]["lexical_topic_evidence"]
        assert lexical["observed_unique_focus_terms"] == 0
        assert lexical["total_unique_focus_terms"] == 5
        assert lexical["matches"] == []
    if case == "keyword_list":
        spans = event["evidence"]
        assert len(spans) == 7
        source = result["analysis"]["linguistic_observations"]["text"]
        assert all(source[span["start"]:span["end"]] == span["text"] for span in spans)
    if case == "main_point":
        assert result["analysis"]["linguistic_observations"]["counts"]["sentence_count"] == 1
        assert result["analysis"]["development_evidence"]["predicate_count"] == 1
        assert result["analysis"]["position_statement_evidence"]["status"] == "NO_RELEVANT_POSITION_OBSERVED"
        assert "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED" in decision["rule_ids"]


@pytest.mark.skipif(NODE is None, reason="Node.js is required for real tutor rendering")
def test_manual_introduction_explanations_evidence_and_safe_highlights(tmp_path, manual_introduction_responses):
    scenario = r'''
(async () => {
  const page=makeWorkspace(fetch,new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements;
  const cases=actualStageResponses.MANUAL_INTRODUCTIONS;
  const show=response=>{
    page.context.currentResponse=response;
    e["stage-text"].value=response.analysis.linguistic_observations.text;
    value(page,`state.currentStage="INTRODUCTION";state.currentView="INTRODUCTION";displayFeedback(currentResponse)`);
    return value(page,"studentFeedbackPresentation(currentResponse)");
  };
  for(const name of ["long_although","cafeteria_although","keyword_list","main_point","cafeteria_complete"]) {
    const response=cases[name], original=JSON.stringify(response);
    const model=show(response),items=model.tutor_items;
    assert.equal(JSON.stringify(response),original,"presentation preserves original backend response");
    assert.equal(e["feedback-writing-focus"].hidden,items.length>1);
    assert.equal(e["tutor-tabs"].querySelectorAll("button").length,items.length>1?items.length:0);
    assert.equal(e["tutor-why"].textContent.includes("These checks recorded an observation"),false);
    if(name==="keyword_list") {
      assert.equal(items[0].label,"Organization · Introduce Your Topic");
      assert.equal(e["editor-mirror"].querySelectorAll("mark").length,7);
      assert.match(items[0].why,/which subject/);
      assert.match(items[0].task_text,/one sentence about it/);
    } else if(name==="main_point") {
      assert.equal(items[0].lesson_id,"HELP-INTRO-STATE-POSITION");
      assert.equal(items[0].label,"Ideas · State Your Position");
      assert.match(items[0].noticed,/could not identify a clear position/);
      assert.equal(e["editor-mirror"].querySelector("mark").textContent,response.analysis.linguistic_observations.text);
      assert.match(items[0].why,/where you stand/);
      assert.match(items[0].task_text,/support or oppose/);
    } else if(name.includes("although")) {
      const target=response.analysis.linguistic_observations.sentences.find(s=>s.text.startsWith("Although"));
      assert.equal(e["editor-mirror"].querySelector("mark").textContent,target.text);
    }
    const vocabularyIndex=items.findIndex(item=>item.lesson_id==="HELP-TOPIC-MATCH");
    if(name.startsWith("cafeteria")) {
      assert.ok(vocabularyIndex>=0);
      if(vocabularyIndex) await dispatch(e["tutor-tabs"].children[vocabularyIndex],"click");
      const item=items[vocabularyIndex];
      assert.match(item.evidence_text,/0 of 5 configured focus terms/);
      assert.match(item.evidence_text,/smartphones, students, classroom, learning, distractions/);
      assert.equal(item.excerpt,null);
      assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0);
      assert.match(e["tutor-task"].textContent,/do not need to insert every assignment word literally/);
    }
  }
  for(const name of ["keyword_list","main_point"]) {
    const response=JSON.parse(JSON.stringify(cases[name]));
    const rule=name==="keyword_list"?"INTRO.TEXT.KEYWORD_LIST_CANDIDATE":"INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE";
    const evidence=response.analysis.rule_evidence.find(event=>event.rule_id===rule).evidence;
    if(name==="keyword_list") evidence[0].start=99999;
    else evidence[0].sentence_end=99999;
    const item=show(response).tutor_items[0];
    assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0);
    assert.equal(item.evidence_text.includes("I could not point"),false,"meaningful lesson-specific evidence fallback");
  }
  const unsupported=JSON.parse(JSON.stringify(cases.keyword_list));
  unsupported.research_trace.stages.INTRODUCTION.feedback_decisions.fields["Primary Feedback"].rule_ids=["INTRO.GOAL.OBSERVABLE_INTRODUCTION"];
  show(unsupported);
  assert.equal(value(page,"selectScaffoldingGuidance(currentResponse)"),null,"keyword label requires its actual rule, not just a branch name");
  const inconsistent=JSON.parse(JSON.stringify(cases.cafeteria_complete));
  inconsistent.analysis.lexical_topic_evidence.observed_unique_focus_terms=4;
  const summary=show(inconsistent).tutor_items[0];
  assert.match(summary.evidence_text,/unavailable or inconsistent/);
  assert.equal(summary.evidence_text.includes("0 of 5"),false,"do not invent counts from contradictory metadata");
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario, {"MANUAL_INTRODUCTIONS": manual_introduction_responses})


@pytest.mark.parametrize("problem", ["missing", "invalid_json", "invalid_marker_slot", "duplicate_marker_slot", "unknown_lesson", "duplicate_binding", "bad_version", "missing_guidance", "invalid_dimension", "missing_mapping_basis"])
def test_optional_catalog_failure_disables_help_without_breaking_existing_lesson(tmp_path, monkeypatch, problem):
    import services.tutoring_lessons as content
    catalog = deepcopy(load_feedback_help())
    path = tmp_path / "optional-help.json"
    if problem == "invalid_marker_slot":
        catalog["lessons"][0]["inline_guidance"]["marker_question"] = "Missing slot"
    elif problem == "duplicate_marker_slot":
        catalog["lessons"][0]["inline_guidance"]["marker_question"] = "{marker} {marker}"
    elif problem == "unknown_lesson":
        catalog["bindings"][0]["lesson_id"] = "UNKNOWN"
    elif problem == "duplicate_binding":
        catalog["bindings"].append(dict(catalog["bindings"][0]))
    elif problem == "bad_version":
        catalog["version"] = True
    elif problem == "missing_guidance":
        del catalog["lessons"][0]["inline_guidance"]["explanation"]
    elif problem == "invalid_dimension":
        catalog["bindings"][0]["dimension"] = "NLP Quality Score"
    elif problem == "missing_mapping_basis":
        del catalog["bindings"][0]["mapping_basis"]
    if problem != "missing":
        path.write_text("{" if problem == "invalid_json" else json.dumps(catalog), encoding="utf-8")
    monkeypatch.setattr(content, "_FEEDBACK_HELP_PATH", path)
    load_feedback_help.cache_clear()
    try:
        assert load_feedback_help()["availability"] == "UNAVAILABLE"
        assert content.load_introduction_lesson()["lesson_id"] == "INTRO-LESSON-001"
    finally:
        load_feedback_help.cache_clear()


def test_student_page_removes_help_interaction_and_keeps_three_feedback_sections(tmp_path):
    app = create_app(secret_key="s51-template")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "template.sqlite3"))
    client = app.test_client()
    assert register_student(client, "s51_template_student").status_code == 302
    html = client.get("/").get_data(as_text=True)
    assert 'id="help-me-understand"' not in html and 'id="feedback-help-panel"' not in html
    assert 'id="feedback-writing-focus"' in html and 'id="scaffolding-guidance-definition" type="application/json"' in html
    assert html.index('id="tutor-noticed"') < html.index('id="tutor-evidence"') < html.index('id="tutor-why"') < html.index('id="tutor-task"')
    assert 'id="introduction-lesson-definition"' in html and 'id="copy-full-analysis"' in html
    root = Path(__file__).resolve().parents[1]
    script = (root / "static" / "app.js").read_text(encoding="utf-8")
    style = (root / "static" / "style.css").read_text(encoding="utf-8")
    assert "feedbackHelpButton" not in script and "function renderFeedbackHelp" not in script
    assert ".feedback-help-panel" not in style and ".feedback-help-section" not in style


@pytest.mark.skipif(NODE is None, reason="Node.js is required for real app.js DOM behavior")
def test_inline_guidance_selection_exact_trace_authorship_and_lifecycle(tmp_path, help_responses):
    scenario = r'''
(async () => {
  let calls=0;
  const page=makeWorkspace((...args)=>{calls++;return fetch(...args);},new Map());
  await waitForRestoration(page);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements;
  const walk=element=>[element,...element.children.flatMap(walk)];
  const text=element=>walk(element).map(item=>item.textContent).join("\n");
  const show=response=>{
    page.context.currentResponse=response;
    e["assignment-topic"].value=response.analysis.assignment_topic;
    e["focus-terms"].value=response.analysis.lexical_topic_evidence.focus_terms.join(", ");
    const linguistic=response.analysis.linguistic_observations||response.research_trace?.stages?.[response.stage_id]?.linguistic_observations;
    e["stage-text"].value=linguistic?.text || "";
    value(page,`state.currentStage=currentResponse.stage_id; state.currentView=currentResponse.stage_id;
      if(state.currentStage!=="INTRODUCTION") state.drafts.INTRODUCTION=currentResponse.research_trace?.stages?.[state.currentStage]?.input_sections?.introduction||"";
      if(state.currentStage==="CONCLUSION") state.drafts.BODY=currentResponse.research_trace?.stages?.[state.currentStage]?.input_sections?.body||"";
      state.drafts[state.currentStage]=document.getElementById("stage-text").value;
      state.analyses[state.currentStage]=currentResponse;
      state.analysisSnapshots[state.currentStage]=analysisSnapshot(state.currentStage);
      displayFeedback(currentResponse);`);
  };
  const serial=value=>JSON.parse(JSON.stringify(value));
  const presentationPath="frontend.studentFeedbackPresentation (prepared catalog + selected-stage response)";
  const supported={point:["Ideas","Develop Your Main Point"],one_sentence:["Ideas","State Your Main Point"],no_root:["Ideas","State Your Main Point"],reason:["Ideas","Review Your Explanation"],detail:["Ideas","Develop Your Supporting Details"],connection:["Organization","Review Paragraph Connections"],closure:["Organization","Clear Ending"],synthesis:["Ideas","Bring Ideas Together"],subordinator:["Sentence Fluency","Complete Your Sentence"],unsupported:["Ideas","Match Your Topic"]};
  for(const [name,[dimension,skill]] of Object.entries(supported)) {
    const response=actualStageResponses.HELP_CASES[name];
    show(response);
    const original=JSON.stringify(response),editor=e["stage-text"].value,state=value(page,"JSON.stringify(state)"),dirty=value(page,"isDirty()"),timers=page.timers.size,before=calls;
    e["feedback-details"].open=true;
    const selected=value(page,"selectScaffoldingGuidance(currentResponse)");
    const presentation=value(page,"studentFeedbackPresentation(currentResponse)");
    const neutral=presentation.status==="NEUTRAL_OBSERVATION";
    if(neutral) {
      assert.equal(presentation.writing_dimension,null,"a recorded neutral review keeps no corrective trait");
      assert.equal(presentation.writing_skill,null,"a recorded neutral review keeps no corrective lesson");
      assert.equal(e["feedback-writing-focus"].textContent,"No specific writing issue detected");
    } else {
      assert.equal(presentation.writing_dimension,dimension);
      assert.equal(presentation.writing_skill,skill);
      assert.equal(e["feedback-writing-focus"].textContent,`${dimension} · ${skill}`);
    }
    assert.equal(e["feedback-writing-focus"].hidden,presentation.tutor_items.length > 1,"multiple concerns have one title per tab");
    const primary=presentation.tutor_items[0];
    assert.equal(e["tutor-noticed"].textContent,primary.noticed);
    assert.equal(e["tutor-why"].textContent,primary.why);
    assert.equal(e["tutor-task"].textContent,primary.task_text);
    assert.equal(e["tutor-limitation"].textContent,primary.limitation);
    assert.equal(e["interpretation-limit"].textContent,presentation.displayed_limitation);
    if(!neutral) {
      const guidance=selected.content.inline_guidance;
      const words=[guidance.goal,guidance.question,guidance.explanation,guidance.next_step].join(" ").split(/\s+/);
      assert.ok(words.length>=40&&words.length<=70,"concise priority guidance, excluding headings/limitation");
    }
    assert.match(presentation.dimension_role,/not a validated NLP/);
    assert.deepEqual(serial(presentation.original_feedback),response.feedback && Object.fromEntries(["Current Goal","Primary Feedback","What's Working","Needs Attention","Next Step"].map(field=>[field,response.feedback[field]])));
    assert.deepEqual(serial(presentation.supporting_rule_events),response.analysis.rule_evidence.filter(event=>presentation.rule_ids.includes(event.rule_id)));
    const techPanel=walk(e["nlp-transparency-content"]).find(item=>item.dataset.subPanel==="engine:primary");
    const compareTable=walk(techPanel).find(item=>item.tagName==="TABLE"&&walk(item).some(cell=>cell.textContent==="Exact displayed guidance"));
    const techRows=walk(compareTable).find(item=>item.tagName==="TBODY").children;
    const guidanceEntries=neutral
      ? [["What I noticed",primary.noticed],...(primary.working_text?[["What's working",primary.working_text]]:[])]
      : [["What I noticed",primary.noticed],["Look at your writing",primary.evidence_text],["Why it matters",primary.why],["How to improve",primary.task_text]];
    for(const [i,[heading,shown]] of guidanceEntries.entries()) {
      assert.equal(techRows[i].children[2].textContent,shown,"transparency equals visible student text");
      assert.equal(presentation.displayed_guidance[heading],shown);
    }
    assert.equal(Object.keys(presentation.displayed_guidance).length,guidanceEntries.length,"presentation shows only the sections that apply");
    const report=value(page,"buildFullAnalysisReport(currentResponse)");
    assert.deepEqual(reportRecord(report,presentationPath),serial(presentation),"copy report uses identical presentation and real event evidence");
    assert.ok(neutral?text(techPanel).includes("neutral"):text(techPanel).includes(dimension));
    assert.equal(e["help-me-understand"],undefined,"no second interaction is needed");
    assert.equal(e["feedback-details"].open,true,"existing disclosure is unaffected");
    assert.equal(value(page,"JSON.stringify(state)"),state,"help does not change progression, lesson mastery, drafts or save state");
    assert.equal(value(page,"isDirty()"),dirty);
    assert.equal(e["stage-text"].value,editor);
    assert.equal(JSON.stringify(response),original);
    assert.equal(calls,before,"guidance and its trace make no API requests");
    assert.equal(page.timers.size,timers);
    e["stage-text"].focused=false;
    value(page,"displayFeedback(currentResponse)");
    assert.equal(e["stage-text"].focused,false,"rendering never moves focus");
    assert.equal(e["feedback-details"].open,true);
    if(name==="reason") {
      assert.equal(e["tutor-noticed"].textContent,"Your sentence has a possible main statement and a 'because' part to review.");
      assert.equal(e["tutor-why"].textContent,"An explanation helps readers understand the point you want to make.");
      assert.deepEqual(serial(presentation.rule_ids),["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE","INTRO.REASON.CLAUSE_TOPIC_OVERLAP"]);
    }
    if(name==="subordinator") {
      assert.equal(e["tutor-noticed"].textContent,"The sentence containing 'Because' was flagged as possibly unfinished. Check whether that sentence part connects to a main statement.");
      assert.equal(e["tutor-why"].textContent,"'Because' introduces a reason. Your reader expects a main statement that gives the result or claim.");
      assert.equal(presentation.rule_ids.includes("INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"),true);
    }
    if(name==="subordinator_clean") {
      assert.equal(value(page,"selectScaffoldingGuidance(currentResponse)"),null,"clean reason sentence keeps original feedback");
      assert.equal(e["feedback-writing-focus"].hidden,true);
    }
  }
  // Real model/API cases: full grammatical guidance, exact source spans and
  // trace/report agreement, including Unicode before Python-character offsets.
  const markerNotes=value(page,"scaffoldingCatalog.lessons.find(l=>l.lesson_id==='HELP-INTRO-COMPLETE-SENTENCE').tutor.marker_notes");
  const checkMarker=(response,expected)=>{
    const snapshot=JSON.stringify(response),before=calls,timers=page.timers.size;
    show(response);
    const presentation=value(page,"studentFeedbackPresentation(currentResponse)");
    const marker=presentation.verified_subordinator;
    assert.equal(marker?.text??null,expected);
    const primary=presentation.tutor_items[0];
    if(expected) {
      assert.equal(e["tutor-noticed"].textContent,`The sentence containing '${expected}' was flagged as possibly unfinished. Check whether that sentence part connects to a main statement.`);
      assert.equal(e["tutor-why"].textContent,markerNotes[expected.toLowerCase()]);
    } else {
      assert.equal(e["tutor-noticed"].textContent,primary.noticed);
      assert.notEqual(e["tutor-noticed"].textContent.includes("{marker}"),true,"unverified markers never surface raw placeholders");
    }
    if(marker) {
      assert.equal(Array.from(response.analysis.linguistic_observations.text).slice(marker.start,marker.end).join(""),expected);
      assert.ok(response.analysis.rule_evidence.some(event=>event.rule_id===marker.rule_id));
    }
    const tech=walk(e["nlp-transparency-content"]).find(item=>item.dataset.subPanel==="engine:primary");
    assert.ok(text(tech).includes(e["tutor-noticed"].textContent));
    const report=value(page,"buildFullAnalysisReport(currentResponse)");
    assert.deepEqual(reportRecord(report,presentationPath),serial(presentation));
    assert.ok(report.includes(response.feedback["Primary Feedback"]));
    assert.equal(JSON.stringify(response),snapshot);
    assert.equal(calls,before);assert.equal(page.timers.size,timers);
  };
  for(const [name,marker] of Object.entries({because_fragment:"Because",although_fragment:"Although",if_fragment:"If",unicode_marker:"Although"})) {
    const response=actualStageResponses.HELP_CASES[name];
    assert.equal(response.research_trace.stages.INTRODUCTION.feedback_decisions.fields["Primary Feedback"].selection_branch,"intro_sentence_fluency_complete_sentence",name);
    checkMarker(response,marker);
  }
  checkMarker(actualStageResponses.HELP_CASES.multiple_markers,null);
  for(const [name,response] of Object.entries(actualStageResponses.HELP_CASES).filter(([name])=>name.startsWith("marker_"))) {
    const branch=response.research_trace.stages.INTRODUCTION.feedback_decisions.fields["Primary Feedback"].selection_branch;
    if(branch==="intro_sentence_fluency_complete_sentence") checkMarker(response,response.analysis.linguistic_observations.text.split(" ")[0]);
    else { show(response);assert.equal(value(page,"studentFeedbackPresentation(currentResponse).verified_subordinator"),null); }
  }
  for(const name of ["because_complete","although_complete","parser_false_positive"]) {
    const response=actualStageResponses.HELP_CASES[name];show(response);
    assert.notEqual(response.research_trace.stages.INTRODUCTION.feedback_decisions.fields["Primary Feedback"].selection_branch,"intro_sentence_fluency_complete_sentence",name);
    assert.equal(value(page,"studentFeedbackPresentation(currentResponse).verified_subordinator"),null);
  }
  // Every incomplete/contradictory record takes neutral prepared guidance;
  // neither words in backend messages nor arbitrary first markers are used.
  for(const corrupt of [
    r=>{r.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR").evidence=[];},
    r=>{delete r.analysis.linguistic_observations.text;},
    r=>{r.analysis.input_text="Different input";},
    r=>{delete r.analysis.linguistic_observations;},
    r=>{r.analysis.observable_structure.incomplete_subordinator_candidates=[];},
    r=>{r.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR").evidence[0].start=-1;},
    r=>{r.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR").evidence[0].end=999;},
    r=>{r.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR").evidence[0].start="0";},
    r=>{r.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR").evidence[0].text="Because";},
    r=>{r.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR").evidence[0].sentence_index=99;},
    r=>{r.analysis.linguistic_observations.tokens[0].pos="NOUN";},
    r=>{r.analysis.rule_evidence.push(r.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"));},
    r=>{r.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR").evidence=null;}
  ]) {
    const response=JSON.parse(JSON.stringify(actualStageResponses.HELP_CASES.although_fragment));
    corrupt(response);checkMarker(response,null);
  }
  // Optional real recorded conditions are preserved verbatim, never inferred.
  const enriched=JSON.parse(JSON.stringify(actualStageResponses.HELP_CASES.although_fragment));
  enriched.analysis.rule_evidence.find(e=>e.rule_id==="INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR").evidence[0].matched_conditions=["recorded-fixture-condition"];
  checkMarker(enriched,"Although");
  for(const name of ["uncertain","no_trace","body_unmapped"]) {
    show(actualStageResponses.HELP_CASES[name]);
    assert.equal(value(page,"selectScaffoldingGuidance(currentResponse)"),null,name);
    assert.equal(e["feedback-writing-focus"].hidden,name!=="body_unmapped",name);
    if(name === "body_unmapped") {
      assert.equal(value(page,"studentFeedbackPresentation(currentResponse).tutor_items[0].role"),"NO_SUPPORTED_CONCERN_SELECTED");
      assert.equal(value(page,"studentFeedbackPresentation(currentResponse).tutor_items[0].task_text"),"");
      assert.equal(e["feedback-writing-focus"].textContent,"No specific writing issue detected");
      assert.match(e["tutor-noticed"].textContent,/available checks did not identify a specific structural concern/);
      assert.equal(e["tutor-task-section"].hidden,true);
      assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0);
    } else assert.equal(e["tutor-noticed"].textContent,actualStageResponses.HELP_CASES[name].feedback["Primary Feedback"]);
    assert.equal(value(page,"studentFeedbackPresentation(currentResponse).writing_dimension"),null,"no invented assessment label");
  }
  const newWords=actualStageResponses.HELP_CASES.conclusion_unmapped;
  show(newWords);
  assert.equal(value(page,"selectScaffoldingGuidance(currentResponse).binding.lesson_id"),"HELP-CONCLUSION-EXPLAIN-NEW-WORDS");
  assert.equal(value(page,"studentFeedbackPresentation(currentResponse).writing_dimension"),"Ideas");
  assert.equal(e["feedback-writing-focus"].textContent,"Ideas · Explain New Words");
  for(const corrupt of [response=>{delete response.research_trace;},response=>{response.research_trace.selected_stage="BODY";},response=>{response.research_trace.stages.INTRODUCTION.feedback_decisions.fields["Primary Feedback"].selected_message="Different message";},response=>{response.feedback["Feedback Provenance"]=[];},response=>{response.analysis.rule_evidence=[];},response=>{response.analysis.rule_evidence.forEach(item=>item.triggered=false);},response=>{response.research_trace.stages.INTRODUCTION.feedback_decisions.fields["Primary Feedback"].rule_ids=[];}]) {
    const response=JSON.parse(JSON.stringify(actualStageResponses.HELP_CASES.reason));
    corrupt(response);show(response);
    assert.equal(e["feedback-writing-focus"].hidden,true,"missing or contradictory provenance retains original feedback");
    assert.equal(e["tutor-noticed"].textContent,response.feedback["Primary Feedback"]);
  }
  // Safe literal rendering of dynamic received feedback, with genuine event links.
  const safe=JSON.parse(JSON.stringify(actualStageResponses.HELP_CASES.reason));
  safe.feedback["Primary Feedback"]='<img src=x onerror="bad()"><script>literal</script>';
  safe.research_trace.stages.INTRODUCTION.feedback_decisions.fields["Primary Feedback"].selected_message=safe.feedback["Primary Feedback"];
  show(safe);
  const tech=walk(e["nlp-transparency-content"]).find(item=>item.dataset.subPanel==="engine:primary");
  assert.ok(text(tech).includes(safe.feedback["Primary Feedback"]));
  assert.equal(walk(tech).some(item=>["IMG","SCRIPT"].includes(item.tagName)),false);
  delete safe.research_trace;show(safe);
  assert.equal(e["tutor-noticed"].textContent,safe.feedback["Primary Feedback"],"unmapped dynamic text stays literal");
  // Cached stages update one instructional focus without extra requests.
  show(actualStageResponses.HELP_CASES.detail);
  show(actualStageResponses.HELP_CASES.reason);
  const stageCalls=calls;
  await click(page.tabs[1]);
  assert.equal(e["feedback-writing-focus"].textContent,"Ideas · Develop Your Supporting Details");
  await click(page.tabs[0]);
  assert.equal(e["feedback-writing-focus"].textContent,"No specific writing issue detected");
  assert.equal(calls,stageCalls);
  e["stage-text"].value+=" Revised.";await input(e["stage-text"]);
  assert.equal(e["feedback-content"].hidden,true);
  assert.equal(e["feedback-writing-focus"].hidden,true);
  assert.equal(e["feedback-writing-focus"].textContent,"");
  assert.equal(e["copy-full-analysis"].disabled,true);
  show(actualStageResponses.HELP_CASES.reason);
  assert.equal(e["feedback-writing-focus"].hidden,false,"current guidance appears directly after analysis");
  e["focus-terms"].value+=" changed";await input(e["focus-terms"]);
  assert.equal(e["feedback-content"].hidden,true,"assignment context changes invalidate guidance");
  show(actualStageResponses.HELP_CASES.reason);
  await click(page.appLinks.find(link=>link.dataset.appLink==="dashboard"));
  assert.equal(value(page,"currentAnalysisForExport()"),null);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  assert.equal(e["tutor-noticed"].textContent,value(page,"studentFeedbackPresentation(currentResponse).displayed_guidance['What I noticed']"));
  value(page,"state.assignmentId=999; resetAnalysisContext(); displayFeedback(null)");
  assert.equal(e["feedback-writing-focus"].hidden,true,"reassignment cannot retain a category");
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario, {"HELP_CASES": help_responses})
