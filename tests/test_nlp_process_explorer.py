"""Frontend process models retain scope, exact evidence and neutral feedback."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from services.essay_analysis_service import EssayAnalysisService
from tests.test_reason_highlighting import NODE, _make_stage_payload, _run_node_scenario

CORPUS = json.loads(Path(__file__).with_name("nlp_process_explorer_cases.json").read_text(encoding="utf-8"))
pytestmark = pytest.mark.skipif(NODE is None, reason="Node required for actual frontend models")


@pytest.fixture(scope="module")
def cases():
    service = EssayAnalysisService()
    values = {}
    for stage in ("INTRODUCTION", "BODY", "CONCLUSION"):
        fields = {"introduction_text": CORPUS["introduction"]}
        if stage in {"BODY", "CONCLUSION"}:
            fields["body_text"] = CORPUS["body"]
        if stage == "CONCLUSION":
            fields["conclusion_text"] = CORPUS["conclusion"]
        values[stage] = _make_stage_payload(service.analyze(CORPUS["assignment_topic"], CORPUS["focus_terms"], **fields, include_research_trace=True), stage)
    for stage in ("BODY", "CONCLUSION"):
        values[stage + "_NO_CONTEXT"] = _make_stage_payload(service.analyze(CORPUS["assignment_topic"], CORPUS["focus_terms"],
            **{stage.lower() + "_text": CORPUS[stage.lower()]}, include_research_trace=True), stage)
    return values


@pytest.mark.parametrize("stage,expected_count,only", [
    ("INTRODUCTION", 23, ["sentence-connection"]),
    ("BODY", 25, ["topic-sentences", "supporting-details"]),
    ("CONCLUSION", 25, ["synthesis", "new-material"]),
])
def test_every_process_has_unique_stage_scoped_purpose_evidence_and_status(cases, stage, expected_count, only, tmp_path):
    _run_node_scenario(cases[stage], r'''
      elements["stage-text"].value=tutorSourceText(analysisResponse).source;
      const before=JSON.stringify(analysisResponse);
      displayFeedback(analysisResponse);
      const processes=transparencyTabsApi.processes;
      assert.equal(processes.length,__COUNT__);
      assert.equal(new Set(processes.map(p=>p.id)).size,processes.length);
      for(const id of __ONLY__)assert.ok(processes.some(p=>p.id===id));
      for(const p of processes){
        assert.ok(p.title&&p.purpose&&p.method&&p.source&&p.next&&p.limitation);
        assert.ok(["EXECUTED","SKIPPED","NOT_APPLICABLE","UNAVAILABLE"].includes(p.execution.status));
        assert.ok(p.execution.basis);
        assert.ok(p.rows.every(row=>row.rule_id.startsWith(analysisResponse.stage_id+".")),"no other stage's rules presented as executed");
      }
      const forbidden=analysisResponse.stage_id==="INTRODUCTION"?["topic-sentences","supporting-details","synthesis","new-material"]:analysisResponse.stage_id==="BODY"?["sentence-connection","synthesis","new-material"]:["sentence-connection","topic-sentences","supporting-details"];
      for(const id of forbidden)assert.equal(processes.some(p=>p.id===id),false);
      assert.equal(JSON.stringify(analysisResponse),before);
    '''.replace("__COUNT__", str(expected_count)).replace("__ONLY__", json.dumps(only)), tmp_path)


def test_all_original_technical_sections_have_exactly_one_reachable_home(cases, tmp_path):
    _run_node_scenario(cases["INTRODUCTION"], r'''
      const oldKeys=HORIZONTAL_TRANSPARENCY_TABS.flatMap(([main,,sections])=>sections.map(([sub])=>main+":"+sub));
      const homes=Object.values(NlpProcessExplorer.sectionOwners).flat();
      assert.equal(homes.length,45);assert.equal(new Set(homes).size,45);
      assert.equal(JSON.stringify([...homes].sort()),JSON.stringify([...oldKeys].sort()));
      assert.equal(Object.keys(NlpProcessExplorer.sectionOwners).includes("student-text"),false);
    ''', tmp_path)


@pytest.mark.parametrize("variant,expected", [("recorded", "SKIPPED"), ("missing", "UNAVAILABLE"), ("failed", "UNAVAILABLE"), ("executed_empty", "EXECUTED")])
def test_wordnet_status_uses_recorded_execution_not_candidate_count(cases, variant, expected, tmp_path):
    payload = deepcopy(cases["INTRODUCTION"])
    steps = payload["research_trace"]["stages"]["INTRODUCTION"]["topic_service"]["steps"]
    record = next(s for s in steps if s["id"] == "wordnet_direct_suggestions")
    if variant == "missing":
        steps.remove(record)
    elif variant == "failed":
        record.update(execution_status="FAILED", status="RESOURCE_MISSING", output=[], lookup_pairs=[])
    elif variant == "executed_empty":
        record.update(execution_status="EXECUTED", status="available", output=[], lookup_pairs=[], suggestion_count=0)
    _run_node_scenario(payload, r'''
      const data=transparencyData(analysisResponse),presentation=studentFeedbackPresentation(analysisResponse);
      const spec=NlpProcessExplorer.catalog(data.stage).find(p=>p.id==="wordnet");
      const model=NlpProcessExplorer.model(spec,analysisResponse,data,presentation);
      assert.equal(model.execution.status,__EXPECTED__);
      const raw=data.stageTrace.topic_service.steps.find(p=>p.id==="wordnet_direct_suggestions");
      assert.equal(JSON.stringify(model.output),JSON.stringify(raw));
    '''.replace("__EXPECTED__", json.dumps(expected)), tmp_path)


@pytest.mark.parametrize("stage", ["BODY", "CONCLUSION"])
def test_missing_earlier_sections_are_not_executed_comparisons(cases, stage, tmp_path):
    _run_node_scenario(cases[stage + "_NO_CONTEXT"], r'''
      const data=transparencyData(analysisResponse),presentation=studentFeedbackPresentation(analysisResponse);
      const spec=NlpProcessExplorer.catalog(data.stage).find(p=>p.id==="cross-stage");
      const model=NlpProcessExplorer.model(spec,analysisResponse,data,presentation);
      assert.equal(model.execution.status,"NOT_APPLICABLE");
      assert.ok(model.paths.length>0&&model.paths.every(p=>p.status.startsWith("NOT_AVAILABLE_NO_")));
      assert.ok(model.input.earlier_sections.every(p=>p.text===null));
    ''', tmp_path)


@pytest.mark.parametrize("stage", ["INTRODUCTION", "BODY", "CONCLUSION"])
def test_new_process_outputs_preserve_original_tokens_matches_and_source_offsets(cases, stage, tmp_path):
    _run_node_scenario(cases[stage], r'''
      const data=transparencyData(analysisResponse),presentation=studentFeedbackPresentation(analysisResponse),source=Array.from(tutorSourceText(analysisResponse).source);
      const get=id=>NlpProcessExplorer.model(NlpProcessExplorer.catalog(data.stage).find(p=>p.id===id),analysisResponse,data,presentation);
      assert.equal(JSON.stringify(get("tokens").output),JSON.stringify(data.linguistic.tokens));
      assert.equal(JSON.stringify(get("concepts").output),JSON.stringify(data.concepts));
      assert.equal(JSON.stringify(get("topic-matching").output),JSON.stringify(data.analysis.lexical_topic_evidence));
      for(const token of get("tokens").output)assert.equal(source.slice(token.start,token.end).join(""),token.text);
      for(const match of get("topic-matching").output.matches)assert.equal(source.slice(match.start,match.end).join(""),match.observed_text??match.text);
      const shared=data.stageTrace.topic_service.steps.find(s=>s.id==="spacy_document_processing");
      assert.equal(get("tokens").execution.duration_ms,shared.duration_ms);
      assert.equal(get("pos").execution.duration_ms,shared.duration_ms);
      assert.match(get("pos").execution.basis,/no separate time or extra NLP run/);
    ''', tmp_path)


def test_neutral_body_explorer_assigns_no_trait_lesson_task_or_highlight(cases, tmp_path):
    _run_node_scenario(cases["BODY"], r'''
      elements["stage-text"].value=analysisResponse.analysis.input_text;
      displayFeedback(analysisResponse);
      const before=JSON.stringify(analysisResponse),presentation=studentFeedbackPresentation(analysisResponse);
      assert.equal(presentation.status,"NO_SUPPORTED_CONCERN_SELECTED");
      assert.equal(presentation.writing_dimension,null);assert.equal(presentation.teaching_content_source,null);
      assert.equal(elements["tutor-why-section"].hidden,true);assert.equal(elements["tutor-task-section"].hidden,true);
      assert.equal(elements["editor-mirror"].querySelectorAll("mark").length,0);
      for(const id of ["trait-mapping","highlight-evidence"]){
        transparencyTabsApi.selectProcess(id);
        assert.equal(transparencyTabsApi.processes.find(p=>p.id===id).execution.status,"NOT_APPLICABLE");
      }
      assert.equal(JSON.stringify(analysisResponse),before);
    ''', tmp_path)


def test_neutral_introduction_mapping_is_not_misreported_as_unavailable(cases, tmp_path):
    _run_node_scenario(cases["INTRODUCTION"], r'''
      elements["stage-text"].value=analysisResponse.analysis.input_text;
      displayFeedback(analysisResponse);
      const before=JSON.stringify(analysisResponse),data=transparencyData(analysisResponse),presentation=studentFeedbackPresentation(analysisResponse);
      assert.equal(presentation.status,"NEUTRAL_OBSERVATION");
      assert.equal(presentation.writing_dimension,null);assert.equal(presentation.teaching_content_source,null);
      const get=id=>NlpProcessExplorer.model(NlpProcessExplorer.catalog(data.stage).find(p=>p.id===id),analysisResponse,data,presentation);
      const mapping=get("trait-mapping");
      assert.equal(mapping.execution.status,"NOT_APPLICABLE");
      assert.match(mapping.execution.basis,/neutral review/);
      assert.equal(mapping.output.actual_presentation.status,"NEUTRAL_OBSERVATION");
      assert.ok(mapping.output.actual_presentation.tutor_items.some(item=>item.lesson_id==="HELP-INTRO-EXPLAIN-POINT"
        &&item.neutral_result===true&&item.role==="PREPARED"&&item.feedback_purpose==="NEUTRAL_REVIEW_TASK"),"the retained prepared explanation item is exposed without becoming a concern");
      const find=(node,id)=>{if(node.dataset&&node.dataset.explorerProcess===id)return node;for(const child of node.children){const hit=find(child,id);if(hit)return hit;}return null;};
      transparencyTabsApi.selectProcess("trait-mapping");
      const page=find(elements["nlp-transparency-content"],"trait-mapping");
      assert.ok(page&&page.textContent.includes("NEUTRAL_OBSERVATION"));
      assert.ok(page.textContent.includes("HELP-INTRO-EXPLAIN-POINT"));
      assert.ok(page.textContent.includes("not a concern"));
      assert.equal(JSON.stringify(analysisResponse),before);
    ''', tmp_path)
