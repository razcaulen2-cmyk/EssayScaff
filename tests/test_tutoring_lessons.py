"""Checks the locally authored tutoring lesson knowledge base."""

from services.tutoring_lessons import load_introduction_lesson


def test_introduction_lesson_has_structured_model_practice_reflect_content():
    lesson = load_introduction_lesson()

    assert lesson["lesson_id"] == "INTRO-LESSON-001"
    assert lesson["intended_stage"] == "INTRODUCTION"
    assert lesson["title"] == "Understanding the Assignment and Choosing a Position"
    assert {item["name"] for item in lesson["source_framework"]} == {
        "IES Teaching Secondary Students to Write Effectively",
        "Self-Regulated Strategy Development (SRSD)",
    }
    assert len(lesson["learning_objectives"]) >= 2

    model = lesson["model"]
    assert model["teacher_authored_example"]["assignment"]
    assert model["teacher_authored_example"]["topic"]
    assert model["teacher_authored_example"]["position_sentence"]
    assert "position" in " ".join(model["instruction"]).lower()

    practice_questions = lesson["practice"]["questions"]
    assert len(practice_questions) >= 2
    for question in practice_questions:
        option_ids = {option["option_id"] for option in question["options"]}
        assert question["correct_option_id"] in option_ids
        assert question["correct_explanation"]
        assert all(option["feedback"] for option in question["options"])

    reflection_questions = lesson["reflect"]["questions"]
    assert {question["prompt"] for question in reflection_questions} == {
        "Does my Introduction discuss the assignment question?",
        "Can readers identify my position?",
    }
    assert all(len(question["options"]) == 2 for question in reflection_questions)
    assert any("not establish writing mastery" in item for item in lesson["completion_conditions"])
    assert "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED" in lesson["associated_rule_ids"]
