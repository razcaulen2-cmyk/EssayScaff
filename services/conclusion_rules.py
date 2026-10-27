"""Deterministic, evidence-linked observations for Conclusion writing."""

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
CLOSING_EXPRESSIONS = (
    "in conclusion", "in summary", "to summarize", "to sum up", "overall",
    "ultimately", "in the end", "all in all", "taken together", "therefore", "thus",
)
MODAL_OR_RECOMMENDATION_CUES = {
    "should", "could", "may", "might", "must", "recommend", "suggest", "need"
}


class ConclusionRuleBase:
    """Analyze Conclusion structure and lexical links without semantic approval."""

    def __init__(self, topic_service: TopicService | None = None) -> None:
        self.topic_service = topic_service or TopicService(NLPService())

    def analyze(
        self,
        conclusion_text: str,
        assignment_topic: str,
        focus_terms: list[str] | None = None,
        introduction_text: str | None = None,
        body_text: str | None = None,
        *,
        prepared_conclusion_analysis: dict[str, Any] | None = None,
        prepared_introduction_analysis: dict[str, Any] | None = None,
        prepared_body_analysis: dict[str, Any] | None = None,
        include_research_trace: bool = False,
    ) -> dict[str, Any]:
        if not isinstance(conclusion_text, str):
            raise TypeError("conclusion_text must be a string")
        if not isinstance(assignment_topic, str):
            raise TypeError("assignment_topic must be a string")

        # Conclusion writing is parsed once; prior sections are separate inputs.
        if prepared_conclusion_analysis is None:
            conclusion_result = self.topic_service.analyze(
                conclusion_text,
                assignment_topic,
                focus_terms,
                include_wordnet=True,
            )
        else:
            self.topic_service.validate_prepared_analysis(
                prepared_conclusion_analysis, conclusion_text, assignment_topic
            )
            conclusion_result = prepared_conclusion_analysis
        linguistic = conclusion_result["linguistic_analysis"]
        paragraph_spans = split_paragraph_spans(conclusion_text)
        paragraphs = self._paragraphs(conclusion_text, paragraph_spans, linguistic)
        clauses = clause_candidates_from_sentences(
            linguistic["sentences"], FINITE_TAGS, CLAUSE_DEPENDENCIES, SUBJECT_DEPENDENCIES
        )
        clauses = [self._mark_clause_source(candidate, "conclusion") for candidate in clauses]
        topic_matches = self._topic_matches(conclusion_result)
        presence = self._text_presence(conclusion_text, linguistic, paragraphs, clauses)
        list_finding = self._keyword_list_finding(conclusion_text, linguistic, paragraphs, clauses)
        conclusion_concepts = conclusion_result["student_concepts"]
        intro_result = self._analyze_prior(
            introduction_text,
            assignment_topic,
            focus_terms,
            prepared_introduction_analysis,
        )
        body_result = self._analyze_prior(
            body_text, assignment_topic, focus_terms, prepared_body_analysis
        )

        (
            intro_continuity,
            body_continuity,
            body_paragraph_distribution,
            prior_concept_sources,
        ) = self._cross_stage_comparisons(
            conclusion_concepts, intro_result, body_result, body_text,
            include_lookup_trace=include_research_trace,
        )
        sentence_segments = linguistic["sentences"]
        synthesis = self._synthesis_candidates(
            sentence_segments,
            clauses,
            conclusion_concepts,
            prior_concept_sources,
            introduction_text is not None or body_text is not None,
        )
        closure = self._closing_candidates(
            conclusion_text, sentence_segments, clauses, linguistic["tokens"]
        )
        new_material = self._new_material_observations(
            conclusion_concepts,
            prior_concept_sources,
            introduction_text is not None,
            body_text is not None,
            intro_continuity,
            body_continuity,
            excluded_concept_spans=closure["summary_expression_candidates"],
        )
        repetition = self._source_repetition(
            repetition_observations(sentence_segments, CONTENT_POS)
        )
        missing = self._missing_elements(
            presence,
            clauses,
            topic_matches,
            synthesis,
            closure,
        )
        events = self._rule_events(
            conclusion_text,
            presence,
            clauses,
            list_finding,
            topic_matches,
            intro_continuity,
            body_continuity,
            synthesis,
            closure,
            new_material,
            repetition,
            introduction_text,
            body_text,
        )

        return {
            "stage": "CONCLUSION",
            "assignment_topic": assignment_topic,
            "text_presence": presence,
            "conclusion_paragraphs": paragraphs,
            "linguistic_observations": linguistic,
            "linguistic_observations_source_section": "conclusion",
            "clause_candidates": clauses,
            "keyword_list_candidate": list_finding,
            "lexical_topic_evidence": {
                "focus_source": conclusion_result["teacher_context"]["focus_source"],
                "focus_terms": [item["term"] for item in conclusion_result["teacher_context"]["focus_terms"]],
                "observed_focus_terms": conclusion_result["focus_coverage"]["observed_focus_terms"],
                "unobserved_focus_terms": conclusion_result["focus_coverage"]["unobserved_focus_terms"],
                "matches": topic_matches,
                "wordnet_relationship_candidates": conclusion_result["wordnet"]["suggestions"],
                "limitation": "Focus-term matches and WordNet candidates do not establish meaningfulness or successful closure.",
            },
            "introduction_to_conclusion_continuity": intro_continuity,
            "body_to_conclusion_continuity": {
                **body_continuity,
                "body_paragraph_concept_distribution": body_paragraph_distribution,
            },
            "synthesis_structure_candidates": synthesis,
            "closure_candidates": closure,
            "new_material_observations": new_material,
            "repetition_observations": repetition,
            "missing_observable_elements": missing,
            "uncertainty": [
                "These rules describe lexical, sentence, and dependency evidence only.",
                "A final sentence or closing expression is not proof of effective rhetorical closure.",
                "Lexical overlap does not prove that the Conclusion restates, synthesizes, or supports earlier claims.",
                "No factual correctness, semantic intelligibility, essay quality, or readiness decision is made.",
            ],
            "rule_evidence": events,
            "interpretation_limit": (
                "Observations are not a conclusion-quality judgment or stage-readiness decision."
            ),
        }

    def _analyze_prior(
        self,
        text: str | None,
        topic: str,
        focus_terms: list[str] | None,
        prepared_analysis: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if text is None:
            return None
        if prepared_analysis is not None:
            self.topic_service.validate_prepared_analysis(prepared_analysis, text, topic)
            return prepared_analysis
        # Prior sections are distinct text inputs, not redundant parses of Conclusion.
        return self.topic_service.analyze(text, topic, focus_terms, include_wordnet=False)

    @staticmethod
    def _paragraphs(
        text: str, spans: list[tuple[int, int]], linguistic: dict[str, Any]
    ) -> list[dict[str, Any]]:
        paragraphs = []
        for index, (start, end) in enumerate(spans, start=1):
            tokens = [
                token for token in linguistic["tokens"]
                if start <= token["start"] and token["end"] <= end
            ]
            sentences = sentence_segments_in_span(
                linguistic["sentences"], text, start, end
            )
            paragraphs.append(
                {
                    "source_section": "conclusion",
                    "paragraph_index": index,
                    "text": text[start:end],
                    "start": start,
                    "end": end,
                    "substantive": any(token["is_alpha"] for token in tokens),
                    "counts": {
                        "alphabetic_word_count": sum(token["is_alpha"] for token in tokens),
                        "token_count": len(tokens),
                        "sentence_count": len(sentences),
                    },
                    "sentence_spans": [
                        {
                            **sentence,
                            "source_section": "conclusion",
                            "tokens": [
                                {**token, "source_section": "conclusion"}
                                for token in sentence["tokens"]
                            ],
                            "dependencies": [
                                {**dependency, "source_section": "conclusion"}
                                for dependency in sentence["dependencies"]
                            ],
                        }
                        for sentence in sentences
                    ],
                }
            )
        return paragraphs

    @staticmethod
    def _mark_clause_source(clause: dict[str, Any], source: str) -> dict[str, Any]:
        result = {**clause, "source_section": source}
        result["subject_evidence"] = [
            {**item, "source_section": source} for item in clause["subject_evidence"]
        ]
        result["predicate_evidence"] = {
            **clause["predicate_evidence"], "source_section": source
        }
        return result

    @staticmethod
    def _text_presence(
        text: str,
        linguistic: dict[str, Any],
        paragraphs: list[dict[str, Any]],
        clauses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        words = linguistic["counts"]["alphabetic_word_count"]
        if words:
            status = "SENTENCE_STRUCTURE_OBSERVED" if clauses else "FRAGMENTARY_OR_NONCLAUSAL_TEXT"
        elif text == "":
            status = "EMPTY"
        elif not text.strip():
            status = "WHITESPACE_ONLY"
        else:
            status = "PUNCTUATION_ONLY"
        noun_count = sum(
            1
            for token in linguistic["tokens"]
            if token["pos"] in {"NOUN", "PROPN"}
        )
        keyword_list = bool(words and not clauses and (len(linguistic["sentences"]) >= 3 or noun_count >= 4))
        return {
            "status": status,
            "alphabetic_word_count": words,
            "token_count": linguistic["counts"]["token_count"],
            "sentence_count": linguistic["counts"]["sentence_count"],
            "paragraph_count": len(paragraphs),
            "substantive_paragraph_count": sum(paragraph["substantive"] for paragraph in paragraphs),
            "keyword_list_candidate": keyword_list,
            "limitation": "Counts and fragment/list flags are structural observations, not quality judgments.",
        }

    @staticmethod
    def _keyword_list_finding(
        text: str,
        linguistic: dict[str, Any],
        paragraphs: list[dict[str, Any]],
        clauses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        keyword_list = ConclusionRuleBase._text_presence(text, linguistic, paragraphs, clauses)["keyword_list_candidate"]
        return {
            "candidate": keyword_list,
            "evidence": [
                {
                    "source_section": "conclusion",
                    "text": sentence["text"],
                    "start": sentence["start"],
                    "end": sentence["end"],
                }
                for sentence in linguistic["sentences"]
            ] if keyword_list else [],
            "trigger_condition": "No subject-linked finite clause with at least three sentence spans or four noun/proper-noun tokens.",
            "limitation": "A fragment or list may be a draft or stylistic choice; it is not a semantic label.",
        }

    @staticmethod
    def _topic_matches(topic_result: dict[str, Any]) -> list[dict[str, Any]]:
        matches = []
        for focus in topic_result["confirmed_lexical_observations"]:
            for method, key in (("direct", "direct_matches"), ("normalized", "normalized_matches")):
                for match in focus[key]:
                    matches.append(
                        {
                            "source_section": "conclusion",
                            "focus_term": focus["term"],
                            "match_method": method,
                            **match,
                        }
                    )
        return matches

    @staticmethod
    def _source_concepts(
        concepts: list[dict[str, Any]], section: str
    ) -> list[dict[str, Any]]:
        return [
            {
                **concept,
                "occurrences": [
                    {**occurrence, "source_section": section}
                    for occurrence in concept["occurrences"]
                ],
            }
            for concept in concepts
        ]

    @staticmethod
    def _body_paragraph_concepts(
        body_text: str | None, body_result: dict[str, Any] | None
    ) -> list[dict[str, Any]]:
        if body_text is None or body_result is None:
            return []
        spans = split_paragraph_spans(body_text)
        body_concepts = []
        for paragraph_index, (start, end) in enumerate(spans, start=1):
            concepts = []
            for concept in body_result["student_concepts"]:
                occurrences = [
                    {**occurrence, "source_section": "body", "paragraph_index": paragraph_index}
                    for occurrence in concept["occurrences"]
                    if start <= occurrence["start"] and occurrence["end"] <= end
                ]
                if occurrences:
                    concepts.append(
                        {
                            "normalized_form": concept["normalized_form"],
                            "occurrences": occurrences,
                        }
                    )
            body_concepts.append(
                {
                    "source_section": "body",
                    "paragraph_index": paragraph_index,
                    "start": start,
                    "end": end,
                    "concepts": concepts,
                    "normalized_concepts": [item["normalized_form"] for item in concepts],
                }
            )
        return body_concepts

    def _cross_stage_comparisons(
        self,
        conclusion_concepts: list[dict[str, Any]],
        introduction_result: dict[str, Any] | None,
        body_result: dict[str, Any] | None,
        body_text: str | None,
        *,
        include_lookup_trace: bool = False,
    ) -> tuple[
        dict[str, Any],
        dict[str, Any],
        list[dict[str, Any]],
        list[dict[str, Any]],
    ]:
        conclusion_concepts = self._source_concepts(conclusion_concepts, "conclusion")
        if introduction_result is None:
            introduction_comparison = {
                "status": "NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED",
                "direct_lexical_continuity": [],
                "lemma_normalized_continuity": [],
                "wordnet_relationship_candidates": {"status": "not_evaluated", "suggestions": []},
                "unmatched_source_concepts": [],
            }
            introduction_concepts = []
        else:
            introduction_concepts = self._source_concepts(
                introduction_result["student_concepts"], "introduction"
            )
            introduction_comparison = {
                "status": "LEXICAL_COMPARISON_AVAILABLE",
                **compare_stage_concepts(
                    introduction_concepts,
                    conclusion_concepts,
                    "introduction",
                    "conclusion",
                    wordnet_resource=wordnet,
                    include_lookup_trace=include_lookup_trace,
                ),
            }

        body_distribution = self._body_paragraph_concepts(body_text, body_result)
        if body_result is None:
            body_comparison = {
                "status": "NOT_AVAILABLE_NO_BODY_SUPPLIED",
                "direct_lexical_continuity": [],
                "lemma_normalized_continuity": [],
                "wordnet_relationship_candidates": {"status": "not_evaluated", "suggestions": []},
                "unmatched_source_concepts": [],
            }
            body_concepts = []
            body_distribution = []
        else:
            body_concepts_by_form: dict[str, dict[str, Any]] = {}
            for paragraph in body_distribution:
                for concept in paragraph["concepts"]:
                    form = concept["normalized_form"]
                    grouped = body_concepts_by_form.setdefault(
                        form, {"normalized_form": form, "occurrences": []}
                    )
                    grouped["occurrences"].extend(concept["occurrences"])
            body_concepts = list(body_concepts_by_form.values())
            body_comparison = {
                "status": "LEXICAL_COMPARISON_AVAILABLE",
                **compare_stage_concepts(
                    body_concepts,
                    conclusion_concepts,
                    "body",
                    "conclusion",
                    wordnet_resource=wordnet,
                    include_lookup_trace=include_lookup_trace,
                ),
            }
        prior_by_form: dict[str, dict[str, Any]] = {}
        for concept in introduction_concepts + body_concepts:
            form = concept["normalized_form"]
            grouped = prior_by_form.setdefault(
                form, {"normalized_form": form, "occurrences": []}
            )
            grouped["occurrences"].extend(concept["occurrences"])
        return (
            introduction_comparison,
            body_comparison,
            body_distribution,
            list(prior_by_form.values()),
        )

    @staticmethod
    def _synthesis_candidates(
        sentences: list[dict[str, Any]],
        clauses: list[dict[str, Any]],
        conclusion_concepts: list[dict[str, Any]],
        prior_concepts: list[dict[str, Any]],
        prior_context_available: bool,
    ) -> dict[str, Any]:
        if not prior_context_available:
            return {
                "status": "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED",
                "candidates": [],
                "limitation": "Synthesis continuity cannot be compared without Introduction or Body text.",
            }
        prior_by_form: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for concept in prior_concepts:
            prior_by_form[concept["normalized_form"]].extend(concept["occurrences"])
        clause_sents: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for clause in clauses:
            clause_sents[clause["sentence_index"]].append(clause)

        candidates = []
        for sentence_index, sentence in enumerate(sentences):
            if sentence_index not in clause_sents:
                continue
            matched_concepts = []
            for concept in conclusion_concepts:
                conclusion_occurrences = [
                    occurrence
                    for occurrence in concept["occurrences"]
                    if sentence["start"] <= occurrence["start"]
                    and occurrence["end"] <= sentence["end"]
                ]
                prior_occurrences = prior_by_form.get(concept["normalized_form"], [])
                if conclusion_occurrences and prior_occurrences:
                    matched_concepts.append(
                        {
                            "normalized_form": concept["normalized_form"],
                            "conclusion_occurrences": [
                                {**occurrence, "source_section": "conclusion"}
                                for occurrence in conclusion_occurrences
                            ],
                            "prior_occurrences": prior_occurrences,
                            "prior_sections": sorted(
                                {item["source_section"] for item in prior_occurrences}
                            ),
                        }
                    )
            if len(matched_concepts) >= 2:
                candidates.append(
                    {
                        "source_section": "conclusion",
                        "sentence_text": sentence["text"],
                        "sentence_span": [sentence["start"], sentence["end"]],
                        "clause_candidates": clause_sents[sentence_index],
                        "earlier_concept_matches": matched_concepts,
                        "evidence_type": "multiple_shared_concept_lemmas_plus_clause_structure",
                        "limitation": (
                            "Multiple lexical references in a clause are a synthesis-structure candidate, not proof of synthesis or logical connection."
                        ),
                    }
                )
        return {
            "status": "SYNTHESIS_STRUCTURE_CANDIDATE" if candidates else "NO_SYNTHESIS_STRUCTURE_CANDIDATE_OBSERVED",
            "candidates": candidates,
            "limitation": "No synthesis quality or semantic relationship is validated.",
        }

    @staticmethod
    def _closing_candidates(
        text: str,
        sentences: list[dict[str, Any]],
        clauses: list[dict[str, Any]],
        tokens: list[dict[str, Any]],
    ) -> dict[str, Any]:
        summary_cues = []
        for expression in CLOSING_EXPRESSIONS:
            for match in re.finditer(r"(?i)(?<!\w)" + re.escape(expression) + r"(?!\w)", text):
                summary_cues.append(
                    {
                        "source_section": "conclusion",
                        "text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "evidence_type": "direct_closing_expression",
                        "limitation": "A closing expression alone does not establish rhetorical closure.",
                    }
                )
        final_sentence = sentences[-1] if sentences else None
        final_clauses = [
            clause
            for clause in clauses
            if final_sentence is not None
            and clause["sentence_index"] == len(sentences) - 1
            and clause["dependency_type"] == "ROOT"
        ]
        final_cues = [
            {
                "source_section": "conclusion",
                "text": token["text"],
                "start": token["start"],
                "end": token["end"],
                "cue_type": "modal_or_recommendation_word_candidate",
                "evidence_type": "direct_token_observation",
            }
            for token in tokens
            if final_sentence is not None
            and final_sentence["start"] <= token["start"] < final_sentence["end"]
            and token["text"].casefold() in MODAL_OR_RECOMMENDATION_CUES
        ]
        candidates = []
        if final_clauses:
            candidates.append(
                {
                    "candidate_type": "final_sentence_clause",
                    "source_section": "conclusion",
                    "sentence_text": final_sentence["text"],
                    "sentence_span": [final_sentence["start"], final_sentence["end"]],
                    "clause_candidates": final_clauses,
                    "evidence_type": "final_position_plus_parser_labeled_clause",
                    "limitation": "A final clause is not confirmation of an effective ending.",
                }
            )
        if summary_cues:
            candidates.extend(
                {"candidate_type": "closing_expression", **cue}
                for cue in summary_cues
            )
        return {
            "status": "CLOSURE_STRUCTURE_CANDIDATE" if candidates else "NO_CLOSURE_CANDIDATE_OBSERVED",
            "candidates": candidates,
            "summary_expression_candidates": summary_cues,
            "final_sentence_modal_or_recommendation_cues": final_cues,
            "limitation": "Conclusion genres vary; no particular cue, recommendation, or summary template is required.",
        }

    @staticmethod
    def _new_material_observations(
        conclusion_concepts: list[dict[str, Any]],
        prior_concepts: list[dict[str, Any]],
        introduction_supplied: bool,
        body_supplied: bool,
        introduction_comparison: dict[str, Any],
        body_comparison: dict[str, Any],
        *,
        excluded_concept_spans: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if not introduction_supplied and not body_supplied:
            return {
                "status": "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED",
                "unobserved_concept_candidates": [],
                "phrase_combinations_of_observed_concepts": [],
                "surface_rewording_candidates": [],
                "candidate_paraphrase_relationships": [],
                "limitation": "Without prior text, earlier concept coverage cannot be compared.",
            }

        prior_forms = {concept["normalized_form"] for concept in prior_concepts}
        prior_words = {
            word
            for form in prior_forms
            for word in form.split()
        }
        novel_candidates = []
        known_word_combinations = []
        excluded_spans = [
            (item["start"], item["end"])
            for item in (excluded_concept_spans or [])
        ]
        for concept in conclusion_concepts:
            if concept["normalized_form"] in prior_forms:
                continue
            independent_occurrences = [
                occurrence
                for occurrence in concept["occurrences"]
                if not any(
                    start <= occurrence["start"] and occurrence["end"] <= end
                    for start, end in excluded_spans
                )
                if not ConclusionRuleBase._occurrence_is_nested_in_larger_phrase(
                    concept, occurrence, conclusion_concepts
                )
            ]
            if not independent_occurrences:
                continue
            occurrence = independent_occurrences[0]
            content_words = [
                lemma
                for lemma, pos in zip(
                    concept["normalized_form"].split(), occurrence["pos"]
                )
                if pos in CONTENT_POS
            ]
            unobserved_words = [word for word in content_words if word not in prior_words]
            record = {
                "normalized_form": concept["normalized_form"],
                "conclusion_occurrences": [
                    {**item, "source_section": "conclusion"}
                    for item in independent_occurrences
                ],
            }
            if unobserved_words:
                novel_candidates.append(
                    {
                        **record,
                        "unobserved_content_lemmas": unobserved_words,
                        "observation": "not lexically observed in the supplied prior sections",
                    }
                )
            elif content_words:
                known_word_combinations.append(
                    {
                        **record,
                        "observation": "phrase form not seen, but its content lemmas were observed earlier",
                        "limitation": "A new phrase is not necessarily new subject matter.",
                    }
                )
        paraphrases = (
            introduction_comparison["wordnet_relationship_candidates"].get("suggestions", [])
            + body_comparison["wordnet_relationship_candidates"].get("suggestions", [])
        )
        return {
            "status": (
                "COMPARISON_WITH_BOTH_PRIOR_SECTIONS"
                if introduction_supplied and body_supplied
                else "PARTIAL_PRIOR_CONTEXT"
            ),
            "prior_sections_supplied": {
                "introduction": introduction_supplied,
                "body": body_supplied,
            },
            "unobserved_concept_candidates": novel_candidates,
            "phrase_combinations_of_observed_concepts": known_word_combinations,
            "surface_rewording_candidates": (
                introduction_comparison["lemma_normalized_continuity"]
                + body_comparison["lemma_normalized_continuity"]
            ),
            "candidate_paraphrase_relationships": paraphrases,
            "limitation": (
                "Concepts not lexically observed in supplied sections are not necessarily new arguments; "
                "paraphrases and unavailable prior text can be missed."
            ),
        }

    @staticmethod
    def _occurrence_is_nested_in_larger_phrase(
        concept: dict[str, Any],
        occurrence: dict[str, Any],
        all_concepts: list[dict[str, Any]],
    ) -> bool:
        """Avoid reporting each component noun as a separate new concept candidate."""
        words = concept["normalized_form"].split()
        for parent in all_concepts:
            parent_words = parent["normalized_form"].split()
            if len(parent_words) <= len(words):
                continue
            contained_words = any(
                parent_words[index : index + len(words)] == words
                for index in range(len(parent_words) - len(words) + 1)
            )
            if not contained_words:
                continue
            if any(
                parent_occurrence["start"] <= occurrence["start"]
                and occurrence["end"] <= parent_occurrence["end"]
                and (
                    parent_occurrence["start"] < occurrence["start"]
                    or occurrence["end"] < parent_occurrence["end"]
                )
                for parent_occurrence in parent["occurrences"]
            ):
                return True
        return False

    @staticmethod
    def _missing_elements(
        presence: dict[str, Any],
        clauses: list[dict[str, Any]],
        matches: list[dict[str, Any]],
        synthesis: dict[str, Any],
        closure: dict[str, Any],
    ) -> list[dict[str, Any]]:
        missing = []
        if presence["alphabetic_word_count"] == 0:
            missing.append({"element": "alphabetic Conclusion text", "rule_id": "CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC"})
        if not clauses:
            missing.append({"element": "parser-labeled subject-linked clause candidate", "rule_id": "CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE"})
        if not matches:
            missing.append({"element": "configured topic-focus lexical match", "rule_id": "CONCLUSION.TOPIC.NO_FOCUS_MATCH"})
        if synthesis["status"] == "NO_SYNTHESIS_STRUCTURE_CANDIDATE_OBSERVED":
            missing.append({"element": "multiple earlier concepts in a parser-labeled Conclusion clause", "rule_id": "CONCLUSION.SYNTHESIS.NO_CANDIDATE"})
        if closure["status"] == "NO_CLOSURE_CANDIDATE_OBSERVED":
            missing.append({"element": "final clause or explicit closing expression candidate", "rule_id": "CONCLUSION.CLOSURE.NO_CANDIDATE"})
        return missing

    @staticmethod
    def _rule_events(
        text: str,
        presence: dict[str, Any],
        clauses: list[dict[str, Any]],
        keyword_list: dict[str, Any],
        topic_matches: list[dict[str, Any]],
        introduction_comparison: dict[str, Any],
        body_comparison: dict[str, Any],
        synthesis: dict[str, Any],
        closure: dict[str, Any],
        new_material: dict[str, Any],
        repetition: dict[str, Any],
        introduction_text: str | None,
        body_text: str | None,
    ) -> list[dict[str, Any]]:
        events = []

        def add(rule_id: str, trigger: str, evidence: list[dict[str, Any]], kind: str, limit: str, sources: list[str] | None = None) -> None:
            events.append(
                {
                    "rule_id": rule_id,
                    "triggering_condition": trigger,
                    "fired": True,
                    "actual_evidence": evidence,
                    "source_sections": sources or ["conclusion"],
                    "evidence_type": kind,
                    "limitations": limit,
                }
            )

        available_prior_sections = [
            section
            for section, supplied in (
                ("introduction", introduction_text is not None),
                ("body", body_text is not None),
            )
            if supplied
        ]

        if presence["alphabetic_word_count"]:
            add(
                "CONCLUSION.TEXT.PRESENT",
                "At least one alphabetic token occurs in Conclusion text.",
                [{"source_section": "conclusion", "text": text, "start": 0, "end": len(text)}],
                "direct_text_observation",
                "Word presence does not establish a developed conclusion.",
            )
        else:
            add(
                "CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC",
                "No alphabetic word was detected in Conclusion text.",
                [{"source_section": "conclusion", "text": text, "start": 0, "end": len(text)}] if text else [],
                "direct_text_observation",
                "No meaningfulness or quality judgment is made from empty/punctuation-only input.",
            )
        if clauses:
            add(
                "CONCLUSION.STRUCTURE.CLAUSE_CANDIDATE",
                "spaCy labeled finite predicates with dependency-linked subject evidence.",
                clauses,
                "spaCy_POS_and_dependency_observation",
                "A grammatical clause can still be semantically anomalous or contradictory.",
            )
        else:
            add(
                "CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE",
                "No subject-linked finite clause candidate was detected.",
                [],
                "absence_under_POS_and_dependency_heuristic",
                "This heuristic can miss fragments used intentionally or unusual sentence structures.",
            )
        if keyword_list["candidate"]:
            add(
                "CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE",
                keyword_list["trigger_condition"],
                keyword_list["evidence"],
                "sentence_and_POS_heuristic",
                keyword_list["limitation"],
            )
        if topic_matches:
            add(
                "CONCLUSION.TOPIC.FOCUS_MATCHES",
                "At least one focus phrase matched directly or by lemma normalization.",
                topic_matches,
                "direct_or_lemma_normalized_lexical_span",
                "Lexical overlap is not evidence of meaning, synthesis, or closure.",
            )
        else:
            add(
                "CONCLUSION.TOPIC.NO_FOCUS_MATCH",
                "No configured focus phrase matched the Conclusion text.",
                [],
                "lexical_matching_result_absence",
                "A paraphrase can be relevant without exact or lemma-matched vocabulary.",
            )

        for name, comparison, supplied, source in (
            ("INTRODUCTION", introduction_comparison, introduction_text is not None, "introduction"),
            ("BODY", body_comparison, body_text is not None, "body"),
        ):
            if not supplied:
                add(
                    f"CONCLUSION.CONTINUITY.{name}_UNAVAILABLE",
                    f"No {source.title()} text was supplied.",
                    [],
                    "input_availability",
                    f"Continuity with {source} cannot be inferred without that text.",
                    [source],
                )
            else:
                evidence = comparison["direct_lexical_continuity"] + comparison["lemma_normalized_continuity"]
                add(
                    f"CONCLUSION.CONTINUITY.{name}_LEXICAL_COMPARISON",
                    f"Compare concepts across supplied {source} and Conclusion text.",
                    evidence,
                    "direct_and_lemma_normalized_concept_comparison",
                    "Lexical continuity does not prove the Conclusion successfully restates or supports earlier claims.",
                    [source, "conclusion"],
                )
                suggestions = comparison["wordnet_relationship_candidates"].get("suggestions", [])
                if suggestions:
                    add(
                        f"CONCLUSION.CONTINUITY.{name}_WORDNET_CANDIDATE",
                        "A single POS-constrained shared synset was found for a concept pair.",
                        suggestions,
                        "WordNet_candidate_only",
                        "WordNet senses are not disambiguated in context.",
                        [source, "conclusion"],
                    )

        if synthesis["candidates"]:
            add(
                "CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE",
                "A Conclusion clause contains at least two concepts previously observed in Introduction/Body text.",
                synthesis["candidates"],
                "cross_stage_lexical_match_plus_clause_structure",
                synthesis["limitation"],
                available_prior_sections + ["conclusion"],
            )
        elif synthesis["status"] == "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED":
            add(
                "CONCLUSION.SYNTHESIS.UNAVAILABLE",
                "Neither Introduction nor Body text was supplied for cross-stage comparison.",
                [],
                "input_availability",
                synthesis["limitation"],
                ["conclusion"],
            )
        else:
            add(
                "CONCLUSION.SYNTHESIS.NO_CANDIDATE",
                "No sentence met the multiple-prior-concept plus clause heuristic.",
                [],
                "absence_under_cross_stage_lexical_heuristic",
                synthesis["limitation"],
                available_prior_sections + ["conclusion"],
            )
        if closure["candidates"]:
            add(
                "CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE",
                "A final parser-labeled clause or an explicit closing expression was observed.",
                closure["candidates"],
                "final_clause_or_direct_closing_expression",
                closure["limitation"],
            )
        else:
            add(
                "CONCLUSION.CLOSURE.NO_CANDIDATE",
                "No final clause or closing expression candidate was observed.",
                [],
                "absence_under_closing_structure_heuristic",
                closure["limitation"],
            )
        if closure["final_sentence_modal_or_recommendation_cues"]:
            add(
                "CONCLUSION.CLOSURE.MODAL_OR_RECOMMENDATION_CUE",
                "A modal or recommendation-associated word occurs in the final sentence.",
                closure["final_sentence_modal_or_recommendation_cues"],
                "direct_token_observation",
                "A modal may qualify a claim and does not by itself constitute a recommendation or effective ending.",
            )
        if new_material["unobserved_concept_candidates"]:
            add(
                "CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS",
                "Conclusion concepts were not lexically observed in supplied earlier sections.",
                new_material["unobserved_concept_candidates"],
                "cross_stage_normalized_concept_difference",
                new_material["limitation"],
                available_prior_sections + ["conclusion"],
            )
        if new_material["phrase_combinations_of_observed_concepts"]:
            add(
                "CONCLUSION.NEW_MATERIAL.KNOWN_CONCEPT_COMBINATION",
                "A Conclusion phrase form is unobserved although its content lemmas occurred in supplied prior text.",
                new_material["phrase_combinations_of_observed_concepts"],
                "normalized_content_word_comparison",
                "A new phrase can combine previously discussed concepts and is not necessarily new material.",
                available_prior_sections + ["conclusion"],
            )
        for field in (
            "repeated_surface_content_words",
            "repeated_normalized_content_terms",
            "repeated_sentence_openings",
        ):
            if repetition[field]:
                add(
                    "CONCLUSION.REPETITION." + field.upper(),
                    "Repeated conclusion content words, lemmas, or sentence openings were observed.",
                    repetition[field],
                    "direct_surface_or_lemma_count",
                    repetition["interpretation"],
                )
        add(
            "CONCLUSION.LIMITATION.NO_SEMANTIC_VALIDATION",
            "Always applied: Conclusion rules do not validate meaning, synthesis quality, facts, or readiness.",
            [],
            "system_scope_limitation",
            "No stage-ready decision or semantic quality judgment is implemented.",
        )
        add(
            "CONCLUSION.GOAL.REVIEW_TOPIC_AND_PRIOR_IDEAS",
            "The requested analysis stage is Conclusion.",
            [],
            "stage_scope_configuration",
            "This is a revision goal, not an effectiveness or readiness decision.",
        )
        return events

    @staticmethod
    def _source_repetition(repetition: dict[str, Any]) -> dict[str, Any]:
        result = dict(repetition)
        for field in (
            "repeated_surface_content_words",
            "repeated_normalized_content_terms",
            "repeated_sentence_openings",
        ):
            result[field] = [
                {
                    **item,
                    "occurrences": [
                        {**occurrence, "source_section": "conclusion"}
                        for occurrence in item["occurrences"]
                    ],
                }
                for item in repetition[field]
            ]
        return result
