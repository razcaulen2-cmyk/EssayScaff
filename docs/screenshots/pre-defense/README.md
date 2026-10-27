# Actual pre-defense Chrome screenshots

`audit-*.png` captures are from the final isolated Student/Teacher workflow audit
at 1440×900, 1366×768 and 390×844, plus specific repaired states. Their hashes
are listed in `../../pre_defense_evidence/screenshots.json`.

Additional captures from the full transparency/browser regression:

- `transparency-simple-desktop.png`, `transparency-simple-mobile.png`
- `feedback-flow-intro-desktop.png`
- `rule-tree-incomplete-subordinator-mobile-summary.png`
- `introduction-quality-desktop-main-editor.png`
- `introduction-quality-mobile-also-tutor.png`

These additional images came from the verified full-Chrome run at
`Temp/opencode/essayscaff-transparency-_da7be1q`; they are not part of the separate
workflow screenshot manifest. Desktop transparency captures use 1440×1000;
the separate workflow audit supplies the required 1440×900/laptop measurements.

`audit-inspector-mobile-before.png` is an actual failing pre-repair Inspector
capture from `Temp/opencode/essayscaff-pre-defense-25p1tasz`, whose overflow
diagnostics measured a 528px layout for the requested 390px mobile viewport.
It is deliberately retained as **before** evidence, not a current passing state.

Screenshots demonstrate rendering. Assertions, real API records, timing/context
probes and persistence/integrity checks in the audit are the functional evidence.
All shown accounts and writing samples are disposable authored test fixtures.
