# EssayScaff V2 — defense smoke-test checklist

Verified against the repaired local application on 2026-10-23. Use designated
**demo** accounts and a demo classroom/assignment, not research accounts. No
account deletion or database migration is needed for this rehearsal.

## 1. Automated preflight — before starting the presentation server

Open PowerShell in `C:\Users\My Pc\Desktop\EssayScaff-V2` and run:

```powershell
& ".venv\Scripts\python.exe" -B -m pytest -q -p no:cacheprovider --tb=short
node --check static/app.js
node --check static/teacher.js
node --check static/research_inspector.js
& ".venv\Scripts\python.exe" -B tests\pre_defense_audit.py --publish-evidence
& ".venv\Scripts\python.exe" -B tests\transparency_browser_check.py
```

Expected: **572 passing tests**, successful syntax checks, both Chrome runners
exit successfully, no unhandled JS errors, and database/research-file checksum
checks pass. The runners use temporary isolated databases and print artifact
locations. The audit's startup probe requires port 5000 to be free; it does not
stop an existing server. A failure or NOT TESTED result needs investigation.

## 2. Start and verify the actual localhost application

```powershell
& ".venv\Scripts\python.exe" -B app.py
```

- [ ] Open Chrome at `http://127.0.0.1:5000/login`.
- [ ] Confirm the login page/logo loads; terminal shows DEBUG off and no traceback.
- [ ] Log in with an incorrect password once: generic error, no password displayed.
- [ ] Log in to the demo Teacher account; Dashboard opens.

## 3. Teacher task setup

- [ ] Open **My Classrooms → Create Classroom**. Create a demo English class and
  note its enrollment code (skip creation if reusing a designated demo class).
- [ ] Open **Assignments → Create Assignment**, choose that class and enter:
  - Title: `Defense Reading Demo`
  - Topic: `Should students read daily?`
  - Instructions: `Explain your point and include an example.`
  - Focus terms: `reading, students`
- [ ] Before student work exists, click **Edit**, adjust the instructions and
  **Save Changes**. Confirm the assignment appears.
- [ ] Open **Account**, use **Back to EssayScaff**, then **Log out**.

## 4. Student navigation and targeted feedback

- [ ] Log in to the demo Student account. Check Dashboard, My Classrooms,
  My Assignments, Writing Workspace and Chrome Back.
- [ ] Use **My Classrooms → Join a classroom**, enter the demo code and join.
  Use the classroom's **View assignments** and **Show all assignments** controls.
- [ ] Open **Writing Workspace → Free Writing / Practice**. Enter topic:
  `Should students be allowed to use smartphones during class?`
- [ ] Enter focus terms: `smartphones, students, classroom, learning, distractions`.
- [ ] Paste this exact Introduction and click **Analyze Now**:

```text
Smartphones are common in many classrooms, and students often use them to find information. Teachers can use smartphones for learning activities, such as looking up difficult words and reading educational materials. However, notifications and games can cause distractions during class. Although smartphones can also interrupt lessons. Schools should allow smartphones during teacher-guided activities because clear rules can help students focus on learning. And have slumber party at my aunt house
```

- [ ] **Main Feedback: Sentence Fluency · Complete Your Sentence** highlights only
  `Although smartphones can also interrupt lessons.`
- [ ] Click **Also Check: Ideas · Review Topic Connection**. It highlights only
  `And have slumber party at my aunt house`, with cautious review wording.
- [ ] Open **Show more feedback**, the optional Introduction guide and **Return
  to Writing**. Confirm your essay text is unchanged.
- [ ] Edit the Introduction: old feedback/highlights disappear until a current
  analysis returns. Save the practice draft before switching workspaces.

## 5. Assigned writing, persistence and submission

- [ ] **My Assignments → Defense Reading Demo → Start Writing** opens a separate
  assignment workspace; practice text/feedback must not appear there.
- [ ] Fill the stages with these demo texts:

| Stage | Demo text |
|---|---|
| Introduction | Students should read daily because reading helps students learn. |
| Body | Students read books. For example, they discuss the story with classmates. |
| Conclusion | Overall, students should read daily. |

- [ ] Analyze each stage, then open **Essay Review** and check all three sections.
- [ ] Click **Save Draft** and **Save Revision**. Saving the same revision again
  reports no new revision. Opening a revision is read-only and preserves the editor.
- [ ] Switch to Practice and back: independent saved text and current revision
  history restore. Refresh Chrome: saved writing survives.
- [ ] Open **Essay Review → Submit**, cancel once (essay remains editable), then
  submit the designated demo essay. Confirm read-only status and no duplicate.
- [ ] Log out/re-login: the same submitted demo essay restores.
- [ ] Teacher: **Assignments → Submissions → View Essay** shows the correct
  student's three sections. Task fields are locked after work; title editing remains.

## 6. Transparency and Inspector

- [ ] On a current student analysis, explore **Student Text**, **Language
  Analysis**, **Topic Check**, **Rule Check**, **Feedback Result**, and
  **Advanced Inspector**. Toggle Simple/Technical View; open the dependency,
  rule-decision and feedback-decision views. No new analysis/save is triggered.
- [ ] **Copy Full Analysis** contains the current stage's actual evidence.
- [ ] Teacher: open **NLP Research Inspector**, load its sample, **Analyze Sample**,
  select **Rule Execution**, filter `INTRO.REASON` and inspect the source:
  `IntroductionRuleBase._reason_clause_lexical_check`, not ConclusionRuleBase.
- [ ] Process navigation, **Copy JSON** and **Export JSON** work without storing
  the sample. Changing the sample disables the previous export until reanalysis.
- [ ] Inspect at 1440×900, 1366×768 and 390×844: account controls remain usable,
  no page-wide overflow, editor/tutor marks align. Technical tables may scroll locally.
- [ ] Log out. Revisiting `/teacher` or `/` redirects to login; protected API access
  is denied. Check Chrome console and server terminal for unexplained errors.

**Presentation wording:** “EssayScaff records linguistic and wording evidence and
offers non-generative revision prompts. These observations do not prove meaning,
logical support, correctness, essay quality or readiness.” Passing this checklist
supports the tested local demonstration; it does not establish universal freedom
from defects or semantic accuracy. See [the full audit](pre_defense_full_system_audit.md).
