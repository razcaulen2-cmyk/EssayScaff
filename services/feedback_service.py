"""Deterministic student feedback for each stage, derived from actual Rule Base events.

The five fields are selected by trait-based branches over recorded evidence. Every
student message is an original revision prompt, never replacement prose, and no
field claims a quality level, grade, or readiness state.
"""

from typing import Any


# These very broad focus words do not, by themselves, communicate the specific
# assignment subject. This only qualifies feedback wording; matching is unchanged.
BROAD_FOCUS_TERMS = {"student", "students", "use", "uses", "used", "using"}


# Trait labels from the writing-tutor vocabulary. These are instructional focus
# labels only: they are not assessments, scores, or correctness decisions.
TRAIT_IDEAS = "Ideas"
TRAIT_ORGANIZATION = "Organization"
TRAIT_SENTENCE_FLUENCY = "Sentence Fluency"
TRAIT_WORD_CHOICE = "Word Choice"
TRAIT_CONVENTIONS = "Conventions"


# selection_branch -> (trait, skill). Neutral branches (empty input, general
# reviews) record no trait: the tutor then presents the recorded feedback
# without an instructional category.
BRANCH_TRAIT_SKILL: dict[str, tuple[str, str]] = {
    # Introduction
    "intro_organization_topic_intro": (TRAIT_ORGANIZATION, "Introduce Your Topic"),
    "intro_sentence_fluency_complete_sentence": (TRAIT_SENTENCE_FLUENCY, "Complete Your Sentence"),
    "intro_word_choice_specific_subject": (TRAIT_WORD_CHOICE, "Name Your Topic"),
    "intro_ideas_topic_match": (TRAIT_IDEAS, "Match Your Topic"),
    "intro_ideas_main_point": (TRAIT_IDEAS, "State Your Main Point"),
    "intro_ideas_point_and_reason": (TRAIT_IDEAS, "Review Your Explanation"),
    "intro_ideas_develop_main_point": (TRAIT_IDEAS, "Develop Your Main Point"),
    "intro_ideas_review_details": (TRAIT_IDEAS, "Review Your Details"),
    "intro_ideas_review_topic_connection": (TRAIT_IDEAS, "Review Topic Connection"),
    "intro_ideas_state_position": (TRAIT_IDEAS, "State Your Position"),
    # Body
    "body_organization_paragraph_shape": (TRAIT_ORGANIZATION, "Build Your Paragraph"),
    "body_organization_paragraph_link": (TRAIT_ORGANIZATION, "Review Paragraph Connections"),
    "body_ideas_develop_point": (TRAIT_IDEAS, "Develop Your Supporting Details"),
    "body_sentence_fluency_sentence_beginnings": (TRAIT_SENTENCE_FLUENCY, "Review Repeated Sentence Openings"),
    # Conclusion
    "conclusion_organization_bring_together": (TRAIT_ORGANIZATION, "Bring Ideas Together"),
    "conclusion_ideas_new_words": (TRAIT_IDEAS, "Explain New Words"),
    "conclusion_ideas_bring_together": (TRAIT_IDEAS, "Bring Ideas Together"),
    "conclusion_organization_clear_ending": (TRAIT_ORGANIZATION, "Clear Ending"),
    "conclusion_ideas_return_to_point": (TRAIT_IDEAS, "Return to Your Point"),
}


def _emitted_events(analysis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Accept both event flag conventions without claiming explicitly false events."""
    return {
        event["rule_id"]: event
        for event in analysis["rule_evidence"]
        if event.get("triggered", True) and event.get("fired", True)
    }


def _emitted_rule_ids(rule_ids: list[str], events: dict[str, Any]) -> list[str]:
    """Keep branch links honest when an expected event was not emitted."""
    return [rule_id for rule_id in rule_ids if rule_id in events]


class FeedbackService:
    """Turn stage findings into short revision guidance, never replacement prose."""

    def generate(self, analysis: dict[str, Any], *, include_trace: bool = False) -> dict[str, Any]:
        events = _emitted_events(analysis)
        observed_focus = analysis["lexical_topic_evidence"]["observed_focus_terms"]
        broad_focus = [term for term in observed_focus if term.strip().casefold() in BROAD_FOCUS_TERMS]
        specific_focus = [term for term in observed_focus if term.strip().casefold() not in BROAD_FOCUS_TERMS]
        central = analysis["observable_structure"]["central_direction_candidates"]
        list_finding = analysis["observable_structure"]["list_or_fragment_candidate"]
        incomplete = analysis["observable_structure"]["incomplete_subordinator_candidates"]
        development = analysis["development_evidence"]
        reason_observed = bool(analysis.get("reason_clause_evidence", {}).get("clauses"))
        reason_rules = [rule for rule in ("INTRO.REASON.CLAUSE_TOPIC_OVERLAP", "INTRO.REASON.NO_CLAUSE_TOPIC_OVERLAP") if rule in events]
        sentence_topic_rule = "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW"
        sentence_topic_review = bool(analysis.get("sentence_topic_evidence", {}).get("review_candidates")) and sentence_topic_rule in events
        position_missing = "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED" in events

        current_goal = "Introduce the topic, then tell readers the main point you plan to explain."
        goal_rules = ["INTRO.GOAL.OBSERVABLE_INTRODUCTION"]

        primary_rules: list[str]
        if analysis["text_presence"]["status"] == "EMPTY":
            primary_branch = "intro_neutral_empty"
            primary = "Your Introduction is empty. Start with one sentence about the topic in your own words."
            primary_rules = ["INTRO.TEXT.EMPTY_OR_NONALPHABETIC"]
        elif analysis["text_presence"]["status"] == "WHITESPACE_ONLY":
            primary_branch = "intro_neutral_whitespace"
            primary = "Your Introduction has only spaces. Start with one sentence about the topic in your own words."
            primary_rules = ["INTRO.TEXT.EMPTY_OR_NONALPHABETIC"]
        elif analysis["text_presence"]["status"] == "PUNCTUATION_ONLY":
            primary_branch = "intro_neutral_punctuation"
            primary = "Your Introduction has punctuation but no words. Start with one sentence about the topic in your own words."
            primary_rules = ["INTRO.TEXT.EMPTY_OR_NONALPHABETIC"]
        elif list_finding["keyword_list_candidate"]:
            primary_branch = "intro_organization_topic_intro"
            if observed_focus:
                primary = (
                    "Your matched assignment words appear as a list of ideas, and no recorded sentence connects them into one thought yet. "
                    "Choose one idea and write a sentence about it in your own words."
                )
            else:
                primary = (
                    "Your opening reads as a word list, and the checks found no assignment words to join with one idea. "
                    "Check the assignment, then write one sentence introducing an idea from it."
                )
            primary_rules = ["INTRO.TEXT.KEYWORD_LIST_CANDIDATE"]
        elif incomplete:
            primary_branch = "intro_sentence_fluency_complete_sentence"
            marker = incomplete[0]["text"]
            primary = (
                f"The words after '{marker}' may leave the thought unfinished. "
                "Add the missing part of your idea so the sentence tells readers your point."
            )
            primary_rules = [
                "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR",
                "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
            ]
        elif broad_focus and not specific_focus:
            primary_branch = "intro_word_choice_specific_subject"
            primary = (
                f"Only broad words such as {', '.join(broad_focus)} matched the assignment so far. "
                "Name the specific subject the assignment asks about in your opening sentence."
            )
            primary_rules = ["INTRO.TOPIC.FOCUS_TERMS_OBSERVED"]
        elif not observed_focus:
            primary_branch = "intro_ideas_topic_match"
            primary = (
                "The checks did not find your assignment words in the opening. "
                "Compare your opening with the assignment; you may be using different words for the same idea."
            )
            primary_rules = ["INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED"]
        elif sentence_topic_review:
            primary_branch = "intro_ideas_review_topic_connection"
            primary = "This sentence may not clearly connect to your topic. Read it with the sentences beside it and check how it helps explain your point."
            primary_rules = [sentence_topic_rule]
        elif position_missing:
            primary_branch = "intro_ideas_state_position"
            primary = "Your introduction discusses the topic, but I could not identify a clear position on the question."
            primary_rules = [
                "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED",
                "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
            ]
        elif central:
            if reason_observed:
                primary_branch = "intro_ideas_point_and_reason"
                primary = "The checks recorded a possible main statement and a 'because' part. Read them together and decide whether a reader needs more explanation."
                primary_rules = ["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE", *reason_rules]
            elif development["status"] != "STRUCTURAL_ELABORATION_CANDIDATE":
                primary_branch = "intro_ideas_develop_main_point"
                primary = "The checks recorded a possible main-point sentence, with no additional sentence parts under this check. Choose a reason, example, or explanation to add if readers need one."
                primary_rules = [
                    "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
                    "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE",
                ]
            else:
                primary_branch = "intro_ideas_review_details"
                primary = "The checks recorded a possible main statement and additional sentence parts. Choose one detail and review how it helps explain your point."
                primary_rules = ["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE", "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES"]
        else:
            one_sentence_with_specific_topic = (
                bool(specific_focus)
                and analysis["linguistic_observations"]["counts"]["sentence_count"] <= 1
            )
            if one_sentence_with_specific_topic:
                primary_branch = "intro_ideas_main_point"
                primary = "Assignment words were recorded, but this sentence did not match the main-statement pattern used by these checks. Read it aloud and decide whether it says what you want to explain."
                primary_rules = [
                    "INTRO.TOPIC.FOCUS_TERMS_OBSERVED",
                    "INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE",
                ]
            else:
                primary_branch = "intro_ideas_main_point"
                primary = (
                    "The checks have limited main-statement evidence for your opening. "
                    "Read it aloud and decide whether it says what you want to explain."
                )
                primary_rules = ["INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE"]

        working: list[str] = []
        working_rules: list[str] = []
        if specific_focus:
            working.append(
                f"These assignment words also appear in your opening: {', '.join(specific_focus)}. "
                "Check that they support the point you want to make."
            )
            working_rules.append("INTRO.TOPIC.FOCUS_TERMS_OBSERVED")
        context_with_specific_focus = [
            candidate
            for candidate in analysis["observable_structure"]["introductory_context_candidates"]
            if any(
                match["focus_term"] in specific_focus
                for match in candidate["topic_match_evidence"]
            )
        ]
        if context_with_specific_focus:
            working.append(
                "One sentence combines assignment words with a possible main point. "
                "Check that it answers the assignment question."
            )
            working_rules.append("INTRO.CONTEXT.TOPIC_AND_CLAUSE_CANDIDATE")
        if central and not specific_focus:
            working.append(
                "An opening sentence may state your main point. "
                "The checks record the sentence pattern; they cannot confirm the idea itself."
            )
            working_rules.append("INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE")

        needs_attention: list[str] = []
        attention_rules: list[str] = []
        if sentence_topic_review and sentence_topic_rule not in primary_rules:
            needs_attention.append("This sentence may not clearly connect to your topic. Read it with the sentences beside it and check how it helps explain your point.")
            attention_rules.append(sentence_topic_rule)
        if incomplete and not primary_rules.count("INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"):
            needs_attention.append(
                f"The words after '{incomplete[0]['text']}' may leave the thought unfinished. "
                "Add the missing part so the sentence states a complete point."
            )
            attention_rules.append("INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR")
        if not observed_focus and "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED" not in primary_rules:
            needs_attention.append(
                "No assignment words were found in the opening. "
                "Compare it with the assignment; you may be using different words for the same idea."
            )
            attention_rules.append("INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED")
        elif broad_focus and not specific_focus and "INTRO.TOPIC.FOCUS_TERMS_OBSERVED" not in primary_rules:
            needs_attention.append(
                f"Only broad words such as {', '.join(broad_focus)} were found. "
                "Name the assignment's specific subject in your opening."
            )
            attention_rules.append("INTRO.TOPIC.FOCUS_TERMS_OBSERVED")
        if position_missing and "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED" not in primary_rules:
            needs_attention.append(
                "Your introduction discusses the topic, but I could not identify a clear position on the question. "
                "Consider stating whether you support or oppose the proposal, using your own words."
            )
            attention_rules.append("INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED")
        if analysis["text_presence"]["status"] in {"EMPTY", "WHITESPACE_ONLY", "PUNCTUATION_ONLY"}:
            next_step_branch = "intro_neutral_write_first"
            next_step = "Write one opening sentence in your own words, then compare it with the assignment topic."
            next_step_rules = ["INTRO.TEXT.EMPTY_OR_NONALPHABETIC"]
        elif list_finding["keyword_list_candidate"]:
            next_step_branch = "intro_organization_topic_intro"
            next_step = (
                "Choose one idea from the words you matched and explain it in a sentence of your own."
                if observed_focus
                else "Look at the assignment, choose one idea you want to introduce, and write it as a sentence in your own words."
            )
            next_step_rules = ["INTRO.TEXT.KEYWORD_LIST_CANDIDATE"]
        elif incomplete:
            next_step_branch = "intro_sentence_fluency_complete_sentence"
            next_step = f"Read the words after '{incomplete[0]['text']}' and finish the thought with your main statement."
            next_step_rules = ["INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR"]
        elif broad_focus and not specific_focus:
            next_step_branch = "intro_word_choice_specific_subject"
            next_step = f"Compare your opening with the assignment. Broad words such as {', '.join(broad_focus)} do not name its specific subject on their own."
            next_step_rules = ["INTRO.TOPIC.FOCUS_TERMS_OBSERVED"]
        elif not observed_focus:
            next_step_branch = "intro_ideas_topic_match"
            next_step = "Compare your opening with the assignment. Different words for the same idea are fine when your point stays clear."
            next_step_rules = ["INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED"]
        elif sentence_topic_review:
            next_step_branch = "intro_ideas_review_topic_connection"
            next_step = "Read this sentence with the others. Does it help explain your point about the assignment topic?"
            next_step_rules = [sentence_topic_rule]
        elif position_missing:
            next_step_branch = "intro_ideas_state_position"
            next_step = "Consider stating whether you support or oppose the proposal, using your own words."
            next_step_rules = [
                "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED",
                "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
            ]
        elif not central:
            if specific_focus and analysis["linguistic_observations"]["counts"]["sentence_count"] <= 1:
                next_step_branch = "intro_ideas_main_point"
                next_step = "Read your opening aloud and check that a new reader can spot the topic and your point. Add words only when something is unclear."
            else:
                next_step_branch = "intro_ideas_main_point"
                next_step = "Read your opening aloud and check whether readers can find the topic and your point. Add or change words where needed."
            next_step_rules = ["INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE"]
        elif reason_observed:
            next_step_branch = "intro_ideas_point_and_reason"
            next_step = "Read your main statement with the explanation part. Keep it if it says what you intend, or add a detail a reader would need."
            next_step_rules = ["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE", *reason_rules]
        elif development["status"] != "STRUCTURAL_ELABORATION_CANDIDATE":
            next_step_branch = "intro_ideas_develop_main_point"
            next_step = "Choose a reason, example, or explanation that would help a reader understand your point. Add it in your own words if needed; no fixed starting word is required."
            next_step_rules = ["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE", "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE"]
        else:
            next_step_branch = "intro_ideas_review_details"
            next_step = "Choose one detail already in your opening. Keep it if it helps explain your point, or add information if a reader needs it."
            next_step_rules = ["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE", "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES"]
        # Resolve links only after message selection: provenance must not change
        # the existing attention-message suppression or branch priorities.
        goal_rules = _emitted_rule_ids(goal_rules, events)
        primary_rules = _emitted_rule_ids(primary_rules, events)
        working_rules = _emitted_rule_ids(working_rules, events)
        attention_rules = _emitted_rule_ids(attention_rules, events)
        next_step_rules = _emitted_rule_ids(next_step_rules, events)
        provenance = []
        field_rules = [
            ("Current Goal", goal_rules),
            ("Primary Feedback", primary_rules),
            ("What's Working", working_rules),
            ("Needs Attention", attention_rules),
            ("Next Step", next_step_rules),
        ]
        for field, rule_ids in field_rules:
            for rule_id in dict.fromkeys(rule_ids):
                event = events.get(rule_id)
                if event is None:
                    continue
                provenance.append(
                    {
                        "feedback_field": field,
                        "rule_id": event["rule_id"],
                        "triggering_condition": event["triggering_condition"],
                        "actual_evidence": event["evidence"],
                        "evidence_type": event["evidence_type"],
                        "limitations": event["limitation"],
                    }
                )

        result = {
            "Current Goal": current_goal,
            "Primary Feedback": primary,
            "What's Working": working,
            "Needs Attention": needs_attention,
            "Next Step": next_step,
            "Feedback Provenance": provenance,
            "interpretation_limit": "These checks highlight sentence structure and topic-word matches; they do not determine whether the idea is correct or meaningful.",
        }
        if include_trace:
            primary_conditions = {
                "intro_ideas_review_topic_connection": "a recorded sentence connection review event exists after higher-priority sentence and whole-topic checks",
                "intro_neutral_empty": "text_presence.status == EMPTY",
                "intro_neutral_whitespace": "text_presence.status == WHITESPACE_ONLY",
                "intro_neutral_punctuation": "text_presence.status == PUNCTUATION_ONLY",
                "intro_organization_topic_intro": "list_or_fragment_candidate.keyword_list_candidate is true",
                "intro_sentence_fluency_complete_sentence": "incomplete_subordinator_candidates is non-empty",
                "intro_word_choice_specific_subject": "no specific focus term matched; at least one broad focus term matched",
                "intro_ideas_topic_match": "observed_focus_terms is empty after higher-priority text, list, and sentence checks",
                "intro_ideas_state_position": "the assignment wording contains an argumentativeness cue, specific focus words and a subject-predicate candidate were observed, and no sentence pairs a modal or first-person stance-verb cue with a specific focus match; the checks cannot detect paraphrased positions",
                "intro_ideas_main_point": "no central subject-linked root candidate after higher-priority checks; this is limited pattern evidence, not absence of a meaningful point",
                "intro_ideas_develop_main_point": "central_direction_candidates is nonempty; no recorded because-clause; development status is not STRUCTURAL_ELABORATION_CANDIDATE",
                "intro_ideas_point_and_reason": "central_direction_candidates is nonempty and reason_clause_evidence.clauses is nonempty; focus-word presence or absence within the reason does not change this neutral review",
                "intro_ideas_review_details": "central_direction_candidates is nonempty; no recorded because-clause; development status is STRUCTURAL_ELABORATION_CANDIDATE; no logical relationship is inferred",
            }
            next_conditions = {
                "intro_ideas_review_topic_connection": "a recorded sentence connection review event exists after higher-priority sentence and whole-topic checks",
                "intro_neutral_write_first": "text_presence.status in {EMPTY, WHITESPACE_ONLY, PUNCTUATION_ONLY}",
                "intro_organization_topic_intro": "keyword_list_candidate is true",
                "intro_sentence_fluency_complete_sentence": "incomplete_subordinator_candidates is non-empty",
                "intro_word_choice_specific_subject": "no specific focus term; broad focus term(s) observed",
                "intro_ideas_topic_match": "no specific focus term and no broad focus term observed",
                "intro_ideas_state_position": primary_conditions["intro_ideas_state_position"],
                "intro_ideas_main_point": "no main-point sentence record; concise specific-focus texts and other openings both fall here",
                "intro_ideas_develop_main_point": primary_conditions["intro_ideas_develop_main_point"],
                "intro_ideas_point_and_reason": primary_conditions["intro_ideas_point_and_reason"],
                "intro_ideas_review_details": primary_conditions["intro_ideas_review_details"],
            }
            result["_Research Decision Trace"] = {
                "fields": {
                    "Current Goal": {"selection_branch": "stage_constant", "rule_ids": goal_rules, "selected_message": current_goal, "trait": None, "skill": None},
                    "Primary Feedback": {"selection_branch": primary_branch, "selection_condition": primary_conditions.get(primary_branch), "rule_ids": primary_rules, "selected_message": primary, "trait": (BRANCH_TRAIT_SKILL.get(primary_branch) or (None, None))[0], "skill": (BRANCH_TRAIT_SKILL.get(primary_branch) or (None, None))[1]},
                    "What's Working": {"selection_branch": "independent_evidence_checks", "selection_condition": "Each positive wording item is appended when its own existing evidence condition passes.", "rule_ids": working_rules, "selected_message_count": len(working), "trait": None, "skill": None},
                    "Needs Attention": {"selection_branch": "independent_attention_checks", "selection_condition": "Each caution is appended when its existing check identifies the corresponding condition.", "rule_ids": attention_rules, "selected_message_count": len(needs_attention), "trait": None, "skill": None},
                    "Next Step": {"selection_branch": next_step_branch, "selection_condition": next_conditions.get(next_step_branch), "rule_ids": next_step_rules, "selected_message": next_step, "trait": (BRANCH_TRAIT_SKILL.get(next_step_branch) or (None, None))[0], "skill": (BRANCH_TRAIT_SKILL.get(next_step_branch) or (None, None))[1]},
                },
                "unselected_alternatives": "FeedbackService does not record unselected candidate messages or a hidden ranking.",
                "priority_order": ["empty", "whitespace-only", "punctuation-only", "keyword-list candidate", "incomplete sentence", "broad-word-only match", "no assignment-word match", "sentence topic-connection review", "missing explicit position on an argumentative assignment", "recorded main statement with because-part (neutral review)", "recorded main statement with additional patterns (detail review)", "recorded main statement without additional patterns (development task)", "limited main-statement pattern evidence"],
                "selection_source": "Branch labels and rule IDs follow the recorded evidence checks; student-facing messages use separate plain-language wording.",
            }
            from services.tutoring_lessons import introduction_instructional_trace
            result["_Research Decision Trace"]["instructional_feedback"] = introduction_instructional_trace(analysis, result, result["_Research Decision Trace"])
        return result


    def generate_conclusion(self, analysis: dict[str, Any], *, include_trace: bool = False) -> dict[str, Any]:
        """Generate deterministic Conclusion feedback from actual Conclusion rule events."""
        events = _emitted_events(analysis)
        presence = analysis["text_presence"]
        lexical = analysis["lexical_topic_evidence"]
        intro = analysis["introduction_to_conclusion_continuity"]
        body = analysis["body_to_conclusion_continuity"]
        synthesis = analysis["synthesis_structure_candidates"]
        closure = analysis["closure_candidates"]
        new_material = analysis["new_material_observations"]

        current_goal = "Return to your main idea, connect it with earlier points, and leave the reader with one clear ending thought."
        goal_rules = ["CONCLUSION.GOAL.REVIEW_TOPIC_AND_PRIOR_IDEAS"]
        if presence["alphabetic_word_count"] == 0:
            primary_branch = "conclusion_neutral_empty"
            primary = "Your Conclusion is empty. Write one closing sentence about your main idea in your own words."
            primary_rules = ["CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC"]
        elif presence["keyword_list_candidate"]:
            primary_branch = "conclusion_organization_bring_together"
            if lexical["observed_focus_terms"]:
                primary = (
                    "Your matched assignment words appear as a list, and no recorded sentence gathers them into one ending. "
                    "Choose your main closing idea and write a closing sentence about it."
                )
            else:
                primary = (
                    "Your Conclusion reads as a word list, and the checks found no assignment words or gathering sentence. "
                    "Check the assignment, then write a closing sentence about one idea."
                )
            primary_rules = ["CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE"]
        elif not analysis["clause_candidates"]:
            primary_branch = "conclusion_neutral_review"
            primary = "The checks could not spot a complete closing sentence. Read your ending aloud and add any missing part."
            primary_rules = ["CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE"]
        elif new_material["unobserved_concept_candidates"]:
            primary_branch = "conclusion_ideas_new_words"
            examples = ", ".join(
                item["normalized_form"]
                for item in new_material["unobserved_concept_candidates"][:3]
            )
            primary = (
                f"These idea words ({examples}) do not appear in the earlier sections you provided. "
                "Decide whether readers need that idea explained earlier; the checks may miss reworded ideas."
            )
            primary_rules = ["CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS"]
        elif synthesis["candidates"]:
            primary_branch = "conclusion_ideas_bring_together"
            primary = (
                "One sentence combines ideas from more than one earlier section. "
                "Read it with those sections and check that it brings the ideas together as you intend."
            )
            primary_rules = ["CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE"]
        elif closure["candidates"]:
            primary_branch = "conclusion_organization_clear_ending"
            primary = (
                "Your ending has a final sentence or closing phrase. "
                "Read it with the whole essay and decide whether it leaves the point you want."
            )
            primary_rules = ["CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE"]
        elif lexical["observed_focus_terms"]:
            primary_branch = "conclusion_ideas_return_to_point"
            primary = (
                "Assignment words appear in your Conclusion without a recorded closing pattern. "
                "Check whether your ending returns to your main point."
            )
            primary_rules = ["CONCLUSION.TOPIC.FOCUS_MATCHES"]
        else:
            primary_branch = "conclusion_neutral_general"
            primary = (
                "Read your final sentences and check that they leave readers with your main point. "
                "There is no one required ending phrase."
            )
            primary_rules = ["CONCLUSION.CLOSURE.NO_CANDIDATE"]

        working: list[str] = []
        working_rules: list[str] = []
        if lexical["observed_focus_terms"]:
            working.append(
                "These assignment words also appear in your Conclusion: "
                + ", ".join(lexical["observed_focus_terms"])
                + ". Check that they return to your main idea."
            )
            working_rules.append("CONCLUSION.TOPIC.FOCUS_MATCHES")
        if intro["status"] == "LEXICAL_COMPARISON_AVAILABLE" and (
            intro["direct_lexical_continuity"] or intro["lemma_normalized_continuity"]
        ):
            working.append(
                "Some Conclusion words also appear in the Introduction. Check whether your ending returns to its main idea."
            )
            working_rules.append("CONCLUSION.CONTINUITY.INTRODUCTION_LEXICAL_COMPARISON")
        if body["status"] == "LEXICAL_COMPARISON_AVAILABLE" and (
            body["direct_lexical_continuity"] or body["lemma_normalized_continuity"]
        ):
            working.append(
                "Some Conclusion words also appear in the Body. Check whether your ending brings those points together."
            )
            working_rules.append("CONCLUSION.CONTINUITY.BODY_LEXICAL_COMPARISON")
        if synthesis["candidates"]:
            working.append(
                "One sentence combines ideas from more than one earlier section. Check whether it brings those ideas together."
            )
            working_rules.append("CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE")
        if closure["candidates"]:
            working.append(
                "Your ending has a final sentence or a closing phrase. Check whether it leaves the point you want."
            )
            working_rules.append("CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE")
        if new_material["phrase_combinations_of_observed_concepts"]:
            working.append(
                "This phrase uses words that appeared earlier, though the full phrase is new here."
            )
            working_rules.append("CONCLUSION.NEW_MATERIAL.KNOWN_CONCEPT_COMBINATION")

        needs: list[str] = []
        needs_rules: list[str] = []
        if presence["keyword_list_candidate"]:
            needs.append("No recorded sentence gathers these words into one ending. Choose your main closing idea and write a sentence about it.")
            needs_rules.append("CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE")
        if not lexical["observed_focus_terms"]:
            needs.append("No assignment words were found in the Conclusion. You may have used different words; compare the Conclusion with the assignment.")
            needs_rules.append("CONCLUSION.TOPIC.NO_FOCUS_MATCH")
        if not analysis["clause_candidates"]:
            needs.append("The checks could not spot a complete closing sentence. Read your ending aloud; this check can miss unusual writing styles.")
            needs_rules.append("CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE")
        if intro["status"] == "LEXICAL_COMPARISON_AVAILABLE" and not (
            intro["direct_lexical_continuity"] or intro["lemma_normalized_continuity"]
        ):
            needs.append("No shared key words were found with the Introduction. Reworded ideas may be missed, so compare the sections yourself.")
            needs_rules.append("CONCLUSION.CONTINUITY.INTRODUCTION_LEXICAL_COMPARISON")
        if body["status"] == "LEXICAL_COMPARISON_AVAILABLE" and not (
            body["direct_lexical_continuity"] or body["lemma_normalized_continuity"]
        ):
            needs.append("No shared key words were found with the Body. Reworded ideas may be missed, so compare the sections yourself.")
            needs_rules.append("CONCLUSION.CONTINUITY.BODY_LEXICAL_COMPARISON")
        if new_material["unobserved_concept_candidates"]:
            needs.append("Some idea words were not found in the earlier sections. Decide whether readers need more explanation earlier.")
            needs_rules.append("CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS")
        if synthesis["status"] == "NO_SYNTHESIS_STRUCTURE_CANDIDATE_OBSERVED" and (
            intro["status"] == "LEXICAL_COMPARISON_AVAILABLE"
            or body["status"] == "LEXICAL_COMPARISON_AVAILABLE"
        ):
            needs.append("The checks did not find a sentence using ideas from two earlier sections. They may miss reworded ideas; read the sections together.")
            needs_rules.append("CONCLUSION.SYNTHESIS.NO_CANDIDATE")
        if closure["status"] == "NO_CLOSURE_CANDIDATE_OBSERVED":
            needs.append("The checks did not find a final closing sentence or phrase. You do not need to use a fixed phrase.")
            needs_rules.append("CONCLUSION.CLOSURE.NO_CANDIDATE")
        needs.append("These checks record structure and wording only; they cannot tell whether an idea is true or whether the ending works well.")
        needs_rules.append("CONCLUSION.LIMITATION.NO_SEMANTIC_VALIDATION")

        if presence["alphabetic_word_count"] == 0:
            next_step_branch = "conclusion_neutral_empty"
            next_step = "Write one closing sentence in your own words. Return to your main point and choose a final thought."
            next_step_rules = ["CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC"]
        elif presence["keyword_list_candidate"]:
            next_step_branch = "conclusion_organization_bring_together"
            next_step = "Choose the main idea you want readers to remember. Connect it to an earlier point in your own words."
            next_step_rules = ["CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE"]
        elif new_material["unobserved_concept_candidates"]:
            next_step_branch = "conclusion_ideas_new_words"
            next_step = "Check the idea words that were not found earlier. Add an explanation before the Conclusion if readers need one."
            next_step_rules = ["CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS"]
        elif synthesis["candidates"]:
            next_step_branch = "conclusion_ideas_bring_together"
            next_step = "Read the Conclusion with the earlier sections. Does it bring the points you chose together?"
            next_step_rules = ["CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE"]
        elif not closure["candidates"]:
            next_step_branch = "conclusion_organization_clear_ending"
            next_step = "Choose the final point you want readers to remember. End in a way that fits your essay; no fixed phrase is needed."
            next_step_rules = ["CONCLUSION.CLOSURE.NO_CANDIDATE"]
        else:
            next_step_branch = "conclusion_organization_clear_ending"
            next_step = "Read the final sentence with the whole essay. Does it leave the ending you want?"
            next_step_rules = ["CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE"]

        goal_rules = _emitted_rule_ids(goal_rules, events)
        primary_rules = _emitted_rule_ids(primary_rules, events)
        working_rules = _emitted_rule_ids(working_rules, events)
        needs_rules = _emitted_rule_ids(needs_rules, events)
        next_step_rules = _emitted_rule_ids(next_step_rules, events)
        provenance = []
        for field, rule_ids in (
            ("Current Goal", goal_rules),
            ("Primary Feedback", primary_rules),
            ("What's Working", working_rules),
            ("Needs Attention", needs_rules),
            ("Next Step", next_step_rules),
        ):
            for rule_id in dict.fromkeys(rule_ids):
                event = events.get(rule_id)
                if event:
                    provenance.append(
                        {
                            "feedback_field": field,
                            "rule_id": rule_id,
                            "triggering_condition": event["triggering_condition"],
                            "actual_evidence": event["actual_evidence"],
                            "source_sections": event["source_sections"],
                            "evidence_type": event["evidence_type"],
                            "limitations": event["limitations"],
                        }
                    )
        result = {
            "Current Goal": current_goal,
            "Primary Feedback": primary,
            "What's Working": working,
            "Needs Attention": needs,
            "Next Step": next_step,
            "Feedback Provenance": provenance,
            "interpretation_limit": "This feedback is deterministic and observational; it does not judge semantic quality or readiness.",
        }
        if include_trace:
            primary_conditions = {
                "conclusion_neutral_empty": "text_presence.alphabetic_word_count == 0",
                "conclusion_organization_bring_together": "text_presence.keyword_list_candidate is true",
                "conclusion_neutral_review": "clause_candidates is empty",
                "conclusion_ideas_new_words": "new_material_observations.unobserved_concept_candidates is non-empty",
                "conclusion_ideas_bring_together": "synthesis_structure_candidates.candidates is non-empty",
                "conclusion_organization_clear_ending": "closure_candidates.candidates is non-empty",
                "conclusion_ideas_return_to_point": "lexical focus exists after all higher-priority branches do not apply",
                "conclusion_neutral_general": "no prior primary branch applies",
            }
            next_conditions = {
                "conclusion_neutral_empty": "alphabetic_word_count == 0",
                "conclusion_organization_bring_together": "keyword_list_candidate is true",
                "conclusion_ideas_new_words": "unobserved_concept_candidates is non-empty",
                "conclusion_ideas_bring_together": "synthesis candidates exist after earlier branches do not apply",
                "conclusion_organization_clear_ending": "a closure record exists (or not) and earlier branches do not apply",
            }
            result["_Research Decision Trace"] = {
                "fields": {
                    "Current Goal": {"selection_branch": "stage_constant", "rule_ids": goal_rules, "selected_message": current_goal, "trait": None, "skill": None},
                    "Primary Feedback": {"selection_branch": primary_branch, "selection_condition": primary_conditions.get(primary_branch), "rule_ids": primary_rules, "selected_message": primary, "trait": (BRANCH_TRAIT_SKILL.get(primary_branch) or (None, None))[0], "skill": (BRANCH_TRAIT_SKILL.get(primary_branch) or (None, None))[1]},
                    "What's Working": {"selection_branch": "independent_evidence_checks", "selection_condition": "Each item is appended when its existing lexical, continuity, synthesis, closure, or phrase-combination condition is met.", "rule_ids": working_rules, "selected_message_count": len(working), "trait": None, "skill": None},
                    "Needs Attention": {"selection_branch": "independent_attention_checks", "selection_condition": "Each caution is appended when its corresponding existing stage result meets the negative/limitation condition.", "rule_ids": needs_rules, "selected_message_count": len(needs), "trait": None, "skill": None},
                    "Next Step": {"selection_branch": next_step_branch, "selection_condition": next_conditions.get(next_step_branch), "rule_ids": next_step_rules, "selected_message": next_step, "trait": (BRANCH_TRAIT_SKILL.get(next_step_branch) or (None, None))[0], "skill": (BRANCH_TRAIT_SKILL.get(next_step_branch) or (None, None))[1], "limitation": "Rule links describe the selected Next Step condition, not necessarily the Primary Feedback condition."},
                },
                "unselected_alternatives": "FeedbackService does not record unselected candidate messages or a hidden ranking.",
                "priority_order": ["empty", "keyword-list candidate", "no closing sentence", "unobserved idea words", "early ideas combined", "closing pattern", "topic words only", "general review"],
                "selection_source": "Branch labels and rule IDs follow the recorded evidence checks; student-facing messages use separate plain-language wording.",
            }
        return result

    def generate_body(self, analysis: dict[str, Any], *, include_trace: bool = False) -> dict[str, Any]:
        """Create Body-specific feedback tied to the Body analyzer's rule events."""
        events = _emitted_events(analysis)
        paragraphs = analysis["paragraphs"]
        substantive = [paragraph for paragraph in paragraphs if paragraph["substantive"]]
        cross_pairs = analysis["cross_paragraph_continuity"]["paragraph_pairs"]
        body_links = analysis["introduction_to_body_continuity"]

        goal = "Body review covers recorded paragraph structure, development patterns, sentence openings, and wording links."
        goal_rules = ["BODY.GOAL.DEVELOP_BODY_IDEAS"]

        list_paragraph = limited_paragraph = repeated_opening = shift_pair = None
        primary_rules: list[str]
        if not substantive:
            primary_branch = "body_neutral_empty"
            primary = "The Body has no words yet. Write your first paragraph in your own words."
            primary_rules = ["BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH"]
        else:
            list_paragraph = next(
                (p for p in substantive if p["fragment_or_list_candidate"]["keyword_list_candidate"]
                 and f"BODY.P{p['paragraph_index']}.PARAGRAPH.KEYWORD_LIST_CANDIDATE" in events),
                None,
            )
            shift_pair = next(
                (
                    pair
                    for pair in cross_pairs
                    if pair["status"] == "NO_EXPLICIT_LEXICAL_LINK_OBSERVED"
                    and "BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON" in events
                ),
                None,
            )
            limited_paragraph = next(
                (
                    p
                    for p in substantive
                    if not p["supporting_detail_candidates"]["candidates"]
                    and p["counts"]["sentence_count"] > 0
                    and p.get("clause_structure_candidates")
                    and not p["fragment_or_list_candidate"]["keyword_list_candidate"]
                    and f"BODY.P{p['paragraph_index']}.SUPPORTING_DETAIL.NOT_OBSERVED" in events
                ),
                None,
            )
            repeated_opening = next(
                (
                    (p, p["repetition_observations"]["repeated_sentence_openings"][0])
                    for p in substantive
                    if p["repetition_observations"]["repeated_sentence_openings"]
                    and f"BODY.P{p['paragraph_index']}.REPETITION.REPEATED_SENTENCE_OPENINGS" in events
                ),
                None,
            )

            if list_paragraph:
                primary_branch = "body_organization_paragraph_shape"
                index = list_paragraph["paragraph_index"]
                if list_paragraph["observed_focus_terms"]:
                    primary = (
                        f"Paragraph {index} contains assignment words as a list of ideas, and no recorded sentence connects them into one thought. "
                        "Choose one idea and explain it in a sentence of your own."
                    )
                else:
                    primary = (
                        f"Paragraph {index} reads as a word list, and the checks found no assignment words or connecting sentence. "
                        "Look at the assignment, then write a sentence about one idea in your own words."
                    )
                primary_rules = [f"BODY.P{index}.PARAGRAPH.KEYWORD_LIST_CANDIDATE"]
            elif limited_paragraph:
                primary_branch = "body_ideas_develop_point"
                index = limited_paragraph["paragraph_index"]
                primary = (
                    f"Paragraph {index} has a possible statement, but the checks did not record another sentence part developing it. "
                    "Other kinds of supporting ideas may still be present."
                )
                primary_rules = [f"BODY.P{index}.SUPPORTING_DETAIL.NOT_OBSERVED"]
            elif repeated_opening:
                primary_branch = "body_sentence_fluency_sentence_beginnings"
                paragraph, opening = repeated_opening
                index = paragraph["paragraph_index"]
                primary = (
                    f"More than one sentence in Paragraph {index} begins with '{opening['opening']}'. "
                    "Change one beginning only if the repetition sounds awkward."
                )
                primary_rules = [f"BODY.P{index}.REPETITION.REPEATED_SENTENCE_OPENINGS"]
            elif shift_pair:
                primary_branch = "body_organization_paragraph_link"
                left_index, right_index = shift_pair["paragraph_pair"]
                primary = (
                    f"The wording check found no shared content words or listed linking phrase between Paragraphs {left_index} and {right_index}. "
                    "Different wording can still express a connection."
                )
                primary_rules = ["BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON"]
            else:
                primary_branch = "body_neutral_observable"
                primary = "The available checks did not identify a specific structural concern in this Body section."
                primary_rules = [
                    f"BODY.P{paragraph['paragraph_index']}.PARAGRAPH.SEGMENTED"
                    for paragraph in substantive
                ]

        working: list[str] = []
        working_rules: list[str] = []
        for paragraph in substantive:
            index = paragraph["paragraph_index"]
            if paragraph["fragment_or_list_candidate"]["keyword_list_candidate"]:
                # Keep its lexical observations in the Rule Base trace, but do
                # not frame keyword stuffing as a paragraph strength.
                continue
            if paragraph["observed_focus_terms"] and f"BODY.P{index}.PARAGRAPH.FOCUS_TERMS_OBSERVED" in events:
                working.append(
                    f"Paragraph {index} uses assignment words such as: "
                    + ", ".join(paragraph["observed_focus_terms"])
                    + "."
                )
                working_rules.append(f"BODY.P{index}.PARAGRAPH.FOCUS_TERMS_OBSERVED")
            if paragraph["topic_sentence_candidates"] and f"BODY.P{index}.TOPIC_SENTENCE.CANDIDATE" in events:
                working.append(
                    f"Paragraph {index} has a sentence that may introduce its idea."
                )
                working_rules.append(f"BODY.P{index}.TOPIC_SENTENCE.CANDIDATE")
            if paragraph["supporting_detail_candidates"]["candidates"] and f"BODY.P{index}.SUPPORTING_DETAIL.CANDIDATE" in events:
                working.append(
                    f"Paragraph {index} has additional sentence parts that may add detail."
                )
                working_rules.append(f"BODY.P{index}.SUPPORTING_DETAIL.CANDIDATE")

            repetitions = paragraph["repetition_observations"]
            repeated_terms = repetitions["repeated_surface_content_words"]
            if repeated_terms and f"BODY.P{index}.REPETITION.REPEATED_SURFACE_CONTENT_WORDS" in events:
                first = repeated_terms[0]
                working.append(
                    f"Paragraph {index} uses '{first['term']}' {first['occurrence_count']} times. "
                    "Repeating a word can help readers follow an idea; it is not automatically a problem."
                )
                working_rules.append(f"BODY.P{index}.REPETITION.REPEATED_SURFACE_CONTENT_WORDS")

        needs: list[str] = []
        needs_rules: list[str] = []
        for paragraph in substantive:
            index = paragraph["paragraph_index"]
            if (paragraph["fragment_or_list_candidate"]["keyword_list_candidate"]
                    and f"BODY.P{index}.PARAGRAPH.KEYWORD_LIST_CANDIDATE" in events):
                needs.append(
                    f"Paragraph {index} has no recorded sentence connecting its words. Choose one idea and explain it in your own words."
                )
                needs_rules.append(f"BODY.P{index}.PARAGRAPH.KEYWORD_LIST_CANDIDATE")
            if (paragraph.get("clause_structure_candidates")
                    and not paragraph["supporting_detail_candidates"]["candidates"]
                    and not paragraph["fragment_or_list_candidate"]["keyword_list_candidate"]
                    and f"BODY.P{index}.SUPPORTING_DETAIL.NOT_OBSERVED" in events):
                needs.append(
                    f"Paragraph {index} has a possible statement, but no additional sentence part was recorded under this check."
                )
                needs_rules.append(f"BODY.P{index}.SUPPORTING_DETAIL.NOT_OBSERVED")
            if (paragraph["repetition_observations"]["repeated_sentence_openings"]
                    and f"BODY.P{index}.REPETITION.REPEATED_SENTENCE_OPENINGS" in events):
                needs.append(f"Paragraph {index} has repeated sentence openings. Repetition can be intentional; review how it sounds.")
                needs_rules.append(f"BODY.P{index}.REPETITION.REPEATED_SENTENCE_OPENINGS")

        if analysis["cross_paragraph_continuity"]["status"] == "PAIRWISE_OBSERVATIONS":
            if shift_pair:
                needs.append(
                    "A neighboring paragraph pair has no recorded shared wording or listed linking phrase. This does not prove a missing connection."
                )
                needs_rules.append("BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON")

        if body_links["status"] == "LEXICAL_COMPARISON_AVAILABLE":
            if (body_links["direct_lexical_continuity"] or body_links["lemma_normalized_continuity"]) and "BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON" in events and any(not p["fragment_or_list_candidate"]["keyword_list_candidate"] for p in substantive):
                working.append(
                    "Some Body words also appear in the Introduction supplied for comparison."
                )
                working_rules.append("BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON")

        if not substantive:
            next_step_branch = "body_neutral_empty"
            next_step = "Write your first Body paragraph in your own words. Explain one idea from your assignment."
            next_step_rules = ["BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH"]
        elif list_paragraph:
            next_step_branch = "body_organization_paragraph_shape"
            next_step = (
                "Choose one recorded idea from these words and explain it in a sentence of your own."
                if list_paragraph["observed_focus_terms"]
                else "Look at the assignment, choose one idea, and explain it in a sentence of your own."
            )
            next_step_rules = [f"BODY.P{list_paragraph['paragraph_index']}.PARAGRAPH.KEYWORD_LIST_CANDIDATE"]
        elif limited_paragraph:
            next_step_branch = "body_ideas_develop_point"
            next_step = f"Think of an activity, example, or explanation that could help readers understand Paragraph {limited_paragraph['paragraph_index']}. Write it in your own words if needed."
            next_step_rules = [f"BODY.P{limited_paragraph['paragraph_index']}.SUPPORTING_DETAIL.NOT_OBSERVED"]
        elif repeated_opening:
            next_step_branch = "body_sentence_fluency_sentence_beginnings"
            next_step = "Read the repeated sentence beginnings aloud. Change one if the repetition sounds awkward."
            next_step_rules = [f"BODY.P{repeated_opening[0]['paragraph_index']}.REPETITION.REPEATED_SENTENCE_OPENINGS"]
        elif shift_pair:
            next_step_branch = "body_organization_paragraph_link"
            next_step = "Read the neighboring paragraphs together. Explain their connection in your own words only if a reader would need it; no particular linking word is required."
            next_step_rules = ["BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON"]
        else:
            next_step_branch = "body_neutral_observable"
            next_step = ""
            next_step_rules = []

        goal_rules = _emitted_rule_ids(goal_rules, events)
        primary_rules = _emitted_rule_ids(primary_rules, events)
        working_rules = _emitted_rule_ids(working_rules, events)
        needs_rules = _emitted_rule_ids(needs_rules, events)
        next_step_rules = _emitted_rule_ids(next_step_rules, events)
        provenance = []
        for field, rule_ids in (
            ("Current Goal", goal_rules),
            ("Primary Feedback", primary_rules),
            ("What's Working", working_rules),
            ("Needs Attention", needs_rules),
            ("Next Step", next_step_rules),
        ):
            for rule_id in dict.fromkeys(rule_ids):
                event = events.get(rule_id)
                if event:
                    provenance.append(
                        {
                            "feedback_field": field,
                            "rule_id": rule_id,
                            "triggering_condition": event["triggering_condition"],
                            "actual_evidence": event["actual_evidence"],
                            "evidence_type": event["evidence_type"],
                            "limitations": event["limitations"],
                        }
                    )
        result = {
            "Current Goal": goal,
            "Primary Feedback": primary,
            "What's Working": working,
            "Needs Attention": needs,
            "Next Step": next_step,
            "Feedback Provenance": provenance,
            "interpretation_limit": (
                "This deterministic feedback reports observed Body structure and lexical evidence; it does not validate support, logic, meaning, or readiness."
            ),
        }
        if include_trace:
            primary_conditions = {
                "body_neutral_empty": "no substantive paragraph exists",
                "body_organization_paragraph_shape": "first substantive list-like paragraph with its fired KEYWORD_LIST_CANDIDATE event",
                "body_organization_paragraph_link": "first pair with NO_EXPLICIT_LEXICAL_LINK_OBSERVED and its fired paragraph-comparison event",
                "body_ideas_develop_point": "first substantive non-list paragraph with a recorded subject-linked clause, no additional detail candidates, and its fired SUPPORTING_DETAIL.NOT_OBSERVED event",
                "body_sentence_fluency_sentence_beginnings": "first substantive paragraph with repeated_sentence_openings and its fired repeated-opening event",
                "body_neutral_observable": "no supported list, development, repeated-opening, or adjacent-wording review concern was selected; missing Introduction context and absent keywords are not writing defects",
            }
            next_conditions = {
                "body_neutral_empty": "no substantive paragraph exists",
                "body_organization_paragraph_shape": primary_conditions["body_organization_paragraph_shape"],
                "body_organization_paragraph_link": primary_conditions["body_organization_paragraph_link"],
                "body_ideas_develop_point": primary_conditions["body_ideas_develop_point"],
                "body_sentence_fluency_sentence_beginnings": primary_conditions["body_sentence_fluency_sentence_beginnings"],
                "body_neutral_observable": primary_conditions["body_neutral_observable"],
            }
            result["_Research Decision Trace"] = {
                "fields": {
                    "Current Goal": {"selection_branch": "stage_constant", "rule_ids": goal_rules, "selected_message": goal, "trait": None, "skill": None},
                    "Primary Feedback": {"selection_branch": primary_branch, "selection_condition": primary_conditions.get(primary_branch), "rule_ids": primary_rules, "selected_message": primary, "trait": (BRANCH_TRAIT_SKILL.get(primary_branch) or (None, None))[0], "skill": (BRANCH_TRAIT_SKILL.get(primary_branch) or (None, None))[1]},
                    "What's Working": {"selection_branch": "paragraph_evidence_loop", "selection_condition": "Per substantive non-list paragraph, append only observations with matching fired source events. Introduction wording overlap is not promoted as a strength for an entirely list-like Body.", "rule_ids": working_rules, "selected_message_count": len(working), "trait": None, "skill": None},
                    "Needs Attention": {"selection_branch": "paragraph_and_cross_stage_checks", "selection_condition": "Append only supported list, development, repeated-opening and adjacent-wording review concerns. Lexical topic/Introduction absence and system limitations are not student defects.", "rule_ids": needs_rules, "selected_message_count": len(needs), "trait": None, "skill": None},
                    "Next Step": {"selection_branch": next_step_branch, "selection_condition": next_conditions.get(next_step_branch), "rule_ids": next_step_rules, "selected_message": next_step, "trait": (BRANCH_TRAIT_SKILL.get(next_step_branch) or (None, None))[0], "skill": (BRANCH_TRAIT_SKILL.get(next_step_branch) or (None, None))[1], "limitation": "No revision task is selected for the neutral state. Missing Introduction context is availability information, not a student writing concern."},
                },
                "priority_order": ["empty", "first supported list-like paragraph", "first supported paragraph-development concern", "first verified repeated sentence opening", "first adjacent-pair wording review", "no supported concern selected"],
                "selection_status": "NO_SUPPORTED_CONCERN_SELECTED" if primary_branch == "body_neutral_observable" else "INPUT_REQUIRED" if primary_branch == "body_neutral_empty" else "SUPPORTED_CONCERN_SELECTED",
                "selection_checks": [],
                "unselected_alternatives": "All Body selection checks below record matched conditions and higher-priority selection; these are FeedbackService records, not new NLP Rule Events.",
            }
            checks = [
                ("body_neutral_empty", not substantive, [], ["BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH"]),
                ("body_organization_paragraph_shape", bool(list_paragraph), [list_paragraph["paragraph_index"]] if list_paragraph else [], [f"BODY.P{list_paragraph['paragraph_index']}.PARAGRAPH.KEYWORD_LIST_CANDIDATE"] if list_paragraph else []),
                ("body_ideas_develop_point", bool(limited_paragraph), [limited_paragraph["paragraph_index"]] if limited_paragraph else [], [f"BODY.P{limited_paragraph['paragraph_index']}.SUPPORTING_DETAIL.NOT_OBSERVED"] if limited_paragraph else []),
                ("body_sentence_fluency_sentence_beginnings", bool(repeated_opening), [repeated_opening[0]["paragraph_index"]] if repeated_opening else [], [f"BODY.P{repeated_opening[0]['paragraph_index']}.REPETITION.REPEATED_SENTENCE_OPENINGS"] if repeated_opening else []),
                ("body_organization_paragraph_link", bool(shift_pair), shift_pair["paragraph_pair"] if shift_pair else [], ["BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON"] if shift_pair else []),
            ]
            trace = result["_Research Decision Trace"]
            for priority, (branch, matched, indices, ids) in enumerate(checks, 1):
                trace["selection_checks"].append({"priority": priority, "branch": branch,
                    "condition": primary_conditions[branch], "condition_matched": matched,
                    "paragraph_indices": indices, "rule_ids": _emitted_rule_ids(ids, events),
                    "status": "SELECTED" if branch == primary_branch else "MATCHED_NOT_SELECTED_HIGHER_PRIORITY" if matched else "NOT_MATCHED"})
            from services.tutoring_lessons import body_instructional_trace

            trace["instructional_feedback"] = body_instructional_trace(analysis, result, trace)
        return result
