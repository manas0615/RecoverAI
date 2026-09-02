export interface Case {
  timeline?: any[];
  case_id: string;
  merchant_id: string;
  customer_id: string;
  status: 'OPEN' | 'CLOSED';
  created_at: string;
  amount_minor: number;
  currency: string;
  verification_count: number;
  outcome_type?: string;
  recovered_amount_minor?: number;
  workflow_state?: string;
  updated_at?: string;
  failure_code?: string;
  historical_failure_count?: number;
  recommendation?: string;
  confidence?: number;
  reasoning?: string;
  provenance?: string;
  policy_decision?: string;
  policy_reasons?: string[];
  action_type?: string;
  action_status?: string;
  provider?: string;
  external_reference?: string;
  workflow_execution_reference?: string;
  verification_state?: string;
  verification_source?: string;
  verification_checked_at?: string;
  observed_event_type?: string;
  observed_amount_minor?: number;
  observed_currency?: string;
  observed_reference?: string;
  action_requested_at?: string;
  action_executed_at?: string;
  action_id?: string;
  events?: any[];
}

export interface Actor {
  type: string;
  id: string | null;
}

export interface TimelineEvent {
  audit_event_id: string;
  timestamp: string;
  event_type: string;
  actor: Actor;
  case_id: string;
  action_id: string | null;
  decision_reference: string | null;
  policy_version: string | null;
  previous_state: string | null;
  new_state: string | null;
  evidence_references: string[];
  metadata: Record<string, any>;
}

export interface HealthResponse {
  status: string;
}

export interface RecoveryCasesResponse {
  cases: Case[];
}

export interface TimelineResponse {
  events: TimelineEvent[];
}
