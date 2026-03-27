import { motion } from 'framer-motion'
import { Activity, ShieldAlert, Sparkles, Video } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { IncidentCard } from '@/components/IncidentCard'
import { useIncidentsContext } from '@/contexts/IncidentsContext'
import { Badge } from '@/components/ui/badge'

function StatCard({
  label,
  value,
  icon: Icon,
  accent,
}: {
  label: string
  value: string | number
  icon: typeof Activity
  accent: string
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted">{label}</CardTitle>
        <div className={`rounded-lg p-2 ${accent}`}>
          <Icon className="h-4 w-4 text-white" />
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-semibold tracking-tight text-slate-50">{value}</p>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-primary to-ai-accent"
            initial={{ width: 0 }}
            animate={{ width: '78%' }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </div>
      </CardContent>
    </Card>
  )
}

export function Dashboard() {
  const { items, loading, usedMock } = useIncidentsContext()
  const violent = items.filter((i) => i.violence).length
  const pending = items.filter((i) => i.alert_status === 'pending').length
  const high = items.filter((i) => i.ai_analysis.risk_level === 'High').length

  const recent = [...items].sort((a, b) => +new Date(b.timestamp) - +new Date(a.timestamp)).slice(0, 3)

  return (
    <div className="space-y-8">
      {usedMock ? (
        <Badge variant="outline" className="border-amber-500/50 text-amber-200">
          Demo data — API unreachable
        </Badge>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Active cameras" value={12} icon={Video} accent="bg-primary/30" />
        <StatCard label="Violence events (24h)" value={loading ? '—' : violent} icon={ShieldAlert} accent="bg-danger/30" />
        <StatCard label="Open alerts" value={loading ? '—' : pending} icon={Activity} accent="bg-ai-accent/30" />
        <StatCard label="High risk" value={loading ? '—' : high} icon={Sparkles} accent="bg-emerald-500/25" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Incident volume</CardTitle>
            <p className="text-sm text-muted">Last 7 days (simulated trend)</p>
          </CardHeader>
          <CardContent>
            <div className="flex h-48 items-end gap-2">
              {[32, 45, 28, 60, 42, 55, 48].map((h, i) => (
                <motion.div
                  key={i}
                  className="flex-1 rounded-t-md bg-gradient-to-t from-primary/20 to-primary/70"
                  initial={{ height: 0 }}
                  animate={{ height: `${h}%` }}
                  transition={{ delay: i * 0.06, duration: 0.5 }}
                />
              ))}
            </div>
            <div className="mt-2 flex justify-between text-xs text-muted">
              <span>Mon</span>
              <span>Sun</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI insights</CardTitle>
            <p className="text-sm text-muted">LLM highlights</p>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-slate-300">
            {loading ? (
              <>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-full" />
              </>
            ) : (
              recent.map((inc) => (
                <div key={inc._id} className="rounded-lg border border-border bg-surface/50 p-3">
                  <p className="text-xs font-mono text-ai-accent">{inc.camera_id}</p>
                  <p className="mt-1 line-clamp-3 text-xs leading-relaxed">{inc.ai_analysis.summary}</p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-50">Recent incidents</h2>
        {loading ? (
          <div className="grid gap-4 md:grid-cols-3">
            <Skeleton className="h-40" />
            <Skeleton className="h-40" />
            <Skeleton className="h-40" />
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-3">
            {recent.map((inc, i) => (
              <IncidentCard key={inc._id} incident={inc} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
