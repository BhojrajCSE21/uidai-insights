/**
 * Recommendations Page
 * Actionable items from business analysis
 */

import React, { useEffect, useState } from 'react';
import apiService from '../services/api';
import { LoadingSpinner, ErrorMessage, SectionHeader } from '../components/UIComponents';

const PriorityBadge = ({ priority }) => {
  const classes = {
    CRITICAL: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    HIGH: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    INFO: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  };

  const icons = {
    CRITICAL: '🚨',
    HIGH: '⚠️',
    INFO: 'ℹ️',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${classes[priority] || classes.INFO}`}>
      {icons[priority]} {priority}
    </span>
  );
};

export const Recommendations = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiService.getRecommendations();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load recommendations');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  const criticalRecs = data?.recommendations?.filter(r => r.priority === 'CRITICAL') || [];
  const highRecs = data?.recommendations?.filter(r => r.priority === 'HIGH') || [];
  const infoRecs = data?.recommendations?.filter(r => r.priority === 'INFO') || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Action Items</h1>
        <p className="text-slate-400 mt-2">Prioritized recommendations from risk analysis</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="glass-card p-6 border-l-4 border-rose-500">
          <p className="text-4xl font-bold text-rose-400">{data?.critical_count || 0}</p>
          <p className="text-slate-400">Critical Actions</p>
        </div>
        <div className="glass-card p-6 border-l-4 border-amber-500">
          <p className="text-4xl font-bold text-amber-400">{data?.high_priority_count || 0}</p>
          <p className="text-slate-400">High Priority</p>
        </div>
        <div className="glass-card p-6 border-l-4 border-indigo-500">
          <p className="text-4xl font-bold text-indigo-400">{data?.total_recommendations || 0}</p>
          <p className="text-slate-400">Total Items</p>
        </div>
      </div>

      {/* Critical Section */}
      {criticalRecs.length > 0 && (
        <div>
          <SectionHeader title="🚨 Critical Actions" subtitle="Immediate attention required" />
          <div className="space-y-4">
            {criticalRecs.map((rec, idx) => (
              <div key={idx} className="glass-card p-6 border-l-4 border-rose-500 hover:bg-slate-700/30 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-white">{rec.state}</h3>
                      <PriorityBadge priority={rec.priority} />
                    </div>
                    <p className="text-slate-300">{rec.recommendation}</p>
                    <p className="text-slate-400 mt-2 text-sm">
                      <span className="text-indigo-400">Action:</span> {rec.action}
                    </p>
                    <p className="text-emerald-400 mt-1 text-sm">
                      Impact: {rec.expected_impact}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* High Priority Section */}
      {highRecs.length > 0 && (
        <div>
          <SectionHeader title="⚠️ High Priority" subtitle="This week" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {highRecs.map((rec, idx) => (
              <div key={idx} className="glass-card p-5 hover:scale-[1.01] transition-transform">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-white">{rec.state}</h3>
                  <PriorityBadge priority={rec.priority} />
                </div>
                <p className="text-slate-300 text-sm">{rec.recommendation}</p>
                <p className="text-slate-400 mt-2 text-xs">{rec.action}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Section */}
      {infoRecs.length > 0 && (
        <div>
          <SectionHeader title="ℹ️ Best Practices" subtitle="Learn from top performers" />
          <div className="glass-card overflow-hidden">
            {infoRecs.map((rec, idx) => (
              <div key={idx} className="p-4 border-b border-slate-700/50 last:border-0 hover:bg-slate-700/20 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-white font-medium">{rec.state}</span>
                    <span className="text-slate-400 mx-2">-</span>
                    <span className="text-slate-300">{rec.recommendation}</span>
                  </div>
                  <PriorityBadge priority={rec.priority} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
