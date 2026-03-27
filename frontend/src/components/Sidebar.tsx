import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Radio,
  ListChecks,
  Sparkles,
  Bell,
  Camera,
  Users,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/live', label: 'Live Feed', icon: Radio },
  { to: '/incidents', label: 'Incidents', icon: ListChecks },
  { to: '/ai-analysis', label: 'AI Analysis', icon: Sparkles },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/cameras', label: 'Cameras', icon: Camera },
  { to: '/users', label: 'Users', icon: Users },
]

export function Sidebar() {
  return (
    <aside className="flex w-64 flex-col border-r border-border bg-surface/90 backdrop-blur-md">
      <div className="flex items-center gap-2 border-b border-border px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/20 text-primary">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-50">Sentinel AI</p>
          <p className="text-xs text-muted">CCTV Intelligence</p>
        </div>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-3">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/15 text-primary'
                  : 'text-muted hover:bg-white/5 hover:text-slate-100'
              )
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-border p-4 text-xs text-muted">
        Secure channel · AES-256
      </div>
    </aside>
  )
}
