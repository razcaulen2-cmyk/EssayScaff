# Body-stage feedback inspection against the 6+1 Trait Model (Ideas and Organization)

Read-only inspection. No production code, tests, messages, thresholds, fixtures, or
configs were changed by this work. The only artifacts created are this report and a
temporary probe script under `C:\Users\MYPC~1\AppData\Local\Temp\opencode\`
(`body_traits_probe.py`). No commits were made.

Scope: the Body stage only, mapped against two traits of the 6+1 Trait® Model —
**Ideas** and **Organization**. Voice, Word Choice, Sentence Fluency, Conventions and
Presentation are out of scope for this report.

---

## 1. Current Body architecture

### 1.1 Request path

- `/api/analyze-stage` (authenticated Flask route in `app.py`) receives
  `stage_id: BODY`, assignment topic, focus terms, and any earlier-stage text, then
  calls `EssayAnalysisService.analyze` (`services/essay_analysis_service.py:31`).
- `EssayAnalysisService.analyze` prepares the teacher context once
  (`TopicService.prepare_teacher_context`), parses each supplied section exactly once
  via `TopicService.analyze` (spaCy; `include_wordnet=True` only for CONCLUSION), then
  runs the stage Rule Base on those prepared outputs
  (`essay_analysis_service.py:57–91`).
- For BODY: `BodyRuleBase.analyze` (`services/body_rules.py:38`) →
  `FeedbackService.generate_body` (`essay_analysis_service.py:137`) → the trace object
  `_Research Decision Trace` is popped and stored as
  `research_trace.stages.BODY.feedback_decisions` (`essay_analysis_service.py:140–142`,
  `:238`), and `research_inspector.build_rule_evaluation_trace` builds the rule-tree
  view (`essay_analysis_service.py:211`).

### 1.2 BodyRuleBase — observation layer (`services/body_rules.py`, 859 lines)

- Paragraphs are blank-line spans via the shared `split_paragraph_spans`
  (`stage_evidence.py:7`); boundary policy recorded at `body_rules.py:108–111`.
  All paragraph features are span-filtered views of the single full-text parse — no
  re-parsing (`body_rules.py:54–55`).
- Per-paragraph features (`_analyze_paragraph`, `body_rules.py:157–279`):
  - **Clause candidates**: finite `VERB/AUX` with tags `VB/VBD/VBP/VBZ` and a
    dependency-linked subject, restricted to dependencies
    `ROOT/conj/advcl/ccomp/xcomp/relcl`
    (`body_rules.py:20–23`; `stage_evidence.clause_candidates_from_sentences`,
    `stage_evidence.py:63–111`).
  - **Supporting details**: `details = clause_candidates if len(clause_candidates) >= 2
    else []` (`body_rules.py:402`) — a paragraph-level count of at least two clause
    candidates; candidates need **not** be in separate sentences. Status
    `STRUCTURAL_DETAIL_CANDIDATES_OBSERVED` / `NO_STRUCTURAL_DETAIL_CANDIDATE`.
  - **Topic-sentence candidates**: a clause candidate in a sentence that also has a
    configured focus-term match or a concept recurring across the paragraph's
    sentences (`body_rules.py:338–396`).
  - **Fragment/list**: `fragmentary` = tokens present but no clause candidate;
    `keyword_list_candidate` = fragmentary AND (≥3 sentences OR ≥4 noun/proper-noun
    tokens) (`body_rules.py:183–186`).
  - **Unity**: adjacent-sentence pairs compared on content-word surfaces and lemmas
    (`body_rules.py:414–459`), status `LEXICAL_CONTINUITY_CANDIDATE` or
    `NO_SHARED_NORMALIZED_CONTENT_TERM_OBSERVED`.
  - **Repetition**: surfaces, lemmas, two-word openings (`stage_evidence.py:114–161`),
    with the standing interpretation "Repetition can maintain continuity and is not
    automatically harmful."
  - **Example/explanation markers**: regex over `for example / for instance / such as
    / including` (`body_rules.py:29`, `:466–480`).
- Cross-paragraph continuity (`body_rules.py:482–531`): for each adjacent pair,
  shared content lemmas plus listed transition expressions (`TRANSITION_EXPRESSIONS`,
  `body_rules.py:24–28`); status `LEXICAL_OR_TRANSITION_CANDIDATE` or
  `NO_EXPLICIT_LEXICAL_LINK_OBSERVED`.
- Introduction→Body continuity (`body_rules.py:557–609`): direct/lemma concept
  comparison via `stage_evidence.compare_stage_concepts` plus WordNet single-synset
  candidates (`stage_evidence.py:164–346`); absent when no Introduction is supplied.
- **Rule Events** are emitted centrally in `_rule_events`
  (`body_rules.py:650–816`) with an explicit `triggering_condition`,
  `actual_evidence`, `evidence_type`, `limitations`, `triggered: True` — the complete
  inventory is in section 2.3 below.
- The analysis object also records `uncertainty` and `prohibited_conclusions`
  (`body_rules.py:136–149`) — unconditional stage-scope statements, never decisions.

### 1.3 FeedbackService — selection layer (`services/feedback_service.py`, 804 lines)

- `_emitted_events` keeps only events with `triggered !== false && fired !== false`
  (`feedback_service.py:13–17`); `_emitted_rule_ids` drops any branch link whose event
  was not emitted, so provenance never cites an unobserved event (`:20–22`).
- `generate_body` (`:534–804`) builds the five student-facing fields, then
  `Feedback Provenance` (one record per cited event per field, `:743–763`) and the
  `interpretation_limit` (`:771–773`).
- With `include_trace=True`, each field records
  `{selection_branch, selection_condition, rule_ids, selected_message|
  selected_message_count, limitation?}` plus a fixed `priority_order`
  (`:793–803`); `unselected_alternatives` is explicitly "FeedbackService does not
  record a ranked list of unselected alternatives" (`:802`).
- The trace is produced in-process by `EssayAnalysisService` and re-serialized into
  `research_trace`; Process 06 (rule trees) and Process 07 (feedback decision flow)
  render it read-only in the UI (`static/app.js` — `buildFeedbackDecisionFlow`
  `:2695`, `renderFeedbackDecisionFlow` `:3069`).

### 1.4 Presentation layer (`static/app.js`, `content/lessons/feedback_help.json`)

- `studentFeedbackPresentation` → `selectTutorItems` → `buildTutorItem`
  (`app.js:5300–5401`) turns recorded branches + cited events into Writing Tutor
  items with roles `PREPARED` / `NEUTRAL_REVIEW` / `GENERAL_REVIEW` (`:5387`).
- Prepared lessons and their branch bindings live in
  `content/lessons/feedback_help.json`, loaded and validated by
  `services/tutoring_lessons.py:load_feedback_help` (`:127–139`); bindings are keyed
  by `(stage_id, feedback_field, selection_branch)` for Primary Feedback and by
  `(stage_id, rule_id_pattern)` for secondary Needs Attention bindings; the only
  allowed `dimension` values are `Clarity`, `Coherence`, `Structure` (`:99`).
- Field-level tutor statuses (`app.js:2796–2830`): Primary → `PREPARED_LESSON` /
  `NEUTRAL_REVIEW` / `GENERAL_REVIEW`; Needs Attention → `SECONDARY_LESSONS` /
  `NO_SECONDARY_LESSON`; What's Working → `LIST_DISPLAY_ONLY`; Current Goal →
  `NOT_MAPPED`; Next Step → `NEXT_STEP_DISPLAY`.
- For `general_observable_body_evidence` specifically, `tutorBodyOverview`
  (`app.js:5275–5298`) builds a **neutral paragraph/sentence-count review** when the
  branch, message and verified spans all line up; `excerpt` is deliberately `null`
  ("Segmentation is neutral evidence, not a diagnosed problem", `:5375`).

---

## 2. Complete Body branch inventory

### 2.1 Primary Feedback — priority chain (`feedback_service.py:546–628`, trace `:776–783`, `:801`)

| # | Branch | Recorded condition | Cited event(s) | Message essence |
|---|--------|--------------------|----------------|-----------------|
| 1 | `no_substantive_paragraph` | no substantive paragraph exists | `BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH` | Body has no words yet; write your first paragraph |
| 2 | `first_list_like_paragraph` | first substantive paragraph with `keyword_list_candidate` true | `BODY.Pn.PARAGRAPH.KEYWORD_LIST_CANDIDATE` | no sentence connecting the assignment words in Paragraph n |
| 3 | `first_unlinked_adjacent_paragraph_pair` | first pair with `NO_EXPLICIT_LEXICAL_LINK_OBSERVED` | `BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON` | no shared key words/transitions between Paragraphs i and j |
| 4 | `first_paragraph_without_additional_clause_candidate` | first sentence-bearing substantive paragraph with no detail candidates | `BODY.Pn.SUPPORTING_DETAIL.NOT_OBSERVED` | did not find another sentence part to develop the idea in Paragraph n |
| 5 | `first_repeated_sentence_opening` | first substantive paragraph with `repeated_sentence_openings` | `BODY.Pn.REPETITION.REPEATED_SENTENCE_OPENINGS` | more than one sentence in Paragraph n starts with '…' |
| 6 | `general_observable_body_evidence` | none of the higher-priority conditions applies | `BODY.Pn.PARAGRAPH.SEGMENTED` (every substantive paragraph) | checks found sentences and words; read each paragraph and check it explains your point |

### 2.2 Next Step — priority chain (`feedback_service.py:704–736`, trace `:784–792`)

Same first five branches as Primary, plus:

- `introduction_context_unavailable` — Introduction continuity status is
  `NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED`; **no Rule Event** (availability condition,
  `rule_ids: []`, noted in the trace limitation at `:799`).
- `general_body_review` — fallback, cites `BODY.GOAL.DEVELOP_BODY_IDEAS`.

### 2.3 What's Working / Needs Attention / Current Goal

- **Current Goal** — `stage_constant`: `BODY.GOAL.DEVELOP_BODY_IDEAS`
  ("Use each Body paragraph to explain one idea. Add details and show how the
  paragraphs connect.", `feedback_service.py:542`).
- **What's Working** — `paragraph_evidence_loop` (`:630–660`), per substantive
  paragraph, appended only when evidence exists: focus terms observed
  (`FOCUS_TERMS_OBSERVED`), topic-sentence candidate (`TOPIC_SENTENCE.CANDIDATE`),
  detail candidates (`SUPPORTING_DETAIL.CANDIDATE`), repeated surface word
  (`REPETITION.REPEATED_SURFACE_CONTENT_WORDS`); plus one cross-stage item when
  Introduction overlap exists (`BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON`, `:689–694`).
- **Needs Attention** — `paragraph_and_cross_stage_checks` (`:662–702`), appended only
  when the negative condition is recorded: keyword-list paragraph
  (`KEYWORD_LIST_CANDIDATE`), no focus terms in paragraph
  (`FOCUS_TERMS_NOT_OBSERVED`), no detail candidates (`SUPPORTING_DETAIL.NOT_OBSERVED`),
  any unlinked pair (`ADJACENT_PARAGRAPH_COMPARISON` when pair status is
  `NO_EXPLICIT_LEXICAL_LINK_OBSERVED`), no Introduction overlap with unobserved
  concepts (`INTRO_CONTINUITY.LEXICAL_COMPARISON`), and — always —
  `BODY.LIMITATION.NO_SEMANTIC_VALIDATION` ("These checks cannot tell whether ideas
  are true or whether they make sense together.", `:701–702`).

### 2.4 Rule Event inventory (`_rule_events`, `body_rules.py:650–816`)

Emitted per paragraph `Pn`:

| Event | Emission condition | Line |
|---|---|---|
| `BODY.Pn.PARAGRAPH.SEGMENTED` | always (each nonblank line group) | `:673` |
| `BODY.Pn.PARAGRAPH.KEYWORD_LIST_CANDIDATE` | `keyword_list_candidate` true | `:680` |
| `BODY.Pn.PARAGRAPH.FOCUS_TERMS_OBSERVED` / `FOCUS_TERMS_NOT_OBSERVED` | exactly one of the two always | `:688` / `:697` |
| `BODY.Pn.TOPIC_SENTENCE.CANDIDATE` / `NO_CANDIDATE` | exactly one of the two always | `:704` / `:712` |
| `BODY.Pn.SUPPORTING_DETAIL.CANDIDATE` / `NOT_OBSERVED` | ≥2 clause candidates in paragraph / none | `:720` / `:729` |
| `BODY.Pn.EXAMPLE_OR_EXPLANATION_MARKER` | marker regex matches in paragraph span | `:736` |
| `BODY.Pn.UNITY.SENTENCE_PAIR_i_j` | each adjacent sentence pair | `:744` |
| `BODY.Pn.REPETITION.REPEATED_SURFACE_CONTENT_WORDS` / `…_NORMALIZED_CONTENT_TERMS` / `…_SENTENCE_OPENINGS` | repeated observation present | `:752` |

Emitted body-wide:

| Event | Condition | Line |
|---|---|---|
| `BODY.TOPIC.NO_FOCUS_MATCH` | focus list exists but none observed in Body | `:767` |
| `BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH` | no substantive paragraph | `:769` |
| `BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON` | ≥2 substantive paragraphs exist (a *comparison was performed*; the absence detail lives in each pair's `status`) | `:778` |
| `BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON` | Introduction supplied and compared | `:786` |
| `BODY.INTRO_CONTINUITY.WORDNET_CANDIDATES` | at least one single-synset candidate | `:794` |
| `BODY.GOAL.DEVELOP_BODY_IDEAS` | always (stage scope) | `:802` |
| `BODY.LIMITATION.NO_SEMANTIC_VALIDATION` | always (system scope) | `:809` |

Absence events (`FOCUS_TERMS_NOT_OBSERVED`, `TOPIC_SENTENCE.NO_CANDIDATE`,
`SUPPORTING_DETAIL.NOT_OBSERVED`) are themselves **emitted events with
`triggered: True`** — they are the recorded evidence a branch cites.

### 2.5 Lesson bindings and tutor statuses for Body (`content/lessons/feedback_help.json`)

Primary Feedback bindings:

| Branch | Lesson | Dimension · Skill |
|---|---|---|
| `first_paragraph_without_additional_clause_candidate` | `HELP-SUPPORTING-DETAIL` | Structure · Supporting Details |
| `first_repeated_sentence_openings` | `HELP-REPEATED-OPENINGS` | Structure · Repeated Openings |
| `first_unlinked_adjacent_paragraph_pair` | `HELP-CONNECTING-IDEAS` | Coherence · Paragraph Connection |

**No Primary binding exists** for `no_substantive_paragraph`,
`first_list_like_paragraph`, or `general_observable_body_evidence`.

Secondary (Needs Attention) rule-pattern bindings for BODY:
`Pn.PARAGRAPH.FOCUS_TERMS_NOT_OBSERVED` → `HELP-TOPIC-VOCABULARY` (Coherence);
`Pn.SUPPORTING_DETAIL.NOT_OBSERVED` → `HELP-SUPPORTING-DETAIL` (Structure);
`CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON` and `INTRO_CONTINUITY.LEXICAL_COMPARISON`
→ `HELP-CONNECTING-IDEAS` (Coherence).

Resulting statuses: bound branch → `PREPARED_LESSON` with highlight; the general
branch → `NEUTRAL_REVIEW` with count summaries and no excerpt (`app.js:5275–5298`,
asserted by `tests/test_causal_transparency.py:160–163`); Needs Attention citing only
the limitation → `NO_SECONDARY_LESSON`; What's Working → `LIST_DISPLAY_ONLY`.

---

## 3. Mapping to the 6+1 Trait Model — Ideas and Organization

Trait principles below are written in original paraphrase from the 6+1 Trait® Model
framework published by Education Northwest (K–2 and 3–12 rubrics; see section 8).
No rubric wording, band descriptors, or official scores are reproduced.

- **Ideas (principle, paraphrased)**: the piece is focused on one clear central
  message, and that message is developed with relevant, sufficient details that help
  the reader understand it — detail earns its place by extending the idea, and
  off-focus material is left out.
- **Organization (principle, paraphrased)**: the writing has an internal structure
  the reader can follow — ideas are grouped into paragraphs, each paragraph has its
  own shape and an order that progresses logically, and the parts are connected so
  the reader can see how one idea leads to the next.

### 3.1 Ideas coverage in the Body stage

| System element | Trait relevance | Kind of signal | Coverage caveat |
|---|---|---|---|
| `BODY.GOAL.DEVELOP_BODY_IDEAS` (Current Goal) | focus + develop the central idea | constant, not evidence | always the same text; no per-essay condition |
| `FOCUS_TERMS_OBSERVED` / `NOT_OBSERVED` (per paragraph) | staying with the assignment's idea | lexical direct/lemma match | paraphrases invisible; teacher/auto focus list only |
| `TOPIC_SENTENCE.CANDIDATE` / `NO_CANDIDATE` | a paragraph's controlling idea | clause + focus/recurring-concept heuristic | rhetorical role not confirmed |
| `SUPPORTING_DETAIL.CANDIDATE` / `NOT_OBSERVED` | developing the idea with detail | ≥2 clause candidates in the paragraph | structural count only; sentence-count and clause-count ≠ useful support |
| `EXAMPLE_OR_EXPLANATION_MARKER` | example/explanation detail | direct expression spans | **recorded but never surfaced in any feedback field** (see 3.3) |
| `HELP-SUPPORTING-DETAIL` lesson | adding a reason/example/explanation | prepared instruction | only reachable when `NOT_OBSERVED` is emitted |

### 3.2 Organization coverage in the Body stage

| System element | Trait relevance | Kind of signal | Coverage caveat |
|---|---|---|---|
| `PARAGRAPH.SEGMENTED` + boundary policy | paragraphing | blank-line boundaries | boundaries ≠ rhetorical paragraphing |
| `KEYWORD_LIST_CANDIDATE` | paragraph not shaped as statements | fragment + sentence/noun thresholds | deliberate fragments/notes can flag |
| `UNITY.SENTENCE_PAIR_i_j` | within-paragraph connection between sentences | shared surfaces/lemmas | **recorded but never surfaced** (see 3.3) |
| `CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON` pair statuses | connections between paragraphs | shared lemmas + listed transitions | only the *absence* status is ever cited; the linked-pair event is never cited as working evidence |
| `REPETITION.REPEATED_SENTENCE_OPENINGS` | sentence flow inside a paragraph | two-word openings | has a full branch + lesson; neutral by design |
| `INTRO_CONTINUITY.LEXICAL_COMPARISON` | cross-section connection | concept overlap | presence → Working item; absence → Needs item; never a progression judgment |
| `WORDNET_CANDIDATES` | cross-section connection (alternative wording) | single-synset candidates | informational only; **never cited by any field** (by design) |

### 3.3 Evidence that exists but reaches no field

Confirmed by both probe runs and the Phase 2 browser run: the following emitted
events appear in no `Feedback Provenance` record and in no field's `rule_ids`:
`BODY.Pn.EXAMPLE_OR_EXPLANATION_MARKER`, `BODY.Pn.UNITY.SENTENCE_PAIR_i_j`,
`BODY.Pn.REPETITION.REPEATED_NORMALIZED_CONTENT_TERMS`,
`BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON` **when the pair is linked**,
`BODY.INTRO_CONTINUITY.WORDNET_CANDIDATES`. They are visible as "NOT CITED" in the
Process 07 decision flow. This is not an error — branches simply never reference them
— but it means the strongest positive Ideas signal the system records (an explicit
example marker) and the strongest positive Organization signals (sentence-to-sentence
unity, a linked paragraph pair) never reach the student.

Note: the system's internal instructional dimensions are `Clarity / Coherence /
Structure`, not the 6+1 trait names; the mapping above is conceptual, and the 6+1
trait labels do not appear anywhere in the product today.

---

## 4. Investigating `body_generic` (why there is no Paragraph-2 highlight)

Confirmed findings (verified by running the actual backend workflow on the corpus
case `body_generic` from `tests/causal_transparency_cases.json`):

**Q1 — What condition selects `body_generic`?**
The Primary Feedback fallback `general_observable_body_evidence` is selected when none
of the five higher-priority conditions applies (`feedback_service.py:546–628`). For
this case, each recorded fact is: no substantive-paragraph problem (2 substantive
paragraphs); no list-like paragraph (`keyword_list_candidate` false both — P1 has
clause candidates, P2 has clause candidates); the adjacent pair status is
`LEXICAL_OR_TRANSITION_CANDIDATE` (shared lemmas "smartphone, student, help" plus the
transition "second"), so no unlinked pair; both paragraphs have detail candidates
(P1: 5, P2: 2), so no `NOT_OBSERVED` paragraph; no repeated sentence openings.

**Q2 — What actual Body evidence existed?**
18 triggered events with the Introduction supplied (17 without): per paragraph
`SEGMENTED`, `FOCUS_TERMS_OBSERVED`, `TOPIC_SENTENCE.CANDIDATE`,
`SUPPORTING_DETAIL.CANDIDATE`; for P1 additionally
`EXAMPLE_OR_EXPLANATION_MARKER` ("For example"), `UNITY.SENTENCE_PAIR_1_2/2_3/3_4`,
`REPETITION.REPEATED_SURFACE_CONTENT_WORDS` ("students" ×3) and
`…_REPEATED_NORMALIZED_CONTENT_TERMS`; body-wide `CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON`,
`INTRO_CONTINUITY.LEXICAL_COMPARISON`, `GOAL.DEVELOP_BODY_IDEAS`,
`LIMITATION.NO_SEMANTIC_VALIDATION`. Paragraph counts P1 = 4 sentences / 5 clause
candidates, P2 = 1 sentence / 2 clause candidates (`help` ROOT, `practice` xcomp —
both inside the single sentence). Feedback: Primary cites `P1`+`P2.SEGMENTED`;
What's Working carries 8 items (9 with the Introduction link); Needs Attention carries
only `BODY.LIMITATION.NO_SEMANTIC_VALIDATION`; Next Step `general_body_review`.

**Q3 — Did the Rule Base emit paragraph-specific findings?**
Yes — paragraph-specific **positive** findings exist for both paragraphs (listed
above). What is *not* emitted for P2 is any paragraph-specific **absence/concern**:
no `P2.SUPPORTING_DETAIL.NOT_OBSERVED`, no `P2.PARAGRAPH.FOCUS_TERMS_NOT_OBSERVED`,
no `P2.TOPIC_SENTENCE.NO_CANDIDATE`. Paragraph-specific *negative* evidence is
therefore unavailable for P2, not suppressed.

**Q4 — Were the emitted findings available to FeedbackService?**
Yes. `generate_body` receives the same analysis object; `_emitted_events` keeps all 18
(all `triggered: True`). SEGMENTED and focus/detail/topic/repetition items are cited
(Primary/Working). The uncited set (section 3.3) is available in the dictionary but
never referenced by any branch condition, so it cannot enter provenance.

**Q5 — Why was the generic message chosen?**
The Primary chain fell through five checks to the fallback (Q1 facts), citing only the
per-paragraph segmentation events. Needs Attention is an independent append loop: its
paragraph checks (list, focus-absence, detail-absence) and its cross checks (unlinked
pair, missing Introduction overlap) all evaluated false, leaving the always-on
limitation message. Nothing was dropped — the selection is exactly the recorded
conditions.

**Q6 — Missing span/provenance/priority, or genuinely no supported concern?**
Confirmed: **genuinely no supported paragraph-specific concern under the existing
rules.** Supporting facts: (a) `_supporting_detail_candidates` counts clause candidates
anywhere in the paragraph (`len(clause_candidates) >= 2`, `body_rules.py:402`), so P2's
one sentence with two clause candidates passes the development heuristic — documented
independently in `docs/live_feedback_body_findings.md:45–57`; (b) provenance is
complete for every cited field (no missing records in either probe run); (c) priority
is recorded and honest (`priority_order` in the trace, rendered by Process 07); (d) the
tutor's missing highlight follows from the *absence of an eligible negative event* —
`tutorBodyOverview` runs only because the branch is general, and its excerpt is
deliberately `null` (`app.js:5375`), asserted by
`tests/test_causal_transparency.py:160–163`. So the transparency layer is working; the
gap is detection granularity, not span/provenance/priority bookkeeping.

Hypotheses (plausible, **not verified** — do not treat as findings):

- H1: a single rich sentence containing several clause candidates would be credited as
  "developed" even if a teacher would call it thin — the ≥2 heuristic cannot see
  sentence-level concentration. No corpus case measures this.
- H2: a student may read the neutral counts summary as reassurance rather than as a
  prompt; no usability evidence was collected.
- H3: the generic Primary wording ("checks found sentences and words") may feel
  unspecific to students even when true; untested.

**Q7 — Can wording or a lesson-mapping change fix it without detection changes?**
Partially, confirmed: the presentation-side neutral review already exists
(`app.js:5275–5298`; `docs/live_feedback_body_findings.md:67–94`), the generic Primary
and Next Step wording is already check-invitational rather than judgmental, and the
honest `NEUTRAL_REVIEW` status is displayed in Process 07. What wording cannot do is
create a targeted Paragraph-2 development signal: none exists (Q3). Adding a prepared
lesson binding for `general_observable_body_evidence` would convert neutral evidence
into a dimension-labelled lesson (`Structure · …`), which risks labelling counts as a
finding — not recommended. The documented route for a targeted signal is a **new
observation**, `BODY.Pn.DEVELOPMENT.SINGLE_SENTENCE_OBSERVED`, already specified with
acceptance cases as a protected proposal requiring separate approval
(`docs/live_feedback_body_findings.md:96–126`); that is a detection change, explicitly
out of bounds here.

---

## 5. Two-paragraph live test

### 5.1 Method

Exact task text was run through the actual backend workflow —
`EssayAnalysisService.analyze(...)` with `include_research_trace=True`, the same
coordinator the `/api/analyze-stage` route invokes (HTTP/auth wrapping omitted; no
code changed). Assignment and focus match the corpus: topic "Should students use
smartphones in the classroom?", focus `smartphones, students, classroom, teacher`.
Body only, as supplied (no Introduction). Probe script:
`C:\Users\MYPC~1\AppData\Local\Temp\opencode\body_traits_probe.py`.

Text used verbatim:

> First, smartphones help students during classroom activities. For example, a teacher
> can ask students to look up a difficult word in an online dictionary. Students can
> read the meaning and explain it to their classmates. This helps students understand
> the lesson.
>
> Second, smartphones can help students practice lessons.

### 5.2 Per-paragraph detections

| Detection | Paragraph 1 | Paragraph 2 |
|---|---|---|
| Segmented (span, substantive) | yes (4 sentences) | yes (1 sentence) |
| Focus terms observed | smartphones, students, classroom, teacher | smartphones, students |
| Topic-sentence candidates | 4 | 1 |
| Clause candidates | 5 (`help`, `ask`, `read`, `helps`, `understand`) | 2 (`help` ROOT, `practice` xcomp — same sentence) |
| Supporting-detail event | `SUPPORTING_DETAIL.CANDIDATE` | `SUPPORTING_DETAIL.CANDIDATE` |
| Example/explanation marker | yes ("For example") | none |
| Unity sentence pairs | `UNITY.SENTENCE_PAIR_1_2/2_3/3_4` | not applicable (single sentence) |
| Repetition | surface + normalized ("students") | none |
| Keyword-list candidate | false | false |

Cross-paragraph: pair [1,2] status `LEXICAL_OR_TRANSITION_CANDIDATE` (shared lemmas +
"second"). Introduction: none supplied → `NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED`.

### 5.3 Feedback result

- Current Goal: stage constant (`BODY.GOAL.DEVELOP_BODY_IDEAS`).
- Primary Feedback: `general_observable_body_evidence` — "The checks found sentences
  and words in the Body. Read each paragraph and check that it explains your point."
  (cites `P1.SEGMENTED`, `P2.SEGMENTED`).
- What's Working: 7 items (focus ×2, topic ×2, detail ×2, repetition ×1).
- Needs Attention: only `BODY.LIMITATION.NO_SEMANTIC_VALIDATION`.
- Next Step: `introduction_context_unavailable`, `rule_ids: []`.

### 5.4 Is any existing Rule Event able to support a targeted supporting-detail suggestion for Paragraph 2?

**No.** `BODY.P2.SUPPORTING_DETAIL.CANDIDATE` is positive evidence and is cited only
in What's Working; `BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED` is not emitted (the
paragraph has two clause candidates); no other negative P2 event exists (focus
observed, topic candidate found, pair linked, not list-like). Therefore no branch can
produce a Paragraph-2 development concern for this input.

**Control (independently re-run):** replacing Paragraph 2 with "Second, smartphones
support learning." (one clause candidate) emits `BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED`
and selects `first_paragraph_without_additional_clause_candidate` — targeted Primary,
Needs Attention and Next Step messages naming Paragraph 2, plus the
`HELP-SUPPORTING-DETAIL` lesson and highlight via the secondary/primary bindings.
This matches the documented control (`docs/live_feedback_body_findings.md:89–94`).

**Sentence count ≠ quality:** Paragraph 2 has one recorded sentence yet two clause
candidates, so the system correctly does not infer deficiency from the count; and the
control shows the system only states an absence when its own recorded heuristic
measured one. The report does not equate "1 sentence" with "weak paragraph".

---

## 6. Evidence limitations (as they bear on Ideas/Organization feedback)

1. **No semantic validation by design** — `BODY.LIMITATION.NO_SEMANTIC_VALIDATION` is
   always emitted; nothing in Body feedback establishes meaning, support, logic, facts
   or readiness (`body_rules.py:143–149` prohibited conclusions).
2. **Clause/detail heuristic** — supporting details = ≥2 finite, subject-linked clause
   candidates anywhere in the paragraph (`body_rules.py:402`); parse errors,
   unusual constructions and clause concentration inside one sentence all affect it
   (`stage_evidence.py:108`: "A parsed clause does not establish meaning, support, or
   validity").
3. **Topic sentence heuristic** — clause + focus/recurring-concept only; rhetorical
   role is never confirmed (`body_rules.py:704–711`).
4. **Focus matching is lexical** — direct or lemma-normalized overlap only;
   paraphrases, synonyms and teacher-list gaps produce both false negatives
   (`FOCUS_TERMS_NOT_OBSERVED`) and weak positives (`:696–703`).
5. **Continuity is lexical** — sentence unity, adjacent-pair continuity and
   Introduction overlap are shared-word/transition observations; absence does not
   prove disconnection, presence does not prove coherence (`:452`, `:524`, `:784`).
   WordNet links are single-synset candidates, never disambiguated, never cited.
6. **Paragraph boundaries** — blank-line inference only; internal newlines preserved;
   boundary events are not rhetorical judgments (`:675–678`).
7. **Example markers** — regex expressions; "a marker alone does not show that an
   example or explanation follows" (`:742`), and the event currently reaches no field.
8. **Repetition counts are neutral** — repetition can be continuity or style; the
   system never judges it (`stage_evidence.py:160`).
9. **Sentence/token counts are not quality** — stated in the neutral review limitation
   (`app.js:5379`) and in the live-feedback findings.
10. **Selection-layer limits** — no ranked unselected alternatives are recorded;
    the trace records the chosen branch's condition only; field item alignment is
    count-checked provenance, not a runtime per-item log (`app.js:2785`).
11. **Uncited-but-emitted events** (section 3.3) — Process 07 shows them as NOT
    CITED; they are honest evidence that no student-facing text uses.
12. **Neutral tutor items carry no excerpt** — `NEUTRAL_REVIEW` deliberately has
    `excerpt: null`; only bound branches produce highlights.
13. **Trace timings** are in-process Python only; browser/network/auth are outside
    (`essay_analysis_service.py:274`).
14. **Corpus breadth** — all fixture cases share one assignment, topic and focus list;
    behavior on other genres/ages is unmeasured (relevant to any wording change).

---

## 7. Recommended first improvement (one, Ideas-aligned)

**Surface the existing `BODY.Pn.EXAMPLE_OR_EXPLANATION_MARKER` event as a
What's Working item.**

- **Existing branch/event extended:** the `paragraph_evidence_loop` branch of
  `FeedbackService.generate_body` (What's Working), using the already-emitted
  `BODY.Pn.EXAMPLE_OR_EXPLANATION_MARKER` event (`body_rules.py:736–743`). No new
  detection, no new event, no threshold change.
- **Supporting recorded evidence:** the event carries verified marker spans
  (`text`, `start`, `end`, `evidence_type: direct_discourse_expression`) plus its
  limitation; it fired for Paragraph 1 in both probe runs ("For example") and sits
  today permanently uncited (section 3.3).
- **Current weakness addressed:** the clearest Ideas-development signal the system
  records never reaches the student; What's Working can only say the paragraph "has
  other sentence patterns that may add detail". For `body_generic`, whose Needs
  Attention is limitation-only, this adds a concrete, paragraph-specific,
  non-judgmental development observation without inventing a concern.
- **Learning goal:** the student notices where example/explanation language appears
  and checks whether the sentences after it actually develop the paragraph's idea —
  the conference habit of asking "does this detail help the reader understand the
  point?"
- **Age-appropriate wording** (neutral, check-invitational, no praise, no claim that
  an example exists): *"Paragraph 1 includes words such as 'for example'. Check that
  the sentences after them explain or give an example for this paragraph's idea."*
  (Join the first recorded marker, following the existing repeated-opens message
  pattern at `feedback_service.py:616`.)
- **Placement:** `services/feedback_service.py` → `generate_body`, What's Working
  loop only. Not the Writing Tutor: What's Working is `LIST_DISPLAY_ONLY`
  (`app.js:2825`), so no lesson binding and no `feedback_help.json` change are needed,
  and no tutor status changes.
- **Tests that would be required:** a `tests/test_body_rules.py`-style case asserting
  the new Working item, its provenance `rule_id`, and `selected_message_count` parity
  when a marker is present and its absence when not; re-run parity assertions in
  `tests/test_feedback_decision_flow.py` (count vs. messages, `:25`); confirm
  `tests/test_causal_transparency.py` fixture assertions (`:67–73`) still hold — no
  hardcoded What's Working lengths exist for Body today; provenance-shape checks in
  `tests/test_feedback_provenance.py`; `node --check static/app.js` plus the browser
  check for the Working list display; full suite green.
- **False-positive / misinterpretation risk:** low–moderate. "such as"/"including"
  can appear without an example following — mitigated by the conditional wording
  ("check that…") and the event's own limitation; risk that a student reads it as
  praise of the example's quality — mitigated by avoiding any evaluative adjective;
  possible overlap with the `HELP-SUPPORTING-DETAIL` lesson — different field and
  non-evaluative, so no duplicate coaching. Wording should be validated against
  broader assignments than the single fixture topic (limitation 14).
- **Relevant 6+1 instructional principle (Ideas, paraphrased):** good Ideas are
  developed with details that extend the central message; the instructional move is
  to help writers locate their example/explanation language and judge whether it
  actually develops the paragraph's point — a noticing-and-checking prompt, not a
  quality verdict.

**Not recommended as the first step** (documented context, unchanged status): the
gated proposal `BODY.Pn.DEVELOPMENT.SINGLE_SENTENCE_OBSERVED`
(`docs/live_feedback_body_findings.md:96–126`) is the only route to a targeted
Paragraph-2 development *signal*; it changes protected detection, selection and
presentation and requires separate approval. Likewise, adding a prepared lesson
binding for `general_observable_body_evidence` is not recommended: it would label
neutral counts with a dimension and risk inventing a finding.

---

## 8. Source references

Framework (external):

- Education Northwest — *6+1 Trait Rubrics* resource page:
  https://educationnorthwest.org/resources/61-trait-rubrics (K–2 and 3–12 rubric
  downloads; March 2021 resource, 2018 refined rubrics). Trait principles in section 3
  are original paraphrases; no rubric text, band descriptors, or official scores are
  used here.

Backend:

- `services/body_rules.py` — paragraph analysis (`:157`), clause candidates
  (`:331`), topic sentences (`:338`), supporting details (`:398–412`), unity
  (`:414`), cross-paragraph continuity (`:482`), Introduction continuity (`:557`),
  rule events (`:650–816`), missing elements (`:627`, `:818`).
- `services/feedback_service.py` — Body selection (`:534–804`), priority order
  (`:801`), provenance (`:743–763`), `_emitted_events`/`_emitted_rule_ids` (`:13–22`).
- `services/stage_evidence.py` — span split (`:7`), sentence clipping (`:28`), clause
  candidates (`:63`), repetition (`:114`), concept comparison + WordNet (`:164`).
- `services/essay_analysis_service.py` — pipeline (`:31`), Body wiring (`:121–147`),
  trace assembly (`:198–278`).
- `services/tutoring_lessons.py` — feedback-help catalog validation/loading (`:47`,
  `:127`).

Presentation:

- `static/app.js` — branch explanations (`:2671`), field tutor statuses
  (`:2770–2830`), neutral Body overview (`:5275–5298`), tutor item construction
  (`:5300–5401`), tutor selection (`:5403`), Process 07
  (`buildFeedbackDecisionFlow` `:2695`, `renderFeedbackDecisionFlow` `:3069`).
- `content/lessons/feedback_help.json` — Body lesson bindings and `HELP-*` lesson
  content (validated by `services/tutoring_lessons.py`).

Tests and fixtures:

- `tests/causal_transparency_cases.json` — `body_generic` / `body_mixed` /
  `body_wordnet` inputs.
- `tests/test_causal_transparency.py` — protected-file guard (`:24`, `:39`), Body
  branch assertions (`:67–73`), neutral-review assertions (`:160–163`).
- `tests/test_feedback_decision_flow.py` — branch/count parity (`:232`, `:25`).
- `tests/test_body_rules.py`, `tests/test_live_body_feedback.py`,
  `tests/body_live_feedback_cases.json` — Body detection and live-feedback contracts.

Reports:

- `docs/feedback_decision_flow_report.md` — Process 07 verification and the §15
  (`§7`) `body_generic` finding.
- `docs/live_feedback_body_findings.md` — controlled Body investigation (`:25–65`),
  neutral presentation (`:67–94`), protected-rule proposal (`:96–126`).

Probe evidence (this inspection): temp script
`C:\Users\MYPC~1\AppData\Local\Temp\opencode\body_traits_probe.py` — three runs:
task example (body only), corpus `body_generic` (with Introduction), and the control
P2 variant; outputs summarized in sections 4 and 5.

---

## 9. Files that would need modification if the recommendation were implemented

For the recommended improvement (marker → What's Working item):

| File | Change | Protection notes |
|---|---|---|
| `services/feedback_service.py` | add the marker item + rule link inside `generate_body`'s What's Working loop (`:630–660`); trace `selected_message_count` updates automatically | protected — requires approval. Guarded by the mutation-during-run hash check in `tests/test_causal_transparency.py:24,39` (captures `app.py`, `services/*.py`, `content/**/*.json` at start); no pinned hash exists for this file (the only pinned service hash found is the Introduction safeguard, `tests/test_nlp_transparency.py:243`) |
| `tests/test_body_rules.py` | new/extended assertions: marker-present item, marker-absent absence, provenance rule id, count parity | test file, modifiable |
| `tests/test_feedback_decision_flow.py` | re-verify branch/count/message parity for fixtures after the response shape changes | test file, modifiable |
| `tests/test_causal_transparency.py` | confirm Body fixture assertions (`:67–73`) still pass; adjust only if any field-level expectation changes | test file, modifiable |
| `tests/test_feedback_provenance.py` | provenance-shape expectations if item counts are asserted | test file, modifiable |
| `tests/transparency_browser_check.cjs` / `.py` | presentation regression for What's Working display | test file, modifiable |
| `static/app.js` | **no change expected** — What's Working is `LIST_DISPLAY_ONLY` and item alignment is count-derived (`:2770–2787`); verify only | allowed to edit, but should not be necessary |
| `content/lessons/feedback_help.json` | **no change** — What's Working has no lesson binding | content JSON is inside the protected hash list |
| `services/body_rules.py` | **no change** — the event already exists | protected detection, untouched |
| `docs/` reports | record the new Working item in the relevant feedback reports | docs, modifiable |

For reference, if the gated single-sentence proposal were ever approved (not part of
this recommendation): `services/body_rules.py` (new observation),
`services/feedback_service.py` (eligibility/priority), `static/app.js`
(presentation/highlight), `content/lessons/feedback_help.json` (any binding), plus
`tests/test_body_rules.py`, `tests/causal_transparency_cases.json`-driven tests,
`tests/test_live_body_feedback.py` and the browser check — each gated behind the
separate approval stated in `docs/live_feedback_body_findings.md:96`.

---

*Inspection only. No implementation was performed; work stops after this report.*
