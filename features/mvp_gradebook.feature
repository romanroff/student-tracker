Feature: Tenant-isolated teacher gradebook
  A teacher manages only their own courses, students, lessons, grades, and attendance.

  Scenario: A teacher records attendance and a grade for a lesson
    Given an authenticated teacher owns a course
    And the course contains a student
    And the course contains a lesson with a maximum score of 10
    When the teacher marks the student present with a score of 8
    Then the lesson register shows the student as present with a score of 8

  Scenario: Another teacher cannot access a course
    Given an authenticated teacher owns a course with students and lessons
    And another teacher is authenticated
    When the other teacher requests or changes that course
    Then the API does not expose or modify the course or its academic records

  Scenario: A teacher sees only their own courses
    Given two authenticated teachers each own a course
    When either teacher opens the Mini App
    Then only courses owned by that teacher are listed

  Scenario: Telegram authentication rejects a forged identity
    Given developer authentication is disabled
    When a user opens the API with missing, expired, or incorrectly signed Telegram init data
    Then the API returns an authentication error without creating a user
