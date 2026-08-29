import { Link } from 'react-router-dom';
import { PageHeader } from '../components/layout/PageHeader';
import { FileQuestion } from 'lucide-react';

export function NotFound() {
  return (
    <div className="space-y-6">
      <PageHeader title="Page Not Found" subtitle="Error 404" />
      <div className="flex flex-col items-center justify-center py-20 px-4 text-center rounded-xl bg-white border border-[var(--color-border)] shadow-sm">
        <FileQuestion className="h-12 w-12 text-[var(--color-text-muted)] mb-4" />
        <h2 className="text-xl font-semibold text-[var(--color-text)] mb-2">
          We couldn't find that page
        </h2>
        <p className="text-[var(--color-text-muted)] max-w-md mb-6">
          The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
        </p>
        <Link
          to="/"
          className="inline-flex items-center justify-center px-4 py-2 bg-[var(--color-primary)] text-white text-sm font-medium rounded-lg hover:opacity-90 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[var(--color-primary)]"
        >
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}
