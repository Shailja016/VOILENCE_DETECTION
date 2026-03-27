import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ExternalLink } from 'lucide-react'
import type { Incident } from '@/types/incident'
import { Badge } from '@/components/ui/badge'
import { RiskBadge } from '@/components/RiskBadge'
import { Button } from '@/components/ui/button'

type Props = {
  items: Incident[]
  onAcknowledge?: (id: string) => void
}

export function AlertsList({ items, onAcknowledge }: Props) {
  if (!items.length) {
    return (
      <p className="rounded-xl border border-border bg-surface/60 p-8 text-center text-sm text-muted">
        No active alerts. Real-time events will appear here.
      </p>
    )
  }

  return (
    <ul className="space-y-3">
      {items.map((inc, i) => (
        <motion.li
          key={inc._id}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          className="flex flex-col gap-3 rounded-xl border border-border bg-surface/70 p-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-sm text-primary">{inc.camera_id}</span>
              <RiskBadge level={inc.ai_analysis.risk_level} />
              <Badge variant="danger" className="animate-alert-badge">
                Live
              </Badge>
            </div>
            <p className="mt-1 text-sm text-slate-300">{inc.location}</p>
            <p className="mt-1 line-clamp-2 text-xs text-muted">{inc.ai_analysis.summary}</p>
          </div>
          <div className="flex shrink-0 gap-2">
            <Button variant="secondary" size="sm" asChild>
              <Link to={`/incidents/${inc._id}`}>
                Details
                <ExternalLink className="h-3.5 w-3.5" />
              </Link>
            </Button>
            {onAcknowledge ? (
              <Button variant="default" size="sm" onClick={() => onAcknowledge(inc._id)}>
                Acknowledge
              </Button>
            ) : null}
          </div>
        </motion.li>
      ))}
    </ul>
  )
}
