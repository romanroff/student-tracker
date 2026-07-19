import { FormEvent, useCallback, useEffect, useState } from 'react'
import { api } from './api'
import { bootstrapSession } from './bootstrap'
import { runFormAction } from './form'
import type { Course, Lesson, Register, Student, User } from './types'

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [courses, setCourses] = useState<Course[]>([])
  const [courseId, setCourseId] = useState<number | null>(null)
  const [students, setStudents] = useState<Student[]>([])
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [lessonId, setLessonId] = useState<number | null>(null)
  const [register, setRegister] = useState<Register | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(true)
  const [retry, setRetry] = useState(0)

  const report = (action: () => Promise<unknown>) => async () => {
    setError('')
    try { await action() } catch (cause) { setError(cause instanceof Error ? cause.message : 'Ошибка') }
  }

  const loadCourses = useCallback(async () => {
    const values = await api.courses()
    setCourses(values)
    setCourseId((current) => current && values.some((item) => item.id === current) ? current : values[0]?.id ?? null)
  }, [])

  const loadCourse = useCallback(async () => {
    if (!courseId) { setStudents([]); setLessons([]); return }
    const [studentValues, lessonValues] = await Promise.all([api.students(courseId), api.lessons(courseId)])
    setStudents(studentValues)
    setLessons(lessonValues)
    setLessonId((current) => current && lessonValues.some((item) => item.id === current) ? current : lessonValues[0]?.id ?? null)
  }, [courseId])

  const loadRegister = useCallback(async () => {
    if (!courseId || !lessonId) { setRegister(null); return }
    setRegister(await api.register(courseId, lessonId))
  }, [courseId, lessonId])

  useEffect(() => { void bootstrapSession(api.me, loadCourses, setUser, setError, setBusy) }, [loadCourses, retry])
  useEffect(() => { report(loadCourse)() }, [loadCourse])
  useEffect(() => { report(loadRegister)() }, [loadRegister])

  async function addCourse(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const formElement = event.currentTarget; const form = new FormData(formElement); const name = String(form.get('name') ?? '').trim()
    if (!name) return; await runFormAction(formElement, async () => { await api.addCourse(name); await loadCourses() })
  }
  async function addStudent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!courseId) return; const formElement = event.currentTarget; const form = new FormData(formElement); const name = String(form.get('name') ?? '').trim()
    if (!name) return; await runFormAction(formElement, async () => { await api.addStudent(courseId, name); await loadCourse(); await loadRegister() })
  }
  async function addLesson(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!courseId) return; const formElement = event.currentTarget; const form = new FormData(formElement)
    await runFormAction(formElement, async () => {
      await api.addLesson(courseId, { title: String(form.get('title')), kind: String(form.get('kind')), held_at: new Date(String(form.get('held_at'))).toISOString(), max_score: Number(form.get('max_score')) })
      await loadCourse()
    })
  }
  async function saveRow(studentId: number, present: boolean | null, rawScore: string) {
    if (!courseId || !lessonId) return
    const score = rawScore === '' ? null : Number(rawScore)
    await api.saveRecord(courseId, lessonId, studentId, present, score); await loadRegister()
  }

  if (busy) return <main className="shell"><p className="loading">Загружаем журнал…</p></main>
  return <main className="shell">
    <header><div><p className="eyebrow">TELEGRAM MINI APP</p><h1>Student Tracker</h1></div><div className="user">{user?.display_name}</div></header>
    {error && <div className="error" role="alert">{error}<button onClick={() => user ? setError('') : setRetry((value) => value + 1)}>{user ? '×' : 'Повторить'}</button></div>}
    <section className="coursebar">
      <label>Курс<select value={courseId ?? ''} onChange={(e) => setCourseId(Number(e.target.value) || null)}><option value="">Выберите курс</option>{courses.map((course) => <option key={course.id} value={course.id}>{course.name}</option>)}</select></label>
      <form onSubmit={(event) => report(() => addCourse(event))()}><input name="name" placeholder="Новый курс" required/><button>Добавить</button></form>
      {courseId && <button className="danger" onClick={report(async () => { if (confirm('Удалить курс со всеми данными?')) { await api.deleteCourse(courseId); await loadCourses() } })}>Удалить курс</button>}
    </section>
    {!courseId ? <section className="empty"><h2>Создайте первый курс</h2><p>У каждого преподавателя будет собственный набор курсов и студентов.</p></section> : <div className="grid">
      <section className="card"><h2>Студенты <span>{students.length}</span></h2><form onSubmit={(event) => report(() => addStudent(event))()} className="stack"><input name="name" placeholder="ФИО студента" required/><button>Добавить студента</button></form><ul>{students.map((student) => <li key={student.id}><span>{student.name}</span><button aria-label={`Удалить ${student.name}`} onClick={report(async () => { await api.deleteStudent(courseId, student.id); await loadCourse(); await loadRegister() })}>×</button></li>)}</ul></section>
      <section className="card"><h2>Пары <span>{lessons.length}</span></h2><form onSubmit={(event) => report(() => addLesson(event))()} className="stack"><input name="title" placeholder="Тема пары" required/><input name="kind" placeholder="Тип пары" required/><input name="held_at" type="datetime-local" required/><label>Максимальный балл<input name="max_score" type="number" min="0" step="1" defaultValue="10" required/></label><button>Добавить пару</button></form><ul>{lessons.map((lesson) => <li key={lesson.id} className={lesson.id === lessonId ? 'active' : ''}><button className="lesson" onClick={() => setLessonId(lesson.id)}><span>{lesson.title}</span><small>{lesson.kind} · {new Date(lesson.held_at).toLocaleString('ru')} · {lesson.max_score} б.</small></button><button aria-label={`Удалить ${lesson.title}`} onClick={report(async () => { await api.deleteLesson(courseId, lesson.id); await loadCourse() })}>×</button></li>)}</ul></section>
    <section className="card register"><h2>Ведомость</h2>{!register ? <p className="muted">Выберите или добавьте пару.</p> : <><h3>{register.lesson.title}</h3><div className="table"><div className="tr th"><span>Студент</span><span>Посещение</span><span>Балл / {register.lesson.max_score}</span></div>{register.students.map((row) => <RecordRow key={`${row.student_id}-${String(row.present)}-${String(row.score)}`} row={row} max={register.lesson.max_score} save={saveRow}/>)}</div></>}</section>
    </div>}
  </main>
}

function RecordRow({ row, max, save }: { row: Register['students'][number]; max: number; save: (id: number, present: boolean | null, score: string) => Promise<void> }) {
  const [present, setPresent] = useState(row.present); const [score, setScore] = useState(row.score?.toString() ?? '')
  return <div className="tr"><strong>{row.student_name}</strong><select value={present === null ? '' : present ? 'yes' : 'no'} onChange={(e) => setPresent(e.target.value === '' ? null : e.target.value === 'yes')}><option value="">—</option><option value="yes">Был(а)</option><option value="no">Не был(а)</option></select><div className="score"><input type="number" min="0" max={max} step="0.5" value={score} onChange={(e) => setScore(e.target.value)}/><button onClick={() => save(row.student_id, present, score)}>✓</button></div></div>
}

export default App
