# Student Essay Review Dashboard — Completion Report

Date: 2026-10-26

## Summary

Essay Review is now a student-facing writing dashboard. Selecting the Essay Review stage shows, in order:

1. the assignment topic and submission state;
2. total words, sections with writing, saved revisions, recorded active writing time, and remaining-time status;
3. a per-stage word count / draft status table with an Edit action per stage;
4. the complete essay in Introduction → Body → Conclusion order, preserving wording and paragraph breaks;
5. the existing submission controls;
6. a collapsed entry point to the unchanged NLP Process Explorer.

The technical Inspector is no longer the first thing students see. It remains available through an explicit "Show technical analysis" control, and its rendering and evidence are unchanged.

No NLP rules, writing-quality scoring, completion percentages, database schema, migrations, or real student records were changed. No commit, push, or deploy was performed.

## Files modified

### Application

- `templates/index.html`
  - Rebuilt the Essay Review panel as a dashboard before the technical Inspector.
  - Added the summary grid, progress table with Edit buttons, full-essay preview, submission section, and the technical-analysis toggle.
  - Removed the old duplicate "Word counts by section" statistics block so counts appear once.
  - Added an explicit unsaved-changes note.
- `static/app.js`
  - `renderEssayReview()` now computes live totals and per-stage status from `state.drafts`.
  - Added revision/activity state rendering, unsaved-state distinction, submission badge rendering, and Edit/technical-toggle behavior.
  - `loadWritingActivitySummary()` flushes the existing activity tracker and reads the recorded total without writing.
  - `syncTechnicalInspectorVisibility()` hides the Inspector only during Essay Review unless the student opens it.
  - `updateReviewEditButtons()` disables Edit actions when the essay is submitted, read-only, or temporarily locked.
- `static/style.css`
  - Added dashboard, summary-grid, progress-table, essay-preview, and unsaved-note styles.
  - Added responsive layouts (5/3/2/1 summary columns; compact Edit buttons at ≤520 px).
  - Removed the dead styles for the deleted duplicate statistics block.
- `services/draft_store.py`
  - Added read-only `get_writing_activity_seconds(user_id, assignment_id)`.
  - It verifies classroom enrollment, returns `None` when no records or no `writing_activity` table exist, and raises `AssignmentNotFoundError` for non-enrolled users.
  - It never creates the activity table or writes data.
- `app.py`
  - Added `GET /api/writing-activity` for the current student's own recorded seconds.
  - Classified `read_writing_activity` in the student endpoint authorization set.
  - Existing `POST /api/writing-activity` behavior is unchanged.

### Tests and audit

- `tests/test_workspace_frontend.py`
  - Added `test_essay_review_dashboard_summary_preview_editing_and_submission` covering the dashboard states, unsaved edits, revision/activity counts, Edit navigation, and submission locking.
  - Added structural assertions for dashboard ordering and the absence of the duplicate word-count block.
  - Extended the Node harness with the new elements and read-only activity/revision mocks.
- `tests/test_writing_activity.py`
  - Added coverage for the read-only, enrollment-scoped activity summary and for avoiding schema creation when tracking is disabled.
- `tests/pre_defense_audit.py`
  - Classified the new route and added a valid query plus an outsider ownership-denial probe.
- `docs/essay_review_dashboard_report.md` — this report.
- `docs/essay_review_dashboard_evidence/` — browser verification JSON and screenshots.

## Cause of the layout problem

The old Essay Review view did not have its own dashboard. When the student selected Essay Review, the app only hid the editor and displayed the existing `#essay-review-panel`, while the `#revision-card` and `#nlp-transparency` Inspector remained above or around it in the document. The Inspector was therefore the dominant content on the page even though the student had selected a review stage.

The fix reorders the page so the student dashboard is the primary Essay Review content:

- the dashboard now precedes the Inspector;
- submission controls follow the essay preview;
- `#nlp-transparency` is hidden during Essay Review unless the student explicitly expands it with `#review-toggle-technical`;
- on every other stage the Inspector behaves as before;
- the Inspector's rendering function and NLP output were not modified.

## Calculations and data sources

| Display | Calculation / source |
| --- | --- |
| Total words | Sum of `countWords(state.drafts[stage])` over Introduction, Body, and Conclusion. `countWords` counts whitespace-separated tokens (`\S+`). |
| Per-stage words | The same `countWords` function applied to that stage's live draft text. |
| Sections with writing | Number of stages whose trimmed text is non-empty, displayed as "N of 3". |
| Stage status | "Drafted" when trimmed text is present; otherwise "Not started". This is only a presence indicator, not a quality or completeness judgment. |
| Saved revisions | Existing revision records for the current writing session via `GET /api/revisions`; displayed as a number, "Checking…", or "Unavailable" on error. Opening review does not create a revision. |
| Recorded active writing time | Existing five-second activity buckets via the new read-only `GET /api/writing-activity`. Displayed as a formatted duration when positive, "Not recorded" when no records exist, and "Unavailable" when the request fails. Opening review never writes activity or creates the activity schema. |
| Estimated time remaining | Always "Unavailable". The assignment schema has no word-target field and there is no validated pace model, so no estimate is invented. |
| Submission state | Existing workspace submission record; badge shows "Submitted", "Read-only", or "Not submitted". Submission validation and POST behavior are unchanged. |
| Unsaved state | Existing `isDirty()` comparison between live drafts and the saved snapshot; the preview note appears only when the browser has unsaved changes. |

The essay preview uses the live draft text (`textContent` inside `<pre>` elements), so original wording and paragraph breaks are preserved. Placeholder text is shown only when a stage is empty.

## Verification screenshots

All screenshots are in `docs/essay_review_dashboard_evidence/`.

| File | What it shows |
| --- | --- |
| `essay-review-dashboard-desktop.png` | Full dashboard: 79 words, 3 of 3 sections, 1 revision, 2 min 5 sec recorded time, remaining Unavailable, stage rows 19/42/18, essay preview, submission controls, collapsed technical analysis. |
| `essay-review-dashboard-empty.png` | Empty practice essay: 0 words, 0 of 3, 0 revisions, Not recorded, Unavailable, all stages Not started, practice-mode submission note. |
| `essay-review-dashboard-unsaved-edit.png` | After editing Body and returning to review: total 85, unsaved note visible, revision count still 1, appended sentence present in preview. |
| `essay-review-technical-analysis.png` | Inspector explicitly expanded; technical content unchanged and reachable. |
| `essay-review-mobile-top.png` | 390 × 844 mobile viewport, top of the dashboard. |
| `essay-review-mobile-dashboard.png` | 390 × 844 mobile viewport, progress table and Edit buttons fitting without horizontal page overflow. |

`browser-verification.json` records the DOM values read during the same Chrome run.

## Automated test results

Commands run from the project root with the project virtual environment:

```text
.venv/Scripts/python.exe -m pytest tests/test_workspace_frontend.py
7 passed

.venv/Scripts/python.exe -m pytest tests/test_pre_defense_system.py
3 passed

.venv/Scripts/python.exe -m pytest tests/test_app.py tests/test_writing_activity.py
30 passed

.venv/Scripts/python.exe -m pytest
707 passed in 185.75s
```

The pre-task baseline was 704 passing tests; the three new tests account for the increase.

Additional checks:

```text
node --check static/app.js
.venv/Scripts/python.exe -m py_compile app.py services/draft_store.py
```

Both completed without errors.

## Chrome verification

Verification used a headless Chrome instance against an isolated Flask server on `127.0.0.1:5077` with its own temporary SQLite database (`essay_review_verify.sqlite3`) and dedicated verification accounts. The real database was not used for writes.

### Desktop, seeded assignment

- Total words: **79**
- Sections with writing: **3 of 3**
- Saved revisions: **1**
- Recorded active writing time: **2 min 5 sec**
- Remaining time: **Unavailable** with the no-word-target note
- Submission badge: **Not submitted**
- Stage rows: Introduction **19 / Drafted**, Body **42 / Drafted**, Conclusion **18 / Drafted**
- All three Edit buttons enabled
- Paragraph breaks preserved in the preview
- Duplicate word-count block absent
- Technical Inspector hidden by default; toggle exposes it with `aria-expanded="true"` and label "Hide technical analysis (NLP Process Explorer)"

### Empty assignment

- Total words: **0**
- Sections: **0 of 3**
- Revisions: **0**
- Active time: **Not recorded**
- Remaining: **Unavailable**
- All stages: **Not started**
- Submission badge: **Not submitted**

### Unsaved edit

- Clicking Edit on Body returned to the Body editor with its existing text.
- Adding a sentence and returning to Essay Review changed the total from **79 to 85**.
- The unsaved-changes note became visible.
- Saved revisions remained **1**.
- No save, revision, or analysis request was triggered by opening review.

### Submission

On a second classroom assignment:

- Total words: **27**
- After submitting, the badge changed to **Submitted** and the note became read-only.
- Submission controls were hidden and all Edit buttons were disabled.
- The submission POST still used the existing validated workflow.

### Mobile

At a 390 × 844 viewport:

- The summary stacked correctly.
- The progress table and Edit buttons fit.
- `document.documentElement.scrollWidth` did not exceed the viewport width.
- The Inspector stayed collapsed.

### Real database safety

A read-only inspection of `instance/essay_scaff_drafts.sqlite3` after verification confirmed:

- 27 users and 8 assignments, with no verification accounts (`review_%` matched none);
- no `writing_activity` table, so production time tracking remains disabled/unmigrated;
- the file was not written during verification.

## Scenario coverage

| # | Required scenario | Result |
| --- | --- | --- |
| 1 | Empty essay | 0 words, 0 of 3, 0 revisions, Not recorded, Unavailable; placeholders shown. |
| 2 | Introduction only | Total and Introduction stage update; Body/Conclusion remain "Not started". |
| 3 | Introduction + Body | 2 of 3 and combined total; both stages "Drafted". |
| 4 | All three sections | 3 of 3; all stages "Drafted"; preview shows all three in order. |
| 5 | Editing one section updates total | Body edit changed the displayed total immediately on return to review. |
| 6 | Review preserves unsaved text | Unsaved browser text appeared in preview; note displayed; no automatic save. |
| 7 | Revision counts match persisted records | Count matched `GET /api/revisions`; editing did not increment it. |
| 8 | Missing active time | "Not recorded" with explanatory note and no invented value. |
| 9 | Missing target / insufficient timing | Remaining time "Unavailable" with the no-word-target note. |
| 10 | Edit returns to correct editor | Each Edit action selected its own stage and focused the editor. |
| 11 | Submission behavior preserved | Existing validation and POST used; Submitted state locked editing and hid controls. |
| 12 | Writing Tutor unchanged | No changes to Introduction, Body, or Conclusion feedback rules or the Inspector's NLP content; regression suite passed. |

## Limitations

- Word counts are whitespace-separated token counts. Hyphenated compounds, contractions, and punctuation-only tokens follow the existing `countWords` behavior.
- "Drafted" means only that text is present. It does not imply academic completeness, correctness, or quality.
- Saved revisions are explicit snapshots created with Save Revision. Navigation, analysis, and reviewing are not revisions.
- Recorded active writing time appears only when the existing tracker recorded buckets and the `writing_activity` table exists. This implementation does not migrate the real database or enable production tracking.
- Remaining-time estimates are not available because assignments have no word-target field and there is no validated pace model. The UI deliberately shows "Unavailable" instead of a guess.
- The dashboard reflects the current browser's live drafts. If the browser has unsaved changes, the server-stored draft can differ until the student saves from an editing stage.
- The technical Inspector remains intentionally separate and collapsed; it was not redesigned or simplified.
