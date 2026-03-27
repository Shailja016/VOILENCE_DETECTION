import { createContext, useContext } from 'react'
import type { Dispatch, ReactNode, SetStateAction } from 'react'
import { useIncidentsList } from '@/hooks/useIncidents'
import type { Incident } from '@/types/incident'

type Ctx = {
  items: Incident[]
  loading: boolean
  usedMock: boolean
  refresh: () => Promise<void>
  setItems: Dispatch<SetStateAction<Incident[]>>
}

const IncidentsContext = createContext<Ctx | null>(null)

export function IncidentsProvider({ children }: { children: ReactNode }) {
  const value = useIncidentsList()
  return <IncidentsContext.Provider value={value}>{children}</IncidentsContext.Provider>
}

export function useIncidentsContext() {
  const ctx = useContext(IncidentsContext)
  if (!ctx) throw new Error('useIncidentsContext must be used within IncidentsProvider')
  return ctx
}
