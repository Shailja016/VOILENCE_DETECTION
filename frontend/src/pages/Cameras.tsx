import { Camera, Circle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const rows = [
  { id: 'CAM-01', zone: 'Transit', status: 'online', fps: 30, bitrate: '6.2 Mbps' },
  { id: 'CAM-02', zone: 'Transit', status: 'online', fps: 30, bitrate: '5.8 Mbps' },
  { id: 'CAM-03', zone: 'Retail', status: 'degraded', fps: 24, bitrate: '4.1 Mbps' },
  { id: 'CAM-04', zone: 'Parking', status: 'online', fps: 25, bitrate: '5.0 Mbps' },
]

export function Cameras() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2">
        <Camera className="h-5 w-5 text-primary" />
        <CardTitle>Registered cameras</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-border text-muted">
              <th className="pb-3 font-medium">Camera</th>
              <th className="pb-3 font-medium">Zone</th>
              <th className="pb-3 font-medium">Status</th>
              <th className="pb-3 font-medium">FPS</th>
              <th className="pb-3 font-medium">Bitrate</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-b border-border/60 last:border-0">
                <td className="py-3 font-mono text-slate-100">{r.id}</td>
                <td className="py-3">{r.zone}</td>
                <td className="py-3">
                  <Badge variant={r.status === 'online' ? 'success' : 'outline'} className="gap-1">
                    <Circle className="h-2 w-2 fill-current" />
                    {r.status}
                  </Badge>
                </td>
                <td className="py-3">{r.fps}</td>
                <td className="py-3 text-muted">{r.bitrate}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}
