"""Process 01 inspects retained response data without analysis or persistence."""

import json
from pathlib import Path

import pytest

from app import create_app
from services.essay_analysis_service import EssayAnalysisService
from tests.auth_helpers import register_student
from tests.test_workspace_frontend import NODE, _run_workspace_frontend

SAMPLE = json.loads(Path(__file__).with_name("body_live_feedback_cases.json").read_text(encoding="utf-8"))
SHORT = "Students use smartphones in the classroom."
UNICODE = "  Café students read 📚—quietly.\r\n\r\n\t第二段: smartphones support learning.  \r\n"
CASES = {
    "short": ("INTRODUCTION", SHORT, None),
    "body": ("BODY", SAMPLE["body"], SAMPLE["introduction"]),
    "unicode_crlf": ("BODY", UNICODE, SAMPLE["introduction"]),
    "unicode_lf": ("BODY", UNICODE.replace("\r\n", "\n"), SAMPLE["introduction"]),
    "revision": ("INTRODUCTION", "Students should use smartphones for teacher-approved learning.", None),
}


@pytest.fixture(scope="module")
def input_responses(tmp_path_factory):
    app = create_app(EssayAnalysisService(), secret_key="process01-input-evidence")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path_factory.mktemp("student-input") / "isolated.sqlite3"))
    client = app.test_client()
    assert register_student(client, "student_input_inspector").status_code == 302
    results = {}
    for name, (stage, text, prior) in CASES.items():
        payload = {"stage_id": stage, "assignment_topic": SAMPLE["assignment_topic"], "focus_terms": SAMPLE["focus_terms"],
                   "include_transparency_trace": True, f"{stage.lower()}_text": text}
        if prior is not None:
            payload["introduction_text"] = prior
        response = client.post("/api/analyze-stage", json=payload)
        assert response.status_code == 200
        results[name] = response.get_json()
    return results


@pytest.mark.parametrize("name", CASES)
def test_actual_input_retention_provenance_and_offsets(input_responses, name):
    stage, text, prior = CASES[name]
    response = input_responses[name]
    assert response["stage_id"] == stage
    trace = response["research_trace"]["stages"][stage]
    linguistic = response["analysis"].get("linguistic_observations") or trace["linguistic_observations"]
    assert linguistic["text"] == text
    assert all(text[token["start"]:token["end"]] == token["text"] for token in linguistic["tokens"])
    assert response["analysis"]["assignment_topic"] == SAMPLE["assignment_topic"]
    assert response["analysis"]["lexical_topic_evidence"]["focus_terms"] == SAMPLE["focus_terms"]
    if prior is not None:
        assert trace["input_sections"]["introduction"] == prior
    assert "request_payload" not in response and "revision_id" not in response
    if name == "short":
        assert (len(text), len(text.split())) == (42, 6)
    if name == "body":
        assert (len(text), len(text.split())) == (337, 52)
        assert "\n\n" in linguistic["text"]
    if name == "unicode_crlf":
        assert linguistic["text"].count("\r\n") == 3


@pytest.mark.skipif(NODE is None, reason="Node.js is required for actual Process 01 rendering")
def test_student_text_inspector_exact_evidence_export_missing_fields_and_read_only(tmp_path, input_responses):
    scenario = r'''
(async () => {
  let calls=0;
  const page=makeWorkspace((...args)=>{calls++;return fetch(...args);},new Map());
  await waitForRestoration(page);await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements,walk=node=>[node,...node.children.flatMap(walk)];
  const text=node=>walk(node).map(item=>item.textContent).join("\n");
  for(const [name,response] of Object.entries(actualStageResponses.INPUT_CASES)) {
    page.context.currentResponse=response;
    const stage=response.stage_id,ling=response.analysis.linguistic_observations||response.research_trace.stages[stage].linguistic_observations;
    e["stage-text"].value=ling.text;e["assignment-topic"].value=response.analysis.assignment_topic;
    e["focus-terms"].value=response.analysis.lexical_topic_evidence.focus_terms.join(", ");
    value(page,`state.currentStage=currentResponse.stage_id;state.currentView=currentResponse.stage_id;
      state.sessionId="a-saved-session-is-not-a-revision-id";state.drafts[state.currentStage]=document.getElementById("stage-text").value;
      state.analyses[state.currentStage]=currentResponse;state.analysisSnapshots[state.currentStage]=analysisSnapshot(state.currentStage)`);
    const before=JSON.stringify(response),beforeState=value(page,"JSON.stringify(state)"),beforeCalls=calls,beforeTimers=page.timers.size;
    value(page,"displayFeedback(currentResponse)");
    const model=value(page,"studentTextInputEvidence(currentResponse)");
    assert.equal(model.text,ling.text);assert.equal(model.code_point_characters,Array.from(ling.text).length);
    assert.equal(model.whitespace_words,ling.text.trim().split(/\s+/).length);
    assert.equal(model.browser_fingerprint,value(page,"transparencyDraftIdentity(studentTextInputEvidence(currentResponse).text,currentResponse.stage_id)"));
    assert.equal(model.saved_revision_id,null);assert.equal(model.transmitted_request_payload,null);
    assert.deepEqual(JSON.parse(JSON.stringify(model.teacher_focus_terms)),response.analysis.lexical_topic_evidence.focus_terms);
    if(stage==="BODY") assert.equal(model.earlier_sections[0].text,response.research_trace.stages.BODY.input_sections.introduction);
    const host=e["nlp-transparency-content"];
    for(const sub of ["overview","text","context"]) {
      const panel=walk(host).find(item=>item.dataset.subPanel===`student:${sub}`);
      const inspector=walk(panel).find(item=>item.attributes["data-student-input-inspector"]===sub);
      const sections=inspector.children.filter(item=>item.attributes["data-input-section"]);
      assert.deepEqual(sections.map(item=>item.attributes["data-input-section"]),["original","received","explanation","observed","forward","limitations"]);
      const viewer=walk(sections[0]).find(item=>item.className==="student-source-text");
      assert.equal(viewer.textContent,ling.text);assert.equal(viewer.dataset.sourceStart,"0");
      assert.equal(viewer.dataset.sourceEnd,String(Array.from(ling.text).length));
      assert.equal(viewer.attributes["aria-readonly"],"true");
      assert.equal(walk(panel).some(item=>item.tagName==="PRE"||item.tagName==="TEXTAREA"),false);
      for(const heading of ["WHAT is it?","WHY do we need it?","HOW does it work?","WHERE is it used?"]) assert.ok(text(inspector).includes(heading));
      const references=walk(inspector).find(item=>item.tagName==="DETAILS"&&item.children[0].textContent==="Source references — file, function and purpose");
      references.open=true;await dispatch(references,"toggle");
      assert.ok(text(references).includes("performStageAnalysis"));assert.ok(text(references).includes("selectStage"));
      assert.ok(text(inspector).includes("Not recorded."));
    }
    if(name==="unicode_crlf") {assert.equal(model.line_endings.crlf_pairs,3);assert.ok(model.code_point_characters<ling.text.length);}
    const report=value(page,"buildFullAnalysisReport(currentResponse)");
    const exported=reportRecord(report,"frontend.studentTextInputEvidence (retained response fields + explicitly browser-derived values)");
    assert.deepEqual(exported,JSON.parse(JSON.stringify(model)));
    const textMarker="Current analyzed writing text [source: analysis.input_text / linguistic observations.text / selected-stage input_sections / supplied_text]";
    const textStart=report.indexOf(textMarker);
    assert.notEqual(textStart,-1,"raw text record is present with its real source paths");
    const textValue=report.slice(textStart+textMarker.length,textStart+textMarker.length+1+ling.text.length);
    assert.equal(textValue,"\n"+ling.text,"record preserves the exact retained text");
    assert.equal(calls,beforeCalls);assert.equal(page.timers.size,beforeTimers);
    assert.equal(JSON.stringify(response),before);assert.equal(value(page,"JSON.stringify(state)"),beforeState);
  }
  const missing=JSON.parse(JSON.stringify(actualStageResponses.INPUT_CASES.body));
  delete missing.analysis.input_text;delete missing.analysis.linguistic_observations;
  delete missing.research_trace.stages.BODY.linguistic_observations;
  delete missing.research_trace.stages.BODY.input_sections.body;delete missing.supplied_text;
  page.context.missingResponse=missing;
  const absent=value(page,"studentTextInputEvidence(missingResponse)");
  assert.equal(absent.text,null);assert.equal(absent.code_point_characters,null);assert.equal(absent.whitespace_words,null);
  assert.equal(absent.browser_fingerprint,null,"do not fingerprint a placeholder or joined paragraph reconstruction");
  const conflict=JSON.parse(JSON.stringify(actualStageResponses.INPUT_CASES.short));
  conflict.analysis.input_text="Different retained text";page.context.conflictResponse=conflict;
  const disputed=value(page,"studentTextInputEvidence(conflictResponse)");
  assert.equal(disputed.text,null);assert.match(disputed.text_status,/disagree/);assert.equal(disputed.browser_fingerprint,null);
  assert.ok(disputed.conflicting_text_sources.some(item=>item.text==="Different retained text"));
  const minimal={stage_id:"BODY",analysis:{},availability:"ANALYZED",feedback:{}};
  page.context.minimalResponse=minimal;
  assert.equal(value(page,"studentTextInputEvidence(minimalResponse).configured_focus_terms"),null);
  assert.equal(value(page,"studentTextInputEvidence(minimalResponse).earlier_sections[0].status"),"Not recorded.");
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario, {"INPUT_CASES": input_responses})


@pytest.mark.skipif(NODE is None, reason="Node.js is required for live snapshot lifecycle")
def test_student_text_previous_snapshot_and_latest_accepted_live_result(tmp_path, input_responses):
    scenario = r'''
(async () => {
  let calls=0;const page=makeWorkspace((...args)=>{calls++;return fetch(...args);},new Map());
  await waitForRestoration(page);await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements,walk=node=>[node,...node.children.flatMap(walk)];
  const first=actualStageResponses.INPUT_CASES.short,next=actualStageResponses.INPUT_CASES.revision;
  e["assignment-topic"].value=first.analysis.assignment_topic;e["focus-terms"].value=first.analysis.lexical_topic_evidence.focus_terms.join(", ");
  e["stage-text"].value=first.analysis.linguistic_observations.text;await input(e["stage-text"]);
  analysisResponseOverride=first;await click(e["analyze-button"]);
  e["stage-text"].value=next.analysis.linguistic_observations.text;await input(e["stage-text"]);
  assert.equal(e["nlp-transparency-content"].dataset.status,"STALE");
  const beforeCalls=calls,timers=page.timers.size;
  const previous=walk(e["nlp-transparency-content"]).find(item=>item.className==="student-source-text");
  assert.equal(previous.textContent,first.analysis.linguistic_observations.text);
  assert.ok(walk(e["nlp-transparency-content"]).some(item=>item.attributes["data-snapshot-status"]==="PREVIOUS"));
  assert.equal(walk(e["nlp-transparency-content"]).filter(item=>item.tagName==="TABLE").length,0);
  for(const details of walk(e["nlp-transparency-content"]).filter(item=>item.tagName==="DETAILS")) {details.open=true;await dispatch(details,"toggle");}
  assert.equal(calls,beforeCalls);assert.equal(page.timers.size,timers);
  assert.equal(e["copy-full-analysis"].disabled,true);
  analysisResponseOverride=next;await runTimers(page,1000);
  assert.equal(e["nlp-transparency-content"].dataset.status,"CURRENT");
  const current=walk(e["nlp-transparency-content"]).find(item=>item.className==="student-source-text");
  assert.equal(current.textContent,next.analysis.linguistic_observations.text);
  e["focus-terms"].value="a newer unsent focus list";await input(e["focus-terms"]);
  const staleText=walk(e["nlp-transparency-content"]).find(item=>item.className==="student-source-text");
  assert.equal(staleText.textContent,next.analysis.linguistic_observations.text);
  assert.ok(walk(e["nlp-transparency-content"]).some(item=>item.textContent==="smartphones, students, classroom, learning, distractions"));
  value(page,"state.assignmentId=999;displayFeedback(null)");
  assert.equal(walk(e["nlp-transparency-content"]).filter(item=>item.className==="student-source-text").length,0,"another assignment cannot inherit the old input inspector");
  console.log("Feedback presentation scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario, {"INPUT_CASES": input_responses})
