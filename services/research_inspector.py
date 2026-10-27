"""Technical, source-linked metadata for the teacher-only Research Inspector.

This module describes the active implementation and packages already-computed
analysis outputs. It does not run NLP, WordNet, or a Rule Base.
"""

from __future__ import annotations

import importlib
import inspect
import json
import platform
import sqlite3
from importlib import metadata
from functools import lru_cache
from pathlib import Path
from typing import Any


PROCESS_ORDER = [
    "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11"
]


def _process(
    process_id: str,
    title: str,
    simple: str,
    technical: str,
    why: str,
    how: str,
    actual_input: str,
    actual_output: str,
    decision: str,
    implementation: str,
    reference: str,
    limitation: str,
    next_process: str,
    *,
    workflow: str = "analysis",
) -> dict[str, Any]:
    return {
        "id": process_id,
        "title": title,
        "workflow": workflow,
        "sections": {
            "A. What is this process?": {"simple": simple, "technical": technical},
            "B. Why is it necessary?": why,
            "C. How does it work?": how,
            "D. Actual input": actual_input,
            "E. Actual output": actual_output,
            "F. What decision was made?": decision,
            "G. Implementation / source code": implementation,
            "H. Reference / theoretical basis": reference,
            "I. Known limitations": limitation,
            "J. What happens next?": next_process,
        },
    }


PROCESS_CATALOG = [
    _process(
        "00", "Complete Pipeline",
        "A map of the operations that produced the selected stage's feedback.",
        "An ordered request-to-response dataflow view. It separates executed stages from optional or separate workflows.",
        "It helps distinguish production operations from storage and offline research utilities.",
        "The student API validates a request, prepares assignment context, parses each supplied section, computes lexical evidence, runs supplied-stage Rule Bases, generates feedback, and returns JSON. The Research Inspector endpoint follows the same coordinator without assignment/session IDs.",
        "Stage request plus selected text, optional prior sections, assignment topic, and focus terms.",
        "Stage analysis, feedback, provenance, and optional trace timings collected during the same run.",
        "A diagram status is taken from this trace. Missing trace entries are shown as not instrumented, not inferred as executed.",
        "app.py:analyze_payload; services/essay_analysis_service.py:EssayAnalysisService.analyze; services/topic_service.py:TopicService.analyze.",
        "The implementation call chain is authoritative. spaCy pipeline documentation describes spaCy component execution, not EssayScaff's application rules.",
        "Timing excludes browser network transfer and rendering unless separately measured in the browser. Storage and evaluation are not per-analysis NLP stages.",
        "Select any diagram stage to inspect its ten-part explanation and evidence.",
    ),
    _process(
        "01", "Request & Validation",
        "The server checks who is asking and whether the submitted analysis request is shaped correctly.",
        "Flask request middleware performs session/account role authorization and CSRF validation before the endpoint validates JSON, stage, field types, and size limits.",
        "Validation prevents malformed requests; role/assignment authorization protects assignment context.",
        "POST JSON is checked for an allowed stage, non-empty topic and selected text, topic max 500 characters, Introduction/Conclusion max 12,000, Body max 30,000, at most 20 focus terms of 120 characters each, and string-only prior-section context. The Flask request body limit is 256 KiB. Student assignment IDs resolve through the enrolled, active assignment query. Inspector samples cannot contain assignment/session/user IDs.",
        "HTTP POST JSON: stage_id, assignment_topic, focus_terms, the selected stage text, and optional Introduction/Body context. CSRF is in X-CSRF-Token.",
        "Validated values passed to EssayAnalysisService; errors return HTTP 4xx/5xx JSON.",
        "The server route determines accepted fields and access scope; browser validation is only a convenience.",
        "app.py:create_app.require_account; app.py:create_app.require_csrf_token; app.py:analyze_stage; app.py:analyze_research_inspector; app.py:analyze_payload.",
        "Flask request handling documentation; implementation-specific validation and limits are in app.py.",
        "The Research Inspector deliberately accepts custom samples only and does not read a student's saved writing.",
        "Validated text and context go to assignment context preparation and the analysis coordinator.",
    ),
    _process(
        "02", "spaCy Processing",
        "spaCy turns each supplied text into words, sentences, grammatical labels, and spans.",
        "The loaded en_core_web_sm Language object tokenizes input and runs its enabled statistical/rule-based pipeline components on a Doc.",
        "One Doc supplies the observations reused by lexical matching and stage rules, avoiding a duplicate full-text parse inside each Rule Base.",
        "NLPService.parse calls self.nlp(text). NLPService.analyze_doc serializes tokens, sentence segments, dependency data, and noun chunks from that Doc. TopicService also extracts concepts from the same Doc.",
        "A Python str for each supplied section. Each full section is passed to spaCy once by TopicService in the coordinator path. Focus phrases are separately passed through spaCy during context normalization.",
        "Token/sentence spans, lemmas, POS/tags, dependency/head labels, subjects/complements, counts, and noun phrases.",
        "The outputs are statistical annotations; they are not a semantic-validity or correctness decision.",
        "services/nlp_service.py:NLPService.__init__, parse, analyze_doc, _token_data; services/topic_service.py:TopicService.analyze.",
        "Official spaCy processing-pipeline and Token API documentation.",
        "Parser, tagger, and NER predictions can be wrong. NER runs in the configured pipeline, but EssayScaff does not consume entity labels.",
        "TopicService uses this same Doc for candidate concept extraction and focus phrase matching.",
    ),
    _process(
        "03", "Concept Extraction",
        "The system collects noun phrases and noun-like words as candidate concepts.",
        "TopicService iterates Doc.noun_chunks and NOUN/PROPN tokens, lemmatizes their words, groups by normalized form, and preserves source occurrences.",
        "Candidate concepts support Body paragraph recurrence and cross-stage lexical comparison.",
        "Each candidate is converted to a space-joined lowercase lemma form. Same normalized forms share a concept record; duplicate extraction of the same span is suppressed, while distinct occurrences remain.",
        "The already parsed spaCy Doc, including noun chunks and token lemmas/POS.",
        "Student concepts with normalized form, original occurrence, POS list, span, source token indices, extraction method, and occurrence count.",
        "There is no concept ranking or confidence score. A candidate is not guaranteed to be an important idea.",
        "services/topic_service.py:TopicService._extract_concepts; services/body_rules.py:_concepts_in_span; services/conclusion_rules.py:_body_paragraph_concepts.",
        "spaCy Doc.noun_chunks and Token lemma/POS documentation describes the source annotations; concept grouping is EssayScaff-specific.",
        "Noun-phrase extraction misses non-nominal ideas and may treat generic nouns as concepts.",
        "Topic matching compares configured terms; Body and Conclusion use concepts in recurrence and cross-stage comparisons.",
    ),
    _process(
        "04", "Topic Matching",
        "The system checks whether configured focus words occur in the student's text.",
        "TopicService scans windows over alphabetic spaCy tokens and compares surface forms first, then lemma sequences, preserving source spans.",
        "These records support lexical coverage reporting and stage feedback conditions.",
        "Focus terms are normalized to lemma sequences. Candidate windows must be consecutive alphabetic tokens; between tokens the implementation permits only characters matching [\\s'’\\-‐‑–]* (whitespace, straight/curly apostrophe, and the configured hyphen/dash forms). A comma, period, or other punctuation prevents the phrase from matching across it. Punctuation is outside the matched token span.",
        "Normalized focus-term records and the student's Doc text/tokens.",
        "Per-focus direct and normalized match lists, observed/unobserved coverage, and actual spans.",
        "Only direct and lemma-normalized matches count as confirmed lexical coverage. No match is not an off-topic decision.",
        "services/topic_service.py:prepare_teacher_context, _unique_focus_terms, _find_matches.",
        "The exact/lemma matching algorithm is project-specific; spaCy documents the token and lemma annotations it consumes.",
        "Paraphrases may be missed; generic focus terms may match unrelated ideas; lexical overlap does not prove relevance.",
        "Stage Rule Bases consume focus coverage and match spans.",
    ),
    _process(
        "05", "WordNet Processing",
        "When enabled, NLTK looks up words in WordNet and EssayScaff compares synset identifiers.",
        "TopicService direct suggestions and stage_evidence cross-stage suggestions are separate optional paths.",
        "The implementation can surface a lexical relationship candidate when exact/lemma overlap is absent or when comparing stage concepts.",
        "The code requires single-word concepts, compatible mapped POS, different words/forms, and exactly one shared synset. It does not disambiguate senses in sentence context.",
        "Single-word focus/concept lemmas and POS; or single-word concepts from two supplied stages.",
        "Candidate pairs with a synset ID, or an explicit disabled/resource-missing/available status.",
        "Introduction TopicService direct suggestions are disabled. Body/Conclusion cross-stage comparison may still query WordNet.",
        "services/topic_service.py:_wordnet_status, _wordnet_suggestions; services/stage_evidence.py:_wordnet_candidates.",
        "NLTK WordNet API documentation and Princeton WordNet documentation describe synsets and lexical relations.",
        "A shared synset does not show the same contextual sense; an absent candidate does not show unrelated meaning.",
        "Suggestions are displayed separately from confirmed lexical coverage and may be included in rule evidence.",
    ),
    _process(
        "06", "Rule Execution",
        "The selected stage's code checks structural and lexical patterns in the already-built analysis.",
        "A deterministic Rule Base derives stage-specific observations from spaCy and TopicService output; it does not run another semantic model.",
        "The current rules provide evidence objects used by stage feedback.",
        "Rules use returned spans, tags, POS, dependencies, paragraph boundaries, focus matches, concept recurrence, and cross-stage lexical comparisons. Body/Conclusion cross-stage comparison may call WordNet from inside the Rule Base. Thresholds and alternatives are shown per rule.",
        "One stage analysis object and optional prior-stage analysis objects.",
        "rule_evidence plus Research Inspector decision records derived from the same returned result fields.",
        "Events emitted by the current Rule Base are marked triggered. A missing event is marked not recorded unless a returned condition explicitly establishes its outcome.",
        "services/introduction_rules.py; services/body_rules.py; services/conclusion_rules.py; services/stage_evidence.py.",
        "Each rule is a local EssayScaff heuristic. External writing references support the criterion, not the condition or threshold.",
        "Rules do not validate semantics, logic, factual accuracy, rhetoric, or readiness.",
        "FeedbackService selects messages using the resulting findings and events.",
    ),
    _process(
        "07", "Feedback Decisions",
        "FeedbackService chooses short messages from the stage findings.",
        "A deterministic priority branch selects the Primary Feedback and Next Step; other conditions populate lists and provenance.",
        "This turns observed evidence into concise feedback without generating replacement writing.",
        "The five-stage feedback functions inspect actual analysis fields and rule IDs. Provenance links selected fields to matching emitted rule events.",
        "A completed stage analysis and its emitted rule events.",
        "Current Goal, Primary Feedback, What's Working, Needs Attention, Next Step, and Feedback Provenance.",
        "Only branches recorded in current feedback outputs can be stated as selected. Hidden candidate rankings are not available.",
        "services/feedback_service.py:generate, generate_body, generate_conclusion.",
        "Hattie & Timperley (2007) and Knight et al. (2020) inform formative-feedback design generally; they do not validate these messages.",
        "A chosen message may inherit limitations or lexical overbreadth from its source heuristic.",
        "The server returns feedback JSON; the frontend renders its five fields and provenance.",
    ),
    _process(
        "08", "API & Rendering",
        "Flask returns JSON, then the browser displays feedback and analysis evidence.",
        "The student app and research inspector make authenticated fetch requests, parse JSON, and render using DOM text nodes.",
        "Rendering exposes the server's recorded outputs to the relevant user.",
        "The API returns stage_id, availability, analysis, feedback, interpretation_limit, and (in inspector mode) research_trace. The browser displays a trace without rerunning analysis when another process tab is selected.",
        "The selected API result and authorized inspector metadata.",
        "Feedback panels, process explanations, tables, rule evidence, glossary, references, and optional raw JSON.",
        "Client-only render time is measured with performance.now and is labeled separately from server timings.",
        "app.py:analyze_payload; static/app.js:renderNlpTransparency; static/research_inspector.js.",
        "Flask and browser DOM APIs; user-controlled text is inserted with textContent.",
        "No browser automation is run by this process; safe server output still needs browser review.",
        "Rendered output does not persist the essay or trace.",
    ),
    _process(
        "09", "Storage & Workflow",
        "Draft saving, revisions, submissions, and teacher progress are separate from analysis.",
        "DraftStore stores sessions and revision/submission snapshots with ownership and assignment keys.",
        "Persistence supports the writing workflow; it is not a step in the NLP pipeline.",
        "Save Draft writes a session; Save Revision creates a snapshot; Submit checks a saved assigned draft and snapshots its sections. Analyze does not save writing.",
        "Authenticated route payloads and, for workspace access, authorized session/assignment references.",
        "SQLite rows in writing_sessions, writing_revisions, or submissions only when their separate routes run.",
        "This process status is NOT_APPLICABLE for an analysis request unless that request explicitly resolves an assignment ID.",
        "services/draft_store.py; app.py draft/revision/submission routes; static/app.js save/submit handlers.",
        "SQLite and Flask implementation; the schema is in DraftStore.__init__.",
        "Submission establishes persistence, not essay quality. Research Inspector custom samples are not saved.",
        "Teacher progress views query saved work and submissions separately.",
        workflow="separate_workflow",
    ),
    _process(
        "10", "Research Evaluation",
        "Evaluation compares model predictions with independently collected human reference labels.",
        "The isolated evaluator can calculate reviewer agreement and classification metrics for matching sample IDs.",
        "It would be necessary to estimate criterion-specific performance, but it is not called by normal analysis.",
        "Human annotation records must have human provenance. A separate model prediction file and selected reference reviewer are required for confusion matrix and precision/recall/F1.",
        "No human reference annotations or aligned predictions are currently present.",
        "Evaluation pending; no valid confusion matrix or performance metric is available.",
        "Not executed in production analysis. No counts or percentages are fabricated.",
        "experiments/semantic_feasibility/evaluate.py; experiments/semantic_feasibility/annotate.py.",
        "Evaluation formulas are standard definitions; the local evaluator enforces provenance and ID alignment.",
        "The 31 diagnostic examples and 31 provisional AI labels are not human gold labels.",
        "A valid future result can be reviewed separately from a per-essay trace.",
        workflow="separate_workflow",
    ),
    _process(
        "11", "References & Raw Trace",
        "This section provides the source-linked technical record and the supporting references.",
        "The raw trace serializes only the authorized custom sample's analysis outputs and metadata; the reference catalogue separates implementation facts from literature.",
        "It supports reproducibility and thesis explanation without implying validation.",
        "The trace is packaged during the same analyzer call. Copy/export serializes only the current inspector response, not cookies, database rows, or other students' work.",
        "Current authorized inspector response, process/rule metadata, and verified citations.",
        "Expandable JSON and a downloadable JSON file generated in browser memory.",
        "References document concepts; source code remains authoritative for actual execution.",
        "services/research_inspector.py; static/research_inspector.js; docs/feedback_rule_references.md.",
        "External source links are included with statements of scope and limitations.",
        "Literature cited for general design does not empirically validate EssayScaff-specific heuristics.",
        "Copy or download only the currently displayed custom sample trace.",
    ),
]


REFERENCES = [
    {
        "id": "spacy-pipelines",
        "category": "Technical documentation",
        "author": "spaCy project",
        "year": "n.d. (spaCy v3.7 documentation)",
        "title": "Language Processing Pipelines",
        "publication": "spaCy Usage Documentation",
        "url": "https://spacy.io/usage/processing-pipelines",
        "supports": "Pipeline execution order, component roles, tokenizer distinction, and Doc processing.",
        "does_not_prove": "It does not describe EssayScaff's custom rule thresholds or validate its outputs.",
    },
    {
        "id": "spacy-token",
        "category": "Technical documentation",
        "author": "spaCy project",
        "year": "n.d. (spaCy v3.7 documentation)",
        "title": "Token API",
        "publication": "spaCy API Reference",
        "url": "https://spacy.io/api/token",
        "supports": "Token attributes including text, lemma, POS, tag, dependency, head, index, and character offset.",
        "does_not_prove": "A Token attribute is a model annotation, not a guarantee of correct grammar or meaning.",
    },
    {
        "id": "nltk-wordnet",
        "category": "Technical documentation",
        "author": "NLTK Project",
        "year": "2025 (NLTK 3.9.2 documentation)",
        "title": "Sample usage for WordNet",
        "publication": "NLTK Documentation",
        "url": "https://www.nltk.org/howto/wordnet.html",
        "supports": "synsets(), POS filtering, synset names, and WordNet relationship API examples.",
        "does_not_prove": "It does not validate EssayScaff's exactly-one-shared-synset heuristic or contextual sense selection.",
    },
    {
        "id": "princeton-wordnet",
        "category": "Technical documentation",
        "author": "Princeton WordNet",
        "year": "n.d.",
        "title": "WordNet: A Lexical Database for English",
        "publication": "Princeton University",
        "url": "https://wordnet.princeton.edu/",
        "supports": "WordNet synsets, senses, and lexical/semantic relations as a lexical database.",
        "does_not_prove": "A shared synset candidate does not identify the intended sense in student context.",
    },
    {
        "id": "hattie-timperley",
        "category": "Educational research",
        "author": "Hattie, J., & Timperley, H.",
        "year": 2007,
        "title": "The Power of Feedback",
        "publication": "Review of Educational Research, 77(1), 81–112",
        "doi": "10.3102/003465430298487",
        "url": "https://doi.org/10.3102/003465430298487",
        "supports": "General feedback-for-learning concepts.",
        "does_not_prove": "It does not establish that EssayScaff messages or outcomes are effective.",
    },
    {
        "id": "knight-acawriter",
        "category": "Educational research",
        "author": "Knight, S., Shibani, A., Abel, S., Gibson, A., & Ryan, P.",
        "year": 2020,
        "title": "AcaWriter: A Learning Analytics Tool for Formative Feedback on Academic Writing",
        "publication": "Journal of Writing Research, 12(1), 141–186",
        "doi": "10.17239/jowr-2020.12.01.06",
        "url": "https://doi.org/10.17239/jowr-2020.12.01.06",
        "supports": "Related formative-feedback and writing-analytics design context.",
        "does_not_prove": "EssayScaff does not reuse AcaWriter code, and the article does not validate EssayScaff rules.",
    },
    {
        "id": "witte-faigley",
        "category": "Educational research",
        "author": "Witte, S. P., & Faigley, L.",
        "year": 1981,
        "title": "Coherence, Cohesion, and Writing Quality",
        "publication": "College Composition and Communication, 32(2), 189–204",
        "doi": "10.58680/ccc198115912",
        "url": "https://doi.org/10.58680/ccc198115912",
        "supports": "Research context around cohesion/coherence and writing quality constructs.",
        "does_not_prove": "It does not validate lexical-overlap continuity as a measure of coherence.",
    },
    {
        "id": "unc-thesis",
        "category": "Institutional writing guidance",
        "author": "UNC Writing Center",
        "year": "n.d.",
        "title": "Thesis Statements",
        "publication": "The University of North Carolina at Chapel Hill Writing Center",
        "url": "https://writingcenter.unc.edu/tips-and-tools/thesis-statements/",
        "supports": "A thesis as a claim/interpretation that responds to an assignment prompt.",
        "does_not_prove": "It does not support using a parser-labeled clause as a thesis detector.",
    },
    {
        "id": "unc-paragraphs",
        "category": "Institutional writing guidance",
        "author": "UNC Writing Center",
        "year": "n.d.",
        "title": "Paragraphs",
        "publication": "The University of North Carolina at Chapel Hill Writing Center",
        "url": "https://writingcenter.unc.edu/tips-and-tools/paragraphs/",
        "supports": "General discussion of paragraph unity, development, examples, explanation, and transitions.",
        "does_not_prove": "It does not validate EssayScaff's POS counts or lexical continuity heuristics.",
    },
]


GLOSSARY = [
    ("Natural Language Processing", "Simple: software operations on human language. Technical: computational methods that represent, annotate, or transform linguistic data.", "spaCy annotates the sample into Doc/Token structures.", "This application uses linguistic annotations to support deterministic checks.", "spaCy processing"),
    ("Statistical language processing", "Simple: a model predicts labels from learned patterns. Technical: model inference assigns annotations based on learned parameters and context.", "The spaCy tagger predicts POS/tag labels.", "These labels feed selected rule conditions.", "spaCy processing"),
    ("Tokenization", "Simple: splitting text into words and punctuation. Technical: converting a string into a spaCy Doc sequence of Token objects.", "‘schools.’ may become ‘schools’ and ‘.’.", "Offsets and phrase matching operate on tokens.", "spaCy processing"),
    ("Lemmatization", "Simple: mapping an inflected word to a base form. Technical: assigning Token.lemma_ using the configured pipeline.", "students → student.", "Lemma sequences enable normalized matching.", "Concepts and Topic Matching"),
    ("Part-of-speech tagging", "Simple: assigning a broad grammatical category. Technical: Token.pos_ such as NOUN, VERB, AUX, ADJ.", "allow is tagged VERB.", "Rules filter clause and content-token candidates.", "spaCy and Rule Base"),
    ("NOUN", "Simple: a word labeled as a person, place, thing, or idea. Technical: spaCy Universal POS label used for content-token and noun-chunk selection.", "students is NOUN.", "Noun/proper-noun tokens contribute to concept extraction and list heuristics.", "Concept Extraction / Rule Base"),
    ("VERB", "Simple: a word labeled as an action or state. Technical: spaCy coarse POS category; finite tags and dependency labels further constrain clause candidates.", "allow is VERB with tag VB.", "Verb tokens can be candidate predicates.", "Rule Base"),
    ("AUX", "Simple: an auxiliary verb such as should or are. Technical: spaCy coarse POS category AUX; included in finite-predicate candidate checks.", "should is AUX.", "Rule code accepts VERB or AUX before applying tag/dependency tests.", "Rule Base"),
    ("SCONJ", "Simple: a subordinating conjunction such as because. Technical: spaCy POS label checked by the Introduction incomplete-subordinator heuristic.", "because is SCONJ.", "It supplies a possible subordinator marker, not a completeness judgment by itself.", "Introduction Rule Base"),
    ("ROOT", "Simple: the parser's top-level token in a sentence. Technical: dependency label assigned to the sentence's syntactic root.", "allow is ROOT in the audited sample.", "Introduction central-direction and Conclusion final-clause candidates require root conditions.", "Dependency parsing / Rule Base"),
    ("nsubj", "Simple: a parser-labeled nominal subject. Technical: dependency relation linking a subject token to its predicate head.", "Schools is nsubj of allow.", "Subject evidence is required by clause-candidate heuristics.", "Dependency parsing / Rule Base"),
    ("ccomp", "Simple: a parser-labeled clausal complement. Technical: a complement clause attached to another predicate in spaCy's dependency scheme.", "use is ccomp of allow in the audited sample.", "Accepted as one of the candidate clause dependencies.", "Dependency parsing / Rule Base"),
    ("advcl", "Simple: a parser-labeled adverbial clause. Technical: an adverbial clause dependent in the predicted dependency tree.", "help is advcl in the audited sample.", "Accepted as a clause-predicate candidate dependency.", "Dependency parsing / Rule Base"),
    ("amod", "Simple: an adjective-like modifier attached to a noun. Technical: adjectival modifier dependency label.", "Artificial modifies tools as amod.", "Displayed for interpreting actual parser edges; not a standalone quality score.", "Dependency parsing"),
    ("dobj", "Simple: a parser-labeled direct object. Technical: legacy-style dependency label for an object governed by a verb.", "them may be dobj of use in the audited parse.", "Serialized as object/complement evidence where emitted.", "Dependency parsing"),
    ("pobj", "Simple: a parser-labeled object of a preposition. Technical: dependency label attached under a preposition in this model's parse scheme.", "schools is pobj of in.", "Displayed in token/dependency evidence.", "Dependency parsing"),
    ("aux", "Simple: an auxiliary attached to a predicate. Technical: dependency label for an auxiliary token.", "should is aux of allow.", "Displayed in the real dependency record.", "Dependency parsing"),
    ("compound", "Simple: one noun-like token modifies another noun. Technical: compound dependency relation.", "intelligence is compound of tools in the audited parse.", "Displayed in the real dependency record.", "Dependency parsing"),
    ("acomp", "Simple: a parser-labeled adjectival complement. Technical: adjectival complement dependency relation.", "common is acomp of becoming.", "Displayed in the real dependency record.", "Dependency parsing"),
    ("prep", "Simple: a parser-labeled prepositional modifier. Technical: dependency label used by this model for a preposition attachment.", "in is prep of becoming.", "Displayed in the real dependency record.", "Dependency parsing"),
    ("mark", "Simple: a marker introducing a subordinate clause. Technical: dependency label for a subordinating marker.", "because is mark of help.", "The Introduction subordinator check inspects POS and dependency/head evidence.", "Introduction Rule Base"),
    ("relcl", "Simple: a relative clause attached to a noun. Technical: dependency label for a relative-clause predicate.", "meet may be relcl of place.", "Included among accepted clause dependencies.", "Rule Base"),
    ("punct", "Simple: punctuation attached by the parser. Technical: dependency label for punctuation tokens.", "a period is punct.", "Punctuation tokens count as tokens but not alphabetic words.", "spaCy processing"),
    ("VB", "Simple: a fine-grained tag for a base-form verb. Technical: English Penn Treebank tag consumed by the finite-tag sets when appropriate.", "allow has tag VB.", "The Introduction/Body/Conclusion clause heuristics admit VB among finite tags.", "Tagging / Rule Base"),
    ("VBP", "Simple: a fine-grained tag often used for a present-tense verb with a non-third-person subject. Technical: Penn Treebank tag included in the configured finite-tag set.", "help has tag VBP.", "The stage rules accept VBP for predicate candidates.", "Tagging / Rule Base"),
    ("VBD", "Simple: a fine-grained past-tense verb tag. Technical: Penn Treebank tag included in the stage finite-tag sets.", "walked can be tagged VBD.", "It is one of the configured predicate tags.", "Tagging / Rule Base"),
    ("VBZ", "Simple: a fine-grained third-person singular present verb tag. Technical: Penn Treebank tag included in the stage finite-tag sets.", "helps has tag VBZ.", "It is one of the configured predicate tags.", "Tagging / Rule Base"),
    ("NN", "Simple: a fine-grained singular/common noun tag. Technical: Penn Treebank tag, separate from the coarse POS label NOUN.", "intelligence has tag NN.", "Shown as a model annotation; rules primarily use coarse POS for noun counts.", "Tagging"),
    ("NNS", "Simple: a fine-grained plural/common noun tag. Technical: Penn Treebank tag, separate from coarse POS NOUN.", "students has tag NNS.", "Shown in the token trace; lemma matching uses student.", "Tagging / Topic Matching"),
    ("JJ", "Simple: a fine-grained adjective tag. Technical: Penn Treebank tag, separate from coarse POS ADJ.", "Artificial has tag JJ.", "Shown in token evidence; WordNet POS mapping uses coarse POS.", "Tagging / WordNet"),
    ("MD", "Simple: a fine-grained modal auxiliary tag. Technical: Penn Treebank tag for modals such as should.", "should has tag MD.", "Displayed as grammar evidence; it is not automatically a recommendation decision.", "Tagging"),
    ("IN", "Simple: a fine-grained preposition/subordinator tag. Technical: Penn Treebank tag used for forms such as in/because.", "because has tag IN and coarse POS SCONJ.", "Fine tag and coarse POS are distinct annotations.", "Tagging / Rule Base"),
    ("TO", "Simple: a fine-grained infinitive marker tag. Technical: Penn Treebank tag for the token to in infinitival constructions.", "to has tag TO.", "Shown in the token trace; it is not a finite predicate.", "Tagging"),
    ("PRP", "Simple: a fine-grained personal-pronoun tag. Technical: Penn Treebank tag separate from coarse POS PRON.", "them has tag PRP.", "Shown in the token trace.", "Tagging"),
    ("Fine-grained tag", "Simple: a more specific grammar label. Technical: Token.tag_ such as VB, VBP, NNS, or MD.", "allow → VB; students → NNS.", "Introduction/Body/Conclusion finite-tag checks use VB, VBD, VBP, VBZ.", "Rule Base"),
    ("Dependency parsing", "Simple: predicting grammatical links among tokens. Technical: assigning each token a dependency label and head in a parse tree.", "students —nsubj→ allow.", "Clause candidates require subject/head links.", "spaCy processing"),
    ("Dependency head", "Simple: the token a dependency attaches to. Technical: Token.head points to a token governor in the predicted dependency tree.", "The subject ‘Schools’ has head ‘allow’ in the audited sample.", "Subject-linked finite predicates are selected by head offsets.", "Rule Base"),
    ("Noun chunk", "Simple: a parser-derived noun phrase. Technical: a spaCy Span exposed through Doc.noun_chunks.", "Artificial intelligence tools.", "TopicService extracts candidate concepts.", "Concept Extraction"),
    ("Clause / predicate", "Simple: a clause expresses a subject-predicate relationship; a predicate is the verbal part. Technical: EssayScaff uses parser labels, POS, tags, and dependency links as a heuristic.", "Schools allow students… has root predicate allow.", "The clauses are candidates, not semantic propositions validated by the app.", "Rule Base"),
    ("Lexical overlap", "Simple: shared words or normalized word forms. Technical: exact case-folded or lemma-normalized token sequence evidence.", "students matches students directly; student/students can share a lemma.", "Used for topic coverage and continuity candidates.", "Topic Matching"),
    ("Normalization", "Simple: converting forms to a common representation. Technical: lowercased spaCy lemmas joined into a normalized phrase.", "students → student.", "Supports phrase deduplication and lemma matching.", "Concept Extraction / Topic Matching"),
    ("WordNet", "Simple: a lexical database grouping word senses. Technical: NLTK exposes synsets and relations from a WordNet corpus.", "The same word may occur in multiple synsets.", "EssayScaff surfaces limited shared-synset candidates.", "WordNet Processing"),
    ("Synset", "Simple: a group of words sharing a particular sense. Technical: a WordNet sense-set identified by a synset ID.", "A synset ID is included in a candidate relationship.", "The code requires exactly one shared synset for a suggestion.", "WordNet Processing"),
    ("Heuristic", "Simple: a practical rule of thumb. Technical: an application-defined deterministic condition over available features.", "Two parser-labeled clause predicates become a development candidate.", "Rules provide observable signals without semantic classification.", "Rule Base"),
    ("Rule Base", "Simple: stage-specific checks on writing evidence. Technical: deterministic functions in IntroductionRuleBase, BodyRuleBase, and ConclusionRuleBase.", "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE.", "Rule events feed feedback and provenance.", "Rule Execution"),
    ("Source offset", "Simple: character position in the original writing. Technical: zero-based, end-exclusive [start,end) interval.", "[0,23) selects ‘Artificial intelligence’.", "Connects evidence back to original text.", "All evidence views"),
    ("Provenance", "Simple: where a displayed statement came from. Technical: feedback-field-to-rule-event linkage including condition, evidence, type, and limitation.", "Next Step cites a clause and development event.", "Allows tracing feedback back to evidence.", "Feedback Decisions"),
    ("Semantic relevance", "Simple: whether the expressed idea addresses a topic. Technical: a contextual judgment beyond exact word overlap.", "‘community garden’ may share a focus word while discussing another subject.", "EssayScaff does not determine this reliably.", "Interpretation limit"),
    ("Confusion matrix", "Simple: counts of predicted vs reference labels. Technical: a contingency table whose cells include TP, FP, TN, FN for a chosen binary label.", "No valid matrix exists until aligned model predictions and human labels exist.", "Research Evaluation remains pending.", "Offline evaluation"),
    ("True Positive", "Simple: a positive prediction that agrees with a positive reference label. Technical: a TP cell for a specified positive class.", "Not countable for this application without aligned predictions and human labels.", "Part of a future criterion-specific confusion matrix.", "Offline evaluation"),
    ("False Positive", "Simple: a positive prediction when the human reference is negative. Technical: a predicted-positive/reference-negative cell for the selected class.", "No valid count exists for the current project state.", "Would represent an overprediction for a defined criterion.", "Offline evaluation"),
    ("True Negative", "Simple: a negative prediction that agrees with a negative reference. Technical: a predicted-negative/reference-negative cell for a selected binary class.", "No valid count exists for the current project state.", "Part of binary-class metric calculations.", "Offline evaluation"),
    ("False Negative", "Simple: a negative prediction when the human reference is positive. Technical: a predicted-negative/reference-positive cell for the selected class.", "No valid count exists for the current project state.", "Would represent a missed positive for a defined criterion.", "Offline evaluation"),
    ("Accuracy", "Simple: fraction of all predictions that match their reference labels. Technical: (TP + TN) / (TP + FP + TN + FN) for a binary task; multiclass accuracy is total correct / total samples.", "Not calculated because there is no human-labeled aligned evaluation set.", "Would summarize overall agreement, but can hide class imbalance.", "Offline evaluation"),
    ("Precision", "Simple: among predicted positives, fraction that are reference positives. Technical: TP/(TP+FP), only for an explicit evaluation target and aligned predictions/labels.", "Not calculable for current production rules.", "Would measure false-positive exposure on a defined dataset.", "Offline evaluation"),
    ("Recall", "Simple: among reference positives, fraction found. Technical: TP/(TP+FN), for a specified positive class.", "Not calculable for current production rules.", "Would measure missed positives on a defined dataset.", "Offline evaluation"),
    ("F1-score", "Simple: harmonic balance of precision and recall. Technical: 2PR/(P+R), for the same target class.", "Not calculable for current production rules.", "Requires valid P and R.", "Offline evaluation"),
]


RULE_SPECS: dict[str, dict[str, str]] = {
    "INTRO.TEXT.PRESENT": {"name": "Alphabetic text present", "condition": "At least one alphabetic token was observed.", "function": "IntroductionRuleBase._rule_events"},
    "INTRO.TEXT.EMPTY_OR_NONALPHABETIC": {"name": "No alphabetic text", "condition": "No alphabetic token was observed in the student input.", "function": "IntroductionRuleBase._rule_events"},
    "INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE": {"name": "Subject-linked finite root clause candidate", "condition": "A finite root predicate has parser-labeled subject evidence attached to it.", "function": "IntroductionRuleBase._clause_candidates"},
    "INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE": {"name": "No subject-predicate candidate", "condition": "No finite root predicate with a parser-labeled subject was found.", "function": "IntroductionRuleBase._clause_candidates"},
    "INTRO.TEXT.KEYWORD_LIST_CANDIDATE": {"name": "Keyword-list candidate", "condition": "No root subject-predicate clause and at least three non-clausal sentence spans or four NOUN/PROPN tokens.", "function": "IntroductionRuleBase._list_or_fragment_finding"},
    "INTRO.TEXT.FRAGMENT_CANDIDATE": {"name": "Fragment candidate", "condition": "Alphabetic text exists but no finite root clause with parser-labeled subject was found; list threshold did not take precedence.", "function": "IntroductionRuleBase._list_or_fragment_finding"},
    "INTRO.TOPIC.FOCUS_TERMS_OBSERVED": {"name": "Configured focus terms observed", "condition": "At least one configured focus phrase has direct or lemma-normalized lexical evidence.", "function": "TopicService._find_matches"},
    "INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED": {"name": "No configured focus match", "condition": "No configured focus phrase matched directly or by lemma normalization.", "function": "TopicService._find_matches"},
    "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW": {"name": "Possible sentence topic-connection gap", "condition": "A verified sentence with a noun and ROOT verb/auxiliary beside a focus-matched sentence has no configured focus match, no shared neighboring content lemma and no third-person/demonstrative reference cue; explicit teacher focus is required. A review signal only, not irrelevance.", "function": "sentence_topic_evidence"},
    "INTRO.POSITION.RELEVANT_POSITION_OBSERVED": {"name": "Explicit position cue observed", "condition": "The assignment wording contains a fixed argumentativeness cue (phrase such as 'agree or disagree' or a should/must question) and a sentence pairs a modal cue (should/must with a subject) or a first-person stance verb (support/agree/favor/believe/think/recommend or oppose/disagree/reject) with a specific assignment-word match in the same sentence.", "function": "IntroductionRuleBase._position_evidence"},
    "INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED": {"name": "No explicit position cue observed", "condition": "The assignment wording contains an argumentativeness cue, specific assignment words and a subject-predicate candidate were observed, and no sentence pairs a modal or first-person stance-verb cue with a specific match. Absence of the cue is not proof that no position is stated.", "function": "IntroductionRuleBase._position_evidence"},
    "INTRO.POSITION.CHECK_NOT_APPLICABLE": {"name": "Position check not applicable", "condition": "The check did not run: the assignment wording contains no argumentativeness cue, or no specific assignment-word match with a subject-predicate candidate was observed.", "function": "IntroductionRuleBase._position_evidence"},
    "INTRO.CONTEXT.TOPIC_AND_CLAUSE_CANDIDATE": {"name": "Topic and clause in one sentence", "condition": "A central clause sentence span contains a focus-term match.", "function": "IntroductionRuleBase._context_candidates"},
    "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR": {"name": "Possible incomplete subordinator", "condition": "An SCONJ in the configured clause-subordinator list is flagged when any of: it is the sentence ROOT (unattached marker); it has a mark dependency but its head is not a parser-labeled clause predicate; it has a mark dependency and its head is the sentence's only finite ROOT clause predicate (suppressed when a separate finite subordinate-clause predicate with its own subject is also observed, indicating likely marker misattachment); it has a prep dependency with no pobj/obj complement; or it is 'because' attached as prep with only a nominal pobj and no later predicate.", "function": "IntroductionRuleBase._incomplete_subordinator_evidence"},
    "INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES": {"name": "Multiple clause-predicate candidates", "condition": "At least two finite clause-predicate candidates remain after incomplete-subordinator sentence filtering.", "function": "IntroductionRuleBase._development_finding"},
    "INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE": {"name": "No additional clause candidate", "condition": "Fewer than two supported finite clause-predicate candidates were observed.", "function": "IntroductionRuleBase._development_finding"},
    "INTRO.GOAL.OBSERVABLE_INTRODUCTION": {"name": "Introduction guidance goal", "condition": "Always emitted for Introduction stage scope.", "function": "IntroductionRuleBase._rule_events"},
    "INTRO.LIMITATION.NO_SEMANTIC_VALIDATION": {"name": "No semantic validation limitation", "condition": "Always emitted; meaning, logic, and facts are not validated.", "function": "IntroductionRuleBase._rule_events"},
    "BODY.TOPIC.NO_FOCUS_MATCH": {"name": "No Body focus match", "condition": "At least one configured focus term exists and none matched anywhere in Body.", "function": "BodyRuleBase._rule_events"},
    "BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH": {"name": "No substantive Body paragraph", "condition": "No alphabetic word appears inside a segmented paragraph.", "function": "BodyRuleBase._rule_events"},
    "BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON": {"name": "Adjacent paragraph comparison", "condition": "At least two substantive paragraphs are pairwise compared for shared content lemmas or transition expressions.", "function": "BodyRuleBase._cross_paragraph_continuity"},
    "BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON": {"name": "Introduction–Body comparison", "condition": "Introduction text was supplied and extracted concepts were compared with Body concepts.", "function": "BodyRuleBase._introduction_continuity"},
    "BODY.INTRO_CONTINUITY.WORDNET_CANDIDATES": {"name": "Introduction–Body WordNet candidates", "condition": "A POS-constrained single-word concept pair shares exactly one WordNet synset.", "function": "compare_stage_concepts"},
    "BODY.GOAL.DEVELOP_BODY_IDEAS": {"name": "Body guidance goal", "condition": "Always emitted for Body stage scope.", "function": "BodyRuleBase._rule_events"},
    "BODY.LIMITATION.NO_SEMANTIC_VALIDATION": {"name": "No semantic validation limitation", "condition": "Always emitted; meaning, support, logic, and facts are not validated.", "function": "BodyRuleBase._rule_events"},
    "CONCLUSION.TEXT.PRESENT": {"name": "Alphabetic Conclusion text present", "condition": "At least one alphabetic token occurs in Conclusion text.", "function": "ConclusionRuleBase._rule_events"},
    "CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC": {"name": "No alphabetic Conclusion text", "condition": "No alphabetic word was detected in Conclusion text.", "function": "ConclusionRuleBase._rule_events"},
    "CONCLUSION.STRUCTURE.CLAUSE_CANDIDATE": {"name": "Conclusion clause candidate", "condition": "Finite parser-labeled predicate(s) have dependency-linked subject evidence.", "function": "clause_candidates_from_sentences"},
    "CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE": {"name": "No Conclusion clause candidate", "condition": "No subject-linked finite clause candidate was detected.", "function": "clause_candidates_from_sentences"},
    "CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE": {"name": "Conclusion keyword-list candidate", "condition": "No subject-linked finite clause and at least three sentence spans or four NOUN/PROPN tokens.", "function": "ConclusionRuleBase._keyword_list_finding"},
    "CONCLUSION.TOPIC.FOCUS_MATCHES": {"name": "Conclusion focus match", "condition": "At least one focus phrase matched directly or by lemma normalization.", "function": "TopicService._find_matches"},
    "CONCLUSION.TOPIC.NO_FOCUS_MATCH": {"name": "No Conclusion focus match", "condition": "No configured focus phrase matched Conclusion text.", "function": "TopicService._find_matches"},
    "CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE": {"name": "Synthesis structure candidate", "condition": "A parser-labeled Conclusion clause contains at least two concepts lexically observed in supplied prior sections.", "function": "ConclusionRuleBase._synthesis_candidates"},
    "CONCLUSION.SYNTHESIS.NO_CANDIDATE": {"name": "No synthesis structure candidate", "condition": "Prior context is available but no sentence met the multiple-prior-concept plus clause heuristic.", "function": "ConclusionRuleBase._synthesis_candidates"},
    "CONCLUSION.SYNTHESIS.UNAVAILABLE": {"name": "Synthesis comparison unavailable", "condition": "Neither Introduction nor Body text was supplied.", "function": "ConclusionRuleBase._synthesis_candidates"},
    "CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE": {"name": "Closure structure candidate", "condition": "A final parser-labeled root clause or explicit closing expression was observed.", "function": "ConclusionRuleBase._closing_candidates"},
    "CONCLUSION.CLOSURE.NO_CANDIDATE": {"name": "No closure candidate", "condition": "No final root clause or listed closing expression was observed.", "function": "ConclusionRuleBase._closing_candidates"},
    "CONCLUSION.CLOSURE.MODAL_OR_RECOMMENDATION_CUE": {"name": "Final sentence modal cue", "condition": "A configured modal/recommendation-associated word occurs in the final sentence.", "function": "ConclusionRuleBase._closing_candidates"},
    "CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS": {"name": "Unobserved prior-section concept", "condition": "A Conclusion concept has content lemmas not lexically observed in supplied prior sections.", "function": "ConclusionRuleBase._new_material_observations"},
    "CONCLUSION.NEW_MATERIAL.KNOWN_CONCEPT_COMBINATION": {"name": "New phrase of observed concepts", "condition": "A phrase form is unseen but its content lemmas were observed earlier.", "function": "ConclusionRuleBase._new_material_observations"},
    "CONCLUSION.REPETITION.REPEATED_SURFACE_CONTENT_WORDS": {"name": "Repeated surface content words", "condition": "A content-token surface occurs more than once.", "function": "repetition_observations"},
    "CONCLUSION.REPETITION.REPEATED_NORMALIZED_CONTENT_TERMS": {"name": "Repeated normalized content terms", "condition": "A content-token lemma occurs more than once.", "function": "repetition_observations"},
    "CONCLUSION.REPETITION.REPEATED_SENTENCE_OPENINGS": {"name": "Repeated sentence openings", "condition": "The same first two alphabetic tokens begin multiple sentences.", "function": "repetition_observations"},
    "CONCLUSION.LIMITATION.NO_SEMANTIC_VALIDATION": {"name": "No semantic validation limitation", "condition": "Always emitted; meaning, synthesis quality, facts, and readiness are not validated.", "function": "ConclusionRuleBase._rule_events"},
    "CONCLUSION.GOAL.REVIEW_TOPIC_AND_PRIOR_IDEAS": {"name": "Conclusion guidance goal", "condition": "Always emitted for Conclusion stage scope.", "function": "ConclusionRuleBase._rule_events"},
}


def _body_rule_specs(analysis: dict[str, Any]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for paragraph in analysis.get("paragraphs", []):
        number = paragraph["paragraph_index"]
        prefix = f"BODY.P{number}."
        result.update({
            prefix + "PARAGRAPH.SEGMENTED": {"name": f"Paragraph {number} segmented", "condition": "A nonblank line group separated by blank lines was found.", "function": "BodyRuleBase._paragraph_spans"},
            prefix + "PARAGRAPH.KEYWORD_LIST_CANDIDATE": {"name": f"Paragraph {number} keyword-list candidate", "condition": paragraph["fragment_or_list_candidate"]["trigger_condition"], "function": "BodyRuleBase._analyze_paragraph"},
            prefix + "PARAGRAPH.FOCUS_TERMS_OBSERVED": {"name": f"Paragraph {number} focus match observed", "condition": "One or more configured focus terms matched within this paragraph span.", "function": "BodyRuleBase._all_focus_matches"},
            prefix + "PARAGRAPH.FOCUS_TERMS_NOT_OBSERVED": {"name": f"Paragraph {number} focus match absent", "condition": "No configured focus term matched in this paragraph span.", "function": "BodyRuleBase._all_focus_matches"},
            prefix + "TOPIC_SENTENCE.CANDIDATE": {"name": f"Paragraph {number} topic-sentence candidate", "condition": "A clause candidate has a focus match in that sentence or a concept recurs across sentences in the paragraph.", "function": "BodyRuleBase._topic_sentence_candidates"},
            prefix + "TOPIC_SENTENCE.NO_CANDIDATE": {"name": f"Paragraph {number} no topic-sentence candidate", "condition": "No sentence met the clause plus focus/recurrence heuristic.", "function": "BodyRuleBase._topic_sentence_candidates"},
            prefix + "SUPPORTING_DETAIL.CANDIDATE": {"name": f"Paragraph {number} clause/detail candidate", "condition": "At least two parser-labeled clause candidates occur in the paragraph.", "function": "BodyRuleBase._supporting_detail_candidates"},
            prefix + "SUPPORTING_DETAIL.NOT_OBSERVED": {"name": f"Paragraph {number} no additional clause candidate", "condition": "Fewer than two parser-labeled clause candidates occur in the paragraph.", "function": "BodyRuleBase._supporting_detail_candidates"},
            prefix + "EXAMPLE_OR_EXPLANATION_MARKER": {"name": f"Paragraph {number} example/explanation marker", "condition": "A listed discourse expression occurs in the paragraph.", "function": "BodyRuleBase._example_marker_evidence"},
        })
        for pair in paragraph["paragraph_unity_evidence"]["sentence_pairs"]:
            left, right = pair["sentence_pair"]
            result[prefix + f"UNITY.SENTENCE_PAIR_{left}_{right}"] = {"name": f"Paragraph {number}, sentences {left}–{right} comparison", "condition": "Adjacent sentence content-token surfaces and lemmas were compared.", "function": "BodyRuleBase._sentence_unity"}
        for key in ("repeated_surface_content_words", "repeated_normalized_content_terms", "repeated_sentence_openings"):
            result[prefix + "REPETITION." + key.upper()] = {"name": f"Paragraph {number}: {key.replace('_', ' ')}", "condition": "A surface content word, normalized content term, or two-word sentence opening occurs more than once.", "function": "repetition_observations"}
    return result


def _conclusion_dynamic_specs() -> dict[str, dict[str, str]]:
    result = {}
    for section in ("INTRODUCTION", "BODY"):
        result[f"CONCLUSION.CONTINUITY.{section}_UNAVAILABLE"] = {"name": f"{section.title()} comparison unavailable", "condition": f"No {section.title()} text was supplied.", "function": "ConclusionRuleBase._cross_stage_comparisons"}
        result[f"CONCLUSION.CONTINUITY.{section}_LEXICAL_COMPARISON"] = {"name": f"{section.title()} lexical comparison", "condition": f"Compare concepts across supplied {section.title()} and Conclusion text.", "function": "compare_stage_concepts"}
        result[f"CONCLUSION.CONTINUITY.{section}_WORDNET_CANDIDATE"] = {"name": f"{section.title()} WordNet candidate", "condition": "A single POS-constrained shared synset was found for a concept pair.", "function": "_wordnet_candidates"}
    return result


@lru_cache(maxsize=128)
def _source_location(function_ref: str) -> dict[str, Any]:
    try:
        module_name, class_name, function_name = function_ref.rsplit(".", 2)
        module = importlib.import_module(module_name)
        owner = getattr(module, class_name)
        function = getattr(owner, function_name)
        lines, start = inspect.getsourcelines(function)
        source_path = Path(inspect.getsourcefile(function) or "")
        return {
            "file": str(Path("services") / source_path.name),
            "class": class_name,
            "function": function_name,
            "start_line": start,
            "end_line": start + len(lines) - 1,
        }
    except (ImportError, AttributeError, OSError, TypeError, ValueError):
        return {"file": "", "class": "", "function": function_ref, "line_status": "not resolved"}


def _rule_spec(rule_id: str, dynamic: dict[str, dict[str, str]]) -> dict[str, Any]:
    spec = dynamic.get(rule_id) or RULE_SPECS.get(rule_id)
    if spec is None and rule_id.startswith("CONCLUSION.CONTINUITY."):
        spec = _conclusion_dynamic_specs().get(rule_id)
    if spec is None:
        spec = {
            "name": rule_id.rsplit(".", 1)[-1].replace("_", " ").title(),
            "condition": "See the emitted event for the exact condition and actual evidence; no registry description is available for this generated event.",
            "function": "IntroductionRuleBase._reason_clause_lexical_check" if rule_id.startswith("INTRO.REASON.") else "BodyRuleBase._rule_events" if rule_id.startswith("BODY.") else "ConclusionRuleBase._rule_events",
        }
    prefix = rule_id.split(".", 1)[0]
    module = {
        "INTRO": "services.introduction_rules",
        "BODY": "services.body_rules",
        "CONCLUSION": "services.conclusion_rules",
    }.get(prefix, "services.stage_evidence")
    function = spec["function"]
    if "." in function:
        class_name, function_name = function.split(".", 1)
    else:
        class_name, function_name = "", function
    if class_name == "TopicService":
        module = "services.topic_service"
    elif function_name == "sentence_topic_evidence":
        module = "services.introduction_sentence_evidence"
        class_name = ""
    elif function_name in {"compare_stage_concepts", "_wordnet_candidates", "repetition_observations", "clause_candidates_from_sentences"}:
        module = "services.stage_evidence"
        class_name = ""
    source = _source_location(f"{module}.{class_name}.{function_name}") if class_name else _function_source(module, function_name)
    reference_ids: list[str] = []
    if rule_id.startswith("INTRO.CLAUSE") or rule_id.startswith("INTRO.TOPIC"):
        reference_ids = ["unc-thesis"]
    elif rule_id.startswith("INTRO.POSITION"):
        reference_ids = ["unc-thesis"]
    elif rule_id.startswith("INTRO.DEVELOPMENT"):
        reference_ids = ["unc-paragraphs"]
    elif rule_id == "INTRO.CONTEXT.TOPIC_AND_CLAUSE_CANDIDATE":
        reference_ids = ["unc-thesis"]
    elif rule_id in {"INTRO.GOAL.OBSERVABLE_INTRODUCTION", "BODY.GOAL.DEVELOP_BODY_IDEAS", "CONCLUSION.GOAL.REVIEW_TOPIC_AND_PRIOR_IDEAS"}:
        reference_ids = ["hattie-timperley", "knight-acawriter"]
    elif "WORDNET" in rule_id:
        reference_ids = ["nltk-wordnet", "princeton-wordnet"]
    elif rule_id.startswith("BODY.") and ("TOPIC_SENTENCE" in rule_id or "SUPPORTING_DETAIL" in rule_id or "UNITY" in rule_id or "CONTINUITY" in rule_id or "EXAMPLE" in rule_id):
        reference_ids = ["unc-paragraphs"]
        if "CONTINUITY" in rule_id or "UNITY" in rule_id:
            reference_ids.append("witte-faigley")
    elif rule_id.startswith("CONCLUSION.CONTINUITY") or rule_id.startswith("CONCLUSION.SYNTHESIS"):
        reference_ids = ["witte-faigley"]
    return {
        "rule_id": rule_id,
        "name": spec["name"],
        "stage": prefix,
        "purpose": spec["name"],
        "educational_rationale": "This is an observable revision signal, not a semantic validation or quality decision.",
        "condition": spec["condition"],
        "implementation": source,
        "required_evidence": "See the current event's actual_evidence/evidence and source spans.",
        "configuration": _rule_configuration(rule_id),
        "interpretation_limit": "A rule event does not establish meaning, correctness, coherence, relevance, quality, or readiness.",
        "reference_ids": reference_ids,
    }


def _rule_configuration(rule_id: str) -> str:
    if rule_id == "INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW":
        from services.introduction_sentence_evidence import CONDITION, LIMITATION
        return CONDITION + " " + LIMITATION
    if rule_id == "INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR":
        return (
            "Gate: token POS is SCONJ and text in CLAUSE_SUBORDINATORS={'although','as','because','before','if','once','since','though','unless','until','when','whereas','while'}. "
            "Flag if any of five OR conditions: (1) dependency == 'ROOT'; "
            "(2) dependency == 'mark' and head_start not in predicate_starts (VERB/AUX with CLAUSE_DEPENDENCIES); "
            "(3) dependency == 'mark' and head_start is the sentence's only finite ROOT predicate (head_is_only_root_clause: VERB/AUX, tag in FINITE_TAGS={'VB','VBD','VBP','VBZ'}, dependency 'ROOT', sole such root); "
            "condition (3) is suppressed when the sentence also contains a separate finite subordinate-clause predicate (dependency in {'advcl','ccomp','xcomp'}, tag in FINITE_TAGS) with its own parser-labeled subject, indicating the marker's ROOT attachment is likely a parser misattachment and the two-clause structure is already observed; "
            "(4) dependency == 'prep' with no pobj/obj child and no prep child that itself has a pobj/obj; "
            "(5) marker == 'because', dependency == 'prep', pobj child (text != 'of') present, and no predicate starts after the marker's end. "
            "Parser attachment can be wrong; this is an observation, not proof."
        )
    if rule_id.startswith("INTRO.POSITION"):
        return (
            "Argumentativeness gate: the assignment topic contains a fixed phrase cue "
            "{'agree or disagree','take a position','take a stand','argue for or against','for or against','your opinion'} "
            "OR its first question word is in POSITION_MODAL_CUES={'should','must'}. "
            "Position cue: an AUX token tagged MD with lemma in {'should','must'} and a subject attached to the modal or its head verb, "
            "OR a VERB with lemma in FOR={'support','agree','favor','believe','think','recommend'} or AGAINST={'oppose','disagree','reject'} "
            "whose subject is I/we; the same sentence must contain a specific (non-broad) assignment-word match "
            "(BROAD_FOCUS_TERMS={'student','students','use','uses','used','using'} excluded). "
            "A 'not' attached to the modal's head verb records stance MODAL_NEGATED. Fixed cues only; paraphrased positions are not detected."
        )
    if rule_id.startswith("INTRO.CLAUSE") or rule_id.startswith("INTRO.DEVELOPMENT"):
        return "FINITE_TAGS={'VB','VBD','VBP','VBZ'}; Introduction also accepts a VBN/VBG predicate with a directly linked AUX tagged MD/VBD/VBP/VBZ and a linked subject. CLAUSE_DEPENDENCIES={'ROOT','conj','advcl','ccomp','xcomp','relcl'}; SUBJECT_DEPENDENCIES={'nsubj','nsubjpass','csubj','csubjpass'}. Development threshold: at least 2 supported clause candidates; not logical support."
    if rule_id == "INTRO.TEXT.KEYWORD_LIST_CANDIDATE" or rule_id.startswith("CONCLUSION.TEXT.KEYWORD_LIST"):
        return "No qualifying subject-linked finite root clause AND (at least 3 non-clausal sentence spans OR at least 4 NOUN/PROPN tokens)."
    if rule_id == "INTRO.CONTEXT.TOPIC_AND_CLAUSE_CANDIDATE":
        return "A central root-clause sentence span must contain at least one direct or lemma-normalized configured focus match."
    if rule_id.startswith("INTRO.TOPIC") or rule_id.startswith("CONCLUSION.TOPIC") or "FOCUS_TERMS" in rule_id:
        return "Direct case-folded surface match OR equal lemma sequence over consecutive alphabetic tokens; only whitespace/apostrophe/hyphen separator characters may occur between phrase tokens."
    if rule_id.startswith("BODY.P") and ".TOPIC_SENTENCE." in rule_id:
        return "A clause candidate plus (focus match in that sentence OR a normalized concept recurring in at least 2 distinct sentences in this paragraph)."
    if rule_id.startswith("BODY.P") and ".SUPPORTING_DETAIL." in rule_id:
        return "Positive condition: at least 2 subject-linked finite clause candidates in this paragraph; all detected candidates are returned."
    if rule_id.startswith("BODY.P") and ".EXAMPLE_OR_EXPLANATION_MARKER" in rule_id:
        return "Exact case-insensitive phrase scan: for example, for instance, such as, including; marker presence only."
    if ".UNITY.SENTENCE_PAIR_" in rule_id:
        return "Compare adjacent-sentence intersections of content-token surfaces and lemmas. CONTENT_POS={NOUN,PROPN,VERB,ADJ,ADV}."
    if ".REPETITION." in rule_id:
        return "Occurrence count > 1. Content-word checks use CONTENT_POS={NOUN,PROPN,VERB,ADJ,ADV}; sentence-opening check uses first 2 alphabetic tokens."
    if rule_id == "BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON":
        return "Compare adjacent substantive paragraph pairs; candidate when shared content lemma exists OR the right paragraph contains a listed transition expression."
    if "WORDNET" in rule_id:
        return "Single-word candidate concepts only; WordNet POS mapped from spaCy NOUN/PROPN→n, VERB→v, ADJ→a, ADV→r; different terms; exactly 1 shared synset. No contextual WSD."
    if rule_id.startswith("CONCLUSION.SYNTHESIS"):
        return "At least 2 distinct normalized concept forms in one parser-labeled Conclusion clause must also occur in supplied prior sections."
    if rule_id.startswith("CONCLUSION.CLOSURE"):
        return "Final root clause OR case-insensitive listed phrase: in conclusion, in summary, to summarize, to sum up, overall, ultimately, in the end, all in all, taken together, therefore, thus. Final cue words: should, could, may, might, must, recommend, suggest, need."
    if rule_id.startswith("CONCLUSION.NEW_MATERIAL"):
        return "Compare normalized concept forms and content lemmas across supplied prior text; remove a component occurrence if nested inside a larger extracted phrase."
    if rule_id.startswith("BODY.P") and ".PARAGRAPH." in rule_id:
        return "Paragraphs split on one or more blank lines; leading/trailing whitespace excluded; internal newlines preserved. List flag threshold uses 3 sentence spans or 4 NOUN/PROPN tokens when no clause candidate exists."
    return "No numeric threshold beyond the exact triggering condition shown above. Consult the source location for the implementation constants."


@lru_cache(maxsize=128)
def _function_source(module_name: str, function_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        lines, start = inspect.getsourcelines(function)
        path = Path(inspect.getsourcefile(function) or "")
        return {"file": str(Path("services") / path.name), "function": function_name, "start_line": start, "end_line": start + len(lines) - 1}
    except (ImportError, AttributeError, OSError, TypeError):
        return {"file": "", "function": function_name, "line_status": "not resolved"}


def rule_inventory(stage: str, analysis: dict[str, Any]) -> list[dict[str, Any]]:
    dynamic: dict[str, dict[str, str]] = {}
    if stage == "BODY":
        dynamic.update(_body_rule_specs(analysis))
    if stage == "CONCLUSION":
        dynamic.update(_conclusion_dynamic_specs())
    ids = set(RULE_SPECS)
    ids.update(dynamic)
    if stage == "INTRODUCTION":
        ids = {rule_id for rule_id in ids if rule_id.startswith("INTRO.")}
    elif stage == "BODY":
        ids = {rule_id for rule_id in ids if rule_id.startswith("BODY.")}
    else:
        ids = {rule_id for rule_id in ids if rule_id.startswith("CONCLUSION.")}
    ids.update(event.get("rule_id", "") for event in analysis.get("rule_evidence", []))
    ids.discard("")
    events_by_id = {event.get("rule_id"): event for event in analysis.get("rule_evidence", [])}
    decisions = {item["rule_id"]: item for item in _observed_rule_decisions(stage, analysis)}
    rows = []
    for rule_id in sorted(ids):
        spec = _rule_spec(rule_id, dynamic)
        decision = decisions.get(rule_id)
        event = events_by_id.get(rule_id)
        if decision is None and event is not None:
            decision = {
                "status": "TRIGGERED",
                "decision_basis": "An event with this rule ID was emitted by the current Rule Base execution.",
            }
        if decision is None:
            decision = {
                "status": "NOT_RECORDED",
                "decision_basis": "The existing output does not record whether this rule branch was evaluated; absence of an event is not treated as a negative result.",
            }
        rows.append({**spec, **decision, "event_available": event is not None})
    return rows


def _observed_rule_decisions(stage: str, analysis: dict[str, Any]) -> list[dict[str, Any]]:
    """Classify decisions only from existing returned stage fields; no analyzer is run."""
    output: list[dict[str, Any]] = []

    def mark(rule_id: str, triggered: bool, basis: str, *, not_applicable: bool = False, status: str | None = None) -> None:
        result_status = status or ("NOT_APPLICABLE" if not_applicable else "TRIGGERED" if triggered else "EVALUATED_NOT_TRIGGERED")
        output.append({"rule_id": rule_id, "status": result_status, "decision_basis": basis})

    emitted = {item.get("rule_id") for item in analysis.get("rule_evidence", [])}
    for rule_id in emitted:
        mark(rule_id, True, "The current Rule Base emitted this event and its evidence.")

    if stage == "INTRODUCTION":
        present = analysis.get("text_presence", {}).get("status") not in {"EMPTY", "WHITESPACE_ONLY", "PUNCTUATION_ONLY"}
        sentence_topic = analysis.get("sentence_topic_evidence")
        if sentence_topic is not None:
            mark("INTRO.TOPIC.SENTENCE_CONNECTION_REVIEW", bool(sentence_topic.get("review_candidates")),
                 "sentence_topic_evidence.sentences retains exact spans, focus matches, concepts, neighboring shared lemmas, reference cues, status, condition and limitations for each sentence.")
        mark("INTRO.TEXT.PRESENT", present, "text_presence status and alphabetic_word_count.")
        mark("INTRO.TEXT.EMPTY_OR_NONALPHABETIC", not present, "text_presence status and alphabetic_word_count.")
        central = analysis.get("observable_structure", {}).get("central_direction_candidates", [])
        mark("INTRO.CLAUSE.SUBJECT_PREDICATE_CANDIDATE", bool(central), "observable_structure.central_direction_candidates.")
        mark("INTRO.CLAUSE.NO_SUBJECT_PREDICATE_CANDIDATE", not bool(central), "observable_structure.central_direction_candidates.")
        finding = analysis.get("observable_structure", {}).get("list_or_fragment_candidate", {})
        keyword_list = bool(finding.get("keyword_list_candidate"))
        fragment = bool(finding.get("fragmentary_text_candidate"))
        mark("INTRO.TEXT.KEYWORD_LIST_CANDIDATE", keyword_list, "observable_structure.list_or_fragment_candidate.keyword_list_candidate.")
        mark("INTRO.TEXT.FRAGMENT_CANDIDATE", fragment and not keyword_list, "observable_structure.list_or_fragment_candidate; keyword-list event takes precedence when both flags are true.", not_applicable=keyword_list)
        observed = bool(analysis.get("lexical_topic_evidence", {}).get("observed_focus_terms"))
        mark("INTRO.TOPIC.FOCUS_TERMS_OBSERVED", observed, "lexical_topic_evidence.observed_focus_terms.")
        mark("INTRO.TOPIC.NO_FOCUS_MATCH_OBSERVED", not observed, "lexical_topic_evidence.observed_focus_terms.")
        mark("INTRO.CONTEXT.TOPIC_AND_CLAUSE_CANDIDATE", bool(analysis.get("observable_structure", {}).get("introductory_context_candidates")), "observable_structure.introductory_context_candidates.")
        mark("INTRO.CLAUSE.POSSIBLE_INCOMPLETE_SUBORDINATOR", bool(analysis.get("observable_structure", {}).get("incomplete_subordinator_candidates")), "observable_structure.incomplete_subordinator_candidates.")
        developed = analysis.get("development_evidence", {}).get("status") == "STRUCTURAL_ELABORATION_CANDIDATE"
        mark("INTRO.DEVELOPMENT.MULTIPLE_CLAUSE_PREDICATES", developed, "development_evidence.status and predicate_count.")
        mark("INTRO.DEVELOPMENT.NO_ADDITIONAL_CLAUSE_CANDIDATE", not developed, "development_evidence.status and predicate_count.")
        position = analysis.get("position_statement_evidence")
        if position is not None:
            basis = ("position_statement_evidence: assignment argumentativeness cue and basis, status, and position "
                     "statements with cue token, subject evidence, stance, and same-sentence specific focus matches.")
            mark("INTRO.POSITION.RELEVANT_POSITION_OBSERVED", position.get("status") == "RELEVANT_POSITION_OBSERVED", basis)
            mark("INTRO.POSITION.NO_RELEVANT_POSITION_OBSERVED", position.get("status") == "NO_RELEVANT_POSITION_OBSERVED", basis)
            mark("INTRO.POSITION.CHECK_NOT_APPLICABLE", position.get("status") in {"CHECK_NOT_APPLICABLE_INFORMATIONAL_ASSIGNMENT", "INSUFFICIENT_TOPIC_EVIDENCE_FOR_POSITION_CHECK"}, basis)
    elif stage == "BODY":
        for paragraph in analysis.get("paragraphs", []):
            n = paragraph["paragraph_index"]
            prefix = f"BODY.P{n}."
            finding = paragraph.get("fragment_or_list_candidate", {})
            mark(prefix + "PARAGRAPH.KEYWORD_LIST_CANDIDATE", bool(finding.get("keyword_list_candidate")), "paragraph.fragment_or_list_candidate.keyword_list_candidate.")
            observed = bool(paragraph.get("focus_term_evidence"))
            mark(prefix + "PARAGRAPH.FOCUS_TERMS_OBSERVED", observed, "paragraph.focus_term_evidence.")
            mark(prefix + "PARAGRAPH.FOCUS_TERMS_NOT_OBSERVED", not observed, "paragraph.focus_term_evidence.")
            topics = bool(paragraph.get("topic_sentence_candidates"))
            mark(prefix + "TOPIC_SENTENCE.CANDIDATE", topics, "paragraph.topic_sentence_candidates.")
            mark(prefix + "TOPIC_SENTENCE.NO_CANDIDATE", not topics, "paragraph.topic_sentence_candidates.")
            details = bool(paragraph.get("supporting_detail_candidates", {}).get("candidates"))
            mark(prefix + "SUPPORTING_DETAIL.CANDIDATE", details, "paragraph.supporting_detail_candidates.candidates.")
            mark(prefix + "SUPPORTING_DETAIL.NOT_OBSERVED", not details, "paragraph.supporting_detail_candidates.candidates.")
            examples = bool(paragraph.get("example_or_explanation_markers"))
            mark(prefix + "EXAMPLE_OR_EXPLANATION_MARKER", examples, "paragraph.example_or_explanation_markers.")
            repetition = paragraph.get("repetition_observations", {})
            for key in ("repeated_surface_content_words", "repeated_normalized_content_terms", "repeated_sentence_openings"):
                mark(prefix + "REPETITION." + key.upper(), bool(repetition.get(key)), f"paragraph.repetition_observations.{key}.")
            for pair in paragraph.get("paragraph_unity_evidence", {}).get("sentence_pairs", []):
                i, j = pair["sentence_pair"]
                mark(prefix + f"UNITY.SENTENCE_PAIR_{i}_{j}", True, f"Pairwise comparison was returned with status {pair.get('status')}.")
        lexical = analysis.get("lexical_topic_evidence", {})
        total = lexical.get("total_unique_focus_terms", 0)
        observed_any = bool(lexical.get("observed_focus_terms"))
        mark("BODY.TOPIC.NO_FOCUS_MATCH", total > 0 and not observed_any, "lexical_topic_evidence total/observed focus fields.", not_applicable=not bool(total))
        substantive = analysis.get("substantive_paragraph_count", 0) > 0
        mark("BODY.TEXT.NO_SUBSTANTIVE_PARAGRAPH", not substantive, "substantive_paragraph_count.")
        pairs = analysis.get("cross_paragraph_continuity", {}).get("paragraph_pairs", [])
        mark("BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON", bool(pairs), "cross_paragraph_continuity.paragraph_pairs.", not_applicable=not bool(pairs))
        intro = analysis.get("introduction_to_body_continuity", {})
        intro_available = intro.get("status") == "LEXICAL_COMPARISON_AVAILABLE"
        mark("BODY.INTRO_CONTINUITY.LEXICAL_COMPARISON", intro_available, "introduction_to_body_continuity.status.", not_applicable=intro.get("status") == "NOT_AVAILABLE_NO_INTRODUCTION_SUPPLIED")
        wordnet = intro.get("wordnet_relationship_candidates", {})
        suggestions = wordnet.get("suggestions", [])
        mark("BODY.INTRO_CONTINUITY.WORDNET_CANDIDATES", bool(suggestions), "introduction_to_body_continuity.wordnet_relationship_candidates.", not_applicable=not intro_available, status="FAILED" if intro_available and wordnet.get("status") == "RESOURCE_MISSING" else None)
    else:
        presence = analysis.get("text_presence", {})
        has_text = presence.get("alphabetic_word_count", 0) > 0
        mark("CONCLUSION.TEXT.PRESENT", has_text, "text_presence.alphabetic_word_count.")
        mark("CONCLUSION.TEXT.EMPTY_OR_NONALPHABETIC", not has_text, "text_presence.alphabetic_word_count.")
        clauses = bool(analysis.get("clause_candidates"))
        mark("CONCLUSION.STRUCTURE.CLAUSE_CANDIDATE", clauses, "clause_candidates.")
        mark("CONCLUSION.STRUCTURE.NO_CLAUSE_CANDIDATE", not clauses, "clause_candidates.")
        mark("CONCLUSION.TEXT.KEYWORD_LIST_CANDIDATE", bool(analysis.get("keyword_list_candidate", {}).get("candidate")), "keyword_list_candidate.candidate.")
        matched = bool(analysis.get("lexical_topic_evidence", {}).get("matches"))
        mark("CONCLUSION.TOPIC.FOCUS_MATCHES", matched, "lexical_topic_evidence.matches.")
        mark("CONCLUSION.TOPIC.NO_FOCUS_MATCH", not matched, "lexical_topic_evidence.matches.")
        for section, comparison_key in (("INTRODUCTION", "introduction_to_conclusion_continuity"), ("BODY", "body_to_conclusion_continuity")):
            comp = analysis.get(comparison_key, {})
            supplied = comp.get("status") == "LEXICAL_COMPARISON_AVAILABLE"
            mark(f"CONCLUSION.CONTINUITY.{section}_UNAVAILABLE", not supplied, f"{comparison_key}.status.", not_applicable=supplied)
            mark(f"CONCLUSION.CONTINUITY.{section}_LEXICAL_COMPARISON", supplied, f"{comparison_key}.status.", not_applicable=not supplied)
            wn = comp.get("wordnet_relationship_candidates", {})
            suggestions = wn.get("suggestions", [])
            mark(f"CONCLUSION.CONTINUITY.{section}_WORDNET_CANDIDATE", bool(suggestions), f"{comparison_key}.wordnet_relationship_candidates.", not_applicable=not supplied, status="FAILED" if supplied and wn.get("status") == "RESOURCE_MISSING" else None)
        synthesis = analysis.get("synthesis_structure_candidates", {})
        synthesis_status = synthesis.get("status")
        mark("CONCLUSION.SYNTHESIS.STRUCTURE_CANDIDATE", synthesis_status == "SYNTHESIS_STRUCTURE_CANDIDATE", "synthesis_structure_candidates.status.")
        mark("CONCLUSION.SYNTHESIS.NO_CANDIDATE", synthesis_status == "NO_SYNTHESIS_STRUCTURE_CANDIDATE_OBSERVED", "synthesis_structure_candidates.status.", not_applicable=synthesis_status == "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED")
        mark("CONCLUSION.SYNTHESIS.UNAVAILABLE", synthesis_status == "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED", "synthesis_structure_candidates.status.")
        closure = analysis.get("closure_candidates", {})
        closed = closure.get("status") == "CLOSURE_STRUCTURE_CANDIDATE"
        mark("CONCLUSION.CLOSURE.STRUCTURE_CANDIDATE", closed, "closure_candidates.status.")
        mark("CONCLUSION.CLOSURE.NO_CANDIDATE", not closed, "closure_candidates.status.")
        mark("CONCLUSION.CLOSURE.MODAL_OR_RECOMMENDATION_CUE", bool(closure.get("final_sentence_modal_or_recommendation_cues")), "closure_candidates.final_sentence_modal_or_recommendation_cues.")
        novel = analysis.get("new_material_observations", {})
        mark("CONCLUSION.NEW_MATERIAL.UNOBSERVED_CONCEPTS", bool(novel.get("unobserved_concept_candidates")), "new_material_observations.unobserved_concept_candidates.", not_applicable=novel.get("status") == "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED")
        mark("CONCLUSION.NEW_MATERIAL.KNOWN_CONCEPT_COMBINATION", bool(novel.get("phrase_combinations_of_observed_concepts")), "new_material_observations.phrase_combinations_of_observed_concepts.", not_applicable=novel.get("status") == "NOT_AVAILABLE_NO_PRIOR_SECTIONS_SUPPLIED")
        repetitions = analysis.get("repetition_observations", {})
        for key in ("repeated_surface_content_words", "repeated_normalized_content_terms", "repeated_sentence_openings"):
            mark("CONCLUSION.REPETITION." + key.upper(), bool(repetitions.get(key)), f"repetition_observations.{key}.")
    return output


def build_rule_evaluation_trace(stage: str, analysis: dict[str, Any]) -> list[dict[str, Any]]:
    """Return rule registry plus outcomes evidenced by emitted events/results."""
    return rule_inventory(stage, analysis)


def runtime_metadata(nlp_service: Any) -> dict[str, Any]:
    try:
        nltk_version = metadata.version("nltk")
    except metadata.PackageNotFoundError:
        nltk_version = "not installed"
    try:
        flask_version = metadata.version("Flask")
    except metadata.PackageNotFoundError:
        flask_version = "not installed"
    nlp = nlp_service.nlp
    return {
        "python_version": platform.python_version(),
        "spacy_version": metadata.version("spacy"),
        "nltk_version": nltk_version,
        "flask_version": flask_version,
        "sqlite_runtime_version": sqlite3.sqlite_version,
        "model": {
            "package_name": nlp.meta.get("name"),
            "version": nlp.meta.get("version"),
            "language": nlp.lang,
        },
        "pipeline": {
            "tokenizer": {"name": "tokenizer", "execution_status": "EXECUTED", "listed_in_pipe_names": False},
            "enabled_components": list(nlp.pipe_names),
            "disabled_components": list(nlp.disabled),
            "component_timings": "not instrumented individually; the recorded parse_ms measures the complete nlp(text) call.",
            "active_component_output_use": {
                "tok2vec": "Runs as part of the configured pipeline; EssayScaff does not directly read its vectors.",
                "tagger": "Token fine-grained tags are serialized; POS/tag values feed rule conditions.",
                "parser": "Dependency labels, heads, sentence boundaries, noun chunks, and subjects/complements feed the services.",
                "attribute_ruler": "Runs in the pipeline; its attributes are available to later components but not separately reported by EssayScaff.",
                "lemmatizer": "Token lemmas feed topic normalization and concept comparison.",
                "ner": "Runs in the pipeline; named entities are not consumed by the active EssayScaff analysis output.",
            },
        },
        "note": "Metadata is read from the already-loaded NLPService. This function does not parse text or query WordNet.",
    }


def _source_line(file_path: str, needle: str) -> dict[str, Any]:
    project_root = Path(__file__).resolve().parent.parent
    path = project_root / file_path
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {"file": file_path, "symbol": needle, "line_status": "source file unavailable"}
    for index, line in enumerate(lines, start=1):
        if needle in line:
            return {"file": file_path, "symbol": needle.strip(), "start_line": index}
    return {"file": file_path, "symbol": needle.strip(), "line_status": "symbol not found"}


def process_source_locations() -> dict[str, list[dict[str, Any]]]:
    """Resolve representative implementation locations from current source files."""
    source_map = {
        "00": [("app.py", "def analyze_payload("), ("services/essay_analysis_service.py", "    def analyze(")],
        "01": [("app.py", "    def require_account()"), ("app.py", "    def require_csrf_token()"), ("app.py", "    def analyze_payload(")],
        "02": [("services/nlp_service.py", "    def __init__("), ("services/nlp_service.py", "    def parse("), ("services/nlp_service.py", "    def analyze_doc("), ("services/nlp_service.py", "    def _token_data(")],
        "03": [("services/topic_service.py", "    def _extract_concepts(")],
        "04": [("services/topic_service.py", "    def prepare_teacher_context("), ("services/topic_service.py", "    def _unique_focus_terms("), ("services/topic_service.py", "    def _find_matches(")],
        "05": [("services/topic_service.py", "    def _wordnet_status("), ("services/topic_service.py", "    def _wordnet_suggestions("), ("services/stage_evidence.py", "def _wordnet_candidates(")],
        "06": [("services/introduction_rules.py", "    def _rule_events("), ("services/body_rules.py", "    def _rule_events("), ("services/conclusion_rules.py", "    def _rule_events("), ("services/stage_evidence.py", "def clause_candidates_from_sentences(")],
        "07": [("services/feedback_service.py", "    def generate("), ("services/feedback_service.py", "    def generate_conclusion("), ("services/feedback_service.py", "    def generate_body(")],
        "08": [("app.py", "    def analyze_payload("), ("static/research_inspector.js", "async function analyzeSample("), ("static/research_inspector.js", "function renderProcess(")],
        "09": [("services/draft_store.py", "    def save("), ("services/draft_store.py", "    def save_revision("), ("services/draft_store.py", "    def create_submission(")],
        "10": [("experiments/semantic_feasibility/evaluate.py", "def reviewer_agreement("), ("experiments/semantic_feasibility/evaluate.py", "def classification_metrics("), ("experiments/semantic_feasibility/annotate.py", "def annotate_samples(")],
        "11": [("services/research_inspector.py", "def build_rule_evaluation_trace("), ("services/research_inspector.py", "def runtime_metadata(")],
    }
    return {process_id: [_source_line(path, needle) for path, needle in entries] for process_id, entries in source_map.items()}


def inspector_metadata(nlp_service: Any | None = None) -> dict[str, Any]:
    return {
        "process_order": PROCESS_ORDER,
        "processes": PROCESS_CATALOG,
        "process_source_locations": process_source_locations(),
        "references": REFERENCES,
        "glossary": [
            {"term": term, "definition": definition, "example": example, "why_used": why, "related_process": related}
            for term, definition, example, why, related in GLOSSARY
        ],
        "evaluation": _evaluation_status(),
        "runtime": runtime_metadata(nlp_service) if nlp_service is not None else None,
    }


def _evaluation_status() -> dict[str, Any]:
    experiment_dir = Path(__file__).resolve().parent.parent / "experiments" / "semantic_feasibility"
    sample_count = 0
    provisional_count = 0
    human_count = 0
    annotation_file_count = 0
    prediction_file_count = 0
    read_errors: list[str] = []
    human_ids_by_reviewer: dict[str, set[str]] = {}
    sample_ids: set[str] = set()
    try:
        samples = json.loads((experiment_dir / "samples.json").read_text(encoding="utf-8"))
        sample_count = len(samples) if isinstance(samples, list) else 0
        sample_ids = {item["sample_id"] for item in samples if isinstance(item, dict) and isinstance(item.get("sample_id"), str)}
    except (OSError, json.JSONDecodeError):
        read_errors.append("samples.json could not be read")
    try:
        provisional = json.loads((experiment_dir / "ai_diagnostic_annotations.json").read_text(encoding="utf-8"))
        provisional_count = sum(
            item.get("annotation_provenance") == "AI_GENERATED_DIAGNOSTIC"
            for item in provisional.get("samples", [])
        )
    except (OSError, json.JSONDecodeError):
        read_errors.append("AI diagnostic annotations could not be read")
    annotation_dir = experiment_dir / "annotations"
    if annotation_dir.exists():
        annotation_paths = list(annotation_dir.glob("*.jsonl"))
        annotation_file_count = len(annotation_paths)
        try:
            from experiments.semantic_feasibility.annotate import validate_annotation
        except ImportError:
            validate_annotation = None
        for path in annotation_paths:
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    record = json.loads(line)
                    if validate_annotation is not None:
                        validate_annotation(record)
                    if (
                        record.get("record_type") == "human_annotation"
                        and record.get("label_provenance") == "human_reviewer"
                        and record.get("sample_id") in sample_ids
                    ):
                        human_count += 1
                        reviewer = record.get("reviewer_id")
                        sample_id = record.get("sample_id")
                        if isinstance(reviewer, str) and isinstance(sample_id, str):
                            human_ids_by_reviewer.setdefault(reviewer, set()).add(sample_id)
            except (OSError, json.JSONDecodeError, ValueError):
                read_errors.append(f"{path.name} contains unreadable annotation data")
    prediction_paths = list(experiment_dir.glob("predictions*.jsonl"))
    prediction_file_count = len(prediction_paths)
    aligned = False
    if prediction_paths and human_ids_by_reviewer:
        try:
            from experiments.semantic_feasibility.evaluate import load_prediction_file

            for path in prediction_paths:
                prediction_ids = [record["sample_id"] for record in load_prediction_file(path)]
                if len(prediction_ids) != len(set(prediction_ids)):
                    continue
                prediction_set = set(prediction_ids)
                if any(prediction_set == reviewer_ids for reviewer_ids in human_ids_by_reviewer.values()):
                    aligned = True
                    break
        except (ImportError, ValueError, OSError) as error:
            read_errors.append(f"Model predictions could not be validated: {error}")
    if human_count and aligned:
        status = "inputs_present_metrics_not_calculated"
        message = "Human annotations and prediction file(s) exist; choose and align a reference reviewer before calculating metrics."
    else:
        status = "pending"
        message = "Evaluation pending — No verified human-labeled dataset and aligned model predictions are both available."
    return {
        "status": status,
        "message": message,
        "diagnostic_sample_count": sample_count,
        "provisional_ai_label_count": provisional_count,
        "human_reference_count": human_count,
        "human_annotation_file_count": annotation_file_count,
        "prediction_file_count": prediction_file_count,
        "aligned_prediction_file_found": aligned,
        "metrics": [],
        "read_errors": read_errors,
        "source": "experiments/semantic_feasibility/evaluate.py",
    }


def process_trace_status(process_id: str, trace: dict[str, Any] | None, stage: str) -> dict[str, Any]:
    """Map recorded execution to diagram states without implying absent work ran."""
    if process_id in {"09", "10"}:
        return {"execution_status": "NOT_APPLICABLE", "duration_ms": None}
    if process_id in {"00", "01", "08", "11"}:
        if process_id == "01":
            return {"execution_status": "EXECUTED", "duration_ms": trace.get("request_validation_and_resolution_ms") if trace else None}
        if process_id == "08":
            return {"execution_status": "EXECUTED", "duration_ms": None, "note": "API returned; browser rendering is measured client-side."}
        return {"execution_status": "EXECUTED", "duration_ms": None}
    if not trace:
        return {"execution_status": "NOT_INSTRUMENTED", "duration_ms": None}
    stage_trace = trace.get("stages", {}).get(stage, {})
    if stage_trace.get("execution_status") != "EXECUTED":
        return {"execution_status": "NOT_APPLICABLE", "duration_ms": None}
    topic = stage_trace.get("topic_service") or {}
    steps = {step.get("id"): step for step in topic.get("steps", [])}
    timings = stage_trace.get("timings_ms", {})
    mapping = {
        "02": ("spacy_document_processing", "topic_service_ms"),
        "03": ("concept_extraction", "topic_service_ms"),
        "04": ("topic_matching", "topic_service_ms"),
        "05": ("wordnet_direct_suggestions", "rule_base_ms"),
        "06": (None, "rule_base_ms"),
        "07": (None, "feedback_ms"),
    }
    step_id, time_key = mapping[process_id]
    if step_id:
        operation = steps.get(step_id, {})
        return {"execution_status": operation.get("execution_status", "NOT_INSTRUMENTED"), "duration_ms": operation.get("duration_ms"), "detail": operation}
    return {"execution_status": "EXECUTED" if time_key in timings else "NOT_INSTRUMENTED", "duration_ms": timings.get(time_key)}
