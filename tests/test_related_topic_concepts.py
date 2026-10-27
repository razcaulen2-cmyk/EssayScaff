"""Curated associations remain lexical, scoped and independent of writing decisions."""

from copy import deepcopy
import json
from unittest.mock import Mock

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from services.draft_store import DraftStore
from services.essay_analysis_service import EssayAnalysisService
from services.nlp_service import NLPService
from services.related_topic_concept_service import DEFAULT_RESOURCE_PATH, RelatedTopicConceptService
from services.topic_service import TopicService
from tests.auth_helpers import register_student
from tests.test_nlp_transparency import (
    PLASTICS_TOPIC, PLASTICS_FOCUS, PLASTICS_INTRODUCTION, PLASTICS_BODY, PLASTICS_CONCLUSION,
)


@pytest.fixture(scope="module")
def nlp():
    return NLPService()


@pytest.fixture(scope="module")
def topic(nlp):
    return TopicService(nlp)


def analyze(topic, text, focus=None, assignment=PLASTICS_TOPIC):
    return topic.analyze(text, assignment, ["environment"] if focus is None else focus, include_wordnet=False)


def test_resource_is_small_valid_and_explicit():
    service = RelatedTopicConceptService()
    assert service.resource["status"] == "AVAILABLE"
    assert service.resource["source"] == "content/topic_concept_relations.json"
    assert service.resource["configuration_version"] == "1.0"
    assert len(service.resource["sha256"]) == 64
    assert {item["focus_concept"] for item in service.relationships} == {"environment"}
    assert {item["related_concept"] for item in service.relationships} == {
        "river", "animal", "forest", "habitat", "ecosystem", "pollution",
    }
    assert len(service.relationships) == 6


@pytest.mark.parametrize("text, expected", [
    ("Rivers, animals, people.", ["river", "animal"]),
    ("Plastic pollution can harm rivers and animals.", ["pollution", "river", "animal"]),
    (PLASTICS_INTRODUCTION, ["river", "animal"]),
    ("People enjoy basketball.", []),
    ("Rivers, rivers! Animals.", ["river", "river", "animal"]),
    ("No rivers or animals are mentioned.", ["river", "animal"]),
    ("FORESTS, habitats, ecosystems; pollution.", ["forest", "habitat", "ecosystem", "pollution"]),
    ("Riverbanks, riversides, animalistic, forestry, impollution.", []),
    ("People, thing, place, good.", []),
    ("", []), (" \n\t ", []), ("!!!", []),
    ("🌍 Rivers\r\n\r\nAnimals live nearby.", ["river", "animal"]),
])
def test_allowed_lemma_mentions_with_exact_original_spans(topic, text, expected):
    result = analyze(topic, text)
    related = result["related_topic_concept_evidence"]
    assert related["execution_status"] == "EXECUTED"
    assert related["reason"] == ("MATCHES_OBSERVED" if expected else "NO_MATCHES")
    assert [item["normalized_student_word"] for item in related["evidence"]] == expected
    assert related["summary"]["unique_related_concepts_observed"] == len(set(expected))
    assert related["summary"]["total_related_concept_occurrences"] == len(expected)
    assert related["summary"]["relationship_record_count"] == len(expected)
    assert related["summary"]["teacher_focus_concepts_with_related_evidence"] == (["environment"] if expected else [])
    assert related["informational_only"] is True and related["affects_rules_or_feedback"] is False
    assert "Negation" in related["limitation"] and "valid argument" in related["limitation"]
    assert result["focus_coverage"]["observed_unique_focus_terms"] == 0
    for item in related["evidence"]:
        assert text[item["start"]:item["end"]] == item["student_word"]
        token = next(token for token in result["linguistic_analysis"]["tokens"] if token["index"] == item["token_index"])
        assert token["lemma"] == item["spacy_lemma"]
        if item["normalization_method"] == "spacy_lemma":
            assert token["lemma"].casefold() == item["normalized_student_word"]
        else:
            relationship = next(record for record in related["approved_relationships"] if record["id"] == item["relationship_id"])
            assert token["text"].casefold() in relationship["surface_forms"]
        sentence = result["linguistic_analysis"]["sentences"][item["sentence_index"]]
        assert sentence["start"] <= item["start"] < item["end"] <= sentence["end"]
        assert item["relationship_source"] == related["resource"]["source"]
        assert item["relationship_id"].startswith("environment.")
        assert item["configuration_version"] == "1.0"
        assert item["match_status"] == "LEXICAL_RELATION_OBSERVED"
    assert len({(item["start"], item["end"], item["relationship_id"]) for item in related["evidence"]}) == len(expected)


@pytest.mark.parametrize("focus", [
    ["school uniforms"], ["natural environment"], ["environmental protection"],
    ["environment river"], ["my environment"], ["unknown"], [],
])
def test_complete_teacher_focus_scope_not_substrings_or_topic_words(topic, focus):
    result = analyze(topic, "Rivers and animals.", focus, assignment="Environment and school uniforms")
    related = result["related_topic_concept_evidence"]
    assert related["execution_status"] == "NOT_APPLICABLE"
    assert related["evidence"] == []
    assert related["approved_relationships"] == []


def test_focus_case_dedup_and_sequential_assignment_isolation(topic):
    first = analyze(topic, "Rivers, rivers! Animals.", ["ENVIRONMENT", "environment", "Environments"])
    related = deepcopy(first["related_topic_concept_evidence"])
    assert len(related["evidence"]) == 3
    assert len(related["active_focus_concepts"]) == 1
    assert related["summary"]["teacher_focus_terms_with_related_evidence"] == ["ENVIRONMENT"]
    second = analyze(topic, "Rivers and animals.", ["school uniforms"], "School uniforms")
    assert second["related_topic_concept_evidence"]["evidence"] == []
    assert analyze(topic, "Animals.")["related_topic_concept_evidence"]["summary"]["total_related_concept_occurrences"] == 1
    assert first["related_topic_concept_evidence"] == related  # later calls do not mutate earlier evidence


def test_direct_lemma_and_related_are_three_separate_channels(topic):
    result = analyze(topic, "Environment. Rivers and animals.", ["environment", "river", "animals"])
    focuses = {item["term"]: item for item in result["confirmed_lexical_observations"]}
    assert len(focuses["environment"]["direct_matches"]) == 1
    assert focuses["environment"]["normalized_matches"] == []
    assert len(focuses["river"]["normalized_matches"]) == 1
    assert len(focuses["animals"]["direct_matches"]) == 1
    assert result["focus_coverage"]["observed_unique_focus_terms"] == 3
    assert len(result["related_topic_concept_evidence"]["evidence"]) == 2
    assert result["wordnet"]["status"] == "disabled"


def write_config(tmp_path, config):
    path = tmp_path / "relations.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


@pytest.mark.parametrize("broken", [
    None, [], {}, {"schema_version": True},
    {"relationships": "not a list"}, {"configuration_version": ""},
    {"schema_version": 2}, {"provenance": "wordnet_generated"},
])
def test_invalid_resource_root_fails_closed(tmp_path, broken, nlp):
    config = json.loads(DEFAULT_RESOURCE_PATH.read_text(encoding="utf-8"))
    if isinstance(broken, dict):
        config.update(broken)
        if broken == {}:
            config = {}
    else:
        config = broken
    service = RelatedTopicConceptService(write_config(tmp_path, config))
    result = service.match({"focus_source": "teacher_provided", "focus_terms": [{"term": "environment", "normalized_form": "environment"}]}, nlp.analyze("Rivers."))
    assert result["execution_status"] == "CONFIGURATION_INVALID"
    assert result["evidence"] == []


@pytest.mark.parametrize("change", [
    {"focus_concept": "Environment"}, {"related_concept": "river bank"},
    {"relationship_label": ""}, {"id": None}, {"relationship_type": ["automatic"]},
    {"extra": "unsupported"}, {"focus_concept": "river"},
])
def test_invalid_relationship_record_rejects_entire_configuration(tmp_path, change):
    config = json.loads(DEFAULT_RESOURCE_PATH.read_text(encoding="utf-8"))
    config["relationships"][0].update(change)
    service = RelatedTopicConceptService(write_config(tmp_path, config))
    assert service.resource["status"] == "CONFIGURATION_INVALID"
    assert service.relationships == []


@pytest.mark.parametrize("duplicate", ["id", "pair", "json_field"])
def test_duplicate_configuration_is_not_silently_accepted(tmp_path, duplicate):
    config = json.loads(DEFAULT_RESOURCE_PATH.read_text(encoding="utf-8"))
    if duplicate == "json_field":
        path = tmp_path / "relations.json"
        path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    else:
        record = dict(config["relationships"][0])
        if duplicate == "id":
            record["related_concept"] = "lake"
        else:
            record["id"] = "another.id"
        config["relationships"].append(record)
        path = write_config(tmp_path, config)
    assert RelatedTopicConceptService(path).resource["status"] == "CONFIGURATION_INVALID"


def test_resource_missing_is_distinct_from_successful_no_matches(tmp_path, nlp):
    topic = TopicService(nlp)
    topic.related_concepts = RelatedTopicConceptService(tmp_path / "missing.json")
    missing = analyze(topic, "Rivers.")["related_topic_concept_evidence"]
    assert missing["execution_status"] == "RESOURCE_UNAVAILABLE" and missing["evidence"] == []
    topic.related_concepts = RelatedTopicConceptService()
    empty = analyze(topic, "People enjoy basketball.")["related_topic_concept_evidence"]
    assert empty["execution_status"] == "EXECUTED" and empty["reason"] == "NO_MATCHES"


@pytest.mark.parametrize("raw", ["not json", "{", "[]", "\ufffd"])
def test_malformed_json_returns_accurate_status(tmp_path, raw):
    path = tmp_path / "bad.json"
    path.write_text(raw, encoding="utf-8")
    assert RelatedTopicConceptService(path).resource["status"] == "CONFIGURATION_INVALID"


def test_duplicate_input_records_do_not_duplicate_occurrence_evidence(nlp):
    service = RelatedTopicConceptService()
    linguistic = nlp.analyze("Rivers, rivers! Animals.")
    linguistic["tokens"] += deepcopy(linguistic["tokens"])
    context = {"focus_source": "teacher_provided", "focus_terms": [{"term": "environment", "normalized_form": "environment"}] * 2}
    original = deepcopy((context, linguistic))
    result = service.match(context, linguistic)
    assert result["summary"]["total_related_concept_occurrences"] == 3
    assert result["summary"]["unique_related_concepts_observed"] == 2
    assert (context, linguistic) == original


@pytest.mark.parametrize("forms", ["rivers", [], ["river", "river"], ["RIVER"], ["river bank"], ["rivers"], [None]])
def test_invalid_approved_surface_forms_are_rejected(tmp_path, forms):
    config = json.loads(DEFAULT_RESOURCE_PATH.read_text(encoding="utf-8"))
    config["relationships"][0]["surface_forms"] = forms
    assert RelatedTopicConceptService(write_config(tmp_path, config)).resource["status"] == "CONFIGURATION_INVALID"


def test_model_lemma_and_explicit_form_normalization_remain_distinguishable():
    context = {"focus_source": "teacher_provided", "focus_terms": [{"term": "environment", "normalized_form": "environment"}]}
    linguistic = {"tokens": [{"text": "FORESTS", "lemma": "FORESTS", "index": 0, "start": 0, "end": 7, "is_alpha": True}], "sentences": []}
    result = RelatedTopicConceptService().match(context, linguistic)
    record = result["evidence"][0]
    assert record["normalization_method"] == "configured_surface_form"
    assert record["spacy_lemma"] == "FORESTS"
    assert record["normalized_student_word"] == "forest"
    assert record["sentence_index"] is None  # missing metadata is not invented
    assert linguistic["tokens"][0]["lemma"] == "FORESTS"


def test_empty_valid_configuration_and_invalid_unicode_have_distinct_resource_status(tmp_path):
    config = json.loads(DEFAULT_RESOURCE_PATH.read_text(encoding="utf-8"))
    config["relationships"] = []
    service = RelatedTopicConceptService(write_config(tmp_path, config))
    assert service.resource["status"] == "AVAILABLE"
    assert service.match({"focus_source": "teacher_provided", "focus_terms": [{"term": "environment", "normalized_form": "environment"}]}, {"tokens": []})["execution_status"] == "NOT_APPLICABLE"
    path = tmp_path / "bad-encoding.json"
    path.write_bytes(b"\xff\xfe")
    assert RelatedTopicConceptService(path).resource["status"] == "CONFIGURATION_INVALID"


def test_explicit_multiword_mapping_and_shared_occurrence_counts_are_supported(tmp_path, nlp):
    config = json.loads(DEFAULT_RESOURCE_PATH.read_text(encoding="utf-8"))
    config["relationships"].append({**config["relationships"][0], "focus_concept": "natural environment", "id": "natural_environment.river.v1"})
    service = RelatedTopicConceptService(write_config(tmp_path, config))
    context = {"focus_source": "teacher_provided", "focus_terms": [{"term": word, "normalized_form": word} for word in ["environment", "natural environment"]]}
    result = service.match(context, nlp.analyze("Rivers."))
    assert len(result["evidence"]) == 2  # two explicitly configured relationships
    assert result["summary"]["total_related_concept_occurrences"] == 1
    assert result["summary"]["unique_related_concepts_observed"] == 1


def test_related_matching_adds_no_spacy_or_wordnet_calls(nlp, monkeypatch):
    language = Mock(wraps=nlp.nlp)
    monkeypatch.setattr(nlp, "nlp", language)
    def forbidden(*args, **kwargs):
        raise AssertionError("Related Introduction evidence must not call WordNet")
    monkeypatch.setattr("services.topic_service.wordnet.synsets", forbidden)
    result = TopicService(nlp).analyze(PLASTICS_INTRODUCTION, PLASTICS_TOPIC, PLASTICS_FOCUS, include_wordnet=False)
    assert language.call_count == len(PLASTICS_FOCUS) + 1
    assert len(result["related_topic_concept_evidence"]["evidence"]) == 2


@pytest.mark.parametrize("stage, fields", [
    ("INTRODUCTION", {"introduction_text": PLASTICS_INTRODUCTION}),
    ("BODY", {"body_text": PLASTICS_BODY}),
    ("BODY", {"introduction_text": PLASTICS_INTRODUCTION, "body_text": PLASTICS_BODY}),
    ("CONCLUSION", {"conclusion_text": PLASTICS_CONCLUSION}),
    ("CONCLUSION", {"introduction_text": PLASTICS_INTRODUCTION, "body_text": PLASTICS_BODY, "conclusion_text": PLASTICS_CONCLUSION}),
    ("INTRODUCTION", {"introduction_text": "Rivers, animals, people."}),
])
def test_all_stage_decisions_and_feedback_are_independent_of_curated_evidence(tmp_path, nlp, stage, fields):
    coordinator = EssayAnalysisService(nlp)
    current = coordinator.analyze(PLASTICS_TOPIC, PLASTICS_FOCUS, **fields, include_research_trace=True)
    coordinator.topic_service.related_concepts = RelatedTopicConceptService(tmp_path / "unavailable.json")
    unavailable = coordinator.analyze(PLASTICS_TOPIC, PLASTICS_FOCUS, **fields, include_research_trace=True)
    for supplied in current["stages"]:
        assert current["stages"][supplied]["analysis"] == unavailable["stages"][supplied]["analysis"]
        assert current["stages"][supplied]["feedback"] == unavailable["stages"][supplied]["feedback"]
        assert current["research_trace"]["stages"][supplied].get("feedback_decisions") == unavailable["research_trace"]["stages"][supplied].get("feedback_decisions")
    selected = current["stages"][stage]
    assert selected["related_topic_concept_evidence"]["execution_status"] == "EXECUTED"
    assert "related_topic_concept_evidence" not in selected["analysis"]
    if fields.get("introduction_text") == "Rivers, animals, people.":
        assert selected["analysis"]["central_direction_candidate"]["candidates"] == []
        assert selected["analysis"]["lexical_topic_evidence"]["observed_unique_focus_terms"] == 0
        assert selected["feedback"]["Primary Feedback"] != ""  # existing structural guidance, not approval


def test_api_serializes_related_evidence_with_or_without_optional_trace(tmp_path, nlp):
    app = create_app(EssayAnalysisService(nlp), secret_key="isolated-related-evidence")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "related.sqlite3"))
    client = app.test_client()
    assert register_student(client, "related_student").status_code == 302
    for trace in (False, True):
        response = client.post("/api/analyze-stage", json={"stage_id": "INTRODUCTION", "assignment_topic": PLASTICS_TOPIC, "focus_terms": PLASTICS_FOCUS, "introduction_text": PLASTICS_INTRODUCTION, "include_transparency_trace": trace})
        assert response.status_code == 200
        result = response.get_json()
        related = result["related_topic_concept_evidence"]
        assert [(item["student_word"], item["start"], item["end"]) for item in related["evidence"]] == [("rivers", 134, 140), ("animals", 150, 157)]
        assert result["analysis"]["lexical_topic_evidence"]["observed_unique_focus_terms"] == 3
        assert len(result["analysis"]["lexical_topic_evidence"]["matches"]) == 4


def test_saved_assignment_context_overrides_client_claimed_environment_focus(tmp_path, nlp):
    app = create_app(EssayAnalysisService(nlp), secret_key="related-assignment-scope")
    app.config.update(TESTING=True, DRAFT_DATABASE_PATH=str(tmp_path / "scope.sqlite3"))
    store = DraftStore(app.config["DRAFT_DATABASE_PATH"])
    teacher = store.create_teacher_user("scope_teacher", generate_password_hash("teacher-password-1"))
    classroom = store.create_classroom(teacher["user_id"], "Writing", "English", "A")
    assignment = store.create_assignment(teacher["user_id"], classroom["classroom_id"], "Uniforms", "School uniforms", "Write your view.", "school uniforms")
    client = app.test_client()
    assert register_student(client, "scope_student").status_code == 302
    assert client.post("/api/classroom-enrollments", json={"enrollment_code": classroom["enrollment_code"]}).status_code == 200
    result = client.post("/api/analyze-stage", json={"stage_id": "INTRODUCTION", "assignment_id": assignment["assignment_id"], "assignment_topic": PLASTICS_TOPIC, "focus_terms": ["environment"], "introduction_text": "Rivers and animals."}).get_json()
    assert result["analysis"]["assignment_topic"] == "School uniforms"
    assert result["related_topic_concept_evidence"]["execution_status"] == "NOT_APPLICABLE"
    assert result["related_topic_concept_evidence"]["evidence"] == []
