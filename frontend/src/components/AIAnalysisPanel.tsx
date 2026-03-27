import { useState } from 'react'
import { ChevronDown, ChevronUp, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import type { AiAnalysis } from '@/types/incident'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RiskBadge } from '@/components/RiskBadge'
import { SuspectCard } from '@/components/SuspectCard'
import { cn } from '@/lib/utils'

type Props = {
  analysis: AiAnalysis
  className?: string
}

export function AIAnalysisPanel({ analysis, className }: Props) {
  const [open, setOpen] = useState(true)
  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-ai-accent" />
          <h2 className="text-lg font-semibold text-slate-50">AI analysis</h2>
        </div>
        <RiskBadge level={analysis.risk_level} />
      </div>

      <div className="rounded-xl border border-border bg-surface/60 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-sm font-medium text-muted">Summary</h3>
          <Button variant="ghost" size="sm" onClick={() => setOpen((v) => !v)}>
            {open ? (
              <>
                Collapse <ChevronUp className="h-4 w-4" />
              </>
            ) : (
              <>
                Expand <ChevronDown className="h-4 w-4" />
              </>
            )}
          </Button>
        </div>
        <AnimatePresence initial={false}>
          {open ? (
            <motion.p
              key="summary"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-2 overflow-hidden text-sm leading-relaxed text-slate-200"
            >
              {analysis.summary}
            </motion.p>
          ) : null}
        </AnimatePresence>
      </div>

      <SuspectCard culprit={analysis.culprit} />

      <div>
        <h3 className="mb-2 text-sm font-medium text-muted">Behavior tags</h3>
        <div className="flex flex-wrap gap-2">
          {analysis.behavior.map((b) => (
            <Badge key={b} variant="outline" className="border-primary/40 text-slate-200">
              {b}
            </Badge>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-danger/30 bg-danger/5 p-4">
        <h3 className="text-sm font-medium text-danger">Recommendation</h3>
        <p className="mt-1 text-sm text-slate-200">{analysis.recommendation}</p>
      </div>
    </div>
  )
}
