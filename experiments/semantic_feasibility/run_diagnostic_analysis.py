"""Join Phase 2 and pinned encoder observations for every diagnostic sample."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import mean
from typing import Any

import spacy

from services.nlp_service import NLPService
from services.topic_service import TopicService

from experiments.semantic_feasibility.annotate import load_samples


LABELS = {"CLEAR", "UNCLEAR", "NONSENSICAL", "UNCERTAIN"}
RELEVANCE = {"ON_TOPIC", "PARTLY_ON_TOPIC", "OFF_TOPIC", "UNCERTAIN"}
FIGURATIVE = {"YES", "NO", "UNCERTAIN"}


def load_ai_diagnostics(
    samples: list[dict[str, Any]], annotation_path: Path
) -> dict[str, dict[str, Any]]:
    """Validate AI-only diagnostic judgments against the immutable source samples."""
    try:
        data = json.loads(annotation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read AI diagnostic annotations: {error}") from error
    if (
        data.get("file_provenance") != "AI_GENERATED_DIAGNOSTIC"
        or data.get("human_reviewed") is not False
        or data.get("label_status") != "provisional_unvalidated_not_human_reviewed"
    ):
        raise ValueError("AI diagnostic provenance metadata is missing or invalid")

    source_by_id = {sample["sample_id"]: sample for sample in samples}
    annotations: dict[str, dict[str, Any]] = {}
    for item in data.get("samples", []):
        sample_id = item.get("sample_id")
        if sample_id not in source_by_id or sample_id in annotations:
            raise ValueError(f"Unknown or duplicate AI diagnostic sample_id: {sample_id}")
        source = source_by_id[sample_id]
        if item.get("assignment_topic") != source["topic"] or item.get("original_writing") != source["text"]:
            raise ValueError(f"AI diagnostic text/topic differs from source sample {sample_id}")
        if item.get("provisional_intelligibility_label") not in LABELS:
            raise ValueError(f"Invalid provisional label for {sample_id}")
        if item.get("topic_relevance") not in RELEVANCE:
            raise ValueError(f"Invalid provisional relevance for {sample_id}")
        if item.get("figurative_language") not in FIGURATIVE:
            raise ValueError(f"Invalid figurative-language label for {sample_id}")
        if item.get("annotation_provenance") != "AI_GENERATED_DIAGNOSTIC":
            raise ValueError(f"Invalid annotation provenance for {sample_id}")
        if not isinstance(item.get("explanation"), str) or not item["explanation"].strip():
            raise ValueError(f"Missing explanation for {sample_id}")
        annotations[sample_id] = item
    if annotations.keys() != source_by_id.keys():
        raise ValueError("AI diagnostic file must contain exactly one record for every sample")
    return annotations


def build_analysis(
    samples: list[dict[str, Any]],
    encoder_results: dict[str, Any],
    focus_config: dict[str, Any],
    ai_annotations: dict[str, dict[str, Any]],
    topic_service: TopicService,
) -> dict[str, Any]:
    encoder_by_id = {item["sample_id"]: item for item in encoder_results["sample_to_topic"]}
    if encoder_by_id.keys() != {sample["sample_id"] for sample in samples}:
        raise ValueError("Encoder output sample IDs do not match the pilot sample IDs")
    if encoder_results["model"]["model_id"] != "sentence-transformers/all-MiniLM-L6-v2":
        raise ValueError("Unexpected encoder model in result file")

    adjacent_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in encoder_results.get("adjacent_statement_pairs", []):
        adjacent_by_id[pair["sample_id"]].append(pair)

    results = []
    for sample in samples:
        sample_id = sample["sample_id"]
        focus_terms = focus_config["topic_focus_terms"].get(sample["topic_id"])
        if not focus_terms:
            raise ValueError(f"No diagnostic focus terms for topic {sample['topic_id']}")
        topic_result = topic_service.analyze(
            sample["text"], sample["topic"], focus_terms, include_wordnet=True
        )
        # TopicService returns Phase 1 observations derived from its same student Doc.
        linguistic = topic_result["linguistic_analysis"]
        evidence = topic_result["confirmed_lexical_observations"]
        sentence_observations = [
            {
                "text": sentence["text"],
                "start": sentence["start"],
                "end": sentence["end"],
                "dependencies": sentence["dependencies"],
                "tokens": [
                    {
                        "text": token["text"],
                        "lemma": token["lemma"],
                        "pos": token["pos"],
                        "dependency": token["dependency"],
                        "head": token["head"],
                    }
                    for token in sentence["tokens"]
                ],
            }
            for sentence in linguistic["sentences"]
        ]
        results.append(
            {
                "sample_id": sample_id,
                "topic_id": sample["topic_id"],
                "provisional_ai_intelligibility_label": ai_annotations[sample_id][
                    "provisional_intelligibility_label"
                ],
                "annotation_provenance": "AI_GENERATED_DIAGNOSTIC",
                "linguistic_observations": {
                    "counts": linguistic["counts"],
                    "sentences": sentence_observations,
                    "noun_phrases": linguistic["noun_phrases"],
                },
                "lexical_observations": {
                    "focus_list_provenance": focus_config["provenance"],
                    "focus_terms": focus_terms,
                    "observed_focus_terms": topic_result["focus_coverage"]["observed_focus_terms"],
                    "unobserved_focus_terms": topic_result["focus_coverage"]["unobserved_focus_terms"],
                    "observed_count": topic_result["focus_coverage"]["observed_unique_focus_terms"],
                    "total_focus_count": topic_result["focus_coverage"]["total_unique_focus_terms"],
                    "matches": [
                        {
                            "term": item["term"],
                            "direct_count": len(item["direct_matches"]),
                            "normalized_count": len(item["normalized_matches"]),
                            "direct_matches": item["direct_matches"],
                            "normalized_matches": item["normalized_matches"],
                        }
                        for item in evidence
                    ],
                    "wordnet_status": topic_result["wordnet"]["status"],
                    "wordnet_suggestions": topic_result["wordnet"]["suggestions"],
                },
                "encoder_observations": {
                    "model_id": encoder_results["model"]["model_id"],
                    "model_revision": encoder_results["model"]["revision"],
                    "topic_cosine_similarity": encoder_by_id[sample_id]["cosine_similarity"],
                    "adjacent_statement_cosines": adjacent_by_id[sample_id],
                },
            }
        )

    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        by_label[result["provisional_ai_intelligibility_label"]].append(result)
    descriptive_groups = {}
    for label, rows in sorted(by_label.items()):
        scores = [row["encoder_observations"]["topic_cosine_similarity"] for row in rows]
        coverage = [
            row["lexical_observations"]["observed_count"]
            / row["lexical_observations"]["total_focus_count"]
            for row in rows
        ]
        descriptive_groups[label] = {
            "sample_count": len(rows),
            "sample_ids": [row["sample_id"] for row in rows],
            "mean_topic_cosine_similarity": mean(scores),
            "minimum_topic_cosine_similarity": min(scores),
            "maximum_topic_cosine_similarity": max(scores),
            "mean_lexical_focus_fraction": mean(coverage),
        }

    return {
        "analysis_provenance": "automated_observations_joined_to_provisional_AI_GENERATED_DIAGNOSTIC_labels",
        "reference_label_warning": (
            "Provisional AI judgments are not human labels, gold labels, or independent validation. "
            "No classification metrics are calculated from this file."
        ),
        "sample_count": len(results),
        "spacy_runtime_version": spacy.__version__,
        "spacy_model_name": topic_service.nlp_service.nlp.meta.get("name"),
        "spacy_model_version": topic_service.nlp_service.nlp.meta.get("version"),
        "encoder_metadata": encoder_results["model"],
        "encoder_generated_at_utc": encoder_results.get("generated_at_utc"),
        "measurement_metadata": encoder_results["measurement"],
        "descriptive_groups_by_provisional_ai_label_not_model_evaluation": descriptive_groups,
        "samples": results,
    }


def run_analysis(
    sample_path: Path,
    encoder_path: Path,
    focus_path: Path,
    annotation_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    samples = load_samples(sample_path)
    encoder_results = json.loads(encoder_path.read_text(encoding="utf-8"))
    focus_config = json.loads(focus_path.read_text(encoding="utf-8"))
    ai_annotations = load_ai_diagnostics(samples, annotation_path)
    nlp_service = NLPService()
    result = build_analysis(
        samples,
        encoder_results,
        focus_config,
        ai_annotations,
        TopicService(nlp_service),
    )
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    experiment_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=experiment_dir / "samples.json")
    parser.add_argument("--encoder-results", type=Path, default=experiment_dir / "encoder_results.json")
    parser.add_argument("--focus-terms", type=Path, default=experiment_dir / "diagnostic_focus_terms.json")
    parser.add_argument("--ai-annotations", type=Path, default=experiment_dir / "ai_diagnostic_annotations.json")
    parser.add_argument("--output", type=Path, default=experiment_dir / "diagnostic_analysis.json")
    arguments = parser.parse_args()
    result = run_analysis(
        arguments.samples,
        arguments.encoder_results,
        arguments.focus_terms,
        arguments.ai_annotations,
        arguments.output,
    )
    print(f"Analyzed {result['sample_count']} samples; wrote {arguments.output}")
    print(json.dumps(result["descriptive_groups_by_provisional_ai_label_not_model_evaluation"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
