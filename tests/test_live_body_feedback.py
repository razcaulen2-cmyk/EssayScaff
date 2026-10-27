"""Debounced real-workspace lifecycle and evidence-bound Body presentation."""

import json
from pathlib import Path

import pytest

from app import create_app
from services.essay_analysis_service import EssayAnalysisService
from tests.auth_helpers import register_student
from tests.test_workspace_frontend import NODE, _run_workspace_frontend

SAMPLE = json.loads(Path(__file__).with_name("body_live_feedback_cases.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def body_cases(tmp_path_factory):
    app = create_app(EssayAnalysisService(), secret_key="body-live-regression")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path_factory.mktemp("body-live") / "isolated.sqlite3"))
    client = app.test_client()
    assert register_student(client, "body_live_student").status_code == 302
    cases = {"A": ("", SAMPLE["body"]), "B": (SAMPLE["introduction"], SAMPLE["body"]),
             "C": (SAMPLE["introduction"], SAMPLE["one_sentence"]), "D": (SAMPLE["introduction"], SAMPLE["developed"]),
             "supported": (SAMPLE["introduction"], SAMPLE["body"].split("\n\n")[0] + "\n\nSecond, smartphones support learning.")}
    results = {}
    for name, (intro, body) in cases.items():
        response = client.post("/api/analyze-stage", json={
            "stage_id": "BODY", "assignment_topic": SAMPLE["assignment_topic"], "focus_terms": SAMPLE["focus_terms"],
            "introduction_text": intro, "body_text": body, "include_transparency_trace": True,
        })
        assert response.status_code == 200
        results[name] = response.get_json()
    return results


@pytest.mark.parametrize("case,counts", [("A", [4, 1]), ("B", [4, 1]), ("C", [1]), ("D", [4, 3])])
def test_controlled_body_observations_not_a_missing_detail_problem(body_cases, case, counts):
    response = body_cases[case]
    assert response["stage_id"] == "BODY"
    analysis = response["analysis"]
    assert [p["counts"]["sentence_count"] for p in analysis["paragraphs"]] == counts
    assert analysis["paragraph_count"] == len(counts)
    decision = response["research_trace"]["stages"]["BODY"]["feedback_decisions"]["fields"]["Primary Feedback"]
    assert decision["selection_branch"] == "body_neutral_observable"
    assert decision["selected_message"] == response["feedback"]["Primary Feedback"]
    events = {event["rule_id"]: event for event in analysis["rule_evidence"]}
    for p in analysis["paragraphs"]:
        assert f"BODY.P{p['paragraph_index']}.SUPPORTING_DETAIL.CANDIDATE" in events
        assert f"BODY.P{p['paragraph_index']}.SUPPORTING_DETAIL.NOT_OBSERVED" not in events
    if case in {"A", "B"}:
        p2 = analysis["paragraphs"][1]
        assert (p2["start"], p2["end"]) == (282, 337)
        assert SAMPLE["body"][p2["start"]:p2["end"]] == p2["text"]
        candidates = p2["supporting_detail_candidates"]["candidates"]
        assert [item["predicate_evidence"]["text"] for item in candidates] == ["help", "practice"]
        assert len({tuple(item["sentence_span"]) for item in candidates}) == 1
    assert analysis["introduction_to_body_continuity"]["status"] == (
        "NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED" if case == "A" else "LEXICAL_COMPARISON_AVAILABLE")


@pytest.mark.skipif(NODE is None, reason="Node.js is required for actual app.js behavior")
def test_body_neutral_summary_and_supported_paragraph_highlight(tmp_path, body_cases):
    scenario = r'''
(async () => {
  const page=makeWorkspace(fetch,new Map()); await waitForRestoration(page);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements;
  const show=response=>{
    page.context.response=response;
    const source=response.analysis.linguistic_observations?.text||response.research_trace.stages.BODY.linguistic_observations.text;
    e["stage-text"].value=source;
    value(page,`state.currentStage="BODY";state.currentView="BODY";state.drafts.BODY=document.getElementById("stage-text").value;displayFeedback(response)`);
    return value(page,"studentFeedbackPresentation(response)");
  };
  for(const name of ["A","B","C","D"]) {
    const response=actualStageResponses.BODY_LIVE[name],before=JSON.stringify(response);
    const primary=show(response).tutor_items[0];
    assert.equal(primary.role,"NO_SUPPORTED_CONCERN_SELECTED"); assert.equal(primary.category,null);
    assert.equal(primary.task_text,"");assert.equal(primary.why,"");assert.equal(primary.lesson_id,null);
    const recorded=response.research_trace.stages.BODY.feedback_decisions.instructional_feedback;
    assert.equal(recorded.selection_status,"NO_SUPPORTED_CONCERN_SELECTED");assert.equal(recorded.items.length,0);
    assert.ok(recorded.strengths.length>0);assert.equal(primary.working_text,recorded.neutral_result.working);
    assert.equal(primary.evidence_text.includes("I could not point"),false);
    assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0,"neutral counts do not diagnose a problem span");
    assert.equal(JSON.stringify(response),before);
  }
  const supported=show(actualStageResponses.BODY_LIVE.supported).tutor_items[0];
   assert.equal(supported.label,"Ideas · Develop Your Supporting Details");
   assert.match(supported.noticed,/Paragraph 2 has a possible main statement, but no additional sentence was recorded/);
  assert.equal(e["editor-mirror"].querySelector("mark").textContent,"Second, smartphones support learning.");
   assert.match(supported.why,/Readers often need more explanation/);
  const bad=JSON.parse(JSON.stringify(actualStageResponses.BODY_LIVE.supported));
  bad.analysis.rule_evidence.find(event=>event.rule_id==="BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED").actual_evidence[0].end=99999;
  show(bad); assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0);
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario, {"BODY_LIVE": body_cases})


@pytest.mark.skipif(NODE is None, reason="Node.js is required for actual workspace behavior")
def test_live_debounce_single_flight_snapshots_context_failure_and_persistence(tmp_path):
    scenario = r'''
(async () => {
  const requests=[]; let active=0,maxActive=0;
  const responseFor=payload=>({stage_id:payload.stage_id,availability:"ANALYZED",
    analysis:{linguistic_observations:{text:payload[payload.stage_id.toLowerCase()+"_text"],tokens:[],sentences:[]}},
    feedback:{"Primary Feedback":payload[payload.stage_id.toLowerCase()+"_text"],"Current Goal":"Goal","What's Working":[],"Needs Attention":[],"Next Step":"Review"}});
  const tracked=(url,options)=>{
    if(url!=="/api/analyze-stage") return fetch(url,options);
    const payload=JSON.parse(options.body); active++;maxActive=Math.max(maxActive,active);
    return new Promise((resolve,reject)=>requests.push({payload,
      finish:()=>{active--;resolve({ok:true,json:async()=>responseFor(payload)});},
      fail:()=>{active--;reject(new TypeError("offline"));}}));
  };
  const flush=async()=>{for(let i=0;i<8;i++) await new Promise(resolve=>setImmediate(resolve));};
  const page=makeWorkspace(tracked,new Map());await waitForRestoration(page);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements,writeCount=persistenceWrites.length;
  e["assignment-topic"].value="Reading habits";e["focus-terms"].value="reading, students";
  for(const text of ["S","Stu","Students read."]) {e["stage-text"].value=text;await input(e["stage-text"]);}
  assert.equal(requests.length,0);assert.equal(page.timers.size,2);
  await runTimers(page,350);assert.equal(e["tutor-state-title"].textContent,"Checking your latest writing…");
  await runTimers(page,999);assert.equal(requests.length,0);
  await runTimers(page,1000);assert.equal(requests.length,1);
  assert.equal(e["tutor-state-title"].textContent,"Analyzing your writing…");
  const duplicate=click(e["analyze-button"]);await flush();assert.equal(requests.length,1);
  e["stage-text"].value="Students read new books.";await input(e["stage-text"]);await runTimers(page,1000);
  assert.equal(requests.length,1,"newest ready snapshot waits for the active server request");
  requests[0].finish();await flush();assert.equal(requests.length,2);
  assert.equal(value(page,"state.analyses.INTRODUCTION"),undefined,"old result never becomes current");
  assert.equal(requests[1].payload.introduction_text,"Students read new books.");
  requests[1].finish();await duplicate;await flush();
  assert.equal(e["tutor-noticed"].textContent,"Students read new books.");
  await click(e["analyze-button"]);assert.equal(requests.length,2,"identical completed snapshot is reused");
  await click(page.tabs[1]);e["stage-text"].value="Reading helps students.";await input(e["stage-text"]);
  const immediate=click(e["analyze-button"]);await flush();assert.equal(requests.length,3,"manual check bypasses debounce");
  assert.equal(requests[2].payload.introduction_text,"Students read new books.");
  await click(page.tabs[0]);e["stage-text"].value="Students read journals.";await input(e["stage-text"]);
  await click(page.tabs[1]);await runTimers(page,1000);assert.equal(requests.length,3);
  requests[2].finish();await flush();assert.equal(requests.length,4);
  assert.equal(requests[3].payload.stage_id,"BODY");
  assert.equal(requests[3].payload.introduction_text,"Students read journals.","earlier section context is captured anew");
  assert.equal(value(page,"state.analyses.BODY"),undefined);
  value(page,"state.assignmentId=102");e["assignment-topic"].value="Different assignment";await input(e["assignment-topic"]);
  await runTimers(page,1000);requests[3].finish();await flush();assert.equal(requests.length,5);
  assert.equal(requests[4].payload.assignment_id,102);
  assert.equal(value(page,"state.analyses.BODY"),undefined,"prior-assignment result is ignored");
  requests[4].fail();await immediate;await flush();
  assert.equal(e["tutor-state-title"].textContent,"Writing analysis is temporarily unavailable. You can try Analyze Now.");
  assert.equal(e["stage-text"].value,"Reading helps students.");
  const retry=click(e["analyze-button"]);await flush();assert.equal(requests.length,6);
  e["stage-text"].value="";await input(e["stage-text"]);await runTimers(page,1000);
  assert.equal(requests.length,6);requests[5].finish();await retry;await flush();
  assert.equal(e["feedback-content"].hidden,true);assert.equal(e["copy-full-analysis"].disabled,true);
  assert.equal(e["tutor-state-title"].textContent,"Start writing your essay. I'll help you review it as you write.");
  assert.equal(maxActive,1,"there is never more than one browser-initiated active execution");
  assert.equal(persistenceWrites.length,writeCount,"typing and analysis never save/revise/submit");
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario)
