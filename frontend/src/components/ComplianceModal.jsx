import React, { useState } from 'react';
import { apiRequest } from '../services/api';
import { motion } from 'framer-motion';
import { ShieldCheck, Mail, UserX, AlertTriangle, CheckCircle2, Lock, Trash2, Send } from 'lucide-react';

export default function ComplianceModal({ isOpen, onClose }) {
  const [emailToErase, setEmailToErase] = useState('');
  const [erasureLoading, setErasureLoading] = useState(false);
  const [erasureResult, setErasureResult] = useState(null);

  const [inboundEmail, setInboundEmail] = useState('');
  const [inboundName, setInboundName] = useState('');
  const [inboundSubject, setInboundSubject] = useState('');
  const [inboundBody, setInboundBody] = useState('');
  const [inboundCategory, setInboundCategory] = useState('IT Support');
  const [inboundLoading, setInboundLoading] = useState(false);
  const [inboundResult, setInboundResult] = useState(null);

  if (!isOpen) return null;

  const handleErasure = async (e) => {
    e.preventDefault();
    if (!window.confirm(`Execute GDPR Right to Erasure on ${emailToErase}? This will purge PII and scrub tickets.`)) return;
    setErasureLoading(true);
    setErasureResult(null);
    try {
      const res = await apiRequest(`/compliance/gdpr/erasure?user_email=${encodeURIComponent(emailToErase)}`, {
        method: 'POST'
      });
      setErasureResult(res);
      setEmailToErase('');
    } catch (err) {
      alert(err.message);
    } finally {
      setErasureLoading(false);
    }
  };

  const handleInboundSimulation = async (e) => {
    e.preventDefault();
    setInboundLoading(true);
    setInboundResult(null);
    try {
      const res = await apiRequest('/compliance/inbound-email', {
        method: 'POST',
        body: JSON.stringify({
          sender_email: inboundEmail,
          sender_name: inboundName,
          subject: inboundSubject,
          body_plain: inboundBody,
          category: inboundCategory,
          priority: 'High'
        })
      });
      setInboundResult(res);
      setInboundSubject('');
      setInboundBody('');
    } catch (err) {
      alert(err.message);
    } finally {
      setInboundLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/75 backdrop-blur-xl z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.94, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.94, y: 15 }}
        transition={{ type: "spring", duration: 0.5 }}
        className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl max-w-4xl w-full h-[85vh] flex flex-col border border-slate-100 dark:border-slate-800 overflow-hidden relative"
      >
        <div className="p-6 bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white flex items-center justify-between shrink-0 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-2xl">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-black tracking-tight">Compliance & Inbound Gateway Control</h3>
              <p className="text-xs text-slate-400">GDPR Right to Erasure, PII Scrubbing, and Email-to-Ticket Ingestion</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-2 rounded-xl hover:bg-slate-800 transition text-sm font-bold">
            Close ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-2 gap-6">
          {/* Left Col: Email Ingestion Parser */}
          <div className="p-5 bg-slate-50 dark:bg-slate-800/60 rounded-3xl border border-slate-200/80 dark:border-slate-700 space-y-4">
            <div className="flex items-center gap-2">
              <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <div>
                <h4 className="font-black text-sm text-slate-800 dark:text-slate-200">Inbound Email Gateway Simulator</h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">Emulates SendGrid / AWS SES Inbound webhook</p>
              </div>
            </div>

            <form onSubmit={handleInboundSimulation} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">Sender Email</label>
                <input
                  type="email"
                  required
                  value={inboundEmail}
                  onChange={(e) => setInboundEmail(e.target.value)}
                  placeholder="client@externalcorp.com"
                  className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">Sender Name</label>
                <input
                  type="text"
                  required
                  value={inboundName}
                  onChange={(e) => setInboundName(e.target.value)}
                  placeholder="Alice Inbound"
                  className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">Email Subject</label>
                <input
                  type="text"
                  required
                  value={inboundSubject}
                  onChange={(e) => setInboundSubject(e.target.value)}
                  placeholder="Production cluster connection failure"
                  className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">Message Body</label>
                <textarea
                  required
                  rows={3}
                  value={inboundBody}
                  onChange={(e) => setInboundBody(e.target.value)}
                  placeholder="Body of incoming customer email..."
                  className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={inboundLoading}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-md shadow-blue-500/20 transition flex items-center justify-center gap-1.5"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{inboundLoading ? 'Ingesting...' : 'Ingest Inbound Email'}</span>
              </button>
            </form>

            {inboundResult && (
              <div className="p-3 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 rounded-2xl text-xs text-emerald-800 dark:text-emerald-300">
                <p className="font-bold">✓ Inbound Ticket Dispatched #{inboundResult.ticket_id}</p>
                <p className="text-[11px] mt-0.5">{inboundResult.title}</p>
              </div>
            )}
          </div>

          {/* Right Col: GDPR Erasure */}
          <div className="p-5 bg-slate-50 dark:bg-slate-800/60 rounded-3xl border border-slate-200/80 dark:border-slate-700 space-y-4">
            <div className="flex items-center gap-2">
              <UserX className="w-5 h-5 text-red-600 dark:text-red-400" />
              <div>
                <h4 className="font-black text-sm text-slate-800 dark:text-slate-200">GDPR Right to Erasure</h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">Purges customer personal identity and anonymizes historical audit records</p>
              </div>
            </div>

            <form onSubmit={handleErasure} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 mb-1">Target Customer Email</label>
                <input
                  type="email"
                  required
                  value={emailToErase}
                  onChange={(e) => setEmailToErase(e.target.value)}
                  placeholder="customer.to.purge@domain.com"
                  className="w-full px-3 py-2 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20"
                />
              </div>

              <div className="p-3 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 rounded-xl text-xs text-red-700 dark:text-red-400">
                <span className="font-bold flex items-center gap-1"><AlertTriangle className="w-3.5 h-3.5" /> Warning: Irreversible Action</span>
                <p className="text-[11px] mt-1 leading-relaxed">Redacts user account, scrubs comment text, and renames requester identity to anonymized cryptographic identifiers.</p>
              </div>

              <button
                type="submit"
                disabled={erasureLoading}
                className="w-full py-2.5 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded-xl shadow-md shadow-red-500/20 transition flex items-center justify-center gap-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{erasureLoading ? 'Purging PII...' : 'Execute GDPR Erasure'}</span>
              </button>
            </form>

            {erasureResult && (
              <div className="p-3 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 rounded-2xl text-xs text-emerald-800 dark:text-emerald-300">
                <p className="font-bold">✓ Subject Purged Successfully</p>
                <p className="text-[11px] mt-0.5">Scrubbed {erasureResult.anonymized_tickets_count} tickets & {erasureResult.anonymized_comments_count} comments.</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
