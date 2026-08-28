import { render, screen } from '@testing-library/react';
import { Timeline } from '../components/data-display/Timeline';
import { describe, it, expect } from 'vitest';

describe('Timeline', () => {
  it('renders empty state', () => {
    render(<Timeline events={[]} />);
    expect(screen.getByText(/No events recorded/)).toBeInTheDocument();
  });

  it('renders events', () => {
    const events = [{
      audit_event_id: '1',
      timestamp: '2026-08-28T10:00:00Z',
      event_type: 'CASE_CREATED',
      actor: { type: 'SYSTEM', id: null },
      case_id: '123',
      action_id: null,
      decision_reference: null,
      policy_version: null,
      previous_state: null,
      new_state: 'DETECTED',
      evidence_references: [],
      metadata: {}
    }];
    render(<Timeline events={events} />);
    expect(screen.getByText('CASE_CREATED')).toBeInTheDocument();
    expect(screen.getByText('DETECTED')).toBeInTheDocument();
  });
});
