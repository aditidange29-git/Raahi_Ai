export interface Opportunity {
  id: string
  title: string
  category: string
  description: string
  deadline: string
  prize_amount?: string
  eligibility_score: number
  portal_url?: string
  decision_date?: string
  criteria?: Criterion[]
  required_documents?: RequiredDoc[]
}

export interface Criterion {
  field: string
  operator: string
  value: string | number | string[]
  label: string
}

export interface RequiredDoc {
  name: string
  description: string
  mandatory: boolean
}

export interface MissionStep {
  id: string
  step_order: number
  name: string
  label: string
  state: 'pending' | 'active' | 'done' | 'failed' | 'skipped'
  started_at?: string
  completed_at?: string
  result?: Record<string, unknown>
}

export interface Mission {
  id: string
  user_id: string
  opportunity_id: string
  title: string
  goal: string
  state: MissionState
  progress: number
  eligibility_score: number
  confirmation_number?: string
  submission_id?: string
  steps: MissionStep[]
  created_at: string
  updated_at: string
}

export type MissionState =
  | 'DISCOVERING' | 'UNDERSTANDING' | 'CHECKING_ELIGIBILITY'
  | 'COLLECTING_DOCUMENTS' | 'PREPARING' | 'WAITING_FOR_APPROVAL'
  | 'EXECUTING' | 'VERIFYING' | 'MONITORING'
  | 'COMPLETED' | 'BLOCKED' | 'FAILED' | 'CANCELLED'

export interface AgentEvent {
  id: string
  mission_id: string
  event_type: string
  message: string
  metadata: Record<string, unknown>
  created_at: string
}

export interface Document {
  id: string
  name: string
  status: string
  last_updated: string
}

export interface Notification {
  id: string
  mission_id?: string
  title: string
  body: string
  type: string
  read: boolean
  created_at: string
}

export interface AgentStatus {
  status: 'idle' | 'running' | 'waiting_approval'
  active_missions: number
  tools_available: string[]
  model_provider: string
  version: string
}
