import { useMemo } from 'react'
import { AlertsList } from '@/components/AlertsList'
import { patchIncident } from '@/lib/api'
import { useIncidentsContext } from '@/contexts/IncidentsContext'

export function Alerts() {
  const { items, setItems } = useIncidentsContext()

  const alerts = useMemo(
    () => items.filter((i) => i.violence && i.alert_status !== 'resolved'),
    [items]
  )

  async function acknowledge(id: string) {
    try {
      const { incident } = await patchIncident(id, { alert_status: 'sent' })
      setItems((prev) => prev.map((x) => (x._id === id ? incident : x)))
    } catch {
      setItems((prev) =>
        prev.map((x) => (x._id === id ? { ...x, alert_status: 'sent' as const } : x))
      )
    }
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted">
        Socket.io pushes <code className="rounded bg-surface px-1 py-0.5 font-mono text-xs">new_incident</code> and{' '}
        <code className="rounded bg-surface px-1 py-0.5 font-mono text-xs">alert_triggered</code> for instant UI refresh.
      </p>
      <AlertsList items={alerts} onAcknowledge={acknowledge} />
    </div>
  )
}
