const SECTIONS = [
  { testid: 'download-settings', title: 'Download Settings' },
  { testid: 'transcript-settings', title: 'Transcript Settings' },
  { testid: 'tts-settings', title: 'TTS Settings' },
  { testid: 'console-settings', title: 'Console & Logging' },
  { testid: 'appearance-settings', title: 'Appearance' },
  { testid: 'dependencies-section', title: 'Dependencies' },
] as const

export function SettingsChrome() {
  return (
    <div data-testid="settings-page" className="flex flex-col gap-4 p-4">
      <h1>Settings</h1>
      {SECTIONS.map((section) => (
        <section key={section.testid} data-testid={section.testid} className="border border-border p-3">
          <h2>{section.title}</h2>
        </section>
      ))}
    </div>
  )
}
