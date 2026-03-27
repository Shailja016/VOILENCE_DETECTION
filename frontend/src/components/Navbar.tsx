import { Bell, Search } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

type Props = {
  title: string
  subtitle?: string
  alertCount?: number
}

export function Navbar({ title, subtitle, alertCount = 0 }: Props) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/80 px-6 backdrop-blur-md">
      <div>
        <h1 className="text-lg font-semibold text-slate-50">{title}</h1>
        {subtitle ? <p className="text-sm text-muted">{subtitle}</p> : null}
      </div>
      <div className="flex items-center gap-3">
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            placeholder="Search cameras, incidents…"
            className="h-10 w-64 rounded-lg border border-border bg-surface/80 pl-9 pr-3 text-sm text-slate-100 placeholder:text-muted focus:border-primary/50 focus:outline-none focus:ring-1 focus:ring-primary/40"
          />
        </div>
        <Button variant="ghost" size="icon" className="relative" aria-label="Alerts">
          <Bell className="h-5 w-5" />
          {alertCount > 0 ? (
            <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-danger px-1 text-[10px] font-bold text-white animate-alert-badge">
              {alertCount > 9 ? '9+' : alertCount}
            </span>
          ) : null}
        </Button>
        <Badge variant="ai" className="hidden sm:inline-flex">
          LLM online
        </Badge>
      </div>
    </header>
  )
}
