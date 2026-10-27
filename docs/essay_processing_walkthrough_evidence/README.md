# Essay Processing Walkthrough — Evidence

This directory contains the screenshots and saved response data for [`docs/essay_processing_walkthrough.md`](../essay_processing_walkthrough.md).

## Provenance

| Item | Value |
|---|---|
| Captured | `2026-10-26T01:11:21.002Z` |
| Viewport | 1440 × 1000 |
| Capture source | [`tests/process_walkthrough_capture.cjs`](../../tests/process_walkthrough_capture.cjs) |
| Launcher | [`tests/process_walkthrough_capture.py`](../../tests/process_walkthrough_capture.py) |
| Analysis requests | 3 |
| Write requests | 0 |
| Screenshots captured | 34 |
| Screenshots used as figures | 28 |
| JavaScript errors | 0 |
| Isolated database | Temporary SQLite file; the real application database was not opened |
| Isolated `writing_sessions` | 0 |
| Isolated `writing_revisions` | 0 |
| Isolated `submissions` | 0 |

The capture used a temporary Flask server, a temporary SQLite database, the isolated account `walkthrough_student`, and an isolated Chrome profile. No real student record was read or modified. No draft, revision, or submission was written.

## Sample

**Assignment topic**

> Should communities reduce their use of single-use plastics?

**Focus terms**

> single-use plastics, communities, reduce, environment

**Introduction**

> Single-use plastics are everywhere in our communities. Communities should reduce their use of these plastics because they can pollute rivers and harm animals.

**Body**

> Communities can reduce single-use plastics by carrying reusable bags. Reusable bags reduce waste in rivers.
>
> Plastic containers harm animals. Communities can protect animals by using reusable containers.

**Conclusion**

> In conclusion, communities should reduce single-use plastics. Reusable bags and containers can protect rivers and animals.

## Files

### Response data

| File | Description |
|---|---|
| [`introduction-response.json`](introduction-response.json) | Full recorded response for the Introduction analysis. |
| [`body-response.json`](body-response.json) | Full recorded response for the Body analysis. |
| [`conclusion-response.json`](conclusion-response.json) | Full recorded response for the Conclusion analysis. |
| [`walkthrough-capture.json`](walkthrough-capture.json) | Metadata emitted by the capture script. Some tutor-frame stage/process labels in this file are stale; use `screenshots.json` for the curated mapping. |

### Manifests

| File | Description |
|---|---|
| [`screenshots.json`](screenshots.json) | 34 captured frames with byte counts, SHA-256 hashes, figure numbers, used/unused status, stage, process, status, and notes. |
| [`walkthrough-verification.json`](walkthrough-verification.json) | Isolated-run verification: request counts, zero writes, zero JS errors, zero isolated rows, sample texts, and figure count. |

### Figures (28)

| Figure | File |
|---:|---|
| 1 | [`01-practice-setup.png`](01-practice-setup.png) |
| 2 | [`03-technical-inspector-overview.png`](03-technical-inspector-overview.png) |
| 3 | [`04-pipeline-map.png`](04-pipeline-map.png) |
| 4 | [`05-focus-preparation.png`](05-focus-preparation.png) |
| 5 | [`06-focus-normalization.png`](06-focus-normalization.png) |
| 6 | [`07-tokenization.png`](07-tokenization.png) |
| 7 | [`08-pos.png`](08-pos.png) |
| 8 | [`09-dependencies.png`](09-dependencies.png) |
| 9 | [`10-lemmas.png`](10-lemmas.png) |
| 10 | [`11-sentences.png`](11-sentences.png) |
| 11 | [`12-noun-phrases.png`](12-noun-phrases.png) |
| 12 | [`13-concepts.png`](13-concepts.png) |
| 13 | [`14-focus-matching.png`](14-focus-matching.png) |
| 14 | [`15-wordnet-skipped.png`](15-wordnet-skipped.png) |
| 15 | [`16-related-words.png`](16-related-words.png) |
| 16 | [`18-stage-rule-checks.png`](18-stage-rule-checks.png) |
| 17 | [`20-rule-events.png`](20-rule-events.png) |
| 18 | [`21-feedback-decision.png`](21-feedback-decision.png) |
| 19 | [`22-feedback-fields.png`](22-feedback-fields.png) |
| 20 | [`23-trait-mapping.png`](23-trait-mapping.png) |
| 21 | [`24-highlight-evidence.png`](24-highlight-evidence.png) |
| 22 | [`25-api-rendering.png`](25-api-rendering.png) |
| 23 | [`27-introduction-tutor.png`](27-introduction-tutor.png) |
| 24 | [`28-body-tutor.png`](28-body-tutor.png) |
| 25 | [`30-body-cross-stage.png`](30-body-cross-stage.png) |
| 26 | [`31-conclusion-tutor.png`](31-conclusion-tutor.png) |
| 27 | [`32-conclusion-cross-stage.png`](32-conclusion-cross-stage.png) |
| 28 | [`34-conclusion-highlight.png`](34-conclusion-highlight.png) |

### Supplemental captures (not figures)

| File | Reason |
|---|---|
| [`02-introduction-editor.png`](02-introduction-editor.png) | Pre-analysis placeholder; redundant with Figure 1. |
| [`17-cross-stage-introduction.png`](17-cross-stage-introduction.png) | Clean earlier-section “not applicable” state; explained in text. |
| [`19-sentence-connection-review.png`](19-sentence-connection-review.png) | Clean empty review state. |
| [`26-technical-trace.png`](26-technical-trace.png) | Presentation defects: concatenated step summaries, `[object Object]`, “Not recorded” model/version fields. |
| [`29-body-topic-sentences.png`](29-body-topic-sentences.png) | Per-candidate details incomplete (“Reason not recorded” / “Start not recorded”). |
| [`33-conclusion-new-material.png`](33-conclusion-new-material.png) | Repeated unlabeled “Not available” rows; zero counts are stated in the walkthrough text. |

## Reproduce

From the repository root:

```bat
.venv\Scripts\python.exe tests\process_walkthrough_capture.py
```

The launcher starts a temporary server and database, captures the frames, and asserts that the isolated persistence tables remain empty. Do not run it against the real database.

## Integrity

Every screenshot entry in [`screenshots.json`](screenshots.json) includes a SHA-256 hash. Verify a file on Windows with:

```bat
certutil -hashfile docs\essay_processing_walkthrough_evidence\01-practice-setup.png SHA256
```

Compare the output with the `sha256` value in the manifest.

## Scope

This evidence set was produced without migrating or modifying the real database, enabling production writing-time tracking, writing test data to the real database, modifying student records, changing application code, or committing, pushing, or deploying.
