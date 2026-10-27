# Feedback system replacement — rollback point

Created 2026-10-22, immediately before Phase C (pre-replacement backup of the
student feedback system: Feedback wording/selection, tutor catalog, frontend
presentation, Process 07, and the tests that pin them).

Every `_ *.bak` file is an exact SHA256-verified copy of the original file.
`.bak` suffixes keep pytest and Node from collecting these copies.

Restore procedure (PowerShell):
`Copy-Item "_rollback_feedback_replacement\static_app.js.bak" "static\app.js" -Force`

File map (source path in the project -> backup name here):
- services/feedback_service.py -> feedback_service.py.bak
- content/lessons/feedback_help.json -> content_lessons_feedback_help.json.bak
- static/app.js -> static_app.js.bak
- static/style.css -> static_style.css.bak
- templates/index.html -> templates_index.html.bak
- tests/test_feedback_help.py -> tests_test_feedback_help.py.bak
- tests/test_feedback_provenance.py -> tests_test_feedback_provenance.py.bak
- tests/test_feedback_decision_flow.py -> tests_test_feedback_decision_flow.py.bak
- tests/test_live_body_feedback.py -> tests_test_live_body_feedback.py.bak
- tests/test_introduction_feedback_targeted.py -> tests_test_introduction_feedback_targeted.py.bak
- tests/test_body_rules.py -> tests_test_body_rules.py.bak
- tests/test_conclusion_rules.py -> tests_test_conclusion_rules.py.bak
- tests/test_before_subordinator_safeguard.py -> tests_test_before_subordinator_safeguard.py.bak
- tests/test_causal_transparency.py -> tests_test_causal_transparency.py.bak
- tests/test_rule_decision_tree.py -> tests_test_rule_decision_tree.py.bak
- tests/test_research_inspector.py -> tests_test_research_inspector.py.bak
- tests/test_interface_views.py -> tests_test_interface_views.py.bak
- tests/test_workspace_frontend.py -> tests_test_workspace_frontend.py.bak
- tests/test_nlp_transparency.py -> tests_test_nlp_transparency.py.bak
- tests/test_essay_analysis.py -> tests_test_essay_analysis.py.bak
- tests/transparency_browser_check.cjs -> tests_transparency_browser_check.cjs.bak
- tests/transparency_browser_check.py -> tests_transparency_browser_check.py.bak
- tests/introduction_tutor_cases.json -> tests_introduction_tutor_cases.json.bak
- tests/body_live_feedback_cases.json -> tests_body_live_feedback_cases.json.bak
- tests/causal_transparency_cases.json -> tests_causal_transparency_cases.json.bak

This folder is superseded by docs/traits_feedback_replacement_report.md when
the replacement is complete; do not delete it before final verification.
