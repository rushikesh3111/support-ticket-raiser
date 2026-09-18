import React, { useState } from 'react';
import { apiRequest, setAuthToken, setCurrentUser } from '../services/api';
import { Shield, LifeBuoy, UserCheck, Lock, Mail, User, Building } from 'lucide-react';

export default function AuthModal({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('user');
  const [department, setDepartment] = useState('IT Operations');
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
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 border border-slate-100 animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-blue-600 rounded-xl text-white shadow-lg shadow-blue-500/30">
            <LifeBuoy className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">SupportDesk Portal</h2>
            <p className="text-sm text-slate-500">
              {isRegister ? 'Create a support desk account' : 'Sign in to access your tickets & SLA dashboard'}
            </p>
          </div>
        </div>

        {error && (
          <div className="p-3.5 mb-5 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl font-medium">
            {error}
          </div>
        )}

        {/* Demo Fast Login Buttons */}
        {!isRegister && (
          <div className="mb-6 p-4 bg-slate-50 rounded-xl border border-slate-200/80">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Quick Demo Personas</p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('admin@supportdesk.com', 'AdminPass123!')}
                className="text-xs py-2 px-2.5 bg-white border border-slate-200 hover:border-blue-500 hover:text-blue-600 rounded-lg font-medium transition shadow-sm flex flex-col items-center gap-1 text-slate-700"
              >
                <Shield className="w-4 h-4 text-purple-600" />
                <span>Admin</span>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('agent@supportdesk.com', 'AgentPass123!')}
                className="text-xs py-2 px-2.5 bg-white border border-slate-200 hover:border-blue-500 hover:text-blue-600 rounded-lg font-medium transition shadow-sm flex flex-col items-center gap-1 text-slate-700"
              >
                <UserCheck className="w-4 h-4 text-emerald-600" />
                <span>Agent</span>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('user@supportdesk.com', 'UserPass123!')}
                className="text-xs py-2 px-2.5 bg-white border border-slate-200 hover:border-blue-500 hover:text-blue-600 rounded-lg font-medium transition shadow-sm flex flex-col items-center gap-1 text-slate-700"
              >
                <User className="w-4 h-4 text-blue-600" />
                <span>Customer</span>
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1.5">Full Name</label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Jane Doe"
                    className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1.5">Role</label>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-3 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
                  >
                    <option value="user">Customer / User</option>
                    <option value="agent">Support Agent</option>
                    <option value="admin">System Admin</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1.5">Department</label>
                  <input
                    type="text"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full px-3 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
                  />
                </div>
              </div>
            </>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold rounded-xl transition shadow-lg shadow-blue-500/25 disabled:opacity-50 mt-2"
          >
            {loading ? 'Authenticating...' : isRegister ? 'Register & Sign In' : 'Sign In'}
          </button>
        </form>

        <div className="mt-5 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            className="text-xs text-blue-600 hover:text-blue-800 font-semibold"
          >
            {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Create one"}
          </button>
        </div>
      </div>
    </div>
  );
}
