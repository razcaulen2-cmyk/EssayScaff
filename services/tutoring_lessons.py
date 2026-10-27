"""Load the locally authored, structured Student Workspace tutoring lessons."""

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


_INTRO_LESSON_PATH = (
    Path(__file__).resolve().parent.parent
    / "content"
    / "lessons"
    / "intro_lesson_001.json"
)


@lru_cache(maxsize=1)
def load_introduction_lesson() -> dict[str, Any]:
    """Return INTRO-LESSON-001 without connecting it to NLP or student storage."""
    lesson = json.loads(_INTRO_LESSON_PATH.read_text(encoding="utf-8"))
    required = {
        "lesson_id",
        "title",
        "learning_objectives",
        "intended_stage",
        "source_framework",
        "model",
        "practice",
        "reflect",
        "completion_conditions",
        "associated_rule_ids",
    }
    missing = required - lesson.keys()
    if missing:
        raise ValueError(f"Introduction lesson is missing fields: {sorted(missing)}")
    if lesson["lesson_id"] != "INTRO-LESSON-001":
        raise ValueError("Unexpected Introduction lesson ID")
    return lesson


_FEEDBACK_HELP_PATH = Path(__file__).resolve().parent.parent / "content" / "lessons" / "feedback_help.json"

_TUTOR_SECTIONS = ("noticed", "why", "task", "limitation")

_TRAIT_DIMENSIONS = {"Ideas", "Organization", "Sentence Fluency", "Word Choice", "Conventions"}


def _validate_feedback_help(catalog: Any) -> None:
    """Validate prepared presentation content, never writing quality or mastery."""
    if not isinstance(catalog, dict) or type(catalog.get("version")) is not int or catalog["version"] not in {3, 4, 5, 6}:
        raise ValueError("Unsupported feedback help version")
    if not isinstance(catalog.get("lessons"), list) or not isinstance(catalog.get("bindings"), list):
        raise ValueError("Feedback help needs lesson and binding lists")
    ids: set[str] = set()
    for lesson in catalog["lessons"]:
        if not isinstance(lesson, dict) or any(
            not isinstance(lesson.get(key), str) or not lesson[key].strip()
            for key in ("lesson_id", "title", "limitation")
        ):
            raise ValueError("Incomplete prepared learning content")
        if lesson["lesson_id"] in ids:
            raise ValueError("Duplicate feedback help lesson ID")
        ids.add(lesson["lesson_id"])
        guidance = lesson.get("inline_guidance")
        if not isinstance(guidance, dict) or any(
            not isinstance(guidance.get(key), str) or not guidance[key].strip()
            for key in ("goal", "question", "explanation", "next_step", "limitation")
        ):
            raise ValueError("Incomplete concise instructional guidance")
        marker_question = guidance.get("marker_question")
        if marker_question is not None and (
            not isinstance(marker_question, str) or marker_question.count("{marker}") != 1
        ):
            raise ValueError("Marker guidance needs exactly one explicit marker slot")
        tutor = lesson.get("tutor")
        if not isinstance(tutor, dict) or any(
            not isinstance(tutor.get(key), str) or not tutor[key].strip()
            for key in _TUTOR_SECTIONS
        ):
            raise ValueError("Incomplete prepared tutor sections")
        marker_notes = tutor.get("marker_notes")
        if marker_notes is not None and (
            not isinstance(marker_notes, dict)
            or not marker_notes
            or any(not isinstance(key, str) or not key.strip() or not isinstance(value, str) or not value.strip()
                   for key, value in marker_notes.items())
        ):
            raise ValueError("Incomplete tutor marker notes")
        task_fallback = tutor.get("task_fallback")
        if task_fallback is not None and (not isinstance(task_fallback, str) or not task_fallback.strip()):
            raise ValueError("Incomplete tutor task fallback")
    bindings: set[tuple[str, str, str]] = set()
    for binding in catalog["bindings"]:
        if not isinstance(binding, dict) or any(
            not isinstance(binding.get(key), str) or not binding[key].strip()
            for key in ("stage_id", "feedback_field", "selection_branch", "lesson_id", "noticed", "dimension", "skill", "mapping_basis")
        ):
            raise ValueError("Incomplete feedback help binding")
        for field in ("required_rule_ids", "required_any_rule_ids", "working_rule_ids"):
            if field in binding and (not isinstance(binding[field], list)
                                     or any(not isinstance(rule, str) or not rule.strip() for rule in binding[field])):
                raise ValueError("Prepared binding rule references must be string lists")
        key = (binding["stage_id"], binding["feedback_field"], binding["selection_branch"])
        if key[0] not in {"INTRODUCTION", "BODY", "CONCLUSION"} or key[1] != "Primary Feedback" or binding["lesson_id"] not in ids or key in bindings or binding["dimension"] not in _TRAIT_DIMENSIONS:
            raise ValueError("Invalid or duplicate feedback help binding")
        bindings.add(key)
    secondary = catalog.get("secondary_bindings", [])
    if not isinstance(secondary, list):
        raise ValueError("Secondary bindings must be a list")
    secondary_keys: set[tuple[str, str]] = set()
    for binding in secondary:
        if not isinstance(binding, dict) or any(
            not isinstance(binding.get(key), str) or not binding[key].strip()
            for key in ("stage_id", "rule_id_pattern", "lesson_id", "dimension", "skill", "mapping_basis")
        ):
            raise ValueError("Incomplete secondary feedback binding")
        key = (binding["stage_id"], binding["rule_id_pattern"])
        if (
            key[0] not in {"INTRODUCTION", "BODY", "CONCLUSION"}
            or binding["lesson_id"] not in ids
            or binding["dimension"] not in _TRAIT_DIMENSIONS
            or key in secondary_keys
        ):
            raise ValueError("Invalid or duplicate secondary feedback binding")
        try:
            re.compile(binding["rule_id_pattern"])
        except re.error as error:
            raise ValueError(f"Invalid secondary rule ID pattern: {error}") from error
        secondary_keys.add(key)


@lru_cache(maxsize=1)
def load_feedback_help() -> dict[str, Any]:
    """Reuse local content infrastructure for concise, branch-linked guidance.

    A missing/invalid catalog leaves original feedback intact, without blocking
    analysis or the existing Model–Practice–Reflect Introduction activity.
    """
    try:
        catalog = json.loads(_FEEDBACK_HELP_PATH.read_text(encoding="utf-8"))
        _validate_feedback_help(catalog)
    except (OSError, UnicodeError, ValueError, TypeError):
        return {"version": 6, "availability": "UNAVAILABLE", "lessons": [], "bindings": []}
    return {**catalog, "availability": "AVAILABLE"}


INTRO_IDEAS_LIMITATIONS = [
    "Lexical overlap is not semantic relevance.",
    "Clause structure is not proof of argument quality.",
    "Missing 'because' is not proof that an explanation is missing.",
    "Missing assignment keywords is not proof that a reason is unrelated.",
    "Demonstratives and pronouns are not resolved references.",
    "No automatic correctness or essay-quality certification is performed.",
]


def _introduction_highlights(analysis, events, rule_ids, branch):
    """Localize existing evidence only; never choose a feedback branch or parse text."""
    source = analysis.get("linguistic_observations", {}).get("text")
    sentences = analysis.get("linguistic_observations", {}).get("sentences", [])
    if not isinstance(source, str) or analysis.get("input_text", source) != source:
        return []

    def span(start, end, text=None):
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(source):
            return None
        actual = source[start:end]
        return {"start": start, "end": end, "text": actual} if text is None or text == actual else None

    def plan(rule, index, evidence, path, kind, reason, whole_sentence=True, start_key="start", end_key="end"):
        anchor_record = evidence
        for key in path:
            anchor_record = anchor_record.get(key, {})
        anchor = span(anchor_record.get(start_key), anchor_record.get(end_key), anchor_record.get("text", anchor_record.get("observed_text")))
        if not anchor:
            return None
        contexts = [(i, s) for i, s in enumerate(sentences) if s["start"] <= anchor["start"] < anchor["end"] <= s["end"]]
        if len(contexts) != 1:
            return None
        number, sentence = contexts[0]
        context = span(sentence["start"], sentence["end"], sentence["text"])
        if not context or ("sentence_index" in evidence and evidence["sentence_index"] != number):
            return None
        if "sentence_start" in evidence and (evidence["sentence_start"] != context["start"] or evidence.get("sentence_end") != context["end"] or evidence.get("sentence_text") != context["text"]):
            return None
        mark = context if whole_sentence else anchor
        return {**mark, "rule_id": rule, "evidence_index": index, "anchor_path": path,
                "anchor_start_field": start_key, "anchor_end_field": end_key, "anchor": anchor,
                "context": {**context, "sentence_index": number}, "kind": kind,
                "selection_reason": reason, "interpretation": "Evidence location, not an error label or a quality judgment."}

    def evidence(rule):
        return events.get(rule, {}).get("evidence", [])

    reason_rule = next((r for r in rule_ids if r.startswith("INTRO.REASON.")), None)
    if reason_rule and evidence(reason_rule):
        item = plan(reason_rule, 0, evidence(reason_rule)[0], [], "reason_clause",
                    "First source-ordered recorded because subtree; marked as explanation evidence, regardless of word overlap.",
                    False, "clause_start", "clause_end")
        return [item] if item else []
    incomplete_rule = "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"
    if incomplete_rule in rule_ids:
        records = evidence(incomplete_rule)
        item = plan(incomplete_rule, 0, records[0], [], "incomplete_sentence", "The single recorded incomplete-marker sentence is the review location.") if len(records) == 1 else None
        return [item] if item else []
    statement_rule = "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE"
    statements = evidence(statement_rule)
    if statement_rule in rule_ids and statements:
        statement = statements[0]
        if not statement.get("subject_evidence"):
            return []
        main = plan(statement_rule, 0, statement, ["predicate_evidence"], "main_statement",
                    "First source-ordered subject-linked root pattern; a possible statement to develop, not a missing-point finding.")
        if not main:
            return []
        if branch == "intro_ideas_review_details":
            development_rule = "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES"
            for index, item in enumerate(evidence(development_rule)):
                if item.get("start") == main["anchor"]["start"]:
                    continue
                extra = plan(development_rule, index, item, [], "development_pattern",
                             "First additional recorded predicate. Its sentence is shown alone; shared-sentence evidence marks only the extra predicate.")
                if extra:
                    if extra["context"]["sentence_index"] == main["context"]["sentence_index"]:
                        extra.update(extra["anchor"])
                    return [extra]
            return []
        return [main]
    for rule in rule_ids:
        if rule in {"INTRO.TEXT.KEYWORD_LIST_CANDIDATE", "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW", "INTRO.TOPIC.FOCUS_TERMS_OBSERVED"}:
            records = evidence(rule)
            if rule != "INTRO.TEXT.KEYWORD_LIST_CANDIDATE":
                records = records[:1]
            plans = [plan(rule, i, item, [], "wording_observation", "Verified source-ordered recorded wording evidence.", rule != "INTRO.TOPIC.FOCUS_TERMS_OBSERVED") for i, item in enumerate(records)]
            return plans if plans and all(plans) else []
    return []


def introduction_instructional_trace(analysis, feedback, decision_trace):
    """Resolve the chosen branch's existing prepared mapping for all displays.

    This is trace/presentation metadata over FeedbackService's completed choices,
    not a second detector, ranking system, or feedback engine. No NLP is called.
    """
    catalog = load_feedback_help()
    events = {e["rule_id"]: e for e in analysis.get("rule_evidence", []) if e.get("triggered", True) and e.get("fired", True)}
    lessons = {item["lesson_id"]: item for item in catalog["lessons"]}
    fields = decision_trace["fields"]
    lexical = analysis.get("lexical_topic_evidence", {})
    structure = analysis.get("observable_structure", {})
    reason = analysis.get("reason_clause_evidence", {})
    observations = {
        "central_candidate_count": len(structure.get("central_direction_candidates", [])),
        "supported_predicate_count": analysis.get("development_evidence", {}).get("predicate_count"),
        "development_status": analysis.get("development_evidence", {}).get("status"),
        "reason_clause_count": len(reason.get("clauses", [])), "reason_topic_status": reason.get("status"),
        "sentence_count": analysis.get("linguistic_observations", {}).get("counts", {}).get("sentence_count"),
        "observed_focus_terms": lexical.get("observed_focus_terms", []), "topic_matches": lexical.get("matches", []),
    }
    items = []

    def add(field, binding, rule_ids):
        choice = fields[field]
        content = lessons.get(binding.get("lesson_id")) if binding else None
        paired = {p["rule_id"] for p in feedback["Feedback Provenance"] if p["feedback_field"] == field}
        required = binding.get("required_rule_ids", []) if binding else []
        any_required = binding.get("required_any_rule_ids", []) if binding else []
        if not rule_ids or not all(r in events and r in paired for r in rule_ids):
            return
        if not set(required) <= set(rule_ids) or (any_required and not set(any_required) & set(rule_ids)):
            return
        tutor = content.get("tutor", {}) if content else {}
        spans = _introduction_highlights(analysis, events, rule_ids, choice["selection_branch"])
        purpose = content.get("feedback_purpose", "NEUTRAL_REVIEW_TASK") if content else "UNMAPPED_RECORDED_FEEDBACK"
        prepared = {key: tutor[key] for key in ("noticed", "working", "why", "task", "limitation") if key in tutor}
        if "{marker}" in tutor.get("noticed", ""):
            # These are existing prepared slots, not generated writing. Resolve
            # only the one verified marker; otherwise retain the same neutral
            # fallback used by the student renderer.
            marker_records = events.get("INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR", {}).get("evidence", [])
            if len(marker_records) == 1 and spans:
                marker = marker_records[0]["text"]
                prepared["noticed"] = tutor["noticed"].replace("{marker}", marker)
                prepared["why"] = tutor.get("marker_notes", {}).get(marker.casefold(), tutor["why"])
                prepared["task"] = tutor["task"].replace("{clause}", spans[0]["context"]["text"].rstrip(".!?"))
            else:
                prepared["noticed"] = binding.get("noticed", feedback["Primary Feedback"])
                prepared["task"] = tutor.get("task_fallback", tutor["task"])
        items.append({
            "feedback_field": field, "selection_branch": choice["selection_branch"],
            "selection_condition": choice.get("selection_condition"),
            "trait": binding.get("dimension") if binding else choice.get("trait"),
            "skill": binding.get("skill") if binding else choice.get("skill"),
            "lesson_id": content["lesson_id"] if content else None,
            "catalog_reference": {"file": "content/lessons/feedback_help.json", "version": catalog["version"],
                                  "lesson_id": content["lesson_id"]} if content else None,
            "mapping_basis": binding.get("mapping_basis") if binding else "No verified prepared mapping",
            "feedback_purpose": purpose,
            "prepared_guidance": prepared,
            "working_text": tutor.get("working", "") if binding and all(r in events for r in binding.get("working_rule_ids", required)) else "",
            "rule_ids": rule_ids, "triggered_rule_ids": [r for r in rule_ids if r in events],
            "rule_conditions": [{"rule_id": r, "condition": events[r]["triggering_condition"]} for r in rule_ids],
            "observed_fields": observations,
            "evidence_reference": "analysis.rule_evidence; original evidence/evidence_type/condition/limitation retained in this same response",
            "highlight_spans": spans, "highlight_status": "VERIFIED_SOURCE_EVIDENCE" if spans else "NO_VERIFIED_SOURCE_SPAN",
            "limitations": INTRO_IDEAS_LIMITATIONS,
        })

    primary = fields["Primary Feedback"]
    binding = next((b for b in catalog["bindings"] if b["stage_id"] == "INTRODUCTION" and b["selection_branch"] == primary["selection_branch"]), None)
    add("Primary Feedback", binding, primary["rule_ids"])
    used = {item["lesson_id"] for item in items}
    messages = feedback["Needs Attention"]
    links = [p for p in feedback["Feedback Provenance"] if p["feedback_field"] == "Needs Attention"]
    if len(messages) == len(links):
        for link in links:
            if len(items) >= 2:
                break
            rule = link["rule_id"]
            secondary = next((b for b in catalog.get("secondary_bindings", []) if b["stage_id"] == "INTRODUCTION" and re.search(b["rule_id_pattern"], rule)), None)
            if not secondary or secondary["lesson_id"] in used or rule in primary["rule_ids"]:
                continue
            add("Needs Attention", secondary, [rule])
            used.add(secondary["lesson_id"])
    coverage = []
    for trait in ("Ideas", "Organization", "Voice", "Word Choice", "Sentence Fluency", "Conventions", "Presentation"):
        if trait in {"Ideas", "Sentence Fluency"}:
            status = "LIMITED_OBSERVATIONAL_CHECKS_RECORDED"
            scope = "Statement/development patterns and wording observations" if trait == "Ideas" else "Possible incomplete-subordinator pattern only"
        elif trait in {"Organization", "Word Choice"}:
            status, scope = "INSTRUCTIONAL_CATEGORY_ONLY", "Existing list/broad-word review labels; no independent trait-quality assessment"
        else:
            status, scope = "NOT_EVALUATED", "No Introduction trait check implemented"
        coverage.append({"trait": trait, "status": status, "scope": scope,
                         "instructional_category_selected": any(item["trait"] == trait for item in items),
                         "trait_quality_assessment": "NOT_PERFORMED"})
    return {"framework": "6+1 Trait Writing Model", "stage": "INTRODUCTION",
            "catalog_status": catalog["availability"], "items": items, "coverage": coverage,
            "limitations": INTRO_IDEAS_LIMITATIONS,
            "source": "FeedbackService.generate completed decisions + existing prepared lesson bindings and emitted evidence; no rerun"}


BODY_FEEDBACK_LIMITATIONS = [
    "These checks cannot determine whether the supporting ideas are logically correct or sufficient.",
    "Topic-sentence and supporting-detail structures are candidates, not verified rhetorical roles.",
    "Lexical absence does not prove irrelevance or disconnection; overlap does not prove relevance or coherence.",
    "No example marker or particular transition word is required.",
    "Repeated openings may be intentional and are not automatically errors.",
    "A neutral result is not a 6+1 Trait evaluation, passing grade, or quality certification.",
]


def body_instructional_trace(analysis, feedback, decision_trace):
    """Present completed Body choices through the existing catalog and evidence.

    Selection and its priority checks belong to generate_body. This helper only
    resolves that recorded selection, localizes source evidence and retains
    observations. It never parses, diagnoses, or selects a fallback correction.
    """
    catalog = load_feedback_help()
    events = {e["rule_id"]: e for e in analysis.get("rule_evidence", [])
              if e.get("triggered", True) and e.get("fired", True)}
    source = analysis.get("input_text")
    paragraphs = {p["paragraph_index"]: p for p in analysis.get("paragraphs", []) if p["substantive"]}

    def span(start, end, text=None):
        if not isinstance(source, str) or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(source):
            return None
        actual = source[start:end]
        return {"start": start, "end": end, "text": actual} if text is None or text == actual else None

    def event_positions(rule):
        positions = []
        for index, evidence in enumerate(events.get(rule, {}).get("actual_evidence", [])):
            bounds = evidence.get("sentence_span")
            item = span(*bounds, evidence.get("sentence_text")) if isinstance(bounds, list) and len(bounds) == 2 else span(evidence.get("start"), evidence.get("end"), evidence.get("text", evidence.get("observed_text")))
            if item:
                positions.append({**item, "sentence_index": evidence.get("sentence_index"), "evidence_index": index})
        return positions

    def strength_source(rule):
        return {"rule_id": rule, "paragraph_index": int(re.match(r"BODY\.P(\d+)\.", rule)[1]),
                "positions": event_positions(rule)}

    # At most two concise observations. Original What's Working entries remain
    # in feedback; every displayed aggregate retains its actual source events.
    strengths = []
    developed = [p for n, p in paragraphs.items() if p["topic_sentence_candidates"]
                 and p["supporting_detail_candidates"]["candidates"]
                 and event_positions(f"BODY.P{n}.TOPIC_SENTENCE.CANDIDATE")
                 and event_positions(f"BODY.P{n}.SUPPORTING_DETAIL.CANDIDATE")]
    if developed:
        indices = [p["paragraph_index"] for p in developed]
        all_openings = all(any(c.get("sentence_index") == 0 for c in p["topic_sentence_candidates"]) for p in developed)
        subject = "Both paragraphs" if len(developed) == len(paragraphs) == 2 else "Paragraph " + str(indices[0]) if len(indices) == 1 else "Paragraphs " + ", ".join(map(str, indices))
        wording = "possible opening statements and additional sentence structures" if all_openings else "possible topic-sentence and additional sentence-structure candidates"
        if len(indices) == 1 and all_openings:
            wording = "a possible opening statement and additional sentence structures"
        ids = [f"BODY.P{n}.{suffix}" for n in indices for suffix in ("TOPIC_SENTENCE.CANDIDATE", "SUPPORTING_DETAIL.CANDIDATE")]
        strengths.append({"text": f"{subject} contain{'s' if len(indices) == 1 else ''} {wording}.",
                          "rule_ids": ids, "source_positions": [strength_source(rule) for rule in ids]})
    else:
        possible = [n for n in paragraphs if event_positions(f"BODY.P{n}.TOPIC_SENTENCE.CANDIDATE")]
        if possible:
            n = possible[0]
            rule = f"BODY.P{n}.TOPIC_SENTENCE.CANDIDATE"
            strengths.append({"text": f"Paragraph {n} contains a possible statement pattern.", "rule_ids": [rule],
                              "source_positions": [strength_source(rule)]})
    matched = [n for n, paragraph in paragraphs.items()
               if not paragraph["fragment_or_list_candidate"]["keyword_list_candidate"]
               and event_positions(f"BODY.P{n}.PARAGRAPH.FOCUS_TERMS_OBSERVED")]
    if matched:
        ids = [f"BODY.P{n}.PARAGRAPH.FOCUS_TERMS_OBSERVED" for n in matched]
        label = "Paragraph " + str(matched[0]) if len(matched) == 1 else "Paragraphs " + ", ".join(map(str, matched))
        strengths.append({"text": f"Assignment-word matches were recorded in {label}.", "rule_ids": ids,
                          "source_positions": [strength_source(rule) for rule in ids]})
    strengths = strengths[:2]
    working = "\n".join(item["text"] for item in strengths)

    def highlights(rule_ids, target_indices):
        plans = []
        for rule in rule_ids:
            records = events.get(rule, {}).get("actual_evidence", [])
            if not records or not target_indices:
                continue
            paragraph = paragraphs.get(target_indices[0])
            context = span(paragraph.get("start"), paragraph.get("end"), paragraph.get("text")) if paragraph else None
            if not context:
                continue

            def plan(index, path, kind, reason, mark=None):
                anchor_record = records[index]
                for key in path:
                    anchor_record = anchor_record[key]
                anchor = span(anchor_record.get("start"), anchor_record.get("end"), anchor_record.get("text"))
                selected = mark or anchor
                if not anchor or not selected or not context["start"] <= selected["start"] < selected["end"] <= context["end"] or not context["start"] <= anchor["start"] < anchor["end"] <= context["end"]:
                    return None
                return {**selected, "rule_id": rule, "evidence_index": index, "anchor_path": path,
                        "anchor_start_field": "start", "anchor_end_field": "end", "anchor": anchor,
                        "context": {**context, "paragraph_index": paragraph["paragraph_index"]},
                        "context_kind": "paragraph", "kind": kind, "selection_reason": reason,
                        "interpretation": "Evidence review location, not a guaranteed error or quality judgment."}

            if rule.endswith(".SUPPORTING_DETAIL.NOT_OBSERVED"):
                candidates = paragraph.get("clause_structure_candidates", [])
                bounds = candidates[0].get("sentence_span") if candidates else None
                mark = span(*bounds, candidates[0].get("sentence_text")) if bounds else None
                if mark:
                    item = plan(0, [], "body_statement_to_develop", "The recorded paragraph absence event anchors its first possible statement; only this statement is marked.", mark)
                    if item:
                        plans.append(item)
            elif rule.endswith(".PARAGRAPH.KEYWORD_LIST_CANDIDATE"):
                for index in range(len(records)):
                    item = plan(index, [], "body_list_structure", "The exact source spans recorded by the list-like paragraph event are the structural review location.")
                    if not item:
                        return []
                    plans.append(item)
            elif rule.endswith(".REPETITION.REPEATED_SENTENCE_OPENINGS"):
                for index, record in enumerate(records):
                    for occurrence in range(len(record.get("occurrences", []))):
                        item = plan(index, ["occurrences", occurrence], "body_repeated_opening", "Only the recorded repeated opening words are marked; repetition is not automatically an error.")
                        if not item:
                            return []
                        plans.append(item)
        return plans

    items = []
    selected = decision_trace["fields"]["Primary Feedback"]
    status = decision_trace["selection_status"]
    lessons = {lesson["lesson_id"]: lesson for lesson in catalog["lessons"]}

    def add(field, binding, rule_ids, target_indices, condition):
        paired = {p["rule_id"] for p in feedback["Feedback Provenance"] if p["feedback_field"] == field}
        if not binding or not rule_ids or not all(rule in paired and rule in events for rule in rule_ids):
            return
        lesson = lessons.get(binding["lesson_id"])
        if not lesson or any(item["lesson_id"] == lesson["lesson_id"] for item in items):
            return
        tutor = lesson["tutor"]
        opening_records = [r for rule in rule_ids for r in events[rule].get("actual_evidence", []) if r.get("opening")]
        slots = {"paragraph": str(target_indices[0]) if target_indices else "",
                 "paragraph_pair": " and ".join(map(str, target_indices)),
                 "opening": opening_records[0]["opening"] if opening_records else ""}
        prepared = {key: str(tutor[key]) for key in ("noticed", "why", "task", "limitation")}
        for key in prepared:
            for slot, value in slots.items():
                prepared[key] = prepared[key].replace("{" + slot + "}", value)
        if lesson["lesson_id"] == "HELP-BODY-DEVELOP-POINT" and target_indices:
            p = paragraphs.get(target_indices[0], {})
            prepared["noticed"] = (f"Paragraph {target_indices[0]} has a possible main statement, but no additional sentence was recorded to develop it."
                                    if p.get("counts", {}).get("sentence_count") == 1 else
                                    f"In Paragraph {target_indices[0]}, the checks did not record another sentence part developing the possible statement. Other kinds of supporting ideas may still be present.")
        prepared["working"] = working
        plans = highlights(rule_ids, target_indices)
        items.append({"feedback_field": field, "selection_branch": decision_trace["fields"][field]["selection_branch"],
                      "selection_condition": condition, "selected_message": feedback[field] if field == "Primary Feedback" else None,
                      "trait": binding["dimension"], "skill": binding["skill"], "lesson_id": lesson["lesson_id"],
                      "catalog_reference": {"file": "content/lessons/feedback_help.json", "version": catalog["version"], "lesson_id": lesson["lesson_id"]},
                      "mapping_basis": binding["mapping_basis"], "feedback_purpose": lesson["feedback_purpose"],
                      "rule_ids": rule_ids, "triggered_rule_ids": rule_ids,
                      "rule_conditions": [{"rule_id": rule, "condition": events[rule]["triggering_condition"]} for rule in rule_ids],
                      "paragraph_indices": target_indices, "prepared_guidance": prepared, "working_text": working,
                      "observed_fields": [{"paragraph_index": n, "sentence_count": paragraphs[n]["counts"]["sentence_count"],
                                           "topic_sentence_candidate_count": len(paragraphs[n]["topic_sentence_candidates"]),
                                           "supporting_detail_candidate_count": len(paragraphs[n]["supporting_detail_candidates"]["candidates"]),
                                           "clause_structure_candidates": paragraphs[n].get("clause_structure_candidates", []),
                                           "focus_term_matches": paragraphs[n].get("focus_term_evidence", [])} for n in target_indices if n in paragraphs],
                      "highlight_spans": plans, "highlight_status": "VERIFIED_SOURCE_EVIDENCE" if plans else "NO_PRECISE_ERROR_SPAN_RECORDED",
                      "limitations": BODY_FEEDBACK_LIMITATIONS})

    if status == "SUPPORTED_CONCERN_SELECTED":
        check = next(c for c in decision_trace["selection_checks"] if c["status"] == "SELECTED")
        binding = next((b for b in catalog["bindings"] if b["stage_id"] == "BODY" and b["selection_branch"] == selected["selection_branch"]), None)
        add("Primary Feedback", binding, selected["rule_ids"], check["paragraph_indices"], selected["selection_condition"])
        for link in (p for p in feedback["Feedback Provenance"] if p["feedback_field"] == "Needs Attention"):
            if len(items) >= 3:
                break
            rule = link["rule_id"]
            if rule in selected["rule_ids"]:
                continue
            binding = next((b for b in catalog.get("secondary_bindings", []) if b["stage_id"] == "BODY" and re.search(b["rule_id_pattern"], rule)), None)
            match = re.match(r"BODY\.P(\d+)\.", rule)
            indices = [int(match[1])] if match else next((c["paragraph_indices"] for c in decision_trace["selection_checks"] if rule in c["rule_ids"]), [])
            add("Needs Attention", binding, [rule], indices, events.get(rule, {}).get("triggering_condition"))

    coverage = []
    scopes = {"Ideas": "Topic-sentence and additional clause/statement candidates; no validity or sufficiency assessment",
              "Organization": "Blank-line paragraph boundaries, list-like structures and lexical-link observations only",
              "Sentence Fluency": "Repeated two-word sentence openings only",
              "Word Choice": "Surface/lemma repetition observations only; no word-quality assessment"}
    for trait in ("Ideas", "Organization", "Voice", "Word Choice", "Sentence Fluency", "Conventions", "Presentation"):
        coverage.append({"trait": trait, "scope": scopes.get(trait, "No Body trait check implemented"),
                         "status": "LIMITED_OBSERVATIONS_RECORDED" if trait in scopes else "NOT_EVALUATED",
                         "instructional_category_selected": any(item["trait"] == trait for item in items),
                         "trait_quality_assessment": "NOT_PERFORMED"})
    return {"framework": "6+1 Trait Writing Model", "stage": "BODY", "selection_status": status,
            "selection_branch": selected["selection_branch"], "selection_condition": selected["selection_condition"],
            "student_message": feedback["Primary Feedback"], "catalog_status": catalog["availability"],
            "items": items, "strengths": strengths, "coverage": coverage, "limitations": BODY_FEEDBACK_LIMITATIONS,
            "neutral_result": {"label": "No specific writing issue detected", "noticed": feedback["Primary Feedback"],
                               "working": working, "limitation": BODY_FEEDBACK_LIMITATIONS[0],
                               "trait": None, "skill": None, "lesson_id": None, "task": ""} if status == "NO_SUPPORTED_CONCERN_SELECTED" else None,
            "selection_checks": decision_trace["selection_checks"], "introduction_context": analysis.get("introduction_context"),
            "observed_paragraphs": [{"paragraph_index": n, "start": p.get("start"), "end": p.get("end"), "text": p.get("text"),
                                     "counts": p["counts"], "sentence_positions": [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in p.get("sentence_spans", [])],
                                     "topic_sentence_candidates": p["topic_sentence_candidates"],
                                     "supporting_detail_candidates": p["supporting_detail_candidates"],
                                     "focus_term_matches": p.get("focus_term_evidence", [])} for n, p in paragraphs.items()],
            "source": "FeedbackService.generate_body completed choices + existing local catalog and emitted evidence; no NLP rerun"}
