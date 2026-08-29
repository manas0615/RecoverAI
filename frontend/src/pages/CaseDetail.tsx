import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCaseDetails } from '../hooks/useCases';
import { AccessBoundary } from '../components/feedback/AccessBoundary';
import { LoadingSkeleton } from '../components/feedback/LoadingSkeleton';
import { CaseDetailView } from './CaseDetailView';
import { apiClient } from '../api/client';

export function CaseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data, loading, error, refetch } = useCaseDetails(id);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  if (error) {
    return <AccessBoundary error={error} onRetry={refetch} fallbackMessage="Case not found or unable to load details." />;
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

  const handleAnalyze = async () => {
    if (!id) return;
    setIsAnalyzing(true);
    try {
      await apiClient.analyzeCase(id);
      await refetch();
    } catch (err) {
      console.error('Failed to analyze case:', err);
      alert('Analysis unavailable');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <CaseDetailView 
      caseData={data.caseData} 
      timeline={data.timeline} 
      onBack={() => navigate('/cases')}
      onAnalyze={handleAnalyze}
      isAnalyzing={isAnalyzing}
    />
  );
}
