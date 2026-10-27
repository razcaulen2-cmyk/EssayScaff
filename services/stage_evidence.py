"""Small span and lexical-comparison helpers shared by essay stages."""

from collections import defaultdict
from typing import Any


def split_paragraph_spans(text: str) -> list[tuple[int, int]]:
    """Split on blank lines and return trimmed, original-text [start, end) spans."""
    spans: list[tuple[int, int]] = []
    block_start: int | None = None
    block_end: int | None = None
    cursor = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        if content.strip():
            if block_start is None:
                block_start = cursor + len(content) - len(content.lstrip())
            block_end = cursor + len(content.rstrip())
        elif block_start is not None and block_end is not None:
            spans.append((block_start, block_end))
            block_start = block_end = None
        cursor += len(line)
    if block_start is not None and block_end is not None:
        spans.append((block_start, block_end))
    return spans


def sentence_segments_in_span(
    sentences: list[dict[str, Any]], text: str, start: int, end: int
) -> list[dict[str, Any]]:
    """Clip already-parsed sentence tokens to a source-text span without reparsing."""
    result = []
    for sentence in sentences:
        tokens = [
            token
            for token in sentence["tokens"]
            if start <= token["start"] and token["end"] <= end
        ]
        if not tokens:
            continue
        sentence_start = tokens[0]["start"]
        sentence_end = tokens[-1]["end"]
        result.append(
            {
                "text": text[sentence_start:sentence_end],
                "start": sentence_start,
                "end": sentence_end,
                "source_sentence_span": [sentence["start"], sentence["end"]],
                "crosses_paragraph_boundary": (
                    sentence["start"] < start or sentence["end"] > end
                ),
                "tokens": tokens,
                "dependencies": [
                    item
                    for item in sentence["dependencies"]
                    if start <= item["start"] and item["end"] <= end
                ],
            }
        )
    return result


def clause_candidates_from_sentences(
    sentences: list[dict[str, Any]],
    finite_tags: set[str],
    clause_dependencies: set[str],
    subject_dependencies: set[str],
) -> list[dict[str, Any]]:
    """Find parser-labeled finite predicates with a dependency-linked subject."""
    candidates = []
    for sentence_index, sentence in enumerate(sentences):
        for token in sentence["tokens"]:
            if (
                token["pos"] not in {"VERB", "AUX"}
                or token["tag"] not in finite_tags
                or token["dependency"] not in clause_dependencies
            ):
                continue
            subjects = [
                {
                    "text": dependency["text"],
                    "start": dependency["start"],
                    "end": dependency["end"],
                    "dependency": dependency["dependency"],
                }
                for dependency in sentence["dependencies"]
                if dependency["dependency"] in subject_dependencies
                and dependency["head_start"] == token["start"]
            ]
            if not subjects:
                continue
            candidates.append(
                {
                    "sentence_index": sentence_index,
                    "sentence_span": [sentence["start"], sentence["end"]],
                    "sentence_text": sentence["text"],
                    "subject_evidence": subjects,
                    "predicate_evidence": {
                        "text": token["text"],
                        "start": token["start"],
                        "end": token["end"],
                        "pos": token["pos"],
                        "tag": token["tag"],
                        "dependency": token["dependency"],
                    },
                    "dependency_type": token["dependency"],
                    "evidence_type": "spaCy_dependency_and_POS_heuristic",
                    "limitation": "A parsed clause does not establish meaning, support, or validity.",
                }
            )
    return candidates


def repetition_observations(
    sentences: list[dict[str, Any]], content_pos: set[str]
) -> dict[str, Any]:
    """Report repeated content-token surfaces, lemmas, and two-word openings."""
    content = [
        token
        for sentence in sentences
        for token in sentence["tokens"]
        if token["is_alpha"] and token["pos"] in content_pos
    ]
    surface_locations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    lemma_locations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for token in content:
        location = {"text": token["text"], "start": token["start"], "end": token["end"]}
        surface_locations[token["text"].casefold()].append(location)
        lemma_locations[token["lemma"].casefold()].append(location)

    openings: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sentence in sentences:
        words = [token for token in sentence["tokens"] if token["is_alpha"]]
        if not words:
            continue
        opening = " ".join(token["text"].casefold() for token in words[:2])
        openings[opening].append(
            {
                "text": " ".join(token["text"] for token in words[:2]),
                "start": words[0]["start"],
                "end": words[min(1, len(words) - 1)]["end"],
            }
        )
    return {
        "repeated_surface_content_words": [
            {"term": term, "occurrence_count": len(items), "occurrences": items}
            for term, items in sorted(surface_locations.items())
            if len(items) > 1
        ],
        "repeated_normalized_content_terms": [
            {"lemma": lemma, "occurrence_count": len(items), "occurrences": items}
            for lemma, items in sorted(lemma_locations.items())
            if len(items) > 1
        ],
        "repeated_sentence_openings": [
            {"opening": opening, "occurrences": items}
            for opening, items in sorted(openings.items())
            if len(items) > 1
        ],
        "interpretation": "Repetition can maintain continuity and is not automatically harmful.",
    }


def compare_stage_concepts(
    source_concepts: list[dict[str, Any]],
    target_concepts: list[dict[str, Any]],
    source_section: str,
    target_section: str,
    *,
    wordnet_resource: Any,
    include_lookup_trace: bool = False,
) -> dict[str, Any]:
    """Compare concept evidence across stages; WordNet links remain candidates."""
    source_by_form = _concepts_by_form(source_concepts)
    target_by_form = _concepts_by_form(target_concepts)
    common_forms = source_by_form.keys() & target_by_form.keys()
    direct_matches = []
    normalized_matches = []

    for form in sorted(common_forms):
        exact_pairs = []
        lemma_pairs = []
        for source in source_by_form[form]:
            for target in target_by_form[form]:
                if source["pos"] != target["pos"]:
                    continue
                pair = {
                    source_section: {**source, "source_section": source_section},
                    target_section: {**target, "source_section": target_section},
                }
                if source["text"].casefold() == target["text"].casefold():
                    exact_pairs.append(pair)
                else:
                    lemma_pairs.append(pair)
        if exact_pairs:
            direct_matches.append(
                {
                    "normalized_form": form,
                    "matching_occurrences": exact_pairs,
                    "evidence_type": "exact_casefolded_surface_concept_match",
                }
            )
        if lemma_pairs:
            normalized_matches.append(
                {
                    "normalized_form": form,
                    "matching_occurrences": lemma_pairs,
                    "evidence_type": "shared_spaCy_lemma_with_different_surface_form",
                }
            )

    wordnet_result = _wordnet_candidates(
        source_concepts,
        target_concepts,
        source_section,
        target_section,
        common_forms,
        wordnet_resource,
        include_lookup_trace=include_lookup_trace,
    )
    return {
        "direct_lexical_continuity": direct_matches,
        "lemma_normalized_continuity": normalized_matches,
        "wordnet_relationship_candidates": wordnet_result,
        "unmatched_source_concepts": sorted(source_by_form.keys() - target_by_form.keys()),
    }


def _concepts_by_form(concepts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_form: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for concept in concepts:
        for occurrence in concept["occurrences"]:
            by_form[concept["normalized_form"]].append(
                {
                    "text": occurrence["text"],
                    "start": occurrence["start"],
                    "end": occurrence["end"],
                    "pos": occurrence["pos"],
                }
            )
    return by_form


def _wordnet_candidates(
    source_concepts: list[dict[str, Any]],
    target_concepts: list[dict[str, Any]],
    source_section: str,
    target_section: str,
    common_forms: set[str],
    wordnet_resource: Any,
    *,
    include_lookup_trace: bool = False,
) -> dict[str, Any]:
    try:
        wordnet_resource.synsets("essay")
    except LookupError:
        missing_result = {
            "status": "RESOURCE_MISSING",
            "suggestions": [],
            "limitation": "WordNet was unavailable; no lexical relationships were fabricated.",
        }
        if include_lookup_trace:
            missing_result["resource_probe"] = "essay"
            missing_result["lookup_pairs"] = []
        return missing_result

    pos_map = {"NOUN": "n", "PROPN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}

    def singles(concepts: list[dict[str, Any]]) -> dict[tuple[str, str | None], list[dict[str, Any]]]:
        result: dict[tuple[str, str | None], list[dict[str, Any]]] = defaultdict(list)
        for concept in concepts:
            words = concept["normalized_form"].split()
            if len(words) != 1:
                continue
            for occurrence in concept["occurrences"]:
                if len(occurrence["pos"]) != 1:
                    continue
                pos = pos_map.get(occurrence["pos"][0])
                result[(words[0], pos)].append(
                    {
                        "text": occurrence["text"],
                        "start": occurrence["start"],
                        "end": occurrence["end"],
                        "source_section": source_section,
                    }
                )
        return result

    source_words = singles(source_concepts)
    target_words = singles(target_concepts)
    synsets_by_word: dict[tuple[str, str | None], set[str]] = {}

    def synsets(word: str, pos: str | None) -> set[str]:
        key = (word, pos)
        if key not in synsets_by_word:
            synsets_by_word[key] = {
                synset.name() for synset in wordnet_resource.synsets(word, pos=pos)
            }
        return synsets_by_word[key]

    suggestions = []
    lookup_pairs: list[dict[str, Any]] = []
    for (source_word, source_pos), source_occurrences in source_words.items():
        for (target_word, target_pos), target_occurrences in target_words.items():
            if source_pos != target_pos or source_word == target_word:
                continue
            if source_word in common_forms and target_word in common_forms:
                continue
            shared = synsets(source_word, source_pos) & synsets(target_word, target_pos)
            if include_lookup_trace:
                lookup_pairs.append(
                    {
                        "source_lemma": source_word,
                        "source_pos": source_pos,
                        "source_synset_ids": sorted(synsets(source_word, source_pos)),
                        "target_lemma": target_word,
                        "target_pos": target_pos,
                        "target_synset_ids": sorted(synsets(target_word, target_pos)),
                        "shared_synset_ids": sorted(shared),
                        "candidate_emitted": len(shared) == 1,
                        "selection_condition": "Different single-word concepts, equal WordNet POS, not already a common normalized form, and exactly one shared synset.",
                    }
                )
            if len(shared) != 1:
                continue
            suggestions.append(
                {
                    source_section: {"term": source_occurrences[0]["text"], "occurrences": source_occurrences},
                    target_section: {"term": target_occurrences[0]["text"], "occurrences": target_occurrences},
                    "pos": source_pos,
                    "relationship_type": "shared_synset_candidate",
                    "synset_id": next(iter(shared)),
                    "evidence_type": "WordNet_POS_constrained_lemma_match",
                    "limitation": "Candidate only: WordNet senses are not disambiguated in sentence context.",
                }
            )
    result = {
        "status": "AVAILABLE",
        "wordnet_version": wordnet_resource.get_version(),
        "suggestions": suggestions,
        "limitation": "WordNet relationships are candidates and do not prove contextual continuity.",
    }
    if include_lookup_trace:
        result["resource_probe"] = "essay"
        result["lookup_pairs"] = lookup_pairs
    return result
