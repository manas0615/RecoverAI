import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-[var(--color-danger-bg)] rounded-xl border border-[var(--color-danger)]/20 animate-[shake_0.3s_ease]">
      <AlertCircle className="w-8 h-8 text-[var(--color-danger)] mb-3" />
      <h3 className="text-sm font-medium text-[var(--color-danger)] mb-4">{message}</h3>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white text-[var(--color-text-primary)] text-sm font-medium rounded-lg border border-[var(--color-border)] shadow-sm hover:bg-[var(--color-surface-secondary)] transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      )}
      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-4px); }
          75% { transform: translateX(4px); }
        }
      `}</style>
    </div>
  );
}
