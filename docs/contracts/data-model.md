# Data Model Contract

## Entities

- `User`: internal id, Telegram user id (unique), profile metadata, timestamps.
- `Course`: id, owner user id, name, timestamps, archival state.
- `CourseMember`: course id, user id, role; unique per pair.
- `Student`: id, course id, display name, optional external identifier, status.
- `Lesson`: id, course id, name, user-provided type string, held-at timestamp,
  and non-negative maximum score.
- `Grade`: student id, topic id, score, author user id, timestamps.
- `Attendance`: student id, topic id, presence state, author user id, timestamps.

The lesson type is descriptive and does not determine scoring behavior. Grades
must be between zero and the lesson maximum. Student/lesson pairs must belong
to the same course. Grade and
attendance uniqueness is one record per student/topic unless history is added
by an ADR. Every query is course-scoped after authorization.

PostgreSQL is authoritative in production; SQLite is a development adapter.
Alembic owns schema migrations.
