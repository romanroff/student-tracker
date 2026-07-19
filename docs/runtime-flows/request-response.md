# Mini App Request-Response Flow

1. Telegram opens the HTTPS Mini App and supplies `initData`.
2. React sends `initData` to FastAPI; it does not send a trusted standalone
   user id.
3. FastAPI validates signature and age, resolves/creates the application user,
   and establishes request identity.
4. The endpoint parses stable resource ids and validates the payload.
5. Authorization checks course ownership or membership before repository work.
6. A service applies domain invariants in a database transaction.
7. SQLAlchemy accesses SQLite locally or PostgreSQL in production.
8. FastAPI returns versioned JSON; the UI renders success or an explicit
   loading/empty/validation/forbidden/error state.

Authentication failures return 401. Authorized identity without sufficient
course rights returns a non-disclosing 403/404 policy chosen in an ADR. Invalid
input returns 422-compatible structured details. Conflicts return 409.
Unexpected failures return a correlation id, log no academic/personal payload,
and roll back the transaction.

## Telegram Bot Long-Polling Flow

1. `backend.app.bot_launcher` receives a Telegram update through long polling.
2. The Telegram sender id resolves or creates the application user.
3. Inline callback ids identify a requested course, lesson, or student but do
   not grant access.
4. `BotGradebook` checks course ownership before every read or mutation.
5. Attendance checkbox changes remain in per-user draft state until Save.
6. Save validates every selected student against the course and commits all
   attendance changes atomically; score updates validate the lesson maximum.
7. The bot renders success, empty, invalid-input, or unavailable-resource
   states without exposing another tenant's data.

For bulk student entry, one Telegram message contains one name per line. The
service validates course ownership, trims lines, ignores blanks, skips
duplicates, commits all new names atomically, and reports added/skipped counts.

For bulk lesson entry, one message contains semicolon-separated title, opaque
type string, and integer maximum score. The service parses and validates the
whole message before persistence, then inserts non-duplicate lessons in one
transaction and reports the submitted maximum-score total.

Course deletion uses a distinct confirmation callback. The service rechecks
ownership at confirmation time and deletes the course graph transactionally;
foreign or stale ids produce the same non-disclosing unavailable state.

Summary download rechecks ownership, reads all course lessons, students, and
scores, calculates averages/totals, renders Markdown into an in-memory byte
stream, and uploads it to Telegram as `course-N-summary.md`. No report file is
written to local storage.

Student statistics and debtors follow the same in-memory Markdown upload flow.
Attendance rate uses only explicit yes/no records. A debtors request validates
the passing score against the selected lesson maximum. Confirmed lesson
deletion rechecks course ownership and transactionally removes lesson records.
