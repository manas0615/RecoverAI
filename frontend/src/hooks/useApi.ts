import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';

export function useApi<T>(fetcher: () => Promise<T>, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [fetcher, ...deps]);

  useEffect(() => {
    execute();
  }, [execute]);

  return { data, loading, error, refetch: execute };
}

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

export function useAnalytics() {
  const fetcher = useCallback(() => apiClient.getAnalytics(), []);
  return useApi(fetcher);
}

export function useAuditEvents() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchAuditEvents = async () => {
    try {
      setLoading(true);
      const result = await apiClient.getAuditEvents();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditEvents();
  }, []);

  return { data, loading, error, refetch: fetchAuditEvents };
}
