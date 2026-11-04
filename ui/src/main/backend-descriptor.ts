import { readFileSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

export const DESCRIPTOR_FILENAME = 'backend.json'
export const PORT_SIBLING_FILENAME = 'backend-port.txt'

export function descriptorPath(appData: string): string {
  return join(appData, DESCRIPTOR_FILENAME)
}

export function portSiblingPath(appData: string): string {
  return join(appData, PORT_SIBLING_FILENAME)
}

export function retireDescriptor(appData: string): void {
  try {
    rmSync(descriptorPath(appData), { force: true })
  } catch {
    writeFileSync(descriptorPath(appData), '{"tombstone":true}\n', { encoding: 'utf8' })
  }
}

export function retirePortSibling(appData: string): void {
  rmSync(portSiblingPath(appData), { force: true })
}

export function readDescriptorPid(appData: string): number | null {
  try {
    const raw = readFileSync(descriptorPath(appData), { encoding: 'utf8' })
    const parsed = JSON.parse(raw) as { pid?: number }
    return typeof parsed.pid === 'number' ? parsed.pid : null
  } catch {
    return null
  }
}
