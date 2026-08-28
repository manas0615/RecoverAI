
interface MetricCardProps {
  label: string;
  value: React.ReactNode;
}

export function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
      <h3 className="text-sm font-medium text-[var(--color-text-secondary)] tracking-tight mb-2">
        {label}
      </h3>
      <div className="text-3xl font-bold font-display text-[var(--color-text-primary)]">
        {value}
      </div>
    </div>
  );
}
