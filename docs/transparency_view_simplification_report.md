# Transparency UI simplification — Simple View / Technical View completion report

Date: 2026-10-22

## Location and files

**Transparency Mode** now opens in **Simple View** with five primary groups — **01 Student Text, 02 Language Analysis, 03 Topic Check, 04 Rule Check, 05 Feedback Result** — plus **Advanced Inspector** (the former Flask Backend tab), which is visible only in **Technical View**. A pill toggle (`VIEW: Simple / Technical`) in the transparency header switches between the two presentations. All 45 existing sub-tabs, renderers, evidence panels and export surfaces remain addressable; the change is presentation only.

Files changed in this phase:

- `static/app.js`: `TRANSPARENCY_VIEW_GROUPS` group model, mode state and helpers (`getTransparencyViewMode`, `setTransparencyViewMode`, `ensureTransparencyTechnical`, `applyTransparencyViewMode`), visualizer relocation (`transparencyWalkElements`, `transparencyRecordVisualizerHomes`, `relocateTransparencyVisualizers`), rewritten `createTransparencyTabs` (group tabs + member-keyed sub-tab rows), `renderNlpTransparency` mode wiring, new `renderTransparencySimpleSummaries`, closed-by-default `transparencyExpandableTable`, Process 07 → Feedback Result wording.
- `static/style.css`: mode pill and summary-card components, compact 54px main tabs with matching sticky offsets, borderless nested details, spacing cleanup in sub-panels and explanation grid, `@media (max-width: 760px)` single-column simple summaries.
- `tests/test_workspace_frontend.py`: fake-DOM `Element` extended with `parentNode`, `_attach`, `insertBefore`, `removeChild`, `replaceChildren` cleanup so relocation logic runs in the DOM harness.
- `tests/test_nlp_transparency.py`: scenario updated for six groups / five simple groups / `GROUP_MEMBERS` sub-tab filtering / `mainTabs[5]` keyboard wrap / six sub-tab lists; new permanent test `test_simple_and_technical_view_modes_navigate_without_reanalysis`.
- `tests/transparency_browser_check.cjs`: `GROUP_OF` mapping, counts 8 → 6, `nlp-tab-backend`, `nlp-subtab-concept-occurrences`, and new `verifyTransparencyViewModes()` with four mode screenshots.
- `docs/transparency_view_simplification_report.md`: this report.

## Baseline before edits

- `node --check static/app.js` — passed.
- `& ".venv\Scripts\python.exe" -m pytest -q --tb=short` — **512 passed**.
- `& ".venv\Scripts\python.exe" -B tests\transparency_browser_check.py` — passed, `javascriptErrors: []`.

This phase added exactly one permanent test: **512 → 513 passed**.

## Navigation model

`TRANSPARENCY_VIEW_GROUPS` defines six groups; the first five are the simple-mode tabs:

| Group id | Label | Member sub-tab keys |
| --- | --- | --- |
| `student` | Student Text | `student` |
| `nlp` | Language Analysis | `nlp`, `concept` |
| `topic` | Topic Check | `topic` |
| `rules` | Rule Check | `rules` |
| `engine` | Feedback Result | `engine`, `final` |
| `backend` | Advanced Inspector | `backend` (Technical View only) |

Main tabs render as `#nlp-tab-{group}` with panels `#nlp-panel-{group}`. Each panel contains a summary slot (`[data-summary-slot]`), a member-keyed sub-tab row (`[data-tab-level="sub"]`) and a sub-panel host. Sub-tab and sub-panel ids are unchanged (`nlp-subtab-concept-overview`, `nlp-subpanel-rules-overview`, …), so `HORIZONTAL_TRANSPARENCY_TABS` (45 entries), deep links, evidence buttons and existing tests keep addressing the same elements.

## Simple View (default)

- Exactly five visible main tabs; the Advanced Inspector tab is `hidden`.
- Each group shows a three-card summary — **What happened? / What did the system find? / Why does it matter?** — built by `renderTransparencySimpleSummaries` from the same recorded analysis fields the technical tables read. Nothing is re-derived: missing values render **Unavailable** (verified by the degraded-response probe asserting `Assignment question: Unavailable`).
- Student Text includes the essay excerpt in a `<details>`; Topic Check includes related-word details; Feedback Result shows the five recorded engine fields.
- **View evidence** buttons (`[data-view-evidence]`) switch to Technical View and activate the group's first row/target sub-tab.
- The interactive **Rule Decision Tree** and other visualizer hosts are relocated from their deep technical sub-panels into the simple summary panels, so they remain usable without opening 45 sub-tabs.

## Technical View

- All six main tabs, all 45 sub-tabs, all existing tables and evidence surfaces — unchanged behavior from before this phase.
- Long technical tables start collapsed (`transparencyExpandableTable` now opens with `details.open = false`); `transparencyDisclosure` lazy helpers are untouched.
- Activating **Advanced Inspector** from either view switches to Technical View automatically. Returning to Simple View while the backend group is active falls back to the recorded `transparencyFallbackGroupKey`.
- Deep-link/evidence activation forces Technical View. Keyboard navigation (Home/End/arrows) skips hidden tabs; End in Technical View lands on `nlp-tab-backend`.
- Help text that referenced "Process 07" now reads "Feedback Result → Overview" with a note that the detailed record is under Advanced Inspector (Technical View).

## Visualizer relocation

`relocateTransparencyVisualizers(technical)` walks each visualizer root with `transparencyWalkElements` (visitors must return an element or `null`, not a boolean — a predicate-style visitor was one of two bugs fixed during verification) and moves hosts between their recorded home (`_transparencyHome = {parent, next}` expando, recorded once via `transparencyRecordVisualizerHomes`) and the active view's summary slots. Detection uses `transparencyHasDataMarker`, which checks both `dataset` camelCase keys and raw attributes (e.g. `data-dependency-tree-section`), keeping the logic fake-DOM portable. Relocation runs in both directions and is a pure DOM move: the `View mode switching never reruns analysis` assertions (`__analysisCalls.length` and full `state` JSON equality) pass in both harness and Chrome.

## Design changes

- Main tab height 62 → 54px; sticky sub-tab offsets adjusted 154 → 146 (mobile 174 → 166) to preserve flush stacking (`box-sizing: border-box`).
- Sub-panel padding 17 → 20 (mobile 12 → 15); explanation grid gap/padding loosened; nested `<details>` borderless to reduce border-in-border nesting.
- New pill toggle, summary cards, group-tab and visualizer-host styles; at ≤760px the simple summaries stack single-column with no page-wide horizontal overflow.
- Global `[hidden] { display: none !important; }` handles the Advanced Inspector tab; `#nlp-transparency-content.transparency-mode-simple` hides sub-tab rows/sub-panels with ID specificity over `.student-app` rules. Protected selectors asserted by `test_nlp_transparency.py` (`.analysis-export`, `.transparency-flow-annotations`, `.transparency-explanation-grid`) remain present.

## Test changes

- **`tests/test_nlp_transparency.py`** — scenario now expects six group labels, `GROUP_MEMBERS` filtering (each group only shows its own sub-tabs), six sub-tab lists, `mainTabs[5]` keyboard wrap, and ends with the harness completion marker `Feedback presentation scenarios completed.` New permanent test `test_simple_and_technical_view_modes_navigate_without_reanalysis` covers: structure counts (6 group tabs, 45 sub-tabs, 45 sub-panels), simple default, summary headings and a no-fabricated-values regex, visualizer relocation via `parentNode`, technical round-trip, group navigation against the full `ROWS` map (`student:3, nlp:11, topic:8, rules:7, engine:12, backend:4`), backend fallback to `nlp`, View-evidence activation, re-render persistence (`transparencyLastContext = null`), the Unavailable probe, and `calls`/`original` integrity.
- **`tests/transparency_browser_check.cjs`** — `GROUP_OF` in `selectView`, `mainTabs: 6`, `nlp-tab-backend`, `nlp-subtab-concept-occurrences`, plus `verifyTransparencyViewModes()`: 5 vs 6 visible groups (computed `display` none/block), relocation in both directions, backend → simple fallback, zero analysis reruns and zero state mutation during switching, and the four mode screenshots. Each capture sets explicit device metrics and scrolls by −110/−90/−95px after `scrollIntoView({block:'start'})` so content is not hidden behind the sticky header.
- **`tests/test_workspace_frontend.py`** — additive fake-DOM container methods only; the required completion-marker check (line 1272) is satisfied by the new scenario.
- **`tests/test_nlp_transparency.py` fixture** — `transparency_responses` unchanged; no backend fixtures were touched.

Two verification-stage bugs were fixed in code, not test-relaxed: a `ReferenceError: trace is not defined` in `renderTransparencySimpleSummaries` (now `const trace = data.trace || null`), and walk visitors returning booleans instead of elements.

## Final verification

- `node --check static/app.js` and `node --check tests/transparency_browser_check.cjs` — passed.
- `& ".venv\Scripts\python.exe" -B -m pytest -q -p no:cacheprovider --tb=short` — **513 passed in ~80s**.
- `& ".venv\Scripts\python.exe" -B tests\transparency_browser_check.py` — exit 0 in Chrome **155.0.8059.85**, **50 checks**, `javascriptErrors: []`.
- Recorded check data: `mainTabs: 6`, `subTabs: 45`, `visibleGroupsInSimple: 5`, `technicalGroups: 6`, `subtabs: 45`, `analysisCallsDuringSwitch: 0`.
- Isolated persistence: `persistenceRequests: 0` on every instrumented check (writing sessions, revisions and submissions all zero).
- All 45 sub-tabs remain functional; existing tables, causal/rule-tree, export, clipboard, stale-response, Writing Tutor and protected-fingerprint regressions pass unchanged.

## Screenshots

Final artifact directory:

`C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-d94csacm`

| Evidence | File | Dimensions |
| --- | --- | --- |
| Simple View, desktop | `transparency-simple-desktop.png` | 1440×1000 |
| Simple View, mobile | `transparency-simple-mobile.png` | 390×844 |
| Technical View, desktop | `transparency-technical-desktop.png` | 1440×1000 |
| Technical View, mobile | `transparency-technical-mobile.png` | 390×844 |

The screenshots were visually reviewed: the simple desktop capture shows the pill toggle, exactly five tabs (no Advanced Inspector), three summary cards and the relocated Rule Decision Tree; the technical captures show all six tabs with sub-tab rows; both mobile captures stack cleanly with no horizontal overflow.

## Remaining limitations and protected scope

Mode switching is display-only; computed `display` states and CSS class toggles are verified in Chrome (the fake DOM's `classList.toggle` is a no-op, so harness assertions rely on properties such as `hidden`, `parentNode`, `aria-pressed` and `dataset`). Simple summaries surface only fields the response actually records; absent or compacted evidence stays **Unavailable** rather than being reconstructed. Advanced Inspector content in Simple View is not rendered at all — it is reached only through Technical View, by design.

Only the frontend presentation, its styles, its tests and this report were edited. No changes were made to NLPService/spaCy, TopicService, WordNet, StageEvidence, any Rule Base, FeedbackService, Research Inspector calculations, EssayAnalysisService, lesson mappings, Writing Tutor logic, authentication, database behavior or protected research fingerprints. All 45 sub-tabs, evidence links and export surfaces were preserved. No new features, scoring systems or dependencies were introduced. No commit or push was performed.
