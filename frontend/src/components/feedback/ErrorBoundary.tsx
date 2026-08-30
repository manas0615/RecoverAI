import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCcw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8 m-8 bg-[var(--color-surface)] border border-[var(--color-danger)]/20 rounded-xl shadow-sm">
          <div className="w-12 h-12 rounded-full bg-[var(--color-danger-bg)] flex items-center justify-center mb-4">
            <AlertTriangle className="w-6 h-6 text-[var(--color-danger)]" />
          </div>
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-2">Something went wrong</h2>
          <p className="text-sm text-[var(--color-text-secondary)] text-center max-w-md mb-6">
            We encountered an unexpected error while rendering this view. The system is still running, but this specific page is currently unavailable.
          </p>
          <div className="flex gap-4">
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--color-primary)] text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity"
            >
              <RefreshCcw className="w-4 h-4" />
              Reload Page
            </button>
            <button
              onClick={() => { this.setState({ hasError: false }); window.location.href = '/'; }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm font-medium rounded-lg hover:bg-[var(--color-border-subtle)] transition-colors border border-[var(--color-border)]"
            >
              <Home className="w-4 h-4" />
              Return Home
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
