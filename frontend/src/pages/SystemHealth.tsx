import { PageHeader } from '../components/layout/PageHeader';
import { useHealth } from '../hooks/useApi';
import { ErrorState } from '../components/feedback/ErrorState';
import { CheckCircle2, XCircle } from 'lucide-react';

export function SystemHealth() {
  const { data, loading, error, refetch } = useHealth();

  if (error) {
    return <ErrorState message="Unable to load system health." onRetry={refetch} />;
  }

  const isHealthy = data?.status === 'ok';

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader 
        title="System Health" 
        subtitle="Current operational status of RecoverAI infrastructure."
      />
      
      <div className="p-8 border border-[var(--color-border)] rounded-xl bg-[var(--color-surface)] shadow-sm max-w-2xl">
        <div className="flex items-center gap-4">
          {loading ? (
            <div className="h-12 w-12 rounded-full bg-[var(--color-surface-secondary)] animate-pulse" />
          ) : isHealthy ? (
            <CheckCircle2 className="w-12 h-12 text-[var(--color-success)]" />
          ) : (
            <XCircle className="w-12 h-12 text-[var(--color-danger)]" />
          )}
          
          <div>
            <h3 className="text-lg font-bold font-display text-[var(--color-text-primary)]">
              {loading ? 'Checking Status...' : isHealthy ? 'System Operational' : 'System Degraded'}
            </h3>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">
              RecoverAI backend is reachable and responding normally.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
