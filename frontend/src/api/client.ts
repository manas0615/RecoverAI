import type { Case, HealthResponse, RecoveryCasesResponse, TimelineResponse } from '../types/domain';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': import.meta.env.VITE_API_KEY || '',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`);
  }

  return response.json();
}

export const apiClient = {
  getHealth: () => fetchJson<HealthResponse>('/api/health'),
  
  getCases: () => fetchJson<RecoveryCasesResponse>('/api/recovery-cases'),
  
  getCase: (caseId: string) => fetchJson<Case>(`/api/recovery-cases/${caseId}`),
  
  getTimeline: (caseId: string) => fetchJson<TimelineResponse>(`/api/recovery-cases/${caseId}/timeline`),
};
