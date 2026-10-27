"""Run descriptive sentence-embedding comparisons; never classify samples."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
from typing import Any

import numpy as np

try:
    from .annotate import load_samples
except ImportError:  # Support direct execution with python encoder_experiment.py.
    from annotate import load_samples


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
EXPECTED_DIMENSIONS = 384


def cosine_similarity(first: np.ndarray, second: np.ndarray) -> float:
    """Cosine similarity for nonzero vectors; normalized model vectors use dot product."""
    first_norm = np.linalg.norm(first)
    second_norm = np.linalg.norm(second)
    if first_norm == 0 or second_norm == 0:
        raise ValueError("Cosine similarity is undefined for a zero vector")
    return float(np.dot(first, second) / (first_norm * second_norm))


def split_sentences_for_diagnostic(text: str) -> list[str]:
    """Small punctuation-based splitter used only for adjacent-text comparisons."""
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def make_experiment_result(
    samples: list[dict[str, Any]],
    vectors: np.ndarray,
    encode_seconds: float,
    model_load_seconds: float,
    model: Any,
    device: str,
    package_versions: dict[str, str],
) -> dict[str, Any]:
    """Map normalized embeddings into transparent pairwise cosine comparisons."""
    expected_inputs: list[str] = []
    for sample in samples:
        expected_inputs.extend([sample["text"], sample["topic"]])
    sentence_pairs = [
        (sample["sample_id"], first, second)
        for sample in samples
        for first, second in zip(
            split_sentences_for_diagnostic(sample["text"]),
            split_sentences_for_diagnostic(sample["text"])[1:],
        )
    ]
    expected_inputs.extend(sentence for _, first, second in sentence_pairs for sentence in (first, second))

    if vectors.ndim != 2 or vectors.shape != (len(expected_inputs), EXPECTED_DIMENSIONS):
        raise ValueError(
            f"Unexpected embedding shape {vectors.shape}; expected "
            f"({len(expected_inputs)}, {EXPECTED_DIMENSIONS})"
        )
    if not np.isfinite(vectors).all():
        raise ValueError("Encoder returned non-finite embedding values")

    cursor = 0
    sample_topic_pairs = []
    for sample in samples:
        sample_vector = vectors[cursor]
        topic_vector = vectors[cursor + 1]
        cursor += 2
        sample_topic_pairs.append(
            {
                "sample_id": sample["sample_id"],
                "topic_id": sample["topic_id"],
                "sample_text": sample["text"],
                "assignment_topic": sample["topic"],
                "cosine_similarity": cosine_similarity(sample_vector, topic_vector),
            }
        )

    adjacent_pairs = []
    for sample_id, first, second in sentence_pairs:
        first_vector = vectors[cursor]
        second_vector = vectors[cursor + 1]
        cursor += 2
        adjacent_pairs.append(
            {
                "sample_id": sample_id,
                "first_statement": first,
                "second_statement": second,
                "cosine_similarity": cosine_similarity(first_vector, second_vector),
            }
        )

    return {
        "experiment_type": "descriptive_embedding_similarity_not_classification",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": {
            "model_id": MODEL_ID,
            "revision": MODEL_REVISION,
            "license": "Apache-2.0",
            "dimensions": EXPECTED_DIMENSIONS,
            "maximum_sequence_length": model.max_seq_length,
            **package_versions,
            "device": device,
        },
        "measurement": {
            "similarity": "cosine similarity between L2-normalized encoder embeddings",
            "score_interpretation": (
                "Descriptive geometric similarity only; not an intelligibility probability, "
                "semantic correctness score, relevance decision, or threshold."
            ),
            "sample_count": len(samples),
            "embedding_count": int(vectors.shape[0]),
            "embedding_shape": list(vectors.shape),
            "all_embedding_values_finite": bool(np.isfinite(vectors).all()),
            "model_load_seconds": model_load_seconds,
            "encode_seconds": encode_seconds,
        },
        "sample_to_topic": sample_topic_pairs,
        "adjacent_statement_pairs": adjacent_pairs,
    }


def run_experiment(
    samples_path: Path,
    output_path: Path,
    *,
    device: str = "cpu",
    model_loader: Any = None,
) -> dict[str, Any]:
    import sentence_transformers
    import torch
    import transformers
    from sentence_transformers import SentenceTransformer as ModelLoader

    samples = load_samples(samples_path)
    torch.set_num_threads(min(4, torch.get_num_threads()))
    start_load = time.perf_counter()
    model = (model_loader or ModelLoader)(MODEL_ID, revision=MODEL_REVISION, device=device)
    load_seconds = time.perf_counter() - start_load

    texts: list[str] = []
    for sample in samples:
        texts.extend([sample["text"], sample["topic"]])
    adjacent_inputs = [
        sentence
        for sample in samples
        for pair in zip(
            split_sentences_for_diagnostic(sample["text"]),
            split_sentences_for_diagnostic(sample["text"])[1:],
        )
        for sentence in pair
    ]
    texts.extend(adjacent_inputs)
    started_encode = time.perf_counter()
    vectors = model.encode(
        texts,
        batch_size=8,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    encode_seconds = time.perf_counter() - started_encode
    result = make_experiment_result(
        samples,
        np.asarray(vectors),
        encode_seconds,
        load_seconds,
        model,
        device,
        {
            "sentence_transformers_version": sentence_transformers.__version__,
            "transformers_version": transformers.__version__,
            "torch_version": torch.__version__,
        },
    )
    result["measurement"]["total_runtime_seconds"] = time.perf_counter() - start_load
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=script_dir / "samples.json")
    parser.add_argument("--output", type=Path, default=script_dir / "encoder_results.json")
    parser.add_argument("--device", choices=("cpu",), default="cpu")
    arguments = parser.parse_args()
    result = run_experiment(arguments.samples, arguments.output, device=arguments.device)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nSaved descriptive encoder output to: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
