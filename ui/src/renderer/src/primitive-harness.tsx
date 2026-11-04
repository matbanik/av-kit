import { useState } from 'react'
import { createRoot } from 'react-dom/client'

import { Disclosure } from './components/ui/Disclosure'
import { FormRow } from './components/ui/FormRow'
import { PathRow } from './components/ui/PathRow'
import { SegmentedControl } from './components/ui/SegmentedControl'
import { StatusChip } from './components/ui/StatusChip'
import './styles.css'

/** Test-only local state for real Electron primitive assertions; no product page imports this entry. */
function PrimitiveHarness(): React.JSX.Element {
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState('none')
  const [modelName, setModelName] = useState('')
  const [path, setPath] = useState('C:/one folder')
  const [browseCount, setBrowseCount] = useState(0)

  return (
    <main data-testid="primitive-harness" className="mx-auto max-w-2xl space-y-5 bg-bg p-6 text-fg">
      <h1>Primitive test harness</h1>
      <Disclosure id="primitive-advanced" title="Advanced" open={open} onOpenChange={setOpen} testId="primitive-disclosure">
        <button type="button">Inside advanced</button>
      </Disclosure>
      <SegmentedControl
        name="primitive-cookie-mode"
        value={mode}
        onValueChange={setMode}
        testId="primitive-segment"
        options={[
          { id: 'primitive-cookie-none', value: 'none', label: 'None' },
          { id: 'primitive-cookie-browser', value: 'browser', label: 'Browser' },
          { id: 'primitive-cookie-file', value: 'file', label: 'File' },
        ]}
      />
      <output data-testid="primitive-segment-value">{mode}</output>
      <StatusChip label="Queued" count={3} tone="warning" testId="primitive-chip" />
      <FormRow id="primitive-form" label="Model name" hint="Required for this run" error="Choose a name" testId="primitive-form">
        <input value={modelName} onChange={(event) => setModelName(event.currentTarget.value)} />
      </FormRow>
      <PathRow
        id="primitive-path"
        label="Output folder"
        value={path}
        onChange={setPath}
        onBrowse={() => setBrowseCount((count) => count + 1)}
        testId="primitive-path"
      />
      <output data-testid="primitive-path-value">{path}</output>
      <output data-testid="primitive-browse-count">{browseCount}</output>
    </main>
  )
}

const root = document.getElementById('root')
if (!root) throw new Error('primitive harness root missing')
createRoot(root).render(<PrimitiveHarness />)
