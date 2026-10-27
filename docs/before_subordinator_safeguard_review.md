# Before-only incomplete-subordinator safeguard — approved metadata-only pin update

## Result

The confirmed complete sentence no longer emits an incomplete-subordinator
finding for `before`. The combined Introduction emits only its genuine
`Although` candidate. This is a structural heuristic correction, not a claim
that EssayScaff has established grammatical or semantic correctness.

Before the separately approved baseline update, the full suite reported
478 passed, 1 failed, 0 skipped, 0 errors. The sole failure was the protected
research pin. That result is preserved below as the pre-approval history.

The user subsequently approved updating only the plastics Introduction
research-output pin, conditional on re-verifying all 15 metadata-only changes.
That verification passed against the saved canonical records and a fresh
authenticated Flask result. Only the expected fingerprint in the existing
assertion is updated; final full-suite verification is recorded separately.

## Source change and boundaries

Production file changed: `services/introduction_rules.py` only.

`IntroductionRuleBase._incomplete_subordinator_evidence` now consults
`_before_adjective_clause_supported` only when the existing predicate filter
does not recognize a `before` marker's head. The exception requires:

- `before` (case-insensitive), SCONJ, dependency `mark`;
- a head recorded as ADJ/JJ with dependency `advcl`;
- that head attached directly to a distinct finite VERB/AUX ROOT;
- separate, explicitly linked grammatical subjects for both candidates;
- no `mark` dependent on that ROOT that would undermine its independent status;
- matching token/dependency records and valid source positions in one sentence.

Missing, contradictory, foreign-sentence, duplicate, or invalid evidence does
not invoke the exception. The ordinary predicate filter, original spaCy
annotations, emitted-event schema and uncertainty limitations are unchanged.
No vocabulary such as *doors* or *open* is hardcoded. The exception is not
extended to other conjunctions or adjective tags.

## Verified installed-model Cases A–H

Exact inputs are stored in `tests/before_subordinator_cases.json`.

| Case | Before correction | After correction |
|---|---|---|
| A: complete workers / before / doors sentence | `before` warning | no incomplete-subordinator event |
| B: incomplete Although / cooks | `Although` | `Although` preserved |
| C: incomplete Although / smartphones | `Although` | `Although` preserved |
| D: complete Although / library | no warning | no warning |
| E: initial Before clause plus main statement | `Before` false warning | no warning |
| F: Before the doors open. | `Before` warning | warning preserved |
| G: complete Because / plastic sentence | no warning | existing safeguard preserved |
| H: combined cafeteria Introduction | `before` and `Although` | `Although` only |

For H the remaining marker is `[229, 237)`, sentence index 3. The unchanged
FeedbackService selects `possible_incomplete_subordinator` with the message
about **Although**, not before. The existing tutor highlights only:

> Although the cooks prepare healthy meals every morning.

Six real-model variations cover different main verbs, subjects, past tense,
later sentence position and a Unicode prefix. All are warning-free after the
correction. Controlled graph tests cover insufficient evidence and prove that
the exception stays before-only. The audit compares all original linguistic
observations before and after for 15 samples (A–H, six variations and the
protected fixture); every annotation is identical.

## Fingerprints and the approved research-output pin

SHA-256 of the actual bytes of `services/introduction_rules.py`:

```text
old: ca78c2b551dd71408594b0a4d0bbf31b1a187497032139e4e30d0d6e9a90ecba
new: 4946454307c2e3bff2a3e50e4022e1bb16bfba90c8b8c2af882059dd8357e0da
```

The pin mechanism is a separate canonical JSON SHA-256 assertion at
`tests/test_nlp_transparency.py:243`, in
`test_exact_plastics_introduction_preserves_prechange_observations_and_feedback`.
It covers `analysis`, `feedback` and recorded `feedback_decisions`, including
Rule Evaluation Trace implementation source locations. It is not a file hash.

```text
previous expected: 448e642716afa25286b9202d9265aebe60b6438301ec0f0008ccf4bf05727967
approved expected: 0d1fc44a95773623b4699b86f60415cace05f6b8fe0da65c0efabf9c3837acbd
```

The protected sample's only differences are these 15 implementation line
metadata fields in `analysis.rule_evaluation_trace`. All other protected sample
data, including original feedback and feedback decisions, compares equal.

| Trace index | Field | Old | New |
|---|---|---:|---:|
| 1 | end_line | 400 | 402 |
| 3 | start_line / end_line | 402 / 432 | 464 / 494 |
| 4, 5 | start_line / end_line | 434 / 465 | 496 / 527 |
| 6, 7, 8, 11 | start_line / end_line | 467 / 616 | 529 / 678 |

Following the user's separate approval, only the expected SHA-256 value in
`tests/test_nlp_transparency.py` is changed. The original fingerprint is retained
above. All existing behavioral assertions, serialization settings and hash
verification remain in place; no assertion is removed, bypassed or weakened.

The reason for the approved baseline update is the 15 source-location metadata
changes listed above after the narrowly scoped before-only rule correction.
Recomputed differences match `protected-pin-changes.json` exactly. Original
linguistic observations, emitted Rule Events/rule evidence, FeedbackService
decisions and feedback messages remain identical. The fresh protected response
matches the saved current canonical response exactly and hashes to the approved
value. No NLP, Rule Base, feedback, or research-evidence changes are made as part
of this pin-update step.

## Commands and results

Run from `C:\Users\My Pc\Desktop\EssayScaff-V2`:

```powershell
# Before edits: 441 passed in 57.31s.
& ".venv\Scripts\python.exe" -B -m pytest tests -q -p no:cacheprovider --tb=long

# After correction: 159 passed in 13.94s.
& ".venv\Scripts\python.exe" -B -m pytest tests/test_before_subordinator_safeguard.py tests/test_subordinator_safeguard.py tests/test_introduction_rules.py tests/test_introduction_feedback_targeted.py tests/test_feedback_provenance.py -q -p no:cacheprovider --tb=long

# After correction: 13 passed, 1 failed (pin), in 15.33s.
& ".venv\Scripts\python.exe" -B -m pytest tests/test_nlp_transparency.py tests/test_research_inspector.py -q -p no:cacheprovider --tb=long

# Full after suite: 478 passed, 1 failed (pin), in 58.96s.
& ".venv\Scripts\python.exe" -B -m pytest tests -q -p no:cacheprovider --tb=long

# Passed; no browser JavaScript errors; isolated persistence counts all zero.
& ".venv\Scripts\python.exe" -B tests/transparency_browser_check.py
```

Browser checks cover the actual combined-Introduction API result, desktop and
mobile editor highlights, concern switching, real clipboard equality with Copy
Full Analysis, and teacher Research Inspector execution for the same input.
Screenshots were also visually inspected. No frontend production code was edited.

## Final verification after the authorized pin update

The full regression command was run again after the approved fingerprint
replacement:

```powershell
& ".venv\Scripts\python.exe" -B -m pytest tests -q -p no:cacheprovider --tb=long
```

Actual result: **479 passed in 58.06s; 0 failed, 0 skipped, 0 errors.**
This includes the corrected Cases A–H, true-positive protections, provenance,
transparency, persistence and protected-fingerprint tests. The before-only
correction remains intact; no rule or production code was edited in this step.

A byte comparison confirms that the pin test changed by exactly the one
approved old-to-new hash replacement, with all other bytes preserved. The only
monitored files changed during this step are the pin test and this review note.
Fresh-response verification and pre-update snapshots are stored at:

`C:\Users\My Pc\AppData\Local\Temp\opencode\approved-research-pin-g7wnte10`

## Review artifacts

Source snapshot, before/after file manifests, complete API responses, canonical
protected records, the unified code diff, and exact pin differences:

`C:\Users\My Pc\AppData\Local\Temp\opencode\before-safeguard-r0k27itq`

In particular: `introduction_rules.review.diff` and `protected-pin-changes.json`.

Browser screenshots and `verification.json`:

`C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-4354s9wk`

## Remaining limitations and unchanged components

This deliberately does not repair other POS/attachment errors or broaden the
exception beyond before-marked ADJ/JJ advcl patterns. Insufficient structure
retains conservative detection. The pre-existing `When communities reduce
plastic waste.` advmod-based missed detection documented in
`tests/test_subordinator_safeguard.py` remains outside this change. Case F is
detected by the installed model; it is not claimed as a resolved false negative.

Byte comparisons of monitored files confirm that NLPService, TopicService,
WordNet-related logic, Body and Conclusion rules, FeedbackService, Research
Inspector, Flask routes, persistence code, the tutor JavaScript/CSS/template,
prepared lessons were unchanged by the detector correction. The protected pin
test was also unchanged during that correction; its expected fingerprint alone
is now updated under the user's subsequent authorization. Dependencies and
models were not changed. No commit or push was made.
