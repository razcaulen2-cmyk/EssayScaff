"""Explainable lexical concepts and teacher-topic evidence."""

import re
from time import perf_counter
from typing import Any

from nltk.corpus import wordnet
from spacy.tokens import Doc, Token

from services.nlp_service import NLPService


def _elapsed_ms(start: float | None) -> float:
    return (perf_counter() - start) * 1000 if start is not None else 0.0


class TopicService:
    """Compare teacher focus phrases with concepts in a student's parsed text."""

    def __init__(self, nlp_service: NLPService | None = None) -> None:
        self.nlp_service = nlp_service or NLPService()

    def analyze(
        self,
        student_text: str,
        assignment_topic: str,
        focus_terms: list[str] | None = None,
        *,
        include_wordnet: bool = True,
        prepared_teacher_context: dict[str, Any] | None = None,
        collect_trace: bool = False,
    ) -> dict[str, Any]:
        if not isinstance(student_text, str):
            raise TypeError("student_text must be a string")
        if not isinstance(assignment_topic, str):
            raise TypeError("assignment_topic must be a string")
        if focus_terms is not None and (
            isinstance(focus_terms, (str, bytes))
            or not all(isinstance(term, str) for term in focus_terms)
        ):
            raise TypeError("focus_terms must be a list of strings")

        stage_started = perf_counter() if collect_trace else None
        parse_started = perf_counter() if collect_trace else None
        # Parse student writing once. Phase 1 and Phase 2 features use this Doc.
        doc = self.nlp_service.parse(student_text)
        parse_ms = _elapsed_ms(parse_started)
        observations_started = perf_counter() if collect_trace else None
        linguistic_analysis = self.nlp_service.analyze_doc(doc)
        observations_ms = _elapsed_ms(observations_started)
        concepts_started = perf_counter() if collect_trace else None
        student_concepts = self._extract_concepts(doc)
        concepts_ms = _elapsed_ms(concepts_started)

        if prepared_teacher_context is not None:
            if prepared_teacher_context.get("assignment_topic") != assignment_topic:
                raise ValueError("prepared teacher context topic does not match the supplied assignment topic")
            expected_source = "teacher_provided" if focus_terms else "topic_derived_candidates"
            if prepared_teacher_context.get("focus_source") != expected_source:
                raise ValueError("prepared teacher context focus source does not match the supplied focus terms")
            prepared_terms = prepared_teacher_context.get("requested_focus_terms")
            if (list(prepared_terms) if prepared_terms is not None else None) != (
                list(focus_terms) if focus_terms is not None else None
            ):
                raise ValueError("prepared teacher context focus terms do not match the supplied terms")
            focus_source = prepared_teacher_context["focus_source"]
            focus_specs = prepared_teacher_context["focus_terms"]
            automatic_candidates = prepared_teacher_context["automatically_derived_candidates"]
        elif focus_terms:
            focus_source = "teacher_provided"
            focus_specs = self._unique_focus_terms(focus_terms)
            automatic_candidates = []
        else:
            focus_source = "topic_derived_candidates"
            focus_specs = self._unique_focus_terms(
                [concept["text"] for concept in self._extract_concepts(
                    self.nlp_service.nlp(assignment_topic)
                )]
            )
            automatic_candidates = focus_specs

        matching_started = perf_counter() if collect_trace else None
        focus_results = []
        for focus in focus_specs:
            direct_matches, normalized_matches = self._find_matches(doc, focus)
            focus_results.append(
                {
                    **focus,
                    "direct_matches": direct_matches,
                    "normalized_matches": normalized_matches,
                    "occurrence_count": len(direct_matches) + len(normalized_matches),
                    "observed": bool(direct_matches or normalized_matches),
                }
            )
        matching_ms = _elapsed_ms(matching_started)

        wordnet_started = perf_counter() if collect_trace else None
        wordnet_status = self._wordnet_status(include_wordnet)
        wordnet_lookup_trace: list[dict[str, Any]] | None = [] if collect_trace else None
        wordnet_suggestions = (
            self._wordnet_suggestions(focus_results, student_concepts, lookup_trace=wordnet_lookup_trace)
            if wordnet_status["available"]
            else []
        )
        wordnet_ms = _elapsed_ms(wordnet_started)
        observed = [term for term in focus_results if term["observed"]]
        unobserved = [term for term in focus_results if not term["observed"]]

        result = {
            "teacher_context": {
                "assignment_topic": assignment_topic,
                "focus_source": focus_source,
                "focus_terms": focus_specs,
                "automatically_derived_candidates": automatic_candidates,
            },
            "student_concepts": student_concepts,
            "confirmed_lexical_observations": focus_results,
            "wordnet": {
                **wordnet_status,
                "suggestions": wordnet_suggestions,
            },
            "focus_coverage": {
                "observed_focus_terms": [term["term"] for term in observed],
                "unobserved_focus_terms": [term["term"] for term in unobserved],
                "total_unique_focus_terms": len(focus_results),
                "observed_unique_focus_terms": len(observed),
            },
            "linguistic_analysis": linguistic_analysis,
            "interpretation_limit": (
                "These paragraphs contain topic-related lexical evidence. Their "
                "semantic intelligibility has not been determined. Lexical matches "
                "do not establish accuracy, coherence, meaningfulness, or quality."
            ),
        }
        if collect_trace:
            result["research_trace"] = {
                "execution_status": "EXECUTED",
                "input": {
                    "text_characters": len(student_text),
                    "assignment_topic": assignment_topic,
                    "focus_terms": [item["term"] for item in focus_specs],
                    "focus_source": focus_source,
                    "include_wordnet": include_wordnet,
                },
                "steps": [
                    {
                        "id": "spacy_document_processing",
                        "execution_status": "EXECUTED",
                        "duration_ms": round(parse_ms + observations_ms, 3),
                        "parse_ms": round(parse_ms, 3),
                        "observation_serialization_ms": round(observations_ms, 3),
                        "output_counts": linguistic_analysis["counts"],
                        "model_name": self.nlp_service.nlp.meta.get("name"),
                        "model_version": self.nlp_service.nlp.meta.get("version"),
                        "pipeline_components": list(self.nlp_service.nlp.pipe_names),
                        "limitation": "spaCy annotations are statistical predictions; this does not validate meaning.",
                    },
                    {
                        "id": "concept_extraction",
                        "execution_status": "EXECUTED",
                        "duration_ms": round(concepts_ms, 3),
                        "candidate_count": len(student_concepts),
                        "output": student_concepts,
                        "implementation": "TopicService._extract_concepts on the already parsed Doc.",
                    },
                    {
                        "id": "topic_matching",
                        "execution_status": "EXECUTED",
                        "duration_ms": round(matching_ms, 3),
                        "focus_term_count": len(focus_specs),
                        "observed_focus_term_count": len(observed),
                        "output": focus_results,
                    },
                    {
                        "id": "wordnet_direct_suggestions",
                        "execution_status": (
                            "SKIPPED" if not include_wordnet
                            else "EXECUTED" if wordnet_status["available"]
                            else "FAILED"
                        ),
                        "duration_ms": round(wordnet_ms, 3),
                        "status": wordnet_status["status"],
                        "wordnet_version": wordnet_status.get("version"),
                        "suggestion_count": len(wordnet_suggestions),
                        "output": wordnet_suggestions,
                        "resource_probe": "essay" if include_wordnet else None,
                        "lookup_pairs": wordnet_lookup_trace,
                        "limitation": "This status covers TopicService focus-term suggestions, not separate cross-stage WordNet comparisons.",
                    },
                ],
                "total_ms": round(_elapsed_ms(stage_started), 3),
            }
        return self._with_related_concepts(result)

    def prepare_teacher_context(
        self, assignment_topic: str, focus_terms: list[str] | None = None
    ) -> dict[str, Any]:
        """Normalize assignment focus once for a coordinator's multiple stage calls."""
        if not isinstance(assignment_topic, str):
            raise TypeError("assignment_topic must be a string")
        if focus_terms is not None and (
            isinstance(focus_terms, (str, bytes))
            or not all(isinstance(term, str) for term in focus_terms)
        ):
            raise TypeError("focus_terms must be a list of strings")
        if focus_terms:
            focus_source = "teacher_provided"
            focus_specs = self._unique_focus_terms(focus_terms)
            automatic_candidates = []
        else:
            focus_source = "topic_derived_candidates"
            topic_doc = self.nlp_service.nlp(assignment_topic)
            focus_specs = self._unique_focus_terms(
                [concept["text"] for concept in self._extract_concepts(topic_doc)]
            )
            automatic_candidates = focus_specs
        return {
            "assignment_topic": assignment_topic,
            "focus_source": focus_source,
            "focus_terms": focus_specs,
            "automatically_derived_candidates": automatic_candidates,
            "requested_focus_terms": list(focus_terms) if focus_terms is not None else None,
        }

    @staticmethod
    def validate_prepared_analysis(
        analysis: dict[str, Any], student_text: str, assignment_topic: str
    ) -> None:
        """Guard reuse so a prepared result cannot silently refer to other text/topic."""
        if not isinstance(analysis, dict):
            raise TypeError("prepared topic analysis must be a dictionary")
        if analysis.get("linguistic_analysis", {}).get("text") != student_text:
            raise ValueError("prepared topic analysis text does not match the supplied writing")
        teacher_context = analysis.get("teacher_context", {})
        if teacher_context.get("assignment_topic") != assignment_topic:
            raise ValueError("prepared topic analysis topic does not match the supplied assignment topic")

    def _unique_focus_terms(self, terms: list[str]) -> list[dict[str, Any]]:
        unique: dict[str, dict[str, Any]] = {}
        for term in terms:
            parsed = self.nlp_service.nlp(term)
            word_tokens = [token for token in parsed if token.is_alpha]
            if not word_tokens:
                continue
            normalized_words = [self._lemma(token) for token in word_tokens]
            normalized = " ".join(normalized_words)
            unique.setdefault(
                normalized,
                {
                    "term": term.strip(),
                    "normalized_form": normalized,
                    "surface_words": [token.text.casefold() for token in word_tokens],
                    "normalized_words": normalized_words,
                    "wordnet_pos": sorted(
                        {
                            mapped
                            for token in word_tokens
                            if (mapped := self._wordnet_pos(token.pos_)) is not None
                        }
                    ),
                },
            )
        return list(unique.values())

    def _extract_concepts(self, doc: Doc) -> list[dict[str, Any]]:
        """Collect noun phrases and noun/proper-noun tokens as candidate concepts."""
        candidates: list[tuple[list[Token], str]] = []
        for phrase in doc.noun_chunks:
            tokens = [token for token in phrase if token.is_alpha]
            if tokens and any(token.pos_ in {"NOUN", "PROPN"} for token in tokens):
                candidates.append((tokens, "noun_phrase"))
        for token in doc:
            if token.is_alpha and token.pos_ in {"NOUN", "PROPN"}:
                candidates.append(([token], "noun_or_proper_noun"))

        concepts_by_form: dict[str, dict[str, Any]] = {}
        for tokens, method in candidates:
            normalized_words = [self._lemma(token) for token in tokens]
            normalized = " ".join(normalized_words)
            if not normalized:
                continue
            start = tokens[0].idx
            end = tokens[-1].idx + len(tokens[-1])
            occurrence = {
                "text": doc.text[start:end],
                "start": start,
                "end": end,
                "source_token_indices": [token.i for token in tokens],
                "extraction_method": method,
                "pos": [token.pos_ for token in tokens],
            }
            concept = concepts_by_form.setdefault(
                normalized,
                {
                    "normalized_form": normalized,
                    "occurrences": [],
                    "extraction_methods": [],
                },
            )
            duplicate_span = any(
                existing["start"] == start and existing["end"] == end
                for existing in concept["occurrences"]
            )
            if not duplicate_span:
                concept["occurrences"].append(occurrence)
            if method not in concept["extraction_methods"]:
                concept["extraction_methods"].append(method)

        concepts = list(concepts_by_form.values())
        for concept in concepts:
            concept["text"] = concept["occurrences"][0]["text"]
            concept["occurrence_count"] = len(concept["occurrences"])
        return concepts

    def _find_matches(
        self, doc: Doc, focus: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        words = [token for token in doc if token.is_alpha]
        direct: list[dict[str, Any]] = []
        normalized: list[dict[str, Any]] = []
        length = len(focus["surface_words"])

        for index in range(len(words) - length + 1):
            window = words[index : index + length]
            # A phrase may include hyphens or possessive apostrophes, but must
            # not bridge a comma, sentence boundary, paragraph boundary, or other punctuation.
            if any(
                not re.fullmatch(r"[\s'’\-‐‑–]*", doc.text[left.idx + len(left) : right.idx])
                or re.search(
                    r"(?:\r\n|\r|\n)[ \t]*(?:\r\n|\r|\n)",
                    doc.text[left.idx + len(left) : right.idx],
                )
                for left, right in zip(window, window[1:])
            ):
                continue
            surfaces = [token.text.casefold() for token in window]
            lemmas = [self._lemma(token) for token in window]
            if surfaces == focus["surface_words"]:
                match_type = "direct"
            elif lemmas == focus["normalized_words"]:
                match_type = "normalized"
            else:
                continue

            start = window[0].idx
            end = window[-1].idx + len(window[-1])
            evidence = {
                "observed_text": doc.text[start:end],
                "start": start,
                "end": end,
                "normalized_form": " ".join(lemmas),
                "source_token_indices": [token.i for token in window],
                "pos": [token.pos_ for token in window],
                "match_method": match_type,
                "evidence_source": "student_text_span",
            }
            (direct if match_type == "direct" else normalized).append(evidence)

        return direct, normalized

    def _wordnet_status(self, include_wordnet: bool) -> dict[str, Any]:
        if not include_wordnet:
            return {"available": False, "status": "disabled", "message": None}
        try:
            # Accessing a corpus method triggers NLTK's missing-resource check.
            wordnet.synsets("essay")
        except LookupError:
            return {
                "available": False,
                "status": "resource_missing",
                "message": "Install the corpus with nltk.download('wordnet').",
            }
        return {
            "available": True,
            "status": "available",
            "message": None,
            "version": wordnet.get_version(),
        }

    def _wordnet_suggestions(
        self,
        focus_results: list[dict[str, Any]],
        student_concepts: list[dict[str, Any]],
        *,
        lookup_trace: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        suggestions = []
        for focus in focus_results:
            if focus["observed"] or len(focus["normalized_words"]) != 1:
                continue
            focus_word = focus["normalized_words"][0]
            focus_synsets = {
                synset.name(): synset
                for pos in (focus["wordnet_pos"] or [None])
                for synset in wordnet.synsets(focus_word, pos=pos)
            }
            for concept in student_concepts:
                observed_words = concept["normalized_form"].split()
                if len(observed_words) != 1 or observed_words[0] == focus_word:
                    continue
                observed_word = observed_words[0]
                matching_occurrences = [
                    occurrence
                    for occurrence in concept["occurrences"]
                    if len(occurrence["source_token_indices"]) == 1
                ]
                for occurrence in matching_occurrences:
                    occurrence_pos = occurrence["pos"][0]
                    mapped_pos = self._wordnet_pos(occurrence_pos)
                    observed_synsets = {
                        synset.name()
                        for synset in wordnet.synsets(observed_word, pos=mapped_pos)
                    }
                    shared = focus_synsets.keys() & observed_synsets
                    if lookup_trace is not None:
                        lookup_trace.append(
                            {
                                "teacher_term": focus["term"],
                                "teacher_lemma": focus_word,
                                "teacher_pos": focus["wordnet_pos"],
                                "teacher_synset_ids": sorted(focus_synsets),
                                "observed_student_term": occurrence["text"],
                                "student_lemma": observed_word,
                                "student_pos": occurrence_pos,
                                "student_synset_ids": sorted(observed_synsets),
                                "shared_synset_ids": sorted(shared),
                                "candidate_emitted": len(shared) == 1,
                                "selection_condition": "Different single-word terms, compatible POS, and exactly one shared synset.",
                                "source_span": [occurrence["start"], occurrence["end"]],
                            }
                        )
                    # Multiple shared senses are too ambiguous to suggest here.
                    if len(shared) != 1:
                        continue
                    synset_id = next(iter(shared))
                    suggestions.append(
                        {
                            "teacher_term": focus["term"],
                            "observed_student_term": occurrence["text"],
                            "teacher_pos": focus["wordnet_pos"],
                            "observed_pos": occurrence_pos,
                            "relationship_type": "shared_synset_synonym_candidate",
                            "synset_id": synset_id,
                            "reason": "The lemmas share exactly one WordNet synset.",
                            "uncertainty": (
                                "Candidate only: WordNet senses are not disambiguated "
                                "against the sentence context. Not counted as confirmed coverage."
                            ),
                            "start": occurrence["start"],
                            "end": occurrence["end"],
                        }
                    )
        return suggestions

    @staticmethod
    def _lemma(token: Token) -> str:
        return (token.lemma_ or token.text).casefold()

    @staticmethod
    def _wordnet_pos(spacy_pos: str) -> str | None:
        return {"NOUN": "n", "PROPN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}.get(
            spacy_pos
        )

    def _with_related_concepts(self, result: dict[str, Any]) -> dict[str, Any]:
        """Add informational evidence without changing existing lexical observations.

        Keeping the extension here also preserves source locations of the existing
        matching helpers recorded in protected rule metadata.
        """
        from services.related_topic_concept_service import RelatedTopicConceptService

        if not hasattr(self, "related_concepts"):
            self.related_concepts = RelatedTopicConceptService()
        result["related_topic_concept_evidence"] = self.related_concepts.match(
            result["teacher_context"], result["linguistic_analysis"]
        )
        return result
