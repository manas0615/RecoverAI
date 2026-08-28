import { PageHeader } from '../components/layout/PageHeader';
import { useCases } from '../hooks/useCases';
import { ErrorState } from '../components/feedback/ErrorState';
import { CaseTable } from '../components/data-display/CaseTable';

export function CaseList() {
  const { data, loading, error, refetch } = useCases();

  if (error) {
    return <ErrorState message="Unable to load recovery cases." onRetry={refetch} />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader 
        title="Recovery Cases" 
        subtitle="All detected payment failures and recovery attempts."
      />
      <CaseTable cases={data?.cases || []} loading={loading} />
    </div>
  );
}
