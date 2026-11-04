export function outputTreeLabels(outputDir: string): { raw: string; compiled: string } {
  const root = outputDir.replace(/[\\/]+$/, '')
  return {
    raw: `${root}/raw`,
    compiled: `${root}/compiled`,
  }
}
