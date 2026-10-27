"""Manual, reviewer-specific annotation CLI for the diagnostic samples."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Callable, Any


INTELLIGIBILITY_LABELS = {"CLEAR", "UNCLEAR", "NONSENSICAL", "UNCERTAIN"}
RELEVANCE_LABELS = {
    "RELEVANT", "PARTLY_RELEVANT", "NOT_RELEVANT", "UNCERTAIN", "NOT_ASSESSED"
}
FIGURATIVE_LABELS = {"YES", "NO", "UNCERTAIN", "NOT_ASSESSED"}
REVIEWER_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,39}\Z")


def load_samples(path: Path) -> list[dict[str, Any]]:
    """Load developer-authored examples and reject unstable/duplicate IDs."""
    try:
        samples = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot load sample file {path}: {error}") from error
    if not isinstance(samples, list):
        raise ValueError("Sample file must contain a JSON list")

    seen_ids: set[str] = set()
    for sample in samples:
        if not isinstance(sample, dict) or not all(
            isinstance(sample.get(field), str) and sample[field].strip()
            for field in ("sample_id", "topic_id", "topic", "text")
        ):
            raise ValueError("Every sample needs non-empty IDs, topic, and text")
        sample_id = sample["sample_id"]
        if sample_id in seen_ids:
            raise ValueError(f"Duplicate sample_id: {sample_id}")
        if sample.get("source") != "developer_authored":
            raise ValueError(f"Sample {sample_id} has unexpected source provenance")
        seen_ids.add(sample_id)
    return samples


def validate_annotation(annotation: dict[str, Any]) -> None:
    """Validate a complete human record before it is persisted."""
    if annotation.get("record_type") != "human_annotation":
        raise ValueError("Annotation record_type must be human_annotation")
    if annotation.get("label_provenance") != "human_reviewer":
        raise ValueError("Human labels must carry human_reviewer provenance")
    if not isinstance(annotation.get("sample_id"), str) or not annotation["sample_id"]:
        raise ValueError("sample_id is required")
    reviewer_id = annotation.get("reviewer_id")
    if not isinstance(reviewer_id, str) or not REVIEWER_ID_PATTERN.fullmatch(reviewer_id):
        raise ValueError("reviewer_id must be a pseudonymous ID (1-40 safe characters)")
    if annotation.get("intelligibility_label") not in INTELLIGIBILITY_LABELS:
        raise ValueError("Invalid intelligibility label")
    if annotation.get("topic_relevance") not in RELEVANCE_LABELS:
        raise ValueError("Invalid topic relevance label")
    if annotation.get("figurative_language") not in FIGURATIVE_LABELS:
        raise ValueError("Invalid figurative-language value")
    confidence = annotation.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, int) or confidence not in range(1, 6):
        raise ValueError("confidence must be an integer from 1 to 5")
    if not isinstance(annotation.get("explanation"), str) or not annotation["explanation"].strip():
        raise ValueError("A short explanation is required")
    if not isinstance(annotation.get("annotated_at_utc"), str):
        raise ValueError("annotated_at_utc is required")


def read_annotation_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            record = json.loads(line)
            validate_annotation(record)
        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError(f"Invalid annotation at {path}:{line_number}: {error}") from error
        records.append(record)
    return records


def save_annotation(path: Path, annotation: dict[str, Any]) -> None:
    """Append a validated record; refuse accidental duplicate reviewer/sample pairs."""
    validate_annotation(annotation)
    prior = read_annotation_file(path)
    key = (annotation["sample_id"], annotation["reviewer_id"])
    if any((item["sample_id"], item["reviewer_id"]) == key for item in prior):
        raise ValueError("This reviewer has already annotated this sample")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(annotation, ensure_ascii=False) + "\n")
        output.flush()


def _ask_choice(
    prompt: str,
    allowed: set[str],
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
    *,
    allow_blank: str | None = None,
) -> str | None:
    while True:
        answer = input_fn(prompt).strip().upper()
        if answer in {"Q", "QUIT"}:
            return None
        if not answer and allow_blank:
            return allow_blank
        if answer in allowed:
            return answer
        output_fn("Choose one of: " + ", ".join(sorted(allowed)) + (" (or Q to stop)."))


def annotate_samples(
    samples: list[dict[str, Any]],
    reviewer_id: str,
    output_path: Path,
    *,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> int:
    """Annotate uncompleted samples for one reviewer; never display other labels."""
    if not REVIEWER_ID_PATTERN.fullmatch(reviewer_id):
        raise ValueError("Use a pseudonymous reviewer ID of 1-40 safe characters")
    input_fn = input_fn or input
    output_fn = output_fn or print
    saved_records = read_annotation_file(output_path)
    completed_ids = {
        record["sample_id"]
        for record in saved_records
        if record["reviewer_id"] == reviewer_id
    }
    output_fn(
        f"Reviewer {reviewer_id}: {len(completed_ids)} completed; "
        f"{len(samples) - len(completed_ids)} remaining. Other reviewers' labels are hidden."
    )
    saved_count = 0

    for sample in samples:
        if sample["sample_id"] in completed_ids:
            continue
        output_fn(f"\nSample {sample['sample_id']} ({sample['topic_id']})")
        output_fn(f"Assignment topic: {sample['topic']}")
        output_fn(f"Writing: {sample['text']}")
        intelligibility = _ask_choice(
            "Intelligibility [CLEAR/UNCLEAR/NONSENSICAL/UNCERTAIN; Q quits]: ",
            INTELLIGIBILITY_LABELS,
            input_fn,
            output_fn,
        )
        if intelligibility is None:
            break
        relevance = _ask_choice(
            "Topic relevance [RELEVANT/PARTLY_RELEVANT/NOT_RELEVANT/UNCERTAIN; Enter skips]: ",
            RELEVANCE_LABELS,
            input_fn,
            output_fn,
            allow_blank="NOT_ASSESSED",
        )
        if relevance is None:
            break
        figurative = _ask_choice(
            "Figurative language [YES/NO/UNCERTAIN; Enter skips]: ",
            FIGURATIVE_LABELS,
            input_fn,
            output_fn,
            allow_blank="NOT_ASSESSED",
        )
        if figurative is None:
            break

        while True:
            confidence_text = input_fn("Confidence 1-5 (Q quits): ").strip()
            if confidence_text.upper() in {"Q", "QUIT"}:
                confidence = None
                break
            if confidence_text in {"1", "2", "3", "4", "5"}:
                confidence = int(confidence_text)
                break
            output_fn("Enter a number from 1 to 5, or Q to stop.")
        if confidence is None:
            break

        explanation = input_fn("Short explanation (Q quits): ").strip()
        if explanation.upper() in {"Q", "QUIT"}:
            break
        if not explanation:
            output_fn("An explanation is required; this sample remains unfinished.")
            continue

        annotation = {
            "record_type": "human_annotation",
            "label_provenance": "human_reviewer",
            "sample_id": sample["sample_id"],
            "reviewer_id": reviewer_id,
            "intelligibility_label": intelligibility,
            "topic_relevance": relevance,
            "figurative_language": figurative,
            "confidence": confidence,
            "explanation": explanation,
            "annotated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        save_annotation(output_path, annotation)
        saved_count += 1
        completed_ids.add(sample["sample_id"])
        output_fn("Saved this human annotation.")

    output_fn(f"Session ended; saved {saved_count} new annotation(s).")
    return saved_count


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-id", required=True, help="Pseudonymous ID; do not use a real name.")
    parser.add_argument("--samples", type=Path, default=script_dir / "samples.json")
    parser.add_argument("--annotations", type=Path, help="Output JSONL; defaults to a reviewer-specific file.")
    arguments = parser.parse_args()
    if not REVIEWER_ID_PATTERN.fullmatch(arguments.reviewer_id):
        parser.error("--reviewer-id must contain 1-40 letters, digits, dots, underscores, or hyphens")
    output_path = arguments.annotations or (
        script_dir / "annotations" / f"{arguments.reviewer_id}.jsonl"
    )
    try:
        samples = load_samples(arguments.samples)
        annotate_samples(samples, arguments.reviewer_id, output_path)
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
