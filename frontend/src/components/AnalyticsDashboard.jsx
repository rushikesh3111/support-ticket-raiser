import React, { useState, useEffect } from 'react';
import { apiRequest } from '../services/api';
import { BarChart3, TrendingUp, CheckCircle, AlertOctagon, UserCheck, Shield } from 'lucide-react';

export default function AnalyticsDashboard() {
  const [sla, setSla] = useState(null);
  const [agents, setAgents] = useState([]);
  const [volume, setVolume] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    try {
      const [slaData, agentsData, volumeData] = await Promise.all([
        apiRequest('/reports/sla-compliance'),
        apiRequest('/reports/agent-performance'),
        apiRequest('/reports/ticket-volume')
      ]);
      setSla(slaData);
      setAgents(agentsData);
      setVolume(volumeData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-400">Loading performance metrics...</div>;
  }

  return (
    <div className="space-y-6 animate-in fade-in">
      {/* High-level Metric Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase text-slate-400">Total Volume</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
              <BarChart3 className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-slate-900">{sla?.total_tickets || 0}</p>
          <p className="text-xs text-slate-500 mt-1">Active tickets in desk</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase text-slate-400">SLA Compliance</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-xl">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-emerald-600">{sla?.compliance_rate || 100}%</p>
          <p className="text-xs text-slate-500 mt-1">Target SLA &gt; 95%</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase text-slate-400">Response Breaches</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-xl">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-amber-600">{sla?.response_breaches || 0}</p>
          <p className="text-xs text-slate-500 mt-1">First response delays</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase text-slate-400">Resolution Breaches</span>
            <div className="p-2 bg-red-50 text-red-600 rounded-xl">
              <AlertOctagon className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl font-bold text-red-600">{sla?.resolution_breaches || 0}</p>
          <p className="text-xs text-slate-500 mt-1">Total resolution misses</p>
        </div>
      </div>

      {/* Breakdowns & Agent Leaderboard */}
      <div className="grid grid-cols-2 gap-6">
        {/* Agent Performance Table */}
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <UserCheck className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-slate-900 text-sm">Agent Performance Leaderboard</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-100">
                <tr>
                  <th className="py-2.5 px-3">Agent</th>
                  <th className="py-2.5 px-3">Assigned</th>
                  <th className="py-2.5 px-3">Resolved</th>
                  <th className="py-2.5 px-3">Avg Resolution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {agents.map(a => (
                  <tr key={a.agent_id} className="hover:bg-slate-50/60">
                    <td className="py-3 px-3 font-semibold text-slate-800">{a.agent_name}</td>
                    <td className="py-3 px-3 text-slate-600">{a.assigned_count}</td>
                    <td className="py-3 px-3 font-bold text-emerald-600">{a.resolved_count}</td>
                    <td className="py-3 px-3 text-slate-600">{a.avg_resolution_mins} mins</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="w-5 h-5 text-purple-600" />
            <h3 className="font-bold text-slate-900 text-sm">Ticket Volume By Category</h3>
          </div>
          <div className="space-y-3">
            {volume && Object.entries(volume.by_category).map(([cat, count]) => (
              <div key={cat} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-700">{cat}</span>
                  <span className="text-slate-500">{count} tickets</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${volume.total ? (count / volume.total) * 100 : 0}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
