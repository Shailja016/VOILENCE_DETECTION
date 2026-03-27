import * as Progress from '@radix-ui/react-progress'
import { cn } from '@/lib/utils'

type Props = {
  value: number
  className?: string
  label?: string
}

export function ConfidenceBar({ value, className, label }: Props) {
  const pct = Math.round(Math.max(0, Math.min(1, value)) * 100)
  return (
    <div className={cn('space-y-1', className)}>
      {label ? (
        <div className="flex justify-between text-xs text-muted">
          <span>{label}</span>
          <span className="font-mono text-slate-200">{pct}%</span>
        </div>
      ) : null}
      <Progress.Root
        value={pct}
        max={100}
        className="relative h-2 w-full overflow-hidden rounded-full bg-white/10"
      >
        <Progress.Indicator
          className="h-full rounded-full bg-gradient-to-r from-primary to-ai-accent transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </Progress.Root>
    </div>
  )
}
