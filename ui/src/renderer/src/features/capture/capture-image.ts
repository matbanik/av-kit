async function backendBaseAndToken(): Promise<readonly [string, string]> {
  const seam = (window as unknown as { __e2eSeamInstalled?: boolean }).__e2eSeamInstalled === true
  return seam
    ? (['http://127.0.0.1:9/api/v1', 'e2e-token'] as const)
    : await Promise.all([window.api.getBackendUrl(), window.api.getToken()])
}

export async function fetchAuthorizedBlob(path: string): Promise<Blob | null> {
  const [base, token] = await backendBaseAndToken()
  const res = await window.fetch(`${base}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) {
    return null
  }
  return res.blob()
}

/** RENDER_CLIENT (MEU-104): POST `body` as JSON with the same base and token as fetchAuthorizedBlob. */
export async function postAuthorizedBlob(path: string, body: unknown): Promise<Blob | null> {
  const [base, token] = await backendBaseAndToken()
  const res = await window.fetch(`${base}${path}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    return null
  }
  return res.blob()
}

export async function fetchCaptureImageObjectUrl(
  id: string,
  variant: 'original' | 'annotated' = 'original',
): Promise<string | null> {
  const blob = await fetchAuthorizedBlob(`/captures/${id}/image?variant=${variant}`)
  if (blob === null) {
    return null
  }
  return URL.createObjectURL(blob)
}
