import { Shield } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const users = [
  { name: 'Ops Supervisor', email: 'supervisor@agency.local', role: 'Admin' },
  { name: 'Analyst North', email: 'analyst.n@agency.local', role: 'Analyst' },
  { name: 'Dispatcher', email: 'dispatch@agency.local', role: 'Dispatcher' },
]

export function Users() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2">
        <Shield className="h-5 w-5 text-primary" />
        <CardTitle>Directory</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {users.map((u) => (
          <div
            key={u.email}
            className="flex flex-col justify-between gap-2 rounded-lg border border-border bg-surface/50 px-4 py-3 sm:flex-row sm:items-center"
          >
            <div>
              <p className="font-medium text-slate-100">{u.name}</p>
              <p className="text-sm text-muted">{u.email}</p>
            </div>
            <Badge variant="outline">{u.role}</Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
