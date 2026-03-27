import type { Incident } from '@/types/incident'

const BASE = import.meta.env.VITE_API_URL || ''

async function parseJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || res.statusText)
  }
  return res.json() as Promise<T>
}

export async function getIncidents(params?: {
  location?: string
  severity?: string
  alert_status?: string
  limit?: number
  skip?: number
}): Promise<{ incidents: Incident[]; total: number }> {
  const q = new URLSearchParams()
  if (params?.location) q.set('location', params.location)
  if (params?.severity) q.set('severity', params.severity)
  if (params?.alert_status) q.set('alert_status', params.alert_status)
  if (params?.limit != null) q.set('limit', String(params.limit))
  if (params?.skip != null) q.set('skip', String(params.skip))
  const res = await fetch(`${BASE}/api/incidents?${q.toString()}`)
  return parseJson(res)
}

export async function getIncident(id: string): Promise<{ incident: Incident }> {
  const res = await fetch(`${BASE}/api/incidents/${id}`)
  return parseJson(res)
}

export async function patchIncident(
  id: string,
  body: { alert_status: 'pending' | 'sent' | 'resolved' }
): Promise<{ incident: Incident }> {
  const res = await fetch(`${BASE}/api/incidents/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return parseJson(res)
}

export async function analyzeIncidentPayload(body: Record<string, unknown>) {
  const res = await fetch(`${BASE}/api/analyze-incident`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return parseJson<{ incident: Incident; ai_analysis: Incident['ai_analysis'] }>(res)
}

export type CameraDto = {
  camera_id: string
  label?: string
  location?: string
  video_url?: string
  mock_violence?: boolean
  enabled?: boolean
}

export async function getCameras(): Promise<{ cameras: CameraDto[] }> {
  const res = await fetch(`${BASE}/api/cameras`)
  return parseJson(res)
}

export async function scanCamera(cameraId: string) {
  const res = await fetch(`${BASE}/api/cameras/${cameraId}/scan`, {
    method: 'POST',
  })
  return parseJson(res)
}
