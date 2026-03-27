import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Send, CheckCircle2 } from 'lucide-react'
import { getIncident, patchIncident } from '@/lib/api'
import { mockIncidents } from '@/data/mock'
import type { Incident } from '@/types/incident'
import { AIAnalysisPanel } from '@/components/AIAnalysisPanel'
import { IncidentTimeline, type TimelineMarker } from '@/components/IncidentTimeline'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useIncidentsContext } from '@/contexts/IncidentsContext'

export function IncidentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { setItems } = useIncidentsContext()
  const [incident, setIncident] = useState<Incident | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const { incident: data } = await getIncident(id)
        if (!cancelled) setIncident(data)
      } catch {
        const fallback = mockIncidents.find((m) => m._id === id) ?? mockIncidents[0]
        if (!cancelled) {
          setIncident(fallback)
          setError('Using offline mock — API unavailable')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [id])

  const markers: TimelineMarker[] = useMemo(() => {
    if (!incident) return []
    const t = new Date(incident.timestamp)
    return [
      { t: new Date(t.getTime() - 120000).toLocaleTimeString(), label: 'Crowd density spike', type: 'info' },
      { t: t.toLocaleTimeString(), label: 'Violence model fired', type: 'violence' },
      { t: new Date(t.getTime() + 15000).toLocaleTimeString(), label: 'LLM analysis complete', type: 'alert' },
    ]
  }, [incident])

  async function sendAlert() {
    if (!incident) return
    try {
      const { incident: updated } = await patchIncident(incident._id, { alert_status: 'sent' })
      setIncident(updated)
      setItems((prev) => prev.map((x) => (x._id === updated._id ? updated : x)))
    } catch {
      setIncident({ ...incident, alert_status: 'sent' })
    }
  }

  async function markResolved() {
    if (!incident) return
    try {
      const { incident: updated } = await patchIncident(incident._id, { alert_status: 'resolved' })
      setIncident(updated)
      setItems((prev) => prev.map((x) => (x._id === updated._id ? updated : x)))
    } catch {
      setIncident({ ...incident, alert_status: 'resolved' })
    }
  }

  if (loading || !incident) {
    return (
      <div className="grid gap-6 lg:grid-cols-2">
        <Skeleton className="aspect-video w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  const video = incident.video_url || 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'

  return (
    <div className="space-y-4">
      {error ? <p className="text-sm text-amber-300">{error}</p> : null}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <Card className="overflow-hidden p-0">
            <div className="relative aspect-video bg-black">
              <video
                className="h-full w-full object-cover"
                src={video}
                controls
                playsInline
                poster=""
              />
              {/* Simulated culprit highlight */}
              <div className="pointer-events-none absolute left-[10%] top-[18%] h-[45%] w-[30%] rounded-lg border-2 border-ai-accent shadow-[0_0_24px_rgba(139,92,246,0.45)]">
                <span className="absolute -top-7 left-0 rounded bg-ai-accent px-2 py-0.5 text-xs font-semibold text-white">
                  Suspect {incident.ai_analysis.culprit.id}
                </span>
              </div>
            </div>
            <CardContent className="p-4">
              <h3 className="text-sm font-medium text-muted">Timeline</h3>
              <div className="mt-3">
                <IncidentTimeline markers={markers} current={new Date(incident.timestamp).toLocaleTimeString()} />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <AIAnalysisPanel analysis={incident.ai_analysis} />
          <div className="flex flex-wrap gap-2">
            <Button className="gap-2" onClick={sendAlert}>
              <Send className="h-4 w-4" />
              Send alert
            </Button>
            <Button variant="secondary" className="gap-2" onClick={markResolved}>
              <CheckCircle2 className="h-4 w-4" />
              Mark resolved
            </Button>
            <Button variant="ghost" onClick={() => navigate('/incidents')}>
              Back to list
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
