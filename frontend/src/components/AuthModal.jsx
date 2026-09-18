import React, { useState } from 'react';
import { apiRequest, setAuthToken, setCurrentUser } from '../services/api';
import { 
  Shield, LifeBuoy, UserCheck, Lock, Mail, User, Sparkles, ArrowRight, Zap, 
  Bot, CheckCircle2, Terminal, Cpu, KeyRound, Globe, Workflow
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function AuthModal({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('user');
  const [department, setDepartment] = useState('Engineering & DevOps');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleQuickLogin = async (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    executeLogin(demoEmail, demoPassword);
  };

  const executeLogin = async (loginEmail, loginPass) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiRequest('/auth/login/json', {
        method: 'POST',
        body: JSON.stringify({ email: loginEmail, password: loginPass })
      });
      setAuthToken(data.access_token);
      setCurrentUser(data.user);
      onLoginSuccess(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        await apiRequest('/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            name,
            email,
            password,
            role,
            department
          })
        });
      }
      await executeLogin(email, password);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 min-h-screen w-full flex bg-slate-950 text-slate-100 overflow-hidden select-none">
      
      {/* Left 60% Hero Showcase & Animated Agentic Platform Teaser */}
      <div className="hidden lg:flex lg:w-7/12 relative flex-col justify-between p-12 overflow-hidden bg-gradient-to-br from-slate-950 via-indigo-950/70 to-slate-900 border-r border-slate-800">
        
        {/* Ambient Glowing Orbs */}
        <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl pointer-events-none animate-pulse" style={{ animationDelay: '2s' }} />

        {/* Brand Header */}
        <div className="relative z-10 flex items-center gap-3.5">
          <motion.div
            whileHover={{ rotate: 180 }}
            transition={{ duration: 0.6 }}
            className="p-3.5 bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 rounded-3xl shadow-xl shadow-blue-500/25 flex items-center justify-center cursor-pointer"
          >
            <LifeBuoy className="w-8 h-8 text-white" />
          </motion.div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black tracking-tight text-white">SupportDesk Enterprise</h1>
              <span className="text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
                AI Agentic Platform
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">Autonomous Multi-Agent ITSM with Human-In-The-Loop Remediation</p>
          </div>
        </div>

        {/* Interactive Feature Architecture Showcase */}
        <div className="relative z-10 my-auto space-y-6 max-w-xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-3"
          >
            <span className="text-xs font-black uppercase tracking-widest text-indigo-400 flex items-center gap-1.5">
              <Bot className="w-4 h-4 text-purple-400" /> Next-Gen Autonomous AI Operations
            </span>
            <h2 className="text-4xl font-black text-white tracking-tight leading-tight">
              Resolve incidents faster with <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">Multi-Agent Swarms</span> and real-time MCP tooling.
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed font-normal">
              Autonomous Triage, RCA Anomaly Isolation, Semantic Duplicate Clustering, and automated Runbook Execution with Human-in-the-Loop oversight.
            </p>
          </motion.div>

          {/* Feature Matrix Cards */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="p-4 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 hover:border-blue-500/40 transition-all">
              <div className="flex items-center gap-2 text-blue-400 font-bold text-xs mb-1">
                <Cpu className="w-4 h-4" />
                <span>Agentic AI Swarms</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                Triage, RCA, Investigation, and Resolution Agents collaborating to diagnose infrastructure.
              </p>
            </div>

            <div className="p-4 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 hover:border-purple-500/40 transition-all">
              <div className="flex items-center gap-2 text-purple-400 font-bold text-xs mb-1">
                <Terminal className="w-4 h-4" />
                <span>MCP Tool Execution</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                Model Context Protocol connects directly to K8s pods, Prometheus, Redis, and Jira.
              </p>
            </div>

            <div className="p-4 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 hover:border-emerald-500/40 transition-all">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs mb-1">
                <Shield className="w-4 h-4" />
                <span>HITL Approval Gates</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                Human-in-the-loop review protects critical production environments prior to remediation.
              </p>
            </div>

            <div className="p-4 bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 hover:border-amber-500/40 transition-all">
              <div className="flex items-center gap-2 text-amber-400 font-bold text-xs mb-1">
                <Globe className="w-4 h-4" />
                <span>Enterprise Okta SSO/MFA</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                Multi-tenancy isolation with GDPR erasure compliance and audit trail immutability.
              </p>
            </div>
          </div>
        </div>

        {/* Live Cluster Footer Status */}
        <div className="relative z-10 flex items-center justify-between text-xs text-slate-500 pt-6 border-t border-slate-800/80">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="font-mono text-slate-400">Cluster 10.0.32.214:8085 Operational</span>
          </div>
          <span className="font-mono text-[11px]">Sub-500ms p95 SLA</span>
        </div>
      </div>

      {/* Right 40% Full-Height Authentication Command Panel */}
      <div className="w-full lg:w-5/12 flex flex-col justify-center px-8 sm:px-14 py-12 bg-slate-900 overflow-y-auto relative">
        <div className="max-w-md w-full mx-auto space-y-6">
          
          <div>
            <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400 block mb-1">Secure Sign-In</span>
            <h2 className="text-2xl font-black text-white tracking-tight">
              {isRegister ? 'Provision Platform Identity' : 'Authenticate to Platform'}
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              {isRegister ? 'Set up full workspace access with customized RBAC permissions' : 'Access your active incident feeds, AI copilot, and telemetry'}
            </p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3.5 bg-red-950/50 border border-red-800 text-red-300 text-xs rounded-2xl font-medium"
            >
              {error}
            </motion.div>
          )}

          {/* 1-Click Fast Persona Switchers */}
          {!isRegister && (
            <div className="p-4 bg-slate-800/80 rounded-2xl border border-slate-700 space-y-2.5">
              <span className="text-[10px] font-black uppercase tracking-wider text-slate-400 flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-amber-400" /> Instant Persona Quick-Switch
              </span>
              <div className="grid grid-cols-3 gap-2">
                <motion.button
                  whileHover={{ scale: 1.04, y: -1 }}
                  whileTap={{ scale: 0.96 }}
                  type="button"
                  onClick={() => handleQuickLogin('admin@supportdesk.com', 'AdminPass123!')}
                  className="py-2.5 px-2 bg-slate-900 border border-slate-700 hover:border-purple-500 rounded-xl font-bold transition flex flex-col items-center gap-1 text-slate-200 text-xs"
                >
                  <Shield className="w-4 h-4 text-purple-400" />
                  <span>Admin</span>
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.04, y: -1 }}
                  whileTap={{ scale: 0.96 }}
                  type="button"
                  onClick={() => handleQuickLogin('agent@supportdesk.com', 'AgentPass123!')}
                  className="py-2.5 px-2 bg-slate-900 border border-slate-700 hover:border-emerald-500 rounded-xl font-bold transition flex flex-col items-center gap-1 text-slate-200 text-xs"
                >
                  <UserCheck className="w-4 h-4 text-emerald-400" />
                  <span>Agent</span>
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.04, y: -1 }}
                  whileTap={{ scale: 0.96 }}
                  type="button"
                  onClick={() => handleQuickLogin('user@supportdesk.com', 'UserPass123!')}
                  className="py-2.5 px-2 bg-slate-900 border border-slate-700 hover:border-blue-500 rounded-xl font-bold transition flex flex-col items-center gap-1 text-slate-200 text-xs"
                >
                  <User className="w-4 h-4 text-blue-400" />
                  <span>Customer</span>
                </motion.button>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="space-y-4 overflow-hidden"
              >
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1.5">Full Name</label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" />
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Sarah Jenkins"
                      className="w-full pl-11 pr-4 py-2.5 text-xs bg-slate-800 border border-slate-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 font-medium text-white"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1.5">Role Tier</label>
                    <select
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      className="w-full px-3 py-2.5 text-xs bg-slate-800 border border-slate-700 rounded-2xl font-bold text-white focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                    >
                      <option value="user">Customer / User</option>
                      <option value="agent">Support Agent</option>
                      <option value="admin">System Admin</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1.5">Department</label>
                    <input
                      type="text"
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      className="w-full px-3 py-2.5 text-xs bg-slate-800 border border-slate-700 rounded-2xl font-medium text-white focus:outline-none focus:ring-2 focus:ring-blue-500/30"
                    />
                  </div>
                </div>
              </motion.div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5">Corporate Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="identity@company.com"
                  className="w-full pl-11 pr-4 py-2.5 text-xs bg-slate-800 border border-slate-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 font-medium text-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5">Authentication Secret</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-2.5 text-xs bg-slate-800 border border-slate-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-500 font-medium text-white"
                />
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold rounded-2xl transition shadow-xl shadow-blue-500/25 disabled:opacity-50 flex items-center justify-center gap-2 text-xs uppercase tracking-wider"
            >
              <span>{loading ? 'Authenticating...' : isRegister ? 'Provision & Sign In' : 'Sign In with SSO / Password'}</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </form>

          <div className="text-center pt-2">
            <button
              type="button"
              onClick={() => {
                setIsRegister(!isRegister);
                setError(null);
              }}
              className="text-xs text-indigo-400 hover:underline font-bold"
            >
              {isRegister ? 'Already registered? Sign In' : "Need a new account? Create one"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
