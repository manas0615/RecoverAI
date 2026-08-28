import { useParams, useNavigate } from 'react-router-dom';
import { useCaseDetails } from '../hooks/useCases';
import { ErrorState } from '../components/feedback/ErrorState';
import { LoadingSkeleton } from '../components/feedback/LoadingSkeleton';
import { CaseDetailView } from './CaseDetailView';

export function CaseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data, loading, error, refetch } = useCaseDetails(id);

  if (error) {
    return <ErrorState message="Case not found or unable to load details." onRetry={refetch} />;
  }

  if (loading || !data) {
    return (
      <div className="space-y-8 animate-in fade-in duration-300">
        <LoadingSkeleton className="h-10 w-1/3" />
        <LoadingSkeleton className="h-40 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <LoadingSkeleton className="h-64 w-full" />
          <LoadingSkeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  return (
    <CaseDetailView 
      caseData={data.caseData} 
      timeline={data.timeline} 
      onBack={() => navigate('/cases')} 
    />
  );
}
