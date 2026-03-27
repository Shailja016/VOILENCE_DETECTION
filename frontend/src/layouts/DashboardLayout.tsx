import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from '@/components/Sidebar'
import { Navbar } from '@/components/Navbar'
import { IncidentsProvider, useIncidentsContext } from '@/contexts/IncidentsContext'

const titles: Record<string, { title: string; subtitle?: string }> = {
  '/': { title: 'Operations dashboard', subtitle: 'Live KPIs and AI insights' },
  '/live': { title: 'Live feed', subtitle: 'Multi-camera grid with AI overlays' },
  '/incidents': { title: 'Incidents', subtitle: 'Searchable log of all events' },
  '/ai-analysis': { title: 'AI analysis', subtitle: 'LLM summaries and risk scoring' },
  '/alerts': { title: 'Alerts', subtitle: 'Real-time dispatch queue' },
  '/cameras': { title: 'Camera management', subtitle: 'Endpoints and health' },
  '/users': { title: 'User management', subtitle: 'Roles and access' },
}

function LayoutShell() {
  const { pathname } = useLocation()
  const meta =
    pathname.startsWith('/incidents/') && pathname !== '/incidents'
      ? { title: 'Incident details', subtitle: 'Forensic review and AI panel' }
      : titles[pathname] ?? { title: 'Sentinel AI', subtitle: undefined }
  const { items } = useIncidentsContext()
  const pendingAlerts = items.filter((i) => i.alert_status === 'pending' && i.violence).length

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar title={meta.title} subtitle={meta.subtitle} alertCount={pendingAlerts} />
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export function DashboardLayout() {
  return (
    <IncidentsProvider>
      <LayoutShell />
    </IncidentsProvider>
  )
}
