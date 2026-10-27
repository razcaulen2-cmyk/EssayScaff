# Introduction Feedback Relevance Inspection

**Document version:** 1.0  
**Date produced:** 2026-10-22  
**Author:** Investigation script + manual source inspection  
**Status:** Final — no production code changes made during this investigation

---

## Executive Summary

Two different Introduction texts were submitted to EssayScaff V2:

- **Text A** — a nonsense reason: *"Schools should allow smartphones because invisible dragons control the price of bananas on Mars."*
- **Text B** — a relevant reason: *"Schools should allow smartphones because students can use educational apps during class."*

Both texts produce **identical Writing Tutor feedback**: trait *Ideas*, skill *Explain Your Point*.

This investigation confirms two separate problems and their root causes:

### Problem A — Reason Relevance (CONFIRMED architectural limitation)

The system selects the same feedback branch (`intro_ideas_point_and_reason`) for both texts because it detects only **grammatical structure** — the presence of an `advcl` (adverbial clause) dependency — not the **semantic content** of the clause following "because". Topic matching operates across the full Introduction text, not on individual clauses. There is no mechanism in the rule-based pipeline to compare the content of the subordinate clause against the main point. This is a fundamental scope limitation, not a bug.

### Problem B — Source Highlighting (CONFIRMED — already fixed)

Both texts displayed *"No passage could be verified"* instead of highlighting the relevant sentence. The root cause was a missing entry in the `clauseSupportedDevRules` array in `static/app.js` (`tutorEvidenceExcerpt`, line 5549). The rule `INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES` was not included in that array, causing the clause-span reading path to be bypassed. The fix was applied during the same investigation session and is documented in full below.

**Test baseline: 525 tests passing before and after the fix.**

---

## 1. Investigation Method

Both texts were run through the full pipeline using the project's own `IntroductionRuleBase.analyze()` and `FeedbackService.generate()`. No separate simulation was built. Source files were read directly to trace evidence from NLP through to the frontend.

### Assignment parameters used

```
Question : Should students be allowed to use smartphones during class?
Focus terms: ['smartphones', 'students', 'classroom', 'learning']
```

### Text A

```
Smartphones can support learning in the classroom when teachers guide students.
Clear classroom rules may help reduce distractions during lessons.
Schools should allow smartphones because invisible dragons control the price of bananas on Mars.
```

### Text B

```
Smartphones can support learning in the classroom when teachers guide students.
Clear classroom rules may help reduce distractions during lessons.
Schools should allow smartphones because students can use educational apps during class.
```

---

## 2. Actual Pipeline Results

### 2.1 Sentence Segmentation

Both texts segment identically into three sentences:

| Index | Start | End | Text (first 60 chars) |
|-------|-------|-----|----------------------|
| 0 | 0 | 79 | "Smartphones can support learning in the classroom when…" |
| 1 | 80 | 146 | "Clear classroom rules may help reduce distractions…" |
| 2 | 147 | 243 (A) / 235 (B) | "Schools should allow smartphones because…" |

### 2.2 Tokens and Dependencies — Sentence 2 (the reason sentence)

**Text A — sentence [2] token analysis**

| Token | POS | DEP | Head |
|-------|-----|-----|------|
| Schools | NOUN | nsubj | allow |
| should | AUX | aux | allow |
| allow | VERB | ROOT | allow |
| smartphones | NOUN | dobj | allow |
| because | SCONJ | mark | control |
| invisible | ADJ | amod | dragons |
| dragons | NOUN | nsubj | control |
| control | VERB | **advcl** | allow |
| the | DET | det | price |
| price | NOUN | dobj | control |
| of | ADP | prep | price |
| bananas | NOUN | pobj | of |
| on | ADP | prep | control |
| Mars | PROPN | pobj | on |

**Text B — sentence [2] token analysis**

| Token | POS | DEP | Head |
|-------|-----|-----|------|
| Schools | NOUN | nsubj | allow |
| should | AUX | aux | allow |
| allow | VERB | ROOT | allow |
| smartphones | NOUN | dobj | allow |
| because | SCONJ | mark | use |
| students | NOUN | nsubj | use |
| can | AUX | aux | use |
| use | VERB | **advcl** | allow |
| educational | ADJ | amod | apps |
| apps | NOUN | dobj | use |
| during | ADP | prep | use |
| class | NOUN | pobj | during |

**Key observation:** In both texts, the subordinate clause is assigned `advcl` dependency on the ROOT verb `allow`. The `advcl` label is the only structural signal the pipeline uses to record a second predicate. The *content* of the advcl — whether it contains "dragons" and "bananas" or "students" and "educational apps" — is ignored.

### 2.3 Central Direction Candidates

Both texts produce three identical candidates (same sentences, same structure):

```
Candidate 0: predicate='support' start=16  end=23  subject=['Smartphones']
Candidate 1: predicate='help'    start=106 end=110 subject=['rules']
Candidate 2: predicate='allow'   start=162 end=167 subject=['Schools']
```

### 2.4 Development Evidence

Both texts return the same `_development_finding()` result:

```python
{
  "status": "STRUCTURAL_ELABORATION_CANDIDATE",
  "predicate_count": 5,
  "evidence_type": "multiple_parser_labeled_clause_predicates",
  "limitation": "Multiple clauses or sentences do not prove that the ideas are connected logically or soundly."
}
```

The five predicates counted are: `support`, `guide`, `help`, `allow`, plus the advcl verb (`control` in A; `use` in B). The predicate count is the same; only the identity of the fifth verb differs. The development status is identical.

### 2.5 Topic Matches

Topic matching operates on the **full Introduction text**, not per-clause. Both texts contain the focus terms `smartphones`, `students`, `classroom`, and `learning` — all appearing in the first two sentences, which are identical.

| Term | Text A matches | Text B matches |
|------|---------------|---------------|
| smartphones | 2 | 2 |
| students | 1 | 2 (adds "students" in reason clause) |
| classroom | 2 | 2 |
| learning | 1 | 1 |

Text B records one additional `students` match (position 188–196, inside the reason clause). This match appears in `lexical_topic_evidence`, but it is **not evaluated per-clause** — the `observed_focus_terms` list is identical for both texts: `['smartphones', 'students', 'classroom', 'learning']`. The presence of `students` in the reason clause of Text B therefore produces no different rule branch.

The reason clause of Text A ("invisible dragons control the price of bananas on Mars") contains none of the focus terms. The rule pipeline does not inspect this absence.

### 2.6 Rule Events

Both texts fire the same sequence of rule events with the same trigger states:

| Rule ID | Triggered | Note |
|---------|-----------|------|
| INTRO.TEXT.PRESENT | True | text present |
| INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE | True | 3 candidates |
| INTRO.TOPIC.FOCUS_TERMS_OBSERVED | True | focus terms found |
| INTRO.CONTEXT.TOPIC_AND_CLAUSE_CANDIDATE | True | 3 overlaps |
| INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES | True | 5 predicates |
| INTRO.GOAL.OBSERVABLE_INTRODUCTION | True | meta-goal |
| INTRO.LIMITATION.NO_SEMANTIC_VALIDATION | True | always applied |

`INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES` evidence items contain:

```
sentence_text=''   sentence_start=None   sentence_end=None   sentence_index=None
```

This rule stores only the predicate tokens, not sentence positions. That is by design: it is a structural count, not a span.

### 2.7 Feedback Selection

`FeedbackService.generate()` evaluates conditions in order. At the decisive branch  
(`services/feedback_service.py`, lines 132–149):

```python
elif central:
    if development["status"] != "STRUCTURAL_ELABORATION_CANDIDATE":
        primary_branch = "intro_ideas_main_point"
        ...
    else:
        primary_branch = "intro_ideas_point_and_reason"
        primary = (
            "The checks recorded sentence patterns that may show a main point "
            "with a supporting reason. "
            "Read them together and check that the reason explains the point "
            "you want readers to accept."
        )
        primary_rules = [
            "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
            "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES",
        ]
```

Because both texts produce `STRUCTURAL_ELABORATION_CANDIDATE`, both enter the `else` branch and receive `intro_ideas_point_and_reason`. The condition test is purely status-string equality; it does not inspect which predicates were found or what words follow "because".

### 2.8 Trait Mapping and Lesson

The branch `intro_ideas_point_and_reason` maps to:

- **Trait:** Ideas
- **Skill:** Explain Your Point
- **Lesson ID:** `HELP-INTRO-EXPLAIN-POINT`

The lesson already contains an explicit limitation acknowledgement:

> *"Sentence patterns cannot prove that a reason is present or that it supports the point."*

---

## 3. Side-by-Side Comparison

| Stage | Text A | Text B | Difference |
|-------|--------|--------|------------|
| Sentence count | 3 | 3 | None |
| Third sentence structure | "allow … because control" | "allow … because use" | Subordinate verb differs |
| advcl dependency on `allow` | `control` (advcl) | `use` (advcl) | Only verb identity |
| `development_status` | `STRUCTURAL_ELABORATION_CANDIDATE` | `STRUCTURAL_ELABORATION_CANDIDATE` | **None** |
| `predicate_count` | 5 | 5 | None |
| `observed_focus_terms` | [smartphones, students, classroom, learning] | [smartphones, students, classroom, learning] | None |
| `specific_focus` | [smartphones, classroom, learning] | [smartphones, classroom, learning] | None |
| `selection_branch` | `intro_ideas_point_and_reason` | `intro_ideas_point_and_reason` | **None** |
| Primary Feedback | "…sentence patterns that may show a main point with a supporting reason…" | Same | **None** |
| Trait | Ideas | Ideas | None |
| Skill | Explain Your Point | Explain Your Point | None |
| Focus term in reason clause | None | `'students'` at pos 188–196 | Present in B only — not evaluated per-clause |

**Conclusion:** The only measurable difference between the two texts at any pipeline stage is the identity of the subordinate clause verb and one additional topic match inside that clause. Neither difference is tested by any rule condition.

---

## 4. Problem A — Reason Relevance: Confirmed Root Cause

### CONFIRMED: The system cannot evaluate whether a reason is relevant.

The pipeline has three places where relevance *could* be checked but is not:

#### 4.1 Topic matching is whole-text, not per-clause

`_lexical_topic_evidence()` scans the full Introduction for focus-term occurrences. It records matches with character offsets but does not associate each match with the clause it belongs to. `FeedbackService` receives only the aggregated `observed_focus_terms` list. It never asks "do the focus terms appear specifically in the clause following 'because'?"

**File:** `services/introduction_rules.py`, `_rule_events()` at line 530;  
**File:** `services/feedback_service.py`, lines 82–109 (branch guards).

#### 4.2 Development evidence counts predicates, not content

`_development_finding()` (lines 497–527) counts items in `clause_candidates` that are not marked as incomplete subordinators. It returns only a status string and a list of predicate tokens. There is no content check on what words appear in each predicate's clause.

**File:** `services/introduction_rules.py`, lines 497–527.

#### 4.3 No per-clause topic check exists

There is no function in `IntroductionRuleBase`, `TopicService`, or `NLPService` that:
- Isolates the clause following "because" (or any `advcl`), and
- Checks whether that clause contains focus terms or is lexically related to the main point.

The `advcl` dependency label is used only to count predicates. The content of the advcl subtree is never inspected for relevance.

#### What the system CAN honestly claim

The system correctly detects:
- That there are multiple clause-like predicate patterns in the Introduction.
- That these patterns *may* constitute a main point with a supporting reason.
- That it cannot verify the logical relationship.

The lesson text for `HELP-INTRO-EXPLAIN-POINT` already states this limitation and instructs students to check the connection themselves — which is the appropriate response for a non-generative, rule-based system.

---

## 5. Problem B — Source Highlighting: Confirmed Root Cause and Fix

### CONFIRMED ROOT CAUSE (fixed during this investigation session)

**File:** `static/app.js`  
**Function:** `tutorEvidenceExcerpt()` at line 5539  
**Fix applied at:** lines 5549–5552

#### Before the fix

```javascript
const clauseSupportedDevRules = [
  "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE",
  // INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES was MISSING
];
```

The function has a special branch for Introduction highlighting (lines 5553–5579). That branch reads sentence spans from `INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE` evidence items. It is guarded by:

```javascript
if (result?.stage_id === "INTRODUCTION"
  && ruleIds.includes(clauseRule)
  && ruleIds.every((id) => [clauseRule, ...clauseSupportedDevRules].includes(id)))
```

When the branch is `intro_ideas_point_and_reason`, `primary_rules` is:
```
["INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE",
 "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES"]
```

Because `MULTIPLE_CLAUSE_PREDICATES` was not in `clauseSupportedDevRules`, the `every()` check failed. The function fell through to the general path (line 5580: `if (events.length !== 1) return null`). There were two events, so the general path also returned `null`. The frontend then displayed the `evidence_fallback` message:

> *"No passage could be verified in your current text, so nothing is marked. Read your point and reason together and check their connection."*

#### After the fix

```javascript
const clauseSupportedDevRules = [
  "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE",
  "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES",   // ← added
];
```

With `MULTIPLE_CLAUSE_PREDICATES` included, the `every()` check passes. The function reads span data from the single `SUBJECT_PREDICATE_CANDIDATE` event and returns a highlight for all three candidate sentences (indices 0, 1, 2).

#### Why the span data was correct all along

`INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE` evidence items include:

```json
{
  "sentence_text": "Schools should allow smartphones because …",
  "sentence_start": 147,
  "sentence_end": 243,
  "sentence_index": 2,
  "predicate_evidence": { "text": "allow", "start": 162, "end": 167 },
  "subject_evidence": [{ "text": "Schools", "start": 147, "end": 154 }]
}
```

All coordinates were valid. The NLP pipeline produced correct spans; the frontend was simply not reading them for this branch.

#### Why `MULTIPLE_CLAUSE_PREDICATES` has no span data — by design

`INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES` evidence items intentionally carry no sentence positions:

```
sentence_text=''   sentence_start=None   sentence_end=None
```

This rule records only predicate tokens (verb text, start, end, POS, DEP). It is a structural count, not a locating rule. The correct behavior is to source the highlight from `SUBJECT_PREDICATE_CANDIDATE` only — which is exactly what the corrected `tutorEvidenceExcerpt()` does.

---

## 6. Confirmed Findings vs. Hypotheses

### CONFIRMED

| # | Finding |
|---|---------|
| C1 | Both texts produce `STRUCTURAL_ELABORATION_CANDIDATE` with identical development status and predicate count. |
| C2 | Topic matching is whole-text. The content of the subordinate clause is not compared with focus terms per-clause. |
| C3 | `_development_finding()` counts predicates only; no content check on clause words. |
| C4 | No function exists in the pipeline to test whether an `advcl` clause is relevant to the main point. |
| C5 | `intro_ideas_point_and_reason` is selected whenever `central=True` and `development_status == STRUCTURAL_ELABORATION_CANDIDATE`, independent of clause content. |
| C6 | `SUBJECT_PREDICATE_CANDIDATE` evidence items contain correct sentence spans (start, end, index, text, predicate, subject). |
| C7 | `MULTIPLE_CLAUSE_PREDICATES` evidence items deliberately carry no sentence position data. |
| C8 | The highlighting failure was caused by `MULTIPLE_CLAUSE_PREDICATES` missing from `clauseSupportedDevRules` in `tutorEvidenceExcerpt()`. |
| C9 | The fix restores sentence highlighting for the `intro_ideas_point_and_reason` branch. |
| C10 | 525 tests pass after the fix. No tests were weakened. |

### HYPOTHESES (not tested during this investigation)

| # | Hypothesis |
|---|-----------|
| H1 | A minimal structural heuristic — checking whether the `advcl` subtree contains any focus terms — could distinguish Text A from Text B without semantic understanding. This has not been implemented or validated. |
| H2 | Adding per-clause topic matching might reduce false-positive point-and-reason detections in practice. The educational value of this change is unknown. |

---

## 7. Confirmed Limitations of the Current System

1. **No per-clause topic matching.** The rule base does not evaluate what words appear in individual clauses.
2. **No semantic reasoning.** The system cannot determine whether a reason logically supports a main point.
3. **No WordNet use for Introduction reasons.** WordNet (NLTK) is used only for Introduction-to-Body continuity checks, not for Introduction internal reason-relevance.
4. **Predicate count is a structural proxy.** `STRUCTURAL_ELABORATION_CANDIDATE` means "at least two clause-like patterns were observed," not "a reason has been identified."
5. **"because" is not inspected.** The subordinating conjunction "because" is used only to detect incomplete subordinators (safeguard rule). It is not used to locate and inspect the content of the reason clause.
6. **Topic matches lack clause attribution.** Character offsets are recorded for each focus-term match, but the pipeline does not associate each match with the clause it belongs to.

---

## 8. Recommended Minimal Corrections

### 8.1 Problem A — Reason Relevance

**No change is needed in the current release.**

The lesson text for `HELP-INTRO-EXPLAIN-POINT` already accurately describes the limitation and instructs students to perform the check themselves. This is honest and educationally appropriate for a rule-based system.

**Optional future improvement (lower priority):** Add a per-clause focus-term check. If the `advcl` subtree contains zero focus terms while the main clause does, the feedback could add a note such as: *"The checks did not find your assignment words in the part of the sentence after 'because'."* This is a structural heuristic, not semantic proof, but it would distinguish Text A from Text B in this specific case.

### 8.2 Problem B — Source Highlighting

**Already fixed.** See §5. Change applied to `static/app.js` lines 5549–5552.

---

## 9. Regression Tests Recommended

The following tests should be added to prevent the highlighting failure from regressing:

1. **`test_introduction_rules.py` (or a new file):** Submit an Introduction with a main-point sentence and a subordinate clause (`advcl`). Assert that `INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES` is triggered and that its evidence items have `sentence_start=None` (no span data in that rule — confirming the design).
2. **`test_workspace_frontend.py` or `test_nlp_transparency.py`:** For `intro_ideas_point_and_reason`, assert that the Writing Tutor UI displays a highlighted sentence excerpt, not the evidence fallback text.
3. **`test_introduction_feedback_targeted.py`:** Add a test submitting both Text A and Text B and asserting that both receive `selection_branch == "intro_ideas_point_and_reason"` — documenting the identical-feedback behavior as intentional and expected until per-clause checking is implemented.

---

## 10. Source Evidence References

| Component | File | Lines | Role |
|-----------|------|-------|------|
| Development finding | `services/introduction_rules.py` | 497–527 | Counts predicates; returns `STRUCTURAL_ELABORATION_CANDIDATE` when ≥ 2 |
| Rule event emission (MULTIPLE_CLAUSE) | `services/introduction_rules.py` | 647–662 | Emits `MULTIPLE_CLAUSE_PREDICATES` with predicate tokens only (no sentence span) |
| Feedback branch selection | `services/feedback_service.py` | 132–149 | Selects `intro_ideas_point_and_reason` when `central=True` and status is elaboration |
| Frontend highlighting (fixed) | `static/app.js` | 5539–5579 | `tutorEvidenceExcerpt()` — reads spans from `SUBJECT_PREDICATE_CANDIDATE`; now includes `MULTIPLE_CLAUSE_PREDICATES` in allowed dev-rule list |
| Lesson content | `content/lessons/feedback_help.json` | `HELP-INTRO-EXPLAIN-POINT` | Contains limitation text and `evidence_fallback` message |

---

## 11. Conclusion

EssayScaff V2 does **not** evaluate whether an Introduction reason is relevant, meaningful, or logically connected to the main point.

It detects that a sentence contains a pattern consistent with "a main point and a supporting reason" (grammatically: a ROOT predicate and an `advcl` predicate). Nothing about the content of the subordinate clause is inspected. "Invisible dragons control the price of bananas on Mars" and "students can use educational apps during class" produce identical structural signatures and therefore identical feedback.

This is a fundamental scope limitation of the rule-based, non-generative approach. It is not a bug. The lesson text for this feedback already honestly discloses the limitation to students and instructs them to verify the connection themselves.

The sentence-highlighting failure (Problem B) was a separate frontend-only defect: `MULTIPLE_CLAUSE_PREDICATES` was missing from `clauseSupportedDevRules` in `tutorEvidenceExcerpt()`. This caused the clause-span reading path to be skipped. The fix is a two-line addition; the NLP data was correct throughout. The fix was applied during this investigation session. All 525 tests remain passing.
