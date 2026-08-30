import type { Case, HealthResponse, RecoveryCasesResponse, TimelineResponse } from '../types/domain';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export class ApiError extends Error {
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
      'X-API-Key': import.meta.env.VITE_API_KEY || 'test_frontend_key_default',
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
  
  analyzeCase: (caseId: string) => fetchJson<{
    status: string;
    recommendation: string;
    recommendation_reason: string;
    expected_recovery_value: number;
    recovery_probability: number;
    probability_meaning: string;
    cause_category: string;
    cause_confidence: number;
    policy_decision: string;
    policy_reasons: string[];
    model_version: string;
  }>(`/api/recovery-cases/${caseId}/analyze`, { method: 'POST' }),
};
