import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CaseDetailView } from '../pages/CaseDetailView';
import { fixtures } from '../test-fixtures/cases';

describe('CaseDetailView State Fixtures', () => {
  it('renders WAITING_APPROVAL state correctly', () => {
    const { caseData, timeline } = fixtures.WAITING_APPROVAL;
    render(<CaseDetailView caseData={caseData} timeline={timeline} />);
    
    expect(screen.getAllByText('WAITING APPROVAL').length).toBeGreaterThan(0);
    
    // Human intervention warning
    expect(screen.getByText('Human Intervention Required')).toBeInTheDocument();
    expect(screen.getAllByText(/Amount exceeds auto-recovery threshold/).length).toBeGreaterThan(0);
  });

  it('renders EXECUTING state correctly', () => {
    const { caseData, timeline } = fixtures.EXECUTING;
    render(<CaseDetailView caseData={caseData} timeline={timeline} />);
    
    // No warning
    expect(screen.queryByText('Human Intervention Required')).not.toBeInTheDocument();
  });

  it('renders UNKNOWN state correctly', () => {
    const { caseData, timeline } = fixtures.UNKNOWN;
    render(<CaseDetailView caseData={caseData} timeline={timeline} />);
    
    // Warning
    expect(screen.getAllByText('External execution state unknown').length).toBeGreaterThan(0);
  });

  it('renders VERIFIED_SUCCESS state correctly', () => {
    const { caseData, timeline } = fixtures.VERIFIED_SUCCESS;
    render(<CaseDetailView caseData={caseData} timeline={timeline} />);
    
    // Status badge
    expect(screen.getAllByText('VERIFIED SUCCESS').length).toBeGreaterThan(0);
  });

  it('renders ESCALATED state correctly', () => {
    const { caseData, timeline } = fixtures.ESCALATED;
    render(<CaseDetailView caseData={caseData} timeline={timeline} />);
    
    expect(screen.getByText('Human Intervention Required')).toBeInTheDocument();
    expect(screen.getAllByText(/Fraud signals detected/).length).toBeGreaterThan(0);
  });
});
