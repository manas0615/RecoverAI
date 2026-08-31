import { useNavigate } from 'react-router-dom';
import type { Case } from '../../types/domain';
import { StatusBadge } from '../status/StatusBadge';
import { MoneyValue } from '../financial/MoneyValue';
import { Inbox } from 'lucide-react';
import { LoadingSkeleton } from '../feedback/LoadingSkeleton';

interface CaseTableProps {
  cases: Case[];
  loading?: boolean;
}

function formatStage(stage?: string) {
  if (!stage) return '-';
  const mapping: Record<string, string> = {
    'WAITING_APPROVAL': 'Human Approval',
    'ESCALATED': 'Human Approval',
    'POLICY_REVIEW': 'Policy Review',
    'EXECUTING': 'Execution',
    'VERIFYING': 'Verification',
    'VERIFIED_SUCCESS': 'Verified',
    'RECOVERED': 'Verified',
    'CLOSED': 'Closed'
  };
  return mapping[stage] || stage.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

export function CaseTable({ cases, loading }: CaseTableProps) {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="border border-[var(--color-border)] rounded-xl overflow-hidden bg-[var(--color-surface)] shadow-sm">
        <div className="divide-y divide-[var(--color-border)]">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="p-4 flex gap-4">
              <LoadingSkeleton className="h-6 w-32" />
              <LoadingSkeleton className="h-6 w-24" />
              <LoadingSkeleton className="h-6 w-20" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (cases.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 border border-[var(--color-border-subtle)] border-dashed rounded-xl bg-[var(--color-surface-secondary)]/50">
        <Inbox className="w-8 h-8 text-[var(--color-text-muted)] mb-3" />
        <p className="text-sm text-[var(--color-text-secondary)] text-center">
          No recovery cases match the current filters.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="hidden lg:block border border-[var(--color-border)] rounded-xl overflow-hidden bg-[var(--color-surface)] shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-[var(--color-surface-secondary)] border-b border-[var(--color-border)]">
              <tr>
                <th className="px-5 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Case</th>
                <th className="px-5 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Amount</th>
                <th className="px-5 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider w-48">Failure</th>
                <th className="px-5 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">AI Recommendation</th>
                <th className="px-5 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Stage</th>
                <th className="px-5 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Updated</th>
                <th className="px-5 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-subtle)]">
              {cases.map((c) => (
                <tr 
                  key={c.case_id}
                  className="group hover:bg-[var(--color-surface-secondary)]/50 transition-colors"
                >
                  <td className="px-5 py-4">
                    <button onClick={() => navigate(`/cases/${c.case_id}`)} className="font-mono text-xs text-[var(--color-primary)] hover:underline focus:outline-none">
                      RC-{c.case_id.slice(0, 4)}
                    </button>
                  </td>
                  <td className="px-5 py-4 text-[var(--color-text-primary)]">
                    <MoneyValue amountMinor={c.amount_minor} currency={c.currency} className="font-medium" />
                    <div className="text-[10px] text-[var(--color-text-muted)] mt-0.5">{c.currency}</div>
                  </td>
                  <td className="px-5 py-4">
                    <div className="font-mono text-xs text-[var(--color-text-secondary)] truncate max-w-[200px]" title={c.failure_code || 'UNKNOWN'}>
                      {c.failure_code || 'UNKNOWN'}
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    {c.recommendation && c.recommendation !== 'N/A' && c.recommendation !== 'UNKNOWN' ? (
                      <span className="inline-flex items-center px-2 py-1 rounded text-[10px] font-mono tracking-wide bg-[var(--color-primary-bg)] text-[var(--color-primary)] border border-[var(--color-primary)]/20">
                        {c.recommendation}
                      </span>
                    ) : (
                      <span className="text-xs text-[var(--color-text-muted)]">N/A</span>
                    )}
                  </td>
                  <td className="px-5 py-4">
                    <StatusBadge status={c.workflow_state === 'WAITING_APPROVAL' ? 'APPROVAL_REQUIRED' : (c.outcome_type === 'RECOVERED' ? 'RECOVERED' : (c.workflow_state === 'EXECUTING' ? 'EXECUTING' : (c.workflow_state === 'ESCALATED' ? 'ESCALATED' : c.status)))} />
                  </td>
                  <td className="px-5 py-4 text-xs text-[var(--color-text-secondary)]">
                    {formatStage(c.workflow_state)}
                  </td>
                  <td className="px-5 py-4 text-[var(--color-text-secondary)] text-xs">
                    {new Date(c.updated_at || c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-5 py-4 text-right">
                    <button 
                      onClick={() => navigate(`/cases/${c.case_id}`)}
                      className="text-xs font-medium text-[var(--color-primary)] hover:text-[var(--color-primary)] hover:underline focus:outline-none"
                    >
                      View Case
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="lg:hidden space-y-4">
        {cases.map((c) => (
          <div 
            key={c.case_id}
            className="flex flex-col p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <button onClick={() => navigate(`/cases/${c.case_id}`)} className="font-mono text-xs text-[var(--color-primary)] hover:underline mb-1">
                  RC-{c.case_id.slice(0, 4)}
                </button>
                <div className="font-mono text-xs text-[var(--color-text-secondary)] truncate max-w-[200px]" title={c.failure_code || 'UNKNOWN'}>
                  {c.failure_code || 'UNKNOWN'}
                </div>
              </div>
              <StatusBadge status={c.workflow_state === 'WAITING_APPROVAL' ? 'APPROVAL_REQUIRED' : (c.outcome_type === 'RECOVERED' ? 'RECOVERED' : c.status)} />
            </div>
            
            <div className="flex items-center justify-between pt-3 border-t border-[var(--color-border-subtle)]">
              <MoneyValue amountMinor={c.amount_minor} currency={c.currency} className="font-medium text-[var(--color-text-primary)]" />
              <button onClick={() => navigate(`/cases/${c.case_id}`)} className="text-sm font-medium text-[var(--color-primary)] hover:underline">
                View Case
              </button>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
