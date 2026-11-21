# StudyMate architecture (single-user online release)

- `security`: existing PIN setup/unlock/recovery and device-bound JWT.
- `academics`: subject, unit and topic syllabus APIs.
- `planner`: dated, timed study tasks linked to syllabus topics.
- `flashcards`: subject decks, question/answer cards and spaced review.
- `progress`: completed planner-time analytics.
- `core`: health, dashboard and preferences.
- `study`: canonical database models and view/serializer implementations retained under their existing Django app label to protect existing database tables.

The Flutter app is online-only. It sends requests directly to Django and does not implement offline synchronization or upload/download workflows. The dashboard calculates syllabus completion from completed planner durations, capped at each topic's estimated teaching time.

Legacy material/synchronization model tables are retained in `study.models` only to avoid destructive schema changes to an existing database. They are not registered as API routes in this release.
