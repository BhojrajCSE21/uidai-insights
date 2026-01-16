/**
 * Dashboard Page
 * Main overview with KPIs, charts, and risk summary
 */

import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';
import apiService from '../services/api';
import { KPICard, RiskBadge, LoadingSpinner, ErrorMessage, SectionHeader } from '../components/UIComponents';

const COLORS = ['#ef4444', '#f59e0b', '#10b981'];

export const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [businessData, setBusinessData] = useState(null);
  const [riskData, setRiskData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [business, risk] = await Promise.all([
          apiService.getBusinessImpact(),
          apiService.getRiskScores(),
        ]);
        setBusinessData(business);
        setRiskData(risk);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to load data. Is the API running?');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  // Format currency in lakhs
  const formatCurrency = (val) => {
    if (val >= 100000) {
      return `₹${(val / 100000).toFixed(1)}L`;
    }
    return `₹${val.toLocaleString()}`;
  };

  // Prepare chart data
  const riskDistribution = [
    { name: 'High', value: riskData?.high_risk_count || 0 },
    { name: 'Medium', value: riskData?.medium_risk_count || 0 },
    { name: 'Low', value: riskData?.low_risk_count || 0 },
  ];

  const topRiskStates = riskData?.scores?.slice(0, 6) || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">UIDAI Insights Dashboard</h1>
        <p className="text-slate-400 mt-2">Real-time analytics and risk monitoring</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Anomalies"
          value={businessData?.fraud_analysis?.total_anomalies_analyzed?.toLocaleString() || '0'}
          icon="🔍"
          color="indigo"
        />
        <KPICard
          title="Potential Savings"
          value={formatCurrency(businessData?.fraud_analysis?.total_potential_savings_inr || 0)}
          icon="💰"
          color="emerald"
          trend="Fraud prevention"
          trendUp
        />
        <KPICard
          title="ROI"
          value={`${businessData?.roi_analysis?.roi_percentage?.toFixed(0) || 0}%`}
          icon="📈"
          color="amber"
          trend="Annual return"
          trendUp
        />
        <KPICard
          title="High Risk States"
          value={riskData?.high_risk_count || 0}
          icon="⚠️"
          color="rose"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution Pie Chart */}
        <div className="glass-card p-6">
          <SectionHeader title="Risk Distribution" subtitle="States by risk category" />
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                itemStyle={{ color: '#f8fafc' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Risk States Bar Chart */}
        <div className="glass-card p-6">
          <SectionHeader title="Top Risk States" subtitle="Risk score (0-100)" />
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topRiskStates} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" />
              <YAxis type="category" dataKey="state" width={120} stroke="#94a3b8" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Bar dataKey="risk_score" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* High Risk States Table */}
      <div className="glass-card p-6">
        <SectionHeader title="High Risk States" subtitle="Immediate attention required" />
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="pb-4 font-medium">State</th>
                <th className="pb-4 font-medium">Risk Score</th>
                <th className="pb-4 font-medium">Category</th>
                <th className="pb-4 font-medium">Total Records</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {riskData?.scores?.filter(s => s.risk_category === 'HIGH').map((state, idx) => (
                <tr key={idx} className="hover:bg-slate-700/30 transition-colors">
                  <td className="py-4 text-white font-medium">{state.state}</td>
                  <td className="py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-rose-500 to-red-600 rounded-full"
                          style={{ width: `${state.risk_score}%` }}
                        />
                      </div>
                      <span className="text-slate-300">{state.risk_score}</span>
                    </div>
                  </td>
                  <td className="py-4"><RiskBadge category={state.risk_category} /></td>
                  <td className="py-4 text-slate-300">{state.total_records?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Business Impact Summary */}
      <div className="glass-card p-6 gradient-border">
        <SectionHeader title="💼 Business Impact Summary" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
          <div className="text-center">
            <p className="text-4xl font-bold text-emerald-400">
              {formatCurrency(businessData?.fraud_analysis?.total_value_generated_inr || 0)}
            </p>
            <p className="text-slate-400 mt-2">Total Value Generated</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-indigo-400">
              {businessData?.roi_analysis?.payback_period_months} mo
            </p>
            <p className="text-slate-400 mt-2">Payback Period</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-amber-400">
              {businessData?.roi_analysis?.efficiency_multiplier?.split('x')[0]}x
            </p>
            <p className="text-slate-400 mt-2">Faster Than Manual</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
