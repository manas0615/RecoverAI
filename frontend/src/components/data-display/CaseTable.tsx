import { useNavigate } from 'react-router-dom';
import type {  Case  } from '../../types/domain';
import { StatusBadge } from '../status/StatusBadge';
import { MoneyValue } from '../financial/MoneyValue';
import { ChevronRight, Inbox } from 'lucide-react';
import { LoadingSkeleton } from '../feedback/LoadingSkeleton';

interface CaseTableProps {
  cases: Case[];
  loading?: boolean;
}

export function CaseTable({ cases, loading }: CaseTableProps) {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="border border-[var(--color-border)] rounded-xl overflow-hidden bg-[var(--color-surface)]">
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
          No recovery cases yet.<br />Cases will appear when payment events are detected.
        </p>
      </div>
    );
  }

  return (
    <div className="border border-[var(--color-border)] rounded-xl overflow-hidden bg-[var(--color-surface)] shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-[var(--color-surface-secondary)] border-b border-[var(--color-border)]">
            <tr>
              <th className="px-6 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Case</th>
              <th className="px-6 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Customer</th>
              <th className="px-6 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Amount at Risk</th>
              <th className="px-6 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 font-medium text-[var(--color-text-secondary)] text-xs uppercase tracking-wider">Updated</th>
              <th className="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-border-subtle)]">
            {cases.map((c) => (
              <tr 
                key={c.case_id}
                onClick={() => navigate(`/cases/${c.case_id}`)}
                className="group cursor-pointer hover:bg-[var(--color-surface-secondary)]/50 transition-colors"
              >
                <td className="px-6 py-4 font-mono text-xs text-[var(--color-text-primary)]">{c.case_id.slice(0, 12)}...</td>
                <td className="px-6 py-4 text-[var(--color-text-secondary)]">{c.customer_id}</td>
                <td className="px-6 py-4 text-[var(--color-text-primary)] font-medium">
                  <MoneyValue amountMinor={c.amount_minor} currency={c.currency} />
                </td>
                <td className="px-6 py-4">
                  <StatusBadge status={c.status} />
                </td>
                <td className="px-6 py-4 text-[var(--color-text-muted)] text-xs">
                  {new Date(c.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-right text-[var(--color-text-muted)] group-hover:text-[var(--color-primary)] transition-colors">
                  <ChevronRight className="w-4 h-4 ml-auto" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
