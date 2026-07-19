Feature: Manage a tenant-isolated gradebook through the Telegram bot
  A teacher uses Telegram buttons for routine student and lesson operations
  without opening the Mini App.

  Scenario: A teacher saves attendance for several students at once
    Given an authenticated Telegram teacher owns a course with a lesson and students
    And the teacher has selected attendance values using checkbox buttons
    When the teacher presses Save
    Then all selected attendance values are stored in one transaction
    And reopening the lesson shows the saved values

  Scenario: A teacher manages students from course buttons
    Given an authenticated Telegram teacher owns a course
    When the teacher adds or removes a student using the bot workflow
    Then the course student list reflects the change

  Scenario: A teacher adds several students in one message
    Given an authenticated Telegram teacher owns a course containing "Петров Пётр"
    When the teacher sends student names on separate lines including blanks and "Петров Пётр"
    Then every new non-empty name is added once
    And the existing student is skipped
    And the bot reports the added and skipped counts

  Scenario: A teacher records a score from the lesson register
    Given an authenticated Telegram teacher owns a lesson and student
    When the teacher enters a score within the lesson maximum
    Then the lesson register shows the saved score

  Scenario: A teacher imports a scored lesson plan
    Given an authenticated Telegram teacher owns a course
    When the teacher sends lines in "Название; тип; целый максимум" format
    Then all valid unique lessons are created in one transaction
    And every user-provided type is stored without interpretation
    And the bot reports the sum of maximum scores

  Scenario: An invalid lesson line rejects the complete import
    Given an authenticated Telegram teacher owns a course
    When one line has an empty type or a non-integer maximum score
    Then the bot reports the invalid line number
    And no lessons from that message are created

  Scenario: A teacher cannot operate on another teacher's course
    Given another Telegram teacher owns a course with students and lessons
    When the teacher submits callback identifiers for that course
    Then the bot reports that the resource is unavailable
    And no foreign academic record is changed

  Scenario: A teacher deletes a course after confirmation
    Given an authenticated Telegram teacher owns a course with students, lessons, and records
    When the teacher confirms course deletion
    Then the course and all of its academic data are deleted
    And another teacher cannot delete that course

  Scenario: A teacher downloads a course summary
    Given an authenticated Telegram teacher owns a course with lessons, students, and scores
    When the teacher presses the Markdown summary button
    Then the bot sends a .md document with one row per student
    And the table contains every lesson, average score, total score, and maximums
    And Markdown control characters in user data cannot break the table

  Scenario: A teacher downloads statistics for one student
    Given a course student has grades and explicit attendance records
    When the teacher selects the student
    Then the bot sends a .md report with every lesson, average, total, and attendance rate

  Scenario: A teacher finds debtors for a selected lesson
    Given a lesson has a teacher-provided passing score
    When the teacher requests debtors
    Then the bot sends a .md report containing students with a missing or lower score

  Scenario: A teacher deletes a lesson after confirmation
    Given a teacher owns a lesson with grades and attendance
    When the teacher confirms lesson deletion
    Then the lesson and its records are deleted
    And another teacher cannot delete the lesson
