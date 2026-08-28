import type { Case, TimelineEvent } from '../types/domain';

const baseCase: Case = {
  case_id: 'REC-FIX-001',
  merchant_id: 'MERCH-DEMO',
  customer_id: 'CUST-DEMO',
  status: 'OPEN' as const,
  created_at: new Date().toISOString(),
  amount_minor: 482500,
  currency: 'INR',
  verification_count: 0
};

let timeOffset = 0;
const createEvent = (
  id: string,
  type: string,
  prev: string | null,
  next: string,
  metadata: any = {}
): TimelineEvent => {
  timeOffset += 1000; // stagger by 1 second
  return {
    audit_event_id: `evt_${id}`,
    timestamp: new Date(Date.now() + timeOffset).toISOString(),
    event_type: type,
  actor: { type: 'SYSTEM', id: null },
  case_id: baseCase.case_id,
  action_id: null,
  decision_reference: null,
  policy_version: '1.0',
  previous_state: prev,
  new_state: next,
  evidence_references: [],
  metadata
  };
};

export const fixtures = {
  DETECTED: {
    caseData: { ...baseCase, status: 'OPEN' as const },
    timeline: [
      createEvent('1', 'RECOVERY_STATE_CHANGED', null, 'DETECTED', { reason: 'Webhook received' })
    ]
  },
  WAITING_APPROVAL: {
    caseData: { ...baseCase, status: 'OPEN' as const },
    timeline: [
      createEvent('1', 'RECOVERY_STATE_CHANGED', null, 'DETECTED'),
      createEvent('2', 'LLM_RECOMMENDATION_CREATED', 'DETECTED', 'ASSESSED', { recommended_action: 'CREATE_PAYMENT_LINK', reasoning: 'High probability of recovery.' }),
      createEvent('3', 'POLICY_DECISION_CREATED', 'ASSESSED', 'PLANNING', { decision: 'WAITING_APPROVAL', decision_reason: 'Amount exceeds auto-recovery threshold. Requires human approval.' }),
      createEvent('4', 'RECOVERY_STATE_CHANGED', 'PLANNING', 'WAITING_APPROVAL')
    ]
  },
  EXECUTING: {
    caseData: { ...baseCase, status: 'OPEN' as const },
    timeline: [
      createEvent('1', 'RECOVERY_STATE_CHANGED', null, 'DETECTED'),
      createEvent('2', 'LLM_RECOMMENDATION_CREATED', 'DETECTED', 'ASSESSED', { recommended_action: 'CREATE_PAYMENT_LINK' }),
      createEvent('3', 'POLICY_DECISION_CREATED', 'ASSESSED', 'PLANNING', { decision: 'APPROVED' }),
      createEvent('4', 'ACTION_EXECUTION_STARTED', 'PLANNING', 'EXECUTING', { action: 'CREATE_PAYMENT_LINK' })
    ]
  },
  UNKNOWN: {
    caseData: { ...baseCase, status: 'OPEN' as const },
    timeline: [
      createEvent('1', 'RECOVERY_STATE_CHANGED', null, 'DETECTED'),
      createEvent('2', 'ACTION_EXECUTION_STARTED', 'PLANNING', 'EXECUTING'),
      createEvent('3', 'RECOVERY_STATE_CHANGED', 'EXECUTING', 'UNKNOWN', { error: 'Timeout waiting for external provider response' })
    ]
  },
  VERIFYING: {
    caseData: { ...baseCase, status: 'OPEN' as const, verification_count: 1 },
    timeline: [
      createEvent('1', 'RECOVERY_STATE_CHANGED', null, 'DETECTED'),
      createEvent('2', 'ACTION_EXECUTION_COMPLETED', 'EXECUTING', 'VERIFICATION_PENDING'),
      createEvent('3', 'VERIFICATION_STARTED', 'VERIFICATION_PENDING', 'VERIFYING')
    ]
  },
  VERIFIED_SUCCESS: {
    caseData: { ...baseCase, status: 'CLOSED' as const, verification_count: 1 },
    timeline: [
      createEvent('1', 'RECOVERY_STATE_CHANGED', null, 'DETECTED'),
      createEvent('2', 'ACTION_EXECUTION_COMPLETED', 'EXECUTING', 'VERIFICATION_PENDING'),
      createEvent('3', 'VERIFICATION_COMPLETED', 'VERIFYING', 'VERIFIED_SUCCESS', { verified_amount: 482500 }),
      createEvent('4', 'RECOVERY_STATE_CHANGED', 'VERIFIED_SUCCESS', 'CLOSED', { outcome: 'SUCCESS' })
    ]
  },
  VERIFIED_FAILURE: {
    caseData: { ...baseCase, status: 'CLOSED' as const, verification_count: 1 },
    timeline: [
      createEvent('1', 'RECOVERY_STATE_CHANGED', null, 'DETECTED'),
      createEvent('2', 'ACTION_EXECUTION_COMPLETED', 'EXECUTING', 'VERIFICATION_PENDING'),
      createEvent('3', 'VERIFICATION_COMPLETED', 'VERIFYING', 'VERIFIED_FAILURE', { reason: 'Payment link expired' }),
      createEvent('4', 'RECOVERY_STATE_CHANGED', 'VERIFIED_FAILURE', 'CLOSED', { outcome: 'FAILURE' })
    ]
  },
  ESCALATED: {
    caseData: { ...baseCase, status: 'OPEN' as const },
    timeline: [
      createEvent('1', 'RECOVERY_STATE_CHANGED', null, 'DETECTED'),
      createEvent('2', 'POLICY_DECISION_CREATED', 'ASSESSED', 'PLANNING', { decision: 'ESCALATED', decision_reason: 'Fraud signals detected.' }),
      createEvent('3', 'RECOVERY_STATE_CHANGED', 'PLANNING', 'ESCALATED')
    ]
  }
};
