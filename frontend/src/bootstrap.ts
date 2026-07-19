import type { User } from './types'

type SetValue<T> = (value: T) => void

export async function bootstrapSession(
  loadUser: () => Promise<User>,
  loadCourses: () => Promise<void>,
  setUser: SetValue<User | null>,
  setError: SetValue<string>,
  setBusy: SetValue<boolean>,
): Promise<void> {
  setBusy(true)
  try {
    setUser(await loadUser())
    await loadCourses()
  } catch (cause) {
    setError(cause instanceof Error ? cause.message : 'Ошибка')
  } finally {
    setBusy(false)
  }
}
