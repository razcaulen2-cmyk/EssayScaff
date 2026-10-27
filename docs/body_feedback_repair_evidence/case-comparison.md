# Actual Body tutor before/after results

Generated from authenticated real-Chrome captures. Original Body observations match in all 12 cases; only input/context retention and feedback/presentation change.

## B01

> A vegetable garden can help students understand science through real activities. They can observe how seeds grow, measure plant growth, and record changes in leaves. These experiences give students opportunities to apply what they learn during lessons.
> 
> A school garden can also teach responsibility. Students can take turns watering the vegetables and removing weeds. Taking care of plants regularly can help them develop patience and teamwork.

- Before Primary / Next Step: `body_neutral_observable` / `body_neutral_general`.
- After Primary / Next Step: `body_neutral_observable` / `body_neutral_observable`.
- Actual status: `NO_SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: None assigned; neutral observation result.
- Actual selection condition: no supported list, development, repeated-opening, or adjacent-wording review concern was selected; missing Introduction context and absent keywords are not writing defects.
- Recorded strength text: Both paragraphs contain possible opening statements and additional sentence structures.
Assignment-word matches were recorded in Paragraphs 1, 2.

### Before — exact displayed guidance

```json
{
  "What I noticed": "The Body contains 2 recorded paragraphs. No specific higher-priority concern was selected by these checks.",
  "Look at your writing": "Paragraph 1: 3 recorded sentences.\nParagraph 2: 3 recorded sentences.\nIntroduction context was compared with the Body.",
  "Why it matters": "These are paragraph and sentence observations, not a finding that your support is adequate or inadequate. Sentence patterns and sentence counts cannot assess the meaning or quality of details.",
  "How to improve": "Read each paragraph beside your Introduction. Decide whether its point connects to your position and whether a reader would need an example, reason, or explanation. Revise in your own words where useful, then check that a reader can follow how each paragraph contributes to your argument."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "The available checks did not identify a specific structural concern in this Body section.",
  "What's working": "Both paragraphs contain possible opening statements and additional sentence structures.\nAssignment-word matches were recorded in Paragraphs 1, 2."
}
```

No error highlight or improvement task is selected.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B02

> A school garden can teach responsibility.

- Before Primary / Next Step: `body_ideas_develop_point` / `body_ideas_develop_point`.
- After Primary / Next Step: `body_ideas_develop_point` / `body_ideas_develop_point`.
- Actual status: `SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: Ideas / Develop Your Supporting Details / `HELP-BODY-DEVELOP-POINT`
- Actual selection condition: first substantive non-list paragraph with a recorded subject-linked clause, no additional detail candidates, and its fired SUPPORTING_DETAIL.NOT_OBSERVED event.
- Recorded strength text: Paragraph 1 contains a possible statement pattern.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "Paragraph 1 contains one recorded sentence. The checks did not identify an additional sentence part developing this paragraph.",
  "Look at your writing": "A school garden can teach responsibility.",
  "Why it matters": "Readers may need more information than you do, because they cannot see what you are thinking. A reason, example, or explanation can make the paragraph's idea clearer.",
  "How to improve": "Choose an example, reason, or explanation that shows this paragraph's idea. Explain what happens and how it connects to your argument in your own words, then check that the added detail helps a reader understand the idea."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "Paragraph 1 has a possible main statement, but no additional sentence was recorded to develop it.",
  "Look at your writing": "A school garden can teach responsibility.",
  "Why it matters": "Readers often need more explanation to understand the point of a Body paragraph.",
  "How to improve": "Think of an activity, example, or explanation that could help readers understand Paragraph 1. Write it in your own words if needed."
}
```

Supporting Rule IDs: `BODY.P1.SUPPORTING_DETAIL.NOT_OBSERVED`.

- Verified source mark [0, 41): **A school garden can teach responsibility.** — The recorded paragraph absence event anchors its first possible statement; only this statement is marked.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B03

> A vegetable garden can help students understand science through real activities. They can observe how seeds grow, measure plant growth, and record changes in leaves. These experiences give students opportunities to apply what they learn during lessons.
> 
> A school garden can teach responsibility.

- Before Primary / Next Step: `body_ideas_develop_point` / `body_ideas_develop_point`.
- After Primary / Next Step: `body_ideas_develop_point` / `body_ideas_develop_point`.
- Actual status: `SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: Ideas / Develop Your Supporting Details / `HELP-BODY-DEVELOP-POINT`
- Actual selection condition: first substantive non-list paragraph with a recorded subject-linked clause, no additional detail candidates, and its fired SUPPORTING_DETAIL.NOT_OBSERVED event.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraphs 1, 2.

### Before — exact displayed guidance

```json
{
  "What I noticed": "Paragraph 2 contains one recorded sentence. The checks did not identify an additional sentence part developing this paragraph.",
  "Look at your writing": "A school garden can teach responsibility.",
  "Why it matters": "Readers may need more information than you do, because they cannot see what you are thinking. A reason, example, or explanation can make the paragraph's idea clearer.",
  "How to improve": "Choose an example, reason, or explanation that shows this paragraph's idea. Explain what happens and how it connects to your argument in your own words, then check that the added detail helps a reader understand the idea."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "Paragraph 2 has a possible main statement, but no additional sentence was recorded to develop it.",
  "Look at your writing": "A school garden can teach responsibility.",
  "Why it matters": "Readers often need more explanation to understand the point of a Body paragraph.",
  "How to improve": "Think of an activity, example, or explanation that could help readers understand Paragraph 2. Write it in your own words if needed."
}
```

Supporting Rule IDs: `BODY.P2.SUPPORTING_DETAIL.NOT_OBSERVED`.

- Verified source mark [254, 295): **A school garden can teach responsibility.** — The recorded paragraph absence event anchors its first possible statement; only this statement is marked.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B04

> Garden, seeds, vegetables, teamwork, students.

- Before Primary / Next Step: `body_organization_paragraph_shape` / `body_organization_paragraph_shape`.
- After Primary / Next Step: `body_organization_paragraph_shape` / `body_organization_paragraph_shape`.
- Actual status: `SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: Organization / Build Your Paragraph / `HELP-BODY-PARAGRAPH-SHAPE`
- Actual selection condition: first substantive list-like paragraph with its fired KEYWORD_LIST_CANDIDATE event.
- Recorded strength text: None claimed.

### Before — exact displayed guidance

```json
{
  "What I noticed": "One Body paragraph reads as a list of ideas, and no recorded sentence connects them yet.",
  "Look at your writing": "Garden, seeds, vegetables, teamwork, students.",
  "Why it matters": "A paragraph develops one idea at a time. Listing related words leaves readers waiting for the idea you will explain.",
  "How to improve": "Choose one idea from the highlighted paragraph and write a sentence about it in your own words. Then read the paragraph and check that it focuses on that idea."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "Paragraph 1 was recorded as a list-like structure, with no supported connecting statement.",
  "Look at your writing": "Garden, seeds, vegetables, teamwork, students.",
  "Why it matters": "A paragraph develops one idea at a time. Listing related words leaves readers waiting for the idea you will explain.",
  "How to improve": "Choose one idea from the highlighted paragraph and write a sentence about it in your own words. Then read the paragraph and check that it focuses on that idea."
}
```

Supporting Rule IDs: `BODY.P1.PARAGRAPH.KEYWORD_LIST_CANDIDATE`.

- Verified source mark [0, 46): **Garden, seeds, vegetables, teamwork, students.** — The exact source spans recorded by the list-like paragraph event are the structural review location.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B05

> Students can plant vegetables. Students can water vegetables. Students can remove weeds.

- Before Primary / Next Step: `body_sentence_fluency_sentence_beginnings` / `body_sentence_fluency_sentence_beginnings`.
- After Primary / Next Step: `body_sentence_fluency_sentence_beginnings` / `body_sentence_fluency_sentence_beginnings`.
- Actual status: `SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: Sentence Fluency / Review Repeated Sentence Openings / `HELP-BODY-SENTENCE-BEGINNINGS`
- Actual selection condition: first substantive paragraph with repeated_sentence_openings and its fired repeated-opening event.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "More than one sentence in one paragraph starts with the same words.",
  "Look at your writing": "Students can plant vegetables.\nStudents can water vegetables.\nStudents can remove weeds.",
  "Why it matters": "Starting several sentences with the same words can sound repetitive. Variety in sentence beginnings can help your reader follow each sentence.",
  "How to improve": "Read the paragraph aloud. If one repeated opening sounds awkward, rewrite that sentence's beginning in your own words, then check that the paragraph still reads smoothly."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "More than one sentence in Paragraph 1 begins with 'students can'. Repetition can be intentional.",
  "Look at your writing": "Students can plant vegetables. Students can water vegetables. Students can remove weeds.",
  "Why it matters": "Starting several sentences with the same words can sound repetitive. Variety in sentence beginnings can help your reader follow each sentence.",
  "How to improve": "Read the paragraph aloud. If one repeated opening sounds awkward, rewrite that sentence's beginning in your own words, then check that the paragraph still reads smoothly."
}
```

Supporting Rule IDs: `BODY.P1.REPETITION.REPEATED_SENTENCE_OPENINGS`.

- Verified source mark [0, 12): **Students can** — Only the recorded repeated opening words are marked; repetition is not automatically an error.
- Verified source mark [31, 43): **Students can** — Only the recorded repeated opening words are marked; repetition is not automatically an error.
- Verified source mark [62, 74): **Students can** — Only the recorded repeated opening words are marked; repetition is not automatically an error.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B06

> A school garden can teach responsibility. Students can take turns watering vegetables and removing weeds. Caring for plants regularly can help them practice patience.

- Before Primary / Next Step: `body_neutral_observable` / `body_neutral_general`.
- After Primary / Next Step: `body_neutral_observable` / `body_neutral_observable`.
- Actual status: `NO_SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: None assigned; neutral observation result.
- Actual selection condition: no supported list, development, repeated-opening, or adjacent-wording review concern was selected; missing Introduction context and absent keywords are not writing defects.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "The Body contains 1 recorded paragraph. No specific higher-priority concern was selected by these checks.",
  "Look at your writing": "Paragraph 1: 3 recorded sentences.\nIntroduction context was compared with the Body.",
  "Why it matters": "These are paragraph and sentence observations, not a finding that your support is adequate or inadequate. Sentence patterns and sentence counts cannot assess the meaning or quality of details.",
  "How to improve": "Read each paragraph beside your Introduction. Decide whether its point connects to your position and whether a reader would need an example, reason, or explanation. Revise in your own words where useful, then check that a reader can follow how each paragraph contributes to your argument."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "The available checks did not identify a specific structural concern in this Body section.",
  "What's working": "Paragraph 1 contains a possible opening statement and additional sentence structures.\nAssignment-word matches were recorded in Paragraph 1."
}
```

No error highlight or improvement task is selected.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B07

> A vegetable garden can help students learn science. Students can observe plant growth. Purple elephants are secretly running the school.

- Before Primary / Next Step: `body_neutral_observable` / `body_neutral_general`.
- After Primary / Next Step: `body_neutral_observable` / `body_neutral_observable`.
- Actual status: `NO_SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: None assigned; neutral observation result.
- Actual selection condition: no supported list, development, repeated-opening, or adjacent-wording review concern was selected; missing Introduction context and absent keywords are not writing defects.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "The Body contains 1 recorded paragraph. No specific higher-priority concern was selected by these checks.",
  "Look at your writing": "Paragraph 1: 3 recorded sentences.\nIntroduction context was compared with the Body.",
  "Why it matters": "These are paragraph and sentence observations, not a finding that your support is adequate or inadequate. Sentence patterns and sentence counts cannot assess the meaning or quality of details.",
  "How to improve": "Read each paragraph beside your Introduction. Decide whether its point connects to your position and whether a reader would need an example, reason, or explanation. Revise in your own words where useful, then check that a reader can follow how each paragraph contributes to your argument."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "The available checks did not identify a specific structural concern in this Body section.",
  "What's working": "Paragraph 1 contains a possible opening statement and additional sentence structures.\nAssignment-word matches were recorded in Paragraph 1."
}
```

No error highlight or improvement task is selected.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B08

> A school garden can teach responsibility. Students can take turns watering vegetables and removing weeds. Caring for plants regularly can help them practice patience.

- Before Primary / Next Step: `body_neutral_observable` / `body_neutral_no_intro_context`.
- After Primary / Next Step: `body_neutral_observable` / `body_neutral_observable`.
- Actual status: `NO_SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: None assigned; neutral observation result.
- Actual selection condition: no supported list, development, repeated-opening, or adjacent-wording review concern was selected; missing Introduction context and absent keywords are not writing defects.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "The Body contains 1 recorded paragraph. No specific higher-priority concern was selected by these checks.",
  "Look at your writing": "Paragraph 1: 3 recorded sentences.\nNo Introduction context was available for comparison.",
  "Why it matters": "These are paragraph and sentence observations, not a finding that your support is adequate or inadequate. Sentence patterns and sentence counts cannot assess the meaning or quality of details.",
  "How to improve": "Read each paragraph beside your Introduction. Decide whether its point connects to your position and whether a reader would need an example, reason, or explanation. Revise in your own words where useful, then check that a reader can follow how each paragraph contributes to your argument."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "The available checks did not identify a specific structural concern in this Body section.",
  "What's working": "Paragraph 1 contains a possible opening statement and additional sentence structures.\nAssignment-word matches were recorded in Paragraph 1."
}
```

No error highlight or improvement task is selected.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B09

> Students can plant vegetables. They can observe plant growth.
> 
> An orchestra performs symphonies. Musicians practice their instruments.

- Before Primary / Next Step: `body_organization_paragraph_link` / `body_organization_paragraph_link`.
- After Primary / Next Step: `body_organization_paragraph_link` / `body_organization_paragraph_link`.
- Actual status: `SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: Organization / Review Paragraph Connections / `HELP-BODY-PARAGRAPH-LINK`
- Actual selection condition: first pair with NO_EXPLICIT_LEXICAL_LINK_OBSERVED and its fired paragraph-comparison event.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "Neighboring paragraphs have no recorded shared words or linking phrase between them.",
  "Look at your writing": "Students can plant vegetables. They can observe plant growth.\nAn orchestra performs symphonies. Musicians practice their instruments.",
  "Why it matters": "Readers need to know why the next paragraph follows the previous one. Word matches and linking phrases are one way the checks look for that connection.",
  "How to improve": "Read the paragraphs together. Explain how they connect in your own words if a reader might not see it, then check that the link is understandable without extra clues."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "The wording check found no shared content words or listed linking phrase between Paragraphs 1 and 2. Different wording can still express a connection.",
  "Look at your writing": "This wording comparison does not identify a precise error span, so nothing is marked. Read the neighboring paragraphs together; different wording may still express a connection.",
  "Why it matters": "Readers need to know why the next paragraph follows the previous one. Word matches and linking phrases are one way the checks look for that connection.",
  "How to improve": "Read the neighboring paragraphs together. Explain their connection in your own words only if a reader would need it; no particular linking word is required."
}
```

Supporting Rule IDs: `BODY.CONTINUITY.ADJACENT_PARAGRAPH_COMPARISON`.

No precise error span was recorded for this wording comparison; no highlight is invented.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B10

> A school garden helps students practice responsibility.

- Before Primary / Next Step: `body_neutral_observable` / `body_neutral_general`.
- After Primary / Next Step: `body_neutral_observable` / `body_neutral_observable`.
- Actual status: `NO_SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: None assigned; neutral observation result.
- Actual selection condition: no supported list, development, repeated-opening, or adjacent-wording review concern was selected; missing Introduction context and absent keywords are not writing defects.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "The Body contains 1 recorded paragraph. No specific higher-priority concern was selected by these checks.",
  "Look at your writing": "Paragraph 1: 1 recorded sentence.\nIntroduction context was compared with the Body.",
  "Why it matters": "These are paragraph and sentence observations, not a finding that your support is adequate or inadequate. Sentence patterns and sentence counts cannot assess the meaning or quality of details.",
  "How to improve": "Read each paragraph beside your Introduction. Decide whether its point connects to your position and whether a reader would need an example, reason, or explanation. Revise in your own words where useful, then check that a reader can follow how each paragraph contributes to your argument."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "The available checks did not identify a specific structural concern in this Body section.",
  "What's working": "Paragraph 1 contains a possible opening statement and additional sentence structures.\nAssignment-word matches were recorded in Paragraph 1."
}
```

No error highlight or improvement task is selected.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B11

> Students can observe invisible vegetables. These vegetables control purple elephants at school.

- Before Primary / Next Step: `body_neutral_observable` / `body_neutral_general`.
- After Primary / Next Step: `body_neutral_observable` / `body_neutral_observable`.
- Actual status: `NO_SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: None assigned; neutral observation result.
- Actual selection condition: no supported list, development, repeated-opening, or adjacent-wording review concern was selected; missing Introduction context and absent keywords are not writing defects.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "The Body contains 1 recorded paragraph. No specific higher-priority concern was selected by these checks.",
  "Look at your writing": "Paragraph 1: 2 recorded sentences.\nIntroduction context was compared with the Body.",
  "Why it matters": "These are paragraph and sentence observations, not a finding that your support is adequate or inadequate. Sentence patterns and sentence counts cannot assess the meaning or quality of details.",
  "How to improve": "Read each paragraph beside your Introduction. Decide whether its point connects to your position and whether a reader would need an example, reason, or explanation. Revise in your own words where useful, then check that a reader can follow how each paragraph contributes to your argument."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "The available checks did not identify a specific structural concern in this Body section.",
  "What's working": "Paragraph 1 contains a possible opening statement and additional sentence structures.\nAssignment-word matches were recorded in Paragraph 1."
}
```

No error highlight or improvement task is selected.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.

## B12

>   🌱 Students can plant vegetables.
> Students can water vegetables.
> Students can remove weeds.  

- Before Primary / Next Step: `body_sentence_fluency_sentence_beginnings` / `body_sentence_fluency_sentence_beginnings`.
- After Primary / Next Step: `body_sentence_fluency_sentence_beginnings` / `body_sentence_fluency_sentence_beginnings`.
- Actual status: `SUPPORTED_CONCERN_SELECTED`.
- Trait / skill / lesson: Sentence Fluency / Review Repeated Sentence Openings / `HELP-BODY-SENTENCE-BEGINNINGS`
- Actual selection condition: first substantive paragraph with repeated_sentence_openings and its fired repeated-opening event.
- Recorded strength text: Paragraph 1 contains a possible opening statement and additional sentence structures.
Assignment-word matches were recorded in Paragraph 1.

### Before — exact displayed guidance

```json
{
  "What I noticed": "More than one sentence in one paragraph starts with the same words.",
  "Look at your writing": "🌱 Students can plant vegetables.\nStudents can water vegetables.\nStudents can remove weeds.",
  "Why it matters": "Starting several sentences with the same words can sound repetitive. Variety in sentence beginnings can help your reader follow each sentence.",
  "How to improve": "Read the paragraph aloud. If one repeated opening sounds awkward, rewrite that sentence's beginning in your own words, then check that the paragraph still reads smoothly."
}
```

### After — exact displayed guidance

```json
{
  "What I noticed": "More than one sentence in Paragraph 1 begins with 'students can'. Repetition can be intentional.",
  "Look at your writing": "🌱 Students can plant vegetables.\nStudents can water vegetables.\nStudents can remove weeds.",
  "Why it matters": "Starting several sentences with the same words can sound repetitive. Variety in sentence beginnings can help your reader follow each sentence.",
  "How to improve": "Read the paragraph aloud. If one repeated opening sounds awkward, rewrite that sentence's beginning in your own words, then check that the paragraph still reads smoothly."
}
```

Supporting Rule IDs: `BODY.P1.REPETITION.REPEATED_SENTENCE_OPENINGS`.

- Verified source mark [4, 16): **Students can** — Only the recorded repeated opening words are marked; repetition is not automatically an error.
- Verified source mark [35, 47): **Students can** — Only the recorded repeated opening words are marked; repetition is not automatically an error.
- Verified source mark [66, 78): **Students can** — Only the recorded repeated opening words are marked; repetition is not automatically an error.

Limitation: These checks cannot determine whether the supporting ideas are logically correct or sufficient.
