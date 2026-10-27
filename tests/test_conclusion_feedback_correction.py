"""Regression coverage for the two confirmed Conclusion feedback defects.

Problem A: a recorded neutral Conclusion branch was rendered as a corrective
trait/lesson even though Stage Progress already treated it as neutral.
Problem B: a lesson task could tell students to read a highlighted sentence
when no verified source span existed.
"""

import pytest

from services.essay_analysis_service import EssayAnalysisService
from tests.test_reason_highlighting import _make_stage_payload
from tests.test_workspace_frontend import NODE, _run_workspace_frontend


TOPIC = "Should schools turn part of their playgrounds into vegetable gardens?"
FOCUS = ["schools", "playgrounds", "vegetable gardens", "students", "learning"]
INTRODUCTION = (
    "Schools should turn a small part of their playgrounds into vegetable gardens because it can help students "
    "learn about science and develop responsibility. Through gardening activities, students can observe how plants "
    "grow and understand the importance of taking care of the environment. These experiences can make learning more "
    "practical while allowing students to enjoy both gardening and playing at school."
)
BODY = (
    "A vegetable garden can help students learn about science. Students can observe how seeds grow and record "
    "changes in the plants. These activities give students a chance to practice what they learn in class.\n\n"
    "A school garden can also teach responsibility. For example, students can take turns watering the vegetables, "
    "removing weeds, and checking whether the plants are healthy. By completing these tasks regularly, students can "
    "learn to be responsible and understand the importance of caring for something."
)
CONCLUSION = (
    "In conclusion, schools should turn a small part of their playgrounds into vegetable gardens. These gardens can "
    "help students learn about science by observing how plants grow. Students can also develop responsibility by "
    "taking turns watering vegetables and caring for the plants."
)
KEYWORD_CONCLUSION = "schools, playgrounds, vegetable gardens, students, learning"
NEW_WORDS_CONCLUSION = "Students should also sell the vegetables to buy new books."
SECONDARY_INTRODUCTION = "Recess is important for young children."
SECONDARY_BODY = "Students grow vegetables and learn responsibility."


def _analyze(service, introduction, body, conclusion):
    return service.analyze(
        TOPIC,
        FOCUS,
        introduction_text=introduction,
        body_text=body,
        conclusion_text=conclusion,
        include_research_trace=True,
    )


def _decision(result):
    return result["research_trace"]["stages"]["CONCLUSION"]["feedback_decisions"]["fields"]["Primary Feedback"]


def _responses():
    service = EssayAnalysisService()
    exact = _analyze(service, INTRODUCTION, BODY, CONCLUSION)
    keyword = _analyze(service, INTRODUCTION, BODY, KEYWORD_CONCLUSION)
    new_words = _analyze(service, INTRODUCTION, BODY, NEW_WORDS_CONCLUSION)
    secondary = _analyze(service, SECONDARY_INTRODUCTION, SECONDARY_BODY, NEW_WORDS_CONCLUSION)
    assert _decision(exact)["selection_branch"] == "conclusion_ideas_bring_together"
    assert _decision(keyword)["selection_branch"] == "conclusion_organization_bring_together"
    assert _decision(new_words)["selection_branch"] == "conclusion_ideas_new_words"
    assert _decision(secondary)["selection_branch"] == "conclusion_ideas_new_words"
    return {
        "EXACT": _make_stage_payload(exact, "CONCLUSION"),
        "KEYWORD": _make_stage_payload(keyword, "CONCLUSION"),
        "NEW_WORDS": _make_stage_payload(new_words, "CONCLUSION"),
        "SECONDARY": _make_stage_payload(secondary, "CONCLUSION"),
    }


def test_exact_school_garden_conclusion_records_neutral_synthesis_and_no_span():
    service = EssayAnalysisService()
    result = _analyze(service, INTRODUCTION, BODY, CONCLUSION)
    decision = _decision(result)
    feedback = result["stages"]["CONCLUSION"]["feedback"]

    assert decision["selection_branch"] == "conclusion_ideas_bring_together"
    assert (decision["trait"], decision["skill"]) == ("Ideas", "Bring Ideas Together")
    assert decision["rule_ids"] == ["CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE"]
    assert decision["selected_message"] == feedback["Primary Feedback"]
    assert "check that it brings the ideas together as you intend" in feedback["Primary Feedback"]
    assert feedback["Needs Attention"] == [
        "These checks record structure and wording only; they cannot tell whether an idea is true "
        "or whether the ending works well."
    ]

    # The same positive synthesis event is retained under What's Working.
    working_links = [item["rule_id"] for item in feedback["Feedback Provenance"] if item["feedback_field"] == "What's Working"]
    assert "CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE" in working_links
    assert any("One sentence combines ideas" in item for item in feedback["What's Working"])

    event = next(item for item in result["stages"]["CONCLUSION"]["analysis"]["rule_evidence"]
                 if item["rule_id"] == "CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE")
    assert event.get("triggered", True) is not False
    evidence = event["actual_evidence"]
    assert len(evidence) == 3
    target = next(item for item in evidence if item["sentence_span"] == [0, 92])
    assert target["sentence_text"] == CONCLUSION[:92]
    # The event records sentence spans, not verified token/occurrence spans, so
    # the shared tutor excerpt verifier has nothing safe to mark here.
    assert all("start" not in item and "end" not in item for item in evidence)


@pytest.mark.skipif(NODE is None, reason="Node.js is required for real app.js DOM behavior")
def test_conclusion_neutral_presentation_and_highlight_dependent_tasks(tmp_path):
    scenario = r'''
(async () => {
  const page=makeWorkspace(fetch,new Map());
  page.context.secondaryResponse=actualStageResponses.SECONDARY;
  page.context.keywordResponse=actualStageResponses.KEYWORD;
  await waitForRestoration(page);
  await click(page.appLinks.find(link=>link.dataset.appLink==="workspace"));
  const e=page.elements;
  const walk=element=>[element,...element.children.flatMap(walk)];
  const text=element=>walk(element).map(item=>item.textContent).join("\n");
  const show=response=>{
    page.context.currentResponse=response;
    e["assignment-topic"].value=response.analysis.assignment_topic;
    e["focus-terms"].value=response.analysis.lexical_topic_evidence.focus_terms.join(", ");
    e["stage-text"].value=response.analysis.linguistic_observations.text;
    value(page,`state.currentStage="CONCLUSION";state.currentView="CONCLUSION";
      state.drafts.INTRODUCTION=currentResponse.research_trace?.stages?.CONCLUSION?.input_sections?.introduction||"";
      state.drafts.BODY=currentResponse.research_trace?.stages?.CONCLUSION?.input_sections?.body||"";
      state.drafts.CONCLUSION=document.getElementById("stage-text").value;
      state.analyses.CONCLUSION=currentResponse;
      state.analysisSnapshots.CONCLUSION=analysisSnapshot("CONCLUSION");
      displayFeedback(currentResponse);`);
    return value(page,"studentFeedbackPresentation(currentResponse)");
  };

  // Problem A: the exact school-garden Conclusion selects the recorded neutral
  // synthesis review. The tutor and Stage Progress must agree, while the raw
  // mapping and evidence remain in the Transparency Inspector.
  const exact=actualStageResponses.EXACT;
  const exactSnapshot=JSON.stringify(exact);
  const neutral=show(exact);
  assert.equal(neutral.status,"NEUTRAL_OBSERVATION");
  assert.equal(neutral.writing_dimension,null,"neutral review keeps no corrective trait");
  assert.equal(neutral.writing_skill,null,"neutral review keeps no corrective lesson");
  assert.equal(JSON.stringify(Object.keys(neutral.displayed_guidance)),JSON.stringify(["What I noticed","What's working"]));
  assert.match(neutral.displayed_guidance["What's working"],/One sentence combines ideas from more than one earlier section/);
  assert.equal(neutral.tutor_items.length,1);
  assert.equal(neutral.tutor_items[0].neutral_result,true);
  assert.equal(neutral.tutor_items[0].label,"No specific writing issue detected");
  assert.equal(neutral.tutor_items[0].category,null);
  assert.equal(neutral.tutor_items[0].skill,null);
  assert.equal(neutral.tutor_items[0].lesson_id,"HELP-CONCLUSION-BRING-TOGETHER");
  assert.equal(JSON.stringify(neutral.tutor_items[0].rule_ids),JSON.stringify(["CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE"]));
  assert.equal(neutral.tutor_items[0].excerpt,null,"the synthesis record has no verified source span");
  assert.match(neutral.tutor_items[0].evidence_text,/No passage could be verified/);
  assert.doesNotMatch(neutral.tutor_items[0].task_text,/highlighted/i,"hidden or visible, no phantom highlight reference");

  assert.equal(e["feedback-writing-focus"].textContent,"No specific writing issue detected");
  assert.equal(e["feedback-writing-focus"].hidden,false);
  assert.equal(e["tutor-evidence-section"].hidden,true,"no Look at your writing heading");
  assert.equal(e["tutor-why-section"].hidden,true,"no Why it matters heading");
  assert.equal(e["tutor-task-section"].hidden,true,"no How to improve heading");
  assert.equal(e["tutor-working-section"].hidden,false,"the recorded positive stays visible");
  assert.match(e["tutor-working"].textContent,/One sentence combines ideas from more than one earlier section/);
  assert.doesNotMatch(e["tutor-working"].textContent,/does not prove/i,"the positive is not presented as the corrective caution");
  assert.equal(e["tutor-evidence"].children.length,0);
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0);
  assert.doesNotMatch(text(e["feedback-content"]),/Read the highlighted sentence/);

  assert.equal(e["stage-progress-title"].textContent,"No Specific Writing Issue Detected");
  assert.equal(e["stage-progress-badge"].dataset.state,"NO_ISSUE");
  assert.equal(e["stage-progress-review"].hidden,true);
  assert.equal(e["stage-progress-continue"].textContent,"Continue to Essay Review");
  assert.equal(e["stage-progress-noticed"].textContent,"Review your ideas before continuing.");

  // Neutral presentation is the same classification Stage Progress already uses.
  assert.equal(value(page,"STAGE_PROGRESS_NEUTRAL_BRANCHES.CONCLUSION.includes('conclusion_ideas_bring_together')"),true);
  assert.equal(value(page,"recordedNeutralSelection(currentResponse)"),true);
  assert.equal(neutral.recorded_feedback_decision.selection_branch,"conclusion_ideas_bring_together");
  const enginePanel=walk(e["nlp-transparency-content"]).find(item=>item.dataset.subPanel==="engine:primary");
  assert.ok(enginePanel);
  const openAll=async root=>{
    for(let pass=0;pass<8;pass+=1) {
      const closed=walk(root).filter(item=>item.tagName==="DETAILS"&&!item.open);
      if(!closed.length) break;
      for(const details of closed) { details.open=true; await dispatch(details,"toggle"); }
    }
  };
  await openAll(enginePanel);
  const inspector=text(enginePanel);
  assert.ok(inspector.includes("CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE"),"recorded rule evidence remains visible");
  assert.ok(inspector.includes("HELP-CONCLUSION-BRING-TOGETHER"),"recorded lesson mapping remains visible");
  assert.ok(inspector.includes("Bring Ideas Together"),"raw recorded trait/skill mapping remains visible");
  assert.ok(inspector.includes("No corrective trait or lesson displayed"),"neutral mapping disclosure");
  assert.equal(JSON.stringify(exact),exactSnapshot,"presentation never mutates the backend response");

  // Continue to Essay Review stays functional from the neutral Conclusion.
  await click(e["stage-progress-continue"]);
  assert.equal(value(page,"state.currentView"),"ESSAY_REVIEW");
  assert.equal(e["essay-review-panel"].hidden,false);

  // Problem B, valid evidence: the list-like Conclusion has recorded sentence
  // spans, so its corrective lesson may display and mark the verified text.
  const keyword=show(actualStageResponses.KEYWORD);
  assert.equal(keyword.status,"PREPARED_INLINE_GUIDANCE");
  assert.equal(keyword.writing_dimension,"Organization");
  assert.equal(keyword.writing_skill,"Bring Ideas Together");
  assert.equal(keyword.tutor_items[0].lesson_id,"HELP-CONCLUSION-LIST-ENDING");
  const validExcerpt=keyword.tutor_items[0].excerpt;
  assert.ok(validExcerpt && validExcerpt.contexts.length>0,"verified sentence spans produce an excerpt");
  assert.ok(validExcerpt.contexts.some(context=>context.marks.length>0));
  assert.ok(e["editor-mirror"].querySelectorAll("mark").length>0);
  assert.equal(e["tutor-evidence-section"].hidden,false);
  assert.equal(e["tutor-task-section"].hidden,false);
  assert.equal(e["stage-progress-title"].textContent,"Review Suggested");
  assert.equal(e["stage-progress-review"].hidden,false);
  assert.doesNotMatch(keyword.tutor_items[0].task_text,/highlighted/i,"this lesson task does not depend on a highlight");

  // Problem B, genuine corrective branch with no verified span: the new-word
  // Conclusion shows general guidance and never a highlighted-sentence task.
  const newWords=show(actualStageResponses.NEW_WORDS);
  assert.equal(newWords.status,"PREPARED_INLINE_GUIDANCE");
  assert.equal(newWords.writing_dimension,"Ideas");
  assert.equal(newWords.writing_skill,"Explain New Words");
  assert.equal(newWords.tutor_items[0].excerpt,null);
  assert.doesNotMatch(newWords.tutor_items[0].task_text,/highlighted/i);
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0);
  assert.equal(e["stage-progress-title"].textContent,"Review Suggested");
  assert.match(e["stage-progress-noticed"].textContent,/idea words in your Conclusion do not appear in the earlier sections/);

  // Problem B, shared component: a secondary Bring Ideas Together lesson can be
  // selected from a continuity concern. Its recorded comparison has no token
  // span, so the highlight-dependent task must fall back to general guidance.
  const secondary=show(actualStageResponses.SECONDARY);
  assert.equal(secondary.status,"PREPARED_INLINE_GUIDANCE");
  assert.equal(secondary.tutor_items[0].lesson_id,"HELP-CONCLUSION-EXPLAIN-NEW-WORDS","the recorded primary branch stays first");
  const secondaryItem=secondary.tutor_items.find(item=>item.lesson_id==="HELP-CONCLUSION-BRING-TOGETHER");
  assert.ok(secondaryItem,"the continuity concern selects the shared lesson");
  assert.ok(secondary.tutor_items.indexOf(secondaryItem)>0,"the shared lesson is an additional supported tab");
  assert.ok(secondaryItem.rule_ids.includes("CONCLUSION.CONTINUITY.INTRODUCTION_LEXICAL_COMPARISON"));
  assert.equal(secondaryItem.excerpt,null);
  assert.match(secondaryItem.evidence_text,/No passage could be verified/);
  const bringTogether=value(page,"scaffoldingCatalog.lessons.find(l=>l.lesson_id==='HELP-CONCLUSION-BRING-TOGETHER').tutor");
  assert.equal(secondaryItem.task_text,bringTogether.task_fallback);
  assert.doesNotMatch(secondaryItem.task_text,/highlighted/i);
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0);
  assert.equal(e["stage-progress-title"].textContent,"Review Suggested");

  // The verifier itself is evidence-conditional: the same lesson produces a
  // verified span for a real occurrence list and none for the synthesis record.
  assert.equal(value(page,"tutorEvidenceExcerpt(secondaryResponse,['CONCLUSION.CONTINUITY.INTRODUCTION_LEXICAL_COMPARISON'],secondaryResponse.analysis.linguistic_observations.text,secondaryResponse.analysis.linguistic_observations)"),null);
  const keywordExcerpt=value(page,"tutorEvidenceExcerpt(keywordResponse,['CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE'],keywordResponse.analysis.linguistic_observations.text,keywordResponse.analysis.linguistic_observations)");
  assert.ok(keywordExcerpt && keywordExcerpt.contexts.length>0);

  // Editing after analysis withdraws the old Conclusion result rather than
  // presenting stale evidence or a stale neutral state.
  show(actualStageResponses.NEW_WORDS);
  e["stage-text"].value+=" Edited.";
  await input(e["stage-text"]);
  assert.equal(e["feedback-content"].hidden,true);
  assert.equal(e["editor-mirror"].querySelectorAll("mark").length,0);
  assert.equal(e["stage-progress-title"].textContent,"Ready to Review Your Writing?");
  assert.match(e["stage-progress-task"].textContent,/changed since the last analysis/);
  assert.equal(e["stage-progress-review"].hidden,true);

  console.log("Feedback presentation scenarios completed. Conclusion feedback correction scenarios completed.");
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
    _run_workspace_frontend(tmp_path, scenario, _responses())
