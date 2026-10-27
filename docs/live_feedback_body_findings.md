# Live feedback and the controlled Body-development finding

## Authorized implementation

Writing feedback is requested through the existing `/api/analyze-stage` route
after 1,000 ms without input. A 350 ms typing-indicator idle timer separates
typing from waiting. Analyze Now bypasses the debounce, shares an identical
pending request, or reuses an exact current completed snapshot.

Requests are serialized. An obsolete request is invalidated immediately, but
allowed to settle before another starts: aborting fetch does not cancel Flask's
already-running spaCy work. While it runs, only the latest ready snapshot is
queued. Further edits reset the debounce and remove obsolete queued work.
Generation, editor text, stage, active view, assignment ID/topic/focus and relevant
earlier-stage text must match before a response can be accepted. Returned source
text and retained earlier-section context are also checked when present.

Editing clears feedback/highlights and disables copying the old analysis.
Empty drafts and inactive stages are not submitted. Automatic analysis never
saves, revises, submits, rewrites or advances a stage. A network failure leaves
the essay intact and offers Analyze Now. A current failed request is not retried
in a loop. If an outstanding request is slow, the latest snapshot waits for it
instead of initiating another server execution.

## Exact controlled Body investigation

Inputs are preserved in `tests/body_live_feedback_cases.json`, including the
blank line between the two paragraphs. All cases use actual authenticated
Flask requests with `stage_id: BODY`, the specified smartphone assignment and
the five teacher focus terms.

| Case | Introduction | Paragraph sentence counts | Actual primary branch |
|---|---|---|---|
| A | Empty | 4, 1 | `general_observable_body_evidence` |
| B | Supplied complete Introduction | 4, 1 | `general_observable_body_evidence` |
| C | Supplied Introduction; exact final paragraph alone | 1 | `general_observable_body_evidence` |
| D | Supplied Introduction; two developed paragraphs | 4, 3 | `general_observable_body_evidence` |

In A and B:

- Paragraph 1 has verified offsets `[0, 280)` and four sentence spans.
- Paragraph 2 has verified offsets `[282, 337)` and one sentence span:
  “Second, smartphones can help students practice lessons.”
- Paragraph 1 supplies five subject-linked clause candidates.
- Paragraph 2 supplies **two** candidates in the same sentence:
  - `help`: VERB/VB, ROOT, `[306, 310)`, subject `smartphones`;
  - `practice`: VERB/VB, xcomp, `[320, 328)`, subject `students`.
- Actual event: `BODY.P2.SUPPORTING_DETAIL.CANDIDATE`.
- **No** `BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED` event is emitted.
- The primary decision cites `BODY.P1.PARAGRAPH.SEGMENTED` and
  `BODY.P2.PARAGRAPH.SEGMENTED`.

`BodyRuleBase._supporting_detail_candidates` treats at least two qualifying
clause candidates as structural detail candidates. It does not require those
candidates to occur in separate sentences. The current annotation of
`help students practice` therefore prevents an absence finding. FeedbackService
is not dropping a negative event; it never receives that event for this case.

With no Introduction, continuity is
`NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED`. With the supplied Introduction,
continuity is `LEXICAL_COMPARISON_AVAILABLE`, with actual
`BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON` and
`BODY.INTRO_CONTINUITY.WORDNET_CANDIDATES` events. The earlier context is
processed; it does not change this primary branch or paragraph-development
result. WordNet/TopicService algorithms are not changed by this work.

## Presentation changes that do not invent a finding

The controlled generic result now presents a neutral Body review and useful
evidence:

> Paragraph 1: 4 recorded sentences.
> Paragraph 2: 1 recorded sentence.
> Introduction context was compared with the Body.

It explicitly says that no specific higher-priority concern was selected and
that counts cannot assess support quality. It does not create a Structure tab
or highlight from neutral segmentation alone. The original backend feedback,
events and decisions remain available in Transparency Mode and Copy Full Analysis.

When an existing `BODY.Pn.SUPPORTING_DETAIL.NOT_OBSERVED` event really is
selected or eligible, the prepared **Structure · Supporting Details** lesson
names that paragraph and its observed sentence count. Its original event span
must agree with the paragraph/source before the paragraph-specific observation
and highlight are used. It suggests an example, activity or reason and an
explanation of its relationship to the argument, without assessing semantic
quality or generating a replacement paragraph.

Verified control: replace the final paragraph with
“Second, smartphones support learning.” The existing rule emits
`BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED`; the primary branch is
`first_paragraph_without_additional_clause_candidate`. The original paragraph
span is highlighted purple. This does not imply that all one-sentence
paragraphs lack support.

## Protected-rule proposal — separate approval required, not implemented

The requested missing-additional-sentences concern is **not supported** by the
current controlled-test Rule Events. Do not infer it in JavaScript, relabel the
positive candidate as a problem, or change the existing clause heuristic without
authorization.

A narrow future proposal is an additional deterministic observation such as
`BODY.Pn.DEVELOPMENT.SINGLE_SENTENCE_OBSERVED`, using the existing substantive
paragraph flag, sentence count and original paragraph span. Its evidence would
state that only one sentence was recorded, **not** that the paragraph is
semantically inadequate or contains no useful details. Preserve the original
clause candidates. Any eligibility, FeedbackService priority or research-pin
changes must be reviewed and approved separately before implementation.

Proposed acceptance cases for that future observation:

| Input shape | Proposed observation / boundary |
|---|---|
| Exact two-paragraph controlled Body (4, 1 sentences) | Review observation for Paragraph 2 only |
| Exact final paragraph alone (two clauses, one sentence) | One-sentence review observation; no semantic deficiency claim |
| Two developed paragraphs (4, 3 sentences) | No one-sentence observation |
| One rich sentence containing an example and several clauses | Count may be reported; never assert support is missing |
| Empty or whitespace-only paragraph | No substantive-paragraph finding |
| List-like paragraph | Preserve existing list findings and avoid duplicate coaching |
| Actual `NOT_OBSERVED` detail event already present | Avoid duplicate Supporting Details lessons |
| Changed Introduction, identical Body | Sentence observation unchanged; continuity recalculated normally |

Also evaluate punctuation boundaries, abbreviations, inline newlines, blank-line
segmentation, Unicode offsets, and valid deliberately short paragraphs. Compare
new events, original evidence and protected hashes before any approved re-pin.

## Verification records

Baseline: **479 passed**, before production changes. New tests cover the actual
Body branches, safe paragraph highlights, continuous typing/debounce, manual
bypass, duplicate suppression, one in-flight execution, stale responses,
assignment/context changes, failure recovery, empty drafts and no persistence.
Existing tests were adapted to the newly authorized live-feedback contract;
source-mismatched response fixtures are rejected instead of displayed.

The Chrome regression uses the actual endpoint for automatic Body cases A–D
and the supported control. It also holds a real older response, checks that the
newer request waits, verifies the exact latest copied report, and exercises
network retry, native undo/redo and desktop/mobile highlights. No protected
Rule Base or pin is modified in this phase.

Final verification:

```powershell
& ".venv\Scripts\python.exe" -B -m pytest tests -q -p no:cacheprovider --tb=long
# 485 passed in 61.37s; 0 failed, 0 skipped, 0 errors.

node --check static/app.js
node --check tests/transparency_browser_check.cjs
# Both passed.

& ".venv\Scripts\python.exe" -B tests/transparency_browser_check.py
# Passed; javascriptErrors: []; maximum concurrent live analysis: 1.
```

Chrome screenshots and `verification.json`:
`C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-fym0zqaw`.
The neutral controlled Body summary and the supported Paragraph 2 purple
highlight were visually inspected, including the mobile editor.

Byte comparisons confirmed all 13 monitored protected source/pin files are
unchanged. Fresh authenticated responses for A–D have identical analysis,
Rule Events, original feedback and recorded FeedbackService decisions to the
pre-edit capture. The approved research pin remains unchanged and passes.
Diagnostic evidence and before/after captures:
`C:\Users\My Pc\AppData\Local\Temp\opencode\body-live-feedback-_py7hg1q`.
