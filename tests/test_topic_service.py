"""Tests for lexical evidence; examples are tests, not a validation dataset."""

from unittest.mock import Mock

import pytest

from services.nlp_service import NLPService
from services.topic_service import TopicService


@pytest.fixture(scope="module")
def nlp_service() -> NLPService:
    return NLPService()


@pytest.fixture(scope="module")
def topic_service(nlp_service: NLPService) -> TopicService:
    return TopicService(nlp_service)


def observations(result: dict, term: str) -> dict:
    return next(
        focus
        for focus in result["confirmed_lexical_observations"]
        if focus["term"].casefold() == term.casefold()
    )


def test_direct_multiword_focus_match(topic_service: TopicService) -> None:
    text = "Social media affects students."
    result = topic_service.analyze(text, "Any topic", ["social media"])
    match = observations(result, "social media")["direct_matches"][0]
    assert match["observed_text"] == "Social media"
    assert match["match_method"] == "direct"
    assert text[match["start"] : match["end"]] == "Social media"


def test_normalized_match_uses_lemma_not_substring(topic_service: TopicService) -> None:
    result = topic_service.analyze(
        "The students were studying.", "Study habits", ["student", "study"]
    )
    student_match = observations(result, "student")["normalized_matches"][0]
    study_match = observations(result, "study")["normalized_matches"][0]
    assert student_match["observed_text"] == "students"
    assert student_match["normalized_form"] == "student"
    assert study_match["observed_text"] == "studying"
    assert study_match["normalized_form"] == "study"


def test_multiword_phrase_does_not_match_separated_components(topic_service: TopicService) -> None:
    result = topic_service.analyze(
        "Students discuss school rules and uniforms.",
        "Uniform policy",
        ["school uniforms"],
    )
    assert not observations(result, "school uniforms")["observed"]
    sentence_break = topic_service.analyze(
        "Social. Media matters.", "Online media", ["social media"]
    )
    assert not observations(sentence_break, "social media")["observed"]


def test_multiword_phrase_cannot_bridge_a_paragraph_boundary(topic_service: TopicService) -> None:
    samples = ["School\n\nuniforms should be required.", "School\r\n \r\nuniforms should be required."]
    for text in samples:
        result = topic_service.analyze(text, "School uniform policies", ["school uniforms"])
        assert not observations(result, "school uniforms")["observed"]

    single_line_break = topic_service.analyze(
        "School\nuniforms should be required.", "School uniform policies", ["school uniforms"]
    )
    assert observations(single_line_break, "school uniforms")["observed"]


def test_hyphenated_focus_phrase_preserves_evidence_span(topic_service: TopicService) -> None:
    text = "Late-night screen use affects sleep."
    result = topic_service.analyze(text, "Sleep", ["late night"])
    match = observations(result, "late night")["direct_matches"][0]
    assert match["observed_text"] == "Late-night"
    assert text[match["start"] : match["end"]] == "Late-night"


def test_duplicate_focus_terms_deduplicate_by_lemma(topic_service: TopicService) -> None:
    result = topic_service.analyze(
        "Students study.", "Reading", ["student", "students", "student"]
    )
    assert result["focus_coverage"]["total_unique_focus_terms"] == 1
    assert result["focus_coverage"]["observed_focus_terms"] == ["student"]


def test_repeated_matches_count_occurrences_but_one_focus(topic_service: TopicService) -> None:
    text = "Students read, and students discuss reading."
    result = topic_service.analyze(text, "Student reading", ["students"])
    match = observations(result, "students")
    assert match["occurrence_count"] == 2
    assert result["focus_coverage"]["observed_unique_focus_terms"] == 1
    assert all(
        text[item["start"] : item["end"]] == item["observed_text"]
        for item in match["direct_matches"]
    )


def test_student_concepts_group_repeat_mentions_without_duplicate_spans(
    topic_service: TopicService,
) -> None:
    result = topic_service.analyze(
        "Students read. The students write.", "Reading", ["students"], include_wordnet=False
    )
    student_concept = next(
        concept for concept in result["student_concepts"]
        if concept["normalized_form"] == "student"
    )
    assert student_concept["occurrence_count"] == 2
    assert len({(item["start"], item["end"]) for item in student_concept["occurrences"]}) == 2


def test_unobserved_focus_terms_are_reported(topic_service: TopicService) -> None:
    result = topic_service.analyze("Students study.", "Reading", ["pollution"])
    assert result["focus_coverage"]["unobserved_focus_terms"] == ["pollution"]
    assert result["focus_coverage"]["observed_focus_terms"] == []


def test_empty_student_text_is_safe(topic_service: TopicService) -> None:
    result = topic_service.analyze("", "Reading habits", ["reading", "students"])
    assert result["student_concepts"] == []
    assert result["focus_coverage"]["unobserved_focus_terms"] == ["reading", "students"]


def test_no_focus_terms_derives_candidates_from_topic(topic_service: TopicService) -> None:
    result = topic_service.analyze("Students read books.", "Reading habits among students", [])
    assert result["teacher_context"]["focus_source"] == "topic_derived_candidates"
    assert result["teacher_context"]["automatically_derived_candidates"]


def test_teacher_focus_list_is_authoritative(topic_service: TopicService) -> None:
    result = topic_service.analyze(
        "Students discuss school uniforms.",
        "Benefits and disadvantages of school uniforms",
        ["uniforms"],
    )
    assert [term["term"] for term in result["teacher_context"]["focus_terms"]] == ["uniforms"]
    assert result["teacher_context"]["automatically_derived_candidates"] == []


@pytest.mark.parametrize(
    ("topic", "focus", "on_topic", "unrelated"),
    [
        (
            "Effects of late-night social media use on classroom attention",
            ["social media", "students", "sleep"],
            "Students use social media late at night and lose sleep.",
            "The garden has tulips and roses.",
        ),
        (
            "Benefits and disadvantages of school uniforms",
            ["school uniforms", "benefits", "disadvantages"],
            "School uniforms can reduce clothing costs.",
            "Renewable energy powers the village.",
        ),
        (
            "Effects of environmental pollution on community health",
            ["environmental pollution", "community", "health"],
            "Environmental pollution harms community health.",
            "Students enjoy reading novels.",
        ),
        (
            "Importance of reading habits among students",
            ["reading habits", "students"],
            "Students who read often build reading habits.",
            "School uniforms use blue fabric.",
        ),
    ],
)
def test_same_matcher_handles_unrelated_topics(
    topic_service: TopicService, topic: str, focus: list[str], on_topic: str, unrelated: str
) -> None:
    on_topic_result = topic_service.analyze(on_topic, topic, focus, include_wordnet=False)
    unrelated_result = topic_service.analyze(unrelated, topic, focus, include_wordnet=False)
    assert on_topic_result["focus_coverage"]["observed_unique_focus_terms"] > 0
    assert unrelated_result["focus_coverage"]["observed_unique_focus_terms"] == 0


def test_keyword_only_and_negation_remain_lexical(topic_service: TopicService) -> None:
    result = topic_service.analyze(
        "No students sleep; fatigue, attention, concentration, classroom, and social media.",
        "Social media and attention",
        ["students", "sleep", "fatigue", "attention", "concentration", "classroom", "social media"],
    )
    assert result["focus_coverage"]["observed_unique_focus_terms"] >= 6
    assert "not" not in result
    assert "semantic intelligibility has not been determined" in result["interpretation_limit"]


@pytest.mark.parametrize(
    ("text", "focus"),
    [
        ("Fatigue swallowed classroom attention.", ["fatigue", "classroom", "attention"]),
        ("School uniforms? Benefits!", ["school uniforms", "benefits"]),
        ("Pollution harms health", ["pollution", "community health"]),
        ("Reading habits", ["reading habits", "students"]),
    ],
)
def test_figurative_and_incomplete_text_returns_only_observations(
    topic_service: TopicService, text: str, focus: list[str]
) -> None:
    result = topic_service.analyze(text, "An arbitrary assignment topic", focus, include_wordnet=False)
    assert result["student_concepts"]
    assert result["focus_coverage"]["observed_unique_focus_terms"] > 0
    assert "semantic intelligibility has not been determined" in result["interpretation_limit"]


def test_wordnet_relationship_is_candidate_and_not_coverage(topic_service: TopicService) -> None:
    result = topic_service.analyze("An automobile is parked.", "Cars", ["car"])
    suggestions = result["wordnet"]["suggestions"]
    assert any(
        suggestion["observed_student_term"].casefold() == "automobile"
        and suggestion["synset_id"] == "car.n.01"
        and "Candidate only" in suggestion["uncertainty"]
        for suggestion in suggestions
    )
    assert result["focus_coverage"]["unobserved_focus_terms"] == ["car"]


def test_wordnet_ambiguous_context_is_not_claimed_as_proven(topic_service: TopicService) -> None:
    result = topic_service.analyze("An automobile is parked.", "Cars", ["car"])
    suggestion = next(
        item for item in result["wordnet"]["suggestions"]
        if item["observed_student_term"].casefold() == "automobile"
    )
    assert suggestion["relationship_type"] == "shared_synset_synonym_candidate"
    assert "not disambiguated" in suggestion["uncertainty"]


def test_missing_wordnet_resource_returns_no_guesses(topic_service: TopicService, monkeypatch) -> None:
    def unavailable(*args, **kwargs):
        raise LookupError("WordNet not installed")

    monkeypatch.setattr("services.topic_service.wordnet.synsets", unavailable)
    result = topic_service.analyze("An automobile is parked.", "Cars", ["car"])
    assert result["wordnet"]["status"] == "resource_missing"
    assert result["wordnet"]["suggestions"] == []


def test_student_text_uses_one_shared_doc(nlp_service: NLPService) -> None:
    parse = Mock(wraps=nlp_service.parse)
    analyze_doc = Mock(wraps=nlp_service.analyze_doc)
    nlp_service.parse = parse
    nlp_service.analyze_doc = analyze_doc
    try:
        result = TopicService(nlp_service).analyze(
            "Students read books.", "Reading", ["student"]
        )
        parse.assert_called_once_with("Students read books.")
        analyze_doc.assert_called_once()
        assert analyze_doc.call_args.args[0].text == "Students read books."
        assert result["linguistic_analysis"]["counts"]["sentence_count"] == 1
    finally:
        nlp_service.parse = parse._mock_wraps
        nlp_service.analyze_doc = analyze_doc._mock_wraps


def test_meaningful_and_keyword_rich_gibberish_only_report_terms(
    topic_service: TopicService,
) -> None:
    topic = "Effects of late-night social media use on students' classroom attention"
    focus = ["social media", "students", "sleep", "fatigue", "attention", "concentration", "classroom"]
    meaningful = (
        "Late-night social media use can reduce students' sleep because they spend too much time online. "
        "As a result, students may experience fatigue and difficulty concentrating during classroom lessons."
    )
    gibberish = (
        "Late-night social media use makes students' sleep dance inside classroom umbrellas. "
        "Fatigue teaches attention to swallow invisible notifications while concentration whispers to digital shadows."
    )
    meaningful_result = topic_service.analyze(meaningful, topic, focus, include_wordnet=False)
    gibberish_result = topic_service.analyze(gibberish, topic, focus, include_wordnet=False)
    assert meaningful_result["focus_coverage"]["observed_unique_focus_terms"] >= 5
    assert gibberish_result["focus_coverage"]["observed_unique_focus_terms"] == 7
    assert "semantic intelligibility has not been determined" in meaningful_result["interpretation_limit"]
    assert "semantic intelligibility has not been determined" in gibberish_result["interpretation_limit"]
    assert "readiness" not in meaningful_result
    assert "readiness" not in gibberish_result


def test_phase_one_analyze_api_keeps_existing_result_fields(nlp_service: NLPService) -> None:
    result = nlp_service.analyze("Students read.")
    assert set(result) == {"text", "counts", "sentences", "tokens", "noun_phrases"}
    assert result["counts"]["sentence_count"] == 1
