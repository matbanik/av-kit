export let isQuitting = false

export function setQuitIntent(): void {
  isQuitting = true
}

export function resetQuitIntent(): void {
  isQuitting = false
}
