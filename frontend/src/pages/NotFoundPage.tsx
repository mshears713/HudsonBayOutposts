/**
 * Not Found Page Component
 *
 * 404 error page for invalid routes
 */

import React from 'react';

const NotFoundPage: React.FC = () => {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>404 - Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <a href="/">Return to Home</a>
    </div>
  );
};

export default NotFoundPage;
