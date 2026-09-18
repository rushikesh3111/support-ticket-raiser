import React, { useState, useEffect } from 'react';
import { apiRequest } from '../services/api';
import { motion } from 'framer-motion';
import { 
  Server, Shield, Radio, Activity, Cpu, CheckCircle2, 
  Send, RefreshCw, Layers, Database, Lock, AlertCircle
} from 'lucide-react';

export default function EnterpriseConsoleModal({ isOpen, onClose }) {
  const [diagnostics, setDiagnostics] = useState(null);
  const [webhooks, setWebhooks] = useState([]);
  const [routingRules, setRoutingRules] = useState({});
  const [loading, setLoading] = useState(true);
  const [testingHookId, setTestingHookId] = useState(null);
  const [dispatchResult, setDispatchResult] = useState(null);

  const fetchEnterpriseData = async () => {
    setLoading(true);
    try {
      const [diagData, hookData, routeData] = await Promise.all([
        apiRequest('/enterprise/system-diagnostics'),
        apiRequest('/enterprise/webhooks'),
        apiRequest('/enterprise/auto-routing')
      ]);
      setDiagnostics(diagData);
      setWebhooks(hookData);
      setRoutingRules(routeData.rules || {});
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchEnterpriseData();
    }
  }, [isOpen]);

  const handleTestWebhook = async (hookId) => {
    setTestingHookId(hookId);
    setDispatchResult(null);
    try {
      const res = await apiRequest(`/enterprise/webhooks/${hookId}/test`, { method: 'POST' });
      setDispatchResult(res);
    } catch (err) {
      alert(err.message);
    } finally {
      setTestingHookId(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/75 backdrop-blur-xl z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.94, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.94, y: 15 }}
        transition={{ type: "spring", duration: 0.5 }}
        className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl max-w-4xl w-full h-[85vh] flex flex-col border border-slate-100 dark:border-slate-800 overflow-hidden relative"
      >
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex items-center justify-between shrink-0 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded-2xl">
              <Server className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-black tracking-tight">Enterprise Ops & Telemetry Console</h3>
                <span className="text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping" /> Live Monitored
                </span>
              </div>
              <p className="text-xs text-slate-400">Intelligent queue auto-routing, outbound webhooks, and core health telemetry</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-2 rounded-xl hover:bg-slate-800 transition text-sm font-bold">
            Close ✕
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="text-center py-20 text-slate-400">Querying platform telemetry...</div>
          ) : (
            <>
              {/* Telemetry Metrics */}
              <div>
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                  <Activity className="w-4 h-4 text-blue-500" /> System Diagnostics & Health Status
                </h4>
                <div className="grid grid-cols-4 gap-4">
                  <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/80 dark:border-slate-700">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Health Check</span>
                    <span className="text-sm font-black text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" /> {diagnostics?.system_status}
                    </span>
                  </div>
                  <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/80 dark:border-slate-700">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Total Workload</span>
                    <span className="text-sm font-black text-slate-800 dark:text-slate-100 mt-1 block">
                      {diagnostics?.diagnostics?.total_tickets} Tickets Processed
                    </span>
                  </div>
                  <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/80 dark:border-slate-700">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">SLA Poller Engine</span>
                    <span className="text-sm font-black text-blue-600 dark:text-blue-400 mt-1 block">
                      {diagnostics?.sla_checker_status}
                    </span>
                  </div>
                  <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/80 dark:border-slate-700">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Data Security</span>
                    <span className="text-[11px] font-black text-purple-600 dark:text-purple-400 mt-1 block leading-tight">
                      {diagnostics?.encryption}
                    </span>
                  </div>
                </div>
              </div>

              {/* Intelligent Category Auto-Routing Rules */}
              <div>
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-indigo-500" /> Intelligent Category Auto-Assignment Rules
                </h4>
                <div className="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-2xl border border-slate-200/80 dark:border-slate-700">
                  <p className="text-xs text-slate-600 dark:text-slate-300 mb-3">
                    New incoming tickets are automatically analyzed and assigned to specialized engineering queues:
                  </p>
                  <div className="grid grid-cols-3 gap-3 text-xs">
                    {Object.entries(routingRules).map(([cat, agentId]) => (
                      <div key={cat} className="p-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                        <span className="text-[10px] font-bold uppercase text-indigo-600 dark:text-indigo-400 block">{cat}</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200 mt-0.5 block">→ Routed to Agent #{agentId}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Webhooks & Event Integrations */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-xs font-black uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <Radio className="w-4 h-4 text-emerald-500" /> Outbound Webhook Subscriptions (Slack / Teams / PagerDuty)
                  </h4>
                </div>

                <div className="space-y-3">
                  {webhooks.map((hook) => (
                    <div
                      key={hook.id}
                      className="p-4 bg-white dark:bg-slate-800/80 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center justify-between"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-900 dark:text-slate-100 text-sm">{hook.name}</span>
                          <span className="text-[10px] font-bold px-2 py-0.5 bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 rounded-md">
                            ACTIVE
                          </span>
                        </div>
                        <p className="font-mono text-[11px] text-slate-400 mt-0.5">{hook.url}</p>
                        <div className="flex gap-1.5 mt-2">
                          {hook.events.map(ev => (
                            <span key={ev} className="text-[10px] font-semibold bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-2 py-0.5 rounded-md font-mono">
                              {ev}
                            </span>
                          ))}
                        </div>
                      </div>

                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleTestWebhook(hook.id)}
                        disabled={testingHookId === hook.id}
                        className="px-3.5 py-2 bg-indigo-50 dark:bg-indigo-950 hover:bg-indigo-100 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm"
                      >
                        <Send className="w-3.5 h-3.5" />
                        <span>{testingHookId === hook.id ? 'Pinging...' : 'Send Test Ping'}</span>
                      </motion.button>
                    </div>
                  ))}
                </div>

                {dispatchResult && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 p-4 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 rounded-2xl text-xs"
                  >
                    <div className="flex items-center gap-1.5 font-bold text-emerald-800 dark:text-emerald-300 mb-1">
                      <CheckCircle2 className="w-4 h-4" /> Webhook Test Ping Delivered Successfully (Latency: {dispatchResult.latency_ms}ms)
                    </div>
                    <pre className="text-[11px] font-mono text-emerald-900 dark:text-emerald-200 bg-white/60 dark:bg-slate-900/60 p-2.5 rounded-xl border border-emerald-100 dark:border-emerald-900 overflow-x-auto">
                      {JSON.stringify(dispatchResult, null, 2)}
                    </pre>
                  </motion.div>
                )}
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
}
