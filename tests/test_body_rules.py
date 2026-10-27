"""Cross-topic tests for evidence-based Body rules and feedback."""

from unittest.mock import Mock

import pytest

from services.body_rules import BodyRuleBase
from services.feedback_service import FeedbackService
from services.nlp_service import NLPService
from services.topic_service import TopicService


@pytest.fixture(scope="module")
def nlp_service() -> NLPService:
    return NLPService()


@pytest.fixture(scope="module")
def body_rules(nlp_service: NLPService) -> BodyRuleBase:
    return BodyRuleBase(TopicService(nlp_service))


@pytest.fixture(scope="module")
def feedback() -> FeedbackService:
    return FeedbackService()


TOPIC_CASES = [
    {
        "name": "social media and classroom attention",
        "topic": "Effects of late-night social media use on classroom attention",
        "focus": ["social media", "students", "sleep", "fatigue", "attention", "classroom"],
        "developed": "Students use social media late at night. This can reduce sleep and affect classroom attention because students feel tired.",
        "second": "Teachers also observe fatigue during morning lessons.",
        "keywords": "Social media. Sleep. Students. Fatigue. Attention. Classroom.",
        "incomplete": "Students use social media because.",
        "gibberish": "Social media makes classroom attention drink invisible clocks while students' sleep dances through digital umbrellas.",
        "figurative": "Each notification is a tiny bell that keeps attention awake.",
        "unrelated": "The library provides books and internet access for residents.",
        "repeat": "Students discuss sleep. Students discuss sleep.",
        "short": "Social media affects sleep.",
        "partial_focus": "Late-night social media can affect sleep.",
        "negated": "Social media does not always reduce sleep.",
    },
    {
        "name": "school uniforms",
        "topic": "Benefits and disadvantages of school uniforms",
        "focus": ["school uniforms", "students", "costs", "equality", "identity", "rules"],
        "developed": "School uniforms may reduce pressure to buy fashionable clothing. Strict rules can also limit students' self-expression.",
        "second": "Students may value clothing choices as part of their identity.",
        "keywords": "Uniforms. Students. Costs. Equality. Identity. Rules.",
        "incomplete": "School uniforms matter because students.",
        "gibberish": "Uniforms make equality drink classroom buttons while identity teaches fabric to swallow silent rules.",
        "figurative": "Uniforms are a shared canvas on which students display school identity.",
        "unrelated": "The local river supports several kinds of fish.",
        "repeat": "Students wear uniforms. Students wear uniforms.",
        "short": "School uniforms express identity.",
        "partial_focus": "Uniforms may reduce clothing costs.",
        "negated": "Uniforms do not guarantee equality for every student.",
    },
    {
        "name": "environmental pollution",
        "topic": "Effects of environmental pollution on community health",
        "focus": ["pollution", "air pollution", "community", "health", "emissions", "lungs"],
        "developed": "Air pollution can worsen respiratory symptoms near busy roads. Pollutants can irritate the lungs.",
        "second": "Local monitoring can identify periods of higher emissions.",
        "keywords": "Pollution. Community. Health. Lungs. Emissions.",
        "incomplete": "Air pollution is harmful because people.",
        "gibberish": "Pollution makes community health drink blue traffic while lungs whisper backward through the chimney.",
        "figurative": "A dirty river carries the city's forgotten smoke downstream.",
        "unrelated": "Students use libraries to find information for assignments.",
        "repeat": "Pollution affects health. Pollution affects health.",
        "short": "Air pollution harms health.",
        "partial_focus": "Pollution can harm health.",
        "negated": "Air pollution does not affect every resident in the same way.",
    },
    {
        "name": "reading habits",
        "topic": "Importance of reading habits among students",
        "focus": ["reading habits", "students", "reading", "books", "libraries", "literacy"],
        "developed": "Regular reading gives students practice with unfamiliar words. It can also help them follow longer arguments.",
        "second": "A library provides access to books for students who do not have them at home.",
        "keywords": "Reading habits. Students. Books. Libraries. Literacy.",
        "incomplete": "Reading habits are important because students.",
        "gibberish": "Reading habits make literacy swallow purple paragraphs while books whisper under invisible desks.",
        "figurative": "Books are windows into unfamiliar ideas.",
        "unrelated": "Solar panels convert sunlight into electricity.",
        "repeat": "Students read books. Students read books.",
        "short": "Reading helps students.",
        "partial_focus": "Reading helps students learn.",
        "negated": "Reading does not benefit every student in the same way.",
    },
    {
        "name": "renewable energy",
        "topic": "Benefits and challenges of renewable energy",
        "focus": ["renewable energy", "solar", "wind power", "electricity", "storage", "fossil fuels"],
        "developed": "Solar and wind power produce electricity without burning fossil fuels during operation. Output varies with weather and time of day.",
        "second": "Storage can help balance supply when generation changes.",
        "keywords": "Solar panels. Wind power. Storage. Electricity. Fossil fuels.",
        "incomplete": "Renewable energy helps communities because storage.",
        "gibberish": "Renewable energy makes electricity drink mountain shadows while storage teaches sunlight to dance.",
        "figurative": "Wind power turns a turbine into a patient clock waiting for weather to wind its hands.",
        "unrelated": "Healthy meals can provide important nutrients.",
        "repeat": "Solar power supplies electricity. Solar power supplies electricity.",
        "short": "Solar power reduces emissions.",
        "partial_focus": "Solar power can reduce fuel use.",
        "negated": "Solar power does not eliminate every storage challenge.",
    },
    {
        "name": "healthy lifestyles",
        "topic": "Factors that support a healthy lifestyle",
        "focus": ["healthy lifestyle", "sleep", "exercise", "nutrition", "health", "stress", "routine"],
        "developed": "A regular sleep schedule can support health. Enjoyable physical activity and nutritious food may also help, although needs differ.",
        "second": "Some people adjust routines to fit work or family responsibilities.",
        "keywords": "Exercise. Nutrition. Sleep. Stress. Health. Routine.",
        "incomplete": "Healthy habits help people because exercise.",
        "gibberish": "Healthy habits make sleep dance inside nutrition umbrellas while exercise swallows silent routines.",
        "figurative": "Sleep gives a tired week a quiet place to rest.",
        "unrelated": "School uniforms can reduce pressure to buy fashionable clothes.",
        "repeat": "Exercise can improve health. Exercise can improve health.",
        "short": "Regular sleep supports health.",
        "partial_focus": "Regular sleep can support health.",
        "negated": "Exercise does not remove every source of stress.",
    },
]


@pytest.mark.parametrize("case", TOPIC_CASES, ids=lambda case: case["name"])
def test_body_rule_diagnostics_generalize_across_topics(
    body_rules: BodyRuleBase, case: dict
) -> None:
    developed = body_rules.analyze(case["developed"], case["topic"], case["focus"])
    assert developed["paragraph_count"] == 1
    assert developed["paragraphs"][0]["counts"]["sentence_count"] >= 2
    assert developed["paragraphs"][0]["topic_sentence_candidates"]
    candidate_sentence_texts = [
        candidate["sentence_text"]
        for candidate in developed["paragraphs"][0]["topic_sentence_candidates"]
    ]
    assert len(candidate_sentence_texts) == len(set(candidate_sentence_texts))
    assert developed["paragraphs"][0]["supporting_detail_candidates"]["candidates"]

    multiple = body_rules.analyze(
        case["developed"] + "\n\n" + case["second"], case["topic"], case["focus"]
    )
    assert multiple["paragraph_count"] == 2
    assert multiple["cross_paragraph_continuity"]["status"] == "PAIRWISE_OBSERVATIONS"
    assert len(multiple["cross_paragraph_continuity"]["paragraph_pairs"]) == 1

    different_focus = body_rules.analyze(
        case["developed"] + "\n\n" + case["unrelated"],
        case["topic"],
        case["focus"],
    )
    assert len(different_focus["cross_paragraph_continuity"]["paragraph_pairs"]) == 1

    keyword_list = body_rules.analyze(case["keywords"], case["topic"], case["focus"])
    assert keyword_list["paragraphs"][0]["fragment_or_list_candidate"]["keyword_list_candidate"]

    incomplete = body_rules.analyze(case["incomplete"], case["topic"], case["focus"])
    assert incomplete["paragraph_count"] == 1
    assert incomplete["paragraphs"][0]["sentence_spans"]

    gibberish = body_rules.analyze(case["gibberish"], case["topic"], case["focus"])
    assert gibberish["paragraphs"][0]["clause_structure_candidates"]
    assert gibberish["lexical_topic_evidence"]["observed_focus_terms"]
    assert "meaningful" not in gibberish
    assert any("does not establish semantic intelligibility" in item for item in gibberish["uncertainty"])

    figurative = body_rules.analyze(case["figurative"], case["topic"], case["focus"])
    assert figurative["paragraphs"][0]["clause_structure_candidates"]
    assert "figurative" not in figurative["prohibited_conclusions"]

    unrelated = body_rules.analyze(case["unrelated"], case["topic"], case["focus"])
    assert unrelated["paragraphs"][0]["sentence_spans"]
    assert "meaningful or off-topic" not in unrelated["prohibited_conclusions"]

    short = body_rules.analyze(case["short"], case["topic"], case["focus"])
    assert short["paragraphs"][0]["sentence_spans"]
    partial_focus = body_rules.analyze(case["partial_focus"], case["topic"], case["focus"])
    assert partial_focus["paragraphs"][0]["observed_focus_terms"]
    assert len(partial_focus["paragraphs"][0]["observed_focus_terms"]) < len(case["focus"])

    negated = body_rules.analyze(case["negated"], case["topic"], case["focus"])
    assert any(
        token["text"].casefold() == "not"
        for sentence in negated["paragraphs"][0]["sentence_spans"]
        for token in sentence["tokens"]
    )

    repeated = body_rules.analyze(case["repeat"], case["topic"], case["focus"])
    assert repeated["paragraphs"][0]["repetition_observations"]["repeated_sentence_openings"]
    assert "not automatically harmful" in repeated["paragraphs"][0]["repetition_observations"]["interpretation"]


def test_blank_line_segmentation_preserves_exact_offsets_and_newlines(
    body_rules: BodyRuleBase,
) -> None:
    samples = [
        "  Students read books.  \n\n \t\n\n Students discuss them.  ",
        "Students read books.\r\n\r\nStudents discuss them.",
        "Students read books.\r\rStudents discuss them.",
    ]
    for text in samples:
        result = body_rules.analyze(text, "Reading habits", ["students", "books"])
        assert result["paragraph_count"] == 2
        for paragraph in result["paragraphs"]:
            assert text[paragraph["start"] : paragraph["end"]] == paragraph["text"]
        assert result["paragraphs"][0]["start"] == text.index("Students")


def test_blank_and_punctuation_only_body_are_not_substantive(body_rules: BodyRuleBase) -> None:
    empty = body_rules.analyze("\n \r\n", "Reading", ["reading"])
    punctuation = body_rules.analyze("?!...\n\n!!!", "Reading", ["reading"])
    assert empty["paragraph_count"] == 0
    assert empty["substantive_paragraph_count"] == 0
    assert punctuation["paragraph_count"] == 2
    assert punctuation["substantive_paragraph_count"] == 0
    assert any(event["rule_id"] == "BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH" for event in empty["rule_evidence"])


def test_long_body_paragraph_is_processed_without_fixed_sentence_limit(
    body_rules: BodyRuleBase,
) -> None:
    text = " ".join("Students read books and discuss ideas." for _ in range(30))
    result = body_rules.analyze(text, "Reading habits", ["students", "books"])
    assert result["paragraph_count"] == 1
    assert result["paragraphs"][0]["counts"]["sentence_count"] >= 20
    assert result["paragraphs"][0]["counts"]["alphabetic_word_count"] > 100


def test_per_paragraph_focus_matches_are_span_scoped(body_rules: BodyRuleBase) -> None:
    text = "Students use social media.\n\nSleep affects classroom attention."
    result = body_rules.analyze(
        text,
        "Social media and classroom attention",
        ["social media", "students", "sleep", "classroom", "attention"],
    )
    first, second = result["paragraphs"]
    assert first["observed_focus_terms"] == ["social media", "students"]
    assert second["observed_focus_terms"] == ["sleep", "classroom", "attention"]
    for paragraph in result["paragraphs"]:
        for match in paragraph["focus_term_evidence"]:
            assert paragraph["start"] <= match["start"] < match["end"] <= paragraph["end"]
            assert text[match["start"] : match["end"]] == match["observed_text"]


def test_multiword_focus_match_cannot_bridge_a_blank_line(body_rules: BodyRuleBase) -> None:
    text = "Students discuss social\n\nmedia effects."
    result = body_rules.analyze(text, "Social media", ["social media"])
    assert result["lexical_topic_evidence"]["observed_focus_terms"] == []
    assert result["lexical_topic_evidence"]["unobserved_focus_terms"] == ["social media"]
    assert all(not paragraph["focus_term_evidence"] for paragraph in result["paragraphs"])

    conclusion_like = body_rules.analyze(
        "School\n\nuniforms should be required.",
        "Benefits of school uniforms",
        ["school uniforms"],
    )
    assert conclusion_like["lexical_topic_evidence"]["matches"] == []
    assert conclusion_like["paragraph_count"] == 2

    same_paragraph = body_rules.analyze(
        "School\nuniforms should be required.",
        "Benefits of school uniforms",
        ["school uniforms"],
    )
    assert same_paragraph["lexical_topic_evidence"]["matches"]


def test_topic_sentence_candidate_need_not_be_first_sentence(body_rules: BodyRuleBase) -> None:
    text = (
        "Modern classrooms contain many challenges. "
        "Late-night social media use can reduce students' sleep. "
        "This may affect classroom attention."
    )
    result = body_rules.analyze(
        text,
        "Effects of late-night social media use on classroom attention",
        ["social media", "sleep", "attention"],
    )
    candidates = result["paragraphs"][0]["topic_sentence_candidates"]
    assert candidates
    assert any(candidate["sentence_index"] == 1 for candidate in candidates)
    assert any(candidate["sentence_index"] == 2 for candidate in candidates)


def test_discourse_marker_without_clause_is_not_supporting_detail(body_rules: BodyRuleBase) -> None:
    result = body_rules.analyze(
        "Students read books. For example, libraries.",
        "Reading habits among students",
        ["students", "reading", "books", "libraries"],
    )
    paragraph = result["paragraphs"][0]
    assert paragraph["example_or_explanation_markers"]
    assert paragraph["supporting_detail_candidates"]["candidates"] == []


def test_repetition_and_unity_findings_include_source_spans(body_rules: BodyRuleBase) -> None:
    text = "Students read books daily. Students read books at home."
    result = body_rules.analyze(text, "Reading habits", ["students", "reading", "books"])
    paragraph = result["paragraphs"][0]
    assert paragraph["repetition_observations"]["repeated_sentence_openings"]
    repeated = paragraph["repetition_observations"]["repeated_surface_content_words"]
    assert repeated
    for item in repeated:
        for occurrence in item["occurrences"]:
            assert text[occurrence["start"] : occurrence["end"]].casefold() == item["term"]
    assert paragraph["paragraph_unity_evidence"]["sentence_pairs"][0]["direct_shared_content_terms"]


def test_cross_paragraph_focus_shift_is_a_review_candidate_not_a_verdict(
    body_rules: BodyRuleBase, feedback: FeedbackService
) -> None:
    result = body_rules.analyze(
        "Wind turbines can generate electricity.\n\nReading habits help students learn.",
        "Benefits and challenges of renewable energy",
        ["wind", "electricity", "storage", "solar"],
    )
    pair = result["cross_paragraph_continuity"]["paragraph_pairs"][0]
    assert pair["status"] == "NO_EXPLICIT_LEXICAL_LINK_OBSERVED"
    generated = feedback.generate_body(result, include_trace=True)
    assert generated["_Research Decision Trace"]["fields"]["Primary Feedback"]["selection_branch"] == "body_ideas_develop_point"
    assert "Paragraph 1" in generated["Primary Feedback"]
    assert next(c for c in generated["_Research Decision Trace"]["selection_checks"] if c["branch"] == "body_organization_paragraph_link")["status"] == "MATCHED_NOT_SELECTED_HIGHER_PRIORITY"
    assert "off-topic" not in generated["Primary Feedback"].casefold()


def test_repetition_feedback_is_neutral(body_rules: BodyRuleBase, feedback: FeedbackService) -> None:
    result = body_rules.analyze(
        "Students read books. Students discuss books.",
        "Reading habits",
        ["students", "books"],
    )
    generated = feedback.generate_body(result)
    assert any("Repeating a word can help readers follow" in item for item in generated["What's Working"])
    assert not any("harmful" in item.casefold() for item in generated["Needs Attention"])
    assert not any("harmful" in item.casefold() for item in generated["Needs Attention"])


def test_introduction_continuity_is_optional_and_lexical_only(body_rules: BodyRuleBase) -> None:
    body = "Students study books at school."
    without_intro = body_rules.analyze(body, "Reading", ["students", "books"])
    with_intro = body_rules.analyze(
        body,
        "Reading",
        ["students", "books"],
        introduction_text="A student studies books at home.",
    )
    assert without_intro["introduction_to_body_continuity"]["status"] == "NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED"
    continuity = with_intro["introduction_to_body_continuity"]
    assert continuity["status"] == "LEXICAL_COMPARISON_AVAILABLE"
    assert continuity["direct_lexical_continuity"]
    assert any(item["normalized_form"] == "student" for item in continuity["lemma_normalized_continuity"])
    assert "cannot establish" in continuity["limitation"]


def test_introduction_wordnet_overlap_is_candidate_not_confirmed(body_rules: BodyRuleBase) -> None:
    result = body_rules.analyze(
        "An automobile is parked.",
        "Vehicle use",
        [],
        introduction_text="A car is parked.",
    )
    wordnet_result = result["introduction_to_body_continuity"]["wordnet_relationship_candidates"]
    assert wordnet_result["status"] == "AVAILABLE"
    assert any(
        item["synset_id"] == "car.n.01"
        and item["relationship_type"] == "shared_synset_candidate"
        for item in wordnet_result["suggestions"]
    )
    assert result["introduction_to_body_continuity"]["direct_lexical_continuity"] == []


def test_introduction_wordnet_resource_missing_does_not_fabricate_links(
    body_rules: BodyRuleBase, monkeypatch
) -> None:
    def unavailable(*args, **kwargs):
        raise LookupError("WordNet resource missing")

    monkeypatch.setattr("services.body_rules.wordnet.synsets", unavailable)
    result = body_rules.analyze(
        "An automobile is parked.",
        "Vehicle use",
        [],
        introduction_text="A car is parked.",
    )
    wordnet_result = result["introduction_to_body_continuity"]["wordnet_relationship_candidates"]
    assert wordnet_result["status"] == "RESOURCE_MISSING"
    assert wordnet_result["suggestions"] == []


def test_phase3_meaningful_and_gibberish_body_share_structural_signals(
    body_rules: BodyRuleBase,
) -> None:
    topic = "Effects of late-night social media use on classroom attention"
    focus = ["social media", "students", "sleep", "fatigue", "attention", "concentration", "classroom"]
    meaningful = (
        "Late-night social media use can reduce students' sleep because they spend too much time online. "
        "As a result, students may experience fatigue and difficulty concentrating during classroom lessons."
    )
    gibberish = (
        "Late-night social media use makes students' sleep dance inside classroom umbrellas. "
        "Fatigue teaches attention to swallow invisible notifications while concentration whispers to digital shadows."
    )
    meaningful_result = body_rules.analyze(meaningful, topic, focus)
    gibberish_result = body_rules.analyze(gibberish, topic, focus)
    meaningful_paragraph = meaningful_result["paragraphs"][0]
    gibberish_paragraph = gibberish_result["paragraphs"][0]
    assert meaningful_paragraph["observed_focus_terms"] == [
        "social media", "students", "sleep", "fatigue", "classroom"
    ]
    assert gibberish_paragraph["observed_focus_terms"] == focus
    assert meaningful_paragraph["clause_structure_candidates"]
    assert gibberish_paragraph["clause_structure_candidates"]
    assert "BODY_READY" in gibberish_result["prohibited_conclusions"]


def test_body_feedback_uses_body_evidence_and_provenance(
    body_rules: BodyRuleBase, feedback: FeedbackService
) -> None:
    body = "Social media. Students. Sleep."
    analysis = body_rules.analyze(body, "Effects of social media on sleep", ["social media", "students", "sleep"])
    output = feedback.generate_body(analysis)
    assert set(output) >= {
        "Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step", "Feedback Provenance"
    }
    assert "assignment words as a list" in output["Primary Feedback"]
    events = {event["rule_id"]: event for event in analysis["rule_evidence"]}
    assert output["Feedback Provenance"]
    for item in output["Feedback Provenance"]:
        assert item["actual_evidence"] == events[item["rule_id"]]["actual_evidence"]
        assert item["triggering_condition"] == events[item["rule_id"]]["triggering_condition"]


def test_list_feedback_does_not_claim_unobserved_focus_terms(
    body_rules: BodyRuleBase, feedback: FeedbackService
) -> None:
    analysis = body_rules.analyze(
        "Pencils. Rivers. Models. Lanterns.",
        "Artificial intelligence in education",
        ["artificial intelligence"],
    )
    generated = feedback.generate_body(analysis)

    assert "no assignment words" in generated["Primary Feedback"].casefold()
    assert "related terms" not in generated["Primary Feedback"].casefold()
    assert any(event["rule_id"] == "BODY.P1.PARAGRAPH.FOCUS_TERMS_NOT_OBSERVED" for event in analysis["rule_evidence"])
    assert not any("assignment words" in item.casefold() for item in generated["Needs Attention"]), "wording absence is retained as an observation, not another corrective lesson"


def test_body_rule_uses_one_parse_and_optional_intro_is_a_distinct_parse(
    nlp_service: NLPService,
) -> None:
    parse = Mock(wraps=nlp_service.parse)
    analyze_doc = Mock(wraps=nlp_service.analyze_doc)
    nlp_service.parse = parse
    nlp_service.analyze_doc = analyze_doc
    rules = BodyRuleBase(TopicService(nlp_service))
    body = "Students read books.\n\nStudents discuss books."
    try:
        rules.analyze(body, "Reading", ["students", "books"])
        parse.assert_called_once_with(body)
        analyze_doc.assert_called_once()
        assert analyze_doc.call_args.args[0].text == body
    finally:
        nlp_service.parse = parse._mock_wraps
        nlp_service.analyze_doc = analyze_doc._mock_wraps

    parse = Mock(wraps=nlp_service.parse)
    nlp_service.parse = parse
    try:
        rules.analyze(body, "Reading", ["students"], introduction_text="Students enjoy books.")
        assert parse.call_count == 2
        assert {call.args[0] for call in parse.call_args_list} == {body, "Students enjoy books."}
    finally:
        nlp_service.parse = parse._mock_wraps


def test_body_output_is_deterministic_and_does_not_create_quality_verdict(
    body_rules: BodyRuleBase,
) -> None:
    text = "Students read books.\n\nStudents discuss books."
    first = body_rules.analyze(text, "Reading habits", ["students", "books"])
    second = body_rules.analyze(text, "Reading habits", ["students", "books"])
    assert first == second
    assert first["stage"] == "BODY"
    assert "body_quality_score" not in first
    assert "BODY_READY" in first["prohibited_conclusions"]
    assert first["cross_paragraph_continuity"]["overall_score"] is None
