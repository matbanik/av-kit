/** `DEVICE_ORDER`: device wire names in the order `runtime_devices` lists them (`_DEVICE_ORDER`, `tts/adapter.py:71`). */
export const DEVICE_ORDER: readonly string[] = ['auto', 'cuda', 'cpu', 'mps']

/** `DEVICE_FLOOR`: the devices every build offers (`DEVICE_PROBE`). */
export const DEVICE_FLOOR: readonly string[] = ['auto', 'cpu']

/**
 * `DEVICE_OPTIONS`: `DEVICE_FLOOR` plus the devices of each row whose `available` isn't `false`,
 * kept to `DEVICE_ORDER` and listed in that order (D-314).
 */
export function buildDevices(
  rows: ReadonlyArray<{ devices?: readonly string[]; available?: boolean }> | undefined,
): string[] {
  const offered = new Set<string>(DEVICE_FLOOR)
  for (const row of rows ?? []) {
    if (row.available === false) continue
    for (const device of row.devices ?? []) offered.add(device)
  }
  return DEVICE_ORDER.filter((device) => offered.has(device))
}
