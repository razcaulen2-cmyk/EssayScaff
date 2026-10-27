"""Branch-specific provenance contracts, not rhetorical-quality assessments.

Controlled records below exercise feedback selection independently of spaCy.
Real-pipeline and authenticated API cases then verify the actual event contracts.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from services.essay_analysis_service import EssayAnalysisService
from services.feedback_service import FeedbackService


FIELDS = ("Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step")
SPAN = {"text": "Readers", "start": 0, "end": 7}
METHODS = {"INTRODUCTION": "generate", "BODY": "generate_body", "CONCLUSION": "generate_conclusion"}


def event(rule_id):
    """A controlled emitted record using the stage's existing schema and Rule ID."""
    goal = ".GOAL." in rule_id
    record = {
        "rule_id": rule_id,
        "triggering_condition": f"Recorded fixture condition: {rule_id}",
        "evidence_type": "stage_scope_configuration" if goal else "controlled_test_evidence",
    }
    evidence = [] if goal else [deepcopy(SPAN)]
    if rule_id.startswith("INTRO."):
        record.update(triggered=True, evidence=evidence, limitation="Structure and wording only.")
    else:
        record.update(actual_evidence=evidence, limitations="Structure and wording only.")
        if rule_id.startswith("BODY."):
            record["triggered"] = True
        else:
            record.update(fired=True, source_sections=["conclusion"])
    return record


def intro_analysis(case):
    central = case != "specific_without_root"
    developed = case == "multiple_clauses"
    return {
        "text_presence": {"status": "SENTENCE_STRUCTURE_OBSERVED" if central else "FRAGMENTARY_OR_NONCLAUSAL_TEXT"},
        "lexical_topic_evidence": {"observed_focus_terms": ["reading"]},
        "observable_structure": {
            "central_direction_candidates": [deepcopy(SPAN)] if central else [],
            "list_or_fragment_candidate": {"keyword_list_candidate": False},
            "incomplete_subordinator_candidates": [],
            "introductory_context_candidates": [],
        },
        "development_evidence": {
            "status": "STRUCTURAL_ELABORATION_CANDIDATE" if developed else "NO_ADDITIONAL_CLAUSE_ELABORATION_OBSERVED",
        },
        "linguistic_observations": {"counts": {"sentence_count": 1}},
        "rule_evidence": [event(rule_id) for rule_id in (
            "INTRO.GOAL.OBSERVABLE_INTRODUCTION",
            "INTRO.TOPIC.FOCUS_TERMS_OBSERVED",
            "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE" if central else "INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE",
            "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES" if developed else "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE",
            *(["INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED"] if case == "single_clause" else []),
        )],
    }


def paragraph(index):
    return {
        "paragraph_index": index,
        "substantive": True,
        "counts": {"sentence_count": 2},
        "fragment_or_list_candidate": {"keyword_list_candidate": False},
        "observed_focus_terms": ["reading"],
        "topic_sentence_candidates": [],
        "clause_structure_candidates": [deepcopy(SPAN)],
        "supporting_detail_candidates": {"candidates": [deepcopy(SPAN), deepcopy(SPAN)]},
        "repetition_observations": {
            "repeated_surface_content_words": [],
            "repeated_sentence_openings": [],
        },
    }


def body_analysis(case):
    paragraphs = [] if case == "empty" else [paragraph(1)]
    if case in {"list", "unlinked", "limited", "repeated"}:
        paragraphs.append(paragraph(2))
        if case == "list":
            paragraphs[1]["fragment_or_list_candidate"]["keyword_list_candidate"] = True
            paragraphs[1]["clause_structure_candidates"] = []
            paragraphs[1]["supporting_detail_candidates"]["candidates"] = []
        elif case == "limited":
            paragraphs[1]["supporting_detail_candidates"]["candidates"] = []
        elif case == "repeated":
            paragraphs[1]["repetition_observations"]["repeated_sentence_openings"] = [{"opening": "readers learn"}]
        # The selected issue must remain P2, even after later paragraphs are visited.
        paragraphs.append(paragraph(3))
    pairs = [{"status": "NO_EXPLICIT_LEXICAL_LINK_OBSERVED", "paragraph_pair": [1, 2]}] if case == "unlinked" else []
    available = case != "no_introduction"
    analysis = {
        "paragraphs": paragraphs,
        "cross_paragraph_continuity": {
            "status": "PAIRWISE_OBSERVATIONS" if pairs else "NOT_APPLICABLE_SINGLE_PARAGRAPH",
            "paragraph_pairs": pairs,
        },
        "introduction_to_body_continuity": {
            "status": "LEXICAL_COMPARISON_AVAILABLE" if available else "NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED",
            "direct_lexical_continuity": [deepcopy(SPAN)] if available else [],
            "lemma_normalized_continuity": [],
            "unobserved_introduction_concepts": [],
        },
    }
    ids = ["BODY.GOAL.DEVELOP_BODY_IDEAS", "BODY.LIMITATION.NO_SEMANTIC_VALIDATION"]
    if not paragraphs:
        ids.append("BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH")
    for item in paragraphs:
        prefix = f"BODY.P{item['paragraph_index']}."
        ids.extend([prefix + "PARAGRAPH.SEGMENTED", prefix + "PARAGRAPH.FOCUS_TERMS_OBSERVED"])
        ids.append(prefix + ("SUPPORTING_DETAIL.CANDIDATE" if item["supporting_detail_candidates"]["candidates"] else "SUPPORTING_DETAIL.NOT_OBSERVED"))
        if item["fragment_or_list_candidate"]["keyword_list_candidate"]:
            ids.append(prefix + "PARAGRAPH.KEYWORD_LIST_CANDIDATE")
        if item["repetition_observations"]["repeated_sentence_openings"]:
            ids.append(prefix + "REPETITION.REPEATED_SENTENCE_OPENINGS")
    if pairs:
        ids.append("BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON")
    if available:
        ids.append("BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON")
    analysis["rule_evidence"] = [event(rule_id) for rule_id in ids]
    return analysis


def conclusion_analysis(case):
    empty = case == "empty"
    listed = case == "list"
    clause = case not in {"empty", "list", "novel", "no_closure", "closure"}
    synthesis = case == "synthesis"
    closed = case not in {"empty", "list", "no_closure"}
    analysis = {
        "text_presence": {"alphabetic_word_count": 0 if empty else 5, "keyword_list_candidate": listed},
        "lexical_topic_evidence": {"observed_focus_terms": [] if empty else ["reading"]},
        "clause_candidates": [deepcopy(SPAN)] if clause else [],
        "introduction_to_conclusion_continuity": {
            "status": "NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED",
            "direct_lexical_continuity": [], "lemma_normalized_continuity": [],
        },
        "body_to_conclusion_continuity": {
            "status": "NOT_AVAILABLE_NO_BODY_SUPPLIED",
            "direct_lexical_continuity": [], "lemma_normalized_continuity": [],
        },
        "synthesis_structure_candidates": {
            "status": "SYNTHESIS_STRUCTURE_CANDIDATE" if synthesis else "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED",
            "candidates": [deepcopy(SPAN)] if synthesis else [],
        },
        "closure_candidates": {
            "status": "CLOSURE_STRUCTURE_CANDIDATE" if closed else "NO_CLOSURE_CANDIDATE_OBSERVED",
            "candidates": [deepcopy(SPAN)] if closed else [],
        },
        "new_material_observations": {
            "unobserved_concept_candidates": [{"normalized_form": "different concept"}] if case == "novel" else [],
            "phrase_combinations_of_observed_concepts": [],
        },
    }
    ids = [
        "CONCLUSION.GOAL.REVIEW_TOPIC_AND_PRIOR_IDEAS",
        "CONCLUSION.LIMITATION.NO_SEMANTIC_VALIDATION",
        "CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC" if empty else "CONCLUSION.TEXT.PRESENT",
        "CONCLUSION.STRUCTURE.CLAUSE_CANDIDATE" if clause else "CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE",
        "CONCLUSION.TOPIC.NO_FOCUS_MATCH" if empty else "CONCLUSION.TOPIC.FOCUS_MATCHES",
        "CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE" if closed else "CONCLUSION.CLOSURE.NO_CANDIDATE",
    ]
    if listed:
        ids.append("CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE")
    if synthesis or case == "novel":
        analysis["introduction_to_conclusion_continuity"]["status"] = "LEXICAL_COMPARISON_AVAILABLE"
        analysis["introduction_to_conclusion_continuity"]["direct_lexical_continuity"] = [deepcopy(SPAN)]
        if not synthesis:
            analysis["synthesis_structure_candidates"]["status"] = "NO_SYNTHESIS_STRUCTURE_CANDIDATE_OBSERVED"
        ids.append("CONCLUSION.CONTINUITY.INTRODUCTION_LEXICAL_COMPARISON")
        ids.append("CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE" if synthesis else "CONCLUSION.SYNTHESIS.NO_CANDIDATE")
    else:
        ids.extend(["CONCLUSION.CONTINUITY.INTRODUCTION_UNAVAILABLE", "CONCLUSION.SYNTHESIS.UNAVAILABLE"])
    ids.append("CONCLUSION.CONTINUITY.BODY_UNAVAILABLE")
    if case == "novel":
        ids.append("CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS")
    analysis["rule_evidence"] = [event(rule_id) for rule_id in ids]
    return analysis


FACTORIES = {"INTRODUCTION": intro_analysis, "BODY": body_analysis, "CONCLUSION": conclusion_analysis}
INTRO_CASES = [
    ("single_clause", "intro_ideas_state_position", ["INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED", "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE"]),
    ("multiple_clauses", "intro_ideas_review_details", ["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE", "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES"]),
    ("specific_without_root", "intro_ideas_main_point", ["INTRO.TOPIC.FOCUS_TERMS_OBSERVED", "INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE"]),
]
BODY_CASES = [
    ("empty", "body_neutral_empty", ["BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH"]),
    ("list", "body_organization_paragraph_shape", ["BODY.P2.PARAGRAPH.KEYWORD_LIST_CANDIDATE"]),
    ("unlinked", "body_organization_paragraph_link", ["BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON"]),
    ("limited", "body_ideas_develop_point", ["BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED"]),
    ("repeated", "body_sentence_fluency_sentence_beginnings", ["BODY.P2.REPETITION.REPEATED_SENTENCE_OPENINGS"]),
    ("no_introduction", "body_neutral_observable", []),
    ("general", "body_neutral_observable", []),
]
CONCLUSION_CASES = [
    ("empty", "conclusion_neutral_empty", ["CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC"]),
    ("list", "conclusion_organization_bring_together", ["CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE"]),
    ("novel", "conclusion_ideas_new_words", ["CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS"]),
    ("synthesis", "conclusion_ideas_bring_together", ["CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE"]),
    ("no_closure", "conclusion_organization_clear_ending", ["CONCLUSION.CLOSURE.NO_CANDIDATE"]),
    ("closure", "conclusion_organization_clear_ending", ["CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE"]),
    ("missing_prior", "conclusion_organization_clear_ending", ["CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE"]),
]

# Captured from the current trait-based FeedbackService, including all five fields/list order.
BASELINE_FIELD_DIGESTS = {
    "INTRODUCTION:single_clause": "65064cbd6c0a333211584e2ebd348057ce46b325ce76092487f6f20b6a6b2356",
    "INTRODUCTION:multiple_clauses": "67fede9df5ad27f30e2800f4adcceb1e30b93a092b30107e4ec1e05c8f9e5bf3",
    "INTRODUCTION:specific_without_root": "abaa278d499c6a1697657852a689d8318593da10f6bdf8faf90f63558d283c8d",
    "BODY:empty": "7d60e22b21bedbcfb948ef3b35e9803e591241c75a72a1df18e4ecc25d39b704",
    "BODY:list": "686431b768fdb8e964521b60bb364b3f615b5a5b3afbe93cc01c93c71dd68629",
    "BODY:unlinked": "798f0edd6a883c4c718de65fe6ac09ab642cdce9818aa35133f14565a42efb9a",
    "BODY:limited": "f1e12241ce5a8d2df854e07bca52461f4b639d3c5ffe2d3a17b036ccd0e25831",
    "BODY:repeated": "5eb973a4e69815005a5cc96d7ce80f4d9075a99df1e13f068192b6ddd7d926d7",
    "BODY:no_introduction": "7faa8d592898dc38a0d8d85ff0b80bbd50a1ef89482ed81a64fdc85d31e9a856",
    "BODY:general": "3a54de9a42dcac535f024025a441ecfb1d7417e0683186722c070db93bd06eee",
    "CONCLUSION:empty": "2eccf4b0c507d5cbeb57de8bc1fb1dcb4608272fa2a31caa39ea963d3d4d8867",
    "CONCLUSION:list": "8ea732dc4f80fa50c8e61dba50f32fe6851e4197ae5a8fa2cfb6f4e20d030fc9",
    "CONCLUSION:novel": "7731356c371b481886534e78be44d99cc5e6a188a684e53ca99b9a120957ce5e",
    "CONCLUSION:synthesis": "5544e22d9e6c1443b01cbe0d7d503566fadc927075884930e3a09e0f45af145e",
    "CONCLUSION:no_closure": "474e666a1788e8ab332e5f65b3291604e268ecafe0daeb48cfd333186d7918b3",
    "CONCLUSION:closure": "82d493e6a159363547c4314a69e7709df1f38c8ecda5933d538e4028a69ec886",
    "CONCLUSION:missing_prior": "72f4b6afe866e134bbf7a88b09ba5bfde0c77b3c75496fea9eb4437f1bf6b5d7",
}

# Intentional Introduction Ideas wording/selection changes for Phase 1. The old
# digests above and the actual pre-change protected fixture are retained; Body
# and Conclusion continue to use their ORIGINAL digests unchanged.
INTRO_IDEAS_FIELD_DIGESTS = {
    "single_clause": "0efcd0c4387c2d023d99a7e05de1707ba3beaaa2b948d7b3bb1c7647fef2fd89",
    "multiple_clauses": "6662263d46e16a1d3952d1fd300502ddef7a491e2c6c6976b22eb684cb8be601",
    "specific_without_root": "3b4f04a99108cdf671b37cb5b3d1d4526fee2c6589e76c4c997dfac049cb4e9c",
}


def fields_digest(feedback):
    data = json.dumps({field: feedback[field] for field in FIELDS}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def field_rules(feedback, field):
    return [item["rule_id"] for item in feedback["Feedback Provenance"] if item["feedback_field"] == field]


def assert_event_contract(analysis, feedback):
    events = {item["rule_id"]: item for item in analysis["rule_evidence"]}
    for item in feedback["Feedback Provenance"]:
        source = events[item["rule_id"]]
        assert source.get("triggered", True) and source.get("fired", True)
        assert item["triggering_condition"] == source["triggering_condition"]
        assert item["actual_evidence"] == source.get("actual_evidence", source.get("evidence"))
        assert item["evidence_type"] == source["evidence_type"]
        assert item["limitations"] == source.get("limitations", source.get("limitation"))
        if "source_sections" in source:
            assert item["source_sections"] == source["source_sections"]
    for field, decision in feedback["_Research Decision Trace"]["fields"].items():
        assert decision["rule_ids"] == field_rules(feedback, field)
    json.dumps(feedback)


@pytest.mark.parametrize("case,branch,expected", INTRO_CASES)
def test_intro_primary_links_emitted_evidence_without_changing_branch(case, branch, expected):
    analysis = intro_analysis(case)
    original = deepcopy(analysis)
    feedback = FeedbackService().generate(analysis, include_trace=True)
    assert field_rules(feedback, "Primary Feedback") == expected
    choice = feedback["_Research Decision Trace"]["fields"]["Primary Feedback"]
    assert choice["selection_branch"] == branch
    assert choice["selection_condition"]
    assert fields_digest(feedback) == INTRO_IDEAS_FIELD_DIGESTS[case]
    assert_event_contract(analysis, feedback)
    assert analysis == original


@pytest.mark.parametrize("case,branch,expected", BODY_CASES)
def test_every_body_next_step_branch_has_its_own_basis(case, branch, expected):
    analysis = body_analysis(case)
    original = deepcopy(analysis)
    feedback = FeedbackService().generate_body(analysis, include_trace=True)
    assert field_rules(feedback, "Next Step") == expected
    choice = feedback["_Research Decision Trace"]["fields"]["Next Step"]
    assert choice["selection_branch"] == branch
    if case in {"no_introduction", "general"}:
        assert feedback["Next Step"] == "" and feedback["Needs Attention"] == []
        assert feedback["_Research Decision Trace"]["selection_status"] == "NO_SUPPORTED_CONCERN_SELECTED"
        assert feedback["_Research Decision Trace"]["instructional_feedback"]["items"] == []
        assert not any("UNAVAILABLE" in item["rule_id"] for item in analysis["rule_evidence"])
    else:
        assert feedback["Next Step"]
        assert feedback["_Research Decision Trace"]["selection_status"] in {"SUPPORTED_CONCERN_SELECTED", "INPUT_REQUIRED"}
    # Preserve the ACTUAL pre-repair five-field snapshots against their original
    # hashes. Live Body wording/neutrality intentionally changes in this repair;
    # the branch, event contract and explicit no-forced-task policy are checked
    # above and in test_body_feedback_repair.py, rather than silently repinning.
    baseline = json.loads(Path(__file__).with_name("body_feedback_protected_baseline.json").read_text(encoding="utf-8"))
    assert fields_digest(baseline[case]) == BASELINE_FIELD_DIGESTS[f"BODY:{case}"]
    assert_event_contract(analysis, feedback)
    assert analysis == original


@pytest.mark.parametrize("case,branch,expected", CONCLUSION_CASES)
def test_every_conclusion_next_step_branch_has_its_own_basis(case, branch, expected):
    analysis = conclusion_analysis(case)
    original = deepcopy(analysis)
    feedback = FeedbackService().generate_conclusion(analysis, include_trace=True)
    choices = feedback["_Research Decision Trace"]["fields"]
    assert choices["Next Step"]["selection_branch"] == branch
    assert field_rules(feedback, "Next Step") == expected
    if case in {"novel", "no_closure", "closure"}:
        assert choices["Primary Feedback"]["selection_branch"] == "conclusion_neutral_review"
        assert field_rules(feedback, "Primary Feedback") == ["CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE"]
        assert field_rules(feedback, "Next Step") != field_rules(feedback, "Primary Feedback")
    assert fields_digest(feedback) == BASELINE_FIELD_DIGESTS[f"CONCLUSION:{case}"]
    assert_event_contract(analysis, feedback)
    assert analysis == original


@pytest.mark.parametrize("overlap", ["positive", "negative", "missing"])
def test_body_overlap_is_associated_with_the_displayed_field(overlap):
    analysis = body_analysis("no_introduction" if overlap == "missing" else "general")
    if overlap == "negative":
        links = analysis["introduction_to_body_continuity"]
        links["direct_lexical_continuity"] = []
        links["unobserved_introduction_concepts"] = ["unmatched"]
        next(item for item in analysis["rule_evidence"] if item["rule_id"] == "BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON")["actual_evidence"] = []
    output = FeedbackService().generate_body(analysis, include_trace=True)
    rule = "BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON"
    assert (rule in field_rules(output, "What's Working")) == (overlap == "positive")
    assert rule not in field_rules(output, "Needs Attention"), "lexical absence is an observation, not a writing defect"
    assert output["_Research Decision Trace"]["selection_status"] == "NO_SUPPORTED_CONCERN_SELECTED"
    assert output["Next Step"] == ""
    assert_event_contract(analysis, output)


def test_positive_body_overlap_does_not_remove_a_separate_warning():
    analysis = body_analysis("limited")
    output = FeedbackService().generate_body(analysis, include_trace=True)
    assert "BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON" in field_rules(output, "What's Working")
    assert "BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON" not in field_rules(output, "Needs Attention")
    assert "BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED" in field_rules(output, "Needs Attention")
    assert output["Needs Attention"][0] == "Paragraph 2 has a possible statement, but no additional sentence part was recorded under this check."
    assert output["_Research Decision Trace"]["instructional_feedback"]["items"][0]["lesson_id"] == "HELP-BODY-DEVELOP-POINT"


@pytest.mark.parametrize("stage,case", [
    ("INTRODUCTION", "multiple_clauses"), ("BODY", "limited"), ("CONCLUSION", "closure"),
])
@pytest.mark.parametrize("state", ["absent", "triggered_false", "fired_false", "legacy_no_flags"])
def test_missing_or_nonfired_events_do_not_get_invented_links(stage, case, state):
    analysis = FACTORIES[stage](case)
    method = getattr(FeedbackService(), METHODS[stage])
    original_feedback = method(analysis, include_trace=True)
    field = "Primary Feedback" if stage == "INTRODUCTION" else "Next Step"
    rule_id = field_rules(original_feedback, field)[0]
    record = next(item for item in analysis["rule_evidence"] if item["rule_id"] == rule_id)
    if state == "absent":
        analysis["rule_evidence"].remove(record)
    elif state == "legacy_no_flags":
        record.pop("triggered", None)
        record.pop("fired", None)
    else:
        record[state.removesuffix("_false")] = False
    before = deepcopy(analysis)
    output = method(analysis, include_trace=True)
    assert (rule_id in field_rules(output, field)) == (state == "legacy_no_flags")
    if stage == "BODY" and state != "legacy_no_flags":
        assert output["Next Step"] == "" and output["Needs Attention"] == []
        assert output["_Research Decision Trace"]["selection_status"] == "NO_SUPPORTED_CONCERN_SELECTED"
        assert output["_Research Decision Trace"]["instructional_feedback"]["items"] == []
    else:
        assert {name: output[name] for name in FIELDS} == {name: original_feedback[name] for name in FIELDS}
        assert output["_Research Decision Trace"]["fields"][field]["selection_branch"] == original_feedback["_Research Decision Trace"]["fields"][field]["selection_branch"]
    assert output["_Research Decision Trace"]["fields"][field]["selection_condition"]
    assert_event_contract(analysis, output)
    assert analysis == before


@pytest.mark.parametrize("stage,case", [
    ("INTRODUCTION", "multiple_clauses"), ("BODY", "no_introduction"), ("CONCLUSION", "closure"),
])
def test_decision_conditions_remain_available_without_any_emitted_events(stage, case):
    analysis = FACTORIES[stage](case)
    method = getattr(FeedbackService(), METHODS[stage])
    before = method(analysis, include_trace=True)
    analysis["rule_evidence"] = []
    after = method(analysis, include_trace=True)
    assert after["Feedback Provenance"] == []
    if stage == "BODY":
        assert after["What's Working"] == [] and after["Needs Attention"] == [] and after["Next Step"] == ""
        assert after["_Research Decision Trace"]["instructional_feedback"]["strengths"] == []
        assert after["Primary Feedback"] == before["Primary Feedback"]
    else:
        assert {field: after[field] for field in FIELDS} == {field: before[field] for field in FIELDS}
    for field in ("Primary Feedback", "Next Step"):
        decision = after["_Research Decision Trace"]["fields"][field]
        assert decision["rule_ids"] == []
        assert decision["selection_condition"]
        assert decision["selection_branch"] == before["_Research Decision Trace"]["fields"][field]["selection_branch"]


@pytest.fixture(scope="module")
def coordinator():
    return EssayAnalysisService()


ENV_TOPIC = "Should communities reduce their use of single-use plastics?"
ENV_FOCUS = ["single-use plastics", "communities", "reduce", "environment"]
ENV_INTRO = "Communities should reduce their use of single-use plastics because plastic waste can harm local waterways."
ENV_BODY = (
    "Single-use plastics often become waste after only one use. For example, plastic bags and bottles can end up in rivers and drainage systems. This waste can harm animals living near the water.\n\n"
    "In addition, communities can reduce plastic waste by using reusable bags and containers. Reusable products can be used many times, so fewer disposable items may be thrown away."
)
REAL_CONCLUSIONS = [
    ("In conclusion.", True, "conclusion_neutral_review", "conclusion_organization_clear_ending", "CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE"),
    ("Plastic waste remains.", True, "conclusion_ideas_bring_together", "conclusion_ideas_bring_together", "CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE"),
    ("Single-use plastics should be reduced.", True, "conclusion_neutral_review", "conclusion_organization_clear_ending", "CONCLUSION.CLOSURE.NO_CANDIDATE"),
    ("Communities should reduce plastics through neighborhood refill stations.", True, "conclusion_ideas_new_words", "conclusion_ideas_new_words", "CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS"),
    ("Communities can reduce plastic waste.", False, "conclusion_organization_clear_ending", "conclusion_organization_clear_ending", "CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE"),
    ("", True, "conclusion_neutral_empty", "conclusion_neutral_empty", "CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC"),
    ("Plastic. Waste. Rivers. Animals.", True, "conclusion_organization_bring_together", "conclusion_organization_bring_together", "CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE"),
]


@pytest.mark.parametrize("text,case", [
    ("Communities reduce single-use plastics.", "single_clause"),
    ("Communities should reduce single-use plastics and they should protect the environment.", "multiple_clauses"),
    ("Single-use plastics should be reduced.", "specific_without_root"),
    ("Single-use plastics.", "actual_nonclausal_focus"),
])
def test_real_intro_primary_branches_use_only_their_existing_events(coordinator, text, case):
    result = coordinator.analyze(ENV_TOPIC, ENV_FOCUS, introduction_text=text, include_research_trace=True)
    stage = result["stages"]["INTRODUCTION"]
    trace = result["research_trace"]["stages"]["INTRODUCTION"]["feedback_decisions"]
    if case == "specific_without_root":
        # This formerly missed passive now has a recorded subject + finite MD
        # auxiliary + VBN root. Keep the difficult real example, correct the
        # expectation, and retain a genuinely nonclausal focus case below.
        branch = "intro_ideas_develop_main_point"
        expected = ["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE", "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE"]
    else:
        _, branch, expected = next(row for row in INTRO_CASES if row[0] == ("specific_without_root" if case == "actual_nonclausal_focus" else case))
    assert trace["fields"]["Primary Feedback"]["selection_branch"] == branch
    assert field_rules(stage["feedback"], "Primary Feedback") == expected
    assert_event_contract(stage["analysis"], {**stage["feedback"], "_Research Decision Trace": trace})


@pytest.mark.parametrize("text,introduction,case,paragraph_number", [
    ("", None, "empty", None),
    ("Plastics. Communities. Environment. Waste.", None, "list", 1),
    ("Wind turbines generate electricity.\n\nReaders discuss books.", None, "limited", 1),
    ("Wind turbines generate electricity. They produce power.\n\nReaders discuss books. Librarians organize shelves.", None, "unlinked", None),
    ("Communities reduce plastics.", None, "limited", 1),
    ("Students read books daily. Students read books at home.", None, "repeated", 1),
    ("Communities reduce plastics. They protect waterways.", None, "no_introduction", None),
    ("Libraries offer books. Readers discuss stories.", ENV_INTRO, "general", None),
])
def test_real_body_next_step_branches_reuse_evidence_without_reclassifying_writing(coordinator, text, introduction, case, paragraph_number):
    result = coordinator.analyze(ENV_TOPIC, ENV_FOCUS, introduction_text=introduction, body_text=text, include_research_trace=True)
    stage = result["stages"]["BODY"]
    trace = result["research_trace"]["stages"]["BODY"]["feedback_decisions"]
    _, branch, expected = next(row for row in BODY_CASES if row[0] == case)
    if paragraph_number:
        expected = [rule_id.replace("BODY.P2.", f"BODY.P{paragraph_number}.") for rule_id in expected]
    assert trace["fields"]["Next Step"]["selection_branch"] == branch
    assert field_rules(stage["feedback"], "Next Step") == expected
    assert_event_contract(stage["analysis"], {**stage["feedback"], "_Research Decision Trace": trace})


@pytest.mark.parametrize("text,context,primary,next_branch,rule", REAL_CONCLUSIONS)
def test_real_conclusion_examples_keep_rules_and_link_the_selected_action(coordinator, text, context, primary, next_branch, rule):
    result = coordinator.analyze(
        ENV_TOPIC, ENV_FOCUS,
        introduction_text=ENV_INTRO if context else None,
        body_text=ENV_BODY if context else None,
        conclusion_text=text, include_research_trace=True,
    )
    stage = result["stages"]["CONCLUSION"]
    trace = result["research_trace"]["stages"]["CONCLUSION"]["feedback_decisions"]["fields"]
    assert trace["Primary Feedback"]["selection_branch"] == primary
    assert trace["Next Step"]["selection_branch"] == next_branch
    assert field_rules(stage["feedback"], "Next Step") == [rule]
    feedback = {**stage["feedback"], "_Research Decision Trace": {"fields": trace}}
    assert_event_contract(stage["analysis"], feedback)


@pytest.mark.parametrize("stage", ["INTRODUCTION", "BODY", "CONCLUSION"])
def test_student_compact_and_teacher_full_provenance_resolve_same_events(tmp_path, coordinator, stage):
    from werkzeug.security import generate_password_hash
    from app import create_app
    from services.draft_store import DraftStore
    from tests.auth_helpers import login_student, register_student

    app = create_app(analysis_service=coordinator, secret_key="provenance-test-secret")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "provenance.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    store.create_teacher_user("provenance_teacher", generate_password_hash("teacher-password-1"))
    payload = {
        "stage_id": stage, "assignment_topic": ENV_TOPIC,
        "focus_terms": ENV_FOCUS, "include_transparency_trace": True,
    }
    if stage == "INTRODUCTION":
        payload["introduction_text"] = ENV_INTRO
    elif stage == "BODY":
        payload.update(introduction_text=ENV_INTRO, body_text=ENV_BODY)
    else:
        payload.update(introduction_text=ENV_INTRO, body_text=ENV_BODY, conclusion_text="In conclusion.")
    student = app.test_client()
    assert register_student(student, "provenance_student").status_code == 302
    student_response = student.post("/api/analyze-stage", json=payload)
    assert student_response.status_code == 200
    compact = student_response.get_json()
    teacher = app.test_client()
    assert login_student(teacher, "provenance_teacher", "teacher-password-1").status_code == 302
    teacher_response = teacher.post("/api/research-inspector/analyze", json=payload)
    assert teacher_response.status_code == 200
    full = teacher_response.get_json()
    assert {field: compact["feedback"][field] for field in FIELDS} == {field: full["feedback"][field] for field in FIELDS}
    links = compact["feedback"]["Feedback Provenance"]
    assert links == [{key: item[key] for key in ("feedback_field", "rule_id")} for item in full["feedback"]["Feedback Provenance"]]
    events = {item["rule_id"]: item for item in compact["analysis"]["rule_evidence"]}
    for item, detailed in zip(links, full["feedback"]["Feedback Provenance"]):
        assert set(item) == {"feedback_field", "rule_id"}
        source = events[item["rule_id"]]
        assert source.get("triggered", True) and source.get("fired", True)
        assert detailed["actual_evidence"] == source.get("actual_evidence", source.get("evidence"))
        assert detailed["triggering_condition"] == source["triggering_condition"]
    assert_event_contract(full["analysis"], {
        **full["feedback"],
        "_Research Decision Trace": full["research_trace"]["stages"][stage]["feedback_decisions"],
    })
