/**
 * API Client for Hudson Bay Backend
 *
 * Handles all HTTP requests to the backend API
 */

import { Outpost, ExpeditionLog } from '../interfaces/outpost';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch all outposts
 */
export async function fetchOutposts(): Promise<Outpost[]> {
  return apiFetch<Outpost[]>('/outposts');
}

/**
 * Fetch a single outpost by ID
 */
export async function fetchOutpost(id: string): Promise<Outpost> {
  return apiFetch<Outpost>(`/outposts/${id}`);
}

/**
 * Fetch expedition logs with optional filters
 */
export async function fetchLogs(params?: {
  outpostId?: string;
  eventType?: string;
  limit?: number;
  offset?: number;
}): Promise<ExpeditionLog[]> {
  const queryParams = new URLSearchParams();

  if (params?.outpostId) queryParams.append('outpost_id', params.outpostId);
  if (params?.eventType) queryParams.append('event_type', params.eventType);
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const query = queryParams.toString();
  return apiFetch<ExpeditionLog[]>(`/expedition/logs${query ? `?${query}` : ''}`);
}

/**
 * Create a new expedition log
 */
export async function createLog(log: {
  outpost_id: string;
  event_type: string;
  details: Record<string, unknown>;
  timestamp?: string;
}): Promise<ExpeditionLog> {
  return apiFetch<ExpeditionLog>('/expedition/logs', {
    method: 'POST',
    body: JSON.stringify(log),
  });
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<{ status: string; service: string }> {
  return apiFetch<{ status: string; service: string }>('/health');
}
