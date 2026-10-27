"""Before-only ADJ/advcl safeguard: real model, API, and conservative boundaries."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from app import create_app
from services.essay_analysis_service import EssayAnalysisService
from services.feedback_service import FeedbackService
from services.introduction_rules import IntroductionRuleBase
from services.nlp_service import NLPService
from services.topic_service import TopicService
from tests.auth_helpers import register_student


SAMPLES = json.loads(Path(__file__).with_name("before_subordinator_cases.json").read_text(encoding="utf-8"))
RULE = "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"
EXPECTED_MARKERS = {"A": [], "B": ["Although"], "C": ["Although"], "D": [],
                    "E": [], "F": ["Before"], "G": [], "H": ["Although"]}


@pytest.fixture(scope="module")
def nlp():
    return NLPService()


@pytest.fixture(scope="module")
def real_results(nlp):
    rules = IntroductionRuleBase(TopicService(nlp))
    return {name: rules.analyze(text, SAMPLES["assignment_topic"], SAMPLES["focus_terms"])
            for name, text in SAMPLES["cases"].items()}


@pytest.mark.parametrize("case", list(EXPECTED_MARKERS))
def test_cases_a_to_h_real_nlp_evidence_and_feedback(real_results, nlp, case):
    text = SAMPLES["cases"][case]
    result = real_results[case]
    # This is a fresh, unmodified model result, not a mocked dependency tree.
    assert result["linguistic_observations"] == nlp.analyze(text)
    evidence = result["observable_structure"]["incomplete_subordinator_candidates"]
    assert [item["text"] for item in evidence] == EXPECTED_MARKERS[case]
    events = [event for event in result["rule_evidence"] if event["rule_id"] == RULE]
    assert len(events) == int(bool(evidence))
    feedback = FeedbackService().generate(result, include_trace=True)
    decision = feedback["_Research Decision Trace"]["fields"]["Primary Feedback"]
    assert (decision["selection_branch"] == "intro_sentence_fluency_complete_sentence") == bool(evidence)
    if evidence:
        assert set(events[0]) == {"rule_id", "triggering_condition", "triggered", "evidence", "evidence_type", "limitation"}
        assert events[0]["evidence"] == evidence and events[0]["triggered"] is True
        assert RULE in decision["rule_ids"]
        assert "parser error" in events[0]["limitation"]
        for item in evidence:
            assert text[item["start"]:item["end"]] == item["text"]
            sentence = result["linguistic_observations"]["sentences"][item["sentence_index"]]
            assert sentence["start"] <= item["start"] < item["end"] <= sentence["end"]
    else:
        assert RULE not in decision["rule_ids"]
        assert all(item["rule_id"] != RULE for item in feedback["Feedback Provenance"])
    assert result["uncertainty"] and result["prohibited_conclusions"]


@pytest.mark.parametrize("text", SAMPLES["complete_variations"])
def test_other_main_verbs_subjects_positions_and_unicode(nlp, text):
    result = IntroductionRuleBase(TopicService(nlp)).analyze(text, SAMPLES["assignment_topic"], SAMPLES["focus_terms"])
    assert result["observable_structure"]["incomplete_subordinator_candidates"] == []
    assert all(event["rule_id"] != RULE for event in result["rule_evidence"])


def test_confirmed_real_parse_annotations_remain_adjectival(real_results):
    result = real_results["A"]
    tokens = {token["text"]: token for token in result["linguistic_observations"]["tokens"]}
    assert (tokens["before"]["pos"], tokens["before"]["dependency"], tokens["before"]["head"]) == ("SCONJ", "mark", "open")
    assert (tokens["open"]["pos"], tokens["open"]["tag"], tokens["open"]["dependency"], tokens["open"]["head"]) == ("ADJ", "JJ", "advcl", "arrange")
    assert (tokens["doors"]["dependency"], tokens["doors"]["head"]) == ("nsubj", "open")
    assert tokens["arrange"]["dependency"] == "ROOT"


def test_authenticated_api_combined_introduction_provenance_and_trace(tmp_path):
    app = create_app(EssayAnalysisService(), secret_key="before-safeguard-api")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "isolated.sqlite3"))
    client = app.test_client()
    assert register_student(client, "before_safeguard_student").status_code == 302
    text = SAMPLES["cases"]["H"]
    response = client.post("/api/analyze-stage", json={
        "stage_id": "INTRODUCTION", "assignment_topic": SAMPLES["assignment_topic"],
        "focus_terms": SAMPLES["focus_terms"], "introduction_text": text, "include_transparency_trace": True,
    })
    assert response.status_code == 200
    result = response.get_json()
    event = next(event for event in result["analysis"]["rule_evidence"] if event["rule_id"] == RULE)
    assert [item["text"] for item in event["evidence"]] == ["Although"]
    item = event["evidence"][0]
    assert item["start"] == 229 and item["end"] == 237 and item["sentence_index"] == 3
    assert text[item["start"]:item["end"]] == "Although"
    trace = result["research_trace"]["stages"]["INTRODUCTION"]
    decision = trace["feedback_decisions"]["fields"]["Primary Feedback"]
    assert decision["selection_branch"] == "intro_sentence_fluency_complete_sentence"
    assert decision["selected_message"] == result["feedback"]["Primary Feedback"]
    assert "Although" in decision["selected_message"] and "before" not in decision["selected_message"]
    assert {"feedback_field": "Primary Feedback", "rule_id": RULE} in result["feedback"]["Feedback Provenance"]
    evaluated = next(row for row in result["analysis"]["rule_evaluation_trace"] if row["rule_id"] == RULE)
    assert evaluated["status"] == "TRIGGERED"
    assert "does not" in result["interpretation_limit"] or "do not" in result["interpretation_limit"]


@pytest.fixture(scope="module")
def parsed_sentence(nlp):
    return nlp.analyze(SAMPLES["cases"]["A"])["sentences"][0]


@pytest.mark.parametrize("damage", [
    "missing_subordinate_subject", "missing_main_subject", "main_not_finite", "main_not_root",
    "subordinate_not_advcl", "subordinate_not_adj", "subordinate_not_jj", "subordinate_is_root",
    "foreign_main_head", "foreign_marker_head", "missing_head_record", "subject_outside_sentence",
    "marker_outside_sentence", "wrong_subordinate_text", "contradictory_link", "duplicate_link",
    "main_is_subordinated", "wrong_sentence_bounds",
])
def test_insufficient_or_contradictory_structures_do_not_suppress(parsed_sentence, damage):
    # Start with the actual model record; mutate only hard-to-reproduce graph
    # failures to check that the new exception stays conservative.
    sentence = deepcopy(parsed_sentence)
    marker = next(token for token in sentence["tokens"] if token["text"] == "before")
    subordinate = next(token for token in sentence["tokens"] if token["text"] == "open")
    main = next(token for token in sentence["tokens"] if token["text"] == "arrange")
    sub_subject = next(token for token in sentence["tokens"] if token["text"] == "doors")
    links = {link["start"]: link for link in sentence["dependencies"]}
    if damage == "missing_subordinate_subject":
        sentence["dependencies"].remove(links[sub_subject["start"]])
    elif damage == "missing_main_subject":
        sentence["dependencies"] = [link for link in sentence["dependencies"] if link["text"] != "workers"]
    elif damage == "main_not_finite": main["tag"] = "VBG"
    elif damage == "main_not_root": main["dependency"] = links[main["start"]]["dependency"] = "conj"
    elif damage == "subordinate_not_advcl": subordinate["dependency"] = links[subordinate["start"]]["dependency"] = "amod"
    elif damage == "subordinate_not_adj": subordinate["pos"] = "NOUN"
    elif damage == "subordinate_not_jj": subordinate["tag"] = "JJR"
    elif damage == "subordinate_is_root": subordinate["dependency"] = links[subordinate["start"]]["dependency"] = "ROOT"
    elif damage == "foreign_main_head": links[subordinate["start"]]["head_start"] = sentence["end"] + 1
    elif damage == "foreign_marker_head": links[marker["start"]]["head_start"] = sentence["end"] + 1
    elif damage == "missing_head_record": sentence["tokens"].remove(subordinate)
    elif damage == "subject_outside_sentence": sub_subject["end"] = links[sub_subject["start"]]["end"] = sentence["end"] + 1
    elif damage == "marker_outside_sentence": sentence["start"] = marker["end"]
    elif damage == "wrong_subordinate_text": subordinate["text"] = links[subordinate["start"]]["text"] = "other"
    elif damage == "contradictory_link": links[subordinate["start"]]["dependency"] = "amod"
    elif damage == "duplicate_link": sentence["dependencies"].append(deepcopy(links[subordinate["start"]]))
    elif damage == "main_is_subordinated":
        sentence["tokens"][0].update(dependency="mark", head=main["text"])
        sentence["dependencies"][0].update(dependency="mark", head=main["text"], head_start=main["start"])
    elif damage == "wrong_sentence_bounds": sentence["end"] += 1
    snapshot = deepcopy(sentence)
    assert not IntroductionRuleBase._before_adjective_clause_supported(sentence, marker)
    assert sentence == snapshot, "the safeguard never repairs or rewrites annotations"
    assert any(item["text"] == "before" for item in IntroductionRuleBase._incomplete_subordinator_evidence([sentence]))


@pytest.mark.parametrize("replacement", ["Though", "Because", "Although", "Unless"])
def test_structural_exception_is_before_only(parsed_sentence, replacement):
    # Replacements adjust the original offsets consistently. These controlled
    # records prove that the exception is not conjunction-wide.
    sentence = deepcopy(parsed_sentence)
    marker = next(token for token in sentence["tokens"] if token["text"] == "before")
    delta = len(replacement) - len(marker["text"])
    start, old_end = marker["start"], marker["end"]
    sentence["text"] = sentence["text"][:start] + replacement + sentence["text"][old_end:]
    sentence["end"] += delta
    for record in sentence["tokens"] + sentence["dependencies"]:
        if record["start"] == start:
            record["text"] = replacement
            record["end"] += delta
        else:
            if record["start"] >= old_end: record["start"] += delta
            if record["end"] >= old_end: record["end"] += delta
        if "head_start" in record and record["head_start"] >= old_end: record["head_start"] += delta
    assert not IntroductionRuleBase._before_adjective_clause_supported(sentence, marker)
    assert [item["text"] for item in IntroductionRuleBase._incomplete_subordinator_evidence([sentence])] == [replacement]
