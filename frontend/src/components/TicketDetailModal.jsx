import React, { useState, useEffect } from 'react';
import { apiRequest } from '../services/api';
import { 
  X, Send, Paperclip, Clock, AlertTriangle, CheckCircle2, 
  UserCheck, ShieldAlert, History, MessageSquare, Lock, Download
} from 'lucide-react';

export default function TicketDetailModal({ ticketId, currentUser, onClose, onRefresh }) {
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState('');
  const [isInternal, setIsInternal] = useState(false);
  const [commentSubmitting, setCommentSubmitting] = useState(false);
  const [statusSubmitting, setStatusSubmitting] = useState(false);
  const [fileToUpload, setFileToUpload] = useState(null);
  const [agents, setAgents] = useState([]);
  const [activeTab, setActiveTab] = useState('comments'); // 'comments' | 'history'

  const fetchTicket = async () => {
    try {
      const data = await apiRequest(`/tickets/${ticketId}`);
      setTicket(data);
    } catch (err) {
      alert(err.message);
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const fetchAgents = async () => {
    if (currentUser.role === 'admin' || currentUser.role === 'agent') {
      try {
        const usersList = await apiRequest('/users/');
        setAgents(usersList.filter(u => u.role === 'agent' || u.role === 'admin'));
      } catch (err) {
        console.error(err);
      }
    }
  };

  useEffect(() => {
    fetchTicket();
    fetchAgents();
  }, [ticketId]);

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    setCommentSubmitting(true);
    try {
      await apiRequest(`/tickets/${ticketId}/comments/`, {
        method: 'POST',
        body: JSON.stringify({
          message: commentText,
          is_internal: isInternal
        })
      });
      setCommentText('');
      setIsInternal(false);
      await fetchTicket();
      onRefresh();
    } catch (err) {
      alert(err.message);
    } finally {
      setCommentSubmitting(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    setStatusSubmitting(true);
    try {
      await apiRequest(`/tickets/${ticketId}`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus })
      });
      await fetchTicket();
      onRefresh();
    } catch (err) {
      alert(err.message);
    } finally {
      setStatusSubmitting(false);
    }
  };

  const handleAssigneeChange = async (newAssigneeId) => {
    try {
      await apiRequest(`/tickets/${ticketId}`, {
        method: 'PUT',
        body: JSON.stringify({ assigned_to: parseInt(newAssigneeId) || null })
      });
      await fetchTicket();
      onRefresh();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      await apiRequest(`/tickets/${ticketId}/attachments`, {
        method: 'POST',
        body: formData
      });
      await fetchTicket();
      onRefresh();
    } catch (err) {
      alert(err.message);
    }
  };

  if (!ticketId) return null;

  const isStaff = currentUser.role === 'admin' || currentUser.role === 'agent';

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full h-[90vh] flex flex-col border border-slate-100 animate-in fade-in zoom-in-95">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <span className="font-mono text-sm font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-lg">
              #{ticket?.id}
            </span>
            <span className={`px-2.5 py-1 text-xs font-bold uppercase rounded-full ${
              ticket?.status === 'Open' ? 'bg-blue-100 text-blue-700' :
              ticket?.status === 'In Progress' ? 'bg-amber-100 text-amber-700' :
              ticket?.status === 'On Hold' ? 'bg-purple-100 text-purple-700' :
              ticket?.status === 'Resolved' ? 'bg-emerald-100 text-emerald-700' :
              ticket?.status === 'Closed' ? 'bg-slate-200 text-slate-700' :
              'bg-red-100 text-red-700'
            }`}>
              {ticket?.status}
            </span>
            <span className={`px-2.5 py-1 text-xs font-semibold rounded-lg ${
              ticket?.priority === 'Critical' ? 'bg-red-50 text-red-600 border border-red-200' :
              ticket?.priority === 'High' ? 'bg-orange-50 text-orange-600 border border-orange-200' :
              'bg-slate-100 text-slate-600'
            }`}>
              {ticket?.priority} Priority
            </span>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-xl text-slate-400 hover:text-slate-600 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        {loading ? (
          <div className="flex-1 flex items-center justify-center text-slate-400">Loading ticket details...</div>
        ) : (
          <div className="flex-1 grid grid-cols-3 divide-x divide-slate-100 overflow-hidden">
            
            {/* Left 2 Cols: Main Content & Thread */}
            <div className="col-span-2 flex flex-col h-full overflow-hidden">
              <div className="p-6 border-b border-slate-100 shrink-0">
                <h2 className="text-xl font-bold text-slate-900 mb-2">{ticket.title}</h2>
                <p className="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                  {ticket.description}
                </p>

                {/* Attachments Section */}
                {ticket.attachments && ticket.attachments.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Attached Files</p>
                    <div className="flex flex-wrap gap-2">
                      {ticket.attachments.map(att => (
                        <a
                          key={att.id}
                          href={`http://${window.location.hostname}:8000/api/v1/attachments/${att.id}/download`}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center gap-2 text-xs font-medium bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-1.5 rounded-lg border border-blue-200 transition"
                        >
                          <Paperclip className="w-3.5 h-3.5" />
                          <span>{att.filename}</span>
                          <Download className="w-3 h-3 text-blue-500" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Tabs for Comments vs Audit History */}
              <div className="flex items-center gap-4 px-6 pt-3 border-b border-slate-100 shrink-0">
                <button
                  onClick={() => setActiveTab('comments')}
                  className={`pb-2 text-xs font-bold uppercase tracking-wider border-b-2 transition flex items-center gap-1.5 ${
                    activeTab === 'comments' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-400 hover:text-slate-600'
                  }`}
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  Conversation ({ticket.comments?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`pb-2 text-xs font-bold uppercase tracking-wider border-b-2 transition flex items-center gap-1.5 ${
                    activeTab === 'history' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-400 hover:text-slate-600'
                  }`}
                >
                  <History className="w-3.5 h-3.5" />
                  Audit Trail ({ticket.audit_logs?.length || 0})
                </button>
              </div>

              {/* Conversation Feed */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {activeTab === 'comments' ? (
                  ticket.comments && ticket.comments.length > 0 ? (
                    ticket.comments.map(c => (
                      <div
                        key={c.id}
                        className={`p-4 rounded-xl border ${
                          c.is_internal
                            ? 'bg-amber-50/70 border-amber-200/80 text-amber-900'
                            : c.author_role === 'agent' || c.author_role === 'admin'
                            ? 'bg-blue-50/50 border-blue-100'
                            : 'bg-slate-50 border-slate-100'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-xs text-slate-900">{c.author_name}</span>
                            <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-slate-200/70 text-slate-600">
                              {c.author_role}
                            </span>
                            {c.is_internal && (
                              <span className="flex items-center gap-1 text-[10px] font-bold uppercase bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full">
                                <Lock className="w-2.5 h-2.5" /> Internal Note
                              </span>
                            )}
                          </div>
                          <span className="text-[11px] text-slate-400">
                            {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        <p className="text-sm text-slate-700 whitespace-pre-wrap">{c.message}</p>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-10 text-slate-400 text-xs">No comments yet. Start the conversation below.</div>
                  )
                ) : (
                  ticket.audit_logs && ticket.audit_logs.length > 0 ? (
                    <div className="space-y-3">
                      {ticket.audit_logs.map(log => (
                        <div key={log.id} className="flex items-start gap-3 text-xs border-l-2 border-blue-500 pl-3 py-1">
                          <div>
                            <span className="font-semibold text-slate-800">{log.action}</span>: <span className="text-slate-600">{log.details}</span>
                            <p className="text-[10px] text-slate-400 mt-0.5">{new Date(log.timestamp).toLocaleString()}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-10 text-slate-400 text-xs">No audit records found.</div>
                  )
                )}
              </div>

              {/* Add Comment Input */}
              {ticket.status !== 'Closed' && ticket.status !== 'Archived' ? (
                <form onSubmit={handleAddComment} className="p-4 border-t border-slate-100 bg-slate-50/50 shrink-0">
                  <div className="flex items-center justify-between mb-2">
                    {isStaff && (
                      <label className="flex items-center gap-1.5 text-xs text-amber-700 font-medium cursor-pointer">
                        <input
                          type="checkbox"
                          checked={isInternal}
                          onChange={(e) => setIsInternal(e.target.checked)}
                          className="rounded border-amber-300 text-amber-600 focus:ring-amber-500"
                        />
                        <span>Private Staff Note (hidden from customer)</span>
                      </label>
                    )}
                    <label className="text-xs text-blue-600 hover:text-blue-800 font-medium cursor-pointer flex items-center gap-1 ml-auto">
                      <Paperclip className="w-3.5 h-3.5" />
                      <span>Attach file</span>
                      <input type="file" className="hidden" onChange={handleFileUpload} />
                    </label>
                  </div>
                  <div className="flex gap-2">
                    <textarea
                      rows={2}
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      placeholder={isInternal ? "Write internal agent note..." : "Reply to ticket..."}
                      className="flex-1 px-3.5 py-2 text-sm bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 resize-none font-medium"
                    />
                    <button
                      type="submit"
                      disabled={commentSubmitting || !commentText.trim()}
                      className="px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold text-sm transition shadow-sm disabled:opacity-50 flex items-center justify-center"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </form>
              ) : (
                <div className="p-4 bg-slate-100 text-center text-xs font-semibold text-slate-500">
                  This ticket is {ticket.status.toLowerCase()}. Further comments are locked.
                </div>
              )}
            </div>

            {/* Right Column: Meta & Control Actions */}
            <div className="p-6 flex flex-col space-y-6 overflow-y-auto">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Ticket Information</h4>
                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-slate-400 block">Raised By:</span>
                    <span className="font-semibold text-slate-800">{ticket.creator_name || `User #${ticket.created_by}`}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Category:</span>
                    <span className="font-semibold text-slate-800">{ticket.category}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Created On:</span>
                    <span className="font-semibold text-slate-800">{new Date(ticket.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* SLA Monitor Widget */}
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-2.5 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-blue-600" />
                  SLA Monitor
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500">First Response:</span>
                    {ticket.is_response_breached ? (
                      <span className="text-red-600 font-bold flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> Breached
                      </span>
                    ) : ticket.first_responded_at ? (
                      <span className="text-emerald-600 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Met
                      </span>
                    ) : (
                      <span className="text-amber-600 font-semibold">Pending</span>
                    )}
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500">Resolution Due:</span>
                    {ticket.is_resolution_breached ? (
                      <span className="text-red-600 font-bold flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> Breached
                      </span>
                    ) : ticket.resolved_at ? (
                      <span className="text-emerald-600 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Met
                      </span>
                    ) : (
                      <span className="text-slate-700 font-medium">
                        {ticket.resolution_due_at ? new Date(ticket.resolution_due_at).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}) : 'N/A'}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Agent Assignment (Staff only) */}
              {isStaff && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Assignee</h4>
                  <select
                    value={ticket.assigned_to || ''}
                    onChange={(e) => handleAssigneeChange(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  >
                    <option value="">Unassigned</option>
                    {agents.map(a => (
                      <option key={a.id} value={a.id}>{a.name} ({a.role})</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Status Action Buttons (Staff only) */}
              {isStaff && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5">Change Status</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {ticket.status !== 'In Progress' && ticket.status !== 'Closed' && (
                      <button
                        onClick={() => handleStatusChange('In Progress')}
                        disabled={statusSubmitting}
                        className="text-xs py-2 px-3 bg-amber-50 hover:bg-amber-100 text-amber-700 rounded-xl font-semibold border border-amber-200 transition"
                      >
                        In Progress
                      </button>
                    )}
                    {ticket.status !== 'On Hold' && ticket.status !== 'Closed' && (
                      <button
                        onClick={() => handleStatusChange('On Hold')}
                        disabled={statusSubmitting}
                        className="text-xs py-2 px-3 bg-purple-50 hover:bg-purple-100 text-purple-700 rounded-xl font-semibold border border-purple-200 transition"
                      >
                        On Hold
                      </button>
                    )}
                    {ticket.status !== 'Resolved' && ticket.status !== 'Closed' && (
                      <button
                        onClick={() => handleStatusChange('Resolved')}
                        disabled={statusSubmitting}
                        className="text-xs py-2 px-3 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 rounded-xl font-semibold border border-emerald-200 transition"
                      >
                        Resolve Ticket
                      </button>
                    )}
                    {ticket.status !== 'Closed' && (
                      <button
                        onClick={() => handleStatusChange('Closed')}
                        disabled={statusSubmitting}
                        className="text-xs py-2 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold border border-slate-300 transition"
                      >
                        Close Ticket
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
