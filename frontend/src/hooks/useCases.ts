import { useCallback } from 'react';
import { apiClient } from '../api/client';
import { useApi } from './useApi';

export function useHealth() {
  const fetcher = useCallback(() => apiClient.getHealth(), []);
  return useApi(fetcher);
}

export function useCases() {
  const fetcher = useCallback(() => apiClient.getCases(), []);
  return useApi(fetcher);
}

export function useCaseDetails(caseId: string | undefined) {
  const fetcher = useCallback(async () => {
    if (!caseId) throw new Error('No case ID provided');
    const [caseData, timelineData] = await Promise.all([
      apiClient.getCase(caseId),
      apiClient.getTimeline(caseId)
    ]);
    return { caseData, timeline: timelineData.events };
  }, [caseId]);

  return useApi(fetcher, [caseId]);
}
