/**
 * Outpost List Component
 *
 * Displays a list of all Raspberry Pi outposts fetched from the API
 */

import React, { useState, useEffect } from 'react';
import { Outpost } from '../interfaces/outpost';
import { fetchOutposts } from '../api/client';

const OutpostList: React.FC = () => {
  const [outposts, setOutposts] = useState<Outpost[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadOutposts = async () => {
      try {
        setLoading(true);
        const data = await fetchOutposts();
        setOutposts(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load outposts');
        console.error('Error loading outposts:', err);
      } finally {
        setLoading(false);
      }
    };

    loadOutposts();
  }, []);

  if (loading) {
    return <div style={{ padding: '2rem' }}>Loading outposts...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', color: 'red' }}>
        <h3>Error</h3>
        <p>{error}</p>
        <p>Make sure the backend server is running at http://localhost:8000</p>
      </div>
    );
  }

  if (outposts.length === 0) {
    return (
      <div style={{ padding: '2rem' }}>
        <p>No outposts found. Add some outposts to the database to get started.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Raspberry Pi Outposts ({outposts.length})</h2>
      <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
        {outposts.map((outpost) => (
          <div
            key={outpost.id}
            style={{
              border: '1px solid #ccc',
              borderRadius: '8px',
              padding: '1rem',
              background: '#f9f9f9',
            }}
          >
            <h3>{outpost.name}</h3>
            <p><strong>Location:</strong> {outpost.location_lat.toFixed(4)}, {outpost.location_lon.toFixed(4)}</p>
            {outpost.description && <p>{outpost.description}</p>}
            {outpost.api_endpoint && (
              <p style={{ fontSize: '0.9em', color: '#666' }}>
                <strong>API:</strong> {outpost.api_endpoint}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default OutpostList;
