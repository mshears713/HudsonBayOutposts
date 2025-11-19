/**
 * TypeScript Interfaces for Hudson Bay Expedition Console
 *
 * Defines type contracts matching backend models
 */

/**
 * Represents a Raspberry Pi outpost
 */
export interface Outpost {
  id: string;
  name: string;
  location_lat: number;
  location_lon: number;
  description: string | null;
  api_endpoint: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Represents an expedition log entry
 */
export interface ExpeditionLog {
  id: string;
  timestamp: string;
  outpost_id: string;
  event_type: string;
  details: Record<string, unknown>;
  created_at: string;
}

/**
 * API response wrapper for lists
 */
export interface ListResponse<T> {
  items: T[];
  total: number;
}

/**
 * API error response
 */
export interface ApiError {
  detail: string;
  status_code: number;
}
