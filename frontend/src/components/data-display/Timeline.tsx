import type {  TimelineEvent as DomainTimelineEvent  } from '../../types/domain';
import { Clock } from 'lucide-react';

interface TimelineProps {
  events: DomainTimelineEvent[];
}

export function Timeline({ events }: TimelineProps) {
  if (!events || events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 border border-[var(--color-border-subtle)] border-dashed rounded-xl bg-[var(--color-surface-secondary)]/50">
        <Clock className="w-6 h-6 text-[var(--color-text-muted)] mb-2" />
        <p className="text-sm text-[var(--color-text-secondary)]">No events recorded for this case.</p>
      </div>
    );
  }

  // Sort events chronologically (oldest first or newest first? Let's do newest first for timeline)
  const sortedEvents = [...events].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <div className="relative pl-4 space-y-6 before:absolute before:inset-y-0 before:left-6 before:w-px before:bg-[var(--color-border)]">
      {sortedEvents.map((event) => (
        <div key={event.audit_event_id} className="relative flex gap-6">
          {/* Node marker */}
          <div className="absolute -left-2 mt-1.5 w-4 h-4 rounded-full bg-[var(--color-surface)] border-2 border-[var(--color-primary)] z-10" />
          
          <div className="flex-1 ml-6 p-4 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-surface)] shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between gap-4 mb-2">
              <div>
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold tracking-widest uppercase bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)]">
                  {event.event_type}
                </span>
                <p className="mt-2 text-sm text-[var(--color-text-primary)]">
                  Actor: <span className="font-medium">{event.actor.type}</span> {event.actor.id && `(${event.actor.id})`}
                </p>
              </div>
              <time className="text-xs font-mono text-[var(--color-text-muted)]">
                {new Date(event.timestamp).toLocaleString()}
              </time>
            </div>
            
            {/* Context specific details */}
            {event.new_state && (
              <p className="text-xs text-[var(--color-text-secondary)] mt-2">
                State transition: <span className="font-mono">{event.previous_state || 'None'}</span> → <span className="font-mono font-medium text-[var(--color-text-primary)]">{event.new_state}</span>
              </p>
            )}
            
            {event.metadata && Object.keys(event.metadata).length > 0 && (
              <div className="mt-3 p-3 bg-[var(--color-bg)] rounded-lg text-xs font-mono text-[var(--color-text-secondary)] overflow-x-auto">
                <pre>{JSON.stringify(event.metadata, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
