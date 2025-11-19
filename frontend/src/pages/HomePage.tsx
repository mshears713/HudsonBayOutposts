/**
 * Home Page Component
 *
 * Landing page for the Hudson Bay Expedition Console
 */

import React from 'react';

const HomePage: React.FC = () => {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Hudson Bay Expedition Console</h1>
      <p>Welcome to the interactive expedition platform for managing Raspberry Pi outposts.</p>
      <nav style={{ marginTop: '2rem' }}>
        <ul>
          <li><a href="/outposts">View Outposts</a></li>
        </ul>
      </nav>
    </div>
  );
};

export default HomePage;
