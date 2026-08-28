import { useHealth } from '../../hooks/useCases';

export function SystemStatus() {
  const { data, loading, error } = useHealth();

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--color-surface-secondary)] border border-[var(--color-border)]">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--color-text-muted)] opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--color-text-muted)]"></span>
        </span>
        <span className="text-xs font-medium text-[var(--color-text-secondary)]">Checking...</span>
      </div>
    );
  }

  const isHealthy = data?.status === 'ok' && !error;

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${isHealthy ? 'bg-[var(--color-success-bg)] border-[var(--color-success)]/20' : 'bg-[var(--color-danger-bg)] border-[var(--color-danger)]/20'}`}>
      <span className={`h-2 w-2 rounded-full ${isHealthy ? 'bg-[var(--color-success)]' : 'bg-[var(--color-danger)]'}`}></span>
      <span className={`text-xs font-medium ${isHealthy ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]'}`}>
        {isHealthy ? 'System Operational' : 'System Degraded'}
      </span>
    </div>
  );
}
