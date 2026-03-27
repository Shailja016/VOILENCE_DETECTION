import { useState } from 'react'
import { motion } from 'framer-motion'
import { Video } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

export type CameraTile = {
  id: string
  label: string
  location: string
  violence?: boolean
  suspectId?: string
  thumbnail?: string
  video_url?: string
}

type Props = {
  cameras: CameraTile[]
  highlightCulpritId?: string
}

export function CameraGrid({ cameras, highlightCulpritId }: Props) {
  const [videoErrors, setVideoErrors] = useState<Record<string, boolean>>({})

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {cameras.map((cam, i) => (
        <motion.div
          key={cam.id}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
        >
          <Card className="overflow-hidden">
            <div
              className={cn(
                'relative aspect-video bg-gradient-to-br from-surface-elevated to-background',
                cam.violence && 'ring-2 ring-danger/60'
              )}
            >
              {cam.video_url && !videoErrors[cam.id] ? (
                <video
                  key={`${cam.id}:${cam.video_url}`}
                  src={cam.video_url}
                  className="h-full w-full object-cover opacity-90"
                  autoPlay
                  muted
                  loop
                  playsInline
                  preload="metadata"
                  crossOrigin="anonymous"
                  onCanPlay={() => {
                    setVideoErrors((prev) => ({ ...prev, [cam.id]: false }))
                  }}
                  onError={() => {
                    setVideoErrors((prev) => ({ ...prev, [cam.id]: true }))
                  }}
                />
              ) : cam.thumbnail ? (
                <img src={cam.thumbnail} alt="" className="h-full w-full object-cover opacity-80" />
              ) : (
                <div className="flex h-full w-full items-center justify-center text-muted">
                  <Video className="h-10 w-10 opacity-40" />
                </div>
              )}
              {/* Simulated bounding box for culprit */}
              {cam.violence && cam.suspectId && cam.suspectId !== 'unknown' && (
                <div
                  className={cn(
                    'absolute rounded-md border-2 border-dashed border-ai-accent/90 shadow-[0_0_20px_rgba(139,92,246,0.35)] transition-all',
                    highlightCulpritId === cam.suspectId || !highlightCulpritId
                      ? 'left-[12%] top-[22%] h-[42%] w-[28%]'
                      : 'opacity-40'
                  )}
                >
                  <span className="absolute -top-6 left-0 rounded bg-ai-accent/90 px-1.5 py-0.5 text-[10px] font-semibold text-white">
                    Suspect {cam.suspectId}
                  </span>
                </div>
              )}
              <div className="absolute left-2 top-2 flex flex-wrap gap-1">
                {cam.violence ? (
                  <Badge variant="danger" className="animate-alert-badge">
                    Violence Detected
                  </Badge>
                ) : (
                  <Badge variant="success">Normal</Badge>
                )}
              </div>
              {cam.video_url && videoErrors[cam.id] ? (
                <div className="pointer-events-none absolute bottom-2 left-2 right-2">
                  <div className="rounded-lg border border-danger/50 bg-danger/10 p-2 text-center text-xs text-slate-200">
                    Video unavailable (fetch blocked or CORS/range issue)
                  </div>
                </div>
              ) : null}
            </div>
            <CardContent className="pt-4">
              <p className="font-medium text-slate-100">{cam.label}</p>
              <p className="text-xs text-muted">{cam.location}</p>
              {cam.suspectId ? (
                <p className="mt-2 text-xs text-ai-accent">
                  AI identified suspect: <span className="font-mono">{cam.suspectId}</span>
                </p>
              ) : null}
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
