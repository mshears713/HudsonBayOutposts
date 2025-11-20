/**
 * Main Application Component with Routing
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import OutpostsPage from './pages/OutpostsPage';
import LogsPage from './pages/LogsPage';
import NotFoundPage from './pages/NotFoundPage';
import './index.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <header style={{
          padding: '1rem 2rem',
          background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
          color: 'white',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ margin: '0 0 0.5rem 0' }}>Hudson Bay Expedition Console</h2>
          <nav>
            <Link to="/" style={{
              color: 'white',
              marginRight: '1.5rem',
              textDecoration: 'none',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px',
              transition: 'background 0.2s'
            }}>Home</Link>
            <Link to="/outposts" style={{
              color: 'white',
              marginRight: '1.5rem',
              textDecoration: 'none',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px'
            }}>Outposts</Link>
            <Link to="/logs" style={{
              color: 'white',
              textDecoration: 'none',
              padding: '0.25rem 0.5rem',
              borderRadius: '4px'
            }}>Expedition Logs</Link>
          </nav>
        </header>

        <main style={{ flex: 1, background: '#f5f5f5' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/outposts" element={<OutpostsPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>

        <footer style={{
          padding: '1rem',
          textAlign: 'center',
          background: '#333',
          color: '#fff',
          fontSize: '0.9rem'
        }}>
          <p style={{ margin: 0 }}>Hudson Bay Expedition Console v1.0.0 | Built with React + FastAPI</p>
        </footer>
      </div>
    </BrowserRouter>
  );
};

export default App;
