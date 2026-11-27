# NIGRAN-360 — API Contracts

Base: `/api/v1`
Auth: Bearer JWT in `Authorization` header.

## Auth
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /auth/login | None | Returns access_token |
| POST | /auth/logout | Required | Invalidates session |
| GET | /auth/me | Required | Current user info |

## Users (Admin only)
| Method | Path | Description |
|---|---|---|
| GET | /users | List all users |
| POST | /users | Create user |
| PATCH | /users/{id} | Update user |
| DELETE | /users/{id} | Deactivate user |

## Examinations
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /examinations | Examiner/Admin | List own exams |
| POST | /examinations | Examiner | Create exam |
| GET | /examinations/{id} | Authorized | Get exam |
| PATCH | /examinations/{id} | Examiner (owner) | Update exam |
| POST | /examinations/{id}/publish | Examiner | Publish exam |

## Questions
| Method | Path | Description |
|---|---|---|
| GET | /questions | List question bank |
| POST | /questions | Create question |
| PATCH | /questions/{id} | Update question |
| POST | /questions/bulk-import | Bulk import CSV/JSON |

## Enrollment
| Method | Path | Description |
|---|---|---|
| POST | /examinations/{id}/enroll | Enroll candidate(s) |
| GET | /examinations/{id}/enrollments | List enrolled |
| DELETE | /examinations/{id}/enroll/{candidate_id} | Remove candidate |

## Attempts
| Method | Path | Description |
|---|---|---|
| POST | /examinations/{id}/attempt | Start attempt (candidate) |
| GET | /attempts/{id} | Get attempt state |
| PUT | /attempts/{id}/answers/{question_id} | Save answer (upsert) |
| POST | /attempts/{id}/submit | Submit attempt |

## Monitoring
| Method | Path | Description |
|---|---|---|
| GET | /examinations/{id}/monitor | Active attempts (examiner) |
| POST | /examinations/{id}/announcements | Send announcement |
| GET | /examinations/{id}/announcements | List announcements |

## Grading
| Method | Path | Description |
|---|---|---|
| POST | /attempts/{id}/grade | Trigger auto-grade |
| PATCH | /attempts/{id}/answers/{q_id}/grade | Manual grade |

## Results
| Method | Path | Description |
|---|---|---|
| GET | /results/{id} | Get result |
| POST | /results/{id}/publish | Publish result |
| GET | /examinations/{id}/results | List exam results |

## Disputes
| Method | Path | Description |
|---|---|---|
| POST | /results/{id}/dispute | Submit dispute |
| GET | /disputes/{id} | Get dispute |
| PATCH | /disputes/{id} | Update status/decision |
| GET | /disputes/{id}/audit | Audit log |

## Reports & Verification
| Method | Path | Description |
|---|---|---|
| GET | /results/{id}/report | Download PDF |
| GET | /verify/{code} | Verify report by code |

## Analytics
| Method | Path | Description |
|---|---|---|
| GET | /examinations/{id}/analytics | Exam-level stats |
| GET | /questions/{id}/analytics | Question-level stats |
