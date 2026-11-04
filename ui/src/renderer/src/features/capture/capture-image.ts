export async function fetchAuthorizedBlob(path: string): Promise<Blob | null> {
  const seam = (window as unknown as { __e2eSeamInstalled?: boolean }).__e2eSeamInstalled === true
  const [base, token] = seam
    ? (['http://127.0.0.1:9/api/v1', 'e2e-token'] as const)
    : await Promise.all([window.api.getBackendUrl(), window.api.getToken()])
  const res = await window.fetch(`${base}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
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
