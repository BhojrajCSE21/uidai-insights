/**
 * Sidebar Navigation Component
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Dashboard', icon: '📊' },
  { path: '/risk', label: 'Risk Scores', icon: '⚠️' },
  { path: '/recommendations', label: 'Actions', icon: '✅' },
];

export const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-64 glass-card m-4 p-4 flex flex-col">
      {/* Logo */}
      <div className="mb-8 p-4">
        <h1 className="gradient-text text-2xl font-bold">UIDAI</h1>
        <p className="text-slate-400 text-sm">Insights Dashboard</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
                ${isActive
                  ? 'bg-indigo-500/20 text-indigo-400 border-l-4 border-indigo-500'
                  : 'text-slate-400 hover:bg-slate-700/50 hover:text-white'
                }
              `}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="pt-4 border-t border-slate-700">
        <p className="text-slate-500 text-xs text-center">
          Built by Bhojraj
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
