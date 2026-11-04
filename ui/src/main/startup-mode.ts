export const START_MINIMIZED_FLAG = '--start-minimized'

export function argvHasFlag(argv: readonly string[], flag: string): boolean {
  return argv.some((arg) => arg === flag)
}

export function shouldStartMinimized(argv: readonly string[]): boolean {
  return argvHasFlag(argv, START_MINIMIZED_FLAG)
}

export function shouldShowWindowAfterLoad(
  argv: readonly string[],
  hideWindow: boolean,
): boolean {
  return !shouldStartMinimized(argv) && !hideWindow
}

export function revealMainWindow(
  window: { show: () => void },
  argv: readonly string[],
  hideFromLoginLaunch: boolean,
): void {
  if (shouldShowWindowAfterLoad(argv, hideFromLoginLaunch)) {
    window.show()
  }
}
