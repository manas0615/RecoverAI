
interface UnavailableMetricProps {
  label: string;
}

export function UnavailableMetric({ label }: UnavailableMetricProps) {
  return (
    <div className="flex flex-col p-6 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface-secondary)]/50 opacity-70">
      <h3 className="text-sm font-medium text-[var(--color-text-muted)] tracking-tight mb-2">
        {label}
      </h3>
      <div className="flex items-center gap-2 text-[var(--color-text-muted)]">
        <span className="text-2xl font-bold font-display">—</span>
        <span className="text-xs uppercase tracking-wider font-medium">Data Unavailable</span>
      </div>
    </div>
  );
}
