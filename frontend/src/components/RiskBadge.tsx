import type { RiskLevel } from '@/types/incident'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const map: Record<RiskLevel, { variant: 'default' | 'danger' | 'success' | 'ai'; className: string }> = {
  Low: { variant: 'success', className: '' },
  Medium: { variant: 'default', className: 'text-amber-300 bg-amber-500/15' },
  High: { variant: 'danger', className: '' },
}

export function RiskBadge({ level }: { level: RiskLevel }) {
  const m = map[level]
  return (
    <Badge variant={m.variant} className={cn('uppercase tracking-wide', m.className)}>
      {level} risk
    </Badge>
  )
}
