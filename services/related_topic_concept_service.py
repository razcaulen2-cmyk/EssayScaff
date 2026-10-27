"""Informational, assignment-scoped lexical associations; no NLP or WordNet calls."""

import hashlib
import json
from pathlib import Path
import re
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESOURCE_PATH = PROJECT_ROOT / "content" / "topic_concept_relations.json"
LIMITATION = (
    "A configured relationship records a lexical mention only, not an exact synonym, "
    "topic understanding, environmental support, a complete statement, or a valid argument. "
    "Negation, word sense and the writer's stance are not evaluated. "
    "This informational evidence does not affect direct/lemma coverage, rules or feedback."
)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


class RelatedTopicConceptService:
    """Load one validated configuration snapshot; scope every match to current focus.

    The resource contains canonical lemmas, not regex patterns or automatically
    expanded terms. Invalid configurations fail as a whole, never as silent
    partial mappings. Reload by reconstructing the service after a config edit.
    """

    def __init__(self, resource_path: str | Path = DEFAULT_RESOURCE_PATH) -> None:
        path = Path(resource_path)
        try:
            source = path.resolve().relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            source = path.name
        self.resource: dict[str, Any] = {
            "source": source, "status": "RESOURCE_UNAVAILABLE",
            "configuration_version": None, "sha256": None,
            "provenance": "developer_curated",
        }
        self.relationships: list[dict[str, Any]] = []
        try:
            raw = path.read_bytes()
        except OSError:
            self.resource["reason"] = "Relationship resource could not be read."
            return
        self.resource["sha256"] = hashlib.sha256(raw).hexdigest()
        try:
            config = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_object)
            self._validate(config)
        except (UnicodeError, ValueError, TypeError) as error:
            self.resource.update(status="CONFIGURATION_INVALID", reason=str(error))
            return
        self.resource.update(
            status="AVAILABLE", configuration_version=config["configuration_version"],
            schema_version=config["schema_version"],
        )
        self.relationships = [dict(record) for record in config["relationships"]]

    @staticmethod
    def _validate(config: Any) -> None:
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a JSON object.")
        if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
            raise ValueError("Unsupported relationship schema_version.")
        if not isinstance(config.get("configuration_version"), str) or not config["configuration_version"].strip():
            raise ValueError("A nonempty configuration_version is required.")
        if config.get("provenance") != "developer_curated":
            raise ValueError("This phase accepts only developer_curated relationships.")
        if not isinstance(config.get("relationships"), list):
            raise ValueError("relationships must be a list.")
        ids: set[str] = set()
        pairs: set[tuple[str, str]] = set()
        surface_keys: set[tuple[str, str]] = set()
        required = {"id", "focus_concept", "related_concept", "relationship_type", "relationship_label"}
        for index, record in enumerate(config["relationships"]):
            if not isinstance(record, dict) or not required.issubset(record) or set(record) - required - {"surface_forms"}:
                raise ValueError(f"Relationship {index} requires the five documented fields, with optional surface_forms only.")
            if any(not isinstance(record[key], str) or not record[key].strip() for key in required):
                raise ValueError(f"Relationship {index} fields must be nonempty strings.")
            if not re.fullmatch(r"[a-z]+(?: [a-z]+)*", record["focus_concept"]):
                raise ValueError(f"Relationship {index} focus_concept must be a canonical lowercase lemma phrase.")
            if not re.fullmatch(r"[a-z]+", record["related_concept"]):
                raise ValueError(f"Relationship {index} related_concept must be a single canonical lowercase lemma.")
            if not re.fullmatch(r"[a-z0-9_.-]+", record["id"]) or not re.fullmatch(r"[a-z_]+", record["relationship_type"]):
                raise ValueError(f"Relationship {index} has an invalid identifier or relationship_type.")
            pair = (record["focus_concept"], record["related_concept"])
            if record["id"] in ids or pair in pairs:
                raise ValueError(f"Relationship {index} repeats an identifier or focus/concept pair.")
            if pair[0] == pair[1]:
                raise ValueError(f"Relationship {index} is an identity, not a related-concept association.")
            forms = record.get("surface_forms", [record["related_concept"]])
            if not isinstance(forms, list) or not forms or any(not isinstance(form, str) or not re.fullmatch(r"[a-z]+", form) for form in forms):
                raise ValueError(f"Relationship {index} surface_forms must be canonical lowercase single words.")
            if len(set(forms)) != len(forms) or record["related_concept"] not in forms:
                raise ValueError(f"Relationship {index} surface_forms must be unique and include its related_concept.")
            for form in forms:
                surface_key = (record["focus_concept"], form)
                if surface_key in surface_keys:
                    raise ValueError(f"Relationship {index} has an ambiguous surface form for this focus concept.")
                surface_keys.add(surface_key)
            ids.add(record["id"])
            pairs.add(pair)

    def match(self, teacher_context: dict[str, Any], linguistic: dict[str, Any]) -> dict[str, Any]:
        """Compare existing alphabetic token lemmas with approved current targets.

        Whole normalized focus phrases must equal a configured key. A word inside
        an unknown multiword focus phrase does not activate a relationship.
        Counts distinguish unique concept lemmas, distinct text occurrences and
        relationship records (one occurrence could link to several future targets).
        """
        result: dict[str, Any] = {
            "execution_status": "NOT_APPLICABLE", "reason": None,
            "resource": dict(self.resource), "active_focus_concepts": [], "approved_relationships": [],
            "evidence": [],
            "summary": {
                "unique_related_concepts_observed": 0,
                "total_related_concept_occurrences": 0,
                "relationship_record_count": 0,
                "teacher_focus_concepts_with_related_evidence": [],
                "teacher_focus_terms_with_related_evidence": [],
            },
            "informational_only": True, "affects_rules_or_feedback": False,
            "limitation": LIMITATION,
            "future_integration": (
                "Potential future evidence for evaluated topic-feedback revisions only after review; "
                "not consumed by any current Rule Base or FeedbackService branch."
            ),
        }
        if self.resource["status"] != "AVAILABLE":
            result.update(execution_status=self.resource["status"], reason=self.resource["reason"])
            return result
        if teacher_context.get("focus_source") != "teacher_provided":
            result["reason"] = "NO_EXPLICIT_TEACHER_FOCUS: derived topic candidates do not activate curated relationships."
            return result
        configured_focus = {item["focus_concept"] for item in self.relationships}
        active: dict[str, str] = {}
        for focus in teacher_context.get("focus_terms", []):
            normalized = focus.get("normalized_form")
            if normalized in configured_focus:
                active.setdefault(normalized, focus["term"])
        result["active_focus_concepts"] = [
            {"teacher_focus_term": term, "normalized_focus_concept": normalized}
            for normalized, term in active.items()
        ]
        if not active:
            result["reason"] = "NO_APPROVED_FOCUS_CONCEPT: no complete active teacher focus matches a configured key."
            return result
        by_lemma: dict[str, list[dict[str, Any]]] = {}
        by_surface: dict[str, list[dict[str, Any]]] = {}
        for relation in self.relationships:
            if relation["focus_concept"] in active:
                by_lemma.setdefault(relation["related_concept"], []).append(relation)
                for form in relation.get("surface_forms", [relation["related_concept"]]):
                    by_surface.setdefault(form, []).append(relation)
                result["approved_relationships"].append(dict(relation))
        # Position lookup uses the serialized sentence records from the same Doc.
        sentence_by_span = {
            (token["start"], token["end"]): index
            for index, sentence in enumerate(linguistic.get("sentences", []))
            for token in sentence.get("tokens", [])
        }
        seen: set[tuple[int, int, str]] = set()
        evidence = result["evidence"]
        for token in linguistic.get("tokens", []):
            if not token.get("is_alpha"):
                continue
            lemma = (token.get("lemma") or token["text"]).casefold()
            # Only explicitly configured forms supplement model lemmas; no suffix
            # stripping, stemming, synonym generation or extra NLP is performed.
            candidates = {relation["id"]: relation for relation in by_lemma.get(lemma, []) + by_surface.get(token["text"].casefold(), [])}
            for relation in candidates.values():
                occurrence = (token["start"], token["end"], relation["id"])
                if occurrence in seen:
                    continue
                seen.add(occurrence)
                evidence.append({
                    "teacher_focus_term": active[relation["focus_concept"]],
                    "normalized_focus_concept": relation["focus_concept"],
                    "student_word": token["text"], "normalized_student_word": relation["related_concept"],
                    "spacy_lemma": token.get("lemma"),
                    "start": token["start"], "end": token["end"],
                    "token_index": token.get("index"),
                    "sentence_index": sentence_by_span.get((token["start"], token["end"])),
                    "relationship_label": relation["relationship_label"],
                    "relationship_type": relation["relationship_type"],
                    "relationship_source": self.resource["source"],
                    "relationship_id": relation["id"],
                    "configuration_version": self.resource["configuration_version"],
                    "normalization_method": "spacy_lemma" if token.get("lemma") and lemma == relation["related_concept"] else "configured_surface_form",
                    "normalization_source": "Existing spaCy lemma (casefolded), or explicitly configured surface_forms; no inferred inflection or synonym expansion",
                    "match_method": "configured_topic_relationship", "match_status": "LEXICAL_RELATION_OBSERVED",
                    "limitation": LIMITATION,
                })
        result.update(execution_status="EXECUTED", reason="MATCHES_OBSERVED" if evidence else "NO_MATCHES")
        result["summary"] = {
            "unique_related_concepts_observed": len({item["normalized_student_word"] for item in evidence}),
            "total_related_concept_occurrences": len({(item["start"], item["end"]) for item in evidence}),
            "relationship_record_count": len(evidence),
            "teacher_focus_concepts_with_related_evidence": list(dict.fromkeys(item["normalized_focus_concept"] for item in evidence)),
            "teacher_focus_terms_with_related_evidence": list(dict.fromkeys(item["teacher_focus_term"] for item in evidence)),
        }
        return result
