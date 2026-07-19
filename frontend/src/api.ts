import type { Course, Lesson, Register, Student, User } from './types'

const apiBase = import.meta.env.VITE_API_URL ?? ''

export function authHeaders(): Record<string, string> {
  const initData = window.Telegram?.WebApp?.initData
  if (initData) return { 'X-Telegram-Init-Data': initData }
  return {
    'X-Dev-Telegram-User-Id': import.meta.env.VITE_DEV_USER_ID ?? '101',
    'X-Dev-Telegram-Name': encodeURIComponent(import.meta.env.VITE_DEV_USER_NAME ?? 'Локальный преподаватель'),
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...init.headers },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Ошибка запроса' }))
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Ошибка запроса')
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  me: () => request<User>('/api/v1/me'),
  courses: () => request<Course[]>('/api/v1/courses'),
  addCourse: (name: string) => request<Course>('/api/v1/courses', { method: 'POST', body: JSON.stringify({ name }) }),
  deleteCourse: (id: number) => request<void>(`/api/v1/courses/${id}`, { method: 'DELETE' }),
  students: (courseId: number) => request<Student[]>(`/api/v1/courses/${courseId}/students`),
  addStudent: (courseId: number, name: string) => request<Student>(`/api/v1/courses/${courseId}/students`, { method: 'POST', body: JSON.stringify({ name }) }),
  deleteStudent: (courseId: number, id: number) => request<void>(`/api/v1/courses/${courseId}/students/${id}`, { method: 'DELETE' }),
  lessons: (courseId: number) => request<Lesson[]>(`/api/v1/courses/${courseId}/lessons`),
  addLesson: (courseId: number, data: Omit<Lesson, 'id'>) => request<Lesson>(`/api/v1/courses/${courseId}/lessons`, { method: 'POST', body: JSON.stringify(data) }),
  deleteLesson: (courseId: number, id: number) => request<void>(`/api/v1/courses/${courseId}/lessons/${id}`, { method: 'DELETE' }),
  register: (courseId: number, lessonId: number) => request<Register>(`/api/v1/courses/${courseId}/lessons/${lessonId}/register`),
  saveRecord: (courseId: number, lessonId: number, studentId: number, present: boolean | null, score: number | null) =>
    request(`/api/v1/courses/${courseId}/lessons/${lessonId}/students/${studentId}`, { method: 'PUT', body: JSON.stringify({ present, score }) }),
}
