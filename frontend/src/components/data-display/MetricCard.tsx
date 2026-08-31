import React from 'react';

interface MetricCardProps {
  label: string;
  value: React.ReactNode;
  labelColor?: string;
  icon?: React.ReactNode;
}

export function MetricCard({ label, value, labelColor = 'text-[var(--color-text-secondary)]', icon }: MetricCardProps) {
  return (
    <div className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
      <div className="flex items-center gap-2 mb-2">
        {icon && icon}
        <h3 className={`text-sm font-medium tracking-tight uppercase ${labelColor}`}>
          {label}
        </h3>
      </div>
      <div className="text-3xl font-bold font-display text-[var(--color-text-primary)]">
        {value}
      </div>
    </div>
  );
}
