import React, { useState } from 'react';
import { apiRequest } from '../services/api';
import { CheckSquare, UserCheck, Shield, RefreshCw, Trash2, X } from 'lucide-react';

export default function BulkActionsToolbar({ selectedIds, onClear, onActionComplete, agents, isAdmin }) {
  const [loading, setLoading] = useState(false);

  if (!selectedIds || selectedIds.length === 0) return null;

  const handleBulkStatus = async (statusValue) => {
    setLoading(true);
    try {
      await apiRequest('/actions/tickets/bulk', {
        method: 'POST',
        body: JSON.stringify({
          ticket_ids: selectedIds,
          action: 'status',
          status_value: statusValue
        })
      });
      onActionComplete();
      onClear();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBulkAssign = async (assigneeId) => {
    setLoading(true);
    try {
      await apiRequest('/actions/tickets/bulk', {
        method: 'POST',
        body: JSON.stringify({
          ticket_ids: selectedIds,
          action: 'assign',
          assignee_id: parseInt(assigneeId)
        })
      });
      onActionComplete();
      onClear();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBulkArchive = async () => {
    if (!window.confirm(`Archive ${selectedIds.length} selected tickets?`)) return;
    setLoading(true);
    try {
      await apiRequest('/actions/tickets/bulk', {
        method: 'POST',
        body: JSON.stringify({
          ticket_ids: selectedIds,
          action: 'archive'
        })
      });
      onActionComplete();
      onClear();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900/90 backdrop-blur-md text-white px-5 py-3 rounded-2xl shadow-2xl z-40 flex items-center gap-4 border border-slate-700 animate-in slide-in-from-bottom-5">
      <div className="flex items-center gap-2 pr-3 border-r border-slate-700">
        <CheckSquare className="w-4 h-4 text-blue-400" />
        <span className="text-xs font-bold">{selectedIds.length} Selected</span>
      </div>

      <div className="flex items-center gap-2">
        <select
          onChange={(e) => {
            if (e.target.value) handleBulkStatus(e.target.value);
          }}
          defaultValue=""
          disabled={loading}
          className="bg-slate-800 text-xs px-2.5 py-1.5 rounded-xl border border-slate-700 text-slate-200 focus:outline-none"
        >
          <option value="" disabled>Set Status...</option>
          <option value="In Progress">In Progress</option>
          <option value="On Hold">On Hold</option>
          <option value="Resolved">Resolved</option>
          <option value="Closed">Closed</option>
        </select>

        <select
          onChange={(e) => {
            if (e.target.value) handleBulkAssign(e.target.value);
          }}
          defaultValue=""
          disabled={loading}
          className="bg-slate-800 text-xs px-2.5 py-1.5 rounded-xl border border-slate-700 text-slate-200 focus:outline-none"
        >
          <option value="" disabled>Assign To...</option>
          {agents && agents.map(a => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>

        {isAdmin && (
          <button
            onClick={handleBulkArchive}
            disabled={loading}
            className="p-1.5 hover:bg-red-500/20 text-red-400 hover:text-red-300 rounded-xl transition flex items-center gap-1 text-xs font-semibold px-2.5"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Archive</span>
          </button>
        )}
      </div>

      <button
        onClick={onClear}
        className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition ml-2"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
