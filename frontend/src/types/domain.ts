export interface Case {
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
