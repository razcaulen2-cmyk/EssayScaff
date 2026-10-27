"""Cross-topic tests for deterministic, structural Introduction guidance."""

from unittest.mock import Mock

import pytest

from services.feedback_service import FeedbackService
from services.introduction_rules import IntroductionRuleBase
from services.nlp_service import NLPService
from services.topic_service import TopicService


@pytest.fixture(scope="module")
def nlp_service() -> NLPService:
    return NLPService()


@pytest.fixture(scope="module")
def rules(nlp_service: NLPService) -> IntroductionRuleBase:
    return IntroductionRuleBase(TopicService(nlp_service))


@pytest.fixture(scope="module")
def feedback() -> FeedbackService:
    return FeedbackService()


TOPIC_CASES = [
    {
        "name": "social media",
        "topic": "Effects of late-night social media use on classroom attention",
        "focus": ["social media", "students", "sleep", "fatigue", "attention", "concentration", "classroom"],
        "meaningful": "Late-night social media use can reduce students' sleep because they spend too much time online. As a result, students may experience fatigue and difficulty concentrating during classroom lessons.",
        "keywords": "Late-night social media. Students. Sleep. Fatigue. Attention. Classroom concentration.",
        "incomplete": "Social media use is important because students.",
        "gibberish": "Late-night social media use makes students' sleep dance inside classroom umbrellas. Fatigue teaches attention to swallow invisible notifications while concentration whispers to digital shadows.",
        "figurative": "At midnight, each notification is a tiny bell that keeps a student's attention awake after class.",
        "imperfect": "Students use social media too late and they is tired in class, so focusing become difficult.",
        "unrelated": "A community garden gives neighbors a place to meet.",
        "short": "Social media affects sleep.",
        "partial_focus": "Late-night social media can affect sleep.",
        "negated": "Social media does not always reduce sleep.",
    },
    {
        "name": "school uniforms",
        "topic": "Benefits and disadvantages of school uniforms",
        "focus": ["school uniforms", "students", "costs", "equality", "identity", "benefits", "disadvantages"],
        "meaningful": "School uniforms can reduce pressure to buy fashionable clothes, although strict rules may limit students' self-expression.",
        "keywords": "Uniforms. Students. Costs. Equality. Identity. School rules.",
        "incomplete": "Uniform rules are important because students.",
        "gibberish": "Uniform policies make identity drink school buttons while equality teaches fabric to sing invisible lessons.",
        "figurative": "Uniforms are a shared canvas where students display school identity.",
        "imperfect": "School uniform make students feel equal, but some student dislike it.",
        "unrelated": "The library provides extended weekend hours for residents.",
        "short": "School uniforms express identity.",
        "partial_focus": "Uniforms may reduce clothing costs.",
        "negated": "Uniforms do not guarantee equality for every student.",
    },
    {
        "name": "environmental pollution",
        "topic": "Effects of environmental pollution on community health",
        "focus": ["pollution", "air pollution", "community", "health", "emissions", "lungs", "particulate matter"],
        "meaningful": "Air pollution can worsen respiratory symptoms in communities near busy roads.",
        "keywords": "Air pollution. Emissions. Community. Health. Lungs.",
        "incomplete": "Air pollution is harmful because communities.",
        "gibberish": "Pollution teaches lungs to drink blue traffic while community health whispers to chimneys.",
        "figurative": "The river carries the city's forgotten smoke downstream.",
        "imperfect": "Pollution make people cough when smoke stay near road.",
        "unrelated": "Reading novels gives students a quiet place to think.",
        "short": "Air pollution harms health.",
        "partial_focus": "Pollution can harm health.",
        "negated": "Air pollution does not affect every resident in the same way.",
    },
    {
        "name": "reading habits",
        "topic": "Importance of reading habits among students",
        "focus": ["reading habits", "students", "reading", "books", "libraries", "literacy"],
        "meaningful": "Regular reading gives students practice with unfamiliar words and longer arguments.",
        "keywords": "Reading habits. Students. Books. Libraries. Literacy.",
        "incomplete": "Reading habits are important because students.",
        "gibberish": "Reading habits make literacy swallow purple paragraphs while books whisper under invisible desks.",
        "figurative": "Books are windows into unfamiliar ideas.",
        "imperfect": "Reading habits helps students learn new words.",
        "unrelated": "Renewable energy can reduce fossil fuel use.",
        "short": "Reading helps students.",
        "partial_focus": "Reading helps students learn.",
        "negated": "Reading does not benefit every student in the same way.",
    },
    {
        "name": "renewable energy",
        "topic": "Benefits and challenges of renewable energy",
        "focus": ["renewable energy", "solar", "wind power", "electricity", "storage", "fossil fuels"],
        "meaningful": "Solar and wind power provide electricity without burning fossil fuels during operation.",
        "keywords": "Solar panels. Wind turbines. Storage. Electricity. Fossil fuels.",
        "incomplete": "Renewable energy is important because storage.",
        "gibberish": "Renewable energy makes electricity drink mountain shadows while storage teaches sunlight to dance.",
        "figurative": "Wind power turns the turbine into a patient clock.",
        "imperfect": "The panels makes energy when sun shine.",
        "unrelated": "Healthy meals can provide important nutrients.",
        "short": "Solar power reduces emissions.",
        "partial_focus": "Solar power can reduce fuel use.",
        "negated": "Solar power does not eliminate every storage challenge.",
    },
    {
        "name": "healthy lifestyles",
        "topic": "Factors that support a healthy lifestyle",
        "focus": ["healthy lifestyle", "sleep", "exercise", "nutrition", "health", "stress", "routine"],
        "meaningful": "A regular sleep schedule and enjoyable activity can support health, although personal needs differ.",
        "keywords": "Exercise. Nutrition. Sleep. Stress. Health. Routine.",
        "incomplete": "Healthy habits matter because students.",
        "gibberish": "Healthy habits make sleep dance inside nutrition umbrellas while exercise swallows silent routines.",
        "figurative": "Sleep gives a tired week a quiet place to rest.",
        "imperfect": "Healthy habits helps people feel better when they sleeps enough.",
        "unrelated": "The library provides books and internet access for residents.",
        "short": "Regular sleep supports health.",
        "partial_focus": "Regular sleep can support health.",
        "negated": "Exercise does not remove every source of stress.",
    },
]


@pytest.mark.parametrize("case", TOPIC_CASES, ids=lambda item: item["name"])
def test_each_topic_supports_all_requested_introduction_diagnostics(
    rules: IntroductionRuleBase, feedback: FeedbackService, case: dict
) -> None:
    def analyze(kind: str) -> tuple[dict, dict]:
        result = rules.analyze(case[kind], case["topic"], case["focus"])
        return result, feedback.generate(result)

    meaningful, meaningful_feedback = analyze("meaningful")
    assert meaningful["central_direction_candidate"]["candidates"]
    assert meaningful["observable_structure"]["summary_status"] in {
        "STRUCTURAL_CANDIDATE",
        "REQUIRES_REVIEW",
    }

    keywords, keyword_feedback = analyze("keywords")
    assert keywords["observable_structure"]["list_or_fragment_candidate"]["keyword_list_candidate"]
    assert keywords["observable_structure"]["summary_status"] == "INSUFFICIENT_OBSERVABLE_STRUCTURE"
    assert "word list" in keyword_feedback["Primary Feedback"] or "list of ideas" in keyword_feedback["Primary Feedback"]
    assert keyword_feedback["Primary Feedback"] != meaningful_feedback["Primary Feedback"]

    incomplete, incomplete_feedback = analyze("incomplete")
    assert incomplete["observable_structure"]["incomplete_subordinator_candidates"]
    assert incomplete["observable_structure"]["summary_status"] == "REQUIRES_REVIEW"
    assert "may leave the thought unfinished" in incomplete_feedback["Primary Feedback"]

    gibberish, gibberish_feedback = analyze("gibberish")
    assert "meaningful" not in gibberish
    assert "ready" not in gibberish
    assert any(
        text in gibberish_feedback["Primary Feedback"]
        for text in ("sentence pattern", "main-point sentence", "main statement", "main-statement", "unfinished")
    )
    assert "correct" not in gibberish_feedback["Primary Feedback"].casefold()
    assert "meaningful" in gibberish_feedback["interpretation_limit"].casefold()
    assert any(
        event["rule_id"] == "INTRO.LIMITATION.NO_SEMANTIC_VALIDATION"
        for event in gibberish["rule_evidence"]
    )

    figurative, figurative_feedback = analyze("figurative")
    assert figurative["central_direction_candidate"]["candidates"]
    assert "meaningful" not in figurative_feedback["Primary Feedback"].casefold()

    imperfect, _ = analyze("imperfect")
    assert imperfect["text_presence"]["alphabetic_word_count"] > 0

    unrelated, _ = analyze("unrelated")
    assert unrelated["central_direction_candidate"]["candidates"]
    assert unrelated["lexical_topic_evidence"]["observed_focus_terms"] == []

    short, _ = analyze("short")
    assert short["central_direction_candidate"]["candidates"]
    assert short["text_presence"]["sentence_count"] == 1

    partial_focus, _ = analyze("partial_focus")
    assert partial_focus["lexical_topic_evidence"]["observed_focus_terms"]
    assert len(partial_focus["lexical_topic_evidence"]["observed_focus_terms"]) < len(case["focus"])

    negated, _ = analyze("negated")
    assert any(token["text"].casefold() == "not" for token in negated["linguistic_observations"]["tokens"])
    assert negated["central_direction_candidate"]["candidates"]


def test_empty_punctuation_fragment_and_sentence_presence_are_distinct(
    rules: IntroductionRuleBase, feedback: FeedbackService
) -> None:
    empty = rules.analyze("", "Reading habits", ["reading"])
    whitespace = rules.analyze("  \n\t", "Reading habits", ["reading"])
    punctuation = rules.analyze("?!...", "Reading habits", ["reading"])
    fragment = rules.analyze("Reading habits", "Reading habits", ["reading"])
    sentence = rules.analyze("Reading helps students.", "Reading habits", ["reading"])
    assert empty["text_presence"]["status"] == "EMPTY"
    assert whitespace["text_presence"]["status"] == "WHITESPACE_ONLY"
    assert punctuation["text_presence"]["status"] == "PUNCTUATION_ONLY"
    assert fragment["text_presence"]["status"] == "FRAGMENTARY_OR_NONCLAUSAL_TEXT"
    assert sentence["text_presence"]["status"] == "SENTENCE_STRUCTURE_OBSERVED"
    assert "is empty" in feedback.generate(empty)["Primary Feedback"]
    assert "has only spaces" in feedback.generate(whitespace)["Primary Feedback"]
    assert "punctuation but no words" in feedback.generate(punctuation)["Primary Feedback"]


def test_development_uses_clause_evidence_not_discourse_marker_alone(
    rules: IntroductionRuleBase,
) -> None:
    result = rules.analyze(
        "Students read. This is because.",
        "Reading habits",
        ["students", "reading"],
    )
    assert result["observable_structure"]["incomplete_subordinator_candidates"]
    assert result["development_evidence"]["status"] == "NO_ADDITIONAL_CLAUSE_ELABORATION_OBSERVED"


def test_subordinator_detection_ignores_complete_whether_since_and_how_clauses(
    rules: IntroductionRuleBase,
) -> None:
    examples = [
        "Whether we use AI to improve education.",
        "Since the beginning of time, students have used technology, but AI changes how they can learn and work.",
        "Since 1950, schools have required uniforms.",
        "We study because students need support.",
    ]
    for text in examples:
        result = rules.analyze(
            text,
            "Should schools allow students to use artificial intelligence tools for learning?",
            ["artificial intelligence", "education", "students", "technology"],
        )
        assert result["observable_structure"]["incomplete_subordinator_candidates"] == []


def test_initial_subordinate_clause_needs_an_independent_clause(
    rules: IntroductionRuleBase,
) -> None:
    incomplete = rules.analyze("Although the school has resources.", "School resources", ["school"])
    complete = rules.analyze(
        "Although the school has resources, it does.", "School resources", ["school"]
    )
    fragment = rules.analyze("Because students.", "School resources", ["school"])

    assert [item["text"] for item in incomplete["observable_structure"]["incomplete_subordinator_candidates"]] == ["Although"]
    assert complete["observable_structure"]["incomplete_subordinator_candidates"] == []
    assert [item["text"] for item in fragment["observable_structure"]["incomplete_subordinator_candidates"]] == ["Because"]


def test_nonroot_finite_clause_prevents_false_introduction_list_finding(
    rules: IntroductionRuleBase,
) -> None:
    text = (
        "Since the beginning of time, students have used technology, "
        "but AI changes how they can learn and work."
    )
    result = rules.analyze(text, "AI in education", ["artificial intelligence", "students", "technology"])

    candidates = result["observable_structure"]["central_direction_candidates"]
    assert [c["predicate_evidence"]["text"] for c in candidates] == ["used"]
    assert candidates[0]["finite_auxiliary_evidence"][0]["text"] == "have"
    assert "changes" in [item["text"] for item in result["development_evidence"]["evidence"]]
    assert not result["observable_structure"]["list_or_fragment_candidate"]["keyword_list_candidate"]


def test_missing_focus_feedback_precedes_generic_no_root_warning(
    rules: IntroductionRuleBase, feedback: FeedbackService
) -> None:
    analysis = rules.analyze(
        "More books, fewer desks.", "Artificial intelligence in education", ["artificial intelligence"]
    )
    generated = feedback.generate(analysis)

    assert generated["Primary Feedback"].startswith("The checks did not find your assignment words")
    primary_evidence = next(
        item for item in generated["Feedback Provenance"]
        if item["feedback_field"] == "Primary Feedback"
    )
    assert primary_evidence["rule_id"] == "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED"


def test_list_feedback_does_not_claim_topic_matches_when_none_were_observed(
    rules: IntroductionRuleBase, feedback: FeedbackService
) -> None:
    analysis = rules.analyze(
        "Pencils. Rivers. Models. Lanterns.", "Artificial intelligence in education", ["artificial intelligence"]
    )
    generated = feedback.generate(analysis)

    assert "no assignment words" in generated["Primary Feedback"].casefold()
    assert "topic words were found" not in generated["Primary Feedback"].casefold()


def test_semantic_anomaly_can_receive_structural_candidate_without_semantic_claim(
    rules: IntroductionRuleBase, feedback: FeedbackService
) -> None:
    text = "Late-night social media use makes students' sleep dance inside classroom umbrellas."
    result = rules.analyze(
        text,
        "Effects of late-night social media use on classroom attention",
        ["social media", "students", "sleep", "classroom"],
    )
    generated = feedback.generate(result)
    assert result["lexical_topic_evidence"]["observed_unique_focus_terms"] == 4
    assert result["central_direction_candidate"]["status"] == "CANDIDATE_FOUND"
    assert result["observable_structure"]["summary_status"] == "STRUCTURAL_CANDIDATE"
    assert "meaning" not in result
    assert "academically good" not in result
    assert "main-point sentence" in generated["Primary Feedback"]
    assert "meaning" not in generated["Primary Feedback"].casefold()
    assert "meaningful" in generated["interpretation_limit"].casefold()


def test_feedback_provenance_references_actual_rule_evidence_and_spans(
    rules: IntroductionRuleBase, feedback: FeedbackService
) -> None:
    text = "Students read books."
    analysis = rules.analyze(text, "Reading habits among students", ["students", "reading"])
    output = feedback.generate(analysis)
    rules_by_id = {event["rule_id"]: event for event in analysis["rule_evidence"]}
    assert set(output) >= {
        "Current Goal",
        "Primary Feedback",
        "What's Working",
        "Needs Attention",
        "Next Step",
        "Feedback Provenance",
    }
    assert output["Feedback Provenance"]
    for source in output["Feedback Provenance"]:
        rule = rules_by_id[source["rule_id"]]
        assert source["actual_evidence"] == rule["evidence"]
        assert source["triggering_condition"] == rule["triggering_condition"]
        for evidence in source["actual_evidence"]:
            if "start" in evidence and "end" in evidence and "text" in evidence:
                assert text[evidence["start"] : evidence["end"]] == evidence["text"]


def test_rulebase_reuses_one_parsed_student_doc(nlp_service: NLPService) -> None:
    parse = Mock(wraps=nlp_service.parse)
    analyze_doc = Mock(wraps=nlp_service.analyze_doc)
    nlp_service.parse = parse
    nlp_service.analyze_doc = analyze_doc
    try:
        analysis = IntroductionRuleBase(TopicService(nlp_service)).analyze(
            "Students read books.", "Reading habits", ["students"]
        )
        parse.assert_called_once_with("Students read books.")
        analyze_doc.assert_called_once()
        assert analyze_doc.call_args.args[0].text == "Students read books."
        assert analysis["linguistic_observations"]["counts"]["sentence_count"] == 1
    finally:
        nlp_service.parse = parse._mock_wraps
        nlp_service.analyze_doc = analyze_doc._mock_wraps


def test_outputs_are_deterministic_and_phase_1_to_3_contracts_remain(
    rules: IntroductionRuleBase, nlp_service: NLPService
) -> None:
    text = "School uniforms express identity."
    first = rules.analyze(text, "School uniforms", ["uniforms", "identity"])
    second = rules.analyze(text, "School uniforms", ["uniforms", "identity"])
    assert first == second
    phase_one = nlp_service.analyze(text)
    assert set(phase_one) == {"text", "counts", "sentences", "tokens", "noun_phrases"}
    phase_two = TopicService(nlp_service).analyze(text, "School uniforms", ["uniforms"])
    assert "confirmed_lexical_observations" in phase_two
    assert "focus_coverage" in phase_two
