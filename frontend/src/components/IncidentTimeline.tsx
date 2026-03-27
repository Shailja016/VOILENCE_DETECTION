import { cn } from '@/lib/utils'

export type TimelineMarker = {
  t: string
  label: string
  type?: 'violence' | 'alert' | 'info'
}

type Props = {
  markers: TimelineMarker[]
  current?: string
}

export function IncidentTimeline({ markers, current }: Props) {
  return (
    <div className="relative border-l border-border pl-4">
      {markers.map((m, i) => (
        <div key={i} className="relative pb-6 last:pb-0">
          <span
            className={cn(
              'absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full border-2 border-background',
              m.type === 'violence' && 'bg-danger',
              m.type === 'alert' && 'bg-ai-accent',
              (!m.type || m.type === 'info') && 'bg-primary',
              current === m.t && 'ring-2 ring-primary ring-offset-2 ring-offset-background'
            )}
          />
          <p className="text-xs font-mono text-muted">{m.t}</p>
          <p className="text-sm text-slate-200">{m.label}</p>
        </div>
      ))}
    </div>
  )
}
