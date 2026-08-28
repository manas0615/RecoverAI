
export function LoadingSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-shimmer rounded bg-[var(--color-surface-secondary)] ${className}`} />
  );
}
