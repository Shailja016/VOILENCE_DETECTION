import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { DashboardLayout } from '@/layouts/DashboardLayout'
import { Dashboard } from '@/pages/Dashboard'
import { LiveFeed } from '@/pages/LiveFeed'
import { Incidents } from '@/pages/Incidents'
import { IncidentDetail } from '@/pages/IncidentDetail'
import { AIAnalysisPage } from '@/pages/AIAnalysisPage'
import { Alerts } from '@/pages/Alerts'
import { Cameras } from '@/pages/Cameras'
import { Users } from '@/pages/Users'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/live" element={<LiveFeed />} />
          <Route path="/incidents" element={<Incidents />} />
          <Route path="/incidents/:id" element={<IncidentDetail />} />
          <Route path="/ai-analysis" element={<AIAnalysisPage />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/cameras" element={<Cameras />} />
          <Route path="/users" element={<Users />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
