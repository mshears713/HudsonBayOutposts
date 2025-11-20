/**
 * Expedition Log List Component
 *
 * Displays expedition logs with filtering options
 */

import React, { useState, useEffect } from 'react';
import { ExpeditionLog } from '../interfaces/outpost';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface ExpeditionLogListProps {
  outpostId?: string;
}

const ExpeditionLogList: React.FC<ExpeditionLogListProps> = ({ outpostId }) => {
  const [logs, setLogs] = useState<ExpeditionLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        setLoading(true);
        const params = outpostId ? `?outpost_id=${outpostId}&limit=20` : '?limit=20';
        const response = await fetch(`${API_URL}/expedition/logs${params}`);

        if (!response.ok) {
          throw new Error(`Failed to load logs: ${response.statusText}`);
        }

        const data = await response.json();
        setLogs(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load logs');
        console.error('Error loading logs:', err);
      } finally {
        setLoading(false);
      }
    };

    loadLogs();
  }, [outpostId]);

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getEventTypeColor = (eventType: string): string => {
    const colors: Record<string, string> = {
      sensor_reading: '#4CAF50',
      status_update: '#2196F3',
      alert: '#FF9800',
      error: '#F44336',
      manual_entry: '#9C27B0',
    };
    return colors[eventType] || '#757575';
  };

  if (loading) {
    return <div style={{ padding: '1rem' }}>Loading logs...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '1rem', color: 'red' }}>
        <h3>Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div style={{ padding: '1rem' }}>
        <p>No expedition logs found.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Expedition Logs ({logs.length})</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {logs.map((log) => (
          <div
            key={log.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '6px',
              padding: '1rem',
              background: '#fff',
              borderLeft: `4px solid ${getEventTypeColor(log.event_type)}`,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span
                style={{
                  background: getEventTypeColor(log.event_type),
                  color: 'white',
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.85rem',
                  fontWeight: 'bold',
                }}
              >
                {log.event_type}
              </span>
              <span style={{ fontSize: '0.9rem', color: '#666' }}>
                {formatTimestamp(log.timestamp)}
              </span>
            </div>
            <div style={{ fontSize: '0.9rem', color: '#333' }}>
              <pre style={{ margin: 0, fontFamily: 'inherit', whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(log.details, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExpeditionLogList;
