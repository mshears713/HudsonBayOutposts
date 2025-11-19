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
 * Fetch expedition logs with optional filters
 */
export async function fetchLogs(outpostId?: string): Promise<ExpeditionLog[]> {
  const params = outpostId ? `?outpost_id=${outpostId}` : '';
  return apiFetch<ExpeditionLog[]>(`/expedition/logs${params}`);
}
