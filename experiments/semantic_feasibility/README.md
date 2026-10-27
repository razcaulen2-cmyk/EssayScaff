# Semantic feasibility experiment

This is an isolated research pilot, not part of active NLP services or any readiness workflow. See the project README for Phase 1–2 dependencies and commands.

## Encoder choice

Candidate: `sentence-transformers/all-MiniLM-L6-v2`, public on Hugging Face, Apache-2.0 licensed. Its model card describes 22.7 million parameters, 384-dimensional sentence vectors, and truncation beyond 256 word pieces. The repository's current revision was checked as `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; the experiment pins this revision. The model is downloaded from its official Hugging Face repository at runtime.

The experiment is CPU-only and uses its own virtual environment and pinned `sentence-transformers==5.1.0` requirement. `requirements-lock.txt` captures the exact tested Windows CPU dependency versions. PyTorch and the model weights are additional downloads; this is a non-generative encoder, not a conversational model. Allow several GB of disk space for the isolated environment and package cache. The model itself is 22.7M parameters; practical memory use also includes PyTorch and tokenizer/runtime overhead.

```powershell
cd "C:\Users\My Pc\Desktop\EssayScaff-V2\experiments\semantic_feasibility"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python encoder_experiment.py
```

The encoder writes `encoder_results.json` locally. It reports topic cosine similarities, selected adjacent-sentence cosine similarities, embedding dimensions, model revision, load/encode time, and runtime versions. Scores are descriptive measurements, **not** intelligibility probabilities, confidence, truth, relevance judgments, or thresholds. The script does not classify samples.

## Interpreting the experiment

A pretrained text encoder converts text into a fixed-length vector. In this experiment, each sentence or short paragraph receives a 384-number embedding from contextual token representations. The model does not generate text and does not reason or understand language like a human.

Cosine similarity measures the angle between two vectors; for the normalized vectors used here, it is their dot product and ranges from -1 to 1. A larger score means the vectors point in a more similar direction according to this model. It does not prove that the statements are related in the way a reader intends, coherent, intelligible, or true.

Keyword-rich nonsense can produce a high topic similarity because it contains much of the same topic vocabulary and patterns. Similarity is therefore not a gibberish detector. Human labels are needed to evaluate a future intelligibility classifier because the desired outcome is a human judgment, not a property established by the embedding. False positives could treat nonsensical writing as understandable; false negatives could reject understandable writing, including imperfect or figurative student writing. Either error could cause harm if used in educational decisions, so this experiment makes no readiness decision.

Factual correctness is outside scope. No human labels or classifier predictions ship with the developer-authored samples. The evaluator reports descriptive class counts, and only calculates confusion matrices, precision, recall, F1, and false-positive/false-negative cases when actual human annotations and a separately supplied model prediction file have matching sample IDs. Held-out topic evaluation and threshold selection must be planned before any future classifier claim.

## Human annotation

Read `annotation_guide.md` first. From the project directory, run:

```powershell
python experiments\semantic_feasibility\annotate.py --reviewer-id reviewer_a
```

Completed records are stored under `experiments\semantic_feasibility\annotations\reviewer_a.jsonl` and never in the sample file. Re-running resumes by skipping only samples that reviewer has completed. The tool does not show labels from other reviewers.

`ai_diagnostic_annotations.json` is a separately maintained, provisional AI diagnostic review requested for Phase 3B. It is explicitly **not human-annotated**, not a gold label file, and not accepted by `evaluate.py` as reference data. Its labels must not be used to claim classifier accuracy.

## Combined diagnostic observations

`diagnostic_focus_terms.json` defines fixed developer-authored focus lists for transparent lexical coverage checks; these are not actual teacher-provided assignment settings. After rerunning the encoder, run the production linguistic/topic services in the main project environment to join spaCy observations, Phase 2 lexical matches, WordNet candidates, encoder similarities, and AI-provisional labels:

```powershell
cd "C:\Users\My Pc\Desktop\EssayScaff-V2"
.\.venv\Scripts\Activate.ps1
python -m experiments.semantic_feasibility.run_diagnostic_analysis
```

The resulting `diagnostic_analysis.json` stores observations for all sample IDs and explicitly warns that provisional labels are not references. It calculates only descriptive group summaries, never classification metrics.

## Evaluation

Class counts and independent reviewer agreement can be inspected without predictions:

```powershell
python experiments\semantic_feasibility\evaluate.py --annotations experiments\semantic_feasibility\annotations\reviewer_a.jsonl experiments\semantic_feasibility\annotations\reviewer_b.jsonl
```

Classification metrics are emitted only when a separately produced prediction JSONL is explicitly supplied. No classifier or predictions are bundled with this pilot, so no effectiveness metrics are currently justified.

## Potential public data (task fit and licensing)

- [GLUE CoLA task card](https://huggingface.co/datasets/nyu-mll/glue) documents 10.7k English acceptability examples (8,551 train, 1,043 validation, 1,063 test), labeled for whether a sentence is grammatical/acceptable. This is useful for a separate acceptability benchmark, not semantic intelligibility: grammaticality is not whether an idea makes sense. GLUE points users to the original task datasets' licenses; its hosted card labels the overall license as `other`, so verify the original CoLA data terms before reuse.
- [SICK resource page](https://marcobaroni.org/composes/sick.html) documents about 10,000 sentence pairs with crowdsourced relatedness ratings and entailment/contradiction/neutral labels. Its stated license is [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/). It can help study semantic relations, negation, and contradiction, but is pair-based and does not label standalone academic sentences for intelligibility; the noncommercial/share-alike terms also matter.
- GLUE's [MNLI task description](https://huggingface.co/datasets/nyu-mll/glue) provides sentence-pair entailment, contradiction, or neutral labels. That is inference between propositions, not a direct standalone intelligibility judgment, and underlying source licenses need separate checking.

These are adjacent research resources, not a verified drop-in labeled dataset for EssayScaff's target. None is downloaded or used to train a classifier in this phase.
