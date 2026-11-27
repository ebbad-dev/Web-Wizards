# NIGRAN-360 — Database Design

## users
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| email | VARCHAR(255) UNIQUE | login identifier |
| full_name | VARCHAR(255) | |
| hashed_password | VARCHAR(255) | Argon2id |
| role | ENUM(administrator, examiner, candidate) | |
| is_active | BOOLEAN | soft-disable |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

## examinations
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| title | VARCHAR(500) | |
| instructions | TEXT | |
| status | ENUM(draft, published, ongoing, completed) | |
| scheduled_start | TIMESTAMPTZ | |
| scheduled_end | TIMESTAMPTZ | |
| duration_minutes | INT | |
| total_marks | INT | |
| passing_marks | INT | |
| randomize_questions | BOOLEAN | |
| randomize_choices | BOOLEAN | |
| created_by | VARCHAR FK→users | |
| is_sandbox | BOOLEAN | sandbox preview flag |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

## questions
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| question_text | TEXT | |
| question_type | ENUM(single_mcq, multi_select, written) | |
| difficulty | ENUM(easy, medium, hard) | |
| category | VARCHAR(255) | |
| marks | FLOAT | default per-question mark |
| model_answer | TEXT | for written questions |
| created_by | VARCHAR FK→users | |

## choices
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| question_id | VARCHAR FK→questions CASCADE | |
| choice_text | TEXT | |
| is_correct | BOOLEAN | |
| display_order | INT | |

## exam_questions
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| exam_id | VARCHAR FK→examinations CASCADE | |
| question_id | VARCHAR FK→questions | |
| display_order | INT | |
| marks_override | FLOAT NULL | override default marks |

## enrollments
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| exam_id | VARCHAR FK→examinations CASCADE | |
| candidate_id | VARCHAR FK→users CASCADE | |
| enrolled_at | TIMESTAMPTZ | |
| enrolled_by | VARCHAR FK→users | UNIQUE(exam_id, candidate_id) |

## attempts
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| exam_id | VARCHAR FK→examinations | |
| candidate_id | VARCHAR FK→users | |
| started_at | TIMESTAMPTZ | server time |
| deadline | TIMESTAMPTZ | started_at + duration |
| submitted_at | TIMESTAMPTZ NULL | |
| status | ENUM(in_progress, submitted, expired) | |
| is_sandbox | BOOLEAN | |
| question_order | JSON | frozen question id list |

## attempt_answers
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| attempt_id | VARCHAR FK→attempts CASCADE | |
| question_id | VARCHAR FK→questions | |
| selected_choice_ids | JSON NULL | list of choice ids |
| written_response | TEXT NULL | |
| is_marked_for_review | BOOLEAN | |
| auto_score | FLOAT NULL | computed on submit |
| manual_score | FLOAT NULL | examiner input |
| grader_note | TEXT NULL | |
| saved_at | TIMESTAMPTZ | last save time |

## results
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| attempt_id | VARCHAR FK→attempts UNIQUE | |
| exam_id | VARCHAR FK→examinations | |
| candidate_id | VARCHAR FK→users | |
| total_score | FLOAT | |
| max_score | FLOAT | |
| is_published | BOOLEAN | |
| published_at | TIMESTAMPTZ NULL | |
| verification_code | VARCHAR(64) UNIQUE | QR/URL verification |
| graded_at | TIMESTAMPTZ | |
| graded_by | VARCHAR FK→users NULL | |

## disputes
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| attempt_id | VARCHAR FK→attempts | |
| result_id | VARCHAR FK→results | |
| candidate_id | VARCHAR FK→users | |
| category | ENUM(grading_error, ambiguous_question, technical_incident, other) | |
| description | TEXT | |
| status | ENUM(submitted, under_review, resolved, rejected) | |
| original_score | FLOAT NULL | |
| revised_score | FLOAT NULL | |
| submitted_at | TIMESTAMPTZ | |
| resolved_at | TIMESTAMPTZ NULL | |
| resolved_by | VARCHAR FK→users NULL | |
| resolution_note | TEXT NULL | |

## dispute_audits
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| dispute_id | VARCHAR FK→disputes CASCADE | |
| action | VARCHAR(100) | e.g. "status_changed", "note_added" |
| actor_id | VARCHAR FK→users | |
| note | TEXT NULL | |
| created_at | TIMESTAMPTZ | immutable |

## exam_events
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| exam_id | VARCHAR FK→examinations | |
| attempt_id | VARCHAR FK→attempts NULL | |
| candidate_id | VARCHAR FK→users NULL | |
| event_type | VARCHAR(100) | e.g. "tab_switch", "submit" |
| details | TEXT NULL | |
| recorded_at | TIMESTAMPTZ | |

## announcements
| Column | Type | Notes |
|---|---|---|
| id | VARCHAR PK | UUID |
| exam_id | VARCHAR FK→examinations | |
| created_by | VARCHAR FK→users | |
| message | TEXT | |
| created_at | TIMESTAMPTZ | |
