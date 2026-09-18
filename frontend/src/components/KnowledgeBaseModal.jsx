import React, { useState, useEffect } from 'react';
import { apiRequest } from '../services/api';
import { BookOpen, Search, Tag, ExternalLink, HelpCircle, ChevronRight, X } from 'lucide-react';

export default function KnowledgeBaseModal({ isOpen, onClose, onSelectArticle }) {
  const [articles, setArticles] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchArticles();
    }
  }, [isOpen, search]);

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const data = await apiRequest(`/kb/?query=${encodeURIComponent(search)}`);
      setArticles(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full h-[80vh] flex flex-col border border-slate-100 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-white/15 backdrop-blur-sm rounded-2xl">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold tracking-tight">Self-Service Knowledge Base</h3>
              <p className="text-xs text-blue-100 font-medium">Search troubleshooting articles, guides, and corporate SOPs</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-xl transition text-white/80 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-4 border-b border-slate-100 bg-slate-50/70">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-4 top-3.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by keywords: VPN, 504 timeout, AWS access, replacement..."
              className="w-full pl-11 pr-4 py-2.5 text-sm bg-white border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-medium shadow-sm transition"
            />
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {selectedArticle ? (
            <div className="space-y-4 animate-in fade-in">
              <button
                onClick={() => setSelectedArticle(null)}
                className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1 mb-2"
              >
                ← Back to all articles
              </button>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-1 bg-purple-50 text-purple-700 rounded-lg">
                  {selectedArticle.category}
                </span>
                {selectedArticle.tags && (
                  <span className="text-[11px] text-slate-400 font-mono">
                    Tags: {selectedArticle.tags}
                  </span>
                )}
              </div>
              <h2 className="text-2xl font-bold text-slate-900">{selectedArticle.title}</h2>
              <div className="p-5 bg-slate-50 border border-slate-100 rounded-2xl text-slate-700 text-sm leading-relaxed whitespace-pre-wrap font-normal">
                {selectedArticle.content}
              </div>
            </div>
          ) : loading ? (
            <div className="text-center py-16 text-slate-400 text-sm">Searching knowledge base...</div>
          ) : articles.length > 0 ? (
            <div className="grid grid-cols-1 gap-3">
              {articles.map((art) => (
                <div
                  key={art.id}
                  onClick={() => setSelectedArticle(art)}
                  className="p-4 rounded-2xl border border-slate-100 hover:border-blue-300 hover:bg-blue-50/40 cursor-pointer transition-all duration-200 flex items-center justify-between group shadow-sm hover:shadow"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 bg-blue-50 text-blue-600 rounded-md">
                        {art.category}
                      </span>
                      <h4 className="font-bold text-slate-800 text-sm group-hover:text-blue-600 transition">
                        {art.title}
                      </h4>
                    </div>
                    <p className="text-xs text-slate-500 line-clamp-1">{art.content}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-blue-600 group-hover:translate-x-1 transition" />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <HelpCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <p className="text-sm font-semibold text-slate-600">No matching help articles found</p>
              <p className="text-xs text-slate-400 mt-1">Try searching with a broader keyword or raise a ticket directly.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
