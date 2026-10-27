"""Deterministic, evidence-linked structural observations for introductions.

These rules identify linguistic and lexical candidates. They do not determine
semantic intelligibility, logical quality, factual truth, or essay readiness.
"""

from typing import Any

from services.feedback_service import BROAD_FOCUS_TERMS
from services.nlp_service import NLPService
from services.topic_service import TopicService


FINITE_TAGS = {"VB", "VBD", "VBP", "VBZ"}
CLAUSE_DEPENDENCIES = {"ROOT", "conj", "advcl", "ccomp", "xcomp", "relcl"}
SUBJECT_DEPENDENCIES = {"nsubj", "nsubjpass", "csubj", "csubjpass"}
CLAUSE_SUBORDINATORS = {
    "although", "as", "because", "before", "if", "once", "since", "though",
    "unless", "until", "when", "whereas", "while",
}
RULE_LIMIT = (
    "A parser or lexical observation does not establish meaning, coherence, relevance, "
    "factual truth, or academic quality."
)

# The position check runs only for assignments that explicitly ask the writer to
# choose a side. Each cue is a fixed, inspectable phrase of the assignment topic.
ARGUMENTATIVE_PHRASE_CUES = (
    "agree or disagree",
    "take a position",
    "take a stand",
    "argue for or against",
    "for or against",
    "your opinion",
)
POSITION_MODAL_CUES = {"should", "must"}
POSITION_STANCE_VERBS_FOR = {"support", "agree", "favor", "believe", "think", "recommend"}
POSITION_STANCE_VERBS_AGAINST = {"oppose", "disagree", "reject"}
POSITION_FIRST_PERSON_SUBJECTS = {"i", "we"}
POSITION_LIMITATION = (
    "Position cues are fixed word and parse patterns: a modal or stance verb plus a "
    "specific assignment-word match in the same sentence. They do not verify that the "
    "position is argued, supported, or clearly expressed, and paraphrased positions "
    "without these cues are not detected."
)


class IntroductionRuleBase:
    """Analyze observable introduction structure using the existing TopicService."""

    def __init__(self, topic_service: TopicService | None = None) -> None:
        self.topic_service = topic_service or TopicService(NLPService())

    def analyze(
        self,
        student_text: str,
        assignment_topic: str,
        focus_terms: list[str] | None = None,
        *,
        prepared_topic_analysis: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return rule findings based on Phase 1 and Phase 2 evidence.

        TopicService parses the student text once and returns the Phase 1 Doc
        analysis alongside Phase 2 lexical matches. No further student parse is
        performed here.
        """
        if prepared_topic_analysis is None:
            topic_result = self.topic_service.analyze(
                student_text,
                assignment_topic,
                focus_terms,
                include_wordnet=False,
            )
        else:
            self.topic_service.validate_prepared_analysis(
                prepared_topic_analysis, student_text, assignment_topic
            )
            topic_result = prepared_topic_analysis
        linguistic = topic_result["linguistic_analysis"]
        sentences = linguistic["sentences"]
        word_count = linguistic["counts"]["alphabetic_word_count"]
        topic_observations = topic_result["confirmed_lexical_observations"]
        matches = self._all_matches(topic_observations)
        clause_candidates = self._clause_candidates(sentences)
        central_candidates = [
            candidate for candidate in clause_candidates if candidate["is_root_clause"]
        ]
        list_finding = self._list_or_fragment_finding(
            sentences, linguistic["tokens"], word_count, clause_candidates, central_candidates
        )
        incomplete_subordinators = self._incomplete_subordinator_evidence(sentences)
        context_candidates = self._context_candidates(central_candidates, matches)
        development = self._development_finding(
            clause_candidates, incomplete_subordinators
        )
        reason_clause = self._reason_clause_lexical_check(sentences, matches)
        position = self._position_evidence(
            assignment_topic,
            sentences,
            matches,
            central_candidates,
            topic_result["focus_coverage"]["observed_focus_terms"],
        )
        events = self._rule_events(
            student_text,
            word_count,
            sentences,
            central_candidates,
            list_finding,
            topic_observations,
            context_candidates,
            incomplete_subordinators,
            development,
            reason_clause,
            position,
        )
        missing = self._missing_elements(
            word_count,
            central_candidates,
            topic_result["focus_coverage"]["observed_focus_terms"],
            development,
            position,
        )

        from services.introduction_sentence_evidence import CONDITION, LIMITATION, REVIEW_RULE, sentence_topic_evidence
        sentence_topic = sentence_topic_evidence(topic_result)
        if sentence_topic["review_candidates"]:
            events.append({"rule_id": REVIEW_RULE, "triggering_condition": CONDITION, "triggered": True,
                           "evidence": sentence_topic["review_candidates"],
                           "evidence_type": "sentence_focus_and_neighbor_wording_observation", "limitation": LIMITATION})

        if word_count == 0:
            structural_status = "INSUFFICIENT_OBSERVABLE_STRUCTURE"
            if student_text == "":
                presence_status = "EMPTY"
            elif not student_text.strip():
                presence_status = "WHITESPACE_ONLY"
            else:
                presence_status = "PUNCTUATION_ONLY"
        elif not clause_candidates:
            structural_status = "INSUFFICIENT_OBSERVABLE_STRUCTURE"
            presence_status = "FRAGMENTARY_OR_NONCLAUSAL_TEXT"
        elif incomplete_subordinators:
            structural_status = "REQUIRES_REVIEW"
            presence_status = "SENTENCE_STRUCTURE_OBSERVED"
        elif not central_candidates:
            structural_status = "INSUFFICIENT_OBSERVABLE_STRUCTURE"
            presence_status = "SENTENCE_STRUCTURE_OBSERVED"
        else:
            structural_status = "STRUCTURAL_CANDIDATE"
            presence_status = "SENTENCE_STRUCTURE_OBSERVED"

        return {
            "stage": "INTRODUCTION",
            "input_text": student_text,
            "assignment_topic": assignment_topic,
            "linguistic_observations": linguistic,
            "text_presence": {
                "status": presence_status,
                "alphabetic_word_count": word_count,
                "sentence_count": len(sentences),
                "token_count": linguistic["counts"]["token_count"],
                "substantive_sentence_candidate_observed": bool(clause_candidates),
            },
            "observable_structure": {
                "summary_status": structural_status,
                "sentence_spans": [
                    {"text": sentence["text"], "start": sentence["start"], "end": sentence["end"]}
                    for sentence in sentences
                ],
                "central_direction_candidates": central_candidates,
                "introductory_context_candidates": context_candidates,
                "list_or_fragment_candidate": list_finding,
                "incomplete_subordinator_candidates": incomplete_subordinators,
            },
            "central_direction_candidate": {
                "status": "CANDIDATE_FOUND" if central_candidates else "NO_STRUCTURAL_CANDIDATE_FOUND",
                "candidates": central_candidates,
                "limitation": (
                    "A parser-labeled clause is not a validated thesis, meaningful proposition, or readiness decision."
                ),
            },
            "lexical_topic_evidence": {
                "focus_source": topic_result["teacher_context"]["focus_source"],
                "focus_terms": [item["term"] for item in topic_result["teacher_context"]["focus_terms"]],
                "observed_focus_terms": topic_result["focus_coverage"]["observed_focus_terms"],
                "unobserved_focus_terms": topic_result["focus_coverage"]["unobserved_focus_terms"],
                "observed_unique_focus_terms": topic_result["focus_coverage"]["observed_unique_focus_terms"],
                "total_unique_focus_terms": topic_result["focus_coverage"]["total_unique_focus_terms"],
                "matches": matches,
                "limitation": "Lexical overlap is not proof of topic understanding or meaningful explanation.",
            },
            "development_evidence": development,
            "reason_clause_evidence": reason_clause,
            "position_statement_evidence": position,
            "sentence_topic_evidence": sentence_topic,
            "missing_observable_elements": missing,
            "uncertainty": [
                "These rules use linguistic structure and lexical overlap only.",
                "A grammatical clause can be semantically anomalous or contradictory.",
                "No semantic intelligibility, logical coherence, or factual correctness judgment is made.",
                "A central-direction candidate is not a validated thesis or a readiness decision.",
                "A recorded position cue is not a verified argument, and paraphrased positions may not be detected.",
            ],
            "rule_evidence": events,
            "prohibited_conclusions": [
                "meaningful or nonsensical",
                "academically good or poor",
                "ready or not ready",
                "stage unlocked",
            ],
        }

    @staticmethod
    def _all_matches(topic_observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        matches = []
        for focus in topic_observations:
            for method, key in (
                ("direct", "direct_matches"),
                ("normalized", "normalized_matches"),
            ):
                for evidence in focus[key]:
                    matches.append(
                        {
                            "focus_term": focus["term"],
                            "match_method": method,
                            **evidence,
                        }
                    )
        return matches

    @staticmethod
    def _assignment_argumentativeness(assignment_topic: str) -> dict[str, Any]:
        """Record only fixed, inspectable cues that the assignment asks for a side."""
        topic = assignment_topic.strip().casefold()
        matched_phrases = [cue for cue in ARGUMENTATIVE_PHRASE_CUES if cue in topic]
        first_question_word = topic.split("?", 1)[0].split(":", 1)[0].strip().split(" ", 1)
        modal_question = (
            len(first_question_word) >= 2
            and first_question_word[0] in POSITION_MODAL_CUES
        )
        if matched_phrases:
            basis = {"cue_type": "assignment_phrase", "matched_cues": matched_phrases}
        elif modal_question:
            basis = {"cue_type": "modal_question", "matched_cues": [first_question_word[0]]}
        else:
            basis = {"cue_type": None, "matched_cues": []}
        return {
            "is_argumentative": bool(matched_phrases or modal_question),
            "basis": basis,
            "limitation": (
                "Argumentativeness is inferred from fixed assignment-wording cues only; "
                "an argumentative assignment described with other wording is not detected."
            ),
        }

    @staticmethod
    def _position_evidence(
        assignment_topic: str,
        sentences: list[dict[str, Any]],
        matches: list[dict[str, Any]],
        central_candidates: list[dict[str, Any]],
        observed_focus_terms: list[str],
    ) -> dict[str, Any]:
        """Find explicit position cues: a topic modal or a first-person stance verb.

        A cue counts only when the same sentence also contains a specific
        (non-broad) assignment-word match, so a modal sentence about an
        unrelated topic does not count as a position on this assignment.
        """
        argumentativeness = IntroductionRuleBase._assignment_argumentativeness(assignment_topic)
        specific_matches = [
            match
            for match in matches
            if match["focus_term"].strip().casefold() not in BROAD_FOCUS_TERMS
        ]
        specific_observed = [
            term
            for term in observed_focus_terms
            if term.strip().casefold() not in BROAD_FOCUS_TERMS
        ]
        positions: list[dict[str, Any]] = []
        if argumentativeness["is_argumentative"]:
            for sentence_index, sentence in enumerate(sentences):
                sentence_matches = [
                    match
                    for match in specific_matches
                    if match["start"] >= sentence["start"] and match["end"] <= sentence["end"]
                ]
                if not sentence_matches:
                    continue
                dependencies = sentence["dependencies"]
                # spaCy attaches a subject and negation to the main verb, while a
                # modal is only an aux dependent of that verb, so both the cue
                # token and its head verb are accepted as the subject's head.
                head_by_start = {
                    dependency["start"]: dependency["head_start"]
                    for dependency in dependencies
                }
                for token in sentence["tokens"]:
                    cue_head_starts = {token["start"]}
                    if token["start"] in head_by_start:
                        cue_head_starts.add(head_by_start[token["start"]])
                    subject = next(
                        (
                            dependency
                            for dependency in dependencies
                            if dependency["head_start"] in cue_head_starts
                            and dependency["dependency"] in SUBJECT_DEPENDENCIES
                        ),
                        None,
                    )
                    if subject is None:
                        continue
                    lemma = token["lemma"].casefold()
                    if (
                        token["pos"] == "AUX"
                        and token["tag"] == "MD"
                        and lemma in POSITION_MODAL_CUES
                    ):
                        negated = any(
                            dependency["dependency"] == "neg"
                            and dependency["head_start"] in cue_head_starts
                            for dependency in dependencies
                        )
                        positions.append(
                            {
                                "sentence_index": sentence_index,
                                "sentence_text": sentence["text"],
                                "sentence_start": sentence["start"],
                                "sentence_end": sentence["end"],
                                "cue_type": "modal",
                                "cue_token": {
                                    "text": token["text"],
                                    "start": token["start"],
                                    "end": token["end"],
                                    "lemma": token["lemma"],
                                    "pos": token["pos"],
                                    "tag": token["tag"],
                                    "dependency": token["dependency"],
                                },
                                "subject_evidence": {
                                    "text": subject["text"],
                                    "start": subject["start"],
                                    "end": subject["end"],
                                    "dependency": subject["dependency"],
                                },
                                "stance": "MODAL_NEGATED" if negated else "MODAL_AFFIRMED",
                                "topic_match_evidence": sentence_matches,
                                "evidence_type": "POS_and_dependency_plus_lexical_match_heuristic",
                                "limitation": POSITION_LIMITATION,
                            }
                        )
                        break
                    if token["pos"] == "VERB" and (
                        lemma in POSITION_STANCE_VERBS_FOR
                        or lemma in POSITION_STANCE_VERBS_AGAINST
                    ):
                        if subject["text"].casefold() not in POSITION_FIRST_PERSON_SUBJECTS:
                            continue
                        positions.append(
                            {
                                "sentence_index": sentence_index,
                                "sentence_text": sentence["text"],
                                "sentence_start": sentence["start"],
                                "sentence_end": sentence["end"],
                                "cue_type": "stance_verb",
                                "cue_token": {
                                    "text": token["text"],
                                    "start": token["start"],
                                    "end": token["end"],
                                    "lemma": token["lemma"],
                                    "pos": token["pos"],
                                    "tag": token["tag"],
                                    "dependency": token["dependency"],
                                },
                                "subject_evidence": {
                                    "text": subject["text"],
                                    "start": subject["start"],
                                    "end": subject["end"],
                                    "dependency": subject["dependency"],
                                },
                                "stance": (
                                    "SUPPORTING"
                                    if lemma in POSITION_STANCE_VERBS_FOR
                                    else "OPPOSING"
                                ),
                                "topic_match_evidence": sentence_matches,
                                "evidence_type": "POS_and_dependency_plus_lexical_match_heuristic",
                                "limitation": POSITION_LIMITATION,
                            }
                        )
                        break
        if not argumentativeness["is_argumentative"]:
            status = "CHECK_NOT_APPLICABLE_INFORMATIONAL_ASSIGNMENT"
        elif positions:
            status = "RELEVANT_POSITION_OBSERVED"
        elif specific_observed and central_candidates:
            status = "NO_RELEVANT_POSITION_OBSERVED"
        else:
            status = "INSUFFICIENT_TOPIC_EVIDENCE_FOR_POSITION_CHECK"
        return {
            "assignment_argumentativeness": argumentativeness,
            "status": status,
            "position_statements": positions,
            "specific_focus_terms_observed": specific_observed,
            "topic_discussion_matches": specific_matches,
            "trigger_condition": (
                "The assignment wording contains a fixed argumentativeness cue, a specific "
                "assignment-word match and a subject-predicate candidate were observed, and no "
                "sentence pairs a topic modal or first-person stance verb with a specific match."
            ),
            "evidence_type": "POS_and_dependency_plus_lexical_match_heuristic",
            "limitation": POSITION_LIMITATION,
        }

    @staticmethod
    def _clause_candidates(sentences: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates = []
        for sentence_index, sentence in enumerate(sentences):
            deps = sentence["dependencies"]
            token_by_start = {item["start"]: item for item in sentence["tokens"]}
            for token in sentence["tokens"]:
                finite_auxiliaries = [
                    token_by_start[dep["start"]] for dep in deps
                    if dep["head_start"] == token["start"] and dep["dependency"] in {"aux", "auxpass"}
                    and dep["start"] in token_by_start
                    and token_by_start[dep["start"]]["pos"] == "AUX"
                    and token_by_start[dep["start"]]["tag"] in {"MD", "VBD", "VBP", "VBZ"}
                ]
                if (
                    token["pos"] not in {"VERB", "AUX"}
                    or not (token["tag"] in FINITE_TAGS or (token["tag"] in {"VBN", "VBG"} and finite_auxiliaries))
                    or token["dependency"] not in CLAUSE_DEPENDENCIES
                ):
                    continue
                subject_evidence = [
                    {
                        "text": dependency["text"],
                        "start": dependency["start"],
                        "end": dependency["end"],
                        "dependency": dependency["dependency"],
                    }
                    for dependency in deps
                    if dependency["dependency"] in SUBJECT_DEPENDENCIES
                    and dependency["head_start"] == token["start"]
                ]
                if not subject_evidence:
                    continue
                complements = [
                    {
                        "text": dependency["text"],
                        "start": dependency["start"],
                        "end": dependency["end"],
                        "dependency": dependency["dependency"],
                    }
                    for dependency in deps
                    if dependency["head_start"] == token["start"]
                    and dependency["dependency"]
                    in {"dobj", "obj", "attr", "acomp", "ccomp", "xcomp", "oprd"}
                ]
                candidates.append(
                    {
                        "sentence_index": sentence_index,
                        "sentence_text": sentence["text"],
                        "sentence_start": sentence["start"],
                        "sentence_end": sentence["end"],
                        "subject_evidence": subject_evidence,
                        "predicate_evidence": {
                            "text": token["text"],
                            "start": token["start"],
                            "end": token["end"],
                            "pos": token["pos"],
                            "tag": token["tag"],
                            "dependency": token["dependency"],
                        },
                        "complement_evidence": complements,
                        "is_root_clause": token["dependency"] == "ROOT",
                        "evidence_type": "spaCy_dependency_and_POS_heuristic",
                        "limitation": (
                            "A subject-predicate parse does not verify the proposition's meaning or validity."
                        ),
                    }
                )
                if token["tag"] not in FINITE_TAGS:
                    candidates[-1]["finite_auxiliary_evidence"] = finite_auxiliaries
        return candidates

    @staticmethod
    def _list_or_fragment_finding(
        sentences: list[dict[str, Any]],
        tokens: list[dict[str, Any]],
        word_count: int,
        clause_candidates: list[dict[str, Any]],
        central_candidates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        clause_sentence_indices = {item["sentence_index"] for item in clause_candidates}
        root_clause_sentence_indices = {
            item["sentence_index"] for item in central_candidates
        }
        non_clause_sentences = [
            sentence
            for index, sentence in enumerate(sentences)
            if index not in clause_sentence_indices
        ]
        noun_count = sum(1 for token in tokens if token["pos"] in {"NOUN", "PROPN"})
        has_text = word_count > 0
        no_complete_clause = has_text and not clause_candidates
        list_candidate = no_complete_clause and (
            len(non_clause_sentences) >= 3 or noun_count >= 4
        )
        return {
            "fragmentary_text_candidate": no_complete_clause,
            "keyword_list_candidate": list_candidate,
            "sentence_count_without_root_subject_predicate": len(sentences) - len(root_clause_sentence_indices),
            "sentence_count_without_subject_linked_finite_clause": len(non_clause_sentences),
            "noun_or_proper_noun_count": noun_count,
            "trigger_condition": (
                "No parser-labeled finite clause with linked subject, plus at least three "
                "sentence spans without such a clause or at least four noun/proper-noun tokens."
            ),
            "evidence": [
                {"text": item["text"], "start": item["start"], "end": item["end"]}
                for item in non_clause_sentences
            ],
            "evidence_type": "heuristic_based_on_sentence_and_POS_evidence",
            "limitation": (
                "Fragments can be deliberate; a possible list is not a judgment of meaning or quality."
            ),
        }

    @staticmethod
    def _incomplete_subordinator_evidence(
        sentences: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        evidence = []
        for sentence_index, sentence in enumerate(sentences):
            dependency_by_start = {
                dependency["start"]: dependency
                for dependency in sentence["dependencies"]
            }
            predicate_starts = {
                token["start"]
                for token in sentence["tokens"]
                if token["pos"] in {"VERB", "AUX"}
                and token["dependency"] in CLAUSE_DEPENDENCIES
            }
            root_predicate_starts = {
                token["start"]
                for token in sentence["tokens"]
                if token["pos"] in {"VERB", "AUX"}
                and token["tag"] in FINITE_TAGS
                and token["dependency"] == "ROOT"
            }
            for token in sentence["tokens"]:
                marker = token["text"].casefold()
                if token["pos"] != "SCONJ" or marker not in CLAUSE_SUBORDINATORS:
                    continue
                marker_dependency = dependency_by_start.get(token["start"], {})
                head_start = marker_dependency.get("head_start")
                marker_has_clause_head = head_start in predicate_starts
                if not marker_has_clause_head and marker == "before" and token["dependency"] == "mark":
                    marker_has_clause_head = IntroductionRuleBase._before_adjective_clause_supported(sentence, token)
                head_is_only_root_clause = (
                    token["dependency"] == "mark"
                    and marker_has_clause_head
                    and head_start in root_predicate_starts
                    and not (root_predicate_starts - {head_start})
                )
                if head_is_only_root_clause:
                    # Safeguard: the marker is attached to the sentence ROOT,
                    # but the parse may also contain a separate finite
                    # subordinate-clause predicate (advcl/ccomp/xcomp) with its
                    # own subject. In that case the two-clause structure is
                    # already observed and the ROOT attachment is likely a
                    # parser misattachment, so the incomplete-subordinator
                    # warning is suppressed.
                    head_is_only_root_clause = not any(
                        other["pos"] in {"VERB", "AUX"}
                        and other["tag"] in FINITE_TAGS
                        and other["dependency"] in {"advcl", "ccomp", "xcomp"}
                        and other["start"] != head_start
                        and any(
                            dep["dependency"] in SUBJECT_DEPENDENCIES
                            and dep["head_start"] == other["start"]
                            for dep in sentence["dependencies"]
                        )
                        for other in sentence["tokens"]
                    )
                is_unattached_marker = token["dependency"] == "ROOT"
                prep_has_no_complement = (
                    token["dependency"] == "prep"
                    and not any(
                        dependency["head_start"] == token["start"]
                        and dependency["dependency"] in {"pobj", "obj"}
                        for dependency in sentence["dependencies"]
                    )
                    and not any(
                        child["dependency"] == "prep"
                        and any(
                            dependency["head_start"] == child["start"]
                            and dependency["dependency"] in {"pobj", "obj"}
                            for dependency in sentence["dependencies"]
                        )
                        for child in sentence["dependencies"]
                        if child["head_start"] == token["start"]
                    )
                )
                because_has_only_nominal_complement = (
                    marker == "because"
                    and token["dependency"] == "prep"
                    and any(
                        dependency["head_start"] == token["start"]
                        and dependency["dependency"] == "pobj"
                        and dependency["text"].casefold() != "of"
                        for dependency in sentence["dependencies"]
                    )
                    and not any(start > token["end"] for start in predicate_starts)
                )
                if (
                    is_unattached_marker
                    or (token["dependency"] == "mark" and not marker_has_clause_head)
                    or head_is_only_root_clause
                    or prep_has_no_complement
                    or because_has_only_nominal_complement
                ):
                    evidence.append(
                        {
                            "sentence_index": sentence_index,
                            "text": token["text"],
                            "start": token["start"],
                            "end": token["end"],
                            "pos": token["pos"],
                            "dependency": token["dependency"],
                            "predicate_starts_in_sentence": sorted(predicate_starts),
                            "evidence_type": "POS_and_dependency_heuristic",
                            "limitation": "Parser attachment can be wrong; a reviewer should inspect the clause.",
                        }
                    )
        return evidence

    @staticmethod
    def _before_adjective_clause_supported(sentence: dict[str, Any], marker: dict[str, Any]) -> bool:
        """Recognize one narrow parser pattern, not grammatical correctness.

        A before-marked ADJ/JJ advcl may still have its own subject and attach
        directly to a separate finite ROOT with its own subject. Do not change
        the original annotations or broaden the ordinary predicate filter.
        """
        if marker.get("text", "").casefold() != "before" or marker.get("dependency") != "mark" or marker.get("pos") != "SCONJ":
            return False
        start, end, text = sentence.get("start"), sentence.get("end"), sentence.get("text")
        if type(start) is not int or type(end) is not int or not isinstance(text, str) or end - start != len(text):
            return False
        tokens = sentence.get("tokens", [])
        dependencies = sentence.get("dependencies", [])

        def verified_node(position):
            if type(position) is not int:
                return None
            nodes = [item for item in tokens if item.get("start") == position]
            links = [item for item in dependencies if item.get("start") == position]
            if len(nodes) != 1 or len(links) != 1:
                return None
            node, link = nodes[0], links[0]
            node_end = node.get("end")
            if (type(node_end) is not int or not start <= position < node_end <= end
                or text[position - start:node_end - start] != node.get("text")
                or any(node.get(key) != link.get(key) for key in ("text", "start", "end", "dependency", "head"))):
                return None
            return node, link

        marker_node = verified_node(marker.get("start"))
        if not marker_node or marker_node[0] != marker:
            return False
        subordinate = verified_node(marker_node[1].get("head_start"))
        if not subordinate or subordinate[0].get("pos") != "ADJ" or subordinate[0].get("tag") != "JJ" or subordinate[0].get("dependency") != "advcl":
            return False
        main = verified_node(subordinate[1].get("head_start"))
        if (not main or main[0]["start"] in {marker["start"], subordinate[0]["start"]}
            or main[0].get("pos") not in {"VERB", "AUX"} or main[0].get("tag") not in FINITE_TAGS
            or main[0].get("dependency") != "ROOT" or main[1].get("head_start") != main[0]["start"]
            or marker["head"] != subordinate[0]["text"] or subordinate[0]["head"] != main[0]["text"]):
            return False
        # A ROOT marked by another subordinating conjunction is not independent
        # evidence of a main statement. Keep conservative behavior in that case.
        if any(link.get("head_start") == main[0]["start"] and link.get("dependency") == "mark" for link in dependencies):
            return False

        def has_subject(predicate):
            return any(
                link.get("dependency") in SUBJECT_DEPENDENCIES
                and link.get("head_start") == predicate["start"]
                and (node := verified_node(link.get("start"))) is not None
                and node[0]["head"] == predicate["text"]
                and node[0]["start"] not in {marker["start"], subordinate[0]["start"], main[0]["start"]}
                for link in dependencies
            )

        return has_subject(subordinate[0]) and has_subject(main[0])

    @staticmethod
    def _context_candidates(
        central_candidates: list[dict[str, Any]],
        matches: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        contexts = []
        for candidate in central_candidates:
            sentence_matches = [
                match
                for match in matches
                if candidate["sentence_start"] <= match["start"]
                and match["end"] <= candidate["sentence_end"]
            ]
            if sentence_matches:
                contexts.append(
                    {
                        "sentence_text": candidate["sentence_text"],
                        "start": candidate["sentence_start"],
                        "end": candidate["sentence_end"],
                        "topic_match_evidence": sentence_matches,
                        "clause_candidate_evidence": {
                            "subject_evidence": candidate["subject_evidence"],
                            "predicate_evidence": candidate["predicate_evidence"],
                        },
                        "evidence_type": "lexical_match_plus_dependency_heuristic",
                        "limitation": (
                            "This is only a topic-term and clause-structure candidate, not verified context or relevance."
                        ),
                    }
                )
        return contexts

    @staticmethod
    def _reason_clause_lexical_check(
        sentences: list[dict[str, Any]],
        matches: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Examine advcl-because clauses for focus-term overlap.

        For each sentence that contains a 'because' subordinating conjunction
        attached via 'mark' to an advcl predicate, collect the token offsets of
        that subordinate clause's subtree and report whether any recorded
        focus-term match falls within those offsets.

        Returns a dict that is always present regardless of whether any
        because-clause is found, with:
          - status: one of
              BECAUSE_CLAUSE_WITH_TOPIC_OVERLAP
              BECAUSE_CLAUSE_NO_TOPIC_OVERLAP
              NO_BECAUSE_CLAUSE_IDENTIFIED
              INSUFFICIENT_EVIDENCE
          - clauses: list of per-clause findings
          - limitation: honest scope statement
        """
        clause_findings: list[dict[str, Any]] = []

        for sentence_index, sentence in enumerate(sentences):
            tokens = sentence.get("tokens", [])
            deps = sentence.get("dependencies", [])
            token_by_start = {tok["start"]: tok for tok in tokens}
            dep_by_start = {dep["start"]: dep for dep in deps}

            # Find 'because' markers with a valid advcl head.
            for tok in tokens:
                if tok.get("text", "").casefold() != "because":
                    continue
                if tok.get("pos") != "SCONJ" or tok.get("dependency") != "mark":
                    continue
                dep_entry = dep_by_start.get(tok["start"])
                if dep_entry is None:
                    continue
                advcl_start = dep_entry.get("head_start")
                advcl_tok = token_by_start.get(advcl_start)
                if advcl_tok is None:
                    continue
                if advcl_tok.get("dependency") not in {"advcl", "ccomp", "xcomp"}:
                    continue

                # Collect the subtree of the advcl predicate using a BFS over
                # head_start relationships recorded in the dependency list.
                subtree_starts: set[int] = {advcl_start}
                frontier = {advcl_start}
                while frontier:
                    next_frontier: set[int] = set()
                    for dep in deps:
                        if dep.get("head_start") in frontier and dep["start"] not in subtree_starts:
                            subtree_starts.add(dep["start"])
                            next_frontier.add(dep["start"])
                    frontier = next_frontier

                subtree_tokens = sorted(
                    [token_by_start[s] for s in subtree_starts if s in token_by_start],
                    key=lambda t: t["start"],
                )
                if not subtree_tokens:
                    continue

                clause_start = subtree_tokens[0]["start"]
                clause_end = subtree_tokens[-1]["end"]

                # Check whether any focus-term match falls inside the clause.
                clause_matches = [
                    m for m in matches
                    if m.get("start") is not None and m.get("end") is not None
                    and clause_start <= m["start"] and m["end"] <= clause_end
                ]
                alpha_clause_tokens = [
                    t for t in subtree_tokens if t.get("is_alpha")
                ]

                clause_findings.append({
                    "sentence_index": sentence_index,
                    "sentence_text": sentence.get("text", ""),
                    "sentence_start": sentence.get("start"),
                    "sentence_end": sentence.get("end"),
                    "because_start": tok["start"],
                    "because_end": tok["end"],
                    "advcl_predicate_text": advcl_tok.get("text", ""),
                    "advcl_predicate_start": advcl_start,
                    "advcl_predicate_end": advcl_tok.get("end"),
                    "clause_start": clause_start,
                    "clause_end": clause_end,
                    "clause_token_count": len(alpha_clause_tokens),
                    "topic_matches_in_clause": clause_matches,
                    "topic_overlap_observed": bool(clause_matches),
                    "evidence_type": "spaCy_subtree_and_lexical_match_heuristic",
                    "limitation": (
                        "Topic-word overlap in the reason clause is not proof that the reason "
                        "supports the point. Absence of overlap is not proof that it does not."
                    ),
                })

        if not clause_findings:
            return {
                "status": "NO_BECAUSE_CLAUSE_IDENTIFIED",
                "clauses": [],
                "limitation": (
                    "No 'because' advcl clause was identified in this Introduction. "
                    "Other reason structures are not detected."
                ),
            }

        has_overlap = any(c["topic_overlap_observed"] for c in clause_findings)
        all_no_overlap = all(not c["topic_overlap_observed"] for c in clause_findings)

        if has_overlap:
            status = "BECAUSE_CLAUSE_WITH_TOPIC_OVERLAP"
        elif all_no_overlap:
            status = "BECAUSE_CLAUSE_NO_TOPIC_OVERLAP"
        else:
            status = "INSUFFICIENT_EVIDENCE"

        return {
            "status": status,
            "clauses": clause_findings,
            "limitation": (
                "This check uses lexical overlap inside a parser-identified advcl subtree. "
                "Topic-word presence does not prove logical support; "
                "topic-word absence does not prove irrelevance. "
                "Pronouns, paraphrases, and synonyms are not detected."
            ),
        }

    @staticmethod
    def _development_finding(
        clause_candidates: list[dict[str, Any]],
        incomplete_subordinators: list[dict[str, Any]],
    ) -> dict[str, Any]:
        incomplete_sentence_indices = {
            item["sentence_index"] for item in incomplete_subordinators
        }
        supported_clauses = [
            item
            for item in clause_candidates
            if item["sentence_index"] not in incomplete_sentence_indices
        ]
        if len(supported_clauses) >= 2:
            return {
                "status": "STRUCTURAL_ELABORATION_CANDIDATE",
                "predicate_count": len(supported_clauses),
                "evidence": [item["predicate_evidence"] for item in supported_clauses],
                "evidence_type": "multiple_parser_labeled_clause_predicates",
                "limitation": (
                    "Multiple clauses or sentences do not prove that the ideas are connected logically or soundly."
                ),
            }
        return {
            "status": "NO_ADDITIONAL_CLAUSE_ELABORATION_OBSERVED",
            "predicate_count": len(supported_clauses),
            "evidence": [item["predicate_evidence"] for item in supported_clauses],
            "evidence_type": "parser_labeled_clause_predicates",
            "limitation": (
                "This rule can miss elaboration expressed through other sentence structures or vocabulary."
            ),
        }

    @staticmethod
    def _rule_events(
        text: str,
        word_count: int,
        sentences: list[dict[str, Any]],
        central_candidates: list[dict[str, Any]],
        list_finding: dict[str, Any],
        topic_observations: list[dict[str, Any]],
        context_candidates: list[dict[str, Any]],
        incomplete_subordinators: list[dict[str, Any]],
        development: dict[str, Any],
        reason_clause: dict[str, Any],
        position: dict[str, Any],
    ) -> list[dict[str, Any]]:
        events = []

        def add(
            rule_id: str,
            condition: str,
            evidence: list[dict[str, Any]],
            evidence_type: str,
            limitation: str,
        ) -> None:
            events.append(
                {
                    "rule_id": rule_id,
                    "triggering_condition": condition,
                    "triggered": True,
                    "evidence": evidence,
                    "evidence_type": evidence_type,
                    "limitation": limitation,
                }
            )

        if word_count:
            alpha_tokens = [token for sentence in sentences for token in sentence["tokens"] if token["is_alpha"]]
            add(
                "INTRO.TEXT.PRESENT",
                "At least one alphabetic student token was observed.",
                [{"text": token["text"], "start": token["start"], "end": token["end"]} for token in alpha_tokens],
                "direct_text_observation",
                "Word presence does not establish sentence completeness or meaning.",
            )
        else:
            add(
                "INTRO.TEXT.EMPTY_OR_NONALPHABETIC",
                "No alphabetic token was observed in the student input.",
                [{"text": text, "start": 0, "end": len(text)}] if text else [],
                "direct_text_observation",
                "Punctuation and empty input provide no writing content to evaluate.",
            )

        if central_candidates:
            add(
                "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
                "spaCy labeled a finite root predicate and a subject dependent on it.",
                central_candidates,
                "spaCy_POS_and_dependency_observation",
                "These labels do not verify whether the proposition makes sense.",
            )
        else:
            add(
                "INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE",
                "No finite root predicate with a parser-labeled subject was found.",
                [],
                "absence_under_spaCy_POS_and_dependency_heuristic",
                "A valid stylistic opening may not match this heuristic.",
            )
        if list_finding["keyword_list_candidate"]:
            add(
                "INTRO.TEXT.KEYWORD_LIST_CANDIDATE",
                list_finding["trigger_condition"],
                list_finding["evidence"],
                list_finding["evidence_type"],
                list_finding["limitation"],
            )
        elif list_finding["fragmentary_text_candidate"]:
            add(
                "INTRO.TEXT.FRAGMENT_CANDIDATE",
                "Alphabetic text is present but no finite clause with a parser-labeled subject was found.",
                list_finding["evidence"],
                list_finding["evidence_type"],
                list_finding["limitation"],
            )

        all_matches = IntroductionRuleBase._all_matches(topic_observations)
        if all_matches:
            add(
                "INTRO.TOPIC.FOCUS_TERMS_OBSERVED",
                "At least one teacher focus phrase has direct or lemma-normalized lexical evidence.",
                all_matches,
                "direct_lexical_span_with_direct_or_lemma_match_method",
                "Focus-term overlap is not evidence of sound or meaningful explanation.",
            )
        else:
            add(
                "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED",
                "No configured focus phrase matched directly or by lemma normalization.",
                [],
                "lexical_matching_result",
                "Paraphrases and other relevant wording may not be in the focus list.",
            )

        if context_candidates:
            add(
                "INTRO.CONTEXT.TOPIC_AND_CLAUSE_CANDIDATE",
                "A sentence span contains both a topic-term match and a subject-predicate candidate.",
                context_candidates,
                "lexical_and_syntactic_heuristic",
                "This does not establish that the sentence introduces the topic coherently.",
            )
        if incomplete_subordinators:
            add(
                "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR",
                "A subordinator did not receive the expected parser attachment for a subordinate clause.",
                incomplete_subordinators,
                "POS_and_dependency_heuristic",
                "This may be a parser error or an unusual construction; inspect the actual wording.",
            )

        if development["status"] == "STRUCTURAL_ELABORATION_CANDIDATE":
            add(
                "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES",
                "At least two finite clause-predicate candidates were observed.",
                development["evidence"],
                development["evidence_type"],
                development["limitation"],
            )
        else:
            add(
                "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE",
                "Fewer than two finite clause-predicate candidates were observed.",
                development["evidence"],
                development["evidence_type"],
                development["limitation"],
            )

        rc_status = reason_clause.get("status", "NO_BECAUSE_CLAUSE_IDENTIFIED")
        rc_clauses = reason_clause.get("clauses", [])
        rc_limitation = reason_clause.get("limitation", RULE_LIMIT)
        if rc_status == "BECAUSE_CLAUSE_WITH_TOPIC_OVERLAP":
            add(
                "INTRO.REASON.CLAUSE_TOPIC_OVERLAP",
                "A 'because' advcl clause was identified and contains at least one focus-term match.",
                rc_clauses,
                "spaCy_subtree_and_lexical_match_heuristic",
                rc_limitation,
            )
        elif rc_status == "BECAUSE_CLAUSE_NO_TOPIC_OVERLAP":
            add(
                "INTRO.REASON.NO_CLAUSE_TOPIC_OVERLAP",
                "A 'because' advcl clause was identified but contains no recorded focus-term match.",
                rc_clauses,
                "spaCy_subtree_and_lexical_match_heuristic",
                rc_limitation,
            )

        if position["status"] == "RELEVANT_POSITION_OBSERVED":
            add(
                "INTRO.POSITION.RELEVANT_POSITION_OBSERVED",
                "An argumentativeness cue was matched in the assignment and a sentence "
                "contains a modal or first-person stance-verb cue plus a specific assignment-word match.",
                position["position_statements"],
                position["evidence_type"],
                position["limitation"],
            )
        elif position["status"] == "NO_RELEVANT_POSITION_OBSERVED":
            add(
                "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED",
                position["trigger_condition"],
                [
                    {
                        "focus_term": match["focus_term"],
                        "start": match["start"],
                        "end": match["end"],
                        "text": match.get("text", match.get("observed_text", "")),
                    }
                    for match in position.get("topic_discussion_matches", [])
                ],
                "absence_under_POS_dependency_and_lexical_match_heuristic",
                position["limitation"],
            )
        else:
            add(
                "INTRO.POSITION.CHECK_NOT_APPLICABLE",
                "The position check did not run: "
                + (
                    "the assignment wording contains no argumentativeness cue."
                    if position["status"] == "CHECK_NOT_APPLICABLE_INFORMATIONAL_ASSIGNMENT"
                    else "no specific assignment-word match with a subject-predicate candidate was observed."
                ),
                [],
                "assignment_wording_and_topic_evidence_gate",
                "A non-run of this check is not evidence that a position is present or missing.",
            )

        add(
            "INTRO.GOAL.OBSERVABLE_INTRODUCTION",
            "The requested analysis stage is Introduction.",
            [],
            "stage_scope_configuration",
            "This is a guidance goal, not a stage-readiness decision.",
        )
        add(
            "INTRO.LIMITATION.NO_SEMANTIC_VALIDATION",
            "Always applied: this Rule Base does not validate meaning, logic, or facts.",
            [],
            "system_scope_limitation",
            RULE_LIMIT,
        )
        return events

    @staticmethod
    def _missing_elements(
        word_count: int,
        central_candidates: list[dict[str, Any]],
        observed_focus_terms: list[str],
        development: dict[str, Any],
        position: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        missing = []
        if word_count == 0:
            missing.append(
                {
                    "element": "alphabetic student writing",
                    "rule_id": "INTRO.TEXT.EMPTY_OR_NONALPHABETIC",
                    "limitation": "This is an input observation, not a quality judgment.",
                }
            )
        if not central_candidates:
            missing.append(
                {
                    "element": "parser-labeled finite root clause with subject",
                    "rule_id": "INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE",
                    "limitation": "A valid stylistic opening may not match this heuristic.",
                }
            )
        if not observed_focus_terms:
            missing.append(
                {
                    "element": "configured teacher-focus lexical match",
                    "rule_id": "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED",
                    "limitation": "Relevant paraphrases may not be included in the focus terms.",
                }
            )
        if development["status"] != "STRUCTURAL_ELABORATION_CANDIDATE":
            missing.append(
                {
                    "element": "additional clause-level development candidate",
                    "rule_id": "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE",
                    "limitation": "Other forms of development are not detected by this rule.",
                }
            )
        if position is not None and position["status"] == "NO_RELEVANT_POSITION_OBSERVED":
            missing.append(
                {
                    "element": "explicit position statement cue",
                    "rule_id": "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED",
                    "limitation": POSITION_LIMITATION,
                }
            )
        return missing
