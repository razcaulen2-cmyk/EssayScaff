# Introduction subordinator false positive — diagnosis and correction status

## Status and scope

Reproduced on 2026-10-21 using the real authenticated Flask analysis pathway,
spaCy `en_core_web_sm` 3.7.1, and an isolated test database. The earlier Writing
Tutor presentation change deliberately left this detector defect unresolved.
The subsequently approved **before-only correction is now implemented and
behaviorally verified**. The protected research pin remains unchanged and
fails on changed implementation line metadata; separate approval is required
before updating that baseline. See [the correction review](before_subordinator_safeguard_review.md).
Removing the sentence from the earlier Although demonstration did not fix it;
the current correction is in the Rule Base itself.

## Reproduction

Assignment: “Should students be allowed to use smartphones during class?”
Focus terms: smartphones, students, classroom, learning, distractions.

Input:

> Local workers arrange vegetables, rice, and fruit before the doors open.

Actual Rule Event: `INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR`.
Actual selected branch: `possible_incomplete_subordinator`.
Original backend message:

> The sentence may be unfinished after 'before'. Add the rest of the thought so readers can follow it.

The sentence already contains a main statement and a subordinate time clause.
That warning is a false positive. Its zero focus matches are a separate,
accurate lexical observation, not the cause of this sentence-structure finding.

## Established cause

The recorded parse includes:

| Text | Span | POS/tag | Dependency | Head |
|---|---|---|---|---|
| arrange | 14–21 | VERB/VBP | ROOT | arrange (14) |
| before | 50–56 | SCONJ/IN | mark | open (67) |
| doors | 61–66 | NOUN/NNS | nsubj | open (67) |
| open | 67–71 | ADJ/JJ | advcl | arrange (14) |

`IntroductionRuleBase._incomplete_subordinator_evidence` builds its
`predicate_starts` only from VERB/AUX tokens with a clause dependency. The ADJ
prediction for *open* excludes that head. Consequently,
`token.dependency == 'mark' and not marker_has_clause_head` fires, even though
the dependency graph links the subordinate subject and head to a separate
finite main predicate. This is a POS/attachment heuristic limitation.

## Original minimal fix proposal — superseded by the before-only correction

Evaluate a narrowly scoped exception to the **mark-with-unrecognized-head**
condition, rather than changing the global predicate set or suppressing every
sentence that contains a main clause.

Candidate guard to investigate:

1. The marker has dependency `mark`.
2. Its recorded head is an ADJ with dependency `advcl`.
3. That head has its own explicitly linked subject (`nsubj`/the existing subject
   dependency set).
4. The head's recorded dependency attaches directly to a **different**, finite
   VERB/AUX ROOT predicate in the same sentence, with its own linked subject.
5. All token/head links refer to the same sentence and valid offsets.

Only under that exact graph should the unrecognized-head condition be
considered for suppression. Keep unattached ROOT markers, missing main-clause
patterns, nominal/prepositional cases, and the other existing conditions
unchanged. Do not infer grammatical correctness from an adjective or a subject
alone. This proposal needs evaluation: a dependency graph can also be wrong.

## Required positive and negative examples for that later change

The table below records the original proposed acceptance examples, not a test
result table. Actual verified Cases A–H and limitations are in the correction review.
Run them through the real model and inspect the parse as well as the emitted
events before approving a detector patch.

| Input | Expected incomplete-subordinator outcome |
|---|---|
| Local workers arrange vegetables, rice, and fruit before the doors open. | No warning for `before` (reported false positive) |
| Workers prepare lunch before the cafeteria opens. | No warning |
| Before the doors open, workers arrange the vegetables. | No warning |
| Although the library was closed, we studied at home. | No warning |
| Although students use smartphones during class. | Keep warning candidate |
| Before the doors open. | Keep warning candidate: no independent main statement |
| Although the library was closed. | Keep warning candidate |
| Because plastic waste harms rivers. | Keep warning candidate |
| Local workers arrange vegetables. Although the cafeteria offers healthy meals. | Keep the Although warning in the second sentence |

Add controlled record tests for the narrow guard: missing subordinate subject,
missing main subject, same ROOT/head, non-`advcl` adjective, and cross-sentence
head links must not invoke the exception. Also test a complete main clause
followed by an actually unfinished subordinate construction, so the exception
does not turn “a main clause exists” into blanket suppression.

## Research-contract handling

For the approved correction, capture before/after analyses, Rule Events, provenance,
branch selections, source metadata, and the protected research fixture. The
Research Inspector exposes implementation line locations, so even a small
detector edit may affect protected trace metadata. Report any contract change
and obtain approval before updating Inspector descriptions or re-pinning a
hash. Source snapshots, old/new fingerprints, and a unified diff were saved.
No protected pin, Inspector implementation, or presentation code was changed.
