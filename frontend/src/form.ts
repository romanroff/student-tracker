export type ResettableForm = { reset: () => void }

export async function runFormAction(form: ResettableForm, action: () => Promise<void>): Promise<void> {
  await action()
  form.reset()
}
