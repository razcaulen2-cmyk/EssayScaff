# Conclusion Feedback Correction Report

Date: 2026-10-26
Scope: two confirmed Conclusion feedback inconsistencies — a corrective Writing Tutor that contradicted Stage Progress, and improvement instructions that referred to a highlight that did not exist.
Approach: investigation first, then the smallest verified correction. No new NLP model, no Conclusion rule rewrite, no Introduction/Body rule change, no schema change, no real student data, no commit/push/deploy.

## 1. Reproduction fixture

Assignment: **The School Garden Debate** — *Should schools turn part of their playgrounds into vegetable gardens?*
Focus terms: `schools, playgrounds, vegetable gardens, students, learning`.

The supplied Conclusion was:

> In conclusion, schools should turn a small part of their playgrounds into vegetable gardens. These gardens can help students learn about science by observing how plants grow. Students can also develop responsibility by taking turns watering vegetables and caring for the plants.

Recorded decision for that exact text:

| Field | Recorded value |
|---|---|
| Selection branch | `conclusion_ideas_bring_together` |
| Trait / skill | `Ideas` / `Bring Ideas Together` |
| Supporting rule | `CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE` |
| Primary Feedback | “One sentence combines ideas from more than one earlier section. Read it with those sections and check that it brings the ideas together as you intend.” |
| Needs Attention | Only the limitation: structure/wording checks cannot tell whether an idea is true or the ending works. |
| What's Working | Includes the same synthesis event: “One sentence combines ideas from more than one earlier section. Check whether it brings those ideas together.” |
| Evidence | Three structural candidates. The target candidate has `sentence_span = [0, 92]` and `sentence_text = "In conclusion, schools should turn a small part of their playgrounds into vegetable gardens."` — no top-level `start`/`end` token span. |

## 2. Diagnosis

### Problem A — contradictory classification (not a wrong NLP branch)

The branch is a **neutral/positive review**, not a genuine corrective concern and not an incorrectly selected branch:

- The recorded Primary Feedback asks the student to check an intended connection; it does not assert a defect.
- The same recorded rule event is also listed under What's Working.
- The Needs Attention list contains only the semantic limitation, not a writing problem.
- The synthesis rule itself records “Multiple lexical references in a clause are a synthesis-structure candidate, not proof of synthesis or logical connection.”

The inconsistency came from presentation, not selection. `STAGE_PROGRESS_NEUTRAL_BRANCHES.CONCLUSION` already listed `conclusion_ideas_bring_together`, so Stage Progress correctly reported “No Specific Writing Issue Detected.” The tutor path, however, neutralized only Introduction branches. It therefore rendered the prepared Conclusion lesson as a corrective trait/skill with “Look at your writing,” “Why it matters,” and “How to improve,” producing the contradiction.

### Problem B — highlight instruction without a verified highlight

`buildTutorItem` used the lesson task unconditionally. `HELP-CONCLUSION-BRING-TOGETHER` hard-codes “Read the highlighted sentence…”. The exact synthesis evidence contains only sentence spans, so the shared verifier correctly produced no excerpt and the tutor displayed “No passage could be verified…”. The task still told the student to read a highlighted sentence.

The same latent path applied to:

- a secondary continuity concern that selects the same lesson (`CONCLUSION.CONTINUITY.INTRODUCTION_LEXICAL_COMPARISON` has nested occurrences, no verifiable token span);
- `HELP-BODY-PARAGRAPH-SHAPE`, the only other lesson whose task mentions a highlight.

## 3. Correction

### A. One shared neutral classification

`static/app.js` now uses the existing Stage Progress neutral-branch list for both presentation layers:

- `recordedNeutralSelection` is shared by tutor selection, the presentation model, and transparency.
- When the recorded primary branch is neutral, the tutor item keeps its raw decision, lesson mapping, rule IDs and spans for transparency, but displays no corrective trait/skill.
- `studentFeedbackPresentation` returns `NEUTRAL_OBSERVATION`, null Writing Dimension/Skill, no teaching-content assignment, no evidence location, no improvement task, and only the neutral notice, recorded positive and limitation.
- The recorded What's Working item tied to the same rule is now shown under “What's working” (only when message/provenance counts align). This keeps the useful positive observation visible instead of silently dropping it.
- Stage Progress code was not changed. It already agreed with the backend branch; the tutor now agrees with it.

### B. Evidence-conditional task text

- A task that mentions “highlighted” uses the catalog `task_fallback` when no verified excerpt exists.
- Text is never invented and no highlight is manufactured.
- Added general-guidance fallbacks to `HELP-CONCLUSION-BRING-TOGETHER` and `HELP-BODY-PARAGRAPH-SHAPE`.
- A valid excerpt still displays and marks the verified source text exactly as before.

## 4. Files modified

| File | Change |
|---|---|
| `static/app.js` | `recordedNeutralSelection` / `recordedWorkingObservation` (5439–5459); highlight-conditional task in `buildTutorItem` (5521–5522); recorded Body task fallback (5545); neutral marking and recorded positive (5600–5607); `NEUTRAL_OBSERVATION` presentation (5674–5678); tutor notes and recorded-observation status (2705, 2729, 2735). |
| `content/lessons/feedback_help.json` | `task_fallback` for `HELP-BODY-PARAGRAPH-SHAPE` (line 226) and `HELP-CONCLUSION-BRING-TOGETHER` (line 344). |
| `tests/test_conclusion_feedback_correction.py` | New focused Python + Node VM regression tests (2 tests) covering neutral, corrective, valid-span, no-span, shared-lesson, Stage Progress, Inspector, stale, and Continue behavior. |
| `tests/conclusion_feedback_browser_check.py` / `.cjs` | New isolated actual-Chrome after-correction check for four Conclusion scenarios. |
| `tests/conclusion_feedback_before_check.py` / `.cjs` | New actual-Chrome reproduction of the pre-correction UI. The orchestrator temporarily reverts only the corrected behaviors, then restores `static/app.js` byte-for-byte (SHA-256 verified). |
| `tests/transparency_browser_check.cjs` | Conclusion synthetic case now expects the corrected neutral contract instead of a corrective lesson. |

No Conclusion rule, threshold, evidence extraction, score or selection order was changed.

## 5. Before / after behavior

| Scenario | Recorded branch | Before | After |
|---|---|---|---|
| Exact school-garden Conclusion | `conclusion_ideas_bring_together` | Tutor: “Ideas · Bring Ideas Together”; Look at your writing fallback; Why it matters; How to improve says “Read the highlighted sentence…”; zero marks. Stage Progress: “No Specific Writing Issue Detected.” | Tutor: “No specific writing issue detected”; What I noticed; What's working (same recorded synthesis positive); limitation; no evidence location, Why or How to improve; zero marks. Stage Progress unchanged and now consistent. Continue to Essay Review works. |
| Focus-term list Conclusion | `conclusion_organization_bring_together` | Corrective Organization · Bring Ideas Together with a real highlighted list and general task. | Unchanged corrective behavior; valid list highlight remains marked; task never depends on a missing highlight. Stage Progress “Review Suggested.” |
| New-words Conclusion | `conclusion_ideas_new_words` | Corrective Ideas · Explain New Words; no verified span; general guidance. | Unchanged corrective behavior; no marks; task contains no highlight reference; Stage Progress “Review Suggested.” |
| Secondary continuity selecting Bring Ideas Together | `conclusion_ideas_new_words` primary + continuity secondary | Primary new-words item plus an additional Bring Ideas Together tab whose task referenced a highlight, although the continuity evidence had no verifiable span. | Primary item remains first; the shared lesson is an additional tab and uses its general `task_fallback`; no marks; Stage Progress still reflects the primary branch. |

Recorded messages and the original five backend fields are unchanged; the raw mapping remains in the Transparency Inspector.

## 6. Highlight verification

The shared verifier only accepts source-backed spans. Recorded evidence shapes in these cases:

| Case | Evidence shape | Verified excerpt | Marks |
|---|---|---|---|
| Synthesis candidate | `sentence_text` + `sentence_span` (no `start`/`end`) | None | 0 |
| Keyword-list candidate | top-level `text` + `start`/`end` | Yes | List text marked in tutor and editor |
| New-material observation | nested `conclusion_occurrences` | None | 0 |
| Continuity comparison | nested `matching_occurrences` | None | 0 |

Chrome confirmed after the fix:

- exact neutral: 0 editor marks, 0 tutor marks, no “how to improve” section, no highlight wording;
- keyword list: one verified list passage marked in both tutor evidence and editor;
- new words: 0 marks, general guidance;
- secondary shared lesson: 0 marks, fallback guidance;
- editing after analysis hides stale feedback, clears marks, and returns Stage Progress to “Ready to Review Your Writing?”.

## 7. Regression results

- Baseline before this work: **702 passed**.
- Focused new tests: **2 passed** (`tests/test_conclusion_feedback_correction.py`).
- Affected group (new tests + feedback-help + decision-flow + Introduction UI corrections): **40 passed**.
- Complete Python suite with final code: **704 passed in 144.63s** (702 baseline + 2 new regression tests).
- JavaScript syntax: `node --check` passed for `static/app.js`, `static/nlp_process_explorer.js`, and the new browser scripts.
- Lesson JSON parses and validates through the existing loader tests.
- Existing Introduction and Body neutral/corrective tests are included in the full suite and passed unchanged.

## 8. Chrome verification (isolated temporary database)

Both runs used real Chrome via CDP, a fresh SQLite database, a fictional student account, and no installed test packages.

- Pre-correction reproduction: temporarily reverted only the three corrected behaviors (Conclusion neutral marking, conditional highlight task, recorded-positive display). Captured the actual contradiction: corrective tutor + “Read the highlighted sentence…” with zero marks, while Stage Progress reported no issue.
- After correction: all four Conclusion scenarios passed, including tab ordering, Stage Progress agreement, Inspector retention and Continue navigation.
- No JavaScript exceptions were recorded in either run.
- Protected database/research/static files were hash-checked; `static/app.js` was restored to its original SHA-256 after the before run.
- Isolated persistence counts stayed at zero for `writing_sessions`, `writing_revisions`, and `submissions`.

Evidence:

- `docs/screenshots/conclusion-feedback-correction/` — before and after tutor, Stage Progress, Essay Review, and valid-highlight screenshots.
- `docs/conclusion_feedback_correction_evidence/` — `before-outputs.json`, `after-outputs.json`, browser logs, and verification summaries.

Note: the broad `tests/transparency_browser_check.py` was also attempted. It stops before the Conclusion section at a pre-existing stale assertion: it expects 8 Introduction rule events, while the current app records 9 because of the paused `INTRO.POSITION.CHECK_NOT_APPLICABLE` rule. That failure is unrelated to this correction and was not “fixed” by changing the expected count. Its Conclusion expectation was updated for the new neutral contract; the dedicated Conclusion Chrome check independently verifies the complete contract.

## 9. Remaining Conclusion limitations

- All comparisons are lexical/form-based. Synonyms and reworded ideas can be missed; absence of a match is not evidence of absence.
- A synthesis candidate means a clause-bearing sentence contains at least two normalized concept lemmas also found in earlier sections. It is a structural signal, not proof of logical synthesis.
- The keyword-list check is structural; a fragment or list can be a draft or stylistic choice.
- The new-material check compares normalized word forms; it cannot judge whether an idea was genuinely introduced earlier.
- Continuity checks compare word forms between sections; they cannot validate the logical relationship.
- The system does not judge whether an ending is effective, whether an idea is true, or whether the essay is good. It does not rewrite student text.
- Conclusion has no stage-specific instructional trace. Tutor content comes from prepared catalog bindings; the recorded positive is matched from What's Working by rule provenance.
- `conclusion_neutral_general` has no prepared lesson binding, so the tutor can fall back to a general review (without a trait) while Stage Progress reports neutral. It does not invent a specific concern.
- Stage Progress reflects the primary branch. Independently supported Needs Attention lessons can still appear as additional tutor tabs.
- A highlight is shown only when source spans verify exactly; missing highlighting does not mean a concern is absent.

## 10. Explicit non-actions

No Conclusion algorithm, Introduction/Body rule, database schema, writing-time tracking, Adaptive Scaffolding, real student record, commit, push, or deployment was changed.
