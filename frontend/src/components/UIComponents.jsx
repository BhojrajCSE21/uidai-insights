/**
 * KPI Card Component
 * Displays a metric with an icon and optional trend
 */

import React from 'react';

export const KPICard = ({ title, value, icon, trend, trendUp, color = 'indigo' }) => {
  const colorClasses = {
    indigo: 'from-indigo-500 to-purple-500',
    emerald: 'from-emerald-500 to-teal-500',
    amber: 'from-amber-500 to-orange-500',
    rose: 'from-rose-500 to-pink-500',
  };

  return (
    <div className="glass-card p-6 hover:scale-[1.02] transition-transform duration-300">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-sm font-medium mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {trend && (
            <p className={`text-sm mt-2 ${trendUp ? 'text-emerald-400' : 'text-rose-400'}`}>
              {trendUp ? '↑' : '↓'} {trend}
            </p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </div>
  );
};

/**
 * Risk Badge Component
 * Colored badge for risk categories
 */
export const RiskBadge = ({ category }) => {
  const classes = {
    HIGH: 'badge-high',
    MEDIUM: 'badge-medium',
    LOW: 'badge-low',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${classes[category] || classes.LOW}`}>
      {category}
    </span>
  );
};

/**
 * Loading Spinner
 */
export const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-8">
    <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
  </div>
);

/**
 * Error Message
 */
export const ErrorMessage = ({ message }) => (
  <div className="glass-card p-6 border-l-4 border-rose-500">
    <p className="text-rose-400 font-medium">Error</p>
    <p className="text-slate-300 mt-1">{message}</p>
  </div>
);

/**
 * Section Header
 */
export const SectionHeader = ({ title, subtitle }) => (
  <div className="mb-6">
    <h2 className="text-2xl font-bold text-white">{title}</h2>
    {subtitle && <p className="text-slate-400 mt-1">{subtitle}</p>}
  </div>
);
