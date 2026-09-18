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
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LifeBuoy, Plus, Search, Filter, Bell, LogOut, Shield, 
  UserCheck, AlertCircle, Clock, CheckCircle2, ChevronRight, BarChart2,
  BookOpen, Sparkles, CheckSquare, Square, Download, RefreshCw, Sun, Moon,
  Layers, Check, TrendingUp
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
  const [isDarkMode, setIsDarkMode] = useState(false);

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

  // Stats calculation for live bar
  const openCount = tickets.filter(t => t.status === 'Open').length;
  const inProgressCount = tickets.filter(t => t.status === 'In Progress').length;
  const resolvedCount = tickets.filter(t => t.status === 'Resolved' || t.status === 'Closed').length;

  return (
    <div className={`min-h-screen flex flex-col ${isDarkMode ? 'dark bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'} transition-colors duration-300`}>
      {/* Top Header */}
      <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2.5">
              <motion.div
                whileHover={{ rotate: 180 }}
                transition={{ duration: 0.6 }}
                className="p-2.5 bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 text-white rounded-2xl shadow-lg shadow-blue-500/25 cursor-pointer"
              >
                <LifeBuoy className="w-5 h-5" />
              </motion.div>
              <div>
                <span className="font-black text-lg tracking-tight bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  SupportDesk Pro
                </span>
                <span className="ml-2 text-[10px] font-bold px-2 py-0.5 bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400 rounded-full">
                  v2.0 Live
                </span>
              </div>
            </div>

            <nav className="flex items-center gap-1.5">
              <button
                onClick={() => setActiveTab('tickets')}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                  activeTab === 'tickets' ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                Tickets Feed
              </button>
              {isStaff && (
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                    activeTab === 'analytics' ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
                  }`}
                >
                  <BarChart2 className="w-3.5 h-3.5" />
                  SLA & Reports
                </button>
              )}
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {/* Dark Mode Toggle */}
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition"
              title="Toggle Dark Mode"
            >
              {isDarkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </motion.button>

            {/* Knowledge Base Trigger with Animated Pulse */}
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              onClick={() => setIsKBOpen(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 bg-purple-50 dark:bg-purple-950/50 hover:bg-purple-100 border border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300 text-xs font-bold rounded-2xl transition shadow-sm"
            >
              <BookOpen className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span>Knowledge Base</span>
            </motion.button>

            {/* Raise Ticket Button with Shimmer Animation */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsCreateOpen(true)}
              className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-xs font-bold rounded-2xl shadow-lg shadow-blue-500/30 transition-all duration-200"
            >
              <Plus className="w-4 h-4" />
              <span>Raise Ticket</span>
            </motion.button>

            {/* Notification Bell */}
            <div className="relative">
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-2xl relative transition"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full ring-2 ring-white dark:ring-slate-900 animate-ping" />
                )}
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full ring-2 ring-white dark:ring-slate-900" />
                )}
              </motion.button>

              <AnimatePresence>
                {showNotifications && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 10 }}
                    className="absolute right-0 mt-2 w-80 bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-800 p-4 z-50 overflow-hidden"
                  >
                    <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-2">
                      <span className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">Live Alerts</span>
                      <button
                        onClick={async () => {
                          await apiRequest('/notifications/read-all', { method: 'PUT' });
                          fetchNotifications();
                        }}
                        className="text-[11px] text-blue-600 dark:text-blue-400 hover:underline font-bold"
                      >
                        Mark all read
                      </button>
                    </div>
                    <div className="max-h-64 overflow-y-auto space-y-2">
                      {notifications.length > 0 ? (
                        notifications.map(n => (
                          <div key={n.id} className={`p-3 rounded-2xl text-xs border ${n.is_read ? 'bg-white dark:bg-slate-800 border-slate-100 dark:border-slate-700' : 'bg-blue-50/50 dark:bg-blue-950/40 border-blue-100 dark:border-blue-900'}`}>
                            <p className="font-bold text-slate-900 dark:text-slate-100">{n.title}</p>
                            <p className="text-slate-600 dark:text-slate-400 text-[11px] mt-0.5">{n.message}</p>
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-slate-400 text-center py-5">No unread notifications</p>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* User Capsule */}
            <div className="flex items-center gap-3 pl-3 border-l border-slate-200 dark:border-slate-800">
              <div className="text-right">
                <p className="text-xs font-bold text-slate-900 dark:text-slate-100">{currentUser.name}</p>
                <span className="text-[10px] font-black uppercase text-blue-600 dark:text-blue-400 tracking-wider">
                  {currentUser.role}
                </span>
              </div>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleLogout}
                title="Sign Out"
                className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/50 rounded-2xl transition"
              >
                <LogOut className="w-4 h-4" />
              </motion.button>
            </div>
          </div>
        </div>
      </header>

      {/* Quick Overview KPI Pills */}
      <div className="max-w-7xl mx-auto px-6 pt-6 w-full">
        <div className="grid grid-cols-3 gap-4">
          <motion.div
            whileHover={{ y: -2 }}
            className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between"
          >
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Open Tickets</span>
              <p className="text-2xl font-black text-blue-600 mt-0.5">{openCount}</p>
            </div>
            <div className="p-3 bg-blue-50 dark:bg-blue-950 text-blue-600 rounded-2xl">
              <AlertCircle className="w-5 h-5" />
            </div>
          </motion.div>

          <motion.div
            whileHover={{ y: -2 }}
            className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between"
          >
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">In Progress</span>
              <p className="text-2xl font-black text-amber-500 mt-0.5">{inProgressCount}</p>
            </div>
            <div className="p-3 bg-amber-50 dark:bg-amber-950 text-amber-500 rounded-2xl">
              <Clock className="w-5 h-5" />
            </div>
          </motion.div>

          <motion.div
            whileHover={{ y: -2 }}
            className="p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm flex items-center justify-between"
          >
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Resolved / Closed</span>
              <p className="text-2xl font-black text-emerald-600 mt-0.5">{resolvedCount}</p>
            </div>
            <div className="p-3 bg-emerald-50 dark:bg-emerald-950 text-emerald-600 rounded-2xl">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </motion.div>
        </div>
      </div>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-6 flex-1 w-full">
        {activeTab === 'analytics' ? (
          <AnalyticsDashboard />
        ) : (
          <div className="space-y-6">
            {/* Filter Bar */}
            <div className="flex items-center justify-between gap-4 bg-white dark:bg-slate-900 p-4 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
              <div className="flex-1 max-w-md relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search tickets by title, body, or category..."
                  className="w-full pl-11 pr-4 py-2.5 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium"
                />
              </div>

              <div className="flex items-center gap-3">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3.5 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl font-bold text-slate-700 dark:text-slate-300 focus:outline-none"
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
                  className="px-3.5 py-2 text-xs bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl font-bold text-slate-700 dark:text-slate-300 focus:outline-none"
                >
                  <option value="">All Priorities</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={exportTicketsToCSV}
                  title="Export to CSV"
                  className="p-2 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-2xl text-xs font-bold flex items-center gap-1.5 px-3.5 transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>CSV</span>
                </motion.button>
              </div>
            </div>

            {/* Table */}
            <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-400 uppercase tracking-wider font-bold border-b border-slate-100 dark:border-slate-800">
                    <tr>
                      {isStaff && (
                        <th className="py-4 px-4 w-10 text-center">
                          <button onClick={toggleSelectAll} className="p-1 hover:text-slate-600">
                            {selectedIds.length > 0 && selectedIds.length === tickets.length ? (
                              <CheckSquare className="w-4 h-4 text-blue-600" />
                            ) : (
                              <Square className="w-4 h-4" />
                            )}
                          </button>
                        </th>
                      )}
                      <th className="py-4 px-4">Ticket</th>
                      <th className="py-4 px-4">Status</th>
                      <th className="py-4 px-4">Priority</th>
                      <th className="py-4 px-4">Category</th>
                      <th className="py-4 px-4">Assignee</th>
                      <th className="py-4 px-4">SLA State</th>
                      <th className="py-4 px-4">Created</th>
                      <th className="py-4 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {loading ? (
                      <tr>
                        <td colSpan={9} className="text-center py-16 text-slate-400">Loading tickets...</td>
                      </tr>
                    ) : tickets.length > 0 ? (
                      tickets.map(t => (
                        <motion.tr
                          key={t.id}
                          whileHover={{ backgroundColor: "rgba(59, 130, 246, 0.04)" }}
                          onClick={() => setSelectedTicketId(t.id)}
                          className="cursor-pointer transition-colors group"
                        >
                          {isStaff && (
                            <td className="py-4 px-4 text-center" onClick={(e) => toggleSelectTicket(t.id, e)}>
                              {selectedIds.includes(t.id) ? (
                                <CheckSquare className="w-4 h-4 text-blue-600 inline" />
                              ) : (
                                <Square className="w-4 h-4 text-slate-300 dark:text-slate-600 group-hover:text-slate-400 inline" />
                              )}
                            </td>
                          )}
                          <td className="py-4 px-4 font-bold text-slate-900 dark:text-slate-100 max-w-xs truncate">
                            <span className="font-mono text-slate-400 mr-2">#{t.id}</span>
                            {t.title}
                          </td>
                          <td className="py-4 px-4">
                            <span className={`px-3 py-1 text-[10px] font-extrabold uppercase rounded-full tracking-wider ${
                              t.status === 'Open' ? 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300 ring-1 ring-blue-300/40' :
                              t.status === 'In Progress' ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 ring-1 ring-amber-300/40' :
                              t.status === 'On Hold' ? 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300 ring-1 ring-purple-300/40' :
                              t.status === 'Resolved' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 ring-1 ring-emerald-300/40' :
                              t.status === 'Closed' ? 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300' :
                              'bg-red-100 text-red-700'
                            }`}>
                              {t.status}
                            </span>
                          </td>
                          <td className="py-4 px-4">
                            <span className={`font-bold ${
                              t.priority === 'Critical' ? 'text-red-600 dark:text-red-400 font-extrabold' :
                              t.priority === 'High' ? 'text-orange-600 dark:text-orange-400' :
                              'text-slate-600 dark:text-slate-400'
                            }`}>
                              {t.priority}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-slate-600 dark:text-slate-400 font-medium">{t.category}</td>
                          <td className="py-4 px-4 text-slate-700 dark:text-slate-300 font-semibold">
                            {t.assignee_name || <span className="text-slate-400 dark:text-slate-600 italic">Unassigned</span>}
                          </td>
                          <td className="py-4 px-4">
                            {t.is_response_breached || t.is_resolution_breached ? (
                              <span className="text-red-600 dark:text-red-400 font-bold flex items-center gap-1 text-[11px]">
                                <AlertCircle className="w-3.5 h-3.5" /> Breached
                              </span>
                            ) : (
                              <span className="text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1 text-[11px]">
                                <CheckCircle2 className="w-3.5 h-3.5" /> In SLA
                              </span>
                            )}
                          </td>
                          <td className="py-4 px-4 text-slate-500 dark:text-slate-400 font-medium">
                            {new Date(t.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-4 px-4 text-right">
                            <ChevronRight className="w-4 h-4 text-slate-300 dark:text-slate-600 group-hover:text-blue-600 group-hover:translate-x-1 transition inline" />
                          </td>
                        </motion.tr>
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
