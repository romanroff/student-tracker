# UI Contract

The target UI is a responsive React/TypeScript Telegram Mini App for teachers.
The first slice is: authenticate, choose/create a course, view its students,
and add a student without exposing another user's data.

Every screen must define loading, empty, validation, error, forbidden, and
offline/retry states. Destructive actions require explicit confirmation and
must report success or failure. Tables remain usable on mobile screens. Forms
are keyboard accessible, labels are programmatically associated, focus is
managed after dialogs/errors, and color is not the only status signal.

The UI treats API data as untrusted, never makes authorization decisions on its
own, and never stores the bot token. Stable behavior is covered by component
tests; the primary teacher flow is covered by Playwright.

Telegram bulk lesson entry accepts one `Название; тип; целый максимум` record
per line. Invalid messages identify the failing line and create no lessons.
The success message reports added/skipped counts and the submitted maximum-score
sum. Lesson type is displayed verbatim and is not interpreted by the UI.

The Telegram course menu exposes a destructive delete button. It opens a
separate confirmation message naming the course and warning that students,
lessons, grades, and attendance will also be deleted. Cancellation returns to
the course unchanged.

The Telegram course menu also exposes `📊 Сводка (.md)`. It sends a UTF-8
GitHub-flavored Markdown file containing the course title, lesson columns,
student rows, average and total scores, and a maximum-score row. User-provided
pipe, slash, and newline characters are escaped so they cannot corrupt the
table.

Selecting a student sends a Markdown document with lesson-level score and
attendance, assigned-score average and total, and the explicit attendance rate.
The selected-lesson menu requests a passing score before sending a debtors
Markdown document. Lesson deletion requires a separate destructive
confirmation and warns that scores and attendance will be removed.
