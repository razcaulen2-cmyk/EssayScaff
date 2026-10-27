"""Safeguarded utilities for human annotation counts, agreement, and later metrics."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

try:
    from .annotate import INTELLIGIBILITY_LABELS, read_annotation_file, validate_annotation
except ImportError:  # Support direct execution with python evaluate.py.
    from annotate import INTELLIGIBILITY_LABELS, read_annotation_file, validate_annotation


def load_prediction_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"Prediction file does not exist: {path}")
    predictions = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            item = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid prediction at {path}:{line_number}") from error
        if (
            not isinstance(item, dict)
            or item.get("record_type") != "model_prediction"
            or item.get("prediction_provenance") != "model_output"
            or not isinstance(item.get("sample_id"), str)
            or item.get("intelligibility_label") not in INTELLIGIBILITY_LABELS
        ):
            raise ValueError(f"Invalid model prediction at {path}:{line_number}")
        predictions.append(item)
    return predictions


def class_counts(annotations: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(item["intelligibility_label"] for item in annotations)
    return {label: counts.get(label, 0) for label in sorted(INTELLIGIBILITY_LABELS)}


def reviewer_agreement(annotations: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate pairwise observed agreement and Cohen's kappa on shared samples."""
    by_reviewer: dict[str, dict[str, str]] = defaultdict(dict)
    for item in annotations:
        validate_annotation(item)
        reviewer = item["reviewer_id"]
        sample_id = item["sample_id"]
        if sample_id in by_reviewer[reviewer]:
            raise ValueError(f"Duplicate annotation for {reviewer}/{sample_id}")
        by_reviewer[reviewer][sample_id] = item["intelligibility_label"]

    reviewers = sorted(by_reviewer)
    comparisons = []
    for left_index, reviewer_a in enumerate(reviewers):
        for reviewer_b in reviewers[left_index + 1 :]:
            common_ids = sorted(by_reviewer[reviewer_a].keys() & by_reviewer[reviewer_b].keys())
            if not common_ids:
                continue
            labels_a = [by_reviewer[reviewer_a][sample_id] for sample_id in common_ids]
            labels_b = [by_reviewer[reviewer_b][sample_id] for sample_id in common_ids]
            observed = sum(a == b for a, b in zip(labels_a, labels_b)) / len(common_ids)
            counts_a = Counter(labels_a)
            counts_b = Counter(labels_b)
            expected = sum(
                counts_a[label] * counts_b[label] for label in INTELLIGIBILITY_LABELS
            ) / (len(common_ids) ** 2)
            kappa = (observed - expected) / (1 - expected) if expected < 1 else None
            comparisons.append(
                {
                    "reviewer_a": reviewer_a,
                    "reviewer_b": reviewer_b,
                    "shared_samples": len(common_ids),
                    "observed_agreement": observed,
                    "cohen_kappa": kappa,
                }
            )

    return {
        "status": "calculated" if comparisons else "insufficient_independent_annotations",
        "reviewer_count": len(reviewers),
        "pairwise_comparisons": comparisons,
        "note": (
            "Agreement is descriptive for these reviewers and samples; it does not "
            "establish that the rubric or labels are valid."
        ),
    }


def classification_metrics(
    annotations: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    reference_reviewer_id: str,
) -> dict[str, Any]:
    """Compare actual model prediction records with one named human reviewer."""
    if not reference_reviewer_id:
        raise ValueError("Choose a reference reviewer explicitly")
    references: dict[str, str] = {}
    for item in annotations:
        validate_annotation(item)
        if item["reviewer_id"] != reference_reviewer_id:
            continue
        if item["sample_id"] in references:
            raise ValueError(f"Duplicate reference label for {item['sample_id']}")
        references[item["sample_id"]] = item["intelligibility_label"]

    predicted: dict[str, str] = {}
    for item in predictions:
        if (
            item.get("record_type") != "model_prediction"
            or item.get("prediction_provenance") != "model_output"
            or item.get("intelligibility_label") not in INTELLIGIBILITY_LABELS
        ):
            raise ValueError("Predictions must be explicit model_output records")
        sample_id = item.get("sample_id")
        if not isinstance(sample_id, str) or sample_id in predicted:
            raise ValueError("Each prediction needs a unique sample_id")
        predicted[sample_id] = item["intelligibility_label"]

    if not references:
        raise ValueError("No human reference labels for the selected reviewer")
    if not predicted:
        raise ValueError("No model predictions supplied; classification metrics are not valid")
    if references.keys() != predicted.keys():
        missing_predictions = sorted(references.keys() - predicted.keys())
        extra_predictions = sorted(predicted.keys() - references.keys())
        raise ValueError(
            f"Reference/prediction sample IDs must match; "
            f"missing predictions={missing_predictions}, extra predictions={extra_predictions}"
        )

    confusion = {
        actual: {
            guess: sum(
                true_label == actual and predicted[sample_id] == guess
                for sample_id, true_label in references.items()
            )
            for guess in sorted(INTELLIGIBILITY_LABELS)
        }
        for actual in sorted(INTELLIGIBILITY_LABELS)
    }
    per_label = {}
    error_analysis = {}
    for label in sorted(INTELLIGIBILITY_LABELS):
        true_positive = confusion[label][label]
        false_positive = sum(confusion[actual][label] for actual in confusion if actual != label)
        false_negative = sum(confusion[label][guess] for guess in confusion if guess != label)
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_label[label] = {"precision": precision, "recall": recall, "f1": f1}
        error_analysis[label] = {
            "false_positive_sample_ids": [
                sample_id
                for sample_id, actual in references.items()
                if actual != label and predicted[sample_id] == label
            ],
            "false_negative_sample_ids": [
                sample_id
                for sample_id, actual in references.items()
                if actual == label and predicted[sample_id] != label
            ],
        }
    return {
        "status": "calculated",
        "reference_reviewer_id": reference_reviewer_id,
        "sample_count": len(references),
        "confusion_matrix_rows_reference_columns_prediction": confusion,
        "per_label_precision_recall_f1": per_label,
        "false_positive_false_negative_sample_ids": error_analysis,
        "warning": "Metrics describe this labeled comparison only; evaluate held-out topics before generalization claims.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", nargs="+", required=True, type=Path)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--reference-reviewer-id")
    arguments = parser.parse_args()
    try:
        annotations = [
            record
            for path in arguments.annotations
            for record in read_annotation_file(path)
        ]
        report: dict[str, Any] = {
            "human_annotation_count": len(annotations),
            "human_class_counts": class_counts(annotations),
            "reviewer_agreement": reviewer_agreement(annotations),
            "classification_metrics": {
                "status": "not_calculated",
                "reason": "No model prediction file was supplied.",
            },
        }
        if arguments.predictions:
            if not arguments.reference_reviewer_id:
                parser.error("--predictions requires --reference-reviewer-id")
            report["classification_metrics"] = classification_metrics(
                annotations,
                load_prediction_file(arguments.predictions),
                arguments.reference_reviewer_id,
            )
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
