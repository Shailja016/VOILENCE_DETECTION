import { Link } from 'react-router-dom'
import { ArrowRight, MapPin } from 'lucide-react'
import { motion } from 'framer-motion'
import type { Incident } from '@/types/incident'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { RiskBadge } from '@/components/RiskBadge'
import { Button } from '@/components/ui/button'

type Props = {
  incident: Incident
  index?: number
}

export function IncidentCard({ incident, index = 0 }: Props) {
  const ts = new Date(incident.timestamp).toLocaleString()
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
    >
      <Card className="hover:border-primary/30 transition-colors">
        <CardHeader className="flex flex-row items-start justify-between gap-2">
          <div>
            <CardTitle className="text-base">{incident.camera_id}</CardTitle>
            <p className="mt-1 flex items-center gap-1 text-xs text-muted">
              <MapPin className="h-3 w-3" />
              {incident.location}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <RiskBadge level={incident.ai_analysis.risk_level} />
            <Badge variant={incident.alert_status === 'pending' ? 'danger' : 'outline'}>
              {incident.alert_status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="line-clamp-2 text-sm text-slate-300">{incident.ai_analysis.summary}</p>
          <div className="flex items-center justify-between text-xs text-muted">
            <span>{ts}</span>
            <span>Vision: {(incident.confidence * 100).toFixed(0)}%</span>
          </div>
          <Button variant="secondary" size="sm" className="w-full" asChild>
            <Link to={`/incidents/${incident._id}`}>
              Open details
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  )
}
