import { useEffect, useState } from 'react'
import { io, type Socket } from 'socket.io-client'

const URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:4000'

export function useSocket() {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const s = io(URL, { transports: ['websocket', 'polling'] })
    setSocket(s)
    s.on('connect', () => setConnected(true))
    s.on('disconnect', () => setConnected(false))
    return () => {
      s.disconnect()
      setSocket(null)
      setConnected(false)
    }
  }, [])

  return { socket, connected }
}
