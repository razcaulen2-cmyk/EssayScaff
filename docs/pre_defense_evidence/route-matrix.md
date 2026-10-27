# Generated Flask route audit

All rows are discovered from the real `app.url_map`.

| URL | Endpoint / function | Methods | Permission | Expected | Actual | Redirect | Status |
|---|---|---|---|---|---|---|---|
| `/static/<path:filename>` | `static` / `Flask.__init__.<locals>.<lambda>` | GET, HEAD, OPTIONS | public | asset | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/assets/essayscaff-logo.png` | `brand_logo` / `create_app.<locals>.brand_logo` | GET, HEAD, OPTIONS | public | asset | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/register` | `register` / `create_app.<locals>.register` | GET, HEAD, OPTIONS | public | HTML page or successful form redirect | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/register` | `create_account` / `create_app.<locals>.create_account` | OPTIONS, POST | public | HTML page or successful form redirect | POST 302; OPTIONS 200 | / | PASS |
| `/login` | `login` / `create_app.<locals>.login` | GET, HEAD, OPTIONS | public | HTML page or successful form redirect | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/login` | `authenticate_student` / `create_app.<locals>.authenticate_student` | OPTIONS, POST | public | HTML page or successful form redirect | POST 302; OPTIONS 200 | / | PASS |
| `/logout` | `logout` / `create_app.<locals>.logout` | OPTIONS, POST | authenticated STUDENT/TEACHER | HTML page or successful form redirect | POST 302; OPTIONS 302 | /login | PASS |
| `/account` | `account_settings` / `create_app.<locals>.account_settings` | GET, HEAD, OPTIONS | authenticated STUDENT/TEACHER | HTML page or successful form redirect | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/account/delete` | `delete_account` / `create_app.<locals>.delete_account` | OPTIONS, POST | authenticated STUDENT/TEACHER | HTML page or successful form redirect | POST 302; OPTIONS 302 | /login | PASS |
| `/` | `homepage` / `create_app.<locals>.homepage` | GET, HEAD, OPTIONS | authenticated STUDENT/TEACHER | HTML page or successful form redirect | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/teacher` | `teacher_dashboard` / `create_app.<locals>.teacher_dashboard` | GET, HEAD, OPTIONS | TEACHER + ownership | HTML page or successful form redirect | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/teacher/research-inspector` | `research_inspector` / `create_app.<locals>.research_inspector` | GET, HEAD, OPTIONS | TEACHER + ownership | HTML page or successful form redirect | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/research-inspector/metadata` | `research_inspector_metadata` / `create_app.<locals>.research_inspector_metadata` | GET, HEAD, OPTIONS | TEACHER + ownership | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/teacher/classrooms` | `create_classroom` / `create_app.<locals>.create_classroom` | OPTIONS, POST | TEACHER + ownership | HTML page or successful form redirect | POST 302; OPTIONS 200 | /teacher | PASS |
| `/teacher/assignments` | `create_assignment` / `create_app.<locals>.create_assignment` | OPTIONS, POST | TEACHER + ownership | HTML page or successful form redirect | POST 302; OPTIONS 200 | /teacher | PASS |
| `/teacher/assignments/<int:assignment_id>/edit` | `edit_assignment` / `create_app.<locals>.edit_assignment` | GET, HEAD, OPTIONS, POST | TEACHER + ownership | HTML page or successful form redirect | GET 200; POST 302; HEAD 200; OPTIONS 200 | /teacher | PASS |
| `/teacher/assignments/<int:assignment_id>/delete` | `delete_assignment` / `create_app.<locals>.delete_assignment` | OPTIONS, POST | TEACHER + ownership | HTML page or successful form redirect | POST 302; OPTIONS 200 | /teacher | PASS |
| `/teacher/assignments/<int:assignment_id>/classroom` | `assign_legacy_assignment` / `create_app.<locals>.assign_legacy_assignment` | OPTIONS, POST | TEACHER + ownership | HTML page or successful form redirect | POST 302; OPTIONS 200 | /teacher | PASS |
| `/api/assignments` | `available_assignments` / `create_app.<locals>.available_assignments` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/archived-assignments` | `student_archived_assignments` / `create_app.<locals>.student_archived_assignments` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/classrooms` | `student_classrooms` / `create_app.<locals>.student_classrooms` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/classroom-enrollments` | `enroll_student` / `create_app.<locals>.enroll_student` | OPTIONS, POST | STUDENT + ownership/enrollment | JSON object | POST 200; OPTIONS 200 | — | PASS |
| `/api/classrooms/<int:classroom_id>/assignments` | `classroom_assignments` / `create_app.<locals>.classroom_assignments` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/assignments/<int:assignment_id>/workspace` | `assignment_workspace` / `create_app.<locals>.assignment_workspace` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/submissions` | `submit_assignment` / `create_app.<locals>.submit_assignment` | OPTIONS, POST | STUDENT + ownership/enrollment | JSON object | POST 200; OPTIONS 200 | — | PASS |
| `/api/submissions/<int:assignment_id>` | `student_submission` / `create_app.<locals>.student_submission` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/teacher/assignments/<int:assignment_id>/submissions` | `teacher_assignment_submissions` / `create_app.<locals>.teacher_assignment_submissions` | GET, HEAD, OPTIONS | TEACHER + ownership | HTML page or successful form redirect | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/teacher/submissions/<int:submission_id>` | `teacher_submission_view` / `create_app.<locals>.teacher_submission_view` | GET, HEAD, OPTIONS | TEACHER + ownership | HTML page or successful form redirect | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/analyze-introduction` | `analyze_introduction` / `create_app.<locals>.analyze_introduction` | OPTIONS, POST | STUDENT + ownership/enrollment | JSON object | POST 200; OPTIONS 200 | — | PASS |
| `/api/analyze-stage` | `analyze_stage` / `create_app.<locals>.analyze_stage` | OPTIONS, POST | STUDENT + ownership/enrollment | JSON object | POST 200; OPTIONS 200 | — | PASS |
| `/api/research-inspector/analyze` | `analyze_research_inspector` / `create_app.<locals>.analyze_research_inspector` | OPTIONS, POST | TEACHER + ownership | JSON object | POST 200; OPTIONS 200 | — | PASS |
| `/api/drafts` | `save_draft` / `create_app.<locals>.save_draft` | OPTIONS, POST | STUDENT + ownership/enrollment | JSON object | POST 200; OPTIONS 200 | — | PASS |
| `/api/drafts` | `restore_draft` / `create_app.<locals>.restore_draft` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/revisions` | `save_revision` / `create_app.<locals>.save_revision` | OPTIONS, POST | STUDENT + ownership/enrollment | JSON object | POST 200; OPTIONS 200 | — | PASS |
| `/api/revisions` | `list_revisions` / `create_app.<locals>.list_revisions` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
| `/api/revisions/<revision_id>` | `view_revision` / `create_app.<locals>.view_revision` | GET, HEAD, OPTIONS | STUDENT + ownership/enrollment | JSON object | GET 200; HEAD 200; OPTIONS 200 | — | PASS |
