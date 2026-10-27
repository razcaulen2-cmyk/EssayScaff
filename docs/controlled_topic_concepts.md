# Controlled Topic Concepts — informational evidence phase

## Verified insertion point

`TopicService.analyze` parses each supplied section through `NLPService.parse`,
collects observations using `analyze_doc`, extracts noun concepts from the shared
Doc and compares prepared focus sequences using `_find_matches`. Preparation
(`prepare_teacher_context` / `_unique_focus_terms`) parses focus phrases separately,
keeping alphabetic surface words and casefolded lemmas. Direct windows take
precedence over equal lemma windows; phrase separators cannot bridge punctuation
or blank paragraphs.

Direct WordNet suggestions are disabled for Introduction/Body and enabled for
Conclusion by `EssayAnalysisService.analyze`. Separate cross-stage WordNet
comparisons occur inside Body/Conclusion Rule Bases when earlier context exists.
These paths and the installed spaCy model are unchanged.

The new `_with_related_concepts` extension reads the **already serialized** token,
lemma and sentence observations and the prepared teacher context. It does not
invoke spaCy, WordNet, stemming, synonyms or a generative/embedding model.
Existing rules read their original linguistic, confirmed lexical, concept and
coverage fields; FeedbackService reads original findings and emitted events.
None of those consumers use the new informational field.

The coordinator attaches the evidence **after** all existing rule, feedback and
evaluation-trace work, as a sibling of `analysis` and `feedback`. Flask forwards
this additive selected-stage field:

`related_topic_concept_evidence`

No existing analysis/feedback object gains a field, so protected analysis/feedback
hashes remain comparable. Source positions of the existing TopicService helpers
are also preserved because evaluation metadata serializes those locations.

## Small developer-curated resource

Source: `content/topic_concept_relations.json`, schema 1, configuration 1.0.

| Active teacher focus concept | Related concept | Approved surface forms | Relationship |
|---|---|---|---|
| environment | river | river, rivers | Natural environmental feature |
| environment | animal | animal, animals | Living organism in the environment |
| environment | forest | forest, forests | Natural environmental feature |
| environment | habitat | habitat, habitats | Environmental habitat |
| environment | ecosystem | ecosystem, ecosystems | Ecological system |
| environment | pollution | pollution, pollutions | Environmental problem |

These are developer-reviewed examples, **not WordNet-proven relationships**.
`people`, `thing`, `place`, `good`, and other broad words are not configured.
`pollute` is not automatically equated with `pollution`.

Each relation requires `id`, `focus_concept`, `related_concept`,
`relationship_type`, and `relationship_label`. Optional `surface_forms` must be
an explicit unique list of lowercase single words containing the base concept.
No regex, suffix rule, alias generation or WordNet expansion is applied.

The installed model can preserve capitalized plurals as proper-noun lemmas.
Approved surface forms handle those limited cases without altering NLP output.
Evidence preserves the actual spaCy lemma and distinguishes `spacy_lemma` from
`configured_surface_form` normalization.

## Scope and algorithm

1. Load and validate one configuration snapshot per TopicService instance.
   Resource edits require restarting/reconstructing the analysis service.
2. Require `focus_source == teacher_provided`. Automatic topic-derived
   candidates do not activate this feature in this conservative initial phase.
3. Compare **complete prepared normalized focus phrases** with configured keys.
   `environment` activates the initial mapping; `natural environment` or
   `environmental protection` does not activate it by substring. Explicit
   multiword focus mappings can be added to the same schema later.
4. For each alphabetic serialized token, compare its casefolded existing lemma
   and explicitly configured casefolded surface forms with active mappings.
5. Emit one record per distinct span/relationship ID. Matching both lemma and
   surface does not double-count that relationship. Repeated mentions retain
   separate spans. No noun-chunk duplication is introduced.
6. Preserve token index, original text, base concept, actual spaCy lemma,
   normalization method, Python `[start,end)` offsets and recorded sentence index.
   Resource path, version, SHA-256 and relation ID make the lookup reviewable.

Separate summary measures:

- unique related concept lemmas;
- distinct source occurrences (span count);
- relationship records (one occurrence could link to multiple explicitly
  configured future focus concepts);
- original teacher terms and normalized focus concepts with evidence.

No counts are merged into existing direct/lemma focus coverage.

## Execution states

| execution_status | Meaning |
|---|---|
| EXECUTED / reason MATCHES_OBSERVED | Active mapping scanned, mentions found |
| EXECUTED / reason NO_MATCHES | Active mapping scanned successfully, no mentions |
| NOT_APPLICABLE | No explicit teacher focus, or no complete approved focus key |
| RESOURCE_UNAVAILABLE | File could not be read; not a successful no-match result |
| CONFIGURATION_INVALID | Invalid JSON/schema/record, duplicate ID/pair/JSON field, or ambiguous surface form; whole resource rejected |

Empty coordinator text can produce EXECUTED/NO_MATCHES with an active mapping;
the existing HTTP route continues to reject empty/whitespace selected writing.
Missing fields in older cached responses display NOT_RECORDED, never inferred zero.

## Dashboard and copy

The existing eight horizontal main tabs remain. Topic Matching adds **Related
Topic Concepts** alongside direct, lemma and WordNet views, with WHAT/HOW/WHY/WHERE,
separate counts, resource/execution status, real evidence rows, active approved
relationships and expandable full provenance. The call map labels this as an
informational side branch not consumed by rules or feedback.

`buildFullAnalysisReport` copies the same root evidence field and explanations;
its complete-evidence index exposes the same record. Neither navigation,
disclosure nor copying calls an analyzer. Existing stale-draft guards remain.

## Interpretation and future review

"No rivers or animals are mentioned" still contains lexical mentions. Related
words do not demonstrate agreement, environmental protection, relevance in
context, a complete sentence, a valid argument or semantic understanding.
Grammatical rules and all five feedback messages/priorities are independent.

Potential future integration could evaluate this evidence for revised topic
feedback, but **no current rule, feedback branch, score or eligibility decision
uses it**. Teacher-controlled per-assignment mapping administration is deferred.

## Verification commands

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tests/transparency_browser_check.py
```

The tests use temporary databases/configurations and synthetic users. Existing
student records are not modified. The original protected Introduction hash was
`78811fc86728b7643ee155eeb260921d136635b4602373af5e57abe853b7f6de`; after the
authorized 2026-10-19 documentation-only correction of the incomplete-
subordinator rule description (see `docs/s5_1_direct_feedback.md` §F), the
pinned protected hash became
`c73bd8844acd37c69007f0fc54741f84de33ee7c3619882d0156845f229aba6b`. After the
authorized 2026-10-19 Introduction subordinator false-positive safeguard (see
`docs/s5_1_direct_feedback.md` §I), which changed only the subordinator rule's
`condition`, `configuration`, and implementation `start_line`/`end_line`
metadata (17 paths; analysis results byte-identical after stripping those
fields), the pinned protected hash is now
`448e642716afa25286b9202d9265aebe60b6438301ec0f0008ccf4bf05727967`.

## Verified implementation results (2026-10-19)

- Baseline: 301 passed. Full regression after implementation: **368 passed**,
  0 failures, 0 skips (89.57 s). Final focused checks after mobile-table polish:
  **75 passed** (19.44 s). JavaScript syntax checks passed.
- Environmental Protection Introduction: unchanged 27 tokens, 24 alphabetic
  tokens, 2 sentences, 23 editor words, 3 unique direct/lemma focus terms,
  4 direct occurrences, 0 lemma-only occurrences, 7 emitted events and 14
  reconstructed evaluations. All five feedback fields and protected hash pass
  unchanged. `environment` remains unmatched under direct/lemma coverage.
- New evidence: `rivers` → `river`, `[134,140)`, relation
  `environment.river.v1`; `animals` → `animal`, `[150,157)`, relation
  `environment.animal.v1`. Both are in sentence index 1 (sentence 2) and use the
  actual spaCy lemmas. Two distinct concepts, two occurrences, one linked focus.
- Actual Chrome 155.0.8059.80 verified all 8 main / 45 sub-tabs, desktop
  1440×1000 and mobile 390×844, all A–G examples, real table/API spans,
  clipboard/report agreement, no rerun on navigation/copy, stale invalidation,
  Body/Conclusion evidence and Teacher Research Inspector operation. No recorded
  JavaScript errors. Isolated database: 0 drafts, 0 revisions, 0 submissions.
- Latest screenshots and `verification.json`:
  `C:\Users\My Pc\AppData\Local\Temp\opencode\essayscaff-transparency-pq2gx_11`.
  In particular, inspect `desktop-related-topic-concepts.png` and
  `mobile-related-topic-concepts.png`.

Ready for informational user manual testing. Rule/feedback integration remains
deferred for review.
