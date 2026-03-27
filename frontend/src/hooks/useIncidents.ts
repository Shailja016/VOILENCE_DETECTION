import { useCallback, useEffect, useState } from 'react'
import { getIncidents } from '@/lib/api'
import { useSocket } from '@/hooks/useSocket'
import { mockIncidents } from '@/data/mock'
import type { Incident } from '@/types/incident'

export function useIncidentsList(initial?: Incident[]) {
  const [items, setItems] = useState<Incident[]>(initial ?? [])
  const [loading, setLoading] = useState(true)
  const [usedMock, setUsedMock] = useState(false)
  const { socket } = useSocket()

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const { incidents } = await getIncidents({ limit: 100 })
      setItems(incidents)
      setUsedMock(false)
    } catch {
      setItems(mockIncidents)
      setUsedMock(true)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  useEffect(() => {
    if (!socket) return
    const onNew = (payload: { incident: Incident }) => {
      setItems((prev) => {
        const rest = prev.filter((x) => x._id !== payload.incident._id)
        return [payload.incident, ...rest]
      })
      setUsedMock(false)
    }
    const onUpd = (payload: { incident: Incident }) => {
      setItems((prev) => prev.map((x) => (x._id === payload.incident._id ? payload.incident : x)))
    }
    socket.on('new_incident', onNew)
    socket.on('incident_updated', onUpd)
    return () => {
      socket.off('new_incident', onNew)
      socket.off('incident_updated', onUpd)
    }
  }, [socket])

  return { items, loading, usedMock, refresh, setItems }
}
