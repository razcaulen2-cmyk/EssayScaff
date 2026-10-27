"""Replacement contract tests for the trait-based Writing Tutor rewrite.

Tests A–X cover the backend branch matrix, recorded trait/skill labels, message
hygiene, the prepared catalog v3, the decision-flow purpose table and the
student-facing presentation/panel wiring, each with controlled evidence.
"""

from copy import deepcopy
import json
import re
from pathlib import Path

import pytest

from services.feedback_service import BRANCH_TRAIT_SKILL, FeedbackService
from services.tutoring_lessons import load_feedback_help

PROJECT = Path(__file__).resolve().parent.parent
APP_JS = (PROJECT / "static" / "app.js").read_text(encoding="utf-8")
INDEX_HTML = (PROJECT / "templates" / "index.html").read_text(encoding="utf-8")
STYLE_CSS = (PROJECT / "static" / "style.css").read_text(encoding="utf-8")

FIELDS = ("Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step")
TRAIT_DIMENSIONS = {"Ideas", "Organization", "Sentence Fluency", "Word Choice", "Conventions"}
FORBIDDEN_MESSAGE_WORDS = ("lexical", "normalized", "heuristic", "rhetorical", "candidate", "clause", "provenance", "paraphrase")

SPAN = {"text": "readers", "start": 0, "end": 7}


def event(rule_id):
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
    base = {
        "text_presence": {"status": "SENTENCE_STRUCTURE_OBSERVED"},
        "lexical_topic_evidence": {"observed_focus_terms": []},
        "observable_structure": {
            "central_direction_candidates": [],
            "list_or_fragment_candidate": {"keyword_list_candidate": False},
            "incomplete_subordinator_candidates": [],
            "introductory_context_candidates": [],
        },
        "development_evidence": {"status": "NO_ADDITIONAL_CLAUSE_ELABORATION_OBSERVED"},
        "linguistic_observations": {"counts": {"sentence_count": 1}},
        "rule_evidence": ["INTRO.GOAL.OBSERVABLE_INTRODUCTION"],
    }
    if case == "empty":
        base["text_presence"]["status"] = "EMPTY"
        base["rule_evidence"].append("INTRO.TEXT.EMPTY_OR_NONALPHABETIC")
    elif case == "whitespace":
        base["text_presence"]["status"] = "WHITESPACE_ONLY"
        base["rule_evidence"].append("INTRO.TEXT.EMPTY_OR_NONALPHABETIC")
    elif case == "punctuation":
        base["text_presence"]["status"] = "PUNCTUATION_ONLY"
        base["rule_evidence"].append("INTRO.TEXT.EMPTY_OR_NONALPHABETIC")
    elif case == "list":
        base["observable_structure"]["list_or_fragment_candidate"]["keyword_list_candidate"] = True
        base["rule_evidence"].append("INTRO.TEXT.KEYWORD_LIST_CANDIDATE")
    elif case == "incomplete":
        base["observable_structure"]["incomplete_subordinator_candidates"] = [
            {"text": "although", "start": 0, "end": 8, "sentence_index": 0},
        ]
        base["rule_evidence"].extend([
            "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR",
            "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
        ])
    elif case == "broad_only":
        base["lexical_topic_evidence"]["observed_focus_terms"] = ["student", "use"]
        base["rule_evidence"].append("INTRO.TOPIC.FOCUS_TERMS_OBSERVED")
    elif case == "no_focus":
        base["rule_evidence"].append("INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED")
    elif case == "main_point":
        base["lexical_topic_evidence"]["observed_focus_terms"] = ["reading"]
        base["observable_structure"]["central_direction_candidates"] = [deepcopy(SPAN)]
        base["rule_evidence"].extend([
            "INTRO.TOPIC.FOCUS_TERMS_OBSERVED",
            "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
            "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE",
        ])
    elif case == "point_reason":
        base["lexical_topic_evidence"]["observed_focus_terms"] = ["reading"]
        base["observable_structure"]["central_direction_candidates"] = [deepcopy(SPAN)]
        base["development_evidence"]["status"] = "STRUCTURAL_ELABORATION_CANDIDATE"
        base["rule_evidence"].extend([
            "INTRO.TOPIC.FOCUS_TERMS_OBSERVED",
            "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
            "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES",
        ])
    elif case == "one_sentence_specific":
        base["lexical_topic_evidence"]["observed_focus_terms"] = ["reading"]
        base["rule_evidence"].extend([
            "INTRO.TOPIC.FOCUS_TERMS_OBSERVED",
            "INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE",
        ])
    base["rule_evidence"] = [event(rule_id) for rule_id in base["rule_evidence"]]
    return base


def paragraph(index, **overrides):
    record = {
        "paragraph_index": index,
        "substantive": True,
        "counts": {"sentence_count": 2},
        "fragment_or_list_candidate": {"keyword_list_candidate": False},
        "observed_focus_terms": ["reading"],
        "topic_sentence_candidates": [],
        "clause_structure_candidates": [deepcopy(SPAN)],
        "supporting_detail_candidates": {"candidates": [deepcopy(SPAN), deepcopy(SPAN)]},
        "repetition_observations": {"repeated_surface_content_words": [], "repeated_sentence_openings": []},
    }
    record.update(overrides)
    return record


def body_analysis(case):
    paragraphs = [] if case == "empty" else [paragraph(1)]
    if case in {"list", "unlinked", "limited", "repeated"}:
        item = paragraph(2)
        if case == "list":
            item["fragment_or_list_candidate"]["keyword_list_candidate"] = True
            item["clause_structure_candidates"] = []
            item["supporting_detail_candidates"]["candidates"] = []
        elif case == "limited":
            item["supporting_detail_candidates"]["candidates"] = []
        elif case == "repeated":
            item["repetition_observations"]["repeated_sentence_openings"] = [{"opening": "readers learn"}]
        paragraphs.append(item)
        paragraphs.append(paragraph(3))
    pairs = [{"status": "NO_EXPLICIT_LEXICAL_LINK_OBSERVED", "paragraph_pair": [1, 2]}] if case == "unlinked" else []
    intro_status = "NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED" if case == "no_introduction" else "LEXICAL_COMPARISON_AVAILABLE"
    analysis = {
        "paragraphs": paragraphs,
        "cross_paragraph_continuity": {
            "status": "PAIRWISE_OBSERVATIONS" if pairs else "NOT_APPLICABLE_SINGLE_PARAGRAPH",
            "paragraph_pairs": pairs,
        },
        "introduction_to_body_continuity": {
            "status": intro_status,
            "direct_lexical_continuity": [deepcopy(SPAN)] if intro_status == "LEXICAL_COMPARISON_AVAILABLE" else [],
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
    if intro_status == "LEXICAL_COMPARISON_AVAILABLE":
        ids.append("BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON")
    analysis["rule_evidence"] = [event(rule_id) for rule_id in ids]
    return analysis


def conclusion_analysis(case):
    analysis = {
        "text_presence": {"alphabetic_word_count": 3, "keyword_list_candidate": False},
        "clause_candidates": [deepcopy(SPAN)],
        "lexical_topic_evidence": {"observed_focus_terms": []},
        "introduction_to_conclusion_continuity": {"status": "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED"},
        "body_to_conclusion_continuity": {"status": "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED"},
        "synthesis_structure_candidates": {"status": "SYNTHESIS_STRUCTURE_CANDIDATE", "candidates": []},
        "closure_candidates": {"status": "NO_CLOSURE_CANDIDATE_OBSERVED", "candidates": []},
        "new_material_observations": {"status": "NEW_MATERIAL_OBSERVATIONS_COMPLETE", "unobserved_concept_candidates": [], "phrase_combinations_of_observed_concepts": []},
        "rule_evidence": ["CONCLUSION.GOAL.REVIEW_TOPIC_AND_PRIOR_IDEAS", "CONCLUSION.LIMITATION.NO_SEMANTIC_VALIDATION"],
    }
    if case == "empty":
        analysis["text_presence"]["alphabetic_word_count"] = 0
        analysis["rule_evidence"].append("CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC")
    elif case == "list":
        analysis["text_presence"]["keyword_list_candidate"] = True
        analysis["rule_evidence"].append("CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE")
    elif case == "no_clause":
        analysis["clause_candidates"] = []
        analysis["rule_evidence"].append("CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE")
    elif case == "new_words":
        analysis["new_material_observations"]["unobserved_concept_candidates"] = [{"normalized_form": "runners"}]
        analysis["rule_evidence"].append("CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS")
    elif case == "synthesis":
        analysis["synthesis_structure_candidates"]["candidates"] = [deepcopy(SPAN)]
        analysis["rule_evidence"].append("CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE")
    elif case == "closure":
        analysis["closure_candidates"]["status"] = "CLOSURE_STRUCTURE_CANDIDATE"
        analysis["closure_candidates"]["candidates"] = [deepcopy(SPAN)]
        analysis["rule_evidence"].append("CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE")
    elif case == "focus_only":
        analysis["lexical_topic_evidence"]["observed_focus_terms"] = ["reading"]
        analysis["rule_evidence"].append("CONCLUSION.TOPIC.FOCUS_MATCHES")
    elif case == "general":
        analysis["closure_candidates"]["candidates"] = []
        analysis["rule_evidence"].append("CONCLUSION.CLOSURE.NO_CANDIDATE")
    analysis["rule_evidence"] = [event(rule_id) for rule_id in analysis["rule_evidence"]]
    return analysis


CASES = {
    "INTRODUCTION": ([("empty", "intro_neutral_empty"), ("whitespace", "intro_neutral_whitespace"),
                      ("punctuation", "intro_neutral_punctuation"), ("list", "intro_organization_topic_intro"),
                      ("incomplete", "intro_sentence_fluency_complete_sentence"),
                      ("broad_only", "intro_word_choice_specific_subject"), ("no_focus", "intro_ideas_topic_match"),
                      ("main_point", "intro_ideas_develop_main_point"), ("point_reason", "intro_ideas_review_details"),
                      ("one_sentence_specific", "intro_ideas_main_point")], intro_analysis, "generate"),
    "BODY": ([("empty", "body_neutral_empty"), ("list", "body_organization_paragraph_shape"),
              ("unlinked", "body_organization_paragraph_link"), ("limited", "body_ideas_develop_point"),
              ("repeated", "body_sentence_fluency_sentence_beginnings"), ("plain", "body_neutral_observable"),
              ("no_introduction", "body_neutral_observable")], body_analysis, "generate_body"),
    "CONCLUSION": ([("empty", "conclusion_neutral_empty"), ("list", "conclusion_organization_bring_together"),
                    ("no_clause", "conclusion_neutral_review"), ("new_words", "conclusion_ideas_new_words"),
                    ("synthesis", "conclusion_ideas_bring_together"), ("closure", "conclusion_organization_clear_ending"),
                    ("focus_only", "conclusion_ideas_return_to_point"), ("general", "conclusion_neutral_general")],
                   conclusion_analysis, "generate_conclusion"),
}

PRIMARY_EXPECTATIONS = {
    "intro_neutral_empty": "Your Introduction is empty.",
    "intro_neutral_whitespace": "Your Introduction has only spaces.",
    "intro_neutral_punctuation": "Your Introduction has punctuation but no words.",
    "intro_organization_topic_intro": "reads as a word list",
    "intro_sentence_fluency_complete_sentence": "may leave the thought unfinished",
    "intro_word_choice_specific_subject": "Name the specific subject",
    "intro_ideas_topic_match": "The checks did not find your assignment words in the opening.",
    "intro_ideas_main_point": "main-statement pattern",
    "intro_ideas_develop_main_point": "recorded a possible main-point sentence",
    "intro_ideas_point_and_reason": "recorded a possible main statement and a 'because' part",
    "intro_ideas_review_details": "recorded a possible main statement and additional sentence parts",
    "body_neutral_empty": "The Body has no words yet.",
    "body_organization_paragraph_shape": "Paragraph 2 contains assignment words as a list",
    "body_organization_paragraph_link": "between Paragraphs 1 and 2",
    "body_ideas_develop_point": "Paragraph 2",
    "body_sentence_fluency_sentence_beginnings": "begins with 'readers learn'",
    "body_neutral_observable": "The available checks did not identify a specific structural concern in this Body section.",
    "conclusion_neutral_empty": "Your Conclusion is empty.",
    "conclusion_organization_bring_together": "reads as a word list",
    "conclusion_neutral_review": "could not spot a complete closing sentence",
    "conclusion_ideas_new_words": "do not appear in the earlier sections",
    "conclusion_ideas_bring_together": "combines ideas from more than one earlier section",
    "conclusion_organization_clear_ending": "Your ending has a final sentence or closing phrase.",
    "conclusion_ideas_return_to_point": "Check whether your ending returns to your main point.",
    "conclusion_neutral_general": "There is no one required ending phrase.",
}


def _messages(value):
    return value if isinstance(value, list) else [value]


def _trailing_text(text):
    return re.sub(r"\s+", " ", text).strip()


# --- A/B/C: backend branch matrix, recorded traits, and message hygiene --------

@pytest.mark.parametrize("stage", ["INTRODUCTION", "BODY", "CONCLUSION"])
def test_branch_matrix_and_traits(stage):
    cases, builder, method_name = CASES[stage]
    service = FeedbackService()
    for case, expected_branch in cases:
        result = getattr(service, method_name)(deepcopy(builder(case)), include_trace=True)
        assert result["Current Goal"], f"{stage}/{case}: goal missing"
        assert isinstance(result["What's Working"], list) and isinstance(result["Needs Attention"], list)
        assert result["interpretation_limit"]
        trace = result["_Research Decision Trace"]["fields"]
        primary = trace["Primary Feedback"]
        assert primary["selection_branch"] == expected_branch
        assert primary["selected_message"] == result["Primary Feedback"]
        assert PRIMARY_EXPECTATIONS[expected_branch] in result["Primary Feedback"], (
            f"{stage}/{case}: unexpected primary wording"
        )
        trait, skill = BRANCH_TRAIT_SKILL.get(expected_branch, (None, None))
        assert (primary["trait"], primary["skill"]) == (trait, skill)
        assert (trace["Current Goal"]["trait"], trace["Current Goal"]["skill"]) == (None, None)
        assert (trace["What's Working"]["trait"], trace["What's Working"]["skill"]) == (None, None)
        assert (trace["Needs Attention"]["trait"], trace["Needs Attention"]["skill"]) == (None, None)
        next_field = trace["Next Step"]
        assert next_field["selected_message"] == result["Next Step"]
        expected_next_trait, expected_next_skill = BRANCH_TRAIT_SKILL.get(next_field["selection_branch"], (None, None))
        assert (next_field["trait"], next_field["skill"]) == (expected_next_trait, expected_next_skill)
        for field in FIELDS:
            for message in _messages(result[field]):
                lowered = _trailing_text(message).lower()
                assert not any(word in lowered for word in FORBIDDEN_MESSAGE_WORDS), (
                    f"{stage}/{case}/{field}: banned wording in {message!r}"
                )
                assert len(re.findall(r"[.!?]", message)) <= 2, (
                    f"{stage}/{case}/{field}: message too long: {message!r}"
                )


def test_next_step_only_branches_expose_recorded_trait():
    trace = FeedbackService().generate(intro_analysis("main_point"), include_trace=True)["_Research Decision Trace"]["fields"]
    assert trace["Next Step"]["selection_branch"] == "intro_ideas_develop_main_point"
    assert (trace["Next Step"]["trait"], trace["Next Step"]["skill"]) == ("Ideas", "Develop Your Main Point")
    body = FeedbackService().generate_body(body_analysis("no_introduction"), include_trace=True)
    fields = body["_Research Decision Trace"]["fields"]
    assert fields["Next Step"]["selection_branch"] == "body_neutral_observable"
    assert (fields["Next Step"]["trait"], fields["Next Step"]["skill"]) == (None, None)
    assert body["Next Step"] == "" and body["_Research Decision Trace"]["instructional_feedback"]["items"] == []
    conclusion = FeedbackService().generate_conclusion(deepcopy(conclusion_analysis("closure")), include_trace=True)
    fields = conclusion["_Research Decision Trace"]["fields"]
    assert fields["Next Step"]["selection_branch"] == "conclusion_organization_clear_ending"
    assert (fields["Next Step"]["trait"], fields["Next Step"]["skill"]) == ("Organization", "Clear Ending")


def test_provenance_and_emitted_rule_ids():
    result = FeedbackService().generate(intro_analysis("main_point"))
    field_ids = {item["feedback_field"]: item["rule_id"] for item in result["Feedback Provenance"] if item["rule_id"].startswith("INTRO.DEVELOPMENT")}
    assert field_ids.get("Primary Feedback") == "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE"
    for item in result["Feedback Provenance"]:
        goal = ".GOAL." in item["rule_id"]
        assert item["actual_evidence"] == ([] if goal else [deepcopy(SPAN)])


# --- D: prepared catalog v3 ---------------------------------------------------

PRIMARY_BRANCHES = {
    "INTRODUCTION": ["intro_neutral_empty", "intro_neutral_whitespace", "intro_neutral_punctuation",
                     "intro_organization_topic_intro", "intro_sentence_fluency_complete_sentence",
                     "intro_word_choice_specific_subject", "intro_ideas_topic_match", "intro_ideas_main_point",
                     "intro_ideas_point_and_reason", "intro_ideas_develop_main_point", "intro_ideas_review_details",
                     "intro_ideas_review_topic_connection", "intro_ideas_state_position"],
    "BODY": ["body_neutral_empty", "body_organization_paragraph_shape", "body_organization_paragraph_link",
             "body_ideas_develop_point", "body_sentence_fluency_sentence_beginnings", "body_neutral_observable"],
    "CONCLUSION": ["conclusion_neutral_empty", "conclusion_organization_bring_together", "conclusion_neutral_review",
                   "conclusion_ideas_new_words", "conclusion_ideas_bring_together", "conclusion_organization_clear_ending",
                   "conclusion_ideas_return_to_point", "conclusion_neutral_general"],
}
BOUND_BRANCHES = {
    "INTRODUCTION": ["intro_organization_topic_intro", "intro_sentence_fluency_complete_sentence",
                     "intro_word_choice_specific_subject", "intro_ideas_topic_match", "intro_ideas_main_point",
                     "intro_ideas_point_and_reason", "intro_ideas_develop_main_point", "intro_ideas_review_details",
                     "intro_ideas_review_topic_connection", "intro_ideas_state_position"],
    "BODY": ["body_organization_paragraph_shape", "body_organization_paragraph_link", "body_ideas_develop_point",
             "body_sentence_fluency_sentence_beginnings"],
    "CONCLUSION": ["conclusion_organization_bring_together", "conclusion_ideas_new_words", "conclusion_ideas_bring_together",
                   "conclusion_organization_clear_ending", "conclusion_ideas_return_to_point"],
}


def test_catalog_v3_structure_and_bindings():
    catalog = load_feedback_help()
    assert catalog["version"] == 6 and catalog["availability"] == "AVAILABLE"
    lessons = {lesson["lesson_id"]: lesson for lesson in catalog["lessons"]}
    assert len(lessons) == len(catalog["lessons"]) == 19
    for stage, branches in BOUND_BRANCHES.items():
        bound = [item for item in catalog["bindings"] if item["stage_id"] == stage]
        assert {item["selection_branch"] for item in bound} == set(branches)
        for item in bound:
            assert set(BRANCH_TRAIT_SKILL[item["selection_branch"]]) == {item["dimension"], item["skill"]}
            assert item["dimension"] in TRAIT_DIMENSIONS
            assert item["feedback_field"] == "Primary Feedback"
            assert item["mapping_basis"] and item["noticed"]
            lesson = lessons[item["lesson_id"]]
            assert set(lesson["tutor"]) >= {"noticed", "why", "task", "limitation"}
            assert "try" not in lesson["tutor"] and "check" not in lesson["tutor"]
            for key in ("goal", "question", "explanation", "next_step", "limitation"):
                assert lesson["inline_guidance"][key].strip()
    for stage, branches in PRIMARY_BRANCHES.items():
        bound = {item["selection_branch"] for item in catalog["bindings"] if item["stage_id"] == stage}
        assert not (set(branches) - bound - {b for b in branches if b not in BOUND_BRANCHES[stage]})
        for branch in branches:
            if branch not in bound:
                assert BRANCH_TRAIT_SKILL.get(branch) is None  # neutrals intentionally carry no prepared lesson
    patterns = [(item["stage_id"], item["rule_id_pattern"]) for item in catalog["secondary_bindings"]]
    assert len(patterns) == len(set(patterns)) == 10
    for item in catalog["secondary_bindings"]:
        assert item["dimension"] in TRAIT_DIMENSIONS and item["lesson_id"] in lessons
        re.compile(item["rule_id_pattern"])


def test_catalog_loader_rejects_version_two_and_invalid_dimension(tmp_path, monkeypatch):
    from services import tutoring_lessons as catalog_module

    catalog = json.loads(catalog_module._FEEDBACK_HELP_PATH.read_text(encoding="utf-8"))
    stale = dict(catalog, version=2)
    invalid = deepcopy(catalog)
    invalid["bindings"] = [{**catalog["bindings"][0], "dimension": "Clarity"}]
    for payload in (stale, invalid):
        replacement = tmp_path / "feedback_help.json"
        replacement.write_text(json.dumps(payload), encoding="utf-8")
        monkeypatch.setattr(catalog_module, "_FEEDBACK_HELP_PATH", replacement)
        catalog_module.load_feedback_help.cache_clear()
        assert catalog_module.load_feedback_help() == {
            "version": 6, "availability": "UNAVAILABLE", "lessons": [], "bindings": [],
        }
        monkeypatch.undo()
    catalog_module.load_feedback_help.cache_clear()
    assert load_feedback_help()["availability"] == "AVAILABLE"


# --- E: Process 07 purpose table coverage -------------------------------------

def test_feedback_flow_purpose_table_covers_all_recorded_branches():
    start = APP_JS.index("const FEEDBACK_FLOW_BRANCH_PURPOSES = {")
    end = APP_JS.index("};", start)
    keys = set(re.findall(r"^  ([a-z0-9_]+): ", APP_JS[start:end], flags=re.MULTILINE))
    expected = set(BRANCH_TRAIT_SKILL) | {
        "stage_constant", "independent_evidence_checks", "independent_attention_checks",
        "paragraph_evidence_loop", "paragraph_and_cross_stage_checks",
        "intro_neutral_write_first", "intro_ideas_develop_main_point", "intro_ideas_review_details",
        "body_neutral_no_intro_context", "body_neutral_general",
        "conclusion_neutral_general", "conclusion_neutral_review",
    }
    assert set(BRANCH_TRAIT_SKILL) <= keys
    assert expected <= keys
    legacy_markers = ["empty_input", "whitespace_only", "punctuation_only", "broad_only_focus_match",
                      "central_clause_without_multiple_clause_candidate", "general_observable_body_evidence",
                      "no_clause_candidate", "closure_candidate\"", "first_list_like_paragraph"]
    for marker in legacy_markers:
        assert marker not in APP_JS[start:end]


# --- F/G: student presentation and panel wiring -------------------------------

def test_student_presentation_displayed_guidance_keys():
    start = APP_JS.index("displayed_guidance:")
    neutral_end = APP_JS.index("} : {", start)
    assert '"How to improve"' not in APP_JS[start:neutral_end]
    start = neutral_end
    end = APP_JS.index("},", start)
    keys = re.findall(r'"([^"]+)": primary\?', APP_JS[start:end])
    assert keys == ["What I noticed", "Look at your writing", "Why it matters", "How to improve"]
    assert "Check your revision" not in APP_JS and '"Try this"' not in APP_JS


def test_tutor_panel_sections_and_task_element():
    assert 'id="tutor-task"' in INDEX_HTML and 'id="tutor-try"' not in INDEX_HTML and 'id="tutor-check"' not in INDEX_HTML
    order = [INDEX_HTML.index(marker) for marker in (
        '<h3>What I noticed</h3>', '<h3>Look at your writing</h3>',
        '<h3>Why it matters</h3>', '<h3>How to improve</h3>')]
    assert order == sorted(order)
    assert 'tutorWhy.textContent = item.why;' in APP_JS and 'tutorTask.textContent = item.task_text;' in APP_JS


def test_trait_category_styles_and_labels():
    assert 'Clarity: "Clarity"' not in APP_JS and 'Coherence' not in APP_JS.split("FEEDBACK_FLOW")[0][:4000]
    for trait in sorted(TRAIT_DIMENSIONS):
        assert f'data-category="{trait}"' in STYLE_CSS
        assert f'{trait!r}: "{trait}"' in APP_JS or f'"{trait}": "{trait}"' in APP_JS
    for legacy in ('data-category="Clarity"', 'data-category="Coherence"', 'data-category="Structure"'):
        assert legacy not in STYLE_CSS and legacy not in APP_JS
