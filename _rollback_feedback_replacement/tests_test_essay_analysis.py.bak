"""Integration checks for the lightweight three-stage analysis coordinator."""

import json
from unittest.mock import Mock

import pytest

from services.essay_analysis_service import EssayAnalysisService
from services.nlp_service import NLPService
from services.topic_service import TopicService


TOPIC = "Effects of late-night social media use on classroom attention"
FOCUS = ["social media", "students", "sleep", "fatigue", "attention", "concentration", "classroom"]
INTRO = "Late-night social media use may affect students' classroom attention."
BODY = "Students use social media at night. This can reduce sleep and cause fatigue."
CONCLUSION = "Overall, students' sleep may affect their concentration during classroom lessons."


@pytest.fixture(scope="module")
def nlp_service() -> NLPService:
    return NLPService()


def test_complete_essay_is_stage_separated_serializable_and_offset_safe(
    nlp_service: NLPService,
) -> None:
    service = EssayAnalysisService(nlp_service)
    result = service.analyze(TOPIC, FOCUS, INTRO, BODY, CONCLUSION)
    encoded = json.dumps(result, ensure_ascii=False)
    assert json.loads(encoded)["stage_order"] == ["INTRODUCTION", "BODY", "CONCLUSION"]
    assert result["assignment_topic"] == TOPIC
    for stage_id, source in (
        ("INTRODUCTION", INTRO),
        ("BODY", BODY),
        ("CONCLUSION", CONCLUSION),
    ):
        stage = result["stages"][stage_id]
        assert stage["availability"] == "ANALYZED"
        assert stage["supplied_text"] == source
        assert stage["analysis"]["stage" if stage_id != "INTRODUCTION" else "stage"] == stage_id
        assert set(stage["feedback"]) >= {
            "Current Goal",
            "Primary Feedback",
            "What's Working",
            "Needs Attention",
            "Next Step",
            "Feedback Provenance",
        }

    intro_matches = result["stages"]["INTRODUCTION"]["analysis"]["lexical_topic_evidence"]["matches"]
    for match in intro_matches:
        assert INTRO[match["start"] : match["end"]] == match["observed_text"]

    body_paragraph = result["stages"]["BODY"]["analysis"]["paragraphs"][0]
    for match in body_paragraph["focus_term_evidence"]:
        assert BODY[match["start"] : match["end"]] == match["observed_text"]

    conclusion_matches = result["stages"]["CONCLUSION"]["analysis"]["lexical_topic_evidence"]["matches"]
    for match in conclusion_matches:
        assert match["source_section"] == "conclusion"
        assert CONCLUSION[match["start"] : match["end"]] == match["observed_text"]


def test_partial_essay_does_not_analyze_or_invent_absent_stages(
    nlp_service: NLPService,
) -> None:
    service = EssayAnalysisService(nlp_service)
    result = service.analyze(TOPIC, FOCUS, introduction_text=INTRO)
    assert result["stages"]["INTRODUCTION"]["availability"] == "ANALYZED"
    for stage_id in ("BODY", "CONCLUSION"):
        stage = result["stages"][stage_id]
        assert stage["availability"] == "NOT_SUPPLIED"
        assert stage["supplied_text"] is None
        assert stage["analysis"] is None
        assert stage["feedback"] is None


def test_no_stage_text_does_not_run_nlp(nlp_service: NLPService) -> None:
    parse = Mock(wraps=nlp_service.parse)
    nlp_service.parse = parse
    try:
        result = EssayAnalysisService(nlp_service).analyze("Reading habits among students")
        parse.assert_not_called()
        assert all(
            stage["availability"] == "NOT_SUPPLIED"
            for stage in result["stages"].values()
        )
    finally:
        nlp_service.parse = parse._mock_wraps


@pytest.mark.parametrize(
    ("provided", "expected"),
    [
        ({"introduction_text": INTRO}, {"INTRODUCTION": "ANALYZED", "BODY": "NOT_SUPPLIED", "CONCLUSION": "NOT_SUPPLIED"}),
        ({"introduction_text": INTRO, "body_text": BODY}, {"INTRODUCTION": "ANALYZED", "BODY": "ANALYZED", "CONCLUSION": "NOT_SUPPLIED"}),
        ({"conclusion_text": CONCLUSION}, {"INTRODUCTION": "NOT_SUPPLIED", "BODY": "NOT_SUPPLIED", "CONCLUSION": "ANALYZED"}),
        ({"introduction_text": ""}, {"INTRODUCTION": "SUPPLIED_EMPTY", "BODY": "NOT_SUPPLIED", "CONCLUSION": "NOT_SUPPLIED"}),
    ],
)
def test_coordinator_supports_partial_and_empty_stage_inputs(
    nlp_service: NLPService, provided: dict, expected: dict
) -> None:
    result = EssayAnalysisService(nlp_service).analyze(TOPIC, FOCUS, **provided)
    assert {stage: output["availability"] for stage, output in result["stages"].items()} == expected


def test_complete_coordinator_parses_each_supplied_section_once(
    nlp_service: NLPService,
) -> None:
    parse = Mock(wraps=nlp_service.parse)
    analyze_doc = Mock(wraps=nlp_service.analyze_doc)
    nlp_service.parse = parse
    nlp_service.analyze_doc = analyze_doc
    try:
        service = EssayAnalysisService(nlp_service)
        service.analyze(TOPIC, FOCUS, INTRO, BODY, CONCLUSION)
        assert parse.call_count == 3
        assert {call.args[0] for call in parse.call_args_list} == {INTRO, BODY, CONCLUSION}
        assert analyze_doc.call_count == 3
    finally:
        nlp_service.parse = parse._mock_wraps
        nlp_service.analyze_doc = analyze_doc._mock_wraps


def test_coordinator_feedback_preserves_stage_specific_provenance(
    nlp_service: NLPService,
) -> None:
    result = EssayAnalysisService(nlp_service).analyze(TOPIC, FOCUS, INTRO, BODY, CONCLUSION)
    for stage_id in result["stage_order"]:
        stage = result["stages"][stage_id]
        rules = {event["rule_id"]: event for event in stage["analysis"]["rule_evidence"]}
        for provenance in stage["feedback"]["Feedback Provenance"]:
            assert provenance["rule_id"] in rules
            event = rules[provenance["rule_id"]]
            assert provenance["actual_evidence"] == (
                event["actual_evidence"] if "actual_evidence" in event else event["evidence"]
            )


@pytest.mark.parametrize(
    "text",
    [
        "Punctuation! Students read.",
        "Readers café study, then students discuss it.",
        "Students study.\r\n\r\nThe conclusion returns to reading.",
    ],
)
def test_stage_offsets_remain_local_for_unicode_and_windows_newlines(
    nlp_service: NLPService, text: str
) -> None:
    result = EssayAnalysisService(nlp_service).analyze(
        "Reading habits", ["students", "reading"], conclusion_text=text
    )
    matches = result["stages"]["CONCLUSION"]["analysis"]["lexical_topic_evidence"]["matches"]
    for match in matches:
        assert match["source_section"] == "conclusion"
        assert text[match["start"] : match["end"]] == match["observed_text"]


def test_coordinator_is_deterministic_and_has_no_readiness_verdict(
    nlp_service: NLPService,
) -> None:
    service = EssayAnalysisService(nlp_service)
    first = service.analyze(TOPIC, FOCUS, INTRO, BODY, CONCLUSION)
    second = service.analyze(TOPIC, FOCUS, INTRO, BODY, CONCLUSION)
    assert first == second
    assert "essay_quality_score" not in first
    assert "readiness_decision" not in first
    assert first["stages"]["CONCLUSION"]["analysis"]["interpretation_limit"]


@pytest.mark.parametrize(
    ("topic", "focus", "intro", "body", "conclusion"),
    [
        (
            "Benefits and disadvantages of school uniforms",
            ["uniforms", "students", "costs", "identity"],
            "School uniforms may reduce clothing pressure.",
            "Rules may also limit self-expression.",
            "Overall, schools should weigh both effects.",
        ),
        (
            "Effects of environmental pollution on community health",
            ["pollution", "community", "health", "lungs"],
            "Air pollution can affect community health.",
            "Pollutants may irritate the lungs near busy roads.",
            "Reducing emissions may help protect residents.",
        ),
    ],
)
def test_coordinator_works_with_unrelated_assignment_topics(
    nlp_service: NLPService, topic: str, focus: list[str], intro: str, body: str, conclusion: str
) -> None:
    result = EssayAnalysisService(nlp_service).analyze(topic, focus, intro, body, conclusion)
    assert all(result["stages"][stage]["availability"] == "ANALYZED" for stage in result["stage_order"])
    assert result["stages"]["INTRODUCTION"]["analysis"]["assignment_topic"] == topic
    assert result["stages"]["BODY"]["analysis"]["assignment_topic"] == topic
    assert result["stages"]["CONCLUSION"]["analysis"]["assignment_topic"] == topic


def test_coordinator_rejects_malformed_public_inputs(nlp_service: NLPService) -> None:
    service = EssayAnalysisService(nlp_service)
    with pytest.raises(TypeError, match="assignment_topic must be a string"):
        service.analyze(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="focus_terms must be a list of strings"):
        service.analyze("Reading", "students")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="each supplied stage must be a string or None"):
        service.analyze("Reading", introduction_text=["not", "text"])  # type: ignore[arg-type]


def test_coordinator_does_not_import_semantic_experiment_models() -> None:
    import inspect
    import services.essay_analysis_service as coordinator

    source = inspect.getsource(coordinator)
    assert "sentence_transformers" not in source
    assert "encoder_experiment" not in source
