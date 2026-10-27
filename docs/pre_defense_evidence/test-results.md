# Recorded test execution results

2026-10-23, project `EssayScaff-V2`, existing `.venv` and installed Chrome/Node.

| Execution | Observed result |
|---|---|
| Initial full pytest baseline | 549 passed in 108.69 s |
| Initial reproduced-defect module, before repairs | ID overflow, source mapping, revision loading, clean-save switch and storage-failure regressions failed as documented in confirmed-defects.log |
| Repairs + auth/assignment/NLP integrations | 48 passed |
| Repairs + complete route/system + inspector/NLP integrations | 37 passed |
| Final full pytest suite after production repairs | **572 passed in 257.97 s**, browser suites running concurrently |
| Final extended route/fixture checks | **3 passed in 9.04 s** |
| Static app.js / teacher.js / research_inspector.js syntax | PASS |
| Both browser-check CJS syntax | PASS |
| Full existing transparency Chrome suite | PASS; no JavaScript errors; zero saved writing/revision/submission rows |
| New complete-route and CRUD workflow Chrome audit | PASS; no unhandled JS/console errors or unexplained HTTP failures |
| CLI linguistic/topic smoke | Exit 0; valid JSON; real installed spaCy and WordNet |
| pip check | No broken requirements |

Full-suite command:

```powershell
& ".venv\Scripts\python.exe" -B -m pytest -q -p no:cacheprovider --tb=short
```

No failing test was deleted and no protected hash expectation was replaced.
The source-pointer compatibility projection is documented in the main report
and its corrected current values have independent real-analysis regressions.
