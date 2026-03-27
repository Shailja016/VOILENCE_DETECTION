import { useEffect, useMemo, useRef, useState } from 'react'
import { CameraGrid, type CameraTile } from '@/components/CameraGrid'
import { useIncidentsContext } from '@/contexts/IncidentsContext'
import { mockIncidents } from '@/data/mock'
import { getCameras, scanCamera, type CameraDto } from '@/lib/api'

export function LiveFeed() {
  const { items } = useIncidentsContext()
  const base = items.length ? items : mockIncidents
  const [cameras, setCameras] = useState<CameraTile[]>([])
  const [loading, setLoading] = useState(true)

  const scanBusyRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    let cancelled = false

    const offlineFallback = () =>
      [
        {
          id: 'CAM-01',
          label: 'CAM-01 - North gate',
          location: 'Metro Station Gate 3',
          video_url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        },
        {
          id: 'CAM-02',
          label: 'CAM-02 - Platform',
          location: 'Platform 2 east',
          video_url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        },
        {
          id: 'CAM-03',
          label: 'CAM-03 - Concourse',
          location: 'Main concourse',
          video_url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        },
        {
          id: 'CAM-04',
          label: 'CAM-04 - Parking',
          location: 'Parking Lot B',
          video_url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        },
        {
          id: 'CAM-05',
          label: 'CAM-05 - Retail',
          location: 'Retail wing',
          video_url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        },
        {
          id: 'CAM-06',
          label: 'CAM-06 - Service',
          location: 'Loading dock',
          video_url: 'https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        },
      ] as CameraTile[]

    async function fetchCameras({ setBusy }: { setBusy: boolean }) {
      try {
        if (setBusy) setLoading(true)
        const res = await getCameras()
        if (cancelled) return
        const mapped: CameraTile[] = res.cameras.map((c: CameraDto) => ({
          id: c.camera_id,
          label: c.label || c.camera_id,
          location: c.location || '',
          video_url: c.video_url,
          violence: false,
          suspectId: undefined,
        }))
        setCameras(mapped)
      } catch {
        if (!cancelled) setCameras(offlineFallback())
      } finally {
        if (setBusy && !cancelled) setLoading(false)
      }
    }

    void fetchCameras({ setBusy: true })
    const interval = window.setInterval(() => {
      // Refresh camera configs so newly updated `video_url` values take effect.
      void fetchCameras({ setBusy: false })
    }, 60000)

    return () => {
      cancelled = true
      window.clearInterval(interval)
    }
  }, [])

  useEffect(() => {
    if (!cameras.length) return
    let cancelled = false
    let timer: number | undefined

    const scanOnce = async () => {
      if (cancelled) return
      await Promise.all(
        cameras.map(async (cam) => {
          if (scanBusyRef.current.has(cam.id)) return
          scanBusyRef.current.add(cam.id)
          try {
            await scanCamera(cam.id)
          } catch {
            // Scan errors are tolerated; UI will remain usable via sockets/rest fetch.
          } finally {
            scanBusyRef.current.delete(cam.id)
          }
        })
      )
    }

    void scanOnce()
    timer = window.setInterval(scanOnce, 15000)

    return () => {
      cancelled = true
      if (timer) window.clearInterval(timer)
    }
  }, [cameras])

  const lastIncidentByCamera = useMemo(() => {
    const map = new Map<string, typeof base[number]>()
    const arr = [...base].sort((a, b) => +new Date(b.timestamp) - +new Date(a.timestamp))
    for (const inc of arr) {
      if (!map.has(inc.camera_id)) map.set(inc.camera_id, inc)
    }
    return map
  }, [base])

  const tiles: CameraTile[] = useMemo(() => {
    return cameras.map((cam) => {
      const latest = lastIncidentByCamera.get(cam.id)
      return {
        ...cam,
        violence: latest?.violence ?? false,
        suspectId: latest?.violence ? latest?.ai_analysis?.culprit?.id : undefined,
      }
    })
  }, [cameras, lastIncidentByCamera])

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted">
        Live CCTV tiles render `video_url`. Every ~15s the UI requests a scan; the backend runs vision (mock for now) and uses the LLM to label culprits.
      </p>
      <CameraGrid cameras={loading ? cameras : tiles} />
    </div>
  )
}
