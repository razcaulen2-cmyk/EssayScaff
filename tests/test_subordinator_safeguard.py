"""Focused tests for the incomplete-subordinator false-positive safeguard.

Covers the controlled sentence set from the repair specification:
genuine incomplete subordinate clauses (Group A), complete sentences that
previously produced false positives (Group B), other legitimate structures
(Group C), and regression cases including the parser "ect" false positive
and all thirteen CLAUSE_SUBORDINATORS (Group D).

All tests use the real installed spaCy model; no annotations are mocked.
"""

import pytest

from services.introduction_rules import IntroductionRuleBase
from services.nlp_service import NLPService
from services.topic_service import TopicService

TOPIC = "Plastics"
FOCUS = ["plastic", "pollution", "rivers"]


@pytest.fixture(scope="module")
def rules() -> IntroductionRuleBase:
    return IntroductionRuleBase(TopicService(NLPService()))


def fired(result: dict) -> bool:
    return bool(result["observable_structure"]["incomplete_subordinator_candidates"])


def markers(result: dict) -> list[str]:
    return [
        item["text"]
        for item in result["observable_structure"]["incomplete_subordinator_candidates"]
    ]


# ---------------------------------------------------------------------
# Group A — genuine incomplete subordinate clauses (must still fire)
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "text,expected_marker",
    [
        ("Because plastic waste harms rivers.", "Because"),
        ("Although communities reduce single-use plastics.", "Although"),
        ("If communities reduce plastic waste.", "If"),
    ],
)
def test_group_a_simple_incomplete_fires(rules, text, expected_marker):
    result = rules.analyze(text, TOPIC, FOCUS)
    assert fired(result)
    assert markers(result) == [expected_marker]


def test_group_a_multiple_finite_verbs_do_not_establish_main_clause(rules):
    """A4: two finite-looking verbs but no independent main clause."""
    result = rules.analyze(
        "Because pollution increases and animals suffer.", TOPIC, FOCUS
    )
    assert fired(result)
    assert markers(result) == ["Because"]


# ---------------------------------------------------------------------
# Group B — complete sentences (false positives; must be suppressed)
# ---------------------------------------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        "Because plastic waste harms rivers, communities should reduce their use of it.",
        "Communities should reduce plastic waste because it harms rivers.",
        "Although plastic is convenient, communities should reduce its use.",
        "If communities reduce plastic waste, rivers will become cleaner.",
        "Because single-use plastics pollute rivers, people should use reusable containers.",
    ],
)
def test_group_b_complete_sentence_no_warning(rules, text):
    result = rules.analyze(text, TOPIC, FOCUS)
    assert not fired(result), f"false positive for: {text!r}"


def test_group_b1_restores_structural_evidence(rules):
    """The confirmed false-positive case regains its clause candidates."""
    result = rules.analyze(
        "Because plastic waste harms rivers, communities should reduce their use of it.",
        TOPIC,
        FOCUS,
    )
    dev = result["development_evidence"]
    assert dev["predicate_count"] == 2
    assert dev["status"] == "STRUCTURAL_ELABORATION_CANDIDATE"


# ---------------------------------------------------------------------
# Group C — other legitimate structures
# ---------------------------------------------------------------------

def test_group_c_coordination_no_warning(rules):
    result = rules.analyze(
        "Communities should reduce plastic waste, and schools should promote recycling.",
        TOPIC,
        FOCUS,
    )
    assert not fired(result)


def test_group_c_multiple_dependent_predicates_still_incomplete(rules):
    """C2: coordination inside the dependent clause is not an independent clause."""
    result = rules.analyze(
        "Although communities recycle and businesses reduce packaging.",
        TOPIC,
        FOCUS,
    )
    assert fired(result)
    assert markers(result) == ["Although"]


def test_group_c_embedded_relative_clause_no_warning(rules):
    result = rules.analyze(
        "People who understand the effects of plastic pollution often choose reusable materials.",
        TOPIC,
        FOCUS,
    )
    assert not fired(result)


def test_group_c_when_initial_complete_no_warning(rules):
    result = rules.analyze(
        "When people reduce plastic waste, rivers become cleaner.", TOPIC, FOCUS
    )
    assert not fired(result)


# ---------------------------------------------------------------------
# Group D — regression cases
# ---------------------------------------------------------------------

def test_group_d_ect_parser_false_positive_no_warning(rules):
    """The misspelled 'ect' case is a known parser artifact; the
    safeguard suppresses the subordinator warning because a separate
    advcl with subject is observed."""
    result = rules.analyze(
        "Ect plastic waste harms rivers, communities should reduce it.",
        TOPIC,
        FOCUS,
    )
    assert not fired(result)


def test_group_d_corrected_ect_spelling_no_warning(rules):
    result = rules.analyze(
        "Excess plastic waste harms rivers, communities should reduce it.",
        TOPIC,
        FOCUS,
    )
    assert not fired(result)


@pytest.mark.parametrize(
    "subordinator",
    [
        "Although", "As", "Because", "Before", "If", "Once", "Since",
        "Though", "Unless", "Until", "While", "Whereas",
    ],
)
def test_group_d_incomplete_with_each_subordinator(rules, subordinator):
    """Twelve of thirteen conjunctions fire for fragment inputs.

    'When' is excluded because spaCy attaches it as advmod rather than
    mark, which the rule does not currently treat as a subordinator
    trigger — a documented pre-existing limitation.
    """
    text = f"{subordinator} communities reduce plastic waste."
    result = rules.analyze(text, TOPIC, FOCUS)
    assert fired(result), f"expected warning for: {text!r}"
    assert markers(result) == [subordinator]


@pytest.mark.parametrize(
    "text",
    [
        "Although plastic is harmful, communities should reduce it.",
        "Because plastic is harmful, communities should reduce it.",
        "If plastic is harmful, communities should reduce it.",
    ],
)
def test_group_d_complete_with_initial_subordinate_no_warning(rules, text):
    result = rules.analyze(text, TOPIC, FOCUS)
    assert not fired(result)


def test_group_d_unicode_prefix_before_conjunction(rules):
    result = rules.analyze(
        "\U0001F30D Because plastic waste harms rivers, communities should reduce it.",
        TOPIC,
        FOCUS,
    )
    assert not fired(result)


def test_group_d_multiple_conjunctions_in_sentence(rules):
    result = rules.analyze(
        "Because plastic waste harms rivers and air pollution increases, communities should act.",
        TOPIC,
        FOCUS,
    )
    assert not fired(result)


def test_group_d_conjunction_in_non_initial_position(rules):
    result = rules.analyze(
        "Communities should reduce plastic because rivers are polluted, although costs are high.",
        TOPIC,
        FOCUS,
    )
    assert not fired(result)


def test_group_d_complete_clause_without_subordinator(rules):
    result = rules.analyze("Communities should reduce plastic waste.", TOPIC, FOCUS)
    assert not fired(result)


# ---------------------------------------------------------------------
# Safeguard mechanism — unit-level evidence checks
# ---------------------------------------------------------------------

def test_b1_marker_attached_to_root_with_separate_advcl():
    """Confirm the exact parse pattern the safeguard keys on."""
    nlp = NLPService()
    doc = nlp.nlp("Because plastic waste harms rivers, communities should reduce their use of it.")
    because = next(t for t in doc if t.text == "Because")
    harms = next(t for t in doc if t.text == "harms")
    reduce = next(t for t in doc if t.text == "reduce")
    assert because.dep_ == "mark"
    assert because.head.text == "reduce"
    assert reduce.dep_ == "ROOT"
    assert harms.dep_ == "advcl"
    assert harms.head.text == "reduce"
    assert any(t.dep_ == "nsubj" and t.head.text == "harms" for t in doc)


def test_a1_marker_attached_to_root_without_separate_advcl():
    """Genuine fragment: marker head is ROOT, no separate advcl."""
    nlp = NLPService()
    doc = nlp.nlp("Because plastic waste harms rivers.")
    because = next(t for t in doc if t.text == "Because")
    harms = next(t for t in doc if t.text == "harms")
    assert because.dep_ == "mark"
    assert because.head.text == "harms"
    assert harms.dep_ == "ROOT"
    assert not any(t.dep_ == "advcl" for t in doc)


def test_rule_event_absent_when_suppressed(rules):
    result = rules.analyze(
        "Because plastic waste harms rivers, communities should reduce their use of it.",
        TOPIC,
        FOCUS,
    )
    events = [
        e
        for e in result["rule_evidence"]
        if e["rule_id"] == "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"
    ]
    assert events == []


def test_rule_event_present_when_fired(rules):
    result = rules.analyze("Because plastic waste harms rivers.", TOPIC, FOCUS)
    events = [
        e
        for e in result["rule_evidence"]
        if e["rule_id"] == "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"
    ]
    assert len(events) == 1
    assert events[0]["triggered"] is True
