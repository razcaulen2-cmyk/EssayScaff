# Introduction UI Correction Report — Neutral Feedback and Stage Progress Consistency

Follow-up to `docs/introduction_stage_evaluation.md` (Tests 1–3: two PARTIAL, one NLP PASS / UI PARTIAL).
Scope: the two confirmed interface issues only. No NLP rule changes, no thesis/position detection,
no workspace redesign, no stage-navigation changes, no database migrations, no real-database
activity tracking, no changes to real student records, no commit or push.

## 1. Files modified

| File | Change |
|---|---|
| `static/app.js` | Neutral-result presentation for Introduction feedback; NEUTRAL state in Guided Progression |
| `tests/test_introduction_ui_corrections.py` | New regression test covering neutral + corrective + shared Body/Conclusion paths |
| `tests/test_reason_highlighting.py` | Neutral cases now assert the neutral contract instead of corrective display |
| `tests/test_feedback_help.py` | Neutral loop branch: no trait label, neutral guidance keys, neutral focus chip |
| `tests/test_introduction_ideas.py` | Neutral path conditional in tutor/export test; fail-closed expectation for damaged evidence |
| `tests/test_feedback_decision_flow.py` | Neutral Introduction statuses for What's Working / Next Step / Primary Feedback nodes |
| `tests/test_workspace_frontend.py` | Guided expectations updated for the new NEUTRAL state |
| `tests/introduction_ideas_browser_check.cjs` | Chrome check: neutral/corrective contract per recorded branch + Guided/Stage-Progress assertions |
| `tests/transparency_browser_check.cjs` | `verifyInlineGuidance` neutral path; neutral reason spans display no marks |
| `tests/browser_reason_verification.cjs` | Test A/B now verify the neutral presentation |

No backend, template, content-catalog, database-schema or NLP-rule files were modified.

## 2. Root causes

**Issue 1 — Neutral feedback presented as corrective.** The neutral Introduction branches
(`intro_ideas_point_and_reason`, `intro_ideas_review_details`) select a prepared catalog lesson
with purpose `NEUTRAL_REVIEW_TASK`. `selectTutorItems` treated that item like any corrective
lesson, so the tutor rendered the error-location span, "Why it matters", "How to improve", a
6+1 trait label ("Ideas") and a lesson chip — presenting a recorded neutral review as a writing
concern.

**Issue 2 — Unsupported "Review Suggested" for neutral results.** `introductionGuidanceModel`
only distinguished CHECKLIST_COMPLETE vs REVIEW_SUGGESTED once an analysis was current, so a
current *neutral* result produced "Your Introduction may need another look before you continue."
plus a Review Suggestions button, with Continue to Body hidden behind Continue Anyway.

## 3. Behavior before → after

### Neutral feedback (Task 1)

| Aspect | Before | After |
|---|---|---|
| Status chip | "Ideas · Review Your Explanation" (corrective label) | "No specific writing issue detected" |
| Why it matters / How to improve | Displayed from the prepared lesson | Hidden — no unnecessary corrective headings |
| Look at your writing (error location) | Reason clause marked as an error span | Hidden; no marks in editor or tutor |
| Applicable positive observation | Shown | Still shown ("What's working": recorded main-statement + explanation pattern) |
| 6+1 trait concern / lesson | Displayed | Not displayed |
| Transparency Inspector / export | — | Unchanged: recorded decision, `Ideas · Review Your Explanation`, `HELP-INTRO-EXPLAIN-POINT`, exact highlight spans and rationale remain inspectable |
| Genuine concern (e.g. incomplete sentence, topic-connection review) | — | Unchanged: all four sections, marks, Review Suggested |

Neutral detection reuses the validated `selectScaffoldingGuidance` record (never text matching):
if the recorded provenance is damaged or contradictory, the tutor falls back to the original
feedback (`ORIGINAL_FEEDBACK`) instead of inventing a neutral result. The recorded `limitation`
("The mark shows sentence evidence, not an error…") is retained and displayed.

### Guided Progression and Stage Progress (Task 2)

| State | Before | After |
|---|---|---|
| Current neutral analysis | REVIEW_SUGGESTED + "may need another look" + Review Suggestions | NEUTRAL / "No Specific Issue Detected": "The available checks did not identify a specific writing concern. You can continue to Body." — Review Suggestions hidden, **Continue to Body accessible** |
| Stage Progress panel for neutral | Followed the same concern logic (already showed "No Specific Writing Issue Detected" when no concern object existed) | Consistent with the Writing Tutor: NO_ISSUE badge, no Review Writing button, Continue active |
| Genuine concern | REVIEW_SUGGESTED, Review Writing, Continue Anyway | Unchanged |
| Self-checks complete | CHECKLIST_COMPLETE | Unchanged |
| Unanalyzed / stale / edited | Existing freshness checks | Unchanged: editing after analysis withdraws the old result (CHECKING → "Ready to Review Your Writing?") and never presents the old neutral result as current |

No readiness scores, checkboxes or stage locks were added (the two existing student self-checks
are unchanged). No database reads/writes were added; viewing feedback and continuing create no
revisions or persistence requests.

Implementation notes: neutral item flagging happens in `selectTutorItems`
(`item.neutral_result = true`); `studentFeedbackPresentation` returns status
`NEUTRAL_OBSERVATION` with null dimension/skill, guidance limited to "What I noticed" plus any
recorded strength; `renderTutorItem` clears the evidence node and hides the three corrective
sections; `introductionGuidanceModel` adds the NEUTRAL state using the same recorded branch plus
the existing automated-check and freshness conditions.

## 4. Automated test results

- New `tests/test_introduction_ui_corrections.py`: neutral stays neutral (no trait/skill/lesson,
  hidden sections, zero marks, strength retained, Inspector/export records identical to the
  backend `instructional_feedback`), guided NEUTRAL state, stale-on-edit, CHECKLIST_COMPLETE +
  working Continue, no revisions/persistence, shared Body neutral and Conclusion/Introduction
  corrective paths — passing.
- Focused suites (UI corrections, introduction ideas, reason highlighting, feedback help,
  feedback decision flow): **79 passed**.
- Complete Python suite: **702 passed** in 115.34 s (previous baseline 701; the +1 is the new
  regression test). No test was weakened: neutral expectations replaced expectations for the
  old, incorrect corrective display of neutral branches; all corrective-path assertions remain.

## 5. Chrome verification (isolated temporary database)

All runs used real Chrome (headless CDP), an isolated SQLite database, and fictional accounts;
the real `instance/essay_scaff_drafts.sqlite3` and research files were verified unchanged
(protected-file hashes compared before/after), and isolated writing/revision/submission counts
were all 0.

| Check | Result |
|---|---|
| `tests/introduction_ideas_browser_check.py` (13 cases T01–T13, student + teacher) | PASS — `javascriptErrors: []`, protected data unchanged, persistence 0. Neutral cases (T02–T05, T07, T09, T10, T13) show no displayed marks with raw spans retained; corrective cases (T01, T06, T11, T12) keep marks and Review Suggested; guided/Stage-Progress state matches each recorded branch |
| `tests/transparency_browser_check.py` (full regression: 45 transparency sections, clipboard export, layouts, teacher inspector) | PASS — `javascriptErrors: []`, persistence 0 |
| `tests/browser_reason_verification.cjs` (Test A dragon reason, Test B educational-app reason) | PASS — both now `NEUTRAL_OBSERVATION`, no marks, corrective headings hidden, raw span retained in transparency |

Published evidence:

- `docs/screenshots/introduction-ui-correction/` —
  `after-T04-desktop.png` (neutral tutor card), `after-T04-stage-progress.png` (neutral Stage
  Progress + Guided Progression), `after-T04-mobile.png` (neutral mobile layout),
  `after-T01-desktop.png` (corrective tutor card), `after-T01-stage-progress.png` (corrective
  Stage Progress + Guided Progression), `after-student-framework-trace.png` (neutral case: raw
  recorded mapping retained in the Transparency Inspector).
- `docs/introduction_ui_correction_evidence/` — `after-outputs.json` (per-case recorded data:
  status, branch, guidance keys, displayed marks, guided state), `browser.log`,
  `verification-summary.json`, `screenshots.json` (SHA-256 manifest).

Observed in the screenshots: the neutral case shows the "No specific writing issue detected"
chip, "What I noticed" and the recorded strength, the NEUTRAL limitation line, Stage Progress
"No Specific Writing Issue Detected" with an active Continue to Body, and Guided Progression
"No Specific Issue Detected" — while the Transparency Inspector for the same case still lists
`Primary Feedback · Ideas · Review Your Explanation · HELP-INTRO-EXPLAIN-POINT ·
intro_ideas_point_and_reason · NEUTRAL_REVIEW_TASK` with the exact span
[46, 111) "because these devices provide quick access to online dictionaries".

## 6. Remaining Introduction NLP limitations (unchanged, out of scope)

- **No thesis/position detection.** A weak or missing position statement (evaluation Test 1)
  is still not identified as a concern; the branch selects a neutral or generic review instead.
  Deliberately not implemented in this task.
- **Lexical overlap is not relevance.** Topic-word overlap in a because-clause cannot tell
  whether an explanation actually supports the point (the dragon-reason case); the system now
  presents this honestly as a neutral review with the recorded limitation, rather than as a
  corrective finding.
- Neutral branches still depend on surface patterns (main-statement pattern, because-subtree,
  detail sentences); other kinds of development may be missed, as each lesson limitation states.
- No semantic truth or argument-quality assessment of any kind is performed; marks identify
  recorded evidence, not errors.
