import { PageHeader } from '../components/layout/PageHeader';
import { Activity, Clock } from 'lucide-react';

export function ActivityLog() {
  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader 
        title="Global Activity Log" 
        subtitle="System-wide audit trail for all recovery events."
      />
      
      <div className="flex flex-col items-center justify-center p-16 border border-[var(--color-border-subtle)] border-dashed rounded-xl bg-[var(--color-surface-secondary)]/30 max-w-4xl mx-auto mt-10">
        <div className="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-full mb-6 shadow-sm">
          <Activity className="w-8 h-8 text-[var(--color-text-muted)]" />
        </div>
        <h2 className="text-xl font-display font-bold text-[var(--color-text-primary)] mb-3">
          Global Audit Coming Soon
        </h2>
        <p className="text-[var(--color-text-secondary)] text-center max-w-md leading-relaxed mb-8">
          Detailed timeline events are currently available on individual Case Detail pages. A unified global view of all system actions across all cases is planned for a future release.
        </p>
        
        <div className="flex items-center gap-2 text-sm font-medium text-[var(--color-text-muted)]">
          <Clock className="w-4 h-4" />
          <span>Slated for Package 18</span>
        </div>
      </div>
    </div>
  );
}
