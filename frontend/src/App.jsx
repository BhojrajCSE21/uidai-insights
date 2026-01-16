/**
 * UIDAI Insights Dashboard - Main App
 * Premium React dashboard with Tailwind CSS
 */

import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import ChatWidget from './components/ChatWidget';
import Dashboard from './pages/Dashboard';
import RiskScores from './pages/RiskScores';
import Recommendations from './pages/Recommendations';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <main className="flex-1 p-8 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/risk" element={<RiskScores />} />
            <Route path="/recommendations" element={<Recommendations />} />
          </Routes>
        </main>

        {/* AI Chat Widget */}
        <ChatWidget />
      </div>
    </BrowserRouter>
  );
}

export default App;

