export type User = { id: number; telegram_id: number; display_name: string }
export type Course = { id: number; name: string }
export type Student = { id: number; name: string }
export type Lesson = { id: number; title: string; kind: string; held_at: string; max_score: number }
export type RegisterRow = {
  student_id: number
  student_name: string
  present: boolean | null
  score: number | null
}
export type Register = { lesson: Lesson; students: RegisterRow[] }

declare global {
  interface Window {
    Telegram?: { WebApp?: { initData: string; ready(): void; expand(): void } }
  }
}
