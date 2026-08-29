import { KeyRound, ShieldAlert, WifiOff } from 'lucide-react';
import { ApiError } from '../../api/client';
import { ErrorState } from './ErrorState';

interface AccessBoundaryProps {
  error: Error;
  onRetry?: () => void;
  fallbackMessage?: string;
}

export function AccessBoundary({ error, onRetry, fallbackMessage = "An unexpected error occurred." }: AccessBoundaryProps) {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return (
        <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-[var(--color-border)] shadow-sm max-w-lg mx-auto mt-12">
          <div className="w-12 h-12 bg-amber-50 text-amber-600 rounded-full flex items-center justify-center mb-6">
            <KeyRound className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold font-display text-[var(--color-text-primary)] mb-2">
            Access Configuration Required
          </h2>
          <p className="text-sm text-[var(--color-text-secondary)] mb-6 max-w-md">
            The frontend could not authenticate with the backend server. Please verify that the <code>VITE_API_KEY</code> environment variable in your frontend configuration corresponds to the backend's <code>FRONTEND_API_KEY</code>. 
          </p>
          <p className="text-xs text-[var(--color-text-muted)] mb-8">
            You may need to restart the frontend development server after updating the configuration.
          </p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-6 py-2.5 bg-[var(--color-primary)] text-white text-sm font-medium rounded-lg shadow-sm hover:bg-slate-800 transition-colors"
            >
              Retry Connection
            </button>
          )}
        </div>
      );
    }
    
    if (error.status === 403) {
      return (
        <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-[var(--color-border)] shadow-sm max-w-lg mx-auto mt-12">
          <div className="w-12 h-12 bg-red-50 text-red-600 rounded-full flex items-center justify-center mb-6">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold font-display text-[var(--color-text-primary)] mb-2">
            Insufficient Permissions
          </h2>
          <p className="text-sm text-[var(--color-text-secondary)] mb-6 max-w-md">
            Your client is authenticated, but does not have the required authorization level to access this resource.
          </p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-6 py-2.5 bg-white text-[var(--color-text-primary)] border border-[var(--color-border)] text-sm font-medium rounded-lg shadow-sm hover:bg-gray-50 transition-colors"
            >
              Try Again
            </button>
          )}
        </div>
      );
    }
  }

  // Fallback to standard error state, distinguishing unavailable/network errors
  const isNetwork = error.message.toLowerCase().includes('fetch') || error.message.toLowerCase().includes('network');
  
  if (isNetwork) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <WifiOff className="w-8 h-8 text-[var(--color-text-muted)] mb-4" />
        <h3 className="text-sm font-medium text-[var(--color-text-primary)] mb-2">Backend Unavailable</h3>
        <p className="text-sm text-[var(--color-text-secondary)] mb-4">The frontend cannot obtain data from the server.</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="px-4 py-2 bg-white border border-[var(--color-border)] text-[var(--color-text-primary)] text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  return <ErrorState message={fallbackMessage} onRetry={onRetry} />;
}
