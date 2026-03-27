export type RiskLevel = 'Low' | 'Medium' | 'High'

export type AlertStatus = 'pending' | 'sent' | 'resolved'

export type Culprit = {
  id: string
  confidence: number
  reason: string
}

export type AiAnalysis = {
  summary: string
  culprit: Culprit
  behavior: string[]
  risk_level: RiskLevel
  recommendation: string
}

export type Incident = {
  _id: string
  camera_id: string
  location: string
  timestamp: string
  violence: boolean
  confidence: number
  video_url: string
  frames?: unknown[]
  detected_people?: Array<{ id: string; position?: string; motion?: string }>
  ai_analysis: AiAnalysis
  alert_status: AlertStatus
  status?: 'processing' | 'completed' | 'failed'
  createdAt?: string
  updatedAt?: string
}
