import { User } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ConfidenceBar } from '@/components/ConfidenceBar'
import type { Culprit } from '@/types/incident'

type Props = {
  culprit: Culprit
}

export function SuspectCard({ culprit }: Props) {
  return (
    <Card className="border-ai-accent/30 bg-ai-accent/5">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <User className="h-4 w-4 text-ai-accent" />
          Culprit identification
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-sm text-muted">Suspect ID</span>
          <span className="font-mono text-lg font-semibold text-ai-accent">{culprit.id}</span>
        </div>
        <ConfidenceBar value={culprit.confidence} label="Model + LLM confidence" />
        <p className="text-sm leading-relaxed text-slate-300">{culprit.reason}</p>
      </CardContent>
    </Card>
  )
}
