"""Tests for experiment tooling only; these are not human annotation results."""

import ast
import json
from pathlib import Path
import sys

import numpy as np
import pytest

from experiments.semantic_feasibility.annotate import (
    annotate_samples,
    load_samples,
    read_annotation_file,
    save_annotation,
    validate_annotation,
)
from experiments.semantic_feasibility.encoder_experiment import (
    EXPECTED_DIMENSIONS,
    cosine_similarity,
    make_experiment_result,
    split_sentences_for_diagnostic,
)
from experiments.semantic_feasibility.evaluate import (
    classification_metrics,
    reviewer_agreement,
)
from experiments.semantic_feasibility.run_diagnostic_analysis import (
    build_analysis,
    load_ai_diagnostics,
)
from services.nlp_service import NLPService
from services.topic_service import TopicService


EXPERIMENT_DIR = Path(__file__).resolve().parents[1] / "experiments" / "semantic_feasibility"


def sample_annotation(sample_id: str, reviewer: str, label: str = "CLEAR") -> dict:
    return {
        "record_type": "human_annotation",
        "label_provenance": "human_reviewer",
        "sample_id": sample_id,
        "reviewer_id": reviewer,
        "intelligibility_label": label,
        "topic_relevance": "NOT_ASSESSED",
        "figurative_language": "NOT_ASSESSED",
        "confidence": 3,
        "explanation": "A test-only reviewer rationale.",
        "annotated_at_utc": "2026-01-01T00:00:00+00:00",
    }


def test_samples_json_integrity_stable_ids_and_provenance() -> None:
    samples = load_samples(EXPERIMENT_DIR / "samples.json")
    ids = [sample["sample_id"] for sample in samples]
    assert len(ids) == len(set(ids))
    assert all(sample["source"] == "developer_authored" for sample in samples)
    assert all("intelligibility_label" not in sample for sample in samples)
    assert {sample["topic_id"] for sample in samples} == {
        "social_media_attention",
        "school_uniforms",
        "environmental_pollution",
        "reading_habits",
        "renewable_energy",
        "healthy_lifestyles",
    }


def test_ai_diagnostics_match_samples_and_are_not_human_labels() -> None:
    samples = load_samples(EXPERIMENT_DIR / "samples.json")
    diagnostics = load_ai_diagnostics(
        samples, EXPERIMENT_DIR / "ai_diagnostic_annotations.json"
    )
    assert len(diagnostics) == 31
    assert all(
        item["annotation_provenance"] == "AI_GENERATED_DIAGNOSTIC"
        for item in diagnostics.values()
    )
    assert not (EXPERIMENT_DIR / "ai_diagnostic_annotations.json").is_relative_to(
        EXPERIMENT_DIR / "annotations"
    )
    with pytest.raises(ValueError, match="record_type"):
        reviewer_agreement(list(diagnostics.values()))


def test_ai_diagnostic_source_text_must_match_original(tmp_path: Path) -> None:
    samples = load_samples(EXPERIMENT_DIR / "samples.json")
    data = json.loads(
        (EXPERIMENT_DIR / "ai_diagnostic_annotations.json").read_text(encoding="utf-8")
    )
    data["samples"][0]["original_writing"] = "Changed text"
    invalid = tmp_path / "ai_annotations.json"
    invalid.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from source"):
        load_ai_diagnostics(samples, invalid)


def test_one_sample_diagnostic_join_has_actual_service_outputs() -> None:
    samples = load_samples(EXPERIMENT_DIR / "samples.json")
    sample = samples[0]
    ai = load_ai_diagnostics(samples, EXPERIMENT_DIR / "ai_diagnostic_annotations.json")
    encoder_file = json.loads(
        (EXPERIMENT_DIR / "encoder_results.json").read_text(encoding="utf-8")
    )
    encoder_subset = {
        **encoder_file,
        "sample_to_topic": [
            row for row in encoder_file["sample_to_topic"] if row["sample_id"] == sample["sample_id"]
        ],
        "adjacent_statement_pairs": [
            row
            for row in encoder_file["adjacent_statement_pairs"]
            if row["sample_id"] == sample["sample_id"]
        ],
    }
    focus = json.loads(
        (EXPERIMENT_DIR / "diagnostic_focus_terms.json").read_text(encoding="utf-8")
    )
    result = build_analysis(
        [sample],
        encoder_subset,
        focus,
        {sample["sample_id"]: ai[sample["sample_id"]]},
        TopicService(NLPService()),
    )
    assert result["sample_count"] == 1
    row = result["samples"][0]
    assert row["linguistic_observations"]["counts"]["sentence_count"] > 0
    assert row["lexical_observations"]["observed_count"] > 0
    assert row["encoder_observations"]["topic_cosine_similarity"] == encoder_subset["sample_to_topic"][0]["cosine_similarity"]


def test_invalid_sample_file_is_rejected(tmp_path: Path) -> None:
    broken = tmp_path / "samples.json"
    broken.write_text('[{"sample_id":"same"},{"sample_id":"same"}]', encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty IDs"):
        load_samples(broken)


def test_annotation_valid_and_invalid_labels() -> None:
    valid = sample_annotation("SM-01", "reviewer_a")
    validate_annotation(valid)
    invalid = {**valid, "intelligibility_label": "LIKELY_CLEAR"}
    with pytest.raises(ValueError, match="Invalid intelligibility"):
        validate_annotation(invalid)
    invalid_source = {**valid, "label_provenance": "developer_expectation"}
    with pytest.raises(ValueError, match="human_reviewer provenance"):
        validate_annotation(invalid_source)


def test_annotation_persistence_and_duplicate_protection(tmp_path: Path) -> None:
    path = tmp_path / "annotations" / "reviewer_a.jsonl"
    annotation = sample_annotation("SM-01", "reviewer_a", "UNCLEAR")
    save_annotation(path, annotation)
    assert read_annotation_file(path) == [annotation]
    with pytest.raises(ValueError, match="already annotated"):
        save_annotation(path, annotation)


def test_malformed_annotation_file_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "annotations.jsonl"
    path.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid annotation"):
        read_annotation_file(path)


def test_incomplete_annotation_cannot_be_saved(tmp_path: Path) -> None:
    annotation = sample_annotation("SM-01", "reviewer_a")
    annotation["explanation"] = " "
    with pytest.raises(ValueError, match="explanation is required"):
        save_annotation(tmp_path / "annotations.jsonl", annotation)


def test_annotation_session_saves_and_resumes(tmp_path: Path) -> None:
    samples = load_samples(EXPERIMENT_DIR / "samples.json")[:2]
    path = tmp_path / "reviewer_a.jsonl"
    prompts = iter(["CLEAR", "RELEVANT", "NO", "4", "The claim is interpretable.", "Q"])
    written = annotate_samples(
        samples,
        "reviewer_a",
        path,
        input_fn=lambda _prompt: next(prompts),
        output_fn=lambda _line: None,
    )
    assert written == 1
    records = read_annotation_file(path)
    assert records[0]["sample_id"] == "SM-01"
    assert records[0]["label_provenance"] == "human_reviewer"

    second_session_output: list[str] = []
    resumed = annotate_samples(
        samples,
        "reviewer_a",
        path,
        input_fn=lambda _prompt: "Q",
        output_fn=second_session_output.append,
    )
    assert resumed == 0
    assert any("1 completed; 1 remaining" in line for line in second_session_output)
    assert any("Sample SM-02" in line for line in second_session_output)


def test_reviewers_do_not_see_each_others_saved_labels(tmp_path: Path) -> None:
    samples = load_samples(EXPERIMENT_DIR / "samples.json")[:2]
    path = tmp_path / "combined.jsonl"
    save_annotation(path, sample_annotation("SM-01", "reviewer_a", "CLEAR"))
    save_annotation(path, sample_annotation("SM-02", "reviewer_b", "NONSENSICAL"))
    output: list[str] = []
    annotate_samples(
        samples,
        "reviewer_a",
        path,
        input_fn=lambda _prompt: "Q",
        output_fn=output.append,
    )
    assert "NONSENSICAL" not in "\n".join(output)
    assert any("Sample SM-02" in line for line in output)


def test_agreement_requires_overlapping_independent_reviews() -> None:
    assert reviewer_agreement([])["status"] == "insufficient_independent_annotations"
    annotations = [
        sample_annotation("SM-01", "reviewer_a", "CLEAR"),
        sample_annotation("SM-01", "reviewer_b", "UNCLEAR"),
    ]
    agreement = reviewer_agreement(annotations)
    assert agreement["status"] == "calculated"
    assert agreement["pairwise_comparisons"][0]["shared_samples"] == 1
    assert agreement["pairwise_comparisons"][0]["observed_agreement"] == 0.0


def test_metrics_refuse_unlabeled_examples_or_no_predictions() -> None:
    prediction = {
        "record_type": "model_prediction",
        "prediction_provenance": "model_output",
        "sample_id": "SM-01",
        "intelligibility_label": "CLEAR",
    }
    with pytest.raises(ValueError, match="No human reference labels"):
        classification_metrics([], [prediction], "reviewer_a")
    with pytest.raises(ValueError, match="No model predictions"):
        classification_metrics([sample_annotation("SM-01", "reviewer_a")], [], "reviewer_a")


def test_metrics_require_matching_human_and_model_sample_ids() -> None:
    reference = sample_annotation("SM-01", "reviewer_a", "CLEAR")
    prediction = {
        "record_type": "model_prediction",
        "prediction_provenance": "model_output",
        "sample_id": "SM-02",
        "intelligibility_label": "CLEAR",
    }
    with pytest.raises(ValueError, match="sample IDs must match"):
        classification_metrics([reference], [prediction], "reviewer_a")


def test_metrics_calculate_from_matched_human_and_model_records() -> None:
    references = [
        sample_annotation("SM-01", "reviewer_a", "CLEAR"),
        sample_annotation("SM-02", "reviewer_a", "NONSENSICAL"),
    ]
    predictions = [
        {
            "record_type": "model_prediction",
            "prediction_provenance": "model_output",
            "sample_id": sample_id,
            "intelligibility_label": prediction,
        }
        for sample_id, prediction in (("SM-01", "CLEAR"), ("SM-02", "CLEAR"))
    ]
    metrics = classification_metrics(references, predictions, "reviewer_a")
    assert metrics["status"] == "calculated"
    assert metrics["sample_count"] == 2
    assert metrics["confusion_matrix_rows_reference_columns_prediction"]["NONSENSICAL"]["CLEAR"] == 1
    assert metrics["false_positive_false_negative_sample_ids"]["CLEAR"]["false_positive_sample_ids"] == ["SM-02"]


def test_encoder_similarity_helpers_handle_empty_malformed_and_cosine() -> None:
    assert split_sentences_for_diagnostic("") == []
    assert split_sentences_for_diagnostic("  \n ") == []
    assert cosine_similarity(np.array([1.0, 0.0]), np.array([0.0, 1.0])) == pytest.approx(0.0)
    with pytest.raises(ValueError, match="zero vector"):
        cosine_similarity(np.zeros(2), np.ones(2))


def test_encoder_output_shape_and_finite_values_are_checked() -> None:
    samples = [{
        "sample_id": "X-01",
        "topic_id": "test_topic",
        "topic": "Reading habits",
        "text": "Students read.",
    }]
    class DummyModel:
        max_seq_length = 256

    vectors = np.zeros((2, EXPECTED_DIMENSIONS), dtype=np.float32)
    vectors[:, 0] = 1.0
    report = make_experiment_result(
        samples,
        vectors,
        0.02,
        0.1,
        DummyModel(),
        "cpu",
        {"sentence_transformers_version": "test", "transformers_version": "test", "torch_version": "test"},
    )
    assert report["measurement"]["embedding_shape"] == [2, EXPECTED_DIMENSIONS]
    assert report["measurement"]["all_embedding_values_finite"] is True
    assert report["sample_to_topic"][0]["cosine_similarity"] == pytest.approx(1.0)
    with pytest.raises(ValueError, match="Unexpected embedding shape"):
        make_experiment_result(
            samples,
            np.ones((1, EXPECTED_DIMENSIONS)),
            0.02,
            0.1,
            DummyModel(),
            "cpu",
            {},
        )
    vectors[0, 0] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        make_experiment_result(samples, vectors, 0, 0, DummyModel(), "cpu", {})


def test_experiment_encoder_is_not_imported_by_production_services() -> None:
    for path in (EXPERIMENT_DIR / "annotate.py", EXPERIMENT_DIR / "evaluate.py", EXPERIMENT_DIR / "encoder_experiment.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        assert not any(name.startswith("services.") for name in imports)
    assert "sentence_transformers" not in sys.modules
