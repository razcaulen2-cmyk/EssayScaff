"""Conservative sentence-level wording observations over one existing TopicService result.

No parsing, semantic classification, similarity scores, or grammatical verdicts.
"""

from typing import Any


REVIEW_RULE = "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW"
CONDITION = (
    "Explicit teacher focus and a matched neighboring sentence are available; "
    "this verified noun-and-predicate sentence has no focus match, no shared neighboring "
    "content lemma, and no third-person or demonstrative reference cue."
)
LIMITATION = (
    "Missing wording links suggest a review only, not irrelevance. Pronoun cues "
    "are not resolved references; shared words do not establish relevance, logic, "
    "or truth. Other reworded connections can be missed."
)


def sentence_topic_evidence(topic: dict[str, Any]) -> dict[str, Any]:
    """Reuse exact sentence/token spans, normalized concepts, and focus matches.

    Only a local gap beside an explicitly matched sentence can emit a review.
    A pronoun cue or shared content wording defers to contextual human review.
    The separate curated-association channel stays informational; it is not a
    validated smartphone vocabulary and is not promoted to confirmed matching.
    """
    linguistic = topic["linguistic_analysis"]
    source = linguistic["text"]
    sentences = linguistic["sentences"]
    focus = topic["teacher_context"]
    matches = [m for item in topic["confirmed_lexical_observations"]
               for key in ("direct_matches", "normalized_matches")
               for m in item[key]]

    def verified(span):
        start, end = span.get("start"), span.get("end")
        return (type(start) is int and type(end) is int and 0 <= start < end <= len(source)
                and source[start:end] == span.get("text", span.get("observed_text")))

    rows = []
    for index, sentence in enumerate(sentences):
        valid = verified(sentence) and bool(sentence["tokens"]) and all(
            verified(t) and sentence["start"] <= t["start"] < t["end"] <= sentence["end"]
            for t in sentence["tokens"]
        )
        tokens = sentence["tokens"] if valid else []
        terms = [item["term"] for item in topic["confirmed_lexical_observations"]
                 if any(sentence["start"] <= m["start"] < m["end"] <= sentence["end"] and verified(m)
                        for key in ("direct_matches", "normalized_matches") for m in item[key])] if valid else []
        rows.append({
            "sentence_index": index, "text": sentence["text"],
            "start": sentence["start"], "end": sentence["end"], "span_verified": valid,
            "matched_focus_terms": terms,
            "focus_matches": [m for m in matches if valid and verified(m)
                              and sentence["start"] <= m["start"] < m["end"] <= sentence["end"]],
            "concepts": [c["normalized_form"] for c in topic["student_concepts"]
                         if valid and any(verified(o) and sentence["start"] <= o["start"] < o["end"] <= sentence["end"]
                                          for o in c["occurrences"])],
            "content_lemmas": sorted({(t["lemma"] or t["text"]).casefold() for t in tokens
                                      if t["is_alpha"] and t["pos"] in {"NOUN", "PROPN", "VERB", "ADJ"}
                                      and (t["lemma"] or t["text"]).casefold() not in {"be", "have", "do"}}),
            "reference_cues": [t["text"] for t in tokens if t["pos"] in {"PRON", "DET", "ADV"}
                               and t["text"].casefold() in {"he", "she", "it", "they", "him", "her", "them",
                                                          "his", "its", "their", "this", "that", "these", "those", "here", "there"}],
            "has_noun": any(t["is_alpha"] and t["pos"] in {"NOUN", "PROPN"} for t in tokens),
            "has_predicate": any(t["pos"] in {"VERB", "AUX"} and t["dependency"] == "ROOT" for t in tokens),
            "condition": CONDITION, "limitation": LIMITATION,
        })
    for index, row in enumerate(rows):
        neighbors = [r for j, r in enumerate(rows) if abs(j - index) == 1 and r["span_verified"]]
        row["neighbor_sentence_indices"] = [r["sentence_index"] for r in neighbors]
        row["matched_neighbor_indices"] = [r["sentence_index"] for r in neighbors if r["matched_focus_terms"]]
        row["shared_neighbor_lemmas"] = sorted(set(row["content_lemmas"]) & {w for r in neighbors for w in r["content_lemmas"]})
        if not row["span_verified"]:
            status = "INSUFFICIENT_SPAN_EVIDENCE"
        elif row["matched_focus_terms"]:
            status = "WORDING_MATCH_OBSERVED_NOT_RELEVANCE"
        elif focus["focus_source"] != "teacher_provided" or not focus["focus_terms"]:
            status = "REVIEW_WITH_TEACHER_NO_CONFIGURED_FOCUS"
        elif not row["matched_neighbor_indices"] or not row["has_noun"] or not row["has_predicate"]:
            status = "INSUFFICIENT_LOCAL_TOPIC_EVIDENCE"
        elif row["reference_cues"] or row["shared_neighbor_lemmas"]:
            status = "CONTEXT_REVIEW_DEFERRED"
        else:
            status = "POSSIBLE_CONNECTION_GAP"
        row["status"] = status
        row["review_signal"] = status == "POSSIBLE_CONNECTION_GAP"
    return {"sentences": rows, "condition": CONDITION, "limitation": LIMITATION,
            "review_candidates": [r for r in rows if r["review_signal"]],
            "source": "Existing TopicService focus spans, concepts, and spaCy sentence/token records; no additional NLP call."}
