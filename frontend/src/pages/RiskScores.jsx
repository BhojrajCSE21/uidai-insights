/**
 * Risk Scores Page
 * Full table of all states with risk scores
 */

import React, { useEffect, useState } from 'react';
import apiService from '../services/api';
import { RiskBadge, LoadingSpinner, ErrorMessage, SectionHeader } from '../components/UIComponents';

export const RiskScores = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [filter, setFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('risk_score');
  const [sortDesc, setSortDesc] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const data = await apiService.getRiskScores();
        setRiskData(data);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  // Filter and sort
  let scores = riskData?.scores || [];
  if (filter !== 'ALL') {
    scores = scores.filter(s => s.risk_category === filter);
  }
  scores = [...scores].sort((a, b) => {
    const aVal = a[sortBy];
    const bVal = b[sortBy];
    return sortDesc ? bVal - aVal : aVal - bVal;
  });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortDesc(!sortDesc);
    } else {
      setSortBy(field);
      setSortDesc(true);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Risk Scores</h1>
          <p className="text-slate-400 mt-2">All states ranked by risk level (0-100)</p>
        </div>

        {/* Filter buttons */}
        <div className="flex gap-2">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === cat
                  ? 'bg-indigo-500 text-white'
                  : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-rose-400">{riskData?.high_risk_count || 0}</p>
          <p className="text-slate-400 text-sm">High Risk</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-amber-400">{riskData?.medium_risk_count || 0}</p>
          <p className="text-slate-400 text-sm">Medium Risk</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-3xl font-bold text-emerald-400">{riskData?.low_risk_count || 0}</p>
          <p className="text-slate-400 text-sm">Low Risk</p>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card p-6 overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-slate-400 border-b border-slate-700">
              <th className="pb-4 font-medium">Rank</th>
              <th className="pb-4 font-medium">State</th>
              <th 
                className="pb-4 font-medium cursor-pointer hover:text-white"
                onClick={() => handleSort('risk_score')}
              >
                Risk Score {sortBy === 'risk_score' ? (sortDesc ? '↓' : '↑') : ''}
              </th>
              <th className="pb-4 font-medium">Category</th>
              <th 
                className="pb-4 font-medium cursor-pointer hover:text-white"
                onClick={() => handleSort('total_records')}
              >
                Records {sortBy === 'total_records' ? (sortDesc ? '↓' : '↑') : ''}
              </th>
              <th className="pb-4 font-medium">Progress</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {scores.map((state, idx) => (
              <tr key={idx} className="hover:bg-slate-700/30 transition-colors">
                <td className="py-4 text-slate-500">#{idx + 1}</td>
                <td className="py-4 text-white font-medium">{state.state}</td>
                <td className="py-4 text-white font-bold">{state.risk_score.toFixed(1)}</td>
                <td className="py-4"><RiskBadge category={state.risk_category} /></td>
                <td className="py-4 text-slate-300">{state.total_records?.toLocaleString()}</td>
                <td className="py-4">
                  <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        state.risk_score >= 70 ? 'bg-rose-500' :
                        state.risk_score >= 40 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${state.risk_score}%` }}
                    />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        <div className="mt-4 text-slate-400 text-sm">
          Showing {scores.length} of {riskData?.total_states || 0} states
        </div>
      </div>
    </div>
  );
};

export default RiskScores;
