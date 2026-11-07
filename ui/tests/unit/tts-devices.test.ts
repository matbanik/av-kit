/**
 * MEU-118 AC-118.1: `DEVICE_OPTIONS`. `buildDevices(rows)` is `DEVICE_FLOOR` plus the `devices`
 * of each row whose `available` isn't `false`, kept to `DEVICE_ORDER` and listed in that order.
 */
import { describe, expect, it } from 'vitest'

type DeviceRows = ReadonlyArray<{ devices?: readonly string[]; available?: boolean }> | undefined

type DevicesModule = {
  DEVICE_ORDER: readonly string[]
  DEVICE_FLOOR: readonly string[]
  buildDevices: (rows: DeviceRows) => string[]
}

// A new module; a glob keeps its absence a test failure, not a load error.
const modules = import.meta.glob('../../src/renderer/src/features/tts/tts-devices.ts')

async function loadDevices(): Promise<DevicesModule> {
  expect(Object.keys(modules), 'AC-118.1 tts-devices.ts exists').toHaveLength(1)
  return (await Object.values(modules)[0]()) as DevicesModule
}

const CPU_ONLY = { devices: ['auto', 'cpu'], available: true }

describe('MEU-118 AC-118.1 buildDevices', () => {
  it('AC-118.1 DEVICE_ORDER is the runtime_devices order and DEVICE_FLOOR is auto and cpu', async () => {
    const { DEVICE_ORDER, DEVICE_FLOOR } = await loadDevices()
    expect([...DEVICE_ORDER]).toEqual(['auto', 'cuda', 'cpu', 'mps'])
    expect([...DEVICE_FLOOR]).toEqual(['auto', 'cpu'])
  })

  it('AC-118.1 no report and an empty report give the floor', async () => {
    const { buildDevices } = await loadDevices()
    expect(buildDevices(undefined)).toEqual(['auto', 'cpu'])
    expect(buildDevices([])).toEqual(['auto', 'cpu'])
  })

  it('AC-118.1 a CPU-only report gives auto and cpu, and an ONNX row listing cuda adds it', async () => {
    const { buildDevices } = await loadDevices()
    expect(buildDevices([CPU_ONLY, CPU_ONLY])).toEqual(['auto', 'cpu'])
    expect(buildDevices([CPU_ONLY, { devices: ['auto', 'cuda', 'cpu'], available: true }])).toEqual([
      'auto',
      'cuda',
      'cpu',
    ])
  })

  it('AC-118.1 an unavailable row adds none of its devices', async () => {
    const { buildDevices } = await loadDevices()
    const pytorch = { devices: ['auto', 'cuda', 'cpu', 'mps'], available: false }
    expect(buildDevices([pytorch, CPU_ONLY])).toEqual(['auto', 'cpu'])
  })

  it('AC-118.1 unknown strings are dropped, DEVICE_ORDER holds with no repeats, and a row without devices adds nothing', async () => {
    const { buildDevices } = await loadDevices()
    expect(buildDevices([{ devices: ['mps', 'tpu', 'cuda', 'cuda', 'CPU', 'auto'] }])).toEqual([
      'auto',
      'cuda',
      'cpu',
      'mps',
    ])
    expect(buildDevices([{ available: true }, {}])).toEqual(['auto', 'cpu'])
  })
})
