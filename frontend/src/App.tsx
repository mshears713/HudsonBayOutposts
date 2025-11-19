/**
 * Main Application Component with Routing
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import OutpostsPage from './pages/OutpostsPage';
import NotFoundPage from './pages/NotFoundPage';
import './index.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header" style={{ padding: '1rem', background: '#282c34', color: 'white' }}>
          <h2>Hudson Bay Expedition Console</h2>
          <nav>
            <Link to="/" style={{ color: 'white', marginRight: '1rem' }}>Home</Link>
            <Link to="/outposts" style={{ color: 'white' }}>Outposts</Link>
          </nav>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/outposts" element={<OutpostsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
