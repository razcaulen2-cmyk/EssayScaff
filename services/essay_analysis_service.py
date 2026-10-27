"""Coordinate the existing stage analyzers into a single JSON-ready result."""

from typing import Any
from time import perf_counter

from services.body_rules import BodyRuleBase
from services.conclusion_rules import ConclusionRuleBase
from services.feedback_service import FeedbackService
from services.introduction_rules import IntroductionRuleBase
from services.nlp_service import NLPService
from services.topic_service import TopicService


def _elapsed_ms(start: float | None) -> float:
    return (perf_counter() - start) * 1000 if start is not None else 0.0


class EssayAnalysisService:
    """Prepare per-stage observations and feedback without making essay decisions."""

    STAGES = ("INTRODUCTION", "BODY", "CONCLUSION")

    def __init__(self, nlp_service: NLPService | None = None) -> None:
        self.nlp_service = nlp_service or NLPService()
        self.topic_service = TopicService(self.nlp_service)
        self.introduction_rules = IntroductionRuleBase(self.topic_service)
        self.body_rules = BodyRuleBase(self.topic_service)
        self.conclusion_rules = ConclusionRuleBase(self.topic_service)
        self.feedback_service = FeedbackService()

    def analyze(
        self,
        assignment_topic: str,
        focus_terms: list[str] | None = None,
        introduction_text: str | None = None,
        body_text: str | None = None,
        conclusion_text: str | None = None,
        *,
        include_research_trace: bool = False,
    ) -> dict[str, Any]:
        """Analyze only supplied sections and retain each stage's own evidence."""
        if not isinstance(assignment_topic, str):
            raise TypeError("assignment_topic must be a string")
        if focus_terms is not None and (
            isinstance(focus_terms, (str, bytes))
            or not all(isinstance(term, str) for term in focus_terms)
        ):
            raise TypeError("focus_terms must be a list of strings")
        section_texts = {
            "INTRODUCTION": introduction_text,
            "BODY": body_text,
            "CONCLUSION": conclusion_text,
        }
        if any(text is not None and not isinstance(text, str) for text in section_texts.values()):
            raise TypeError("each supplied stage must be a string or None")

        context_started = perf_counter() if include_research_trace else None
        if any(text is not None for text in section_texts.values()):
            teacher_context = self.topic_service.prepare_teacher_context(
                assignment_topic, focus_terms
            )
        else:
            # Do not invoke NLP for an assignment with no submitted stage text.
            teacher_context = {
                "assignment_topic": assignment_topic,
                "focus_source": "not_prepared_no_stage_text",
                "focus_terms": [],
                "automatically_derived_candidates": [],
            }
        context_ms = _elapsed_ms(context_started)
        timings: dict[str, dict[str, float]] = {stage: {} for stage in self.STAGES}
        feedback_decisions: dict[str, dict[str, Any]] = {}

        # Prepare lexical/linguistic output once per supplied text. The existing
        # rules receive these exact outputs, avoiding duplicate full-text parses.
        prepared: dict[str, dict[str, Any]] = {}
        for stage, text in section_texts.items():
            if text is None:
                continue
            topic_started = perf_counter() if include_research_trace else None
            prepared[stage] = self.topic_service.analyze(
                text,
                assignment_topic,
                focus_terms,
                include_wordnet=(stage == "CONCLUSION"),
                prepared_teacher_context=teacher_context,
                collect_trace=include_research_trace,
            )
            if include_research_trace:
                timings[stage]["topic_service_ms"] = _elapsed_ms(topic_started)

        stage_results: dict[str, dict[str, Any]] = {}
        if introduction_text is None:
            stage_results["INTRODUCTION"] = self._unavailable_stage("INTRODUCTION")
        else:
            rule_started = perf_counter() if include_research_trace else None
            introduction_analysis = self.introduction_rules.analyze(
                introduction_text,
                assignment_topic,
                focus_terms,
                prepared_topic_analysis=prepared["INTRODUCTION"],
            )
            if include_research_trace:
                timings["INTRODUCTION"]["rule_base_ms"] = _elapsed_ms(rule_started)
            feedback_started = perf_counter() if include_research_trace else None
            introduction_feedback = self.feedback_service.generate(
                introduction_analysis, include_trace=include_research_trace
            )
            decision_trace = introduction_feedback.pop("_Research Decision Trace", None)
            if decision_trace is not None:
                feedback_decisions["INTRODUCTION"] = decision_trace
            if include_research_trace:
                timings["INTRODUCTION"]["feedback_ms"] = _elapsed_ms(feedback_started)
            stage_results["INTRODUCTION"] = self._stage_result(
                "INTRODUCTION",
                introduction_text,
                introduction_analysis,
                introduction_feedback,
            )

        if body_text is None:
            stage_results["BODY"] = self._unavailable_stage("BODY")
        else:
            rule_started = perf_counter() if include_research_trace else None
            body_analysis = self.body_rules.analyze(
                body_text,
                assignment_topic,
                focus_terms,
                introduction_text,
                prepared_body_analysis=prepared["BODY"],
                prepared_introduction_analysis=prepared.get("INTRODUCTION"),
                include_research_trace=include_research_trace,
            )
            if include_research_trace:
                timings["BODY"]["rule_base_ms"] = _elapsed_ms(rule_started)
            feedback_started = perf_counter() if include_research_trace else None
            body_feedback = self.feedback_service.generate_body(
                body_analysis, include_trace=include_research_trace
            )
            decision_trace = body_feedback.pop("_Research Decision Trace", None)
            if decision_trace is not None:
                feedback_decisions["BODY"] = decision_trace
            if include_research_trace:
                timings["BODY"]["feedback_ms"] = _elapsed_ms(feedback_started)
            stage_results["BODY"] = self._stage_result(
                "BODY", body_text, body_analysis, body_feedback
            )

        if conclusion_text is None:
            stage_results["CONCLUSION"] = self._unavailable_stage("CONCLUSION")
        else:
            rule_started = perf_counter() if include_research_trace else None
            conclusion_analysis = self.conclusion_rules.analyze(
                conclusion_text,
                assignment_topic,
                focus_terms,
                introduction_text,
                body_text,
                prepared_conclusion_analysis=prepared["CONCLUSION"],
                prepared_introduction_analysis=prepared.get("INTRODUCTION"),
                prepared_body_analysis=prepared.get("BODY"),
                include_research_trace=include_research_trace,
            )
            if include_research_trace:
                timings["CONCLUSION"]["rule_base_ms"] = _elapsed_ms(rule_started)
            feedback_started = perf_counter() if include_research_trace else None
            conclusion_feedback = self.feedback_service.generate_conclusion(
                conclusion_analysis, include_trace=include_research_trace
            )
            decision_trace = conclusion_feedback.pop("_Research Decision Trace", None)
            if decision_trace is not None:
                feedback_decisions["CONCLUSION"] = decision_trace
            if include_research_trace:
                timings["CONCLUSION"]["feedback_ms"] = _elapsed_ms(feedback_started)
            stage_results["CONCLUSION"] = self._stage_result(
                "CONCLUSION",
                conclusion_text,
                conclusion_analysis,
                conclusion_feedback,
            )

        result = {
            "assignment_topic": assignment_topic,
            "teacher_focus_terms": focus_terms,
            "teacher_context": {
                key: value
                for key, value in teacher_context.items()
                if key != "requested_focus_terms"
            },
            "stage_order": list(self.STAGES),
            "stages": stage_results,
            "interpretation_limit": (
                "This combined result contains stage-specific linguistic and lexical observations. "
                "It does not establish semantic understanding, essay quality, factual correctness, "
                "readiness, or permission to advance."
            ),
        }
        if include_research_trace:
            from services.research_inspector import build_rule_evaluation_trace, runtime_metadata

            stage_traces: dict[str, dict[str, Any]] = {}
            for stage in self.STAGES:
                stage_result = stage_results[stage]
                if stage_result["availability"] == "NOT_SUPPLIED":
                    stage_traces[stage] = {
                        "execution_status": "NOT_APPLICABLE",
                        "reason": "This section was not supplied to the analysis coordinator.",
                    }
                    continue
                analysis = stage_result["analysis"]
                analysis["rule_evaluation_trace"] = build_rule_evaluation_trace(stage, analysis)
                supplied_inputs = {
                    key: value
                    for key, value in (
                        ("introduction", introduction_text),
                        ("body", body_text),
                        ("conclusion", conclusion_text),
                    )
                    if value is not None
                }
                cross_stage_inputs: dict[str, Any] = {}
                if stage == "BODY" and "INTRODUCTION" in prepared:
                    cross_stage_inputs["introduction_concepts"] = prepared["INTRODUCTION"]["student_concepts"]
                    cross_stage_inputs["body_concepts"] = prepared["BODY"]["student_concepts"]
                elif stage == "CONCLUSION":
                    if "INTRODUCTION" in prepared:
                        cross_stage_inputs["introduction_concepts"] = prepared["INTRODUCTION"]["student_concepts"]
                    if "BODY" in prepared:
                        cross_stage_inputs["body_concepts"] = prepared["BODY"]["student_concepts"]
                    cross_stage_inputs["conclusion_concepts"] = prepared["CONCLUSION"]["student_concepts"]
                stage_traces[stage] = {
                    "execution_status": "EXECUTED",
                    "input_sections": supplied_inputs,
                    "linguistic_observations": prepared[stage]["linguistic_analysis"],
                    "topic_service": prepared[stage].get("research_trace"),
                    "cross_stage_comparison_inputs": cross_stage_inputs,
                    "rule_evaluation_trace": analysis["rule_evaluation_trace"],
                    "feedback_decisions": feedback_decisions.get(stage),
                    "timings_ms": {
                        key: round(value, 3) for key, value in timings[stage].items()
                    },
                    "output_counts": {
                        "rule_events": len(analysis.get("rule_evidence", [])),
                        "feedback_provenance_items": len(
                            stage_result["feedback"].get("Feedback Provenance", [])
                        ),
                    },
                }
            result["research_trace"] = {
                "trace_version": 1,
                "runtime": runtime_metadata(self.nlp_service),
                "teacher_context": {
                    key: value for key, value in teacher_context.items()
                    if key != "requested_focus_terms"
                },
                "teacher_context_preparation_ms": round(context_ms, 3),
                "teacher_context_call_frequency": {
                    "execution_status": "EXECUTED" if any(text is not None for text in section_texts.values()) else "NOT_APPLICABLE",
                    "spacy_calls_for_assignment_topic": 0 if focus_terms else (1 if any(text is not None for text in section_texts.values()) else 0),
                    "spacy_calls_for_focus_phrase_normalization": len(focus_terms) if focus_terms else len(teacher_context.get("automatically_derived_candidates", [])),
                    "teacher_context_spacy_calls_source_derived": (
                        (0 if focus_terms else 1) + (len(focus_terms) if focus_terms else len(teacher_context.get("automatically_derived_candidates", [])))
                    ) if any(text is not None for text in section_texts.values()) else 0,
                    "full_section_spacy_documents": sum(text is not None for text in section_texts.values()),
                    "total_spacy_nlp_invocations_source_derived": (
                        ((0 if focus_terms else 1) + (len(focus_terms) if focus_terms else len(teacher_context.get("automatically_derived_candidates", []))))
                        + sum(text is not None for text in section_texts.values())
                    ) if any(text is not None for text in section_texts.values()) else 0,
                    "basis": "prepare_teacher_context calls the model once for the topic when no focus list is supplied, then once for each term passed to _unique_focus_terms; explicit terms skip topic parsing.",
                    "status": "SOURCE_DERIVED_CALL_COUNT_NOT_TIMED_SEPARATELY",
                },
                "stages": stage_traces,
                "limitations": [
                    "Timings cover the marked in-process Python calls; Flask authentication, network transfer, and browser rendering are separate.",
                    "Cross-stage WordNet comparisons run inside the relevant Rule Base timing and do not have a separate duration measurement.",
                    "The rule trace is built from existing stage outputs and emitted events; it does not rerun the Rule Base or spaCy.",
                ],
            }
        # Attach informational evidence only after all existing rule/feedback/trace
        # work. Keep analysis/feedback structures and protected serializations intact.
        for stage, topic_result in prepared.items():
            if "related_topic_concept_evidence" in topic_result:
                stage_results[stage]["related_topic_concept_evidence"] = topic_result["related_topic_concept_evidence"]
        return result

    @staticmethod
    def _stage_result(
        stage: str, text: str, analysis: dict[str, Any], feedback: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "stage_id": stage,
            "availability": "SUPPLIED_EMPTY" if not text.strip() else "ANALYZED",
            "supplied_text": text,
            "analysis": analysis,
            "feedback": feedback,
        }

    @staticmethod
    def _unavailable_stage(stage: str) -> dict[str, Any]:
        return {
            "stage_id": stage,
            "availability": "NOT_SUPPLIED",
            "supplied_text": None,
            "analysis": None,
            "feedback": None,
        }
