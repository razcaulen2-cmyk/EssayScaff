# EssayScaff V2 — Phase 2 lexical topic evidence

A small standalone experiment that extracts linguistic observations and explainable lexical topic evidence from English student writing. It does not assess essay quality, generate writing, or determine whether a sentence is meaningful or factually true.

## Requirements and installation (Windows PowerShell)

Python 3.11 is the tested runtime. spaCy 3.7.5, pytest 8.3.5, and NLTK 3.9.2 are pinned in `requirements.txt`; Click is included for spaCy's model-download command.

```powershell
cd "C:\Users\My Pc\Desktop\EssayScaff-V2"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('wordnet')"
```

The English model is installed separately because it is a spaCy model package, not a dependency resolved by this small requirements file. The service loads the model once when an `NLPService` instance is created and reuses that instance for each analysis.

WordNet suggestions use the NLTK WordNet corpus. If it is not installed or is unavailable, the report marks WordNet as unavailable and returns no suggestions; direct and normalized matching continue to work.

## Run the CLI

```powershell
python cli.py "Social media affects students' concentration because they sleep less."
python cli.py
python cli.py --topic "Effects of late-night social media use on classroom attention" --focus-term "social media" --focus-term students --focus-term sleep "Social media affects students' concentration because they sleep less."
```

Supply text as a quoted command-line argument, or omit it to enter a paragraph interactively. `--topic` turns on lexical topic analysis and each `--focus-term` supplies one authoritative teacher phrase; with a topic but no focus terms, conservative candidate terms are extracted from the topic. Output is JSON. Token count includes punctuation tokens but excludes whitespace. Offsets are zero-based character positions with an exclusive end, measured against the original input; sentence spans exclude surrounding whitespace.

## Run the writing workspace

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser. During registration, choose Student or Teacher; both use the same login page. Teachers can also be created locally with `python create_teacher.py`, which prompts for and hides the password. Teachers can create assignments; students see them only in classrooms they have joined, alongside Free Writing / Practice. Each student has a separate writing session for each assignment. Passwords are stored as Werkzeug hashes. The first run creates a persistent secret key in the ignored `instance/.flask_secret_key` file; do not commit it. **Save Draft** stores the active session; **Save Revision** saves an immutable snapshot. Drafts are not saved automatically. Older drafts created before accounts remain unowned and are preserved without being assigned to any student. This localhost prototype is not a secure public multiuser service. The interface does not rewrite student writing or assess meaning, correctness, or essay quality.

Teachers can open **NLP Research Inspector** from the Teacher Workspace navigation. The inspector accepts custom samples for Introduction, Body, and Conclusion, optionally including prior sections for cross-stage comparisons. It reuses the active analysis coordinator, displays actual returned evidence and optional in-process timings, and does not save samples to writing sessions, revisions, or submissions. The isolated semantic-feasibility experiment and evaluation utilities are shown as separate research workflows, not as production NLP steps.

## Run tests

```powershell
python -m pytest -v
```

Tests run the actual `en_core_web_sm` pipeline. No statistical accuracy claim is made.

## What the analysis fields mean

For the input **“Social media affects students' concentration because they sleep less.”**, spaCy processes the text into one `Doc`. Tokenization splits it into token units (including punctuation); the analyzer reports those tokens and counts alphabetic tokens separately from all tokens. Lemmatization maps inflected forms to dictionary-like base forms (for example, “affects” to “affect” and “students” to “student”). Part-of-speech (POS) tagging assigns model labels such as `NOUN`, `VERB`, `PRON`, and `ADV`. Dependency parsing labels grammatical relationships between tokens; the result can report parser-labeled subjects, objects, or complements when present. Sentence boundaries, tokens, and noun phrases are all derived from that same parsed `Doc`.

These are linguistic observations, not semantic understanding. A grammatical dependency structure does not establish that a sentence makes sense: “classroom attention drink invisible clocks” may still receive token, POS, and dependency labels. Similarly, the analyzer cannot prove the factual truth of a statement about social media and sleep. Phase 1 deliberately provides no meaning score, quality judgment, or readiness decision.

## Scope

## Phase 2 lexical evidence

`TopicService` extracts candidate concepts from noun phrases and noun/proper-noun tokens, groups repeated occurrences by their lemma-normalized form, and preserves each occurrence's surface text, character span, source token indices, POS, and extraction method. Teacher focus phrases are deduplicated by normalized form. Exact case-insensitive word/phrase matches are reported as direct; matching lemmas with different surface forms are reported as normalized. Phrase words must occur consecutively in the student's lexical token sequence; punctuation such as hyphens and possessive apostrophes is ignored between tokens, and the evidence span retains the original punctuation.

Confirmed matches determine observed/unobserved focus coverage. WordNet suggestions are separate, conservative candidates: a single-word focus term and a single-word student concept must share exactly one synset. The report includes that synset ID and marks the possibility as contextually uncertain. Suggestions never increase confirmed coverage. WordNet does not determine which sense is used in a sentence.

Student concepts are grammatical lexical candidates, not guaranteed important ideas. Topic-derived candidates are explicitly marked as automatic when teachers do not supply a focus list. Neither concept extraction nor keyword coverage establishes relevance, semantic intelligibility, explanation quality, or factual accuracy. Meaningful and nonsensical text can have similar lexical evidence; this phase makes no educational judgment.

The browser interface provides one editor for each selected writing stage, simple draft persistence and read-only revision snapshots. It has no essay scoring or semantic classification.

## Phase 3A feasibility experiments

The isolated pilot, manually labeled diagnostic samples, reviewer annotation tool, and non-generative sentence-encoder experiment are in `experiments/semantic_feasibility/`. The encoder output is experimental only: its cosine similarities are not intelligibility judgments and are not connected to the Phase 2 service or any readiness workflow. See that directory's README and `annotation_guide.md` before annotating.
