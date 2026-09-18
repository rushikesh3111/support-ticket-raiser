import React, { useState, useEffect } from 'react';
import { 
  getCurrentUser, removeAuthToken, apiRequest 
} from './services/api';
import AuthModal from './components/AuthModal';
import CreateTicketModal from './components/CreateTicketModal';
import TicketDetailModal from './components/TicketDetailModal';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import KnowledgeBaseModal from './components/KnowledgeBaseModal';
import BulkActionsToolbar from './components/BulkActionsToolbar';
import confetti from 'canvas-confetti';
import { 
  LifeBuoy, Plus, Search, Filter, Bell, LogOut, Shield, 
  UserCheck, AlertCircle, Clock, CheckCircle2, ChevronRight, BarChart2,
  BookOpen, Sparkles, CheckSquare, Square, Download, RefreshCw
} from 'lucide-react';

export default function App() {
  const [currentUser, setCurrentUser] = useState(getCurrentUser());
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTicketId, setSelectedTicketId] = useState(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isKBOpen, setIsKBOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('tickets'); // 'tickets' | 'analytics'
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);
  const [agents, setAgents] = useState([]);

  const fetchTickets = async () => {
    if (!currentUser) return;
    setLoading(true);
    try {
      let query = `/tickets/?limit=50`;
      if (filterStatus) query += `&status=${filterStatus}`;
      if (filterPriority) query += `&priority=${filterPriority}`;
      if (searchQuery) query += `&search=${encodeURIComponent(searchQuery)}`;
      
      const data = await apiRequest(query);
      setTickets(data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchNotifications = async () => {
    if (!currentUser) return;
    try {
      const data = await apiRequest('/notifications/');
      setNotifications(data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAgents = async () => {
    if (currentUser?.role === 'admin' || currentUser?.role === 'agent') {
      try {
        const usersList = await apiRequest('/users/');
        setAgents(usersList.filter(u => u.role === 'agent' || u.role === 'admin'));
      } catch (err) {
        console.error(err);
      }
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchTickets();
      fetchNotifications();
      fetchAgents();
    }
  }, [currentUser, filterStatus, filterPriority, searchQuery]);

  const handleLogout = () => {
    removeAuthToken();
    setCurrentUser(null);
  };

  const toggleSelectTicket = (id, e) => {
    e.stopPropagation();
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === tickets.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(tickets.map(t => t.id));
    }
  };

  const exportTicketsToCSV = () => {
    if (tickets.length === 0) return;
    const headers = ["ID", "Title", "Status", "Priority", "Category", "Assignee", "Created At"];
    const rows = tickets.map(t => [
      t.id,
      `"${t.title.replace(/"/g, '""')}"`,
      t.status,
      t.priority,
      t.category,
      t.assignee_name || "Unassigned",
      new Date(t.created_at).toISOString()
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `tickets_export_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!currentUser) {
    return <AuthModal onLoginSuccess={(user) => setCurrentUser(user)} />;
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;
  const isStaff = currentUser.role === 'admin' || currentUser.role === 'agent';

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Top Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2.5">
              <div className="p-2.5 bg-gradient-to-tr from-blue-600 to-indigo-600 text-white rounded-2xl shadow-lg shadow-blue-500/25 animate-float">
                <LifeBuoy className="w-5 h-5" />
              </div>
              <span className="font-extrabold text-lg text-slate-900 tracking-tight">SupportDesk Pro</span>
            </div>

            <nav className="flex items-center gap-1.5">
              <button
                onClick={() => setActiveTab('tickets')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
                  activeTab === 'tickets' ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Tickets Feed
              </button>
              {isStaff && (
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                    activeTab === 'analytics' ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <BarChart2 className="w-3.5 h-3.5" />
                  SLA & Reports
                </button>
              )}
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {/* Knowledge Base Trigger */}
            <button
              onClick={() => setIsKBOpen(true)}
              className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition"
            >
              <BookOpen className="w-4 h-4 text-purple-600" />
              <span>Knowledge Base</span>
            </button>

            {/* Raise Ticket Button with Pulse Glow */}
            <button
              onClick={() => setIsCreateOpen(true)}
              className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 active:scale-95 transition-all duration-150"
            >
              <Plus className="w-4 h-4" />
              <span>Raise Ticket</span>
            </button>

            {/* Notification Bell */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-xl relative transition"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full ring-2 ring-white animate-pulse" />
                )}
              </button>

              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-3xl shadow-2xl border border-slate-100 p-4 z-50 animate-in fade-in zoom-in-95">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-2">
                    <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">Notifications</span>
                    <button
                      onClick={async () => {
                        await apiRequest('/notifications/read-all', { method: 'PUT' });
                        fetchNotifications();
                      }}
                      className="text-[11px] text-blue-600 hover:underline font-semibold"
                    >
                      Mark all read
                    </button>
                  </div>
                  <div className="max-h-64 overflow-y-auto space-y-2">
                    {notifications.length > 0 ? (
                      notifications.map(n => (
                        <div key={n.id} className={`p-3 rounded-2xl text-xs border ${n.is_read ? 'bg-white border-slate-100' : 'bg-blue-50/50 border-blue-100'}`}>
                          <p className="font-bold text-slate-900">{n.title}</p>
                          <p className="text-slate-600 text-[11px] mt-0.5">{n.message}</p>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-400 text-center py-4">No notifications</p>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* User Capsule */}
            <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
              <div className="text-right">
                <p className="text-xs font-bold text-slate-900">{currentUser.name}</p>
                <span className="text-[10px] font-bold uppercase text-blue-600 tracking-wider">
                  {currentUser.role}
                </span>
              </div>
              <button
                onClick={handleLogout}
                title="Sign Out"
                className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Area */}
      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 w-full">
        {activeTab === 'analytics' ? (
          <AnalyticsDashboard />
        ) : (
          <div className="space-y-6">
            {/* Filters Bar & CSV Export */}
            <div className="flex items-center justify-between gap-4 bg-white p-4 rounded-3xl border border-slate-100 shadow-sm">
              <div className="flex-1 max-w-md relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search tickets by title, body, or category..."
                  className="w-full pl-11 pr-4 py-2.5 text-xs bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
                />
              </div>

              <div className="flex items-center gap-3">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-2xl font-semibold text-slate-700 focus:outline-none"
                >
                  <option value="">All Statuses</option>
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="On Hold">On Hold</option>
                  <option value="Resolved">Resolved</option>
                  <option value="Closed">Closed</option>
                </select>

                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                  className="px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-2xl font-semibold text-slate-700 focus:outline-none"
                >
                  <option value="">All Priorities</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>

                <button
                  onClick={exportTicketsToCSV}
                  title="Export to CSV"
                  className="p-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600 hover:text-slate-900 rounded-2xl text-xs font-semibold flex items-center gap-1.5 px-3 transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>CSV</span>
                </button>
              </div>
            </div>

            {/* Table */}
            <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-400 uppercase tracking-wider font-bold border-b border-slate-100">
                    <tr>
                      {isStaff && (
                        <th className="py-3.5 px-4 w-10 text-center">
                          <button onClick={toggleSelectAll} className="p-1 hover:text-slate-600">
                            {selectedIds.length > 0 && selectedIds.length === tickets.length ? (
                              <CheckSquare className="w-4 h-4 text-blue-600" />
                            ) : (
                              <Square className="w-4 h-4" />
                            )}
                          </button>
                        </th>
                      )}
                      <th className="py-3.5 px-4">Ticket</th>
                      <th className="py-3.5 px-4">Status</th>
                      <th className="py-3.5 px-4">Priority</th>
                      <th className="py-3.5 px-4">Category</th>
                      <th className="py-3.5 px-4">Assignee</th>
                      <th className="py-3.5 px-4">SLA State</th>
                      <th className="py-3.5 px-4">Created</th>
                      <th className="py-3.5 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {loading ? (
                      <tr>
                        <td colSpan={9} className="text-center py-16 text-slate-400">Loading tickets...</td>
                      </tr>
                    ) : tickets.length > 0 ? (
                      tickets.map(t => (
                        <tr
                          key={t.id}
                          onClick={() => setSelectedTicketId(t.id)}
                          className="hover:bg-blue-50/40 cursor-pointer transition group"
                        >
                          {isStaff && (
                            <td className="py-4 px-4 text-center" onClick={(e) => toggleSelectTicket(t.id, e)}>
                              {selectedIds.includes(t.id) ? (
                                <CheckSquare className="w-4 h-4 text-blue-600 inline" />
                              ) : (
                                <Square className="w-4 h-4 text-slate-300 group-hover:text-slate-400 inline" />
                              )}
                            </td>
                          )}
                          <td className="py-4 px-4 font-semibold text-slate-900 max-w-xs truncate">
                            <span className="font-mono text-slate-400 mr-2">#{t.id}</span>
                            {t.title}
                          </td>
                          <td className="py-4 px-4">
                            <span className={`px-2.5 py-1 text-[11px] font-bold uppercase rounded-full ${
                              t.status === 'Open' ? 'bg-blue-100 text-blue-700' :
                              t.status === 'In Progress' ? 'bg-amber-100 text-amber-700' :
                              t.status === 'On Hold' ? 'bg-purple-100 text-purple-700' :
                              t.status === 'Resolved' ? 'bg-emerald-100 text-emerald-700' :
                              t.status === 'Closed' ? 'bg-slate-200 text-slate-700' :
                              'bg-red-100 text-red-700'
                            }`}>
                              {t.status}
                            </span>
                          </td>
                          <td className="py-4 px-4">
                            <span className={`font-semibold ${
                              t.priority === 'Critical' ? 'text-red-600 font-bold' :
                              t.priority === 'High' ? 'text-orange-600' :
                              'text-slate-600'
                            }`}>
                              {t.priority}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-slate-600 font-medium">{t.category}</td>
                          <td className="py-4 px-4 text-slate-700 font-medium">
                            {t.assignee_name || <span className="text-slate-400 italic">Unassigned</span>}
                          </td>
                          <td className="py-4 px-4">
                            {t.is_response_breached || t.is_resolution_breached ? (
                              <span className="text-red-600 font-bold flex items-center gap-1 text-[11px]">
                                <AlertCircle className="w-3.5 h-3.5" /> Breached
                              </span>
                            ) : (
                              <span className="text-emerald-600 font-semibold flex items-center gap-1 text-[11px]">
                                <CheckCircle2 className="w-3.5 h-3.5" /> In SLA
                              </span>
                            )}
                          </td>
                          <td className="py-4 px-4 text-slate-500 font-medium">
                            {new Date(t.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-4 px-4 text-right">
                            <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-blue-600 group-hover:translate-x-1 transition inline" />
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={9} className="text-center py-16 text-slate-400">
                          No tickets found. Raise one using the button above!
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Floating Bulk Actions Toolbar */}
      {isStaff && (
        <BulkActionsToolbar
          selectedIds={selectedIds}
          onClear={() => setSelectedIds([])}
          onActionComplete={fetchTickets}
          agents={agents}
          isAdmin={currentUser.role === 'admin'}
        />
      )}

      {/* Modals */}
      <CreateTicketModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onTicketCreated={() => {
          fetchTickets();
          fetchNotifications();
        }}
      />

      <KnowledgeBaseModal
        isOpen={isKBOpen}
        onClose={() => setIsKBOpen(false)}
      />

      {selectedTicketId && (
        <TicketDetailModal
          ticketId={selectedTicketId}
          currentUser={currentUser}
          onClose={() => setSelectedTicketId(null)}
          onRefresh={() => {
            fetchTickets();
            fetchNotifications();
          }}
        />
      )}
    </div>
  );
}
