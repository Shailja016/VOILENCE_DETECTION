import { useMemo, useState } from 'react'
import { IncidentCard } from '@/components/IncidentCard'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { useIncidentsContext } from '@/contexts/IncidentsContext'
import type { RiskLevel } from '@/types/incident'

export function Incidents() {
  const { items, loading } = useIncidentsContext()
  const [location, setLocation] = useState('')
  const [severity, setSeverity] = useState<RiskLevel | ''>('')

  const filtered = useMemo(() => {
    return items.filter((i) => {
      if (location && !i.location.toLowerCase().includes(location.toLowerCase())) return false
      if (severity && i.ai_analysis.risk_level !== severity) return false
      return true
    })
  }, [items, location, severity])

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1 space-y-1">
          <label className="text-xs font-medium text-muted">Location</label>
          <input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Filter by location"
            className="h-10 w-full max-w-md rounded-lg border border-border bg-surface/80 px-3 text-sm text-slate-100 placeholder:text-muted focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/40"
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium text-muted">Severity</label>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value as RiskLevel | '')}
            className="h-10 rounded-lg border border-border bg-surface/80 px-3 text-sm text-slate-100 focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/40"
          >
            <option value="">All</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </div>
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            setLocation('')
            setSeverity('')
          }}
        >
          Reset
        </Button>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((inc, i) => (
            <IncidentCard key={inc._id} incident={inc} index={i} />
          ))}
        </div>
      )}

      {!loading && filtered.length === 0 ? (
        <p className="text-center text-sm text-muted">No incidents match your filters.</p>
      ) : null}
    </div>
  )
}
