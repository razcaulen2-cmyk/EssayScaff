# S5.1 — optional guided learning feedback

> Historical implementation record. The separate help interaction described here
> has been replaced by direct concise guidance. Current behavior and verification:
> [S5.1 refinement](s5_1_direct_feedback.md). The earlier content is preserved for
> research traceability; the Model–Practice–Reflect activity remains separate.

## Initial inspection and baseline

The real student interface already displays **Your Goal**, **What to Check** and
**Your Next Step**; What's Working / Needs Attention are in a native disclosure.
`FeedbackService.generate`, `generate_body`, and `generate_conclusion` select the
existing messages from stage findings and emitted Rule Events. With the existing
`include_transparency_trace=true` student request, the coordinator returns recorded
field branches/conditions and Rule IDs. Flask compacts provenance into field/Rule
ID links, preserving full events separately. `runStageAnalysis` checks request ID,
assignment/input snapshot and stage/view before caching and calling `displayFeedback`.

Introduction progression is an advisory checklist with student confirmations and
existing Continue / Continue Anyway behavior. It is not a new S5.1 readiness gate.

Existing lesson infrastructure is `services/tutoring_lessons.py`, local JSON in
`content/lessons`, and safe DOM helpers in `static/app.js`. The pre-existing
Introduction Model–Practice–Reflect activity has quizzes/reflection and IES/SRSD
metadata. That activity and its completion behavior remain unchanged. S5.1 reuses
the loader module, content directory and DOM helpers for a short **reading mode**,
without adding quizzes, grading or a second NLP/feedback/scaffolding engine.

Baseline: **368 passed**, no failures/skips, 68.13 seconds.

## Implementation and supported branches

The new local `content/lessons/feedback_help.json` has five prepared lessons and
eight exact **Primary Feedback** branch bindings:

| Stage | Recorded branch | Lesson |
|---|---|---|
| Introduction | central_clause_without_multiple_clause_candidate | Making your main point clear |
| Introduction | one_sentence_specific_focus_without_root_candidate | Making your main point clear |
| Introduction | no_root_subject_predicate_candidate | Making your main point clear |
| Introduction | central_clause_with_multiple_clause_candidates | Connecting your point and reason |
| Body | first_paragraph_without_additional_clause_candidate | Developing an idea with detail |
| Body | first_unlinked_adjacent_paragraph_pair | Helping readers follow your paragraphs |
| Conclusion | closure_structure_candidate | Choosing what your conclusion should do |
| Conclusion | synthesis_structure_candidate | Choosing what your conclusion should do |

Each binding supplies a cautious observation appropriate to that branch. Each
lesson supplies beginner definitions, purpose, one/two reflection questions, one
independent revision task and an honest limitation. No lesson contains replacement
essay sentences, student-specific examples, answers, grading or mastery logic.

`load_feedback_help` validates and caches this optional catalog. A missing or
invalid catalog disables help while normal feedback and the older activity remain
available. The student homepage embeds it with Jinja `tojson`; no extra endpoint
or analysis request is added.

`feedbackHelpForResult` performs a deterministic lookup, requiring:

- a successful selected-stage response with a recorded Primary Feedback branch;
- an exact match between the recorded selected message and the returned message;
- a configured stage/field/branch binding;
- nonempty recorded Rule IDs, emitted events without false trigger flags, and
  matching Primary Feedback provenance links.

It never reconstructs feedback priorities or evaluates new writing conditions.
Unknown branches, missing trace, contradictory messages and incomplete provenance
produce no Help Me Understand action. In normal student requests the existing
transparency trace is already requested.

The UI also requires the current cached response to match the displayed feedback
and existing input/assignment/stage/view snapshot guard. It starts closed after
analysis. Clicking **Help Me Understand** opens the compact, scrollable panel;
**Return to Writing** closes it and focuses the editor; Escape closes it and
returns focus to the launcher. Toggling the launcher closes it too. Editing,
changing context/stage or leaving the workspace closes/removes stale content.
Reanalysis does not automatically reopen it.

All dynamic strings use the existing text-node DOM helpers. Help actions do not
change draft text, save state, progression confirmations, existing lesson progress,
analysis objects or feedback. There is no persistence for S5.1 participation.

## Transparency and authorship

The full horizontal technical dashboard remains intact. Feedback Engine → Primary
Feedback includes an expandable prepared-help mapping: lesson ID/title, stage,
field, recorded branch, linked Rule IDs and local content source. Copy Full Analysis
includes that same frontend mapping, explicitly distinguished from backend analysis
decisions. Normal feedback and all technical evidence remain unchanged.

The observation for the point/reason branch does **not** claim that a parser has
identified a validated thesis or reason. It explains that sentence patterns were
found and that their rhetorical/logical relationship was not verified. Similar
cautions distinguish lexical paragraph links and Conclusion wording comparisons
from meaningful coherence or synthesis.

## Verification

Full regression after implementation: **386 passed**, 0 failures/skips, 76.71 s.
Focused implementation checks: **35 passed**, 23.90 s. JavaScript syntax checks
passed. The existing protected Environmental Protection analysis/feedback hash
remains unchanged. Its 27 tokens, 7 events and 14 evaluation records still pass.
After a final beginner-wording polish, the **18 S5.1 tests passed** again in
8.03 s and the real Chrome workflow passed again.

`tests/test_feedback_help.py` uses real isolated Flask API outputs to exercise all
eight mapped branches, plus unmapped `no_focus_match`, punctuation-only and
missing-trace cases. Frontend checks cover all five lesson parts, exact binding
observations, open/close/Escape, cached stage switching, edits/context changes,
literal HTML-shaped feedback rendering, unchanged editor/state/progression,
unchanged request/timer counts and no grading/replacement-writing controls.
The existing Model–Practice–Reflect and draft/revision/submission tests also pass.

The real Chrome runner additionally checks all five concepts, unsupported cases,
return-to-editor focus, desktop/mobile layout, stale content removal, no additional
NLP or storage calls, technical transparency/copy and Teacher Research Inspector.
It creates only synthetic accounts in an isolated temporary database.

Latest actual browser: Chrome 155.0.8059.80, headless, desktop 1440×1000 and mobile
390×844. All five teaching concepts were opened/closed with unchanged editor and
application state, no extra analysis/storage calls and no recorded JavaScript
errors. Isolated storage counts: 0 drafts, 0 revisions, 0 submissions. Screenshots
and `verification.json` are in
`C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-x19lbbjl`;
the help-panel images are `s51-desktop-help.png` and `s51-mobile-help.png`.

Created files: `content/lessons/feedback_help.json`, `tests/test_feedback_help.py`,
and this document. Modified files: `services/tutoring_lessons.py`, `app.py`,
`templates/index.html`, `static/app.js`, `static/style.css`,
`tests/test_workspace_frontend.py`, `tests/test_interface_views.py`, and
`tests/transparency_browser_check.cjs`.

## Research alignment and limitations

The module applies the project's established scaffolding foundation by supplying
optional, manageable support at a verified feedback context. Definitions and
questions implement explanatory, actionable formative feedback. The student makes
the revision decisions and writes every change. Contingency here is limited to
branch-linked content and student-requested help; it is not adaptive mastery
modeling or automatic fading.

The catalog records the user-established Wood/Bruner/Ross (1976), Shute (2008),
van de Pol/Volman/Beishuizen (2010) foundations and McNamara and colleagues (2013)
as related technical research. These references do not validate the local rules
or establish that the software improved learning. That requires educational
review and empirical study with students.

Initial coverage is deliberately limited to the eight Primary Feedback branches.
Within-paragraph connectivity is not given a new detector or invented branch.
Missing trace disables mapped help rather than guessing from message wording.
Content edits require restarting the app because the loader caches the catalog.
Mobile browser verification is emulation, not a physical-device/screen-reader audit.

## S5.2 considerations — not implemented

After user approval, consider evidence-linked highlighting using actual emitted
event offsets, source sections and Python-compatible character positions. Account
for Unicode, stale snapshots and missing spans. A grammatical span must not be
relabeled as a verified thesis/reason or logical support. Review teaching wording
with beginner students and the professor before expanding coverage. No advanced
highlighting, quiz, grading, automatic fading, new score, analytics or NLP detector
was added in S5.1.
