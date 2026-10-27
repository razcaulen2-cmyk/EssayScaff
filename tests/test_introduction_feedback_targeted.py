"""Targeted Introduction feedback checks for specific, generic, and nonsensical writing."""

from app import create_app
from services.essay_analysis_service import EssayAnalysisService
from services.feedback_service import FeedbackService
from services.introduction_rules import IntroductionRuleBase
from services.nlp_service import NLPService
from services.topic_service import TopicService
from tests.auth_helpers import register_student


TOPIC = "Should schools allow students to use artificial intelligence tools for learning?"
FOCUS = ["artificial intelligence", "education", "students", "technology", "critical thinking"]


def analyze_introduction(text, topic=TOPIC, focus=FOCUS):
    rules = IntroductionRuleBase(TopicService(NLPService()))
    analysis = rules.analyze(text, topic, focus)
    feedback = FeedbackService().generate(analysis)
    return analysis, feedback


def test_ai_introduction_uses_existing_structure_to_ask_about_its_reason():
    text = (
        "Artificial intelligence tools are becoming common in schools. "
        "Schools should allow students to use them because students can use technology in education."
    )
    analysis, feedback = analyze_introduction(text)
    assert analysis["central_direction_candidate"]["candidates"]
    assert analysis["development_evidence"]["status"] == "STRUCTURAL_ELABORATION_CANDIDATE"
    assert "possible main statement and a 'because' part" in feedback["Primary Feedback"]
    assert "decide whether a reader needs more explanation" in feedback["Primary Feedback"]
    assert "Read your main statement with the explanation part" in feedback["Next Step"]
    assert "add a detail a reader would need" in feedback["Next Step"]
    assert feedback["Needs Attention"] == []

    provenance = next(
        item for item in feedback["Feedback Provenance"]
        if item["feedback_field"] == "Next Step"
        and item["rule_id"] == "INTRO.REASON.CLAUSE_TOPIC_OVERLAP"
    )
    event = next(
        item for item in analysis["rule_evidence"]
        if item["rule_id"] == provenance["rule_id"]
    )
    assert provenance["actual_evidence"] == event["evidence"]
    reason_spans = event["evidence"]
    assert reason_spans
    assert all(text[item["clause_start"]:item["clause_end"]].startswith("because") for item in reason_spans)

    ai_match = next(
        item for item in analysis["lexical_topic_evidence"]["matches"]
        if item["focus_term"] == "artificial intelligence"
    )
    assert text[ai_match["start"] : ai_match["end"]] == ai_match["observed_text"]
    assert ai_match["observed_text"].casefold() == "artificial intelligence"


def test_off_topic_introduction_reports_missing_focus_overlap_cautiously():
    text = (
        "Public transportation is important in crowded cities. Buses and trains can reduce traffic congestion "
        "and help commuters travel more efficiently. Cities should invest in public transportation because "
        "it can reduce pollution and improve daily travel."
    )
    analysis, feedback = analyze_introduction(text)
    assert analysis["lexical_topic_evidence"]["observed_focus_terms"] == []
    assert feedback["Primary Feedback"] == (
        "The checks did not find your assignment words in the opening. Compare your opening with the assignment; "
        "you may be using different words for the same idea."
    )
    assert "Different words for the same idea are fine" in feedback["Next Step"]
    warning = next(
        item for item in feedback["Feedback Provenance"]
        if item["feedback_field"] == "Primary Feedback"
        and item["rule_id"] == "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED"
    )
    event = next(item for item in analysis["rule_evidence"] if item["rule_id"] == warning["rule_id"])
    assert warning["actual_evidence"] == event["evidence"]
    assert "off-topic" not in feedback["Primary Feedback"].casefold()


def test_broad_focus_words_alone_are_not_presented_as_topic_relevance():
    text = "Students use buses to travel between crowded city neighborhoods."
    analysis, feedback = analyze_introduction(text, focus=["students", "use"])
    assert set(analysis["lexical_topic_evidence"]["observed_focus_terms"]) == {"students", "use"}
    assert "Only broad words such as" in feedback["Primary Feedback"]
    assert "specific subject the assignment asks about" in feedback["Primary Feedback"]
    assert not any("focus wording:" in item for item in feedback["What's Working"])
    broad_match = next(
        item for item in feedback["Feedback Provenance"]
        if item["feedback_field"] == "Primary Feedback"
    )
    assert broad_match["rule_id"] == "INTRO.TOPIC.FOCUS_TERMS_OBSERVED"


def test_well_developed_and_short_introductions_are_not_automatically_warned():
    developed = (
        "Artificial intelligence tools are becoming part of education. Schools can use them to give students practice "
        "that fits their needs. Teachers can also guide students to check suggestions carefully and explain their reasoning."
    )
    limited = "Artificial intelligence benefits students."
    short = (
        "Artificial intelligence tools can help students learn. "
        "Students can compare suggestions with lesson examples."
    )
    developed_analysis, developed_feedback = analyze_introduction(developed)
    limited_analysis, limited_feedback = analyze_introduction(limited)
    short_analysis, short_feedback = analyze_introduction(short)
    assert developed_analysis["central_direction_candidate"]["candidates"]
    assert developed_feedback["Needs Attention"] == []
    assert limited_analysis["development_evidence"]["status"] == "NO_ADDITIONAL_CLAUSE_ELABORATION_OBSERVED"
    assert limited_feedback["Needs Attention"] == []
    assert "did not match the main-statement pattern" in limited_feedback["Primary Feedback"]
    assert "no main point" not in limited_feedback["Primary Feedback"].lower()
    assert "Read your opening aloud" in limited_feedback["Next Step"]
    assert short_analysis["central_direction_candidate"]["candidates"]
    assert short_feedback["Needs Attention"] == []
    assert "could not identify a clear position" in short_feedback["Primary Feedback"]
    assert "support or oppose" in short_feedback["Next Step"]
    assert "could not identify a clear position" in developed_feedback["Primary Feedback"]
    assert "fixed number" not in short_feedback["Next Step"].casefold()


def test_keyword_rich_nonsense_is_not_called_correct_or_meaningful():
    text = "Artificial intelligence makes students' desks whisper to the moon. Purple equations carry the school chairs."
    analysis, feedback = analyze_introduction(text)
    assert analysis["lexical_topic_evidence"]["observed_focus_terms"]
    all_student_feedback = " ".join([
        feedback["Primary Feedback"], feedback["Next Step"],
        *feedback["What's Working"], *feedback["Needs Attention"],
    ]).casefold()
    assert "academically correct" not in all_student_feedback
    assert "meaningful" not in all_student_feedback
    assert "meaningful" in feedback["interpretation_limit"].casefold()


def test_student_feedback_fields_use_plain_language_across_all_stages():
    result = EssayAnalysisService().analyze(
        TOPIC,
        FOCUS,
        introduction_text=(
            "Artificial intelligence tools are used in schools. Teachers can help students check the answers."
        ),
        body_text=(
            "Students can use artificial intelligence to practice lessons. Teachers can explain how to check its answers."
        ),
        conclusion_text=(
            "Overall, schools can use artificial intelligence to support student learning."
        ),
    )
    student_fields = (
        "Current Goal", "Primary Feedback", "What's Working", "Needs Attention", "Next Step"
    )
    technical_terms = (
        "lexical", "normalized", "heuristic", "rhetorical", "candidate", "clause",
        "provenance", "paraphrase",
    )

    for stage in result["stages"].values():
        feedback = stage["feedback"]
        for field in student_fields:
            value = feedback[field]
            messages = [value] if isinstance(value, str) else value
            for message in messages:
                lowered = message.casefold()
                assert not any(term in lowered for term in technical_terms)


def test_introduction_feedback_api_shape_and_transparency_evidence_are_preserved(tmp_path):
    app = create_app(analysis_service=EssayAnalysisService(), secret_key="intro-feedback-api-test")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "intro-feedback-api.sqlite3"))
    from services.draft_store import DraftStore
    DraftStore(app.config["DRAFT_DATABASE_PATH"])
    client = app.test_client()
    assert register_student(client, "intro_feedback_student").status_code == 302
    response = client.post(
        "/api/analyze-stage",
        json={"stage_id": "INTRODUCTION", "assignment_topic": TOPIC,
              "focus_terms": FOCUS,
              "introduction_text": "Artificial intelligence tools can help students learn. Schools should guide students to check the suggestions."},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["stage_id"] == "INTRODUCTION"
    assert set(payload["feedback"]) >= {
        "Current Goal", "Primary Feedback", "What's Working", "Needs Attention",
        "Next Step", "Feedback Provenance", "interpretation_limit",
    }
    assert payload["analysis"]["linguistic_observations"]["tokens"]
    assert payload["analysis"]["rule_evidence"]


def test_well_structured_complete_essay_keeps_all_stages_without_intro_warning():
    result = EssayAnalysisService().analyze(
        TOPIC,
        FOCUS,
        introduction_text=(
            "Artificial intelligence tools are becoming part of education. "
            "Schools can use them to give students practice that fits their needs. "
            "Teachers can guide students to check suggestions and explain their reasoning."
        ),
        body_text=(
            "Students can use artificial intelligence tools to practice problems and get explanations. "
            "They can compare a tool's response with class notes and ask a teacher when something is unclear.\n\n"
            "Teachers can set clear rules for technology use. Students can explain when an AI suggestion helped and how they checked it."
        ),
        conclusion_text=(
            "Schools can allow artificial intelligence tools for learning while teaching students to verify responses and explain their reasoning."
        ),
    )
    introduction = result["stages"]["INTRODUCTION"]["feedback"]
    assert "could not identify a clear position" in introduction["Primary Feedback"]
    assert introduction["Needs Attention"] == []
    assert all(result["stages"][stage]["availability"] == "ANALYZED" for stage in result["stage_order"])


def test_body_repetition_and_low_topic_overlap_examples_remain_evidence_bound():
    service = EssayAnalysisService()
    repetitive = service.analyze(
        TOPIC, FOCUS,
        body_text="Students use social media. Students use social media. Students use social media.",
    )["stages"]["BODY"]
    repetition_rule = next(
        event for event in repetitive["analysis"]["rule_evidence"]
        if event["rule_id"] == "BODY.P1.REPETITION.REPEATED_SURFACE_CONTENT_WORDS"
    )
    repetition_feedback = repetitive["feedback"]
    assert repetition_rule["actual_evidence"]
    assert any("Repeating a word can help readers follow" in item for item in repetition_feedback["What's Working"])

    low_overlap = service.analyze(
        TOPIC, FOCUS,
        body_text="At dusk the room became quiet. Bright windows framed the street. People arranged their bags before leaving.",
    )["stages"]["BODY"]
    topic_rule = next(
        event for event in low_overlap["analysis"]["rule_evidence"]
        if event["rule_id"] == "BODY.TOPIC.NO_FOCUS_MATCH"
    )
    assert topic_rule["triggering_condition"]
    assert "off-topic" not in low_overlap["feedback"]["Primary Feedback"].casefold()
