# Introduction Stage Evaluation — EssayScaff V2

**Evaluation date:** 2026-10-25  
**Scope:** Introduction stage only. Body and Conclusion were not evaluated.  
**Test type:** Controlled browser evaluation using the running application and real NLP responses (no mocked analysis).  
**Application changes:** None. No NLP algorithm, feedback wording, rule, schema, UI, or migration changes were made.

---

## A. Test Environment

### Application and browser

- Local EssayScaff V2 instance at `http://127.0.0.1:5059`.
- Chrome 150 engine (Qoder in-app browser, Electron-based).
- The application was started from a temporary launcher that imported the existing app and overrode `app.config["DRAFT_DATABASE_PATH"]`. `app.py` itself does not read a `DRAFT_DATABASE_PATH` environment variable.
- Isolated temporary database: `C:\Users\My Pc\AppData\Local\Temp\essayscaff_intro_eval\intro_eval.sqlite3`.
- Fictional teacher and student accounts were registered through the normal application forms. No real student information or credentials are included in this report.

### Assignment created through the teacher workflow

The assignment was created through the actual teacher interface, not by inserting rows directly:

| Field | Value |
|---|---|
| Title | The School Garden Debate |
| Writing Topic | Should schools turn part of their playgrounds into vegetable gardens? |
| Focus Terms | schools, playgrounds, vegetable gardens, students, learning |

The student account joined the classroom with the generated enrollment code and opened the assignment workspace through the normal student flow.

### Real database safety

The real database was not migrated, written to, or otherwise modified.

| Check | Result |
|---|---|
| SHA-256 of `instance/essay_scaff_drafts.sqlite3` | `d6ed740fb17ad30a2b1af7b5cbd71572617e2f465e32717489ad570159d83814` |
| Size | 114,688 bytes |
| `PRAGMA integrity_check` | `ok` |
| `PRAGMA foreign_key_check` | no rows |
| `writing_activity` table | absent |
| Users / classrooms / enrollments / assignments | 27 / 1 / 1 / 8 |
| Writing sessions / revisions / submissions | 7 / 0 / 2 |
| Writing activity tracking | disabled |

### Evidence capture method

- Raw `/api/analyze-stage` responses were captured in the browser at response time. The rendered Writing Tutor used those same responses; analysis was not rerun for export.
- The application's **Copy Full Analysis** action was used for each test. The exported reports state: "Source: cached selected-stage analysis response; no analysis was rerun."
- Screenshots were taken of the entered writing, Writing Tutor, highlighted evidence, Stage Progress, Guided Progression, and relevant Transparency Inspector sections.
- Full analysis exports, raw responses, and transparency text are stored under `docs/introduction_stage_testing/`.

### Existing automated tests run without modification

| Suite group | Result |
|---|---|
| `test_introduction_rules.py`, `test_introduction_feedback_quality.py`, `test_introduction_feedback_targeted.py`, `test_introduction_ideas.py` | 79 passed |
| `test_reason_highlighting.py`, `test_tutoring_lessons.py`, `test_feedback_decision_flow.py`, `test_feedback_provenance.py` | 68 passed |
| `test_essay_analysis.py` | 17 passed |
| **Total** | **164 passed, 0 failed** |

No tests were weakened or rewritten.

### Evaluation limits

- Three samples are illustrative evidence, not a benchmark. No accuracy percentage or confusion matrix is reported.
- The evaluation covers one assignment prompt and one isolated database.
- The browser session used the application's real rule-based pipeline and the installed spaCy model `core_web_sm` 3.7.1.

---

## B. Test 1 — Weak Introduction

### Input

> Schools have playgrounds where students spend time during breaks. Some schools also have vegetable gardens where plants are grown. Students can learn about plants and vegetables in different ways. This topic has many things that people can talk about.

### Actual processing

| Observation | Recorded value |
|---|---|
| Words / sentences / tokens | 39 / 4 / 43 |
| Teacher focus terms matched | All 5: schools, playgrounds, vegetable gardens, students, learning |
| Match evidence | 7 spans; 6 direct and 1 normalized (`learning` → `learn`) |
| Central-direction candidates | 4 |
| Supported clause predicates | 7 |
| `because` clause | None (`NO_BECAUSE_CLAUSE_IDENTIFIED`) |
| Rules evaluated / triggered | 15 / 7 |
| Missing observable elements | none recorded |
| Analyzed-text fingerprint | `INTRODUCTION · 251 characters · a16c3698` |

### Student-facing feedback

| Field | Exact text |
|---|---|
| Header | **Ideas · Review Your Details** |
| What I noticed | "The checks recorded a possible main statement and additional sentence parts." |
| Look at your writing | Sentence 1, with **"spend"** highlighted (offsets 40–45) |
| What's working | "More than one subject-and-verb pattern was recorded in your opening." |
| Why it matters | "Readers can follow your point when they can see how your details connect to it." |
| How to improve | "Choose one detail already in your opening. Keep it if it helps explain your point, or add information if a reader needs it." |
| Limitation | "You do not need to use 'because'. The mark shows recorded sentence evidence, not an error or proof that the ideas work together." |
| Primary Feedback | "The checks recorded a possible main statement and additional sentence parts. Choose one detail and review how it helps explain your point." |
| Next Step | "Choose one detail already in your opening. Keep it if it helps explain your point, or add information if a reader needs it." |

### Decision trace

| Item | Recorded value |
|---|---|
| Selection branch | `intro_ideas_review_details` |
| Selection condition | "central_direction_candidates is nonempty; no recorded because-clause; development status is STRUCTURAL_ELABORATION_CANDIDATE; no logical relationship is inferred" |
| 6+1 Trait shown | Ideas |
| Instructional skill | Review Your Details |
| Lesson | `HELP-INTRO-REVIEW-DETAILS` |
| Highlight rule | First additional recorded predicate |
| Highlight reason | "First additional recorded predicate. Its sentence is shown alone; shared-sentence evidence marks only the extra predicate." |
| Worked example / thesis supplied? | No |

### Check results

| Check | Result | Evidence |
|---|---|---|
| Topic-term recognition | **PASS** | All five teacher focus terms were observed. `learning` matched through lemma normalization (`learn`). |
| Missing / unclear position detected | **FAIL** | No position or stance rule exists in the evaluated rule inventory. The final vague sentence was not identified as a problem. The result is a neutral detail review, not a missing-position finding. |
| Justification comes from actual text | **PARTIAL** | The structural observations are real: four root-clause candidates, seven supported predicates, and no `because` clause. However, the feedback treats the first sentence ("Schools have playgrounds…") as a "possible main statement" and does not connect the review task to the vague closing sentence. |
| 6+1 Trait correspondence | **PASS** | The branch maps to Ideas as an instructional category. Transparency records `trait_quality_assessment: NOT_PERFORMED`; no Ideas quality score is claimed. |
| "What I noticed" supported by evidence | **PASS** | It restates the recorded structural observations without inventing a thesis or an error. |
| Highlight relevance | **PARTIAL** | "spend" is correctly located and is the first additional predicate, but it is not the pedagogically weak part of this Introduction. The vague final sentence is not highlighted. |
| "How to improve" does not write the thesis | **PASS** | It asks the student to choose a detail and explain its connection; it does not supply a position or thesis. |
| Stage Progress consistency | **PARTIAL** | Stage Progress showed "No Specific Writing Issue Detected" while the Writing Tutor asked for a detail review and Guided Progression showed "Review Suggested". The neutral Stage Progress branch is intentional, but the three surfaces can read as contradictory. |
| Continue to Body accessible | **PASS** | The button was enabled and navigated to Body. |
| Transparency Inspector accurate | **PASS** | It recorded the same branch, rule IDs, candidate counts, highlight offsets, and `Direct WordNet Suggestions — Skipped`. |

### Test 1 classification

**Overall: PARTIAL.**

- The system correctly recognizes the topic and produces evidence-bound, non-hallucinated feedback.
- It does **not** identify the central weakness of the sample: the Introduction never states a position.
- The neutral result is an appropriate output for the implemented rule set, but it is a **missed concern** relative to the evaluation goal.
- The highlight is structurally accurate but pedagogically weak.

This is primarily a **rule-based NLP scope limitation** and a **missed concern**, not a crash or a false factual claim.

---

## C. Test 2 — Improved Introduction

### Input

> Schools should turn a small part of their playgrounds into vegetable gardens. These gardens can help students learn outside the classroom. Planting vegetables can also teach students useful skills.

### Actual processing

| Observation | Recorded value |
|---|---|
| Words / sentences / tokens | 29 / 3 / 32 |
| Teacher focus terms matched | All 5 |
| Match evidence | 6 spans; 5 direct and 1 normalized (`learning` → `learn`) |
| Central-direction candidates | 3 |
| Supported clause predicates | 4 |
| `because` clause | None |
| Rules evaluated / triggered | 15 / 7 |
| Analyzed-text fingerprint | `INTRODUCTION · 197 characters · 4d785e9f` |

### Student-facing feedback

The feedback text was **identical** to Test 1:

| Field | Exact text |
|---|---|
| Header | **Ideas · Review Your Details** |
| What I noticed | "The checks recorded a possible main statement and additional sentence parts." |
| Look at your writing | Sentence 2, **"These gardens can help students learn outside the classroom."** highlighted (offsets 78–138) |
| What's working | "More than one subject-and-verb pattern was recorded in your opening." |
| Why it matters | "Readers can follow your point when they can see how your details connect to it." |
| How to improve | "Choose one detail already in your opening. Keep it if it helps explain your point, or add information if a reader needs it." |
| Limitation | "You do not need to use 'because'. The mark shows recorded sentence evidence, not an error or proof that the ideas work together." |

### Decision trace

| Item | Recorded value |
|---|---|
| Selection branch | `intro_ideas_review_details` (same as Test 1) |
| 6+1 Trait shown | Ideas |
| Instructional skill | Review Your Details |
| Highlight rule | First additional recorded predicate |
| Highlight reason | "First additional recorded predicate. Its sentence is shown alone; shared-sentence evidence marks only the extra predicate." |

### Change from Test 1

| Dimension | Test 1 | Test 2 | Interpretation |
|---|---|---|---|
| Explicit position | No | Yes ("Schools should turn…") | Student added a clear position |
| Feedback branch | `intro_ideas_review_details` | `intro_ideas_review_details` | Unchanged |
| Primary feedback / Next Step | Detail review | Same detail review | Unchanged |
| Highlight | "spend" in sentence 1 | Sentence 2 | Changed only because the first additional predicate moved |
| Stage Progress | No Specific Writing Issue Detected | No Specific Writing Issue Detected | Unchanged neutral state |
| Topic relevance | All 5 terms | All 5 terms | Correctly preserved |

### Check results

| Check | Result | Evidence |
|---|---|---|
| Response to updated writing | **PARTIAL** | The system re-analyzed the new text and changed the highlight span, but the feedback branch, message, trait, and task stayed identical. The newly explicit position was not acknowledged. |
| Disappearance of prior concerns | **PASS (not applicable)** | No explicit missing-position or topic concern existed in Test 1. No stale concern was carried forward. |
| Remaining concerns justified | **PARTIAL** | The remaining "additional sentence parts" review is structurally true, but the feedback does not explain why the highlighted supporting sentence needs review or why the position sentence does not. |
| Topic relevance | **PASS** | All five focus terms were still observed. |
| Stage Progress update | **PASS (appropriate neutral)** | It remained neutral because the rule set found no supported concern. It did not claim that the new writing had resolved anything. |
| No false claim that all problems were resolved | **PASS** | No resolution claim was made. The system did not state that the Introduction was complete or correct. |
| Accurate highlighting / evidence | **PASS (structural) / PARTIAL (pedagogical)** | Offsets 78–138 exactly match sentence 2. The highlighted sentence is a real additional predicate, but it is a supporting detail rather than the new thesis sentence. |
| 6+1 Trait correspondence | **PASS** | Still mapped to Ideas as an instructional category; no quality score claimed. |
| Transparency Inspector accurate | **PASS** | The trace matches the rendered feedback and highlight. |

### Test 2 classification

**Overall: PARTIAL.**

The application handled the improved text safely and did not invent a problem. However, the student-visible feedback did not meaningfully respond to the most important change—the addition of an explicit position. The only observable adaptation was the highlight moving to sentence 2. This is a **rule-based limitation**: the implemented checks observe structure and lexical overlap, not thesis presence or stance clarity.

---

## D. Test 3 — Well-Developed Introduction

### Input

> Schools should turn part of their playgrounds into vegetable gardens because students can learn science through planting and develop responsibility by caring for plants. Students can observe how seeds grow, record changes, and connect these observations to their science lessons. Taking turns watering and maintaining the garden can also help students practice responsibility.

### Actual processing

| Observation | Recorded value |
|---|---|
| Words / sentences / tokens | 53 / 3 / 58 |
| Teacher focus terms matched | All 5 |
| Match evidence | 7 spans; 6 direct and 1 normalized (`learning` → `learn`) |
| Central-direction candidates | 3 |
| Supported clause predicates | 6 |
| `because` clause | One clause, offsets 69–168 |
| Clause topic overlap | Observed: `students` (direct) and `learning` → `learn` (normalized) |
| Rules evaluated / triggered | 16 / 8 |
| Analyzed-text fingerprint | `INTRODUCTION · 376 characters · c616ae37` |

### Triggered reason event

| Item | Recorded value |
|---|---|
| Rule | `INTRO.REASON.CLAUSE_TOPIC_OVERLAP` |
| Condition | "A 'because' advcl clause was identified and contains at least one focus-term match." |
| Evidence type | `spaCy_subtree_and_lexical_match_heuristic` |
| Clause span | Offsets 69–168; 14 tokens |
| Clause predicate | "learn" (offsets 90–95) |
| Limitation | "Topic-word overlap in the reason clause is not proof that the reason supports the point. Absence of overlap is not proof that it does not." |

### Student-facing feedback

| Field | Exact text |
|---|---|
| Header | **Ideas · Review Your Explanation** |
| What I noticed | "Your sentence has a possible main statement and a 'because' part to review." |
| Look at your writing | The full `because` clause: "because students can learn science through planting and develop responsibility by caring for plants" (offsets 69–168) |
| What's working | "The checks recorded a main-statement pattern and an explanation part." |
| Why it matters | "An explanation helps readers understand the point you want to make." |
| How to improve | "Read the explanation with your main statement. Keep it if it says what you intend, or add a detail a reader would need." |
| Limitation | "The mark shows sentence evidence, not an error. Word matches cannot tell whether the explanation is true or supports your point." |
| Primary Feedback | "The checks recorded a possible main statement and a 'because' part. Read them together and decide whether a reader needs more explanation." |
| Next Step | "Read your main statement with the explanation part. Keep it if it says what you intend, or add a detail a reader would need." |

### Decision trace

| Item | Recorded value |
|---|---|
| Selection branch | `intro_ideas_point_and_reason` |
| Selection condition | "central_direction_candidates is nonempty and reason_clause_evidence.clauses is nonempty; focus-word presence or absence within the reason does not change this neutral review" |
| 6+1 Trait shown | Ideas |
| Instructional skill | Review Your Explanation |
| Lesson | `HELP-INTRO-EXPLAIN-POINT` |
| Feedback purpose | Neutral review task (`NEUTRAL_REVIEW_TASK`) |
| Trait quality assessment | `NOT_PERFORMED` |
| Highlight rule | First source-ordered recorded `because` subtree |
| Highlight reason | "First source-ordered recorded because subtree; marked as explanation evidence, regardless of word overlap." |

### Stage Progress and Guided Progression

| Surface | Recorded state |
|---|---|
| Stage Progress data-state | `NO_ISSUE` |
| Stage Progress title | "No Specific Writing Issue Detected" |
| Stage Progress lead | "The available checks did not identify a specific structural concern." |
| Stage Progress detail | "Review your ideas before continuing." |
| Continue to Body | enabled |
| Review Writing | hidden (no supported concern) |
| Guided Progression badge | "Review Suggested" |
| Guided topic step | Detected |
| Guided complete-thought step | Detected |
| Guided position step | Not Checked |
| Guided reason/direction step | Not Checked |

The Guided Progression result is a **student self-check checklist**, not an automated NLP judgment. Its "Review Suggested" badge appears because the position and reason checkboxes were not confirmed by the student. It is independent of the Stage Progress neutral branch.

### Check results

| Check | Result | Evidence |
|---|---|---|
| Correct processing | **PASS** | Three sentences, 53 words, 58 tokens; the `because` clause was correctly identified at offsets 69–168; the highlighted text exactly matches. |
| No invented missing-thesis problem | **PASS** | No missing-thesis language appears. The feedback treats the main statement as merely "possible" and does not claim the thesis is weak. |
| No invented topic-relevance problem | **PASS** | All five focus terms were observed; no topic warning was displayed. |
| No arbitrary requirements | **PASS** | The task asks the student to read the statement and explanation together and keep or add detail; it does not require a specific length, structure, or `because`. |
| No forced 6+1 Trait when no concern is supported | **PASS with caveat** | The only selected trait is Ideas, recorded as an instructional category with `trait_quality_assessment: NOT_PERFORMED`. The header still displays "Ideas · …", which could be read as a trait judgment, but the transparency and limitation wording correctly deny a quality assessment. |
| Neutral state label | **PASS** | Stage Progress says "No Specific Writing Issue Detected." |
| Unnecessary corrective headings hidden | **PARTIAL / FAIL** | "What I noticed", "Look at your writing", "Why it matters", and "How to improve" all remained visible in the neutral state. The content is neutral, but the presentation still uses corrective framing. |
| Stage Progress reflects analysis | **PASS** | `NO_ISSUE` corresponds to the neutral `intro_ideas_point_and_reason` branch; Review Writing is hidden and Continue is enabled. |
| Continue to Body accessible | **PASS** | The button was enabled and navigated to Body using the existing stage navigation. |
| Transparency Inspector accurate | **PASS** | The trace matches the rendered feedback, trait mapping, rule IDs, and highlight. `Direct WordNet Suggestions — Skipped` is correct. |

### Test 3 classification

**Overall: PARTIAL.**

- **NLP behavior: PASS.** The analysis is accurate, evidence-bound, appropriately neutral, and does not invent problems.
- **Student-facing presentation: PARTIAL.** The neutral state still uses all four corrective section headings, and Stage Progress ("No Specific Writing Issue Detected") sits alongside Guided Progression ("Review Suggested").
- No software defect was observed in the analysis pipeline.

---

## E. NLP Transparency Findings

### What the transparency trace demonstrated

| Evidence | Test 1 | Test 2 | Test 3 |
|---|---|---|---|
| Analyzed text and input records | Present; fingerprint `a16c3698` | Present | Present; fingerprint `c616ae37` |
| Tokenization | Executed (43 tokens) | Executed (32 tokens) | Executed (58 tokens) |
| Part-of-speech tagging | Executed | Executed | Executed |
| Dependency parsing | Executed | Executed | Executed |
| Lemmatization | Executed | Executed | Executed |
| Sentence detection | Executed (4 sentences) | Executed (3 sentences) | Executed (3 sentences) |
| Noun phrase extraction | Executed | Executed | Executed |
| Concept candidate extraction | Executed | Executed | Executed |
| Teacher focus-term matching | Executed | Executed | Executed |
| Direct WordNet suggestions | **Skipped** | **Skipped** | **Skipped** |
| Related-word resource evidence | Not applicable | Not applicable | Not applicable |
| Introduction clause checks | Executed | Executed | Executed |
| Sentence topic-connection review | Executed | Executed | Executed |
| Earlier-section comparisons | Not applicable | Not applicable | Not applicable |
| Rule events and evaluation evidence | Executed (15 rules) | Executed (15 rules) | Executed (16 rules) |
| Rule-based feedback decision | Executed | Executed | Executed |
| 6+1 Trait and lesson mapping | Executed | Executed | Executed |
| Highlight evidence selection | Executed | Executed | Executed |

### Topic matching

- Teacher-provided focus terms were used; no automatic keyword expansion was claimed.
- Matching was direct or lemma-normalized.
- All five focus terms were observed in all three tests.
- `learning` matched the student word `learn` through the normalized path.
- The trace does not demonstrate TF-IDF participation, so no TF-IDF claim is made.
- The trace explicitly records WordNet suggestions as skipped; WordNet did not participate in any of these three decisions.

### Rule evaluation and feedback selection

| Item | Test 1 | Test 2 | Test 3 |
|---|---|---|---|
| Branch | `intro_ideas_review_details` | `intro_ideas_review_details` | `intro_ideas_point_and_reason` |
| Trait | Ideas | Ideas | Ideas |
| Skill | Review Your Details | Review Your Details | Review Your Explanation |
| Highlight | `spend` (40–45) | Sentence 2 (78–138) | `because` clause (69–168) |
| `INTRO.REASON.CLAUSE_TOPIC_OVERLAP` | Evaluated, not triggered | Evaluated, not triggered | **Triggered** |
| `INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE` | Evaluated, not triggered | Evaluated, not triggered | Evaluated, not triggered |

The neutral Stage Progress behavior is explained by the application's neutral-branch map at [static/app.js:6476](file:///C:/Users/My%20Pc/Desktop/EssayScaff-V2/static/app.js#L6476). Both Introduction branches used in Tests 1 and 2, and the Test 3 branch, are treated as neutral for Stage Progress.

### Trait mapping

The instructional-feedback record shows:

- Ideas: selected as an instructional category, with `trait_quality_assessment: NOT_PERFORMED`.
- Organization, Voice, Word Choice, Sentence Fluency, Conventions, Presentation: not selected for these Introduction results.
- The framework is identified as the 6+1 Trait Writing Model.
- The mapping is an instructional lesson selection, not a scored trait assessment.

### Highlight selection

- Test 1: the selection rule chose the first additional recorded predicate, "spend." The sentence shown is the first sentence.
- Test 2: the same rule chose the first additional predicate, which is now in sentence 2; the thesis sentence is not highlighted.
- Test 3: the reason-event rule chose the first source-ordered `because` subtree, offsets 69–168.
- In all three cases, the rendered `<mark>` in the editor mirror matched the recorded offsets and text. The highlighting is source-accurate. Its pedagogical relevance is weaker in Tests 1 and 2.

### Was the feedback current?

- Each captured response was the response used for the rendered feedback; the Full Analysis exports state that no analysis was rerun.
- The Transparency Inspector displayed a "CURRENT · Analyzed snapshot" state with a fingerprint for the analyzed text.
- When the editor content was changed without an immediate analysis, the Writing Tutor marked the result as stale ("Draft edited — analyze again"), cleared the old feedback content, and the application scheduled a new analysis. A subsequent analysis restored current feedback.
- No captured state presented an old analysis as current for a materially different text.

### The core transparency limitation

The inspector is accurate about what the system did, but the system itself has no stance/position detector for Introductions. The rule inventory contains clause, fragment, keyword-list, focus-term, development, reason, and goal checks; it does not contain a rule that decides whether the Introduction states a position. That absence explains the Test 1 miss and the lack of meaningful change in Test 2. The application does not hide this absence—its limitation text says the checks do not determine whether an idea is correct or meaningful—but a student may still read "possible main statement" as stronger feedback than it is.

---

## F. Student Interface Findings

| Interaction | Result | Evidence |
|---|---|---|
| Editor accepts entered text | **PASS** | The exact Test 3 text was accepted: 376 characters, 53 words. |
| Editor preserves text | **PASS** | After navigating to Body and back to Introduction, the exact text was still present. An unsaved edited version also survived navigation away to the dashboard and back within the session. |
| Analyze Now shows Writing Tutor feedback | **PASS** | Each analysis rendered the Writing Tutor with the recorded branch, sections, and highlight. |
| Editor and tutor remain usable | **PASS** | No crash, frozen state, or blocked control was observed during the three analyses. |
| Highlight points to correct text | **PASS** | The editor mirror `<mark>` matched the recorded span in all three tests: "spend", sentence 2, and the `because` clause. |
| Corrective state renders | **PASS** | The detail/reason review states rendered with the expected sections and limitation text. |
| Neutral state renders | **PARTIAL** | Stage Progress renders "No Specific Writing Issue Detected," but the tutor still shows corrective headings rather than a compact neutral presentation. |
| Stage Progress updates | **PASS with note** | It reached `NO_ISSUE` for all three tests. Because none of the three produced a supported concern, it did not show a review-required state. Guided Progression can still say "Review Suggested" from unchecked self-checks. |
| Review Writing focuses editor | **PASS (auxiliary state)** | Review Writing is hidden in neutral states. In an auxiliary keyword-list state it appeared; clicking it moved focus to the textarea (`document.activeElement` = `stage-text`) and scrolled the editor into view. |
| Continue to Body uses existing navigation | **PASS** | Clicking Continue to Body changed the active stage to Body, showed the Body editor, and did not silently discard the Introduction. Returning to Introduction restored the text and its feedback. |
| Continue to Body does not auto-run Body analysis | **PASS** | No BODY analysis request was issued on navigation. |
| Unsaved edits do not create revisions | **PASS** | After an unsaved edit, no `POST /api/revisions` occurred and the revision area still said "No revisions saved yet. Select Save Revision to save a snapshot." |
| Transparency Inspector remains functional | **PASS** | Sections expanded, decision evidence was visible, and Copy Full Analysis produced complete exports. |
| No new buttons or features | **PASS** | Only existing controls were used. |

### Student-facing inconsistencies to note

1. **Neutral Stage Progress vs. Guided Progression.** Stage Progress says "No Specific Writing Issue Detected" while Guided Progression says "Review Suggested" because the student has not checked the position and reason self-check boxes. The two surfaces answer different questions—automatic structural checks vs. a student checklist—but the labels do not make that distinction obvious.
2. **Corrective headings in a neutral result.** The tutor keeps "What I noticed", "Look at your writing", "Why it matters", and "How to improve" in the neutral state. The wording is careful and includes a limitation, but the structure still frames the result as a correction.
3. **Trait label.** "Ideas · Review Your Explanation" is an instructional category, not a quality rating. The Transparency Inspector says so, but the header alone could be misread.

---

## G. Overall Introduction Stage Assessment

### Outcome by check

| Check | Test 1 (Weak) | Test 2 (Improved) | Test 3 (Well-developed) |
|---|---|---|---|
| Topic-term recognition | PASS | PASS | PASS |
| Missing / unclear position detection | FAIL (not implemented) | FAIL (not implemented) | PASS (no false problem invented) |
| Justification from actual text | PARTIAL | PARTIAL | PASS |
| 6+1 Trait correspondence | PASS | PASS | PASS (instructional category only) |
| "What I noticed" evidence | PASS | PASS | PASS |
| Highlight relevance | PARTIAL | PARTIAL | PASS |
| "How to improve" avoids writing the thesis | PASS | PASS | PASS |
| Stage Progress consistency | PARTIAL | PASS (appropriate neutral) | PASS (with Guided Progression note) |
| Continue to Body accessible | PASS | PASS | PASS |
| Transparency Inspector accuracy | PASS | PASS | PASS |
| **Overall test classification** | **PARTIAL** | **PARTIAL** | **PARTIAL (NLP PASS; presentation PARTIAL)** |

### What works well

- Teacher focus terms are recognized reliably across direct and lemma-normalized forms.
- Feedback is tied to recorded structure and lexical evidence; the system does not invent a thesis, a missing thesis, or a topic-relevance failure.
- The well-developed sample produces an appropriate neutral result rather than a manufactured problem.
- The Writing Tutor states its limitations clearly and does not present structural evidence as an error.
- The Transparency Inspector accurately exposes processing, rule events, branch selection, trait mapping, and highlight selection.
- The editor preserves writing across navigation, unsaved edits do not create revisions, and Continue to Body uses the existing stage navigation.
- No stale analysis was presented as current in the captured states.

### What does not work as an evaluation of Introduction quality

- **No stance/position detection.** The weak Introduction and the improved Introduction receive the same branch and nearly the same feedback. The system cannot tell that one lacks a position and the other contains one.
- **No meaningful response to thesis improvement.** Test 2 changed only the highlight location; the student-visible review task did not acknowledge the new position.
- **Highlighting is structural, not pedagogical.** Test 1 highlights "spend", and Test 2 highlights a supporting sentence, while the vague closing sentence and the thesis sentence are not the focus of the review.
- **Neutral presentation still looks corrective.** A well-developed Introduction that receives no supported concern still gets all four corrective section headings.
- **Guidance surfaces can conflict.** Stage Progress and Guided Progression can say different things because one is automatic and the other is a self-check list.

### Classification of findings

| Category | Finding |
|---|---|
| **Software defect** | None observed in the analysis, rendering, navigation, or persistence paths exercised. No crash, lost writing, or revision created by an unsaved edit. |
| **Rule-based NLP limitation** | No stance/position classifier; reason detection depends on a `because` clause with topic overlap; highlighting uses source-order structural selection rather than pedagogical relevance. |
| **Missed concern** | Test 1's missing position was not identified. Test 2's newly explicit position was not acknowledged. |
| **False positive** | None observed. Test 3 did not receive an invented thesis, topic, or structure problem. |
| **Appropriate neutral result** | Test 3's `NO_ISSUE` Stage Progress result is consistent with the neutral `intro_ideas_point_and_reason` branch and the stated limitation. |
| **Human-judgment / UX finding** | Corrective headings remain in the neutral state; Stage Progress and Guided Progression can appear contradictory; the "Ideas" header can be read as a trait judgment. |

### Suggested follow-up (not implemented)

These are observations for review, not changes made during this evaluation:

1. Add or explicitly scope a position/stance check for Introductions, or state in the student-facing feedback that position clarity is a self-check.
2. Make the neutral Writing Tutor visually distinct from a corrective state, or hide the corrective headings when the branch is neutral.
3. Reconcile the Stage Progress `NO_ISSUE` label with the Guided Progression "Review Suggested" badge, or label the Guided checklist as a separate student confirmation.
4. Consider whether the first additional predicate is the most useful highlight target, or whether the main-statement candidate should be highlighted when the review is about the main statement.

No application changes were made in response to these findings.

---

## H. Evidence

All evidence is stored in `docs/introduction_stage_testing/`.

### Screenshots

| File | Contents |
|---|---|
| `00-workspace-initial.png` | Initial student workspace for The School Garden Debate |
| `test1-weak-feedback.png` | Test 1 Writing Tutor and feedback |
| `test1-weak-tutor.png` | Test 1 "What I noticed" and "spend" highlight |
| `test1-weak-tutor-top.png` | Test 1 tutor header |
| `test1-weak-tutor-stage-progress.png` | Test 1 Stage Progress and Guided Progression |
| `test1-weak-how-to-improve-stage-progress.png` | Test 1 "How to improve" and neutral Stage Progress |
| `test1-weak-transparency-feedback-decision.png` | Test 1 feedback decision section |
| `test1-weak-transparency-feedback-evidence.png` | Test 1 feedback evidence section |
| `test1-weak-transparency-trait-mapping.png` | Test 1 trait and lesson mapping |
| `test2-improved-tutor.png` | Test 2 Writing Tutor and sentence-2 highlight |
| `test2-improved-stage-progress.png` | Test 2 Stage Progress |
| `test2-improved-transparency-feedback-decision.png` | Test 2 feedback decision section |
| `test3-developed-tutor.png` | Test 3 Writing Tutor and `because`-clause highlight |
| `test3-developed-stage-progress.png` | Test 3 neutral Stage Progress and Guided Progression |
| `test3-developed-transparency-feedback-decision.png` | Test 3 feedback decision section |
| `test3-developed-transparency-trait-mapping.png` | Test 3 trait and lesson mapping |

### Exported analysis and transparency files

| File | Contents |
|---|---|
| `test1-weak-analysis.json` | Raw captured Test 1 response |
| `test1-weak-full-analysis.txt` | Test 1 Copy Full Analysis export (source: cached response) |
| `test1-weak-transparency.txt` | Test 1 Transparency Inspector text |
| `test2-improved-analysis.json` | Raw captured Test 2 response |
| `test2-improved-full-analysis.txt` | Test 2 Copy Full Analysis export |
| `test2-improved-transparency.txt` | Test 2 Transparency Inspector text |
| `test3-developed-analysis.json` | Raw captured Test 3 response |
| `test3-developed-full-analysis.txt` | Test 3 Copy Full Analysis export |
| `test3-developed-transparency.txt` | Test 3 Transparency Inspector text |

The raw responses and full-analysis exports contain the recorded input text, segmentation counts, token/POS/dependency/lemma evidence, topic matches, rule events, feedback decision, trait mapping, and highlight spans described above.

---

**End of Introduction evaluation.** Body and Conclusion were not tested. No commit, push, migration, or application change was made.
