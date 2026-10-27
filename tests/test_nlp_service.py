"""Tests for actual linguistic extraction using en_core_web_sm."""

from unittest.mock import Mock

import pytest

from services.nlp_service import NLPService


@pytest.fixture(scope="module")
def service() -> NLPService:
    return NLPService()


def test_sentence_segmentation_and_multiple_paragraphs(service: NLPService) -> None:
    result = service.analyze("Students read. They learn.\n\nTeachers help.")
    assert [sentence["text"] for sentence in result["sentences"]] == [
        "Students read.",
        "They learn.",
        "Teachers help.",
    ]
    assert result["counts"]["sentence_count"] == 3


def test_alphabetic_word_count_is_separate_from_token_count(service: NLPService) -> None:
    result = service.analyze("Well-written essays, often!")
    assert result["counts"]["alphabetic_word_count"] == 4
    assert result["counts"]["token_count"] > result["counts"]["alphabetic_word_count"]


def test_tokenization_includes_punctuation(service: NLPService) -> None:
    result = service.analyze("Hello, world!")
    assert [token["text"] for token in result["tokens"]] == ["Hello", ",", "world", "!"]


def test_lemmatization_uses_spacy_lemmas(service: NLPService) -> None:
    result = service.analyze("Students were studying.")
    by_text = {token["text"]: token["lemma"] for token in result["tokens"]}
    assert by_text["Students"] == "student"
    assert by_text["studying"] == "study"


def test_pos_tags_are_populated(service: NLPService) -> None:
    result = service.analyze("Students study carefully.")
    by_text = {token["text"]: token for token in result["tokens"]}
    assert by_text["Students"]["pos"] == "NOUN"
    assert by_text["study"]["pos"] == "VERB"
    assert by_text["carefully"]["pos"] == "ADV"
    assert all(token["tag"] for token in result["tokens"])


def test_dependencies_are_real_parser_relations(service: NLPService) -> None:
    result = service.analyze("Social media affects students' concentration.")
    sentence = result["sentences"][0]
    assert sentence["subjects"]
    assert any(item["text"] == "affects" for item in sentence["dependencies"])
    assert sentence["objects_or_complements"]
    assert all(item["dependency"] for item in sentence["dependencies"])


def test_noun_phrases_preserve_text_and_offsets(service: NLPService) -> None:
    text = "Social media affects students' concentration."
    result = service.analyze(text)
    assert result["noun_phrases"]
    for phrase in result["noun_phrases"]:
        assert text[phrase["start"] : phrase["end"]] == phrase["text"]


def test_token_offsets_preserve_original_text(service: NLPService) -> None:
    text = "A student writes clearly."
    result = service.analyze(text)
    for token in result["tokens"]:
        assert text[token["start"] : token["end"]] == token["text"]
    sentence = result["sentences"][0]
    assert text[sentence["start"] : sentence["end"]] == sentence["text"]


@pytest.mark.parametrize("text", ["", "   \n\t"])
def test_empty_and_whitespace_input(text: str, service: NLPService) -> None:
    result = service.analyze(text)
    assert result["counts"] == {
        "alphabetic_word_count": 0,
        "sentence_count": 0,
        "token_count": 0,
    }
    assert result["sentences"] == []
    assert result["noun_phrases"] == []


def test_unexpected_punctuation_does_not_crash(service: NLPService) -> None:
    result = service.analyze("??? ... !!!")
    assert result["counts"]["token_count"] > 0
    assert result["counts"]["alphabetic_word_count"] == 0


def test_repeated_analysis_is_consistent(service: NLPService) -> None:
    text = "The student writes essays."
    assert service.analyze(text) == service.analyze(text)


def test_one_shared_doc_is_used_for_one_analysis(service: NLPService) -> None:
    original_pipeline = service.nlp
    counting_pipeline = Mock(wraps=original_pipeline)
    service.nlp = counting_pipeline
    try:
        result = service.analyze("Students read books.")
        assert result["sentences"]
        counting_pipeline.assert_called_once_with("Students read books.")
    finally:
        service.nlp = original_pipeline


def test_meaningful_and_nonsensical_examples_are_linguistic_only(service: NLPService) -> None:
    meaningful = service.analyze(
        "Late-night social media use affects students' concentration because they get insufficient sleep."
    )
    nonsensical = service.analyze(
        "Social media makes classroom attention drink invisible clocks while students' sleep dances through digital umbrellas."
    )
    assert meaningful["counts"]["alphabetic_word_count"] > 0
    assert nonsensical["counts"]["alphabetic_word_count"] > 0
    assert meaningful["sentences"][0]["dependencies"]
    assert nonsensical["sentences"][0]["dependencies"]
    assert "meaning_score" not in meaningful
    assert "meaning_score" not in nonsensical


def test_non_string_input_has_clear_error(service: NLPService) -> None:
    with pytest.raises(TypeError, match="text must be a string"):
        service.analyze(None)  # type: ignore[arg-type]
