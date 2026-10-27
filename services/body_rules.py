"""Deterministic, evidence-based observations for Body paragraphs."""

import re
from collections import defaultdict
from typing import Any

from nltk.corpus import wordnet

from services.nlp_service import NLPService
from services.stage_evidence import (
    clause_candidates_from_sentences,
    compare_stage_concepts,
    repetition_observations,
    sentence_segments_in_span,
    split_paragraph_spans,
)
from services.topic_service import TopicService


FINITE_TAGS = {"VB", "VBD", "VBP", "VBZ"}
CLAUSE_DEPENDENCIES = {"ROOT", "conj", "advcl", "ccomp", "xcomp", "relcl"}
SUBJECT_DEPENDENCIES = {"nsubj", "nsubjpass", "csubj", "csubjpass"}
CONTENT_POS = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}
TRANSITION_EXPRESSIONS = (
    "for example", "for instance", "in addition", "as a result", "in contrast",
    "by contrast", "however", "therefore", "consequently", "furthermore",
    "moreover", "similarly", "finally", "first", "second",
)
EXAMPLE_EXPRESSIONS = ("for example", "for instance", "such as", "including")


class BodyRuleBase:
    """Analyze Body paragraphs by reusing Phase 1–2 analysis of the full text."""

    def __init__(self, topic_service: TopicService | None = None) -> None:
        self.topic_service = topic_service or TopicService(NLPService())

    def analyze(
        self,
        body_text: str,
        assignment_topic: str,
        focus_terms: list[str] | None = None,
        introduction_text: str | None = None,
        *,
        prepared_body_analysis: dict[str, Any] | None = None,
        prepared_introduction_analysis: dict[str, Any] | None = None,
        include_research_trace: bool = False,
    ) -> dict[str, Any]:
        if not isinstance(body_text, str):
            raise TypeError("body_text must be a string")
        if not isinstance(assignment_topic, str):
            raise TypeError("assignment_topic must be a string")

        # One TopicService request parses the entire Body. All paragraph features
        # below are span-filtered views of its returned Doc-derived observations.
        if prepared_body_analysis is None:
            topic_result = self.topic_service.analyze(
                body_text,
                assignment_topic,
                focus_terms,
                include_wordnet=False,
            )
        else:
            self.topic_service.validate_prepared_analysis(
                prepared_body_analysis, body_text, assignment_topic
            )
            topic_result = prepared_body_analysis
        linguistic = topic_result["linguistic_analysis"]
        paragraph_spans = self._paragraph_spans(body_text)
        all_focus_matches = [
            match
            for match in self._all_focus_matches(topic_result)
            if any(start <= match["start"] and match["end"] <= end for start, end in paragraph_spans)
        ]
        paragraphs = [
            self._analyze_paragraph(
                index,
                start,
                end,
                body_text,
                linguistic,
                topic_result,
                all_focus_matches,
            )
            for index, (start, end) in enumerate(paragraph_spans, start=1)
        ]
        cross_paragraph = self._cross_paragraph_continuity(paragraphs)
        introduction_continuity = self._introduction_continuity(
            introduction_text,
            topic_result,
            body_text,
            assignment_topic,
            focus_terms,
            prepared_introduction_analysis,
            include_lookup_trace=include_research_trace,
        )
        missing = self._missing_elements(paragraphs, topic_result)
        rule_events = self._rule_events(
            paragraphs,
            cross_paragraph,
            introduction_continuity,
            topic_result["focus_coverage"],
        )

        return {
            "stage": "BODY",
            "input_text": body_text,
            "introduction_context": {
                "status": "SUPPLIED" if introduction_text is not None else "NOT_SUPPLIED",
                "text": introduction_text,
                "source": "Exact Introduction string supplied to this analysis request",
                "persistence_status": "NOT_DETERMINED_BY_ANALYSIS",
                "limitation": "Request text can include unsaved edits; analysis does not look up a saved Introduction version.",
            },
            "assignment_topic": assignment_topic,
            "paragraph_boundary_policy": (
                "One or more blank lines separate paragraphs. Leading/trailing whitespace "
                "is excluded from paragraph spans; internal newlines are preserved."
            ),
            "substantive_paragraph_count": sum(item["substantive"] for item in paragraphs),
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs,
            "lexical_topic_evidence": {
                "focus_source": topic_result["teacher_context"]["focus_source"],
                "focus_terms": [
                    item["term"] for item in topic_result["teacher_context"]["focus_terms"]
                ],
                "observed_focus_terms": list(dict.fromkeys(match["focus_term"] for match in all_focus_matches)),
                "unobserved_focus_terms": [
                    focus["term"]
                    for focus in topic_result["teacher_context"]["focus_terms"]
                    if not any(match["focus_term"] == focus["term"] for match in all_focus_matches)
                ],
                "observed_unique_focus_terms": len(
                    {match["focus_term"] for match in all_focus_matches}
                ),
                "total_unique_focus_terms": len(topic_result["teacher_context"]["focus_terms"]),
                "matches": all_focus_matches,
                "limitation": "Lexical matches show word overlap, not understanding, support, or correctness.",
            },
            "cross_paragraph_continuity": cross_paragraph,
            "introduction_to_body_continuity": introduction_continuity,
            "missing_observable_elements": missing,
            "uncertainty": [
                "Linguistic and lexical structure does not establish semantic intelligibility or logical coherence.",
                "A topic-sentence or supporting-detail candidate is not a confirmed rhetorical role or valid argument.",
                "Low lexical overlap may reflect paraphrase or focus terms that do not cover the student's wording.",
                "No factual correctness, academic quality, or Body readiness judgment is made.",
            ],
            "rule_evidence": rule_events,
            "prohibited_conclusions": [
                "BODY_READY",
                "meaningful or nonsensical",
                "proven topic support",
                "logically coherent",
                "stage unlocked",
            ],
        }

    @staticmethod
    def _paragraph_spans(text: str) -> list[tuple[int, int]]:
        """Expose shared blank-line segmentation for existing Body callers."""
        return split_paragraph_spans(text)

    def _analyze_paragraph(
        self,
        paragraph_index: int,
        start: int,
        end: int,
        body_text: str,
        linguistic: dict[str, Any],
        topic_result: dict[str, Any],
        all_focus_matches: list[dict[str, Any]],
    ) -> dict[str, Any]:
        paragraph_tokens = [
            token
            for token in linguistic["tokens"]
            if start <= token["start"] and token["end"] <= end
        ]
        paragraph_sentences = self._sentences_in_span(
            linguistic["sentences"], body_text, start, end
        )
        concepts = self._concepts_in_span(topic_result["student_concepts"], start, end)
        focus_matches = [
            match
            for match in all_focus_matches
            if start <= match["start"] and match["end"] <= end
        ]
        clause_candidates = self._paragraph_clause_candidates(paragraph_sentences)
        noun_count = sum(1 for token in paragraph_tokens if token["pos"] in {"NOUN", "PROPN"})
        fragmentary = bool(paragraph_tokens) and not clause_candidates
        keyword_list = fragmentary and (
            len(paragraph_sentences) >= 3 or noun_count >= 4
        )
        focus_by_sentence: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for match in focus_matches:
            for sentence_index, sentence in enumerate(paragraph_sentences):
                if sentence["start"] <= match["start"] and match["end"] <= sentence["end"]:
                    focus_by_sentence[sentence_index].append(match)

        repeated_concepts = [
            concept
            for concept in concepts
            if len(
                {
                    self._sentence_index_for_span(
                        concept_occurrence["start"], concept_occurrence["end"], paragraph_sentences
                    )
                    for concept_occurrence in concept["occurrences"]
                }
                - {-1}
            )
            >= 2
        ]
        recurring_forms = {concept["normalized_form"] for concept in repeated_concepts}
        topic_sentence_candidates = self._topic_sentence_candidates(
            paragraph_sentences,
            clause_candidates,
            focus_by_sentence,
            concepts,
            recurring_forms,
        )
        detail_candidates = self._supporting_detail_candidates(
            clause_candidates
        )
        sentence_unity = self._sentence_unity(paragraph_sentences)
        repetitions = self._repetition_observations(paragraph_sentences)
        examples = self._example_marker_evidence(body_text, start, end)
        substantive = any(token["is_alpha"] for token in paragraph_tokens)

        return {
            "paragraph_index": paragraph_index,
            "text": body_text[start:end],
            "start": start,
            "end": end,
            "substantive": substantive,
            "counts": {
                "alphabetic_word_count": sum(token["is_alpha"] for token in paragraph_tokens),
                "token_count": len(paragraph_tokens),
                "sentence_count": len(paragraph_sentences),
            },
            "clause_structure_candidates": clause_candidates,
            "fragment_or_list_candidate": {
                "fragmentary": fragmentary,
                "keyword_list_candidate": keyword_list,
                "noun_or_proper_noun_count": noun_count,
                "trigger_condition": (
                    "No subject-linked finite clause candidate plus at least three sentences "
                    "or four noun/proper-noun tokens for the list flag."
                ),
                "evidence": [
                    {"text": sentence["text"], "start": sentence["start"], "end": sentence["end"]}
                    for sentence in paragraph_sentences
                ] if fragmentary else [],
                "limitation": "This is a fragment/list candidate only; labels and fragments may be deliberate.",
            },
            "sentence_spans": paragraph_sentences,
            "paragraph_focus_candidates": concepts,
            "prominent_concept_candidates": [
                concept
                for concept in concepts
                if concept["occurrence_count"] > 1
                or any(
                    concept["normalized_form"] == match["normalized_form"]
                    for match in focus_matches
                )
            ],
            "observed_focus_terms": list(dict.fromkeys(match["focus_term"] for match in focus_matches)),
            "focus_term_evidence": focus_matches,
            "topic_sentence_candidates": topic_sentence_candidates,
            "supporting_detail_candidates": detail_candidates,
            "paragraph_unity_evidence": sentence_unity,
            "repetition_observations": repetitions,
            "example_or_explanation_markers": examples,
            "missing_observable_elements": self._paragraph_missing_elements(
                paragraph_index,
                clause_candidates,
                focus_matches,
                topic_sentence_candidates,
                detail_candidates,
            ),
            "limitations": [
                "Concepts are lexical candidates, not guaranteed paragraph ideas.",
                "Topic sentence candidates are not confirmed topic sentences.",
                "Clause structure and lexical repetition do not establish support or unity of meaning.",
            ],
        }

    @staticmethod
    def _sentences_in_span(
        sentences: list[dict[str, Any]], text: str, start: int, end: int
    ) -> list[dict[str, Any]]:
        """Return sentence/token evidence intersecting a paragraph without reparsing."""
        return sentence_segments_in_span(sentences, text, start, end)

    @staticmethod
    def _concepts_in_span(
        concepts: list[dict[str, Any]], start: int, end: int
    ) -> list[dict[str, Any]]:
        paragraph_concepts = []
        for concept in concepts:
            occurrences = [
                occurrence
                for occurrence in concept["occurrences"]
                if start <= occurrence["start"] and occurrence["end"] <= end
            ]
            if not occurrences:
                continue
            paragraph_concepts.append(
                {
                    "text": occurrences[0]["text"],
                    "normalized_form": concept["normalized_form"],
                    "occurrence_count": len(occurrences),
                    "occurrences": occurrences,
                    "extraction_methods": concept["extraction_methods"],
                }
            )
        return paragraph_concepts

    @staticmethod
    def _all_focus_matches(topic_result: dict[str, Any]) -> list[dict[str, Any]]:
        matches = []
        for focus in topic_result["confirmed_lexical_observations"]:
            for method, key in (("direct", "direct_matches"), ("normalized", "normalized_matches")):
                for item in focus[key]:
                    matches.append({"focus_term": focus["term"], "match_method": method, **item})
        return matches

    @staticmethod
    def _sentence_index_for_span(
        start: int, end: int, sentences: list[dict[str, Any]]
    ) -> int:
        for index, sentence in enumerate(sentences):
            if sentence["start"] <= start and end <= sentence["end"]:
                return index
        return -1

    @staticmethod
    def _paragraph_clause_candidates(
        sentences: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return clause_candidates_from_sentences(
            sentences, FINITE_TAGS, CLAUSE_DEPENDENCIES, SUBJECT_DEPENDENCIES
        )

    def _topic_sentence_candidates(
        self,
        sentences: list[dict[str, Any]],
        clause_candidates: list[dict[str, Any]],
        focus_by_sentence: dict[int, list[dict[str, Any]]],
        concepts: list[dict[str, Any]],
        recurring_forms: set[str],
    ) -> list[dict[str, Any]]:
        candidates_by_sentence: dict[int, dict[str, Any]] = {}
        for clause in clause_candidates:
            index = clause["sentence_index"]
            reasons = []
            lexical_matches = focus_by_sentence.get(index, [])
            if lexical_matches:
                reasons.append("configured_focus_term_match_in_sentence")
            recurring = [
                occurrence
                for concept in concepts
                if concept["normalized_form"] in recurring_forms
                for occurrence in concept["occurrences"]
                if self._sentence_index_for_span(
                    occurrence["start"], occurrence["end"], sentences
                )
                == index
            ]
            if recurring:
                reasons.append("concept_recurs_across_sentences_in_paragraph")
            if not reasons:
                continue
            candidate = candidates_by_sentence.setdefault(
                index,
                {
                    "sentence_index": index,
                    "sentence_span": clause["sentence_span"],
                    "sentence_text": clause["sentence_text"],
                    "candidate_reasons": [],
                    "clause_candidate_evidence": [],
                    "focus_match_evidence": lexical_matches,
                    "recurrent_concept_evidence": [],
                    "limitation": (
                        "The candidate is selected by lexical and syntactic cues; sentence order or a match does not "
                        "prove rhetorical role."
                    ),
                },
            )
            candidate["candidate_reasons"] = list(
                dict.fromkeys(candidate["candidate_reasons"] + reasons)
            )
            candidate["clause_candidate_evidence"].append(clause["predicate_evidence"])
            known_spans = {
                (item["start"], item["end"])
                for item in candidate["recurrent_concept_evidence"]
            }
            candidate["recurrent_concept_evidence"].extend(
                item
                for item in recurring
                if (item["start"], item["end"]) not in known_spans
            )
        return [candidates_by_sentence[index] for index in sorted(candidates_by_sentence)]

    @staticmethod
    def _supporting_detail_candidates(
        clause_candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        details = clause_candidates if len(clause_candidates) >= 2 else []
        # Example language is recorded separately and never suffices by itself.
        return {
            "status": "STRUCTURAL_DETAIL_CANDIDATES_OBSERVED" if details else "NO_STRUCTURAL_DETAIL_CANDIDATE",
            "candidate_kind": "additional_clause_or_statement_structure",
            "candidates": details,
            "evidence_type": "additional_parser_labeled_clause_or_sentence_candidate",
            "limitation": (
                "These may be elaboration candidates, not valid evidence or support; meaning and logical connection are not assessed."
            ),
        }

    @staticmethod
    def _sentence_unity(sentences: list[dict[str, Any]]) -> dict[str, Any]:
        pairs = []
        for index, (left, right) in enumerate(zip(sentences, sentences[1:])):
            left_content = [token for token in left["tokens"] if token["pos"] in CONTENT_POS and token["is_alpha"]]
            right_content = [token for token in right["tokens"] if token["pos"] in CONTENT_POS and token["is_alpha"]]
            left_surface = {token["text"].casefold(): token for token in left_content}
            right_surface = {token["text"].casefold(): token for token in right_content}
            left_lemma: dict[str, list[dict[str, Any]]] = defaultdict(list)
            right_lemma: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for token in left_content:
                left_lemma[token["lemma"].casefold()].append(token)
            for token in right_content:
                right_lemma[token["lemma"].casefold()].append(token)
            common_surface = left_surface.keys() & right_surface.keys()
            common_lemmas = left_lemma.keys() & right_lemma.keys()
            pairs.append(
                {
                    "sentence_pair": [index + 1, index + 2],
                    "left_sentence_span": [left["start"], left["end"]],
                    "right_sentence_span": [right["start"], right["end"]],
                    "direct_shared_content_terms": [
                        {
                            "term": word,
                            "left_span": [left_surface[word]["start"], left_surface[word]["end"]],
                            "right_span": [right_surface[word]["start"], right_surface[word]["end"]],
                        }
                        for word in sorted(common_surface)
                    ],
                    "normalized_shared_content_terms": [
                        {
                            "lemma": lemma,
                            "left_spans": [[token["start"], token["end"]] for token in left_lemma[lemma]],
                            "right_spans": [[token["start"], token["end"]] for token in right_lemma[lemma]],
                        }
                        for lemma in sorted(common_lemmas)
                    ],
                    "status": "LEXICAL_CONTINUITY_CANDIDATE" if common_lemmas else "NO_SHARED_NORMALIZED_CONTENT_TERM_OBSERVED",
                    "limitation": "Lexical overlap is not proof of unity; distinct words may still express related ideas.",
                }
            )
        return {
            "status": "NOT_APPLICABLE_SINGLE_SENTENCE" if len(sentences) < 2 else "PAIRWISE_LEXICAL_OBSERVATIONS",
            "sentence_pairs": pairs,
            "overall_score": None,
        }

    @staticmethod
    def _repetition_observations(sentences: list[dict[str, Any]]) -> dict[str, Any]:
        return repetition_observations(sentences, CONTENT_POS)

    @staticmethod
    def _example_marker_evidence(text: str, start: int, end: int) -> list[dict[str, Any]]:
        paragraph_text = text[start:end]
        markers = []
        for expression in EXAMPLE_EXPRESSIONS:
            for match in re.finditer(r"(?i)(?<!\w)" + re.escape(expression) + r"(?!\w)", paragraph_text):
                markers.append(
                    {
                        "text": match.group(0),
                        "start": start + match.start(),
                        "end": start + match.end(),
                        "evidence_type": "direct_discourse_expression",
                        "limitation": "A marker alone does not show that an example or explanation follows.",
                    }
                )
        return markers

    def _cross_paragraph_continuity(self, paragraphs: list[dict[str, Any]]) -> dict[str, Any]:
        pairs = []
        substantive_paragraphs = [paragraph for paragraph in paragraphs if paragraph["substantive"]]
        for left, right in zip(substantive_paragraphs, substantive_paragraphs[1:]):
            left_tokens = self._body_content_tokens(left)
            right_tokens = self._body_content_tokens(right)
            left_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
            right_surface: dict[str, list[dict[str, Any]]] = defaultdict(list)
            left_lemmas: dict[str, list[dict[str, Any]]] = defaultdict(list)
            right_lemmas: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for token in left_tokens:
                evidence = {"text": token["text"], "start": token["start"], "end": token["end"]}
                left_surface[token["text"].casefold()].append(evidence)
                left_lemmas[token["lemma"].casefold()].append(evidence)
            for token in right_tokens:
                evidence = {"text": token["text"], "start": token["start"], "end": token["end"]}
                right_surface[token["text"].casefold()].append(evidence)
                right_lemmas[token["lemma"].casefold()].append(evidence)
            common_direct = left_surface.keys() & right_surface.keys()
            common_lemmas = left_lemmas.keys() & right_lemmas.keys()
            transitions = self._transition_evidence(right["text"], right["start"])
            pairs.append(
                {
                    "paragraph_pair": [left["paragraph_index"], right["paragraph_index"]],
                    "direct_shared_terms": [
                        {
                            "term": term,
                            "left_spans": left_surface[term],
                            "right_spans": right_surface[term],
                        }
                        for term in sorted(common_direct)
                    ],
                    "normalized_shared_terms": [
                        {
                            "lemma": lemma,
                            "left_spans": left_lemmas[lemma],
                            "right_spans": right_lemmas[lemma],
                        }
                        for lemma in sorted(common_lemmas)
                    ],
                    "transition_expression_evidence": transitions,
                    "status": "LEXICAL_OR_TRANSITION_CANDIDATE" if common_lemmas or transitions else "NO_EXPLICIT_LEXICAL_LINK_OBSERVED",
                    "limitation": "Terms and transition expressions do not prove logical coherence or paragraph relevance.",
                }
            )
        return {
            "status": "NOT_APPLICABLE_SINGLE_PARAGRAPH" if len(substantive_paragraphs) < 2 else "PAIRWISE_OBSERVATIONS",
            "paragraph_pairs": pairs,
            "overall_score": None,
        }

    @staticmethod
    def _body_content_tokens(paragraph: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            token
            for sentence in paragraph["sentence_spans"]
            for token in sentence["tokens"]
            if token["is_alpha"] and token["pos"] in CONTENT_POS
        ]

    @staticmethod
    def _transition_evidence(paragraph_text: str, paragraph_start: int) -> list[dict[str, Any]]:
        evidence = []
        for expression in TRANSITION_EXPRESSIONS:
            for match in re.finditer(r"(?i)(?<!\w)" + re.escape(expression) + r"(?!\w)", paragraph_text):
                evidence.append(
                    {
                        "text": match.group(0),
                        "start": paragraph_start + match.start(),
                        "end": paragraph_start + match.end(),
                        "evidence_type": "direct_transition_expression",
                    }
                )
        return evidence

    def _introduction_continuity(
        self,
        introduction_text: str | None,
        body_result: dict[str, Any],
        body_text: str,
        assignment_topic: str,
        focus_terms: list[str] | None,
        prepared_introduction_analysis: dict[str, Any] | None = None,
        *,
        include_lookup_trace: bool = False,
    ) -> dict[str, Any]:
        if introduction_text is None:
            return {
                "status": "NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED",
                "direct_lexical_continuity": [],
                "lemma_normalized_continuity": [],
                "wordnet_relationship_candidates": {"status": "not_evaluated", "suggestions": []},
                "limitation": "No Introduction text was supplied for comparison.",
            }
        if prepared_introduction_analysis is None:
            intro_result = self.topic_service.analyze(
                introduction_text,
                assignment_topic,
                focus_terms,
                include_wordnet=False,
            )
        else:
            self.topic_service.validate_prepared_analysis(
                prepared_introduction_analysis, introduction_text, assignment_topic
            )
            intro_result = prepared_introduction_analysis
        intro_concepts = intro_result["student_concepts"]
        body_concepts = self._concepts_within_paragraphs(
            body_result["student_concepts"], body_text
        )
        comparison = compare_stage_concepts(
            intro_concepts,
            body_concepts,
            "introduction",
            "body",
            wordnet_resource=wordnet,
            include_lookup_trace=include_lookup_trace,
        )
        return {
            "status": "LEXICAL_COMPARISON_AVAILABLE",
            "direct_lexical_continuity": comparison["direct_lexical_continuity"],
            "lemma_normalized_continuity": comparison["lemma_normalized_continuity"],
            "wordnet_relationship_candidates": comparison["wordnet_relationship_candidates"],
            "unobserved_introduction_concepts": comparison["unmatched_source_concepts"],
            "limitation": (
                "Overlap cannot establish that Body paragraphs support an Introduction thesis; low overlap does not prove contradiction."
            ),
        }

    @staticmethod
    def _concepts_within_paragraphs(
        concepts: list[dict[str, Any]], body_text: str
    ) -> list[dict[str, Any]]:
        spans = BodyRuleBase._paragraph_spans(body_text)
        filtered = []
        for concept in concepts:
            occurrences = [
                occurrence
                for occurrence in concept["occurrences"]
                if any(start <= occurrence["start"] and occurrence["end"] <= end for start, end in spans)
            ]
            if occurrences:
                filtered.append({**concept, "occurrences": occurrences})
        return filtered

    @staticmethod
    def _missing_elements(
        paragraphs: list[dict[str, Any]], topic_result: dict[str, Any]
    ) -> list[dict[str, str]]:
        missing = []
        if not any(paragraph["substantive"] for paragraph in paragraphs):
            missing.append(
                {
                    "element": "nonblank Body paragraph",
                    "rule_id": "BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH",
                    "limitation": "This only reports that the submitted Body is blank or whitespace.",
                }
            )
        if not topic_result["focus_coverage"]["observed_focus_terms"]:
            missing.append(
                {
                    "element": "configured focus-term lexical match",
                    "rule_id": "BODY.TOPIC.NO_FOCUS_MATCH",
                    "limitation": "Paraphrases may be relevant but absent from the focus list.",
                }
            )
        return missing

    @staticmethod
    def _rule_events(
        paragraphs: list[dict[str, Any]],
        cross: dict[str, Any],
        intro_continuity: dict[str, Any],
        lexical_topic_evidence: dict[str, Any],
    ) -> list[dict[str, Any]]:
        events = []

        def event(rule_id: str, trigger: str, evidence: list[dict[str, Any]], kind: str, limit: str) -> None:
            events.append(
                {
                    "rule_id": rule_id,
                    "triggering_condition": trigger,
                    "triggered": True,
                    "actual_evidence": evidence,
                    "evidence_type": kind,
                    "limitations": limit,
                }
            )

        for paragraph in paragraphs:
            index = paragraph["paragraph_index"]
            event(
                f"BODY.P{index}.PARAGRAPH.SEGMENTED",
                "A nonblank line group separated by blank lines was found.",
                [{"paragraph_index": index, "start": paragraph["start"], "end": paragraph["end"], "text": paragraph["text"]}],
                "direct_text_boundary_observation",
                "Paragraph boundaries are inferred from blank lines, not rhetorical quality.",
            )
            if paragraph["fragment_or_list_candidate"]["keyword_list_candidate"]:
                event(
                    f"BODY.P{index}.PARAGRAPH.KEYWORD_LIST_CANDIDATE",
                    paragraph["fragment_or_list_candidate"]["trigger_condition"],
                    paragraph["fragment_or_list_candidate"]["evidence"],
                    "sentence_and_POS_heuristic",
                    paragraph["fragment_or_list_candidate"]["limitation"],
                )
            if paragraph["focus_term_evidence"]:
                event(
                    f"BODY.P{index}.PARAGRAPH.FOCUS_TERMS_OBSERVED",
                    "One or more configured focus terms or topic-derived candidates matched inside this paragraph span.",
                    paragraph["focus_term_evidence"],
                    "direct_or_lemma_normalized_lexical_span",
                    "This is lexical overlap, not proof of paragraph meaning or relevance.",
                )
            else:
                event(
                    f"BODY.P{index}.PARAGRAPH.FOCUS_TERMS_NOT_OBSERVED",
                    "No configured focus term matched inside this paragraph span.",
                    [{"start": paragraph["start"], "end": paragraph["end"], "text": paragraph["text"]}],
                    "lexical_matching_result_absence",
                    "Paraphrases may be relevant but not match teacher focus wording.",
                )
            if paragraph["topic_sentence_candidates"]:
                event(
                    f"BODY.P{index}.TOPIC_SENTENCE.CANDIDATE",
                    "A sentence has a clause candidate plus a configured focus-term match or recurring paragraph concept.",
                    paragraph["topic_sentence_candidates"],
                    "lexical_and_syntactic_heuristic",
                    "This does not confirm rhetorical function.",
                )
            else:
                event(
                    f"BODY.P{index}.TOPIC_SENTENCE.NO_CANDIDATE",
                    "No sentence met the focus-match or recurring-concept topic-sentence heuristic.",
                    [{"start": paragraph["start"], "end": paragraph["end"], "text": paragraph["text"]}],
                    "lexical_and_syntactic_heuristic_absence",
                    "A valid topic sentence may use paraphrase or a structure this heuristic misses.",
                )
            if paragraph["supporting_detail_candidates"]["candidates"]:
                event(
                    f"BODY.P{index}.SUPPORTING_DETAIL.CANDIDATE",
                    "Additional parser-labeled clause or sentence candidates occur in the paragraph.",
                    paragraph["supporting_detail_candidates"]["candidates"],
                    "dependency_structure_heuristic",
                    paragraph["supporting_detail_candidates"]["limitation"],
                )
            else:
                event(
                    f"BODY.P{index}.SUPPORTING_DETAIL.NOT_OBSERVED",
                    "No additional clause or statement candidate was detected within the paragraph.",
                    [{"start": paragraph["start"], "end": paragraph["end"], "text": paragraph["text"]}],
                    "syntactic_structure_heuristic_absence",
                    paragraph["supporting_detail_candidates"]["limitation"],
                )
            if paragraph["example_or_explanation_markers"]:
                event(
                    f"BODY.P{index}.EXAMPLE_OR_EXPLANATION_MARKER",
                    "An explicit example/explanation expression occurs in the paragraph text.",
                    paragraph["example_or_explanation_markers"],
                    "direct_expression_span",
                    "A discourse marker alone does not establish that an example or explanation follows.",
                )
            for pair in paragraph["paragraph_unity_evidence"]["sentence_pairs"]:
                event(
                    f"BODY.P{index}.UNITY.SENTENCE_PAIR_{pair['sentence_pair'][0]}_{pair['sentence_pair'][1]}",
                    "Adjacent sentence concepts were compared using content-token surfaces and lemmas.",
                    [pair],
                    "direct_and_lemma_normalized_lexical_evidence",
                    pair["limitation"],
                )
            for repetition_type in (
                "repeated_surface_content_words",
                "repeated_normalized_content_terms",
                "repeated_sentence_openings",
            ):
                observations = paragraph["repetition_observations"][repetition_type]
                if observations:
                    event(
                        f"BODY.P{index}.REPETITION." + repetition_type.upper(),
                        "The same surface word, normalized content term, or two-word opening occurs more than once.",
                        observations,
                        "direct_span_or_lemma_count",
                        paragraph["repetition_observations"]["interpretation"],
                    )

        if lexical_topic_evidence["total_unique_focus_terms"] and not lexical_topic_evidence["observed_focus_terms"]:
            event("BODY.TOPIC.NO_FOCUS_MATCH", "No configured focus term or topic-derived candidate matched in the Body text.", [], "lexical_matching_result", "Paraphrases may be relevant but not match the configured terms.")
        if not any(paragraph["substantive"] for paragraph in paragraphs):
            event(
                "BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH",
                "No alphabetic word was present inside a segmented paragraph.",
                [],
                "direct_text_and_token_observation",
                "This is an input observation, not a writing-quality decision.",
            )

        if cross["paragraph_pairs"]:
            event(
                "BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON",
                "At least two substantive paragraph spans are available for pairwise comparison.",
                cross["paragraph_pairs"],
                "lexical_and_transition_expression_observation",
                "Overlap or transitions do not prove coherent progression.",
            )
        if intro_continuity["status"] == "LEXICAL_COMPARISON_AVAILABLE":
            event(
                "BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON",
                "An Introduction string was supplied and its concept candidates were compared with the Body.",
                intro_continuity["direct_lexical_continuity"] + intro_continuity["lemma_normalized_continuity"],
                "direct_surface_and_lemma_normalized_concept_comparison",
                intro_continuity["limitation"],
            )
            if intro_continuity["wordnet_relationship_candidates"]["suggestions"]:
                event(
                    "BODY.INTRO_CONTINUITY.WORDNET_CANDIDATES",
                    "POS-constrained single-word concepts share exactly one WordNet synset.",
                    intro_continuity["wordnet_relationship_candidates"]["suggestions"],
                    "WordNet_candidate_only",
                    intro_continuity["wordnet_relationship_candidates"]["limitation"],
                )
        event(
            "BODY.GOAL.DEVELOP_BODY_IDEAS",
            "The requested analysis stage is Body.",
            [],
            "stage_scope_configuration",
            "This is a revision goal, not a readiness or quality decision.",
        )
        event(
            "BODY.LIMITATION.NO_SEMANTIC_VALIDATION",
            "Always applied: this service does not validate meaning, support, logic, or facts.",
            [],
            "system_scope_limitation",
            "Structural and lexical evidence is not semantic validation.",
        )
        return events

    @staticmethod
    def _paragraph_missing_elements(
        paragraph_index: int,
        clauses: list[dict[str, Any]],
        focus_matches: list[dict[str, Any]],
        topic_sentence_candidates: list[dict[str, Any]],
        supporting_details: dict[str, Any],
    ) -> list[dict[str, str]]:
        missing = []
        if not clauses:
            missing.append(
                {
                    "element": "subject-linked clause candidate",
                    "rule_id": f"BODY.P{paragraph_index}.TOPIC_SENTENCE.NO_CANDIDATE",
                    "limitation": "The parser heuristic may miss valid fragments or unusual constructions.",
                }
            )
        if not focus_matches:
            missing.append(
                {
                    "element": "configured focus-term match in this paragraph",
                    "rule_id": f"BODY.P{paragraph_index}.PARAGRAPH.FOCUS_TERMS_NOT_OBSERVED",
                    "limitation": "Paraphrases may be relevant but not match configured focus wording.",
                }
            )
        if not topic_sentence_candidates:
            missing.append(
                {
                    "element": "topic sentence candidate under current lexical/structural rules",
                    "rule_id": f"BODY.P{paragraph_index}.TOPIC_SENTENCE.NO_CANDIDATE",
                    "limitation": "A valid topic sentence may use wording or structure this heuristic misses.",
                }
            )
        if not supporting_details["candidates"]:
            missing.append(
                {
                    "element": "additional clause or statement candidate",
                    "rule_id": f"BODY.P{paragraph_index}.SUPPORTING_DETAIL.NOT_OBSERVED",
                    "limitation": "Other forms of development are not captured by this structural rule.",
                }
            )
        return missing
