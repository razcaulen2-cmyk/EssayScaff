# Human annotation guide — semantic feasibility pilot

## Purpose and provenance

These are developer-authored diagnostic examples created to exercise varied language and topics. Their construction tags are experiment-design notes, **not human labels, expected answers, or a gold-standard dataset**. Annotators should judge the displayed topic and text independently and should not use the construction tags to make a decision. No real student work is included.

Do not infer factual correctness. This pilot asks what a reader can interpret, not whether a statement is true.

## Semantic intelligibility (required)

- **CLEAR** — The text communicates an interpretable idea in context. Grammar can be imperfect, and a claim can be factually questionable.
- **UNCLEAR** — Some intent is recoverable, but key relationships, references, or propositions are incomplete, confusing, or ambiguous.
- **NONSENSICAL** — In the stated academic context, the text does not communicate a reasonably interpretable idea. Do not use this label merely because a term is unfamiliar or the writing is figurative.
- **UNCERTAIN** — You cannot confidently choose among the other labels.

Use the assignment topic as context, but assess intelligibility separately from whether the writing addresses that topic.

## Topic relevance (optional, separate label)

- **RELEVANT** — The expressed idea addresses the assignment topic.
- **PARTLY_RELEVANT** — Some of the idea relates, but important content is off-topic or the relation is weak.
- **NOT_RELEVANT** — The interpretable idea does not address the topic.
- **UNCERTAIN** — Relevance cannot be judged confidently.
- **NOT_ASSESSED** — Leave relevance unscored.

Keyword overlap alone is not sufficient to mark text relevant. A nonsensical string can contain many topic terms.

## Figurative language (optional, separate field)

Choose **YES**, **NO**, **UNCERTAIN**, or **NOT_ASSESSED**. Figurative writing can be clear (for example, “Books are windows”); do not equate metaphor with nonsense.

## Confidence and explanation

Record confidence from **1** (low) to **5** (high) in the intelligibility label. Give a short explanation citing the text or missing relationship that informed your decision. The explanation is not a factuality judgment.

## Examples for rubric calibration (illustrative only)

| Example | Considerations (not a prescribed label) |
|---|---|
| “Late-night phone use can reduce sleep, which may make it harder to concentrate in class.” | Clear cause-and-effect claim; truth is not being assessed. |
| “Students use the social media too late and they is tired in class.” | Grammar errors do not by themselves prevent interpretation. |
| “Sleep. Students. Attention. Social media.” | A keyword list may have lexical coverage without expressing a proposition. |
| “Reading is important because students…” | The intended completion is missing; judge the incompleteness. |
| “Classroom attention drinks invisible clocks.” | Topic-like words occur, but their relationship may not yield an interpretable idea. |
| “Books are windows that let a reader travel through an idea.” | Figurative language can still be interpretable. |
| “A community garden gives neighbors a place to meet.” | Understandable text may be unrelated to an assigned topic. |
| “Social media does not always reduce sleep.” | Negation changes the claim; do not ignore it. |
| “Uniforms always make students equal, and uniforms never make students equal.” | Contradiction is different from uninterpretable language; consider the intended propositions. |
| “Particulate matter can enter the respiratory tract.” | Unfamiliar terminology can still appear in an intelligible statement. |

## Independent review and privacy

Use a pseudonymous reviewer ID (for example, `reviewer_a`), not a real name or email. Annotators should work independently and must not inspect another reviewer's file before independent labeling is complete. The tool filters progress and saved records to the current reviewer ID and displays no other reviewer's decisions. After independent annotation is complete, files may be combined for agreement analysis.

Annotations are written separately from `samples.json`. Each record records the reviewer ID, UTC time, and `human_annotation` provenance. The program does not pre-fill labels or convert developer construction tags into labels.
