import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState, type ReactNode, type RefObject } from 'react'

import { HelpCard } from '../../components/help/HelpCard'
import { Button } from '../../components/ui/Button'
import { FormRow } from '../../components/ui/FormRow'
import { PathRow } from '../../components/ui/PathRow'
import { SegmentedControl } from '../../components/ui/SegmentedControl'
import { useG30Styles } from '../../components/ui/SelectInput'
import { StatusChip, type StatusChipTone } from '../../components/ui/StatusChip'
import { ApiError, apiFetch } from '../../lib/api'
import { consoleLogFileLabel } from '../../lib/console-log-path'
import { ariaKeyshortcuts } from '../../registry/shortcuts'
import { useConverterSettings } from '../converter/useConverterSettings'
import { useCaptureSettings } from '../capture/useCaptureSettings'
import { BACKUP_DIR_DEFAULT_NAME } from '../capture/capture-flatten'
import { ANNOTATED_FORMATS, type AnnotatedFormat } from './settings-schemas'
import {
  assetChip,
  assetGetVisible,
  presentAssetRows,
  QUERY_HEALTH_DEPENDENCIES,
  TTS_ASSET_LABELS,
  type TtsAssetRow,
} from '../tts/tts-assets'
import { postDownloadAsset } from '../tts/tts-commands'
import { buildDevices } from '../tts/tts-devices'
import { useModelsAvailable, useRefreshDependenciesOnSettle } from '../tts/useTtsJob'
import { GPU_PREF_WIRES, PRESET_LABELS, PRESET_WIRES, type GpuPrefWire, type PresetWire } from '../converter/convert-presets'
import {
  COOKIE_BROWSERS,
  cookieBrowserVisible,
  cookieFileVisible,
  type CookieMode,
} from '../downloader/cookie-bar'
import {
  AUDIO_DEFAULT,
  AUDIO_WIRE,
  QUALITY_DEFAULT,
  QUALITY_WIRE,
  type AudioWire,
  type QualityWire,
} from '../downloader/quality-options'
import { SETTINGS_COMMANDS, SETTINGS_EVENTS } from './settings-commands'
import { SETTINGS_HELP_SECTIONS } from './settings-help-content'
import { SETTINGS_NAMESPACE_PATHS } from './settings-paths'
import {
  CHECKBOX_COPY_SOURCES,
  NUMBER_HINT_SOURCES,
  SAVE_MODE_CAPTIONS,
  SETTINGS_SECTION_SET,
  readinessCount,
  type SettingsSection,
  type SettingsSectionKey,
} from './settings-sections'
import { revealSection, SettingsRail } from './SettingsRail'
import { sectionFrameProps } from './settings-section-frame'
import { StartAtSignInControl } from './StartAtSignInControl'
import { useTailSpacer } from './settings-tail-spacer'
import { SETTINGS_ERROR_EVENT, useSettingsPage } from './useSettingsPage'

const LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] as const
const TTS_OUTPUT_FORMATS = ['MP3', 'WAV'] as const
const ANNOTATED_FORMAT_LABELS: Record<AnnotatedFormat, string> = { png: 'PNG', jpeg: 'JPEG', webp: 'WebP' }
const ANNOTATED_FORMAT_OPTIONS = ANNOTATED_FORMATS.map((wire) => ({ value: wire, label: ANNOTATED_FORMAT_LABELS[wire] }))

type DependenciesOut = {
  yt_dlp: { available: boolean; version?: string | null; path?: string | null }
  ffmpeg: { available: boolean; path?: string | null; version?: string | null; ffprobe_available?: boolean }
  /** MEU-62; absent on an older backend, and then not rendered. */
  tts_onnx_vocab?: TtsAssetRow
  tts_spacy_model?: TtsAssetRow
  /** MEU-73. */
  tts_voice_packs?: TtsAssetRow
  /** MEU-74 `ESPEAK_DETECT`; absent on an older backend, and then not rendered. */
  tts_espeak?: EspeakDependency
  /** MEU-141 `RUNTIME_WIRE`; absent on an older backend, and then not rendered. */
  js_runtime?: JsRuntimeDependency
}

type JsRuntimeDependency = {
  available: boolean
  name: string | null
  path: string | null
  version: string | null
  source: 'setting' | 'bundled' | 'path' | null
  solver: boolean
}

type EspeakDependency = { available: boolean; version: string | null; path: string | null }

const ESPEAK_RELEASES_URL = 'https://github.com/espeak-ng/espeak-ng/releases'

// CLIENT_SET (MEU-71): mirrors MCP_CLIENTS in src/main/mcp-setup-prompt.ts, which builds the prompt text.
const MCP_CLIENT_OPTIONS = [
  { value: 'claude-code', label: 'Claude Code' },
  { value: 'codex', label: 'Codex' },
  { value: 'cursor', label: 'Cursor' },
  { value: 'vscode', label: 'VS Code' },
  { value: 'claude-desktop', label: 'Claude Desktop' },
  { value: 'windsurf', label: 'Windsurf (community)' },
  { value: 'generic', label: 'Other MCP client' },
] as const
type McpClientWire = (typeof MCP_CLIENT_OPTIONS)[number]['value']
type McpScopeWire = 'user' | 'project'
const MCP_SCOPE_OPTIONS = [
  { value: 'user', label: 'User (all projects)' },
  { value: 'project', label: 'This project only' },
] as const
// SCOPE_DISABLED: these clients have no project-scope config file.
const MCP_USER_ONLY_CLIENTS: readonly McpClientWire[] = ['claude-desktop', 'windsurf', 'generic']
const PROMPT_UNAVAILABLE = 'The setup prompt is not available in this window.'

const SECTION_BY_KEY = Object.fromEntries(SETTINGS_SECTION_SET.map((section) => [section.key, section])) as Record<
  SettingsSectionKey,
  SettingsSection
>

const SELECT_CLASS =
  'h-7 w-40 cursor-pointer rounded-[var(--radius-control)] border border-border bg-surface-0 px-2 text-sm text-fg focus:border-accent focus:outline-none'
const INPUT_CLASS = 'h-7 rounded-[var(--radius-control)] border border-border bg-surface-0 px-2 text-sm text-fg'
const NUMBER_CLASS = `${INPUT_CLASS} w-[5.25rem] text-right tabular-nums`

/** Unknown before the source has loaded: never render a fabricated ok/missing state (ST7). */
function checkChip(value: boolean | undefined, okLabel = 'ok', badLabel = 'missing'): { label: string; tone: StatusChipTone } {
  if (value === undefined) return { label: 'checking', tone: 'neutral' }
  return value ? { label: okLabel, tone: 'success' } : { label: badLabel, tone: 'warning' }
}

/** The version number from the `espeak-ng --version` first line; the whole line if none is found. */
function espeakVersionLabel(version: string | null): string | null {
  if (!version) return null
  return /\d+(?:\.\d+)+/.exec(version)?.[0] ?? version
}

/**
 * MEU-74: the user-installed eSpeak NG. av-kit never downloads or ships it, so the row has no
 * Get button. When it is absent, the guidance gives the releases URL as text with a Copy link
 * button, because the app has no external-link path (D-96).
 */
/** MEU-141 `RUNTIME_ROW` (D-648): the runtime yt-dlp is given, or what its absence costs. */
function JsRuntimeRow({ runtime }: { runtime: JsRuntimeDependency }): React.JSX.Element {
  const chip = checkChip(runtime.available, 'available', 'missing')
  const detail = [runtime.name, runtime.version, runtime.source, runtime.path].filter(
    (part): part is string => typeof part === 'string' && part.length > 0,
  )
  return (
    <li data-testid="deps-js-runtime-row" className="flex min-w-0 flex-col gap-1.5">
      <div className="flex min-w-0 items-center gap-2">
        <StatusChip label={chip.label} tone={chip.tone} />
        <span>JavaScript runtime</span>
        {runtime.available && detail.length > 0 ? (
          <span className="min-w-0 truncate font-mono text-xs text-fg-muted">{detail.join(' · ')}</span>
        ) : null}
      </div>
      {runtime.available ? null : (
        <span className="text-xs text-fg-muted">
          No JavaScript runtime found: yt-dlp runs without one, and some YouTube formats may be missing.
          Set a Deno path, or install Deno 2.3 or later.
        </span>
      )}
    </li>
  )
}

function EspeakRow({ espeak }: { espeak: EspeakDependency }): React.JSX.Element {
  const chip = checkChip(espeak.available, 'Detected', 'Not installed')
  const version = espeak.available ? espeakVersionLabel(espeak.version) : null
  return (
    <li data-testid="tts-espeak-row" className="flex min-w-0 flex-col gap-1.5">
      <div className="flex min-w-0 items-center gap-2">
        <StatusChip label={chip.label} tone={chip.tone} />
        <span>eSpeak NG</span>
        {version ? (
          <span className="min-w-0 truncate font-mono text-xs text-fg-muted" title={espeak.path ?? undefined}>
            {version}
          </span>
        ) : null}
      </div>
      {espeak.available ? null : (
        <div data-testid="tts-espeak-guidance" className="flex min-w-0 flex-col gap-1 text-xs text-fg-muted">
          <span>Spanish, French, Hindi, Italian and Portuguese voices need eSpeak NG. Install it from:</span>
          <div className="flex min-w-0 items-center gap-2">
            <span className="min-w-0 truncate font-mono select-all">{ESPEAK_RELEASES_URL}</span>
            <Button
              data-testid="tts-espeak-copy-link-btn"
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => {
                void window.api.writeClipboardText(ESPEAK_RELEASES_URL)
              }}
            >
              Copy link
            </Button>
          </div>
        </div>
      )}
    </li>
  )
}

function SettingsSectionFrame({
  sectionKey,
  current,
  caption,
  sectionRef,
  children,
  footer,
}: {
  sectionKey: SettingsSectionKey
  /** ACTIVE_SOURCE: whether the rail marks this section current (SECTION_EMPHASIS). */
  current: boolean
  caption?: ReactNode
  sectionRef?: RefObject<HTMLElement | null>
  children: ReactNode
  footer?: ReactNode
}): React.JSX.Element {
  const section = SECTION_BY_KEY[sectionKey]
  const mode = section.mode
  const modeCaption =
    caption ?? (mode === 'none' || mode === 'readiness-count' ? undefined : SAVE_MODE_CAPTIONS[mode])
  return (
    <section
      ref={sectionRef}
      tabIndex={-1}
      data-testid={section.testId}
      data-settings-section={section.key}
      {...sectionFrameProps(current)}
    >
      <div className="flex items-baseline gap-3 border-b border-bg-elevated pb-1">
        <h2 className="text-[15px] font-semibold">{section.label}</h2>
        {modeCaption !== undefined ? (
          <span data-testid={`settings-mode-${section.key}`} className="text-xs text-fg-muted">
            {modeCaption}
          </span>
        ) : null}
      </div>
      {children}
      {footer !== undefined ? <div className="flex justify-end">{footer}</div> : null}
    </section>
  )
}

/** Native select in the 168px label grid (G30 styling; one accessible label via FormRow). */
function GridSelect({
  id,
  label,
  testId,
  value,
  options,
  onChange,
  disabled,
  hint,
}: {
  id: string
  label: string
  testId: string
  value: string
  options: ReadonlyArray<{ value: string; label: string }>
  onChange: (value: string) => void
  disabled?: boolean
  hint?: string
}): React.JSX.Element {
  const g30 = useG30Styles()
  return (
    <FormRow id={id} label={label} hint={hint}>
      <select
        data-testid={testId}
        className={SELECT_CLASS}
        disabled={disabled}
        style={g30}
        value={value}
        onChange={(event) => {
          onChange(event.target.value)
        }}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value} style={g30}>
            {option.label}
          </option>
        ))}
      </select>
    </FormRow>
  )
}

function CheckboxRow({
  id,
  label,
  leaf,
  testId,
  checked,
  onChange,
  suffix,
}: {
  id: string
  label: string
  leaf: string
  /** Literal leaf test ID, kept greppable in this file for the source contracts. */
  testId: string
  checked: boolean
  onChange: (checked: boolean) => void
  suffix?: ReactNode
}): React.JSX.Element {
  return (
    <FormRow id={id} label={label} hint={CHECKBOX_COPY_SOURCES[leaf]} suffix={suffix}>
      <input
        type="checkbox"
        data-testid={testId}
        checked={checked}
        onChange={(event) => {
          onChange(event.target.checked)
        }}
      />
    </FormRow>
  )
}

function NumberRow({
  id,
  label,
  leaf,
  testId,
  value,
  onChange,
}: {
  id: string
  label: string
  leaf: string
  /** Literal leaf test ID, kept greppable in this file for the source contracts. */
  testId: string
  value: number | string
  onChange: (value: number) => void
}): React.JSX.Element {
  return (
    <FormRow id={id} label={label} hint={NUMBER_HINT_SOURCES[leaf]}>
      <input
        type="number"
        data-testid={testId}
        className={NUMBER_CLASS}
        value={value}
        onChange={(event) => {
          onChange(Number(event.target.value))
        }}
      />
    </FormRow>
  )
}

export function SettingsPage() {
  const queryClient = useQueryClient()
  const { downloaderQuery, transcriptQuery, ttsQuery, appQuery, uiQuery, schedulePut, putNow, runSettingsAction } =
    useSettingsPage()
  const converter = useConverterSettings()
  const capture = useCaptureSettings()
  const depsSectionRef = useRef<HTMLElement>(null)
  const ttsSectionRef = useRef<HTMLElement>(null)
  const pageRef = useRef<HTMLDivElement>(null)
  const [startupAvailable, setStartupAvailable] = useState(false)
  const g30 = useG30Styles()

  const depsQuery = useQuery({
    queryKey: QUERY_HEALTH_DEPENDENCIES,
    queryFn: async () => apiFetch<DependenciesOut>('/health/dependencies'),
  })
  useRefreshDependenciesOnSettle()

  const readinessQuery = useQuery({
    queryKey: ['setup', 'readiness'],
    queryFn: async () => window.api.getSetupReadiness(),
  })

  const mcpQuery = useQuery({
    queryKey: ['mcp', 'access'],
    queryFn: async () => window.api.getMcpAccessStatus(),
  })

  const [settingsError, setSettingsError] = useState<string | null>(null)

  const [mcpClient, setMcpClient] = useState<McpClientWire>('claude-code')
  const [mcpScope, setMcpScope] = useState<McpScopeWire>('user')
  const [mcpPrompt, setMcpPrompt] = useState('')
  const [mcpPromptStatus, setMcpPromptStatus] = useState('')
  const mcpPromptAvailable = window.api.getMcpSetupPrompt !== undefined
  const mcpScopeLocked = MCP_USER_ONLY_CLIENTS.includes(mcpClient)
  const mcpEffectiveScope: McpScopeWire = mcpScopeLocked ? 'user' : mcpScope

  useEffect(() => {
    const getPrompt = window.api.getMcpSetupPrompt
    setMcpPromptStatus('')
    if (getPrompt === undefined) {
      setMcpPrompt(PROMPT_UNAVAILABLE)
      return
    }
    // Clear first, so a failed fetch never leaves another pair's text to copy.
    setMcpPrompt('')
    let current = true
    void runSettingsAction('general', async () => {
      const { text } = await getPrompt({ client: mcpClient, scope: mcpEffectiveScope })
      if (current) {
        setMcpPrompt(text)
      }
    })
    return () => {
      current = false
    }
  }, [mcpClient, mcpEffectiveScope, runSettingsAction])

  const downloader = downloaderQuery.data
  const transcript = transcriptQuery.data
  const tts = ttsQuery.data
  const modelsQuery = useModelsAvailable()
  const storedDevice = tts?.device ?? 'auto'
  // DEVICE_OPTIONS (D-314): what this build reports; until the report arrives, or if it fails,
  // the floor plus the stored value. A stored value it can't offer shows as auto and is kept.
  const deviceOptions = modelsQuery.isSuccess
    ? buildDevices(modelsQuery.data.items)
    : buildDevices([{ devices: [storedDevice] }])
  const deviceValue = deviceOptions.includes(storedDevice) ? storedDevice : 'auto'
  const appSettings = appQuery.data
  const uiSettings = uiQuery.data

  const cookieMode = (downloader?.cookie_mode ?? 'none') as CookieMode

  useEffect(() => {
    const onCheckDeps = () => {
      void depsQuery.refetch()
      void readinessQuery.refetch()
    }
    const onSettingsError = (event: Event) => {
      const detail = (event as CustomEvent<{ message?: string }>).detail
      setSettingsError(detail?.message ?? 'Settings validation failed')
    }
    window.addEventListener(SETTINGS_EVENTS.checkDeps, onCheckDeps)
    window.addEventListener(SETTINGS_ERROR_EVENT, onSettingsError)
    return () => {
      window.removeEventListener(SETTINGS_EVENTS.checkDeps, onCheckDeps)
      window.removeEventListener(SETTINGS_ERROR_EVENT, onSettingsError)
    }
  }, [depsQuery, readinessQuery])

  const ffmpegAvailable = depsQuery.data?.ffmpeg?.available ?? false
  const readiness = readinessQuery.data

  function focusSection(section: HTMLElement | null): void {
    if (section !== null) {
      revealSection(section)
    }
  }

  async function browseDownloadPath(): Promise<void> {
    await runSettingsAction('downloader', async () => {
      const path = await window.api.showDirectoryDialog()
      if (path === undefined) {
        return
      }
      await putNow('downloader', { path })
    })
  }

  async function browseFfmpeg(): Promise<void> {
    await runSettingsAction('downloader', async () => {
      const chosen = await window.api.showFileDialog([{ name: 'Executables', extensions: ['exe', ''] }])
      if (chosen === undefined) {
        return
      }
      await putNow('downloader', { ffmpeg_path: chosen })
    })
  }

  async function browseDeno(): Promise<void> {
    await runSettingsAction('downloader', async () => {
      const chosen = await window.api.showFileDialog([{ name: 'Executables', extensions: ['exe', ''] }])
      if (chosen === undefined) {
        return
      }
      await putNow('downloader', { deno_path: chosen })
    })
  }

  async function browseCookieFile(): Promise<void> {
    await runSettingsAction('downloader', async () => {
      const chosen = await window.api.showFileDialog([{ name: 'Text', extensions: ['txt'] }])
      if (chosen === undefined) {
        return
      }
      await putNow('downloader', { cookie_file_path: chosen })
    })
  }

  async function browseTranscriptDir(): Promise<void> {
    await runSettingsAction('transcript', async () => {
      const chosen = await window.api.showDirectoryDialog()
      if (chosen === undefined) {
        return
      }
      await putNow('transcript', { output_dir: chosen })
    })
  }

  async function browseModelsDir(): Promise<void> {
    await runSettingsAction('tts', async () => {
      const chosen = await window.api.showDirectoryDialog()
      if (chosen === undefined) {
        return
      }
      await putNow('tts', { models_directory: chosen })
    })
  }

  async function browseTtsOutputPath(): Promise<void> {
    await runSettingsAction('tts', async () => {
      const chosen = await window.api.showDirectoryDialog()
      if (chosen === undefined) {
        return
      }
      await putNow('tts', { output_path: chosen })
    })
  }

  async function applyDefaults(): Promise<void> {
    await runSettingsAction('downloader', async () => {
      await apiFetch('/downloads/apply-defaults', { method: 'POST' })
      await queryClient.invalidateQueries({ queryKey: ['downloads'] })
    })
  }

  function checkDependencies(): void {
    SETTINGS_COMMANDS.checkDeps()
  }

  async function copyMcp(pinEndpoint: boolean): Promise<void> {
    await runSettingsAction('general', async () => {
      await window.api.copyMcpConfig({ pinEndpoint })
    })
  }

  async function copyMcpPrompt(): Promise<void> {
    const label = MCP_CLIENT_OPTIONS.find((option) => option.value === mcpClient)?.label ?? mcpClient
    await runSettingsAction('general', async () => {
      await window.api.writeClipboardText(mcpPrompt)
      setMcpPromptStatus(`Copied the ${label} setup prompt.`)
    })
  }

  const readinessLoaded = readinessCount(readiness, depsQuery.data?.ffmpeg?.available)
  const sections = SETTINGS_SECTION_SET.filter((section) => section.key !== 'startup' || startupAvailable)
  // TAIL_SPACER (MEU-70, plan D-9/D-16): lets the last section scroll up to the rail's top band.
  const tailSpacer = useTailSpacer(pageRef, sections.map((section) => section.key).join('|'))
  // ACTIVE_SOURCE (MEU-70, plan D-15): the rail's active entry, reported by SettingsRail.
  const [currentSection, setCurrentSection] = useState<SettingsSectionKey | null>(null)
  const dots: Partial<Record<SettingsSectionKey, boolean>> = {
    convert: converter.isDirty,
    capture: capture.isDirty,
    readiness: readinessLoaded !== null && readinessLoaded.ready < readinessLoaded.total,
  }
  const ytDlp = depsQuery.data?.yt_dlp
  const ffmpeg = depsQuery.data?.ffmpeg
  const ffprobeChip = checkChip(
    depsQuery.data === undefined ? undefined : ffmpeg?.ffprobe_available === true,
    'available',
    'missing',
  )
  const readinessRows: Array<{ label: string; value: boolean | undefined; link?: ReactNode }> = [
    {
      label: 'Descriptor present',
      value: readiness?.descriptorPresent,
      link:
        readiness?.descriptorPresent === false ? (
          <Button data-testid="readiness-descriptor-link" type="button" size="sm" variant="secondary" onClick={() => {
            focusSection(depsSectionRef.current)
          }}>
            Fix
          </Button>
        ) : null,
    },
    {
      label: 'Backend port OK',
      value: readiness?.portOk,
      link:
        readiness?.portOk === false ? (
          <Button data-testid="readiness-port-link" type="button" size="sm" variant="secondary" onClick={() => {
            focusSection(depsSectionRef.current)
          }}>
            Fix
          </Button>
        ) : null,
    },
    {
      label: 'Models directory writable',
      value: readiness?.modelsDirWritable,
      link:
        readiness?.modelsDirWritable === false ? (
          <Button data-testid="readiness-models-link" type="button" size="sm" variant="secondary" onClick={() => {
            focusSection(ttsSectionRef.current)
          }}>
            Fix
          </Button>
        ) : null,
    },
    {
      label: 'FFmpeg available',
      value: depsQuery.data === undefined ? undefined : ffmpegAvailable,
      link: !ffmpegAvailable ? (
        <Button data-testid="readiness-ffmpeg-link" type="button" size="sm" variant="secondary" onClick={() => {
          focusSection(depsSectionRef.current)
        }}>
          Fix
        </Button>
      ) : null,
    },
  ]

  return (
    <div
      ref={pageRef}
      data-testid="settings-page"
      className="grid w-full max-w-[60rem] items-start gap-5 p-4 min-[1000px]:grid-cols-[11rem_minmax(0,1fr)]"
    >
      <SettingsRail sections={sections} rootRef={pageRef} dots={dots} onActiveChange={setCurrentSection} />
      <div className="flex min-w-0 flex-col gap-6">
        <h1 className="text-xl font-semibold">Settings</h1>
        <HelpCard feature="settings" tabKey="main" sections={SETTINGS_HELP_SECTIONS} />

        {settingsError ? (
          <p className="text-sm text-error" role="alert">
            {settingsError}
          </p>
        ) : null}

        <SettingsSectionFrame
          sectionKey="download"
          current={currentSection === 'download'}
          footer={
            <Button data-testid="apply-defaults-btn" type="button" variant="ghost" size="sm" onClick={() => void applyDefaults()}>
              Apply defaults to pending downloads
            </Button>
          }
        >
          <PathRow
            id="settings-download-path"
            label="Download path"
            value={downloader?.path ?? ''}
            onChange={() => undefined}
            onBrowse={() => void browseDownloadPath()}
            readOnly
            inputTestId="settings-leaf-path"
            browseTestId="browse-download-path-btn"
          />
          <GridSelect
            id="settings-quality"
            label="Quality"
            testId="settings-leaf-quality"
            options={QUALITY_WIRE.map((option) => ({ value: option, label: option }))}
            value={(downloader?.quality as QualityWire | undefined) ?? QUALITY_DEFAULT}
            onChange={(value) => {
              schedulePut('downloader', { quality: value as QualityWire })
            }}
          />
          <CheckboxRow
            id="settings-audio-only"
            label="Audio only"
            leaf="audio_only"
            testId="settings-leaf-audio_only"
            checked={downloader?.audio_only ?? false}
            onChange={(checked) => {
              schedulePut('downloader', { audio_only: checked })
            }}
            suffix={
              <select
                data-testid="settings-leaf-audio_format"
                aria-label="Audio format"
                className={SELECT_CLASS}
                style={g30}
                value={(downloader?.audio_format as AudioWire | undefined) ?? AUDIO_DEFAULT}
                onChange={(event) => {
                  schedulePut('downloader', { audio_format: event.target.value as AudioWire })
                }}
              >
                {AUDIO_WIRE.map((option) => (
                  <option key={option} value={option} style={g30}>
                    {option}
                  </option>
                ))}
              </select>
            }
          />
          <PathRow
            id="settings-ffmpeg-path"
            label="FFmpeg path"
            value={downloader?.ffmpeg_path ?? ''}
            onChange={() => undefined}
            onBrowse={() => void browseFfmpeg()}
            readOnly
            inputTestId="settings-leaf-ffmpeg_path"
            browseTestId="browse-ffmpeg-btn"
          />
          <PathRow
            id="settings-deno-path"
            label="Deno path"
            value={downloader?.deno_path ?? ''}
            onChange={() => undefined}
            onBrowse={() => void browseDeno()}
            readOnly
            inputTestId="settings-leaf-deno_path"
            browseTestId="browse-deno-btn"
          />
          <div className="grid gap-1.5 sm:grid-cols-[10.5rem_minmax(0,1fr)] sm:items-start">
            <span className="text-sm text-fg">Cookie mode</span>
            <SegmentedControl
              name="cookie_mode"
              label="Cookie mode"
              testId="settings-leaf-cookie_mode"
              value={cookieMode}
              options={(['none', 'browser', 'file'] as const).map((mode) => ({
                id: `settings-cookie-mode-${mode}`,
                testId: `settings-leaf-cookie_mode-${mode}`,
                value: mode,
                label: mode,
              }))}
              onValueChange={(mode) => {
                schedulePut('downloader', { cookie_mode: mode as CookieMode })
              }}
            />
          </div>
          {cookieBrowserVisible(cookieMode) ? (
            <div className="flex flex-col gap-3 border-l border-bg-elevated pl-4">
              {/* browser cookie-browser profile */}
              <GridSelect
                id="settings-cookie-browser"
                label="Browser"
                testId="settings-leaf-cookie_browser"
                options={COOKIE_BROWSERS.map((browser) => ({ value: browser, label: browser }))}
                value={downloader?.cookie_browser ?? 'chrome'}
                onChange={(value) => {
                  schedulePut('downloader', { cookie_browser: value })
                }}
              />
              <FormRow id="settings-cookie-profile" label="Profile">
                <input
                  data-testid="settings-leaf-cookie_browser_profile"
                  className={`${INPUT_CLASS} w-40`}
                  value={downloader?.cookie_browser_profile ?? ''}
                  onChange={(event) => {
                    schedulePut('downloader', { cookie_browser_profile: event.target.value })
                  }}
                  onBlur={(event) => {
                    schedulePut('downloader', { cookie_browser_profile: event.target.value })
                  }}
                />
              </FormRow>
            </div>
          ) : null}
          {cookieFileVisible(cookieMode) ? (
            <div className="border-l border-bg-elevated pl-4">
              {/* file browse-cookie-file-btn */}
              <PathRow
                id="settings-cookie-file"
                label="Cookie file"
                value={downloader?.cookie_file_path ?? ''}
                onChange={() => undefined}
                onBrowse={() => void browseCookieFile()}
                readOnly
                inputTestId="settings-leaf-cookie_file_path"
                browseTestId="browse-cookie-file-btn"
              />
            </div>
          ) : null}
          <CheckboxRow
            id="settings-archive-tracking"
            label="Archive tracking"
            leaf="archive_tracking"
            testId="settings-leaf-archive_tracking"
            checked={downloader?.archive_tracking ?? false}
            onChange={(checked) => {
              schedulePut('downloader', { archive_tracking: checked })
            }}
          />
          <CheckboxRow
            id="settings-yt-dlp-debug"
            label="yt-dlp debug"
            leaf="yt_dlp_debug"
            testId="settings-leaf-yt_dlp_debug"
            checked={downloader?.yt_dlp_debug ?? false}
            onChange={(checked) => {
              schedulePut('downloader', { yt_dlp_debug: checked })
            }}
          />
        </SettingsSectionFrame>

        <SettingsSectionFrame sectionKey="transcript" current={currentSection === 'transcript'}>
          <PathRow
            id="settings-transcript-output"
            label="Output directory"
            value={transcript?.output_dir ?? ''}
            onChange={() => undefined}
            onBrowse={() => void browseTranscriptDir()}
            readOnly
            inputTestId="settings-leaf-output_dir"
            browseTestId="browse-transcript-dir-btn"
          />
          <div className="grid gap-3 md:grid-cols-2 md:gap-x-6">
            {(
              [
                ['requests_per_hour', 'Requests per hour', 'settings-leaf-requests_per_hour'],
                ['batch_size', 'Batch size', 'settings-leaf-batch_size'],
                ['delay_between_requests', 'Delay between requests', 'settings-leaf-delay_between_requests'],
                ['pause_between_batches', 'Pause between batches', 'settings-leaf-pause_between_batches'],
                ['max_retries', 'Max retries', 'settings-leaf-max_retries'],
                ['playlist_end', 'Playlist end', 'settings-leaf-playlist_end'],
                ['retry_delay', 'Retry delay', 'settings-leaf-retry_delay'],
                ['max_words_per_document', 'Max words per document', 'settings-leaf-max_words_per_document'],
              ] as const
            ).map(([leaf, label, testId]) => (
              <NumberRow
                key={leaf}
                id={`settings-transcript-${leaf}`}
                label={label}
                leaf={leaf}
                testId={testId}
                value={transcript?.[leaf] ?? ''}
                onChange={(value) => {
                  schedulePut('transcript', { [leaf]: value })
                }}
              />
            ))}
          </div>
        </SettingsSectionFrame>

        <SettingsSectionFrame sectionKey="tts" current={currentSection === 'tts'} sectionRef={ttsSectionRef}>
          <PathRow
            id="settings-models-dir"
            label="Models directory"
            value={tts?.models_directory ?? ''}
            onChange={() => undefined}
            onBrowse={() => void browseModelsDir()}
            readOnly
            inputTestId="settings-leaf-models_directory"
            browseTestId="browse-models-dir-btn"
          />
          <FormRow id="settings-voice" label="Voice">
            <input
              data-testid="settings-leaf-voice"
              className={`${INPUT_CLASS} w-40`}
              value={tts?.voice ?? ''}
              onChange={(event) => {
                schedulePut('tts', { voice: event.target.value })
              }}
            />
          </FormRow>
          <FormRow
            id="settings-speed"
            label="Speed"
            suffix={
              <span className="text-sm tabular-nums text-fg-muted">
                {typeof tts?.speed === 'number' ? tts.speed.toFixed(1) : '1.0'}×
              </span>
            }
          >
            <input
              type="range"
              data-testid="settings-leaf-speed"
              className="w-[13.75rem]"
              min={0.5}
              max={2.0}
              step={0.1}
              value={typeof tts?.speed === 'number' ? tts.speed : 1}
              onChange={(event) => {
                schedulePut('tts', { speed: Number(event.target.value) })
              }}
            />
          </FormRow>
          <GridSelect
            id="settings-output-format"
            label="Output format"
            testId="settings-leaf-output_format"
            options={TTS_OUTPUT_FORMATS.map((option) => ({ value: option, label: option }))}
            value={tts?.output_format === 'MP3' || tts?.output_format === 'WAV' ? tts.output_format : 'MP3'}
            onChange={(value) => {
              schedulePut('tts', { output_format: value })
            }}
          />
          <PathRow
            id="settings-tts-output"
            label="Output path"
            value={tts?.output_path ?? ''}
            onChange={() => undefined}
            onBrowse={() => void browseTtsOutputPath()}
            readOnly
            inputTestId="settings-leaf-output_path"
            browseTestId="browse-tts-output-btn"
          />
          <GridSelect
            id="settings-device"
            label="Device"
            testId="settings-leaf-device"
            options={deviceOptions.map((option) => ({ value: option, label: option }))}
            value={deviceValue}
            onChange={(value) => {
              schedulePut('tts', { device: value })
            }}
          />
          <NumberRow
            id="settings-chunk-max-chars"
            label="Chunk max chars"
            leaf="chunk_max_chars"
            testId="settings-leaf-chunk_max_chars"
            value={tts?.chunk_max_chars ?? ''}
            onChange={(value) => {
              schedulePut('tts', { chunk_max_chars: value })
            }}
          />
        </SettingsSectionFrame>

        <SettingsSectionFrame
          sectionKey="convert"
          current={currentSection === 'convert'}
          footer={
            <Button
              data-testid="convert-settings-save"
              variant="primary"
              size="sm"
              className={converter.isDirty ? 'btn-save-dirty' : 'opacity-50'}
              onClick={() => {
                void runSettingsAction('general', async () => {
                  await converter.save()
                })
              }}
            >
              {converter.isDirty ? 'Save Changes •' : 'Save'}
            </Button>
          }
        >
          <PathRow
            id="settings-convert-output"
            label="Output directory"
            value={converter.form.output_dir}
            onChange={(value) => {
              converter.patchForm({ output_dir: value })
            }}
            onBrowse={() => {
              void (async () => {
                const chosen = await window.api.showDirectoryDialog()
                if (chosen === undefined) {
                  return
                }
                converter.patchForm({ output_dir: chosen })
              })()
            }}
            inputTestId="settings-leaf-converter-output_dir"
            browseTestId="browse-convert-path-btn"
          />
          <GridSelect
            id="settings-default-preset"
            label="Default preset"
            testId="settings-leaf-default_preset"
            value={converter.form.default_preset}
            options={PRESET_WIRES.map((id) => ({ value: id, label: PRESET_LABELS[id] }))}
            onChange={(value) => {
              converter.patchForm({ default_preset: value as PresetWire })
            }}
          />
          <CheckboxRow
            id="settings-skip-existing"
            label="Skip files that already exist"
            leaf="skip_existing"
            testId="settings-leaf-skip_existing"
            checked={converter.form.skip_existing}
            onChange={(checked) => {
              converter.patchForm({ skip_existing: checked })
            }}
          />
          <GridSelect
            id="settings-gpu-preference"
            label="GPU preference"
            testId="settings-leaf-gpu_preference"
            value={converter.form.gpu_preference}
            options={GPU_PREF_WIRES.map((pref) => ({ value: pref, label: pref }))}
            onChange={(value) => {
              converter.patchForm({ gpu_preference: value as GpuPrefWire })
            }}
          />
        </SettingsSectionFrame>

        <SettingsSectionFrame
          sectionKey="capture"
          current={currentSection === 'capture'}
          footer={
            <Button
              data-testid="capture-settings-save"
              variant="primary"
              size="sm"
              className={capture.isDirty ? 'btn-save-dirty' : 'opacity-50'}
              onClick={() => {
                void runSettingsAction('general', async () => {
                  await capture.save()
                })
              }}
            >
              {capture.isDirty ? 'Save Changes •' : 'Save'}
            </Button>
          }
        >
          <PathRow
            id="settings-capture-inbox"
            label="Inbox directory"
            value={capture.form.inbox_dir}
            onChange={(value) => {
              capture.patchForm({ inbox_dir: value })
            }}
            onBrowse={() => {
              void (async () => {
                const chosen = await window.api.showDirectoryDialog()
                if (chosen === undefined) {
                  return
                }
                capture.patchForm({ inbox_dir: chosen })
              })()
            }}
            inputTestId="settings-leaf-capture-inbox_dir"
            browseTestId="browse-capture-path-btn"
          />
          <FormRow id="settings-hotkey" label="Hotkey">
            <input
              data-testid="settings-leaf-hotkey"
              className={`${INPUT_CLASS} w-20 font-mono`}
              value={capture.form.hotkey}
              onChange={(event) => {
                capture.patchForm({ hotkey: event.target.value })
              }}
            />
          </FormRow>
          <CheckboxRow
            id="settings-copy-to-clipboard"
            label="Copy new captures to the clipboard"
            leaf="copy_to_clipboard"
            testId="settings-leaf-copy_to_clipboard"
            checked={capture.form.copy_to_clipboard}
            onChange={(checked) => {
              capture.patchForm({ copy_to_clipboard: checked })
            }}
          />
          <CheckboxRow
            id="settings-close-to-tray"
            label="Close to tray"
            leaf="close_to_tray"
            testId="settings-leaf-close_to_tray"
            checked={capture.form.close_to_tray}
            onChange={(checked) => {
              capture.patchForm({ close_to_tray: checked })
            }}
          />
          <CheckboxRow
            id="settings-flatten-backup"
            label="Back up the original before Flatten into image"
            leaf="flatten_backup"
            testId="settings-leaf-flatten_backup"
            checked={capture.form.flatten_backup}
            onChange={(checked) => {
              capture.patchForm({ flatten_backup: checked })
            }}
          />
          <PathRow
            id="settings-capture-backup"
            label="Backup folder"
            inputTestId="settings-leaf-capture-backup_dir"
            browseTestId="settings-capture-backup-browse"
            value={capture.form.backup_dir}
            placeholder={`${capture.form.inbox_dir}/${BACKUP_DIR_DEFAULT_NAME}`}
            onChange={(value) => {
              capture.patchForm({ backup_dir: value })
            }}
            onBrowse={() => {
              void (async () => {
                const chosen = await window.api.showDirectoryDialog()
                if (chosen === undefined) {
                  return
                }
                capture.patchForm({ backup_dir: chosen })
              })()
            }}
          />
          <GridSelect
            id="settings-annotated-format"
            label="Save annotations format"
            testId="settings-leaf-annotated_format"
            value={capture.form.annotated_format}
            options={ANNOTATED_FORMAT_OPTIONS}
            onChange={(value) => {
              capture.patchForm({ annotated_format: value as AnnotatedFormat })
            }}
          />
        </SettingsSectionFrame>

        <SettingsSectionFrame sectionKey="console" current={currentSection === 'console'}>
          <GridSelect
            id="settings-log-level"
            label="Log level"
            hint="The level the Console opens at. A level shows its own lines and every more severe one."
            testId="settings-leaf-log_level"
            options={LOG_LEVELS.map((level) => ({ value: level, label: level }))}
            value={appSettings?.log_level ?? 'INFO'}
            onChange={(value) => {
              schedulePut('app', { log_level: value })
            }}
          />
          <div data-testid="settings-log-row">
            <FormRow
              id="settings-log-to-file"
              label="Log to file"
              hint="Errors are always written to this file. Turn on Log to file to write every Console line there too."
              suffix={
                <>
                  <span className="min-w-0 truncate font-mono text-xs text-fg-muted" data-testid="settings-log-file-path">
                    Persist to {consoleLogFileLabel(readiness?.logFilePath)}
                  </span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    data-testid="settings-copy-log-path"
                    onClick={() => {
                      void window.api.writeClipboardText(consoleLogFileLabel(readiness?.logFilePath))
                    }}
                  >
                    Copy log path
                  </Button>
                </>
              }
            >
              <input
                type="checkbox"
                data-testid="settings-leaf-log_to_file"
                checked={appSettings?.log_to_file ?? false}
                onChange={(event) => {
                  schedulePut('app', { log_to_file: event.target.checked })
                }}
              />
            </FormRow>
          </div>
          <CheckboxRow
            id="settings-console-visible"
            label="Console visible"
            leaf="console_visible"
            testId="settings-leaf-console_visible"
            checked={appSettings?.console_visible ?? false}
            onChange={(checked) => {
              schedulePut('app', { console_visible: checked })
            }}
          />
        </SettingsSectionFrame>

        <SettingsSectionFrame sectionKey="appearance" current={currentSection === 'appearance'}>
          <div role="group" aria-label="Theme" className="inline-flex gap-1 self-start rounded-[var(--radius-control)] border border-border p-0.5">
            <Button
              data-testid="theme-dark-btn"
              type="button"
              size="sm"
              title="Dark (Ctrl+Shift+D)"
              aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Shift+D')}
              aria-pressed={uiSettings?.theme === 'dark'}
              variant={uiSettings?.theme === 'dark' ? 'primary' : 'secondary'}
              onClick={() => {
                void runSettingsAction('ui', () => putNow('ui', { theme: 'dark' }))
              }}
            >
              Dark
            </Button>
            <Button
              data-testid="theme-light-btn"
              type="button"
              size="sm"
              title="Light (Ctrl+Shift+L)"
              aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Shift+L')}
              aria-pressed={uiSettings?.theme === 'light'}
              variant={uiSettings?.theme === 'light' ? 'primary' : 'secondary'}
              onClick={() => {
                void runSettingsAction('ui', () => putNow('ui', { theme: 'light' }))
              }}
            >
              Light
            </Button>
          </div>
        </SettingsSectionFrame>

        <StartAtSignInControl onAvailabilityChange={setStartupAvailable} current={currentSection === 'startup'} />

        <SettingsSectionFrame
          sectionKey="dependencies"
          current={currentSection === 'dependencies'}
          sectionRef={depsSectionRef}
          footer={
            <Button data-testid="check-deps-btn" type="button" variant="ghost" size="sm" onClick={checkDependencies}>
              Check dependencies
            </Button>
          }
        >
          <ul className="flex flex-col gap-2 text-sm">
            {(
              [
                ['yt-dlp', ytDlp, ytDlp?.available],
                ['FFmpeg', ffmpeg, ffmpeg?.available],
              ] as const
            ).map(([name, dep, isAvailable]) => {
              const chip = checkChip(depsQuery.data === undefined ? undefined : isAvailable === true, 'available', 'missing')
              const detail = [dep?.version, dep?.path].filter((part): part is string => typeof part === 'string' && part.length > 0)
              return (
                <li key={name} className="flex min-w-0 items-center gap-2">
                  <StatusChip label={chip.label} tone={chip.tone} />
                  <span>{name}</span>
                  {detail.length > 0 ? (
                    <span className="min-w-0 truncate font-mono text-xs text-fg-muted">{detail.join(' · ')}</span>
                  ) : null}
                </li>
              )
            })}
            <li data-testid="deps-ffprobe-row" className="flex min-w-0 items-center gap-2">
              <StatusChip label={ffprobeChip.label} tone={ffprobeChip.tone} />
              <span>FFprobe</span>
            </li>
            {depsQuery.data?.js_runtime ? <JsRuntimeRow runtime={depsQuery.data.js_runtime} /> : null}
            {presentAssetRows(depsQuery.data).map(([wire, row]) => {
              const chip = assetChip(row.state)
              return (
                <li key={wire} data-testid={`tts-asset-row-${wire}`} className="flex min-w-0 items-center gap-2">
                  <StatusChip label={chip.label} tone={chip.tone} />
                  <span>{TTS_ASSET_LABELS[wire]}</span>
                  {row.version ? <span className="font-mono text-xs text-fg-muted">{row.version}</span> : null}
                  {assetGetVisible(row.state) ? (
                    <Button
                      data-testid={`tts-asset-get-btn-${wire}`}
                      type="button"
                      variant="secondary"
                      size="sm"
                      disabled={row.state === 'downloading'}
                      onClick={() => {
                        void runSettingsAction('general', async () => {
                          await postDownloadAsset(wire)
                        })
                      }}
                    >
                      Get
                    </Button>
                  ) : null}
                </li>
              )
            })}
            {depsQuery.data?.tts_espeak ? <EspeakRow espeak={depsQuery.data.tts_espeak} /> : null}
          </ul>
        </SettingsSectionFrame>

        <SettingsSectionFrame
          sectionKey="readiness"
          current={currentSection === 'readiness'}
          caption={
            readinessLoaded !== null ? (
              <span data-testid="settings-readiness-count">
                {readinessLoaded.ready} of {readinessLoaded.total} ready
              </span>
            ) : (
              ''
            )
          }
        >
          <ul className="flex flex-col gap-2 text-sm">
            {readinessRows.map((row) => {
              const chip = checkChip(row.value)
              return (
                <li key={row.label} className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-2">
                    <StatusChip label={chip.label} tone={chip.tone} />
                    <span>{row.label}</span>
                  </span>
                  {row.link}
                </li>
              )
            })}
          </ul>
        </SettingsSectionFrame>

        <SettingsSectionFrame sectionKey="mcp" current={currentSection === 'mcp'}>
          <div className="flex flex-wrap items-center gap-2">
            <StatusChip
              testId="mcp-token-present"
              label={`Token present: ${mcpQuery.data?.tokenPresent ? 'yes' : 'no'}`}
              tone={mcpQuery.data?.tokenPresent ? 'success' : 'warning'}
            />
          </div>
          <GridSelect
            id="mcp-client"
            label="Client"
            testId="mcp-client-select"
            value={mcpClient}
            options={MCP_CLIENT_OPTIONS}
            onChange={(value) => {
              const next = value as McpClientWire
              setMcpClient(next)
              if (MCP_USER_ONLY_CLIENTS.includes(next)) {
                setMcpScope('user')
              }
            }}
          />
          <GridSelect
            id="mcp-scope"
            label="Scope"
            testId="mcp-scope-select"
            value={mcpEffectiveScope}
            options={MCP_SCOPE_OPTIONS}
            disabled={mcpScopeLocked}
            onChange={(value) => {
              setMcpScope(value as McpScopeWire)
            }}
          />
          <textarea
            data-testid="mcp-setup-prompt"
            aria-label="MCP setup prompt"
            readOnly
            rows={12}
            className="resize-y rounded-[var(--radius-control)] border border-border bg-bg-elevated p-3 font-mono text-xs"
            value={mcpPrompt}
          />
          <div className="flex flex-wrap items-center gap-2">
            <Button
              data-testid="mcp-copy-prompt-btn"
              type="button"
              variant="secondary"
              size="sm"
              disabled={!mcpPromptAvailable || mcpPrompt === ''}
              onClick={() => void copyMcpPrompt()}
            >
              Copy prompt
            </Button>
          </div>
          <p data-testid="mcp-prompt-status" role="status" className="text-xs text-fg-muted">
            {mcpPromptStatus}
          </p>
          <details data-testid="mcp-advanced">
            <summary data-testid="mcp-advanced-summary" className="cursor-pointer text-sm text-fg-muted">
              Advanced
            </summary>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <Button data-testid="copy-mcp-btn" type="button" variant="secondary" size="sm" onClick={() => void copyMcp(false)}>
                Copy MCP config
              </Button>
              <Button data-testid="pin-mcp-btn" type="button" variant="ghost" size="sm" onClick={() => void copyMcp(true)}>
                Pin endpoint &amp; copy
              </Button>
            </div>
          </details>
        </SettingsSectionFrame>
        <div data-testid="settings-tail-spacer" aria-hidden="true" style={{ height: `${tailSpacer}px` }} />
      </div>
    </div>
  )
}

export async function putSettingsLeaf(
  namespace: 'downloader' | 'transcript' | 'tts' | 'app' | 'ui',
  patch: Record<string, unknown>,
): Promise<void> {
  try {
    await apiFetch(SETTINGS_NAMESPACE_PATHS[namespace], {
      method: 'PUT',
      body: JSON.stringify(patch),
    })
  } catch (caught) {
    if (caught instanceof ApiError) {
      throw caught
    }
    throw caught
  }
}
