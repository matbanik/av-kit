export const CONSOLE_LOG_FILE_SPEC_PATH = '{app_data}/logs/console.log'

export function consoleLogFileLabel(resolvedPath: string | undefined): string {
  if (resolvedPath === undefined || resolvedPath.trim() === '') {
    return CONSOLE_LOG_FILE_SPEC_PATH
  }
  return resolvedPath
}
