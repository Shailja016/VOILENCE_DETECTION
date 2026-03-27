import { Link } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { RiskBadge } from '@/components/RiskBadge'
import { Skeleton } from '@/components/ui/skeleton'
import { ConfidenceBar } from '@/components/ConfidenceBar'
import { useIncidentsContext } from '@/contexts/IncidentsContext'

export function AIAnalysisPage() {
  const { items, loading } = useIncidentsContext()
  const list = [...items].sort((a, b) => +new Date(b.timestamp) - +new Date(a.timestamp)).slice(0, 12)

  return (
    <div className="space-y-6">
      <p className="text-sm text-muted">
        Curated cards from the LLM pipeline — summaries, suspect focus, and calibrated risk.
      </p>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-64" />)
          : list.map((inc, i) => (
              <motion.div
                key={inc._id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
              >
                <Link to={`/incidents/${inc._id}`}>
                  <Card className="h-full transition-colors hover:border-ai-accent/40">
                    <CardHeader className="flex flex-row items-start justify-between gap-2">
                      <div>
                        <CardTitle className="flex items-center gap-2 text-base">
                          <Sparkles className="h-4 w-4 text-ai-accent" />
                          {inc.camera_id}
                        </CardTitle>
                        <p className="mt-1 text-xs text-muted">{inc.location}</p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <RiskBadge level={inc.ai_analysis.risk_level} />
                        {inc.status === 'processing' && (
                          <Badge variant="outline" className="animate-pulse bg-blue-500/10 text-blue-400">
                            Processing...
                          </Badge>
                        )}
                        {inc.status === 'failed' && (
                          <Badge variant="outline" className="bg-red-500/10 text-red-400">
                            Failed
                          </Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="aspect-video rounded-lg bg-gradient-to-br from-surface-elevated to-background" />
                      <p className="line-clamp-3 text-sm text-slate-300">{inc.ai_analysis.summary}</p>
                      <div className="flex items-center justify-between text-xs text-muted">
                        <span>Suspect</span>
                        <span className="font-mono text-ai-accent">{inc.ai_analysis.culprit.id}</span>
                      </div>
                      <ConfidenceBar value={inc.ai_analysis.culprit.confidence} label="Culprit confidence" />
                    </CardContent>
                  </Card>
                </Link>
              </motion.div>
            ))}
      </div>
    </div>
  )
}
